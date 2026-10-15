"""Second event batch: disaster relief, intrigue and dedicated school techniques.

Only transform_event changes existing setup/resolution. All other additions are
new choices; their vanilla alternatives and cleanup remain intact.
"""
from textwrap import indent

ABILITIES = {
    'rubble': 'OR = { has_perk = ac_4_element_earth_a_perk has_perk = ac_3_style_midorikatai_g_perk }',
    'relief_healer': 'OR = { ac_can_chi_heal_trigger = yes has_perk = ac_1_alchemy_i_perk } NOT = { has_character_flag = ac_chi_healing_cooldown }',
    'relief_food': 'OR = { has_perk = ac_4_element_earth_d_perk has_perk = ac_4_element_earth_h_perk has_perk = ac_4_element_ice_b_perk }',
    'bind_looters': 'has_perk = ac_2_handseals_h_perk',
    'subjugation': 'has_perk = ac_3_style_midorikatai_e_perk',
    'prevention': 'OR = { has_perk = ac_4_element_light_c_perk has_perk = ac_1_alchemy_j_perk has_perk = ac_2_handseals_g_perk }',
    'alchemist_book': 'has_perk = ac_1_alchemy_j_perk',
    'burial_earth': 'has_perk = ac_4_element_earth_a_perk',
    'burial_fire': 'has_perk = ac_4_element_fire_g_perk',
    'purification': 'OR = { has_perk = ac_4_element_fire_i_perk has_perk = ac_4_element_light_c_perk }',
    'corpse_seal': 'OR = { has_perk = ac_2_handseals_g_perk has_perk = ac_3_style_kiihakai_e_perk }',
    'illness_healer': 'OR = { has_perk = ac_4_element_light_c_perk has_perk = ac_1_alchemy_c_perk } NOT = { has_character_flag = ac_chi_healing_cooldown }',
    'wind_arrows': 'has_perk = ac_4_element_wind_f_perk',
    'treasure_repair': 'has_perk = ac_1_alchemy_f_perk',
    'poison_gift': 'has_perk = ac_1_alchemy_b_perk has_perk = ac_1_alchemy_d_perk',
    'tunnel_scry': 'has_perk = ac_3_style_kiihakai_d_perk',
    'tunnel_shadow': 'has_perk = ac_3_style_kurokonton_a_perk',
    'retrieve_chest': 'OR = { has_trait = ac_element_water has_trait = ac_element_wind }',
    'frost_control': 'OR = { has_trait = ac_element_fire has_perk = ac_4_element_ice_j_perk }',
    'antidote': 'OR = { has_perk = ac_1_alchemy_d_perk has_perk = ac_4_element_fire_i_perk has_perk = ac_4_element_light_c_perk }',
    'beast_subdue': 'OR = { has_perk = ac_3_style_midorikatai_b_perk has_perk = ac_3_style_midorikatai_e_perk }',
    'beast_thunder': 'has_perk = ac_4_element_storm_b_perk',
    'mud': 'OR = { has_perk = ac_4_element_earth_a_perk has_trait = ac_element_water has_perk = ac_3_style_midorikatai_a_perk }',
    'mido_fire_rescue': 'has_perk = ac_3_style_midorikatai_i_perk',
    'aoyusumu_crowd': 'has_perk = ac_3_style_aoyusumu_b_perk has_perk = ac_3_style_aoyusumu_e_perk',
    'aoyusumu_exorcism': 'has_perk = ac_3_style_aoyusumu_g_perk',
    'aoyusumu_prayer': 'has_perk = ac_3_style_aoyusumu_h_perk',
    'aoyusumu_meditation': 'has_perk = ac_3_style_aoyusumu_b_perk NOT = { has_character_flag = ac_event_meditation_cooldown }',
    'aoyusumu_refuge': 'has_perk = ac_3_style_aoyusumu_e_perk',
    'precognition': 'has_perk = ac_3_style_aoyusumu_i_perk',
    'kiihakai_barrier': 'has_perk = ac_3_style_kiihakai_i_perk',
    'kiihakai_ward': 'has_perk = ac_3_style_kiihakai_b_perk',
    'kiihakai_runes': 'has_perk = ac_3_style_kiihakai_g_perk',
    'kiihakai_mending': 'has_perk = ac_3_style_kiihakai_c_perk NOT = { has_character_flag = ac_chi_healing_cooldown }',
    'akakiru_disarm': 'has_perk = ac_3_style_akakiru_g_perk',
    'mido_subdue': 'has_perk = ac_3_style_midorikatai_e_perk',
    'shadow_escape': 'has_perk = ac_3_style_kurokonton_a_perk',
}


