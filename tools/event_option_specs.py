"""Aura Clash choices inserted into otherwise intact vanilla events."""
from textwrap import indent

LOCALIZATION = {
    'EVENT_WINDOW_OPTION_AVAILABLE_CULTIVATION': 'This option is available because you or a present companion can use the required cultivation technique.',
    'ac_event_chi_exertion_modifier': 'Spent Chi',
    'ac_event_chi_exertion_modifier_desc': 'A recent cultivation technique has left this character temporarily drained.',
    'ac_event_great_exertion_modifier': 'Overextended Chi',
    'ac_event_great_exertion_modifier_desc': 'This character pushed their cultivation to its limits to avert a catastrophe.',
    'ac_event_restored_fields_modifier': 'Cultivated Fields',
    'ac_event_restored_fields_modifier_desc': 'Cultivation techniques and funded relief are helping these fields recover.',
    'ac_event_warded_patrols_modifier': 'Warded Patrol Posts',
    'ac_event_warded_patrols_modifier_desc': 'Patrols operate from posts protected by cultivation formations.',
    'ac_event_cultivator_patrols_modifier': 'Cultivator Patrols',
    'ac_event_cultivator_patrols_modifier_desc': 'A cultivator has organized patrols to restore order without collective punishment.',
    'ac_event_preserved_provisions_modifier': 'Fresh Provisions Kept on Ice',
    'ac_event_preserved_provisions_modifier_desc': 'New supplies are kept fresh by an ice cultivator.',
    'ac_event_poison_recovery_modifier': 'Purging Poison',
    'ac_event_poison_recovery_modifier_desc': 'Cultivation saved this character from poisoning, but recovery will take time.',
    'ac_event_poison_intervention_desc': 'A bitter taste lingers after the meal. My pulse stumbles as I climb the stairs, and [stop_host_scope.GetTitledFirstNamePossessive] expression leaves no doubt: this was deliberate.\\n\\nBefore the darkness can claim me, I turn my awareness inward. There is still time to force the poison from my body.',
    'ac_event_poison_survived_log_title': 'Poison Purged',
    'ac_event_poison_survived_log': '[CHARACTER.GetShortUIName|U] used cultivation to survive poisoning during a visit to [TARGET_CHARACTER.GetShortUIName].',
    'ac_event_poison_survived_toast': 'Cultivation Defeated the Poison',
    'ac_event_sea_saved_tt': 'You and your entourage survive the storm. The cultivator who shields the ship suffers severe exhaustion.',
    'ac_event_poison_saved_tt': 'You survive the poisoning, expose your host\'s attack, and spend six months recovering.',
    'ac_event_heal_tt': 'The patient recovers one wound tier. Infection and gangrene are not cured. The healer cannot use Chi Healing again for six months.',
}


def available(ability):
    return f'ac_event_available_practitioner_trigger = {{ ABILITY = {ability} }}'


def choose(ability):
    return f'ac_event_choose_practitioner_effect = {{ ABILITY = {ability} }}'


def exert(major=False):
    return 'scope:ac_event_practitioner = { ac_event_' + ('great_' if major else '') + 'exertion_effect = yes }'


def option(key, label, trigger, effects, tooltip=None):
    key = 'ac_event_' + key
    LOCALIZATION[key] = label
    lines = [f'option = {{ # AC: {key}', f'\tname = {key}', '\treason = cultivation', '\ttrigger = { ' + trigger + ' }']
    if tooltip:
        lines.append('\tcustom_tooltip = ' + tooltip)
    lines.extend('\t' + line for line in effects.splitlines())
    lines += ['\tai_chance = { base = 200 }', '}']
    return indent('\n'.join(lines), '\t')


def travel_option(key, label, ability, effects='', tooltip=None, major=False, extra_trigger=''):
    return option(key, label, available(ability) + (' ' + extra_trigger if extra_trigger else ''), '\n'.join(filter(None, [choose(ability), effects, exert(major)])), tooltip)


SPECS = []


def add(event, group, *options):
    SPECS.append((event, group, '\n\n'.join(options)))


add('travel_danger_events.3004', 'travel',
    travel_option('squall_water', 'Let the current carry our crippled ship.', 'water', 'custom_tooltip = ac_event_squall_water_tt'),
    travel_option('squall_wind', 'A scrap of canvas is enough for my wind.', 'wind', 'custom_tooltip = ac_event_squall_wind_tt'))
LOCALIZATION.update(ac_event_squall_water_tt='A controlled current carries the damaged ship to safety without additional delay.', ac_event_squall_wind_tt='A steady magical wind drives an improvised rig without additional delay.')

