"""Ensure the event register covers the shipping overrides and remains sorted."""
import collections
import json
import re
import unittest

import build_event_overrides as builder
import build_event_tracker as tracker
from event_option_specs import SPECS


class EventTrackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tracker.build()

    def test_registry_and_csvs_are_current(self):
        for path, payload in tracker.outputs(self.data).items():
            self.assertEqual(path.read_bytes(), payload, str(path))

    def test_every_event_and_added_option_is_recorded_once(self):
        self.assertEqual({r['event_id'] for r in self.data['events']}, {e for e, _, _ in SPECS})
        self.assertEqual(len(self.data['events']), len(SPECS))
        actual = [(r['event_id'], r['option_key']) for r in self.data['options']]
        expected = [(e, key) for e, _, choices in SPECS
                    for key in re.findall(r'\bname\s*=\s*(ac_event_\w+)', choices)]
        self.assertCountEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))
        counts = collections.Counter(e for e, _ in actual)
        for row in self.data['events']:
            self.assertEqual(row['added_choices'], counts[row['event_id']])
        self.assertEqual(sum(row['change_type'] == 'Linked resolution' for row in self.data['events']), 2)

    def test_sort_and_source_lines_match_shipping_files(self):
        for collection in ('events', 'options'):
            rows = self.data[collection]
            key = lambda r: (r['content_pack'].casefold(), r['event_name'].casefold(), r['event_id'], r.get('option_key', ''))
            self.assertEqual(rows, sorted(rows, key=key))
        for row in self.data['events']:
            path, line = row['mod_source'].rsplit(':', 1)
            text = (builder.ROOT / path).read_text(encoding='utf-8-sig').splitlines()
            self.assertTrue(text[int(line) - 1].startswith(row['event_id'] + ' = {'), row['event_id'])
        for row in self.data['options']:
            self.assertTrue(row['added_option'])
            self.assertTrue(row['outcome'])
            self.assertTrue(row['requirements_script'])
            self.assertNotIn('Cultivation resolution; exact effects', row['outcome'])


if __name__ == '__main__':
    unittest.main()
