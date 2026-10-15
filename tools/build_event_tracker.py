"""Generate the sorted vanilla-event register directly from the option specs.

Run after build_event_overrides.py. CSVs are readable without Excel; the JSON
also retains exact eligibility/effect scripts for reviewing scopes and costs.
"""
import argparse
import csv
import io
import json
import re
from pathlib import Path

import build_event_overrides as builder
from event_option_specs import SPECS, LOCALIZATION
from event_dlc_specs import strip_fields

ROOT = builder.ROOT
PACKS = {
    'ep1': 'Royal Court', 'ep2': 'Tours and Tournaments', 'ep3': 'Roads to Power',
    'fp1': 'Northern Lords', 'fp2': 'Fate of Iberia', 'fp3': 'Legacy of Persia',
    'bp1': 'Friends & Foes', 'bp2': 'Wards & Wardens', 'bp3': 'Wandering Nobles',
    'ce1': 'Legends of the Dead', 'mpo': 'Khans of the Steppe',
    'tgp': 'All Under Heaven', 'pam': 'By God Alone', 'ach': 'Coronations',
}


def localization(game):
    result = {}
    for root in (game / 'localization/english', ROOT / 'AuraClash/localization/english'):
        for path in sorted(root.rglob('*.yml')):
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                match = re.match(r'\s*([^#\s:]+):\s*\d*\s*"((?:[^"\\]|\\.)*)"', line)
                if match:
                    result[match[1]] = match[2].replace('\\"', '"').replace('\\n', ' ')
    result.update(LOCALIZATION)
    return result


def readable(text, loc):
    for _ in range(8):
        expanded = re.sub(r'\$([^$|]+)(?:\|[^$]*)?\$', lambda m: loc.get(m[1], m[0]), text)
        if expanded == text:
            break
        text = expanded
    text = re.sub(r'#[\w!]+\s?', '', text)
    text = re.sub(r'@(\w+)!', '', text)
    # Preserve dynamic character/holding placeholders; actual values need a save.
    text = re.sub(r'\[([a-z_]+)\|[^\]]+\]', lambda m: m[1].replace('_', ' '), text)
    return re.sub(r'\s+', ' ', text).strip()


def pack_for(source):
    match = re.search(r'events/dlc/([^/]+)/', source)
    if match:
        return PACKS.get(match[1], match[1].upper())
    for folder, pack in {
        'imperial_examination_activity': 'All Under Heaven', 'debate_activity': 'All Under Heaven',
        'festival_activity': 'All Under Heaven', 'chariot_race_activity': 'Roads to Power',
        'hold_court_activity': 'Royal Court', 'tournament_activity': 'Tours and Tournaments',
        'tournaments': 'Tours and Tournaments',
        'tour_activity': 'Tours and Tournaments', 'wedding_activity': 'Tours and Tournaments',
    }.items():
        if '/' + folder + '/' in source:
            return pack
    return 'Base game / shared activities'


def friendly_title(template):
    """Readable placeholders, with the exact localization retained separately."""
    def placeholder(match):
        expr = match[1]
        for fragment, label in [
            ('GetRegionalPoetryExam', '[regional examination]'),
            ('PilgrimageHeader', 'Pilgrimage:'), ('EventTitleDisease', '[disease]'),
            ('GetCurrentPhase', '[contest]'), ('GetVersusRound', '[round]'),
            ('GetShortName', '[activity]'), ('GetYear', '[year]'),
            ('WaterGodName', "[water god's]"), ('TricksterGodName', "[trickster god's]"),
            ('GetAnimalType', '[animal]'), ('BG_GameType', '[board game]'),
            ('RelationToMe', '[relative]'), ('GetTerrain', '[terrain]'),
            ('GetTitleAsName', '[ruler title]'), ('GetWomanMan', 'Person'),
            ('GetHerHim', '[them]'), ('epidemic.', '[epidemic]'),
            ('city_location.', '[settlement]'), ('county.', '[county]'),
        ]:
            if fragment in expr:
                return label
        return '[character]' if 'Name' in expr else '[dynamic]'
    return re.sub(r'\[([^\]]+)\]', placeholder, template)


def trigger_definitions():
    result = {}
    for path in sorted((ROOT / 'AuraClash/common/scripted_triggers').glob('*.txt')):
        source = path.read_text(encoding='utf-8-sig')
        for m in re.finditer(r'(?m)^(ac_\w+)\s*=\s*\{', source):
            opening = source.index('{', m.start())
            result[m[1]] = source[opening + 1:builder.close_brace(source, opening) - 1]
    return result