add('travel_danger_events.4000', 'travel', travel_option('overboard', 'Lift our companion clear of the waves!', 'water_rescue', 'ac_event_saved_companion_effect = { COMPANION = scope:overboard_character }'))
add('travel_danger_events.2001', 'travel', travel_option('flood', 'Turn the flood aside. We leave no one behind.', 'flood', 'ac_event_saved_companion_effect = { COMPANION = scope:flood_victim }\ncustom_tooltip = ac_event_flood_tt'))
LOCALIZATION['ac_event_flood_tt'] = 'Both your companion and the caravan supplies are saved.'
add('travel_danger_events.1007', 'travel', travel_option('water_source', 'There is water beneath us. Bring the skins.', 'water_source', '''remove_character_modifier = dehydrated_modifier
current_travel_plan = {
    every_entourage_character = { remove_character_modifier = dehydrated_modifier }
}
custom_tooltip = ac_event_water_source_tt'''))
LOCALIZATION['ac_event_water_source_tt'] = 'You replenish the caravan\'s drinking water without sacrificing a companion or suffering new dehydration.'
add('travel_danger_events.3005', 'travel', travel_option('brushfire', 'The flames will not cross this line.', 'fire_control', 'ac_event_saved_companion_effect = { COMPANION = scope:burned_victim }\ncustom_tooltip = ac_event_brushfire_tt'))
LOCALIZATION['ac_event_brushfire_tt'] = 'You contain the brushfire, protecting the caravan from burns and delays.'
add('travel_danger_events.3003', 'travel', travel_option('snowbound', 'We shall make our own passage through the snow.', 'snow', '''current_travel_plan = { delay_travel_plan = { days = 2 } }
custom_tooltip = ac_event_snowbound_tt'''))
LOCALIZATION['ac_event_snowbound_tt'] = 'You clear a safe passage in two days without paying the guides.'
add('travel_danger_events.3001', 'travel', travel_option('avalanche', 'Hold the snow steady. I can reach them!', 'avalanche', '''ac_event_saved_companion_effect = { COMPANION = scope:first_avalanche_victim }
ac_event_saved_companion_effect = { COMPANION = scope:second_avalanche_victim }
current_travel_plan = { delay_travel_plan = { days = 2 } }''', major=True))
add('travel_danger_events.1006', 'travel', travel_option('forest', 'Let chi show us the road beyond these trees.', 'scouting', 'custom_tooltip = ac_event_forest_tt'))
LOCALIZATION['ac_event_forest_tt'] = 'Your cultivation reveals a route out of the forest without paying for a guide or adding a delay.'
add('travel_danger_events.3000', 'travel', travel_option('mountain_rescue', 'Catch them upon the wind!', 'fall_rescue', 'ac_event_saved_companion_effect = { COMPANION = scope:fallen_victim }'))

add('travel_events.3070', 'travel',
    travel_option('bridge_mido', 'Try stopping an Iron Body with that little blade.', 'bridge_mido', '''scope:bandit_scope = { increase_wounds_no_death_effect = { REASON = fight } }
add_prestige = 25
custom_tooltip = ac_event_bridge_mido_tt'''),
    travel_option('bridge_akakiru', 'One cut, and your weapons fall into the river.', 'bridge_akakiru', 'add_prestige = 25\ncustom_tooltip = ac_event_bridge_blade_tt'),
    travel_option('bridge_storm', 'Let thunder collect your toll.', 'storm', 'add_dread = 5\ncustom_tooltip = ac_event_bridge_storm_tt'),
    travel_option('bridge_darkness', 'Our shadows will cross where your eyes cannot follow.', 'darkness', 'custom_tooltip = ac_event_bridge_darkness_tt'))
LOCALIZATION.update(ac_event_bridge_mido_tt='The cultivator overpowers and wounds the bandit leader. Your party crosses without paying or risking a knight.', ac_event_bridge_blade_tt='A precise display of Akakiru disarms the bandits and clears the bridge.', ac_event_bridge_storm_tt='A thunderclap scatters the bandits. You cross without paying the toll.', ac_event_bridge_darkness_tt='You conceal the party\'s crossing and slip past without a fight or payment.')

add('travel_danger_events.6030', 'travel',
    travel_option('safe_forage', 'I know which roots will feed us and which will kill us.', 'foraging', '''if = {
    limit = { has_government = landless_adventurer_government }
    domicile = { change_provisions = minor_provisions_loss }
}
custom_tooltip = ac_event_safe_forage_tt'''),
    travel_option('ice_supplies', 'Buy fresh stores. I will keep these cold.', 'preservation', '''remove_short_term_gold = tiny_gold_value
if = {
    limit = { has_government = landless_adventurer_government }
    domicile = { change_provisions = minor_provisions_loss }
}
add_character_modifier = { modifier = ac_event_preserved_provisions_modifier months = 6 }
custom_tooltip = ac_event_ice_supplies_tt'''))
LOCALIZATION.update(ac_event_safe_forage_tt='You replace spoiled food with safe forage, avoiding poisonous plants and illness.', ac_event_ice_supplies_tt='The spoiled food is discarded. You purchase replacements and keep them fresh with ice; this does not restore rotten food.')
add('travel_danger_events.9040', 'travel', travel_option('rainstorm', 'Their chi is still close. Follow me!', 'rain_search', 'ac_event_saved_companion_effect = { COMPANION = scope:victim }'))

