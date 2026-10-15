"""Activity techniques for CK3 1.20.1; ordinary single combat is out of scope.

Contest techniques change the native progress score, not the declared winner.
The original choices remain available. Only the explicitly listed injury setup
and bookkeeping receive surgical transformations.
"""
from textwrap import indent
import re


ABILITIES = {
    'aki_edge': 'has_perk = ac_3_style_akakiru_a_perk',
    'aki_pike': 'has_perk = ac_3_style_akakiru_c_perk',
    'aki_ranks': 'has_perk = ac_3_style_akakiru_d_perk',
    'aki_duelist': 'has_perk = ac_3_style_akakiru_g_perk',
    'mido_body': 'has_perk = ac_3_style_midorikatai_a_perk',
    'mido_line': 'has_perk = ac_3_style_midorikatai_c_perk',
    'mido_strengthen': 'has_perk = ac_3_style_midorikatai_d_perk',
    'mido_rider': 'has_perk = ac_3_style_midorikatai_f_perk',
    'mido_breaker': 'has_perk = ac_3_style_midorikatai_g_perk',
    'mido_endurance': 'has_perk = ac_3_style_midorikatai_i_perk',
    'aoyu_calm': 'has_perk = ac_3_style_aoyusumu_b_perk',
    'aoyu_mirror': 'has_perk = ac_3_style_aoyusumu_c_perk',
    'aoyu_prayer': 'has_perk = ac_3_style_aoyusumu_h_perk',
    'kii_academy': 'has_perk = ac_3_style_kiihakai_h_perk',
    'hunt_tracks': 'OR = { has_perk = ac_3_style_kiihakai_d_perk has_perk = ac_4_element_earth_e_perk }',
    'pit_escape': 'OR = { ac_event_fall_rescue_trigger = yes ac_event_rubble_trigger = yes ac_activity_mido_body_trigger = yes }',
}

# These modifications are reviewed explicitly by the preservation tests.
SETUP_CHANGES = {'hunt_events_anna.0010', 'feast_default.6351'}
OPTION_CHANGES = {'hunt_events_anna.0010'}


def render_triggers():
    return '# Generated from tools/event_activity_specs.py.\n' + '\n'.join(
        f'ac_activity_{key}_trigger = {{\n\tac_event_practitioner_trigger = yes\n\t{condition}\n}}\n'
        for key, condition in ABILITIES.items())


def render_effects():
    return '''# Activity contest techniques; no ordinary single-combat hooks.
# The contestant can be the owner of a horse while the practitioner is its jockey.
ac_activity_contest_technique_effect = {
    save_scope_as = ac_activity_contestant
    remove_character_flag = success_pivotal_flag
    remove_character_flag = neutral_pivotal_flag
    remove_character_flag = failure_pivotal_flag
    $PRACTITIONER$ = {
        duel = {
            skill = $SKILL$
            value = decent_skill_rating
            70 = {
                desc = ac_event_activity_technique_success
                compare_modifier = { value = scope:duel_value multiplier = 2 min = -69 }
                modifier = {
                    add = 15
                    has_trait_xp = { trait = ac_cultivator track = $CORE$ value >= 50 }
                }
                modifier = {
                    factor = 0.75
                    scope:versus_contestant ?= { has_trait = ac_cultivator }
                    exists = scope:versus_contestant
                }
                scope:ac_activity_contestant = {
                    activity_tournament_change_contestant_score_effect = { SCORE = increase_$GAIN$ }
                    add_character_flag = { flag = success_pivotal_flag days = 30 }
                }
            }
            30 = {
                desc = ac_event_activity_technique_failure
                compare_modifier = { value = scope:duel_value multiplier = -2 min = -29 }
                scope:ac_activity_contestant = {
                    activity_tournament_change_contestant_score_effect = { SCORE = decrease_minor }
                    add_character_flag = { flag = failure_pivotal_flag days = 30 }
                }
            }
        }
    }
}
'''


def original(event_id):
    from build_event_overrides import DEFAULT_GAME, load_event
    return load_event(DEFAULT_GAME, event_id)[0]


def native_option(event_id, name):
    from build_event_overrides import fields
    text = original(event_id)
    return next(f.body(text) for f in fields(text) if f.key == 'option'
                and re.search(r'\bname\s*=\s*' + re.escape(name) + r'\b', f.body(text)))