def requirements(trigger, loc, definitions):
    # A readable index of abilities; exact AND/OR logic is in requirements_script.
    expanded = trigger
    ability = re.search(r'ABILITY\s*=\s*(\w+)', expanded)
    if ability:
        expanded += '\nac_event_' + ability[1] + '_trigger = yes'
    seen = set()
    for _ in range(8):
        found = set(re.findall(r'\bac_\w+_trigger\b', expanded)) - seen
        if not found:
            break
        seen.update(found)
        expanded += '\n' + '\n'.join(definitions.get(key, '') for key in sorted(found))
    keys = set(re.findall(r'\bhas_(?:perk|trait)\s*=\s*(ac_\w+)', expanded))
    names = sorted({readable(loc.get(key + '_name', loc.get('trait_' + key, loc.get(key, key))), loc)
                    for key in keys if key != 'ac_cultivator'}, key=str.casefold)
    return '; '.join(names) if names else 'Cultivator eligibility / trained Core (see exact requirements)'


LEGACY_SUMMARIES = {
    'ac_event_aoyusumu_stampede': 'Calm the stampede, remove its county penalty, gain legitimacy and run the existing nearby-character rescue effect.',
    'ac_event_activity_pilgrim_sickness': 'Recover from ordinary illness during the pilgrimage. Uses the shared six-month healing cooldown.',
    'ac_event_plantation_fire': 'Save the workers; gain Local Hero and county rescued-worker modifiers for three years.',
    'ac_event_plantation_mido': 'Save the workers; gain Local Hero and county rescued-worker modifiers for three years.',
    'ac_event_purify_dungeon_wound': 'Remove the infected-wound character modifier. Does not cure other diseases or remove wound traits.',
    'ac_event_alchemy_compendium': 'Pay the normal medium gold cost to create a masterwork pharmaceutical book with epidemic resistance and health-penalty mitigation.',
    'ac_event_earth_graves': 'Pay for safe burial grounds; the affected county gains the safe-burials modifier for three years.',
    'ac_event_aoyusumu_doomsday': 'Fund reassurance, gain minor legitimacy and give the capital county three years of Reassured People.',
    'ac_event_martial_patrols': 'Pay for patrols; the petition county gains Cultivator Patrols for three years.',
    'ac_event_warded_patrols': 'Pay for patrols; the petition county gains Warded Patrol Posts for three years.',
}


def outcome(record, loc, key):
    if key in LEGACY_SUMMARIES:
        return LEGACY_SUMMARIES[key]
    keys = ([record['tooltip']] if record['tooltip'] else [])
    keys += re.findall(r'custom_tooltip\s*=\s*(ac_\w+)', record['effects'])
    summaries = [readable(loc[key], loc) for key in dict.fromkeys(keys) if key in loc]
    if summaries:
        return ' '.join(summaries)
    body = record['effects']
    parts = []
    if 'complete_task_contract' in body:
        result = re.search(r'complete_task_contract\s*=\s*(\w+)', body)[1]
        parts.append('Complete the native contract through ' + result.replace('_', ' ') + ', preserving its completion rewards and costs.')
    if 'escape_from_prison_effect' in body:
        parts.append('Escape prison and notify a human jailer through the native prison follow-up.')
    if 'delay_travel_plan' in body:
        delay = re.search(r'delay_travel_plan\s*=\s*\{\s*days\s*=\s*(\d+)', body)
        if delay:
            parts.append('Continue travel with a ' + delay[1] + '-day delay.')
    if 'change_opportunities' in body:
        amount = re.search(r'change_opportunities\s*=\s*(-?\d+)', body)[1]
        parts.append('Gain ' + amount + ' scheme opportunities.')
    if 'hunt_activity_success_change_effect' in body:
        amount = re.search(r'CHANGE\s*=\s*(\w+)', body)[1]
        parts.append('Native hunt success: ' + amount.replace('_', ' ') + '.')
    if 'ce1_quarantined_corpse' in body:
        parts.append('Quarantine the corpse in the affected county for ten years; the epidemic remains.')
    if 'ac_activity_contest_technique_effect' in body:
        parts.append('Native tournament skill roll: improve contest progress on success; minor setback on failure.')
    for change, label in [('activity_tournament_change_contestant_score_effect', 'Tournament progress'),
                          ('add_stress', 'Stress'), ('add_prestige', 'Prestige'),
                          ('add_piety', 'Piety'), ('change_inspiration_progress', 'Inspiration progress')]:
        values = list(dict.fromkeys(re.findall(r'\b' + change + r'\s*=\s*([-\w.]+)', body)))
        if values:
            parts.append(label + ': ' + ', '.join(v.replace('_', ' ') for v in values) + '.')
    if 'ac_heal_one_wound_effect' in body:
        parts.append('Heal one wound tier; shared six-month healing cooldown.')
    if 'ac_event_saved_companion_effect' in body:
        parts.append('Save the actual companion and apply gratitude to the practitioner.')
    if 'activity_tournament_change_contestant_score_effect' in body and not parts:
        gains = re.findall(r'SCORE\s*=\s*(\w+)', body)
        parts.append('Native tournament progress: ' + ', '.join(dict.fromkeys(gains)).replace('_', ' ') + '.')
    if not parts:
        # Always expose the real source rather than inventing an effect description.
        keys = list(dict.fromkeys(re.findall(r'\b(ac_\w+_effect)\s*=', body)))
        keys = [k for k in keys if 'exertion' not in k and 'choose_practitioner' not in k]
        parts.append('Apply ' + ', '.join(k.removeprefix('ac_event_').removesuffix('_effect').replace('_', ' ') for k in keys) + '.'
                     if keys else 'Cultivation resolution; exact effects are recorded in the registry JSON and source option.')
    return ' '.join(parts)