def render_triggers():
    text = '# Generated from tools/event_expansion_specs.py.\n'
    for ability, condition in ABILITIES.items():
        text += f'ac_event_{ability}_trigger = {{\n\tac_event_practitioner_trigger = yes\n\t{condition}\n}}\n'
    # Captive techniques deliberately do not use the normal "not imprisoned" gate.
    text += '''
ac_event_captive_trigger = {
    has_trait = ac_cultivator
    age >= 16
    is_alive = yes
    is_imprisoned = yes
    NOT = { has_trait = incapable }
}
ac_event_captive_purify_trigger = {
    ac_event_captive_trigger = yes
    OR = { has_perk = ac_4_element_light_c_perk has_perk = ac_4_element_fire_i_perk }
}
ac_event_captive_mido_trigger = { ac_event_captive_trigger = yes has_perk = ac_3_style_midorikatai_g_perk }
ac_event_captive_shadow_trigger = { ac_event_captive_trigger = yes has_perk = ac_3_style_kurokonton_d_perk }
ac_event_captive_earth_trigger = { ac_event_captive_trigger = yes has_perk = ac_4_element_earth_a_perk }
'''
    return text


def own(key, label, ability, effects, *, extra='', major=False, tip=None, exhaust=True):
    return option(key, label, f'ac_event_{ability}_trigger = yes ' + extra,
                  'save_scope_as = ac_event_practitioner\n' + effects + ('\n' + exert(major) if exhaust else ''), tip)


def contract(outcome):
    return 'scope:ongoing_contract = { complete_task_contract = ' + outcome + ' }'


def county_modifier(scope, modifier, years=3):
    return f'{scope} = {{ add_county_modifier = {{ modifier = {modifier} years = {years} }} }}'


def grateful(scope):
    return 'ac_event_saved_companion_effect = { COMPANION = ' + scope + ' }'