def native_block(text, key):
    from build_event_overrides import close_brace
    m = re.search(r'\b' + re.escape(key) + r'\s*=\s*\{', text)
    if not m:
        raise ValueError(f'Missing native block {key}')
    opening = text.index('{', m.start())
    return text[m.start():close_brace(text, opening)]


def score(amount='minor'):
    return 'activity_tournament_change_contestant_score_effect = { SCORE = increase_' + amount + ' }'


def register(base):
    option, exert, loc = (base[k] for k in ('option', 'exert', 'LOCALIZATION'))
    specs = {}

    def add(eid, *choices):
        specs.setdefault(eid, []).extend(choices)

    def own(key, label, gate, effects, extra='', tip=None, major=False, cost=True):
        return option('activity_' + key, label, gate + ' ' + extra,
                      'save_scope_as = ac_event_practitioner\n' + effects +
                      ('\n' + exert(major) if cost else ''), tip)

    def ability(key):
        return ('ac_activity_' if key in ABILITIES else 'ac_event_') + key + '_trigger = yes'

    def roll(practitioner='root', skill='prowess', core='ac_core_power', gain='medium'):
        return ('ac_activity_contest_technique_effect = { PRACTITIONER = ' + practitioner +
                f' SKILL = {skill} CORE = {core} GAIN = {gain} }}')

    loc.update({
        'ac_event_activity_technique_success': 'Your cultivation improves your position in this contest.',
        'ac_event_activity_technique_failure': 'Your opponent withstands the technique, costing you ground.',
        'ac_event_activity_roll_tt': 'Your technique has an improved chance of gaining contest progress. Your skill and core training affect the roll; a cultivating opponent is harder to overcome. It does not guarantee victory.',
        'ac_event_activity_board_tt': 'Foresee one strong move using a skill supported by this game. Opposing Precognition reduces the advantage. Normal counters, scoring, stakes and match resolution still apply. Usable once per day.',
        'ac_event_activity_pit_desc': 'The ground gives way beneath me, and I fall into a hidden pit. Before I strike the bottom, I reach for my cultivation. There may yet be a way to land safely and escape.',
        'ac_event_activity_pit_tt': 'Your technique prevents the fall injury and gets you out without another injury roll.',
        'ac_event_activity_wrestle_desc': 'My opponent locks an arm around my neck and tightens the hold. The pressure builds frighteningly quickly. I must reinforce my stance and break free before something snaps.',
        'ac_event_activity_wrestle_safe_tt': 'Break the dangerous headlock without the event\'s death or permanent-disfigurement outcomes. This does not guarantee winning the bout.',
        'ac_event_activity_joust_safe_tt': 'Use Iron Body to continue this pass without the event\'s additional wound. This does not guarantee winning the joust.',
        'ac_event_activity_pilgrim_calm_tt': 'Restore order and organize the rescue. Your companion still faces the normal risk of drowning; calming alone does not lift someone from the sea.',
        'ac_event_activity_repair_tt': 'Pay for materials and restore only the durability lost in this brawl. Older damage remains.',
        'ac_event_activity_jockey_prepare_tt': 'Choose this jockey through the normal selection process and gain a small preparation advantage. You must be present to assist. The jockey does not gain your cultivation.',
        'ac_event_activity_jockey_treat_tt': 'Mend one wound tier on the jockey who is here. Uses the shared six-month healing cooldown.',
        'ac_event_activity_collision_tt': 'Recover only the small contest-score penalty your horse suffered in this collision. The other horse\'s result is unchanged.',
        'ac_event_activity_escape_tt': 'Escape the murder feast using the normal survivor bookkeeping. Your companions and the guest of honor still face the original outcomes.',
        'ac_event_activity_child_tt': 'Teach calm breathing and ordinary archery. The child receives hunting practice, not cultivation advancement.',
    })

    # Ordinary board games: use a supported move, never inspect an unchosen move.
    moves = []
    for i, skill in enumerate(('diplomacy', 'martial', 'stewardship', 'intrigue', 'learning', 'prowess')):
        moves.append(('if' if i == 0 else 'else_if') + ' = {\n'
                     f'    limit = {{ scope:bg_skill_a = flag:{skill} }}\n'
                     '    if = { limit = { this = scope:bg_defender }\n'
                     f'        save_scope_value_as = {{ name = bg_defender_move value = flag:{skill} }}\n'
                     '    }\n    else = {\n'
                     f'        save_scope_value_as = {{ name = bg_attacker_move value = flag:{skill} }}\n'
                     '    }\n}')
    moves.append('''if = {
    limit = { scope:bg_opponent = { ac_event_precognition_trigger = yes } }
    set_variable = { name = bg_move_result value = flag:success }
}
else = { set_variable = { name = bg_move_result value = flag:crit_success } }
add_character_flag = { flag = ac_activity_board_foresight days = 1 }''')
    add('board_games.0001', own('board_foresight', 'I have seen where this line of play leads.',
        ability('precognition'), '\n'.join(moves),
        'exists = scope:bg_skill_a NOT = { has_character_flag = ac_activity_board_foresight }',
        'ac_event_activity_board_tt'))
    for eid, label in [
        ('contest_events.0863', 'I have already seen the decisive sequence.'),
        ('contest_events.5520', 'A glimpse ahead will tell me whether this gambit holds.'),
        ('contest_events.5530', 'I need no hidden piece. I can see the winning line.')]:
        add(eid, own('board_' + eid.split('.')[1], label, ability('precognition'),
                     roll(skill='learning', core='ac_core_soul'),
                     'scope:pivotal_contestant ?= root' if eid.endswith('0863') else '',
                     'ac_event_activity_roll_tt'))

    # Main contest decisions. No vanilla delayed-roll flag is armed here.
    techniques = {
        'contest_events.0610': [
            ('aki_ranks', 'Close ranks! We advance as one.', 'martial', 'ac_core_power', 'major'),
            ('mido_line', 'Rally on me. Our line will not break.', 'martial', 'ac_core_fortitude', 'medium'),
            ('mido_breaker', 'Follow me through the breach!', 'prowess', 'ac_core_power', 'major')],
        'contest_events.0860': [
            ('aki_pike', 'Steady lance, perfect line. Let the charge do the work.', 'martial', 'ac_core_agility', 'medium'),
            ('mido_rider', 'My mount and I will meet this charge together.', 'martial', 'ac_core_power', 'medium'),
            ('mido_body', 'Brace the Iron Body. Hold the saddle.', 'prowess', 'ac_core_fortitude', 'medium')],
        'contest_events.0861': [
            ('mido_body', 'An Iron Body is no easy thing to pin.', 'prowess', 'ac_core_fortitude', 'medium'),
            ('mido_line', 'Root my stance. Turn the hold against them.', 'martial', 'ac_core_fortitude', 'medium'),
            ('mido_breaker', 'Break the pin with one explosive reversal!', 'prowess', 'ac_core_power', 'major')],
        'contest_events.0862': [
            ('aki_duelist', 'One precise counter. Their weapon, not their life.', 'martial', 'ac_core_agility', 'medium'),
            ('aki_edge', 'Press them with the Crimson Edge!', 'prowess', 'ac_core_power', 'major'),
            ('mido_body', 'Let their attack break against my guard.', 'prowess', 'ac_core_fortitude', 'medium'),
            ('mido_breaker', 'Their guard cannot withstand this pressure.', 'prowess', 'ac_core_power', 'major')],
        'contest_events.0711': [
            ('aoyu_calm', 'Let my breath settle, and the words flow.', 'diplomacy', 'ac_core_soul', 'medium'),
            ('aoyu_prayer', 'I will give voice to the prayers we share.', 'diplomacy', 'ac_core_soul', 'major'),
            ('precognition', 'I have glimpsed which verse will move them.', 'learning', 'ac_core_soul', 'major'),
            ('kii_academy', 'A disciplined mind will give this verse its shape.', 'learning', 'ac_core_soul', 'medium')],
    }
    for eid, choices in techniques.items():
        for key, label, skill, core, gain in choices:
            add(eid, own(eid.replace('.', '_') + '_' + key, label, ability(key),
                         roll(skill=skill, core=core, gain=gain),
                         'scope:pivotal_contestant = root', 'ac_event_activity_roll_tt'))

    # Flavor events: each technique has its own perk gate and contest effect.
    flavor = {
        'ep2_tournament_events.1003': [
            ('aki_duelist', 'Keep my footing. Recover the blade in one clean motion.'),
            ('mido_body', 'Make room! I will force my way back to my weapon.')],
        'ep2_tournament_events.1007': [
            ('mido_strengthen', 'Gather close. Let me strengthen those who are flagging.'),
            ('aki_ranks', 'Reform the ranks. We return to the melee together.')],
        'ep2_tournament_events.1017': [
            ('aki_ranks', 'With me! We will catch these three between us.'),
            ('mido_breaker', 'Stand aside. I am breaking through!')],
        'ep2_tournament_events.0010': [
            ('aki_duelist', 'I know this feint. Let the blade pass, then counter.'),
            ('mido_body', 'Brace, close the distance, and turn this into a grapple.')],
        'ep2_tournament_events.0011': [
            ('aki_duelist', 'The other hand knows the blade just as well.'),
            ('mido_endurance', 'Pain cannot loosen my resolve. Change the grip and fight.')],
        'ep2_tournament_events.4003': [
            ('aki_pike', 'That cumbersome lance leaves an opening. I will take it.'),
            ('mido_rider', 'A steady mount and seat will withstand this pass.')],
        'ep2_tournament_events.4004': [
            ('aki_duelist', 'On foot? Gladly. Let us see your bladework.'),
            ('mido_body', 'On foot, my stance will be stronger still.')],
        'ep2_tournament_events.4008': [
            ('mido_rider', 'Easy, now. Trust my hands, not the shouting.'),
            ('aoyu_calm', 'Find stillness amid the noise. Keep the horse settled.')],
        'ep2_tournament_events.2001': [
            ('mido_body', 'Keep the dirt. My strength will break this hold.')],
        'ep2_tournament_events.2501': [
            ('mido_line', 'Root my stance and let them tire themselves.'),
            ('mido_body', 'Secure a crushing body grapple.'),
            ('mido_breaker', 'Commit to one powerful takedown!')],
        'ep2_tournament_events.2502': [
            ('mido_endurance', 'Favor the sound hand. My endurance will carry me through.')],
    }
    for eid, choices in flavor.items():
        for key, label in choices:
            effects = roll(core='ac_core_fortitude' if key in ('mido_line', 'mido_endurance', 'mido_body') else 'ac_core_power')
            if eid.endswith('.1003'):
                # The weapon was unequipped in setup; restore the same artifact.
                effects = 'scope:tournament_weapon = { equip_artifact_to_owner = yes }\n' + score()
            elif eid.endswith('.1007'):
                effects = '\n'.join(f'scope:teammate_{i} = {{ {score()} }}' for i in (1, 2, 3)) + '\n' + score()
            add(eid, own(eid.replace('.', '_') + '_' + key, label, ability(key), effects,
                         tip='ac_event_activity_roll_tt' if 'technique_effect' in effects else None))

    add('ep2_tournament_events.4001', own('joust_iron_body', 'Seal my stance with chi. I can safely continue.',
        ability('mido_body'), score(), tip='ac_event_activity_joust_safe_tt'))
    # Death occurs in the native choice, not in setup. The new choice bypasses it.
    add('ep2_tournament_events.2506', own('neck_iron_body', 'Reinforce my neck. Break the hold before it snaps!',
        ability('mido_body'), score(), tip='ac_event_activity_wrestle_safe_tt', major=True))

    recitals = {
        'contest_events.5000': [('aoyu_mirror', 'Their insults will find only a composed reply.'), ('kii_academy', 'Answer with a learned verse sharper than any insult.')],
        'contest_events.5020': [('aoyu_prayer', 'Let the encore speak to their deepest hopes.'), ('kii_academy', 'One polished encore, drawn from a well-trained memory.')],
        'contest_events.5030': [('aoyu_calm', 'Breathe. Begin the next verse with a steadier voice.'), ('kii_academy', 'Rework the meter. I can still save this composition.')],
        'ep2_tournament_events.5501': [('aoyu_calm', 'The words may be alike. My delivery will make them mine.'), ('kii_academy', 'I have studied enough verse to compose another.')],
        'ep2_tournament_events.5503': [('aoyu_calm', 'Let the Calming Current restore my voice.'), ('kii_academy', 'Recall the practiced opening. The rest will follow.')],
        'ep2_tournament_events.5504': [('aoyu_calm', 'Thunder will not shake my composure.'), ('kiihakai_barrier', 'A barrier over the dais will keep this recital going.')],
    }
    for eid, choices in recitals.items():
        for key, label in choices:
            add(eid, own(eid.replace('.', '_') + '_' + key, label, ability(key),
                         roll(skill='learning' if key == 'kii_academy' else 'diplomacy', core='ac_core_soul'),
                         tip='ac_event_activity_roll_tt'))

    # Final Lap uses the actual jockey's cultivation and charges their exertion.
    for key, label, skill, core in [
        ('mido_rider', '[jockey.GetFirstNameNoTooltip], use Beast Riders to find the opening!', 'martial', 'ac_core_power'),
        ('precognition', '[jockey.GetFirstNameNoTooltip], follow the line you have foreseen!', 'learning', 'ac_core_soul'),
        ('kiihakai_barrier', '[jockey.GetFirstNameNoTooltip], shield the dangerous turn with chi!', 'martial', 'ac_core_fortitude')]:
        add('contest_events.0510', option('activity_final_lap_' + key, label,
            'scope:pivotal_contestant = root scope:jockey = { ' + ability(key) + ' location = root.location }',
            'scope:jockey = { save_scope_as = ac_event_practitioner }\n' + roll('scope:jockey', skill, core) + '\n' + exert(),
            'ac_event_activity_roll_tt'))
    # Preserve all three native candidates and the jockey-selection effect.
    for i in (1, 2, 3):
        for key, label in [('kiihakai_ward', 'ward the equipment'), ('aoyu_calm', 'settle their nerves'), ('mido_rider', 'coach their horse handling')]:
            add('ep2_tournament_events.4500', own(f'prepare_jockey_{i}_{key}',
                f'I choose [jockey{i}.GetFirstNameNoTooltip]. Let me {label}.', ability(key),
                f'scope:jockey{i} = {{ tournament_choose_jockey_effect = yes accolade_medium_glory_gain_with_checks_effect = yes }}\n' + score(),
                f'scope:jockey{i} = {{ is_alive = yes location = root.location }}', 'ac_event_activity_jockey_prepare_tt'))
    for eid in ('jason_first_race_event.1', 'contest_events.3010'):
        present = 'scope:jockey = { is_alive = yes location = root.location }'
        for key, label in [('mido_rider', 'Steady hands and a familiar voice will restore control.'), ('aoyu_calm', 'Breathe slowly. Let horse and rider settle together.')]:
            add(eid, own(eid.replace('.', '_') + '_' + key, label, ability(key), score(), present,
                         'ac_event_activity_collision_tt' if eid.startswith('jason') else None))
        if eid.startswith('jason'):
            add(eid, own('collision_barrier', 'Keep the stricken pair safe behind my barrier.',
                         ability('kiihakai_barrier'), score(), present, 'ac_event_activity_collision_tt'))
        else:
            add(eid, own('jockey_mending', 'Bring the jockey here. Mending Chi will close those wounds.',
                ability('kiihakai_mending'), 'scope:jockey = { ac_heal_one_wound_effect = yes }\nac_event_chi_healing_cooldown_effect = yes',
                present + ' scope:jockey = { has_trait = wounded }', 'ac_event_activity_jockey_treat_tt'))

    # Hunts, pilgrimages, social activities and tours from the approved batch.
    add('hunt.8050', own('hunt_tracks', 'Chi will show which tracks are fresh. Follow this trail.',
                         ability('hunt_tracks'), 'hunt_activity_success_change_effect = { CHANGE = increase_major }'))
    for key, label in [('fall_rescue', 'Cushion the fall, then lift myself out on the wind.'),
                       ('rubble', 'Shape footholds in the earth and climb out.'),
                       ('mido_body', 'An Iron Body can survive the landing and climb back out.')]:
        add('hunt_events_anna.0010', own('pit_' + key, label, ability(key), 'add_prestige = 25', tip='ac_event_activity_pit_tt'))
    add('hunt_events_anna.0015', own('child_breathing', 'Breathe with me. Steady the bow, then release.', ability('aoyu_calm'), '''scope:child_with_bow = {
    if = { limit = { NOT = { has_trait = lifestyle_hunter } } add_trait = lifestyle_hunter }
    add_trait_xp = { trait = lifestyle_hunter track = hunter value = 5 }
    add_stress = -15
}''', 'scope:child_with_bow = { is_alive = yes }', 'ac_event_activity_child_tt'))
    for key, label in [('mido_subdue', 'Be still. There is no prey for you here.'), ('aoyu_calm', 'Still my breathing. Withdraw without alarming the beast.')]:
        add('hunt.8580', own('stare_' + key, label, ability(key), 'hunt_activity_success_change_effect = { CHANGE = increase_minor }'))
    for key, label in [('aoyu_calm', 'Calm yourselves. This contest is no cause for bloodshed.'), ('bind_looters', 'Bind their hands until tempers cool.'), ('kiihakai_barrier', 'A barrier between them will end this brawl.')]:
        # Binding Wards is the school-specific alternative to Handseal formations.
        gate = 'ac_event_practitioner_trigger = yes has_perk = ac_3_style_kiihakai_e_perk' if key == 'bind_looters' else ability(key)
        add('tournament_events.1410', own('fans_' + key, label, gate, 'add_prestige = 25'))
    add('pilgrimage.1100', own('pilgrim_overboard_water_rescue', 'The waves will return our companion to us.',
        ability('water_rescue'),
        'ac_event_saved_companion_effect = { COMPANION = scope:victim_pilgrim }\npilgrimage_st_elmo_success_effect = yes',
        'scope:victim_pilgrim = { is_alive = yes }'))
    # Reassurance is available independently of an elemental rescue. Keep the
    # original drowning risk, including its family-opinion consequences.
    calm_risk = native_block(native_option('pilgrimage.1100', 'pilgrimage.1100.a'), 'if')
    add('pilgrimage.1100', own('pilgrim_overboard_aoyu_calm', 'Keep calm. We will organize the rescue together.',
        ability('aoyu_calm'), calm_risk + '''
scope:panicked_pilgrim ?= { add_stress = -20 }
pilgrimage_st_elmo_success_effect = yes''', tip='ac_event_activity_pilgrim_calm_tt'))
    add('pilgrimage.2008', own('pilgrim_sickness', 'A tested remedy will carry me through this sickness.',
        ability('illness_healer'), 'recover_from_disease_effect = { DISEASE = ill }\nac_event_chi_healing_cooldown_effect = yes',
        'has_trait = ill'))
    ritual = '''pious_type_option_effect = yes
add_piety = minor_piety_gain
if = { limit = { has_trait = pilgrim } add_trait_xp = { trait = pilgrim value = 5 } }'''
    for key, label in [('water', 'Make room in the sacred waters. I will guide the current.'), ('aoyu_prayer', 'Let us pray and cleanse ourselves together, high and low alike.')]:
        add('pilgrimage.3201', own('ritual_' + key, label, ability(key), ritual))
    for key, label in [('precognition', 'I saw this ambush. We will leave by the path you failed to watch.'), ('aoyusumu_exorcism', 'I will answer your threats with the Exorcist\'s Rite.')]:
        add('pilgrimage.6532', own('pilgrim_ambush_' + key, label, ability(key), 'add_piety = 50'))
    add('feast_default.6351', own('feast_runes', 'Fetch materials. I will restore the damaged runes myself.',
        ability('kiihakai_runes'), '''remove_short_term_gold = tiny_gold_value
scope:feast_target_artifact = { add_durability = scope:ac_activity_brawl_damage }''',
        'exists = scope:feast_target_artifact exists = scope:ac_activity_brawl_damage', 'ac_event_activity_repair_tt'))

    # Reuse native survivor bookkeeping AND the original companion/guest outcomes.
    from build_event_overrides import close_brace
    victim = native_option('feast_default.8004', 'feast_default.8004.a')
    duel = native_block(victim, 'duel')
    m = re.search(r'^\s*40\s*=\s*\{', duel, re.M)
    opening = duel.index('{', m.start())
    survivor = duel[opening + 1:close_brace(duel, opening) - 1]
    # Strip random-weight metadata from the selected outcome, retaining all effects.
    compare = native_block(survivor, 'compare_modifier')
    survivor = survivor.replace(compare, '', 1)
    survivor = re.sub(r'^\s*min\s*=\s*5\s*$', '', survivor, flags=re.M)
    survivor = re.sub(r'^\s*desc\s*=\s*feast_default\.8004\.a\.tt\.failure\s*$', '', survivor, flags=re.M)
    tail = victim[victim.index(duel) + len(duel):]
    for key, label in [('precognition', 'I saw this betrayal. The escape route is already clear.'), ('shadow_escape', 'A shadow slips between the closing doors.'), ('kiihakai_barrier', 'Hold their blades behind a barrier while I escape!')]:
        add('feast_default.8004', own('murder_feast_' + key, label, ability(key), survivor + tail,
                                     tip='ac_event_activity_escape_tt', major=True))
    # A Chance to Perform is intentionally excluded: its spar is a one-on-one duel
    # outside tournaments, which the user explicitly deferred.
    prey_success = native_option('tour_grounds_events.3003', 'tour_grounds_events.3003.a')
    d = native_block(prey_success, 'duel')
    m = re.search(r'^\s*50\s*=\s*\{', d, re.M)
    opening = d.index('{', m.start())
    success = d[opening + 1:close_brace(d, opening) - 1]
    success = success.replace(native_block(success, 'compare_modifier'), '', 1)
    success = success.replace(native_block(success, 'modifier'), '', 1)
    for key, label in [('burial_earth', 'Shape a safe ledge before I approach the prey.'), ('wind_arrows', 'Let the wind guide my shot across the precipice.')]:
        add('tour_grounds_events.3003', own('tour_prey_' + key, label, ability(key), success))
    add('funeral.1060', own('comfort_mourner', 'There is no need to grieve alone. Let me hear you.',
        ability('aoyu_prayer'), '''scope:other_mourner = {
    add_stress = -30
    add_opinion = { target = root modifier = grateful_opinion opinion = 20 }
}
add_piety = 50''', 'scope:other_mourner = { is_alive = yes }'))
    for eid, choices in specs.items():
        base['add'](eid, 'activities', *choices)


