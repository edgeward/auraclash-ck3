"""Cultivation in DLC, civil activities and physical harm events (CK3 1.20.1).

Use each activity's native scoring and completion path. No single-combat event
or combat resolver is overridden. Source options and setup remain intact.
"""
import re
from event_activity_specs import ABILITIES, native_option, native_block


def gate(ability):
    return ('ac_activity_' if ability in ABILITIES else 'ac_event_') + ability + '_trigger = yes'


def strip_fields(body, names):
    """Remove direct UI/weight metadata while preserving nested gameplay effects."""
    from build_event_overrides import fields, masked
    wrapper = 'wrapper = {' + body + '}'
    spans = [(f.start, f.end) for f in fields(wrapper) if f.key in names]
    clean = masked(wrapper)
    depth = 0
    depths = []
    for char in clean:
        depths.append(depth)
        depth += (char == '{') - (char == '}')
    for m in re.finditer(r'(?m)^[ \t]*(\w+)\s*=\s*[^\n{]+$', wrapper):
        keypos = m.start(1)
        if depths[keypos] == 1 and m[1] in names:
            spans.append((m.start(), m.end()))
    for start, end in sorted(set(spans), reverse=True):
        wrapper = wrapper[:start] + wrapper[end:]
    return wrapper[len('wrapper = {'):-1].strip()


def effects(eid, name):
    return strip_fields(native_option(eid, name), {
        'name', 'trigger', 'show_as_unavailable', 'ai_chance', 'reason',
        'flavor', 'trait', 'skill', 'custom_tooltip', 'add_internal_flag'})


def winning_branch(eid, name, weight):
    from build_event_overrides import close_brace
    source = native_option(eid, name)
    parent = native_block(source, 'duel')
    m = re.search(r'(?m)^\s*' + str(weight) + r'\s*=\s*\{', parent)
    if not m:
        raise ValueError(f'Missing native success branch: {eid} {weight}')
    opening = parent.index('{', m.start())
    body = parent[opening + 1:close_brace(parent, opening) - 1]
    return strip_fields(body, {'compare_modifier', 'modifier', 'min', 'desc', 'show_chance',
                              'inspection_activity_options_positive_modifier'})


def boosted_check(source):
    """Keep the real native skill contest, adding a bounded cultivation edge."""
    # The first outcome is the native success branch. Do not change its prize.
    return source.replace('compare_modifier = {', '''modifier = { add = 20 }
                compare_modifier = {''', 1)


def exam_attempt(exam):
    return '''# AC: borrow one advantage for this attempt, then restore prior preparation.
if = {
    limit = { has_variable = has_exam_advantage }
    save_scope_value_as = { name = ac_dlc_prior_exam_advantage value = var:has_exam_advantage }
    change_variable = { name = has_exam_advantage add = 1 }
}
else = { set_variable = { name = has_exam_advantage value = 1 } }
imperial_examination_set_up_exam_advantage_scope = yes
imperial_examination_exam_duel_effect = { EXAM = ''' + exam + ''' }
if = {
    limit = { exists = scope:ac_dlc_prior_exam_advantage }
    set_variable = { name = has_exam_advantage value = scope:ac_dlc_prior_exam_advantage }
    clear_saved_scope = ac_dlc_prior_exam_advantage
}
else = { remove_variable = has_exam_advantage }
'''


