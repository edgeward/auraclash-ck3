"""Static invariants accompanying the native-engine tests in AuraClash/tests.

The engine harness is the authority for gameplay transitions. These checks
catch broken wiring, incomplete generation, resource references, and accidental
government/duel coupling before launching a game.
"""
from pathlib import Path
import re
import unittest

import build_event_overrides as parser
import build_sect_content as content

MOD = content.MOD


class SectContentTests(unittest.TestCase):
    def test_generated_files_are_current(self):
        for relative, text in content.render().items():
            self.assertEqual((MOD / relative).read_bytes(), ('\ufeff' + text.rstrip() + '\n').encode('utf-8'), relative)

    def test_every_identity_has_two_distinct_elements_and_real_traits(self):
        traits = (MOD / 'common/traits/ac_cultivation_traits.txt').read_text(encoding='utf-8-sig')
        seen_styles = set()
        for key, _, one, two, style, foundation in content.IDENTITIES:
            self.assertNotEqual(one, two, key)
            for trait in (f'ac_element_{one}', f'ac_element_{two}', f'ac_style_{style}', f'ac_foundation_{foundation}'):
                self.assertRegex(traits, rf'(?m)^{trait}\s*=')
            seen_styles.add(style)
        self.assertEqual(seen_styles, {'akakiru', 'aoyusumu', 'kiihakai', 'kurokonton', 'midorikatai'})

    def test_new_scripts_balance_and_use_bom(self):
        for path in MOD.rglob('ac_sect*'):
            if path.suffix not in ('.txt', '.gui', '.yml'):
                continue
            self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'), path)
            if path.suffix != '.yml':
                clean = parser.masked(path.read_text(encoding='utf-8-sig'))
                depth = 0
                for char in clean:
                    depth += (char == '{') - (char == '}')
                    self.assertGreaterEqual(depth, 0, path)
                self.assertEqual(depth, 0, path)

    def test_no_duplicate_sect_events_or_missing_localizations(self):
        keys = set()
        for path in (MOD / 'localization/english').glob('ac_sect*.yml'):
            for key in re.findall(r'^\s+([^\s:]+):\d*\s+"', path.read_text(encoding='utf-8-sig'), re.M):
                self.assertNotIn(key, keys, key)
                keys.add(key)
        events = set()
        for path in (MOD / 'events').glob('ac_sect*.txt'):
            source = path.read_text(encoding='utf-8-sig')
            for eid in re.findall(r'^(ac_sect\w*\.\d+)\s*=\s*\{', source, re.M):
                self.assertNotIn(eid, events, eid)
                events.add(eid)
                self.assertIn(eid + '.t', keys)
            # Variable names also use `name`; only option names are localization.
            refs = re.findall(r'\b(?:title|desc)\s*=\s*(ac_sect[\w.]*)', parser.masked(source))
            refs += re.findall(r'\boption\s*=\s*\{\s*name\s*=\s*(ac_sect[\w.]*)', parser.masked(source))
            for ref in refs:
                self.assertIn(ref, keys, (path.name, ref))
        self.assertTrue(events)

    def test_sect_office_preserves_secular_government_and_avoids_single_combat(self):
        for path in MOD.rglob('ac_sect*.txt'):
            source = parser.masked(path.read_text(encoding='utf-8-sig'))
            if path.name != 'ac_sect_domicile_effects.txt':
                self.assertNotRegex(source, r'\b(?:set_government|change_government|set_primary_title_to|change_title_holder|create_adventurer_title)\s*=')
            self.assertNotRegex(source, r'\b(?:start_single_combat|configure_start_single_combat_effect|single_combat\.\d+)\b')

    def test_native_domicile_assets_and_title_are_wired(self):
        source = (MOD / 'common/scripted_effects/ac_sect_domicile_effects.txt').read_text(encoding='utf-8-sig')
        self.assertIn('create_domicile_title = {', source)
        self.assertNotRegex(source, r'\bchange_government\s*=')
        self.assertIn('scope:ac_domicile_master = { is_ruler = no }', source)
        self.assertIn('holder = scope:ac_domicile_creator', source)
        self.assertIn('change_title_holder = { holder = scope:ac_domicile_master', source)
        self.assertNotIn('give_noble_family_title', source)
        definitions = (MOD / 'common/domiciles/buildings/ac_sect_domicile_buildings.txt').read_text(encoding='utf-8-sig')
        self.assertEqual(len(re.findall(r'^ac_sect_\w+_0[123] =', definitions, re.M)), 18)
        game = Path('C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game')
        for asset in re.findall(r'"(gfx/[^"\n]+)"', definitions):
            self.assertTrue((game / asset).exists() or (MOD / asset).exists(), asset)

    def test_sect_landscape_reproduces(self):
        import build_sect_landscape
        self.assertEqual(build_sect_landscape.TARGET.read_bytes(), build_sect_landscape.render())

    def test_every_generated_character_has_explicit_gender(self):
        for path in MOD.rglob('ac_sect*.txt'):
            source = path.read_text(encoding='utf-8-sig')
            for match in re.finditer(r'\bcreate_character\s*=\s*\{', parser.masked(source)):
                end = parser.close_brace(source, source.index('{', match.start()))
                self.assertIn('gender_female_chance = 50', source[match.start():end], path)

    def test_missions_capture_contract_and_gate_repeat_claims(self):
        definitions = (MOD / 'common/task_contracts/ac_sect_contracts.txt').read_text(encoding='utf-8-sig')
        for key, _, _, _, reward in content.MISSIONS:
            self.assertIn(f'ac_sect_{key}_success', definitions)
            self.assertIn(f'ac_sect_{key}_failure', definitions)
            self.assertIn(f'ac_sect_{key}_abandoned', definitions)
            self.assertGreater(reward, 0)
        event = (MOD / 'events/ac_sect_mission_events.txt').read_text(encoding='utf-8-sig')
        self.assertIn('var:ac_sect_mission ?= scope:ac_mission_contract', event)
        resolver = (MOD / 'common/scripted_effects/ac_sect_mission_resolution.txt').read_text(encoding='utf-8-sig')
        self.assertLess(resolver.index('set_variable = { name = ac_resolved'), resolver.index('random_list ='))

    def test_native_trial_phases_all_advance(self):
        source = (MOD / 'common/activities/activity_types/ac_sect_activities.txt').read_text(encoding='utf-8-sig')
        for key in ('theory', 'body', 'spirit', 'joint_forms', 'joint_formation'):
            phase = re.search(rf'\bac_sect_{key}_phase\s*=\s*\{{', source)
            end = parser.close_brace(source, source.index('{', phase.start()))
            block = source[phase.start():end]
            self.assertIn('progress_activity_phase_after', block, key)
            self.assertIn('on_phase_active_activity', block, key)

    def test_contract_offers_use_native_letters_and_arrival_not_timers(self):
        definitions = (MOD / 'common/task_contracts/ac_sect_contracts.txt').read_text(encoding='utf-8-sig')
        self.assertEqual(definitions.count('ac_sect_depart_for_contract_effect = yes'), len(content.MISSIONS))
        self.assertEqual(definitions.count('travel = no'), len(content.MISSIONS))
        self.assertNotRegex(definitions, r'trigger_event\s*=\s*\{[^}]*days\s*=')
        # A native taker does not exist until acceptance. Using it for an
        # unaccepted offer's validity silently removes jobs during travel.
        for match in re.finditer(r'valid_to_keep\s*=\s*\{', definitions):
            end = parser.close_brace(definitions, definitions.index('{', match.start()))
            self.assertIn('var:ac_contract_disciple', definitions[match.start():end])
            self.assertNotIn('task_contract_taker', definitions[match.start():end])
        effects = (MOD / 'common/scripted_effects/ac_sect_contract_effects.txt').read_text(encoding='utf-8-sig')
        board = effects[effects.index('ac_sect_open_contract_board_effect = {'):]
        self.assertNotIn('accept_task_contract', board)
        gui = (MOD / 'gui/ac_sect_contract_board.gui').read_text(encoding='utf-8-sig')
        self.assertIn("OpenGameViewData('task_contract', TaskContract.Self)", gui)
        self.assertIn("GetList('ac_sect_offers')", gui)
        encounters = (MOD / 'events/ac_sect_job_events.txt').read_text(encoding='utf-8-sig')
        self.assertEqual(len(re.findall(r'^ac_sect_job\.\d+ =', encounters, re.M)), 6)
        self.assertEqual(encounters.count('var:ac_sect_mission ?= scope:ac_mission_contract'), 6)

    def test_sect_hud_opens_exact_sect_estate(self):
        source = (MOD / 'gui/ac_sect_hud.gui').read_text(encoding='utf-8-sig')
        self.assertIn('parentanchor = bottom|left', source)
        self.assertIn("GetScriptedGui('ac_sect_hud_estate').Execute", source)
        self.assertNotIn('Character.GetDomicile', source)
        self.assertIn("Var('ac_estate_domicile').Domicile", source)

    def test_native_harness_never_runs_in_normal_mod(self):
        for path in MOD.rglob('*.txt'):
            if 'tests' in path.parts:
                continue
            self.assertNotIn('ac_sect_qa_startup', path.read_text(encoding='utf-8-sig'), path)

    def test_trial_places_are_ranked_once_before_activity_cleanup(self):
        source = (MOD / 'common/activities/activity_types/ac_sect_activities.txt').read_text(encoding='utf-8-sig')
        trial = source.split('activity_ac_sect_joint_training = {')[0]
        completion = trial[trial.index('on_complete = {'):]
        self.assertLess(completion.index('set_variable = { name = ac_trials_resolved'), completion.index('ordered_attending_character'))
        ranked = list(re.finditer(r'ordered_attending_character\s*=\s*\{', completion))
        self.assertEqual(len(ranked), 2)
        self.assertEqual(completion.count('order_by = var:ac_sect_trial_score'), 2)
        self.assertIn('has_variable = ac_sect_trial_paid', completion[ranked[0].start():ranked[1].start()])

    def test_recruitment_interest_does_not_start_or_fund_an_activity(self):
        source = (MOD / 'common/scripted_effects/ac_sect_recruitment_effects.txt').read_text(encoding='utf-8-sig')
        registration = source[source.index('ac_sect_register_interest_effect = {'):source.index('ac_sect_clear_interest_effect = {')]
        self.assertIn('ac_sect_recruitment_interest', registration)
        self.assertNotRegex(registration, r'\b(?:ai_attempt_to_host_activity|remove_gold|remove_short_term_gold|set_activity_host)\s*=')
        activity = (MOD / 'common/activities/activity_types/ac_sect_activities.txt').read_text(encoding='utf-8-sig')
        trial = activity.split('activity_ac_sect_joint_training = {')[0]
        fields = {f.key: f.body(trial) for f in parser.fields(trial)}
        self.assertIn('ac_sect_master_trigger = yes', fields['is_shown'])
        self.assertNotIn('ac_sect_application', fields['is_shown'])
        self.assertIn('ac_sect_trial_planner_trigger = yes', fields['can_start'])

    def test_single_location_activities_assign_all_predefined_phases(self):
        source = (MOD / 'common/activities/activity_types/ac_sect_activities.txt').read_text(encoding='utf-8-sig')
        self.assertNotIn('first_picked_phase', source)
        self.assertEqual(source.count('is_single_location = yes'), 2)
        self.assertEqual(source.count('location_source = pickable'), 5)

    def test_recruitment_schedule_and_player_notice_are_independent(self):
        source = (MOD / 'common/scripted_effects/ac_sect_recruitment_effects.txt').read_text(encoding='utf-8-sig')
        scheduling = source[source.index('ac_sect_consider_recruitment_effect = {'):source.index('ac_sect_mark_activity_started_effect = {')]
        self.assertIn('is_ai = yes', scheduling)
        self.assertIn('chance = 30', scheduling)
        self.assertNotIn('ac_sect_recruitment_interest', scheduling)
        notice = source[source.index('ac_sect_announce_trial_effect = {'):]
        self.assertIn('has_character_flag = ac_sect_recruitment_interest', notice)
        self.assertIn('can_join_activity = scope:ac_invited_trial', notice)
        self.assertNotIn('add_to_activity', notice)


if __name__ == '__main__':
    unittest.main()