def transform_event(text, event_id):
    from build_event_overrides import one, fields, replace_body
    if event_id == 'hunt_events_anna.0010':
        injury = one(text, 'immediate').body(text)
        text = replace_body(text, 'immediate', '''
        # AC: defer the landing injury until an eligible cultivator chooses.
        if = {
            limit = { ac_activity_pit_escape_trigger = yes }
            save_scope_value_as = { name = ac_activity_pit_pending value = yes }
        }
        else = {
''' + indent(injury, '\t') + '\n        }\n')
        # Declining cultivation still pays the original landing injury.
        for field in reversed([f for f in fields(text) if f.key == 'option']):
            text = text[:field.opening + 1] + '''
        if = { limit = { exists = scope:ac_activity_pit_pending }
''' + indent(injury, '\t') + '\n        }\n\t' + text[field.opening + 1:]
        text = text.replace('desc = hunt_events_anna.0010.desc', '''desc = {
        first_valid = {
            triggered_desc = { trigger = { exists = scope:ac_activity_pit_pending } desc = ac_event_activity_pit_desc }
            desc = hunt_events_anna.0010.desc
        }
    }''', 1)
    elif event_id == 'feast_default.6351':
        # Record the exact damage roll once, rather than repairing unrelated wear.
        body = one(text, 'immediate').body(text)
        damage = native_block(body[body.index('#...and damage it a bit'):], 'add_durability')
        expr = damage[damage.index('{') + 1:damage.rfind('}')]
        new = '''save_scope_value_as = { name = ac_activity_brawl_damage value = {\n''' + expr + '''
            multiply = -1
        } }
        add_durability = { value = scope:ac_activity_brawl_damage multiply = -1 }'''
        body = body.replace(damage, new, 1)
        text = replace_body(text, 'immediate', body)
    elif event_id == 'ep2_tournament_events.2506':
        text = text.replace('desc = ep2_tournament_events.2506.desc', '''desc = {
        first_valid = {
            triggered_desc = { trigger = { ac_activity_mido_body_trigger = yes } desc = ac_event_activity_wrestle_desc }
            desc = ep2_tournament_events.2506.desc
        }
    }''', 1)
    return text