def register(base):
    option, exert, loc = (base[k] for k in ('option', 'exert', 'LOCALIZATION'))
    specs = {}

    def add(eid, key, label, ability, body, outcome, *, extra='', major=False, cost=True):
        requirement = gate(ability) if ability else 'ac_event_practitioner_trigger = yes'
        requirement += ' ' + extra
        tooltip = 'ac_event_dlc_' + key + '_tt'
        loc[tooltip] = outcome
        choices = option('dlc_' + key, label, requirement,
                         'save_scope_as = ac_event_practitioner\n' + body +
                         ('\n' + exert(major) if cost else ''), tooltip)
        specs.setdefault(eid, []).append(choices)

    # Governance contracts: retain the contract's own cost/reward resolution.
    for key, ability, label, result in [
        ('bridge_earth', 'burial_earth', 'Shape sound supports while the builders lay the span.', 'slower_replacement'),
        ('bridge_runes', 'kiihakai_runes', 'Reinforce the new bridge with carefully laid runes.', 'slower_replacement'),
        ('bridge_water', 'water', 'A controlled current will carry the ferry safely across.', 'ferry_crossing')]:
        add('tgp_governor_contract_event.0025', key, label, ability,
            f'scope:ongoing_contract = {{ complete_task_contract = {result} }}',
            'Complete the existing bridge contract through its reconstruction or ferry outcome, preserving its costs and rewards.',
            extra='exists = scope:ongoing_contract location = scope:ongoing_destination')

    rescue_healer = '''small_mandala_piety_reward_effect = yes
add_to_entourage_court_and_activity_effect = { CHAR_TO_ADD = scope:local_character_2 NEW_COURT_OWNER = root }'''
    add('tgp_east_asia_mandala_task_contract_events.2400', 'spirits_calm',
        'Fear is no proof of guilt. Let the healer leave with me.', 'aoyu_calm', rescue_healer,
        'Calm the crowd and protect the accused healer without burning the hut or banning local healers.')
    add('tgp_east_asia_mandala_task_contract_events.2400', 'spirits_remedies',
        'Bring clean water and remedies. We will help the sick together.', 'illness_healer',
        rescue_healer + '''
remove_short_term_gold = minor_gold_value
scope:ritual_location.county = { add_county_modifier = { modifier = ac_event_epidemic_defenses_modifier years = 1 } }
ac_event_chi_healing_cooldown_effect = yes''',
        'Fund local treatment and protect the healer. Improve local epidemic resistance for one year; the epidemic itself remains.')
    for key, ability, label in [
        ('naga_mido', 'mido_subdue', 'Be still, river beast. Your hunting ends here.'),
        ('naga_water', 'water', 'Hold the crocodile in a still pool. Bring the nets.')]:
        add('tgp_east_asia_mandala_task_contract_events.4900', key, label, ability, '''mandala_piety_reward_effect = yes
small_mandala_legitimacy_reward_effect = yes
add_character_modifier = { modifier = 6140_pet_modifier years = 30 }''',
            'Capture the crocodile without the native wound and death roll. The ritual contract completes normally.', major=True)
    add('tgp_east_asia_mandala_task_contract_events.4900', 'naga_barrier',
        'Stay behind the barrier. Let the archers finish this safely.', 'kiihakai_barrier',
        'mandala_piety_reward_effect = yes\nsmall_mandala_legitimacy_reward_effect = yes',
        'Protect the nearby villagers and companion while removing the crocodile threat. Complete the existing ritual contract.', major=True)

    # Adult examinations use their own score and native attempt, never tournament progress.
    for eid, exam, choices in [
        ('imperial_examination.5000', 'essay', [('kii_academy', 'Order the argument as I was taught in the Mystic Academy.'), ('aoyu_calm', 'Settle my breath, clear my thoughts, and begin.')]),
        ('imperial_examination.5100', 'poetry', [('kii_academy', 'Give every line its proper measure.'), ('aoyu_prayer', 'Let the verse give voice to our common hopes.')]),
        ('imperial_examination.5160', 'polearm', [('aki_pike', 'A perfect stance, a steady point. Demonstrate the Pike Wall.')]),
        ('imperial_examination.5170', 'riding', [('mido_rider', 'Let horse and rider move as one.'), ('wind_arrows', 'Steady the bow. Let the wind guide the arrow.')]),
    ]:
        for ability, label in choices:
            add(eid, 'exam_' + exam + '_' + ability, label, ability, exam_attempt(exam),
                'Gain one temporary preparation advantage for this native examination attempt. Existing preparation is restored afterward; passing and promotion remain uncertain.')
    for ability, label in [('kii_academy', 'A clear structure will carry the imperial argument.'), ('aoyu_calm', 'Write calmly, with every word serving the argument.')]:
        # Palace assessments have different result flags and a dedicated follow-up.
        attempt = ('imperial_examination_set_up_exam_advantage_scope = yes\n' +
                   boosted_check(effects('imperial_examination.5300', 'imperial_examination.5300.a')))
        add('imperial_examination.5300', 'palace_' + ability, label, ability, attempt,
            'Improve the chance of a strong imperial essay. Preserve the native examination score, palace result flags and result event.')

    for eid in ('debate_event.5000', 'debate_event.5010'):
        name = eid + ('.b' if eid.endswith('5000') else '.c')
        for ability, label in [('aoyu_mirror', 'Answer the argument, undisturbed by its heat.'), ('kii_academy', 'Build the rebuttal from sound principles and careful study.')]:
            body = boosted_check(effects(eid, name))
            # Later feedback expects a recognized tactic even when this is a new option.
            body += '\nset_variable = { name = debate_selected_tactic value = flag:learning }'
            add(eid, eid.replace('.', '_') + '_' + ability, label, ability, body,
                'Improve the native scholarly argument roll. Keep the debate score, audience feedback and final political resolution.')

    for ability, label in [('water', 'Draw the sacred water in one unbroken stream.'), ('aoyu_prayer', 'Let our prayers flow together with the cleansing water.')]:
        add('festival.006', 'cleansing_' + ability, label, ability,
            effects('festival.006', 'festival.006.a'), 'Perform the cleansing rite and gain its normal piety and activity log entry.')
    for ability, label in [('mido_body', 'An Iron Body will hold its ground in this scramble.'), ('mido_line', 'Root my stance and wait for the opening.')]:
        add('festival.007', 'fortune_' + ability, label, ability,
            boosted_check(effects('festival.007', 'festival.007.a')),
            'Improve the strength-contest roll against the actual festival opponent, keeping the normal prestige and piety stakes.')
    add('festival.009', 'answer_wishes', 'Let me hear these prayers and offer what comfort I can.', 'aoyu_prayer', '''scope:guest_with_wish = {
    add_stress = -20
    add_opinion = { target = root modifier = grateful_opinion opinion = 20 }
}
add_piety = minor_piety_gain''', 'Comfort the guest whose wish is on the tree and gain piety, without creating a hook.',
        extra='scope:guest_with_wish = { is_alive = yes location = root.location }')

    for ability, label in [('water', 'There is water to be drawn here. Bring every waterskin.'), ('hunt_tracks', 'Read the land and its chi. Find the hidden water.')]:
        # Earthsense, not Scrying Sphere alone, supplies the second technique.
        extra = 'has_perk = ac_4_element_earth_e_perk' if ability == 'hunt_tracks' else ''
        add('ep3_laamp_flavour_ewan.4021', 'camp_water_' + ability, label, ability,
            'ep3_laamp_flavour_ewan_4021_camp_avoids_dehydration_effect = yes',
            'Find water for the present camp through the native dehydration-avoidance outcome. Travel resumes normally.', extra=extra)
    for ability, label, extra in [
        ('storm', 'Turn the worst of this gale away from our column.', 'OR = { scope:weather_type = flag:storm_thunder scope:weather_type = flag:storm_wind }'),
        ('wind', 'Break the wind around the train. Keep the carts moving.', 'OR = { scope:weather_type = flag:storm_wind scope:weather_type = flag:storm_sand }'),
        ('burial_earth', 'Firm the ground beneath the wheels and clear the ruts.', 'scope:weather_type = flag:storm_thunder'),
        ('mido_breaker', 'Shelter the children first. I will free these carts.', ''),
        ('kiihakai_barrier', 'Gather the vulnerable within my barrier. We advance together.', '')]:
        add('ep3_laamp_flavour_ewan.4041', 'convoy_' + ability, label, ability,
            'ep3_laamp_flavour_ewan_4041_train_rallies_effect = { OPINION = 30 }',
            'Get the present convoy through the storm without this event\'s new weather injuries, losses or deaths. Existing injuries remain.', extra=extra, major=True)
    for ability, label in [('aki_ranks', 'Close ranks around the tents. Hold the perimeter!'), ('kiihakai_ward', 'The perimeter wards will give us time to regroup.'), ('precognition', 'I saw where they would strike. Clear those tents!')]:
        add('ep3_laamp_flavour_ewan.4091', 'night_' + ability, label, ability,
            'add_prestige = medium_prestige_gain',
            'Repel the camp attack without the native defeat roll that wounds you and nearby followers. No single combat is started.', major=True)
    for ability, label in [('shadow_escape', 'A shadow can pass where the guard cannot see.'), ('aki_edge', 'One controlled cut through the shackles.'), ('mido_breaker', 'These chains will yield before the prisoner does.'), ('kiihakai_ward', 'Bind the guard behind a ward while we leave.')]:
        if ability == 'kiihakai_ward':
            extra = 'has_perk = ac_3_style_kiihakai_e_perk'
        else:
            extra = ''
        add('ep3_contract_event.0570', 'rescue_' + ability, label, ability, '''add_character_flag = contract_success_flag
trigger_event = { id = ep3_contract_event.0575 days = 1 }''',
            'Free the prisoner through the native noncombat success path and contract follow-up. The guard is not killed.', extra=extra)

    # Both native outcomes below hurt the invaders. Cultivation removes only the
    # catastrophic friendly-fire branch, not the normal opposed attack roll.
    greek = '''add_character_flag = { flag = used_fire_dromons days = 30 }
remove_character_flag = successful_greek_fire_attack
remove_character_flag = failed_greek_fire_attack
remove_character_flag = crit_failed_greek_fire_attack
duel = {
    skill = martial
    target = scope:duel_target_char
    55 = {
        compare_modifier = { value = scope:duel_value multiplier = 3.5 min = -54 }
        add_character_flag = successful_greek_fire_attack
    }
    45 = {
        compare_modifier = { value = scope:duel_value multiplier = -3.5 min = -44 }
        add_character_flag = failed_greek_fire_attack
    }
}
trigger_event = ep3_emperor_yearly.3012'''
    for ability, label in [('fire_control', 'Control the release. Our own ships will not burn.'), ('water', 'Turn the currents so the burning liquid stays clear of our hulls.'), ('wind', 'Keep the flames downwind of the defending fleet.')]:
        extra = 'scope:city_defender = root location = root.capital_province'
        if ability == 'fire_control':
            extra += ' has_trait = ac_element_fire'
        add('ep3_emperor_yearly.3011', 'greek_' + ability, label, ability, greek,
            'Make an opposed Greek-fire attack while preventing catastrophic friendly fire. Native success or partial-success effects resolve in the normal follow-up; the fleet cooldown remains.', extra=extra, major=True)
    for ability, label in [('water', 'Guide the creek into its new channel while the workers build.'), ('burial_earth', 'Shape a sound millrace. Skilled hands can finish the mill.')]:
        add('ep3_laamp_decision_event.1133', 'mill_' + ability, label, ability, '''add_character_flag = laamp_city_builder_mill_upgrade
show_as_tooltip = { scope:city_location = { add_building = watermills_03 } }
remove_short_term_gold = 160''',
            'Fund the upgraded watermill for 160 gold rather than 200. Preserve the construction flag and scheduled settlement follow-up; the building is not created twice.',
            extra='gold >= 160 location = scope:city_location')

    # Rescue the two actual charioteers; being a spectator conveys no Iron Body.
    for ability, label in [('kiihakai_barrier', 'Shield the wreckage. Stop the next chariots before they reach it.'), ('fall_rescue', 'Lift both drivers clear on the wind.')]:
        body = '''scope:charioteer_1 = { increase_wounds_no_death_effect = { REASON = death_crushed_in_chariot_race } }
scope:charioteer_2 = { increase_wounds_no_death_effect = { REASON = death_crushed_in_chariot_race } }'''
        add('chariot_race.3040', 'chariot_' + ability, label, ability, body,
            'Both drivers survive the wreck with nonfatal wounds. Normal standings are updated afterward; this does not award either driver a victory.',
            extra='scope:charioteer_1 = { is_alive = yes location = root.location } scope:charioteer_2 = { is_alive = yes location = root.location }', major=True)
    add('chariot_race.3040', 'chariot_mending', 'Stop the race. I will extract the drivers and tend their wounds.',
        'kiihakai_mending', '''scope:charioteer_1 = {
    increase_wounds_no_death_effect = { REASON = death_crushed_in_chariot_race }
    ac_heal_one_wound_effect = yes
}
scope:charioteer_2 = { increase_wounds_no_death_effect = { REASON = death_crushed_in_chariot_race } }
ac_event_chi_healing_cooldown_effect = yes''',
        'Both drivers survive. Mend one wound tier on the first driver; the other still needs treatment. Uses the shared healing cooldown.',
        extra='scope:charioteer_1 = { is_alive = yes location = root.location } scope:charioteer_2 = { is_alive = yes location = root.location }', major=True)

    for ability, label in [('water', 'Hold back the current until the smallest beasts are across.'), ('burial_earth', 'Raise a firm ford beneath their hooves.'), ('mido_rider', 'Keep the herd together. Follow my mount across.')]:
        add('mpo_migration_travel_events.0040', 'river_' + ability, label, ability,
            'add_prestige = 25', 'Cross with the herd intact, avoiding this event\'s herd-loss roll and additional 15- or 60-day delay.', major=True)
    add('mpo_migration_travel_events.0030', 'herd_remedies', 'Separate the sick and prepare remedies for the surviving herd.',
        'illness_healer', 'remove_short_term_gold = medium_gold_value\nac_event_chi_healing_cooldown_effect = yes',
        'Treat the surviving livestock without further herd losses. The animals already lost and the initial 30-day delay remain; character wound healing is not applied to livestock.')
    for ability, label in [('water', 'Find water for the herd before the weak animals fall.'), ('hunt_tracks', 'Read the land and lead us onto a gentler path.'), ('mido_strengthen', 'I will lend strength to those struggling at the back.')]:
        add('migration_events.1060', 'herd_route_' + ability, label, ability,
            'add_character_modifier = { modifier = mpo_found_paths_for_herds_modifier months = 6 }',
            'Help the present herd complete this difficult passage without the event\'s herd-loss or delay outcome. Gain the existing six-month migration assistance modifier.',
            extra='has_perk = ac_4_element_earth_e_perk' if ability == 'hunt_tracks' else '')
    add('mpo_events_anna.0020', 'messenger_mending', 'Close the wound with Mending Chi. Then we can hear the message.',
        'kiihakai_mending', '''scope:messenger = { ac_heal_one_wound_effect = yes }
current_travel_plan = { delay_travel_plan = { days = 14 } add_companion = scope:messenger }
liege ?= { add_character_modifier = { modifier = mpo_messenger_negative_liege_modifier years = 10 } }
scope:messenger = { add_opinion = { target = root modifier = grateful_opinion opinion = 10 } }
ac_event_chi_healing_cooldown_effect = yes''',
        'Save the messenger and mend one wound tier. Keep the 14-day treatment delay and the native consequence of delaying the message, rather than falsely claiming it was delivered.',
        extra='scope:messenger = { is_alive = yes has_trait = wounded location = root.location }')

    for ability, label in [('treasure_repair', 'I will refine the fittings. Buy the remaining materials.'), ('kiihakai_runes', 'Renew the forge with runes and sound materials.'), ('fire_control', 'I will regulate the heat while the smith rebuilds the forge.')]:
        add('fund_inspiration.2005', 'forge_' + ability, label, ability,
            effects('fund_inspiration.2005', 'fund_inspiration.2005.a') + '\nscope:inspiration = { change_inspiration_progress = 1 }',
            'Invest the normal 50 gold in the forge and retain its quality improvement. Cultivation also advances the current commission one step.',
            extra='scope:inspiration_owner = { location = root.location }' + (' has_trait = ac_element_fire' if ability == 'fire_control' else ''))
    add('fund_inspiration.2070', 'artisan_calm', 'Set down the tools. Let us find a calmer rhythm for this work.',
        'aoyu_calm', '''scope:inspiration_owner = {
    add_stress = -30
    add_opinion = { target = root modifier = grateful_opinion opinion = 15 }
}
scope:inspiration = { change_inspiration_progress = 1 }''',
        'Ease the artisan\'s distress and recover one step of stalled progress. Existing personality and mental-health traits remain.',
        extra='scope:inspiration_owner = { is_alive = yes location = root.location }')
    add('hold_court.6140', 'court_beast', 'Leave the chains to me. I will show you how to handle this beast.',
        'beast_subdue', '''add_character_modifier = { modifier = 6140_pet_modifier years = 30 }
change_current_court_grandeur = medium_court_grandeur_gain''',
        'Keep the exotic animal and demonstrate control safely, without sending the jester into a maiming or death roll.')
    for ability, label, native in [('kii_academy', 'I have studied riddles such as these.', 'fp1_yearly.0101.b'), ('aoyu_mirror', 'A clear mind will see through this turn of phrase.', 'fp1_yearly.0101.a')]:
        add('fp1_yearly.0101', 'riddles_' + ability, label, ability, boosted_check(effects('fp1_yearly.0101', native)),
            'Improve the native verbal contest roll, retaining the normal prestige and opinion stakes.')
    add('fp2_struggle.1050', 'visionary_calm', 'Rest beside me. Let the Calming Current quiet your fear.',
        'aoyu_calm', '''scope:visionary_spouse = {
    add_stress = -30
    add_opinion = { target = root modifier = comforted_opinion opinion = 20 }
}''', 'Comfort your spouse without worsening the illness or creating a new depressive trait. The existing illness and foreboding visions remain for separate treatment.',
        extra='scope:visionary_spouse = { is_alive = yes location = root.location }')
    add('fp3_yearly.8033', 'sorbet_ice', 'Bring fresh ingredients. I can keep them chilled for now.',
        'preservation', '''remove_short_term_gold = tiny_gold_value
scope:sorbet_enthusiast = { add_opinion = { target = root modifier = pleased_opinion opinion = 20 } }''',
        'Supply temporary refrigeration for purchased ingredients. The broken icehouses still need permanent repairs.')
    add('fp3_yearly.8033', 'icehouse_runes', 'Pay the masons; I will reinforce the repaired icehouses.',
        'kiihakai_runes', effects('fp3_yearly.8033', 'fp3_yearly.8033.c'),
        'Fund the normal icehouse repairs, remove the broken-icehouse modifier and satisfy the courtier. Construction is not free.')
    for ability, label in [('aoyu_mirror', 'Lower our voices. Then let us consider the argument.'), ('kii_academy', 'The distinction is clear if we follow the reasoning carefully.')]:
        add('bp2_adult_education.1000', 'university_' + ability, label, ability,
            boosted_check(effects('bp2_adult_education.1000', 'bp2_adult_education.1000.a')),
            'Improve the native university debate roll and keep its educational, opinion and rivalry outcomes.')
    add('bp2_yearly.7000', 'nurse_remedies', 'Rest away from the nursery. I will prepare a safe remedy.',
        'illness_healer', '''remove_short_term_gold = minor_gold_value
scope:wet_nurse = { recover_from_disease_effect = { DISEASE = ill } }
ac_event_chi_healing_cooldown_effect = yes''',
        'Treat the wet nurse\'s ordinary illness without the extra child-exposure roll. Serious diseases require their own treatment.',
        extra='scope:wet_nurse = { is_alive = yes has_trait = ill location = root.location NOT = { has_serious_disease_trigger = yes } }')

    fire_success = winning_branch('bp3_survey.1040', 'bp3_survey.1040.a', 50)
    for ability, label in [('fire_control', 'Contain the blaze before it reaches the next house.'), ('fall_rescue', 'Carry the trapped residents clear of the roofs.'), ('kiihakai_barrier', 'Shield the workers while they clear the burning street.')]:
        add('bp3_survey.1040', 'city_fire_' + ability, label, ability,
            'inspection_success_chance_change_focus_effect = { FOCUS = domain CHANGE = increase_minor }\n' + fire_success,
            'Save the residents and preserve the threatened building without the wound or death roll. Apply the native successful inspection rewards.', major=True)
    for ability, label in [('burial_earth', 'Shape the foundations while the builders raise the walls.'), ('kiihakai_runes', 'Pay the builders. I will strengthen the completed works.')]:
        add('bp3_survey.1050', 'walls_' + ability, label, ability,
            effects('bp3_survey.1050', 'bp3_survey.1050.a') + '\ninspection_success_chance_change_effect = { CHANGE = increase_minor }',
            'Fund the normal ten-year wall improvement and gain an additional small inspection benefit. No permanent building tiers are created.')
    add('epidemic_events.1064', 'trials_relief', 'Send supplies and trained relief workers. Answer fear with care.',
        'aoyusumu_refuge', '''remove_short_term_gold = medium_gold_value
scope:witch_trial_county = { add_county_modifier = { modifier = witch_trials_obstructed years = 15 } }''',
        'Fund organized relief and obstruct trials in the reported county. This is an administrative response; it neither removes the epidemic nor casts a spell on a remote crowd.')
    add('epidemic_events.1064', 'trials_barrier', 'Here, the threatened people will stand behind my barrier.',
        'kiihakai_barrier', '''scope:witch_trial_county = { add_county_modifier = { modifier = witch_trials_obstructed years = 15 } }''',
        'Protect people in the county where you are physically present and obstruct its trials. The epidemic remains.',
        extra='location.county = scope:witch_trial_county', major=True)
    for ability, label in [('water', 'Quench the bonfire before the artifact touches it.'), ('preservation', 'Freeze the flames around my threatened treasure.'), ('fall_rescue', 'Lift my treasure clear on the wind.')]:
        add('bp1_yearly.5728', 'rival_fire_' + ability, label, ability,
            'add_prestige = miniscule_prestige_gain',
            'Save your existing artifact without destroying it or starting single combat. Its ownership and existing durability remain unchanged.',
            extra='exists = scope:burned_artifact')
    add('pam_generic_events.0009', 'nightmare_prayer', 'Breathe within the Calming Current, then return to prayer.',
        'aoyu_calm', 'add_stress = -30\nchange_spiritual_fulfillment = minor_spiritual_fulfillment_value',
        'Ease the nightmare through composure and prayer, without self-punishment or changing personality traits.', cost=False)

    # Physical accidents: outcomes happen in the original choices, so a new
    # intervention can prevent this incident without curing pre-existing incapacity.
    harm = {
        'harm.0511': [('fall_rescue', 'Let the wind catch my fall.'), ('mido_body', 'Brace the Iron Body before I strike the ground.'), ('precognition', 'I saw the stumble before the horse lost its footing.')],
        'harm.0521': [('water', 'The current will carry me back to air.'), ('fall_rescue', 'Lift myself above the water on the wind.')],
        'harm.0561': [('mido_body', 'Steady my stance before the fall.'), ('fall_rescue', 'Catch my weight upon the wind.')],
        'harm.0581': [('water', 'Draw the slippery water away from my feet.'), ('fall_rescue', 'A breath of wind will soften this landing.')],
        'harm.0591': [('kiihakai_barrier', 'A barrier between my skull and the falling pot.'), ('precognition', 'I have already stepped out of its path.'), ('mido_body', 'Reinforce my body before the impact.')],
    }
    for eid, choices in harm.items():
        for ability, label in choices:
            add(eid, eid.replace('.', '_') + '_' + ability, label, ability, '',
                'Prevent this accident\'s incapacitating outcome. The normal harm-event and dynasty cooldowns remain; pre-existing infirmity or incapacity is not cured.')
    for eid, choices in specs.items():
        base['add'](eid, 'dlc', *choices)