def build(game=builder.DEFAULT_GAME):
    loc = localization(game)
    definitions = trigger_definitions()
    events, options = [], []
    for eid, group, choices in SPECS:
        native, source, line = builder.load_event(game, eid)
        title = re.search(r'(?m)^\s*title\s*=\s*([\w.]+)\s*$', native)
        key = title[1] if title else eid + '.t'
        template = readable(loc.get(key, eid + ' (resolution)' if not choices else eid), loc)
        name = friendly_title(template)
        override = f'AuraClash/events/ac_vanilla_{group}_options.txt'
        mod = (ROOT / override).read_text(encoding='utf-8-sig')
        m = re.search(r'^' + re.escape(eid) + r'\s*=\s*\{', mod, re.M)
        if not m:
            raise ValueError('Build the event overrides first: ' + eid)
        start = mod.count('\n', 0, m.start()) + 1
        option_keys = re.findall(r'\bname\s*=\s*(ac_event_\w+)', choices)
        row = {'content_pack': pack_for(source), 'event_name': name, 'event_id': eid,
               'added_choices': len(option_keys), 'change_type': 'Added options' if option_keys else 'Linked resolution',
               'vanilla_source': f'{source}:{line}', 'mod_source': f'{override}:{start}', 'title_template': template}
        events.append(row)
        for key in option_keys:
            # Read final scripts, including legacy choices specialized through
            # string substitution after their shared template was generated.
            wrapper = 'wrapper = {' + choices + '}'
            body = next(f.body(wrapper) for f in builder.fields(wrapper)
                        if f.key == 'option' and re.search(r'\bname\s*=\s*' + re.escape(key) + r'\b', f.body(wrapper)))
            trigger = builder.one('wrapper = {' + body + '}', 'trigger').body('wrapper = {' + body + '}')
            record = {'label': LOCALIZATION[key], 'trigger': trigger,
                      'effects': strip_fields(body, {'name', 'trigger', 'ai_chance', 'reason'}), 'tooltip': None}
            effects = record['effects']
            cost = ('Major: +40 stress; 6 months Overextended Chi; +100 cultivation XP'
                    if 'ac_event_great_exertion_effect' in effects else
                    'Standard: +15 stress; 3 months Spent Chi; +25 cultivation XP'
                    if 'ac_event_exertion_effect' in effects else 'No cultivation exertion')
            cost += ' (other native costs may apply)'
            options.append({**{k: row[k] for k in ('content_pack', 'event_name', 'event_id')},
                            'added_option': readable(record['label'], loc),
                            'ability_index': requirements(record['trigger'], loc, definitions),
                            'outcome': outcome(record, loc, key), 'exertion': cost, 'option_key': key,
                            'vanilla_source': row['vanilla_source'], 'mod_source': row['mod_source'],
                            'requirements_script': record['trigger'], 'effects_script': effects})
    sortkey = lambda row: (row['content_pack'].casefold(), row['event_name'].casefold(), row['event_id'], row.get('option_key', ''))
    events.sort(key=sortkey)
    options.sort(key=sortkey)
    return {'ck3_version': '1.20.1', 'sort': 'Content pack, event name, event ID, option key',
            'scope': 'All modified vanilla event integrations, including linked resolution events. Dynamic names depend on the save. Ability index lists referenced abilities; exact requirements retain AND/OR and presence checks.',
            'events': events, 'options': options}


def outputs(data):
    result = {ROOT / 'docs/event-registry.json': (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')}
    for name, keys in [('events', list(data['events'][0])),
                       ('event-options', [k for k in data['options'][0] if not k.endswith('_script')])]:
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, keys, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(data['events' if name == 'events' else 'options'])
        result[ROOT / f'docs/{name}.csv'] = stream.getvalue().encode('utf-8-sig')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = build()
    stale = []
    for path, payload in outputs(data).items():
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if stale:
        raise SystemExit('Tracker is stale: ' + ', '.join(stale))
    print(f"{'Checked' if args.check else 'Generated'} tracker: {len(data['events'])} events, {len(data['options'])} options.")
