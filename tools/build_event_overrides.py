"""Build individual CK3 1.20.1 event overrides, preserving vanilla event bodies.

Run with --game-root pointing at CK3's game directory; --check is read-only.
The parser deliberately ignores braces inside quoted strings and comments.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game')


def masked(text: str) -> str:
    chars = list(text)
    quoted = comment = escaped = False
    for i, char in enumerate(text):
        if comment:
            if char == '\n':
                comment = False
            else:
                chars[i] = ' '
        elif quoted:
            if char != '\n':
                chars[i] = ' '
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '#':
            comment = True
            chars[i] = ' '
        elif char == '"':
            quoted = True
            chars[i] = ' '
    if quoted:
        raise ValueError('Unclosed quoted string')
    return ''.join(chars)


def close_brace(text: str, start: int) -> int:
    clean = masked(text)
    assert clean[start] == '{'
    depth = 0
    for i in range(start, len(clean)):
        depth += (clean[i] == '{') - (clean[i] == '}')
        if depth == 0:
            return i + 1
    raise ValueError('Unbalanced braces')


@dataclass(frozen=True)
class Field:
    key: str
    start: int
    opening: int
    end: int

    def body(self, text: str) -> str:
        return text[self.opening + 1:self.end - 1]


def fields(text: str) -> list[Field]:
    clean = masked(text)
    depth = 0
    depths = []
    for char in clean:
        depths.append(depth)
        depth += (char == '{') - (char == '}')
        if depth < 0:
            raise ValueError('Unexpected closing brace')
    if depth:
        raise ValueError('Unbalanced braces')
    result = []
    for match in re.finditer(r'\b([a-zA-Z_]\w*)\s*=\s*\{', clean):
        if depths[match.start()] == 1:
            opening = clean.index('{', match.start())
            result.append(Field(match[1], match.start(), opening, close_brace(text, opening)))
    return result


def one(text: str, key: str) -> Field:
    matches = [field for field in fields(text) if field.key == key]
    if len(matches) != 1:
        raise ValueError(f'Expected one {key}, got {len(matches)}')
    return matches[0]


def replace_body(text: str, key: str, body: str) -> str:
    field = one(text, key)
    return text[:field.opening + 1] + '\n' + body.rstrip() + '\n\t' + text[field.end - 1:]


def indent(text: str, tabs: int = 1) -> str:
    return '\n'.join('\t' * tabs + line if line else '' for line in text.strip('\n').splitlines())


@lru_cache(maxsize=4)
def event_sources(game: Path) -> dict[str, str]:
    """Index live definitions, including differently named DLC namespaces."""
    result = {}
    for path in sorted((game / 'events').rglob('*.txt')):
        for match in re.finditer(r'^([\w]+\.\d+)\s*=\s*\{', masked(path.read_text(encoding='utf-8-sig')), re.M):
            if match[1] in result:
                raise ValueError(f'Duplicate installed event: {match[1]}')
            result[match[1]] = path.relative_to(game).as_posix()
    return result


@lru_cache(maxsize=256)
def load_event(game: Path, event_id: str) -> tuple[str, str, int]:
    files = {
        'travel_danger_events.3004': 'events/travel_events/travel_danger_events_klank.txt',
        'travel_danger_events.4000': 'events/travel_events/travel_danger_events_filippa.txt',
        'travel_danger_events.2001': 'events/travel_events/travel_danger_events_dan.txt',
        'travel_danger_events.1007': 'events/travel_events/travel_danger_events.txt',
        'travel_danger_events.3005': 'events/travel_events/travel_danger_events_klank.txt',
        'travel_danger_events.3003': 'events/travel_events/travel_danger_events_klank.txt',
        'travel_danger_events.3001': 'events/travel_events/travel_danger_events_klank.txt',
        'travel_danger_events.1006': 'events/travel_events/travel_danger_events.txt',
        'travel_danger_events.3000': 'events/travel_events/travel_danger_events_klank.txt',
        'travel_events.3070': 'events/travel_events/travel_events_veronica.txt',
        'travel_danger_events.6030': 'events/travel_events/travel_danger_events_joe.txt',
        'travel_danger_events.9040': 'events/travel_events/travel_danger_events_oltner.txt',
        'travel_danger_events.6020': 'events/travel_events/travel_danger_events_joe.txt',
        'host_dinner_events.1091': 'events/activities/tour_activity/tour_phase_host_a_dinner.txt',
        'hunt.4007': 'events/activities/hunt_activity/hunt_events.txt',
        'hunt.4010': 'events/activities/hunt_activity/hunt_events.txt',
        'hold_court.6000': 'events/activities/hold_court_activity/hold_court_events_general.txt',
        'hold_court.5010': 'events/activities/hold_court_activity/hold_court_events_general.txt',
    }
    relative = files.get(event_id) or event_sources(game)[event_id]
    text = (game / relative).read_text(encoding='utf-8-sig')
    match = re.search(r'^' + re.escape(event_id) + r'\s*=\s*\{', text, re.M)
    if not match:
        raise ValueError(f'{event_id} missing in {relative}')
    end = close_brace(text, text.index('{', match.start()))
    return text[match.start():end], relative, text[:match.start()].count('\n') + 1


def add_options(text: str, options: str) -> str:
    if options.strip():
        first = next(field for field in fields(text) if field.key == 'option')
        line = text.rfind('\n', 0, first.start) + 1
        text = text[:line] + options.rstrip() + '\n\n' + text[line:]
    opening = text.index('{') + 1
    return text[:opening] + '\n\tid_override_priority = 10 # AC: individual CK3 1.20.1 event override\n' + text[opening:]


def modify_fatal(text: str, event_id: str) -> str:
    immediate = one(text, 'immediate').body(text)
    if event_id == 'travel_danger_events.6020':
        marker = '\t\t# For correct order'
        setup, separator, fatal = immediate.partition(marker)
        if not separator:
            raise ValueError('Sea-storm death sequence changed upstream')
        fatal = separator + fatal
        guard = 'ac_event_available_practitioner_trigger = { ABILITY = sea_rescue }'
        pending = 'ac_event_sea_rescue_pending'
        body = setup + '\n\t\tif = {\n\t\t\tlimit = { ' + guard + ' }\n\t\t\tsave_scope_value_as = { name = ' + pending + ' value = yes }\n\t\t}\n\t\telse = {\n' + indent(fatal, 1) + '\n\t\t}'
    else:
        fatal = immediate
        guard = 'ac_event_poison_survival_trigger = yes'
        pending = 'ac_event_poison_rescue_pending'
        body = '\t\tif = {\n\t\t\tlimit = { ' + guard + ' }\n\t\t\tsave_scope_value_as = { name = ' + pending + ' value = yes }\n\t\t}\n\t\telse = {\n' + indent(fatal, 1) + '\n\t\t}'
    text = replace_body(text, 'immediate', body)
    # An eligible cultivator may still choose the original fatal outcome.
    option = one(text, 'option')
    declined = '\n\t\tif = {\n\t\t\tlimit = { exists = scope:' + pending + ' }\n' + indent(fatal, 1) + '\n\t\t}\n\t'
    text = text[:option.end - 1] + declined + text[option.end - 1:]
    if event_id == 'host_dinner_events.1091':
        text = text.replace('desc = host_dinner_events.1091.desc', 'desc = {\n\t\tfirst_valid = {\n\t\t\ttriggered_desc = {\n\t\t\t\ttrigger = { exists = scope:ac_event_poison_rescue_pending }\n\t\t\t\tdesc = ac_event_poison_intervention_desc\n\t\t\t}\n\t\t\tdesc = host_dinner_events.1091.desc\n\t\t}\n\t}', 1)
    return text


@lru_cache(maxsize=64)
def inline_helpers(game: Path, relative: str) -> dict[str, str]:
    """Inline scripted helpers are file-local, so event overrides need copies."""
    source = (game / relative).read_text(encoding='utf-8-sig')
    result = {}
    for match in re.finditer(r'^scripted_(?:effect|trigger)\s+(\w+)\s*=\s*\{', masked(source), re.M):
        opening = source.index('{', match.start())
        result[match[1]] = source[match.start():close_brace(source, opening)]
    return result


def required_inline_helpers(game: Path, relatives: set[str], blocks: list[str]) -> str:
    candidates = {}
    origins = {}
    for relative in sorted(relatives):
        for name, body in inline_helpers(game, relative).items():
            if name in candidates and candidates[name] != body:
                raise ValueError(f'Conflicting file-local helper {name}; split these event groups')
            candidates[name] = body
            origins[name] = relative
    required = set()
    pending = '\n'.join(blocks)
    while pending:
        references = set(re.findall(r'\b(\w+)\s*=', masked(pending)))
        newly_required = references.intersection(candidates).difference(required)
        required.update(newly_required)
        pending = '\n'.join(candidates[name] for name in newly_required)
    helpers = '\n'.join('# Source: ' + origins[name] + ' (file-local helper)\n' + candidates[name] + '\n'
                        for name in sorted(required))
    # File-local @variables are not inherited by an individual event override.
    constants = {}
    for relative in sorted(relatives):
        source = (game / relative).read_text(encoding='utf-8-sig')
        clean = masked(source)
        depth = 0
        depths = []
        for char in clean:
            depths.append(depth)
            depth += (char == '{') - (char == '}')
        for match in re.finditer(r'(?m)^\s*(@\w+)\s*=\s*([^\n#]+)', source):
            if depths[match.start(1)] != 0:
                continue
            name, value = match[1], match[2].strip()
            if name in constants and constants[name] != value:
                raise ValueError(f'Conflicting file-local constant {name}; split event groups')
            constants[name] = value
    needed = set()
    pending = '\n'.join(blocks) + helpers
    while pending:
        found = set(re.findall(r'@\w+', masked(pending))).intersection(constants) - needed
        needed.update(found)
        pending = '\n'.join(constants[name] for name in found)
    declarations = ''.join(f'{name} = {constants[name]}\n' for name in sorted(needed))
    return declarations + ('\n' if declarations else '') + helpers


def rename_inline_symbols(text: str, aliases: dict[str, str]) -> str:
    """Rename helper declarations/calls without changing strings or comments.

    Despite their file-only visibility, inline helpers share a native name
    registry. Reusing the vanilla name makes one file steal the other's helper.
    """
    for match in reversed(list(re.finditer(r'\b(\w+)(?=\s*=)', masked(text)))):
        if match[1] in aliases:
            text = text[:match.start()] + aliases[match[1]] + text[match.end():]
    return text


def canonical_inline_symbols(text: str) -> str:
    aliases = {name: re.sub(r'^ac_vanilla_[a-z]+_', '', name)
               for name in re.findall(r'\bac_vanilla_[a-z]+_\w+(?=\s*=)', masked(text))}
    return rename_inline_symbols(text, aliases)


def render(game: Path) -> dict[Path, bytes]:
    from event_option_specs import SPECS, LOCALIZATION
    from event_expansion_specs import transform_event, render_triggers
    import event_activity_specs as activities

    version = json.loads((game.parent / 'launcher/launcher-settings.json').read_text(encoding='utf-8-sig'))['rawVersion']
    if version not in ('1.20.1', '1.20.1.1'):
        raise ValueError(f'Review upstream event changes before building against CK3 {version}; expected reviewed 1.20.1 or 1.20.1.1')
    groups: dict[str, list[str]] = {}
    group_sources: dict[str, set[str]] = {}
    sources = []
    for event_id, group, options in SPECS:
        vanilla, relative, line = load_event(game, event_id)
        text = modify_fatal(vanilla, event_id) if group == 'fatal' else vanilla
        text = transform_event(text, event_id)
        text = activities.transform_event(text, event_id)
        text = add_options(text, options)
        groups.setdefault(group, []).append(f'# Source: {relative}:{line}\n{text}\n')
        group_sources.setdefault(group, set()).add(relative)
        sources.append({'event': event_id, 'source': relative, 'source_sha256': hashlib.sha256(vanilla.encode()).hexdigest(), 'original_options': sum(field.key == 'option' for field in fields(vanilla)), 'added_options': sum(field.key == 'option' for field in fields(text)) - sum(field.key == 'option' for field in fields(vanilla))})
    output = {}
    output[ROOT / 'AuraClash/common/scripted_triggers/ac_event_expansion_triggers.txt'] = render_triggers().encode('utf-8-sig')
    output[ROOT / 'AuraClash/common/scripted_triggers/ac_activity_triggers.txt'] = activities.render_triggers().encode('utf-8-sig')
    output[ROOT / 'AuraClash/common/scripted_effects/ac_activity_effects.txt'] = activities.render_effects().encode('utf-8-sig')
    for group, blocks in groups.items():
        namespaces = sorted({spec[0].split('.')[0] for spec in SPECS if spec[1] == group})
        header = '# Generated by tools/build_event_overrides.py; edit event_option_specs.py, then rebuild.\n# Vanilla event bodies remain copyright Paradox Interactive; Aura Clash additions are MIT.\n# CK3 1.20.1: retain original options, scopes and after-effects.\n\n'
        helpers = required_inline_helpers(game, group_sources[group], blocks)
        # CK3's event preprocessor expects file-local @ declarations before the
        # namespaces. Putting them between namespaces and inline helpers makes
        # the native reader parse `scripted_trigger` as an event ID (1.20.1).
        declarations = ''.join(line + '\n' for line in helpers.splitlines() if line.startswith('@'))
        helpers = '\n'.join(line for line in helpers.splitlines() if not line.startswith('@'))
        header += declarations + ('\n' if declarations else '')
        header += '\n'.join('namespace = ' + namespace for namespace in namespaces) + '\n\n'
        aliases = {name: f'ac_vanilla_{group}_{name}' for name in
                   re.findall(r'^scripted_(?:effect|trigger)\s+(\w+)\s*=', helpers, re.M)}
        contents = header + helpers + '\n'.join(blocks)
        output[ROOT / f'AuraClash/events/ac_vanilla_{group}_options.txt'] = rename_inline_symbols(contents, aliases).encode('utf-8-sig')
    loc = 'l_english:\n' + ''.join(' ' + key + ':0 "' + value.replace('"', '\\"') + '"\n' for key, value in LOCALIZATION.items())
    output[ROOT / 'AuraClash/localization/english/ac_event_options_l_english.yml'] = loc.encode('utf-8-sig')
    output[ROOT / 'tools/event_override_sources.json'] = (json.dumps({'ck3_version': version, 'events': sources}, indent=2) + '\n').encode()
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, default=DEFAULT_GAME)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = render(args.game_root)
    for path, data in output.items():
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'Generated file is stale: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(('Verified' if args.check else 'Generated') + f' {len(output)} files for CK3 1.20.1.')


if __name__ == '__main__':
    main()