def register(base):
    global option, travel_option, exert
    option, travel_option, exert = (base[k] for k in ('option', 'travel_option', 'exert'))
    add, loc = base['add'], base['LOCALIZATION']
    loc.update({
        'ac_event_epidemic_defenses_modifier': 'Cultivated Plague Defenses',
        'ac_event_epidemic_defenses_modifier_desc': 'Funded remedies and protective formations support the capital\'s plague response.',
        'ac_event_safe_burials_modifier': 'Cultivated Funeral Relief',
        'ac_event_safe_burials_modifier_desc': 'A cultivator has funded safe disposal of the dead, easing pressure on the burial grounds.',
        'ac_event_reassured_people_modifier': 'Prayers Answered',
        'ac_event_reassured_people_modifier_desc': 'Aoyusumu prayers and public relief have reassured frightened inhabitants.',
        'ac_event_meditative_retreat_modifier': 'Within the Calming Current',
        'ac_event_meditative_retreat_modifier_desc': 'A demanding meditative retreat leaves less time for diplomatic and administrative duties.',
        'ac_event_disaster_cost_tt': 'You fund supplies and organize relief. If you are still traveling, your journey is delayed three days. The contract is completed through the existing relief outcome.',
        'ac_event_plague_limit_tt': 'The funded measures improve epidemic resistance in your capital county for three years. They do not remove an existing epidemic.',
        'ac_event_frost_control_tt': 'You reduce frostbite severity and update its existing modifiers. Previously lost limbs are not restored.',
        'ac_event_contest_safe_tt': 'Your technique prevents injury and death in this encounter, including its delayed resolution. It does not guarantee winning the tournament.',
        'ac_event_cultivated_contest_desc': 'Our deadly encounter ends with a display of cultivation. Neither of us suffers a wound: the murderous exchange has been interrupted before it can claim a life.\\n\\nThe tournament continues around us.',
        'ac_event_refuge_tt': 'You protect yourself and the family members or courtier present in this event. Only people physically here benefit.',
        'ac_event_ward_camp_tt': 'Your protected rallying point shelters nearby people and you avoid the event\'s wound roll.',
        'ac_event_meditation_tt': 'Lose 40 stress and spend six months in a demanding meditative retreat. This choice cannot be used again for three years.',
        'ac_event_besieged_soul_tt': 'The event\'s spiritual-affliction modifier is removed. Other illnesses and permanent mental-health traits are unchanged.',
        'ac_event_child_healing_tt': 'Treat the child\'s ordinary illness without the normal contact-infection roll. This does not cure epidemics throughout the county.',
        'ac_event_mending_named_tt': 'Kiihakai\'s Mending Chi restores one wound tier. The six-month cooldown is shared with other Chi Healing treatments.',
        'ac_event_retrieve_chest_tt': 'The artifact stays in your possession and your caravan master is not sent into danger.',
        'ac_event_burial_cremation_tt': 'The remains are safely cremated. If your faith\'s funeral tradition does not permit cremation, you lose piety.',
        'ac_event_safe_antidote_tt': 'You neutralize this snakebite, remove its ordinary illness, and avoid the event\'s lethal venom outcomes.',
        'ac_event_poison_gift_tt': 'You send the poisoned gift through its normal response event, gaining scheme opportunities without accidentally poisoning your household.',
        'ac_event_wheel_tt': 'Runes reinforce the repaired wheel. Your caravan resumes after one day, with its supplies intact.',
        'ac_event_artifact_repair_tt': 'You pay for materials and restore the artifact to its maximum durability.',
        'ac_event_chipped_repair_tt': 'You pay for materials, preserve your existing weapon, and recover the tournament score lost when it was chipped.',
        'ac_event_precognition_tt': 'Precognition warns you before the attack. You avert it without taking a lethal combat roll.',
    })

    relief_cost = 'remove_short_term_gold = minor_gold_value\nif = { limit = { exists = current_travel_plan } current_travel_plan = { delay_travel_plan = { days = 3 } } }\n'
    add('tgp_natural_disaster_contract_event.0006', 'disaster', own('rubble_relief', 'Hold the walls steady. We will bring them all out.', 'rubble', relief_cost + contract('remove_debris'), major=True, tip='ac_event_disaster_cost_tt'))
    add('tgp_natural_disaster_contract_event.0011', 'disaster',
        own('medical_relief', 'Set out clean beds. My chi will aid the physicians.', 'relief_healer', relief_cost + contract('assisting_physician') + '\nac_event_chi_healing_cooldown_effect = yes', major=True, tip='ac_event_disaster_cost_tt'),
        own('mending_relief', 'Mending Chi will close their wounds while the physicians work.', 'kiihakai_mending', relief_cost + contract('medical_assistance') + '\nac_event_chi_healing_cooldown_effect = yes', major=True, tip='ac_event_disaster_cost_tt'))
    add('tgp_natural_disaster_contract_event.0002', 'disaster', own('food_relief', 'Keep relief flowing while this county recovers.', 'relief_food', relief_cost + contract('distribution_of_food') + '\n' + county_modifier('scope:ongoing_destination.county', 'ac_event_restored_fields_modifier'), major=True, tip='ac_event_disaster_cost_tt'))
    add('tgp_natural_disaster_contract_event.0016', 'disaster',
        own('bind_looters', 'Bind their hands. There need be no executions.', 'bind_looters', contract('deployed_troops')),
        own('subdue_looters', 'My domain ends this looting. Put down what you have taken.', 'subjugation', contract('deployed_troops') + '\nadd_dread = 5'))
    add('tgp_travel_danger_events.0001', 'disaster', travel_option('rebuild_farm', 'A child should not have to lift these stones alone.', 'rubble', '''remove_short_term_gold = tiny_gold_value
location.county = { change_county_control = 5 }
scope:peasant_character_child = { add_opinion = { target = scope:ac_event_practitioner modifier = grateful_opinion opinion = 30 } }
add_prestige = 25'''))

    add('physician_epidemic_events.1020', 'epidemic', own('cultivated_prevention', 'Fund remedies and protective formations around the capital.', 'prevention', 'remove_short_term_gold = medium_gold_value\n' + county_modifier('capital_county', 'ac_event_epidemic_defenses_modifier'), tip='ac_event_plague_limit_tt'))
    add('physician_epidemic_events.1030', 'epidemic', own('alchemy_compendium', 'Let us record remedies I have tested myself.', 'alchemist_book', '''remove_short_term_gold = medium_gold_value
set_artifact_rarity_masterwork = yes
create_artifact = {
    name = pharmaceuticals
    description = pharmaceuticals_desc
    type = miscellaneous
    modifier = artifact_epidemic_resistance_1_modifier
    modifier = artifact_negate_health_penalty_add_1_modifier
    visuals = pocket_book
    quality = scope:quality
    wealth = scope:wealth
    creator = root
}'''))
    add('epidemic_events.1110', 'epidemic',
        own('earth_graves', 'Raise new burial grounds beyond the crowded streets.', 'burial_earth', 'remove_short_term_gold = minor_gold_value\n' + county_modifier('scope:graveyard_county', 'ac_event_safe_burials_modifier')),
        own('fire_cremation', 'I will tend the funeral pyres until the streets are clear.', 'burial_fire', '''remove_short_term_gold = minor_gold_value
if = { limit = { NOT = { faith = { has_doctrine = doctrine_funeral_cremation } } } add_piety = -100 }
''' + county_modifier('scope:graveyard_county', 'ac_event_safe_burials_modifier'), tip='ac_event_burial_cremation_tt'))
    corpse_effect = county_modifier('scope:flung_corpse_location', 'ce1_quarantined_corpse', 10)
    add('epidemic_events.1121', 'epidemic',
        own('purify_corpse', 'Destroy the contamination before anyone touches it.', 'purification', corpse_effect),
        own('seal_corpse', 'Seal the remains and keep the workers beyond the wards.', 'corpse_seal', corpse_effect + '\nremove_short_term_gold = tiny_gold_value'))
    add('epidemic_events.5003', 'epidemic', own('heal_child', 'Bring the child here. I can offer more than a royal touch.', 'illness_healer', '''scope:child = { remove_trait = ill }
scope:peasant = { add_opinion = { target = root modifier = grateful_opinion opinion = 30 } }
add_legitimacy_effect = { LEGITIMACY = medium_legitimacy_gain }
ac_event_chi_healing_cooldown_effect = yes''', tip='ac_event_child_healing_tt'))
    add('dungeon_ongoing.0004', 'prison', own('purify_dungeon_wound', 'Even here, I can drive the corruption from this wound.', 'captive_purify', 'remove_character_modifier = infected_wound_modifier'))

    add('contest_events.0710', 'tournament', own('wind_arrow', 'The wind will carry this arrow true.', 'wind_arrows', '''activity_tournament_change_contestant_score_effect = { SCORE = increase_major }
add_character_flag = { flag = success_pivotal_flag days = 30 }''', extra='exists = scope:pivotal_contestant scope:pivotal_contestant = root'))
    contest_protection = 'add_character_flag = { flag = ac_event_contest_safe days = 3 }'
    add('contest_events.1131', 'tournament',
        own('contest_disarm', 'Akakiru teaches that a drawn blade need not draw blood.', 'akakiru_disarm', contest_protection, tip='ac_event_contest_safe_tt'),
        own('contest_subdue', 'Enough. You cannot break this stance.', 'mido_subdue', contest_protection, tip='ac_event_contest_safe_tt'),
        own('contest_shadow', 'Your hatred strikes an empty shadow.', 'shadow_escape', contest_protection + '\nadd_character_flag = { flag = contest_agency_fled months = 1 }', tip='ac_event_contest_safe_tt'),
        own('contest_precognition', 'I have already seen where that blow will fall.', 'precognition', contest_protection + '\nadd_character_flag = { flag = contest_agency_fled months = 1 }', tip='ac_event_precognition_tt'))
    add('contest_events.1132', 'tournament')
    add('contest_events.1133', 'tournament')
    add('ep2_locale_events.4500', 'tournament', own('refine_chipped_sword', 'Fetch materials. I shall refine the damaged edge myself.', 'treasure_repair', '''remove_short_term_gold = tiny_gold_value
activity_tournament_change_contestant_score_effect = { SCORE = increase_minor }''', tip='ac_event_chipped_repair_tt'))

    add('intrigue_scheme_ongoing.5019', 'intrigue',
        own('scry_tunnel', 'My Scrying Sphere will show whether that passage is still open.', 'tunnel_scry', 'add_piety = -100\nscope:scheme = { change_opportunities = 3 }'),
        own('shadow_tunnel', 'A forgotten passage is the perfect road for a shadow.', 'tunnel_shadow', 'scope:scheme = { change_opportunities = 3 }'))
    add('intrigue_scheme_ongoing.5005', 'intrigue', own('refined_poison_gift', 'I will refine the powder and seal it away from our own hands.', 'poison_gift', '''save_scope_as = owner
pay_short_term_gold = { target = scope:target gold = root.minor_gold_value }
scope:scheme = { change_opportunities = 2 }
scope:target = { trigger_event = intrigue_scheme_ongoing.5006 }''', tip='ac_event_poison_gift_tt'))
    escape = '''escape_from_prison_effect = yes
remove_character_flag = block_for_prison_release_notification
if = { limit = { scope:imprisoner = { is_ai = no } } scope:imprisoner = { trigger_event = prison.9499 } }'''
    # Preserve the normal escape bookkeeping and imprisoner's notification.
    prison_options = []
    for ability, label in [('captive_mido', 'Your chains cannot hold a Wallbreaker.'), ('captive_shadow', 'You caught my hand. You did not catch my shadow.'), ('captive_earth', 'Then I shall make a door of the stone itself.')]:
        key = 'prison_' + ability
        prison_options.append(own(key, label, ability, escape, major=True))
    add('prison.9501', 'prison', *prison_options)

    add('travel_events.1005', 'travel', travel_option('retrieve_artifact', 'Let the wind and waves return what is ours.', 'retrieve_chest', '', tooltip='ac_event_retrieve_chest_tt'))
    add('travel_danger_events.1011', 'travel', travel_option('frost_control', 'Steady warmth, carefully guided. We can halt this frostbite.', 'frost_control', '''scope:frostbite_victim = {
    change_variable = { name = frostbite_severity subtract = 6 }
    change_frostbite_modifier_with_severity_effect = { SEVERITY = var:frostbite_severity }
}
''' + grateful('scope:frostbite_victim'), tooltip='ac_event_frost_control_tt'))
    add('travel_danger_events.7000', 'travel', travel_option('snake_antidote', 'I know how to draw this venom out.', 'antidote', 'scope:snake_victim = { remove_trait = ill }\n' + grateful('scope:snake_victim'), tooltip='ac_event_safe_antidote_tt'))
    add('travel_danger_events.6000', 'travel',
        travel_option('subdue_travel_beast', 'Be still, beast. There is no prey for you here.', 'beast_subdue', grateful('scope:beast_victim')),
        travel_option('thunder_travel_beast', 'A thunderclap will send it running.', 'beast_thunder', grateful('scope:beast_victim')))
    add('travel_danger_events.9030', 'travel', travel_option('free_wagons', 'Firm ground, drained ruts, and one final push.', 'mud', 'current_travel_plan = { delay_travel_plan = { days = 1 } }'))
    fire_rescue = '''add_character_modifier = { modifier = travel_local_hero_modifier years = 3 }
location.county = { add_county_modifier = { modifier = travel_rescued_workers_modifier years = 3 } }'''
    add('travel_events.2012', 'travel',
        travel_option('plantation_fire', 'Turn the flames aside and bring the workers out.', 'fire_control', fire_rescue),
        travel_option('plantation_mido', 'My Iron Body will carry them through the flames.', 'mido_fire_rescue', fire_rescue, major=True))
    add('travel_events.3120', 'travel',
        travel_option('forest_fire_control', 'Open a path through those flames!', 'fire_control', grateful('scope:endangered_character')),
        travel_option('forest_fire_wind', 'Lift our companion clear of the fire!', 'fall_rescue', grateful('scope:endangered_character')),
        travel_option('forest_fire_barrier', 'Stand behind my Barrier of Chi!', 'kiihakai_barrier', grateful('scope:endangered_character'), major=True))

    # Dedicated school applications.
    add('ach_coronation.0015', 'school', own('aoyusumu_stampede', 'Breathe with me. There is room for everyone.', 'aoyusumu_crowd', '''location.county = { remove_county_modifier = ach_coronation_stampede_modifier }
add_legitimacy_effect = { LEGITIMACY = medium_legitimacy_gain }
ac_event_coronation_rescue_effect = yes''', major=True))
    add('pam_secular_faith_events.0026', 'school', own('aoyusumu_exorcism', 'I will perform the Exorcist\'s Rite. Hold them gently.', 'aoyusumu_exorcism', '''scope:afflicted = {
    remove_character_modifier = pam_sf_besieged_by_demons_modifier
    add_character_flag = cured_demons
    add_opinion = { target = root modifier = grateful_opinion opinion = 30 }
}''', tip='ac_event_besieged_soul_tt'))
    add('epidemic_events.1050', 'school', own('aoyusumu_doomsday', 'Let us hear their prayers and answer their fear.', 'aoyusumu_prayer', '''remove_short_term_gold = tiny_gold_value
add_legitimacy_effect = { LEGITIMACY = minor_legitimacy_gain }
''' + county_modifier('capital_county', 'ac_event_reassured_people_modifier')))
    add('stress_threshold.2311', 'school', own('aoyusumu_meditation', 'I will find stillness within the Calming Current.', 'aoyusumu_meditation', '''add_stress = -40
add_character_flag = { flag = ac_event_meditation_cooldown years = 3 }
add_character_modifier = { modifier = ac_event_meditative_retreat_modifier months = 6 }
add_ac_cultivation_lifestyle_xp = 25''', tip='ac_event_meditation_tt', exhaust=False))
    add('tgp_governor_contract_event.0031', 'school', own('aoyusumu_quake_refuge', 'Set up a refuge. I will hear each family\'s fears myself.', 'aoyusumu_refuge', relief_cost + contract('convene_public_meeting'), major=True, tip='ac_event_disaster_cost_tt'))
    add('natural_disaster_flavor_events.0015', 'school', own('kiihakai_family_barrier', 'Stay behind me—all of you!', 'kiihakai_barrier', '''if = { limit = { exists = scope:spouse scope:spouse = { is_at_same_location = root } } ''' + grateful('scope:spouse') + ''' }
if = { limit = { exists = scope:heir } ''' + grateful('scope:heir') + ''' }
if = { limit = { exists = scope:courtier } ''' + grateful('scope:courtier') + ' }', major=True, tip='ac_event_refuge_tt'))
    add('natural_disaster_flavor_events.0005', 'school',
        own('kiihakai_camp_ward', 'Gather within the ward. We will hold here together.', 'kiihakai_ward', 'add_character_modifier = { modifier = tgp_finding_safe_spot_character_modifier years = 10 }', major=True, tip='ac_event_ward_camp_tt'),
        own('aoyusumu_disaster_foresight', 'I have seen the danger. Follow my retreat!', 'precognition', 'add_character_modifier = { modifier = tgp_finding_safe_spot_character_modifier years = 10 }', tip='ac_event_precognition_tt'))
    add('travel_danger_events.9010', 'school', travel_option('kiihakai_wheel', 'A few runes will hold the wheel until proper repairs.', 'kiihakai_runes', 'current_travel_plan = { delay_travel_plan = { days = 1 } }', tooltip='ac_event_wheel_tt'))
    add('tgp_japan_yearly_events.1230', 'school', own('kiihakai_artifact', 'Renew its runes, and let it serve us faithfully again.', 'kiihakai_runes', '''remove_short_term_gold = tiny_gold_value
scope:cursed_artifact = { add_durability = { value = artifact_max_durability subtract = artifact_durability } }
add_stress = -10''', tip='ac_event_artifact_repair_tt'))

    # Give existing generic healing and defense events explicit school choices.
    for index, (event, group, choices) in enumerate(base['SPECS']):
        if event in {'health.4000', 'health.4001', 'health.4002'}:
            named = own('kiihakai_mend_wounds', 'Let Kiihakai\'s Mending Chi close these wounds.', 'kiihakai_mending', '''scope:sick_character = { ac_heal_one_wound_effect = yes }
ac_event_chi_healing_cooldown_effect = yes''', extra='scope:sick_character = { is_alive = yes has_trait = wounded } OR = { scope:sick_character = root location = scope:sick_character.location }', tip='ac_event_mending_named_tt')
            choices = named + '\n\n' + choices
        if event == 'hunt.4010':
            # Reuse the already safe intervention and all its scheme/log cleanup.
            named = choices.replace('ac_event_hunt_defend', 'ac_event_aoyusumu_hunt_precognition').replace('ac_event_hunt_defend_trigger', 'ac_event_precognition_trigger')
            # Replacement order above also renamed the trigger; make it explicit.
            named = named.replace('ac_event_aoyusumu_hunt_precognition_trigger', 'ac_event_precognition_trigger')
            loc['ac_event_aoyusumu_hunt_precognition'] = 'I saw your attack before you drew the blade.'
            loc['ac_event_aoyusumu_hunt_precognition_tt'] = loc['ac_event_hunt_defend_tt']
            choices = named + '\n\n' + choices
        base['SPECS'][index] = (event, group, choices)