for event_id in ['health.4000', 'health.4001', 'health.4002']:
    add(event_id, 'health', option('heal_wounds', 'Let me mend these wounds with chi.', '''ac_event_healer_trigger = yes
scope:sick_character = { is_alive = yes has_trait = wounded }
OR = {
    scope:sick_character = root
    location = scope:sick_character.location
}''', '''save_scope_as = ac_event_practitioner
scope:sick_character = { ac_heal_one_wound_effect = yes }
ac_event_chi_healing_cooldown_effect = yes
ac_event_exertion_effect = yes''', 'ac_event_heal_tt'))

add('hunt.4007', 'activity', option('hunt_beast', 'A cultivated stance is enough to break its charge.', 'ac_event_hunt_control_trigger = yes', '''save_scope_as = ac_event_practitioner
save_scope_as = rampant_scare
ac_event_exertion_effect = yes
custom_tooltip = ac_event_hunt_beast_tt'''))
LOCALIZATION['ac_event_hunt_beast_tt'] = 'Your technique forces the beast to retreat. You and your companion avoid injury; the hunt continues normally.'
add('hunt.4010', 'activity', option('hunt_defend', 'Your blade will never reach them.', 'ac_event_hunt_defend_trigger = yes', '''save_scope_as = ac_event_practitioner
scope:targeted_participant = {
    add_opinion = { target = root modifier = saved_my_life_opinion opinion = 30 }
}
if = {
    limit = { exists = scope:murder_secret }
    scope:murder_secret = { expose_secret = root }
}
scope:activity = {
    add_activity_log_entry = {
        key = hunt_family_defend_log
        score = 25
        tags = { random good scheme intent }
        character = scope:targeted_participant
        target = scope:schemer
    }
}
ac_event_exertion_effect = yes
custom_tooltip = ac_event_hunt_defend_tt'''))
LOCALIZATION['ac_event_hunt_defend_tt'] = 'You interrupt the attack and protect its intended victim. Any active scheme is exposed by the normal event follow-up.'
add('hold_court.6000', 'activity', option('restore_fields', 'We shall restore these fields with cultivation and relief.', 'ac_event_restore_fields_trigger = yes', '''remove_short_term_gold = tiny_gold_value
save_scope_as = ac_event_practitioner
scope:6000_province.county = {
    add_county_modifier = { modifier = ac_event_restored_fields_modifier years = 3 }
}
ac_event_exertion_effect = yes
custom_tooltip = ac_event_restore_fields_tt'''))
LOCALIZATION['ac_event_restore_fields_tt'] = 'You fund a local relief project. The petitioning county gains three years of improved recovery and supply; famine and epidemics are not instantly removed.'
add('hold_court.5010', 'activity',
    option('warded_patrols', 'Ward the patrol posts. Make the roads safe again.', 'ac_event_warded_patrols_trigger = yes', '''remove_short_term_gold = tiny_gold_value
save_scope_as = ac_event_practitioner
scope:county = {
    add_county_modifier = { modifier = ac_event_warded_patrols_modifier years = 3 }
}
ac_event_exertion_effect = yes'''),
    option('martial_patrols', 'I will lead the patrols and train their captains.', 'ac_event_martial_patrols_trigger = yes', '''remove_short_term_gold = tiny_gold_value
save_scope_as = ac_event_practitioner
scope:county = {
    add_county_modifier = { modifier = ac_event_cultivator_patrols_modifier years = 3 }
}
ac_event_exertion_effect = yes'''))

add('travel_danger_events.6020', 'fatal', travel_option('survive_sea_storm', 'Gather your chi! This ship will not sink!', 'sea_rescue', 'custom_tooltip = ac_event_sea_saved_tt', major=True, extra_trigger='exists = scope:ac_event_sea_rescue_pending'))
add('host_dinner_events.1091', 'fatal', option('purge_poison', 'Force the poison out before it reaches my heart.', 'exists = scope:ac_event_poison_rescue_pending ac_event_poison_survival_trigger = yes', '''save_scope_as = ac_event_practitioner
add_character_modifier = { modifier = ac_event_poison_recovery_modifier months = 6 }
ac_event_great_exertion_effect = yes
add_opinion = { target = scope:stop_host_scope modifier = attempted_murder_opinion }
scope:activity = {
    add_activity_log_entry = {
        key = ac_event_poison_survived_log
        show_in_conclusion = yes
        tags = { bad }
        character = root
        target = scope:stop_host_scope
    }
}
send_interface_toast = {
    type = event_toast_effect_good
    title = ac_event_poison_survived_toast
    left_icon = root
}
custom_tooltip = ac_event_poison_saved_tt'''))

from event_expansion_specs import register
register(globals())

from event_activity_specs import register as register_activities
register_activities(globals())

from event_dlc_specs import register as register_dlc
register_dlc(globals())