def transform_event(text, event_id):
    """Patch the two linked tournament resolvers; leave other vanilla logic intact."""
    from build_event_overrides import one, replace_body, fields
    if event_id == 'contest_events.1132':
        body = one(text, 'immediate').body(text)
        wrapper = 'wrapper = {' + body + '}'
        initial = next(f for f in fields(wrapper) if f.key == 'hidden_effect')
        original_roll = initial.body(wrapper)
        selected = '''
        if = {
            limit = { scope:contest_opponent_a = { has_character_flag = ac_event_contest_safe } }
            scope:contest_opponent_a = { save_scope_as = agency_winner }
            scope:contest_opponent_b = { save_scope_as = agency_loser }
            save_scope_value_as = { name = ac_event_contest_resolved value = yes }
        }
        else_if = {
            limit = { scope:contest_opponent_b = { has_character_flag = ac_event_contest_safe } }
            scope:contest_opponent_b = { save_scope_as = agency_winner }
            scope:contest_opponent_a = { save_scope_as = agency_loser }
            save_scope_value_as = { name = ac_event_contest_resolved value = yes }
        }
        else = {
''' + indent(original_roll, '\t') + '\n        }\n'
        wrapper = wrapper[:initial.opening + 1] + selected + '\t\t' + wrapper[initial.end - 1:]
        # Find the actual loser's scope (fields() intentionally only sees word keys).
        marker = '\t\tscope:agency_loser = {'
        start = wrapper.index(marker)
        opening = wrapper.index('{', start)
        from build_event_overrides import close_brace
        end = close_brace(wrapper, opening)
        loser = wrapper[opening + 1:end - 1]
        injuries, separator, notify = loser.partition('\t\t\ttrigger_event = contest_events.1133')
        if not separator:
            raise ValueError('Tournament lethal resolver changed upstream')
        guarded = '\n\t\t\tif = {\n\t\t\t\tlimit = { NOT = { exists = scope:ac_event_contest_resolved } }\n' + indent(injuries, '\t') + '\n\t\t\t}\n' + separator + notify
        wrapper = wrapper[:opening + 1] + guarded + wrapper[end - 1:]
        cleanup = '''
        scope:contest_opponent_a = { remove_character_flag = ac_event_contest_safe }
        scope:contest_opponent_b = { remove_character_flag = ac_event_contest_safe }
'''
        text = replace_body(text, 'immediate', wrapper[wrapper.index('{') + 1:-1] + cleanup)
    elif event_id == 'contest_events.1133':
        desc = one(text, 'desc')
        body = desc.body(text)
        text = text[:desc.opening + 1] + '''
        first_valid = {
            triggered_desc = {
                trigger = { exists = scope:ac_event_contest_resolved }
                desc = ac_event_cultivated_contest_desc
            }
            desc = {
''' + body + '\n            }\n        }\n\t' + text[desc.end - 1:]
    return text
