"""Sect jobs use native contract letters, acceptance/travel and reward objects."""

ENCOUNTERS = {
    'patrol': ('Brigands on the Sect Roads', 'The merchants were right: a barricade blocks the road at [ac_mission_contract.GetLocation.GetName]. Armed men watch the wagons from the trees. I must clear the route without leaving the travellers exposed.', 'Scout their positions before advancing.', 'Strike at the barricade before they can scatter.', 'Break their line with my martial cultivation.', 'OR = { has_trait = ac_style_akakiru has_trait = ac_style_midorikatai }'),
    'herbs': ('The Hidden Harvest', 'The medicinal plants grow above a treacherous stream at [ac_mission_contract.GetLocation.GetName]. A hurried harvest could destroy the roots or spoil the medicine. The pavilion needs living, usable specimens.', 'Identify the mature plants and prepare containers.', 'Climb down and harvest before the weather turns.', 'Guide water and earth around the fragile roots.', 'OR = { has_trait = ac_element_earth has_trait = ac_element_water }'),
    'manual': ('The Missing Scripture', 'My inquiries in [ac_mission_contract.GetLocation.GetName] lead to a dealer who insists the missing scripture is an innocent purchase. His locked storeroom may hold the original, but a public accusation will warn him.', 'Watch the dealer and trace his suppliers.', 'Confront him and demand the scripture.', 'Use Kurokonton to enter the storeroom unseen.', 'has_trait = ac_style_kurokonton'),
    'mediation': ('Two Houses, One Grievance', 'The feuding households at [ac_mission_contract.GetLocation.GetName] have finally agreed to hear the sect\'s representative. Each brings witnesses, accusations, and a different account of the same boundary.', 'Hear both accounts and examine the boundary.', 'Propose a settlement before the argument worsens.', 'Use Aoyusumu to understand the words left unspoken.', 'has_trait = ac_style_aoyusumu'),
    'relief': ('A Village in Need', 'At [ac_mission_contract.GetLocation.GetName], damaged stores and sickness threaten the coming season. I can organize what remains, but the villagers need a workable recovery, not promises.', 'Inventory the supplies and organize their distribution.', 'Put every available hand to work immediately.', 'Restore clean water and tend the sick through cultivation.', 'OR = { has_trait = ac_style_aoyusumu has_trait = ac_element_water }'),
    'escort': ('The Delegation at the Crossing', 'The sect delegation has reached [ac_mission_contract.GetLocation.GetName], where a narrow crossing leaves the tribute exposed. Riders have been following us. I must bring the envoys and their correspondence through safely.', 'Secure the crossing and arrange a protective formation.', 'Lead the delegation across before the riders arrive.', 'Use Kiihakai or Midorikatai to shield the delegation.', 'OR = { has_trait = ac_style_kiihakai has_trait = ac_style_midorikatai }'),
}


def render(missions, loc):
    files, contracts, effects, events = {}, [], [], ['namespace = ac_sect_job']
    for index, (key, name, desc, skill, reward) in enumerate(missions, 1):
        eid = f'ac_sect_job.{index:04}'
        contracts.append(f'''ac_sect_{key} = {{
group = ac_sect_missions
icon = "gfx/interface/icons/traits/ac_cultivator.dds"
desc = ac_sect_{key}_desc
task_contract_request = ac_sect_{key}_request
travel = no
is_criminal = no
use_diplomatic_range = yes
valid_to_create = {{ ac_sect_member_trigger = yes }}
valid_to_accept = {{ ac_sect_mission_ready_trigger = yes }}
valid_to_keep = {{
    var:ac_contract_disciple = {{ ac_sect_member_trigger = yes var:ac_sect = prev.var:ac_contract_sect }}
}}
valid_to_continue = {{
    task_contract_taker = {{ ac_sect_member_trigger = yes ac_sect_available_trigger = yes var:ac_sect = prev.var:ac_contract_sect }}
}}
on_create = {{
    scope:contract = {{
        set_variable = {{ name = ac_contract_sect value = prev.var:ac_sect }}
        set_variable = {{ name = ac_contract_disciple value = prev }}
        set_variable = {{ name = ac_contract_version value = 2 }}
    }}
}}
on_accepted = {{
    save_scope_as = ac_mission_contract
        task_contract_taker = {{
        set_variable = {{ name = ac_sect_mission value = scope:ac_mission_contract }}
        set_variable = {{ name = ac_sect_mission_kind value = flag:{key} }}
        set_variable = {{ name = ac_sect_mission_bonus value = 0 }}
        play_sound_effect = "event:/DLC/EP3/SFX/UI/Contracts/ep3_ui_contracts_accept_contract"
        ac_sect_depart_for_contract_effect = yes
    }}
}}
on_completed = {{ ac_sect_contract_cleanup_effect = yes }}
on_invalidated = {{ ac_sect_contract_cleanup_effect = yes }}
task_contract_reward = {{
    ac_sect_{key}_success = {{
        visible = yes positive = yes should_print_on_complete = yes
        effect = {{
            custom_tooltip = ac_sect_{key}_reward_tt
            hidden_effect = {{
            save_scope_as = ac_reward_contract
            task_contract_taker = {{
                ac_sect_award_contribution_effect = {{ VALUE = ac_sect_{key}_reward_value }}
                add_ac_cultivation_lifestyle_xp = ac_sect_contract_xp_value
                var:ac_sect = {{ change_variable = {{ name = ac_treasury add = 20 }} }}
                play_sound_effect = "event:/DLC/EP3/SFX/UI/Contracts/ep3_ui_contracts_success_on_contract"
            }}
        }}
        }}
    }}
    ac_sect_{key}_failure = {{ visible = yes positive = no effect = {{ task_contract_taker = {{ add_stress = 15 }} }} }}
    ac_sect_{key}_abandoned = {{ visible = no positive = no effect = {{ }} }}
}}
should_show_toast_on_complete = yes
weight = {{ value = 0 }}
}}''')
        # Offers belong to the disciple, just like native adventurer contracts.
        # Store persistent scopes instead of manufacturing a new job on accept.
        effects.append(f'''ac_sect_offer_{key}_effect = {{
if = {{
    limit = {{ NOT = {{ has_variable = ac_sect_offer_{key} }} }}
    var:ac_sect.var:ac_headquarters = {{ save_scope_as = ac_job_location }}
    var:ac_sect.var:ac_kingdom = {{
        random_de_jure_county = {{
            limit = {{ exists = title_province exists = holder }}
            title_province = {{ save_scope_as = ac_job_location }}
        }}
    }}
    create_task_contract = {{
        task_contract_type = ac_sect_{key}
        task_contract_tier = ac_sect_offer_tier
        task_contract_employer = var:ac_sect.story_owner
        location = scope:ac_job_location
        save_scope_as = ac_created_contract
    }}
    set_variable = {{ name = ac_sect_offer_{key} value = scope:ac_created_contract }}
    add_to_variable_list = {{ name = ac_sect_offers target = scope:ac_created_contract }}
}}
}}
ac_sect_start_{key}_effect = {{
if = {{
    limit = {{ ac_sect_mission_ready_trigger = yes }}
    ac_sect_offer_{key}_effect = yes
    accept_task_contract = var:ac_sect_offer_{key}
}}
}}''')
        title, narrative, careful, bold, cultivation, gate = ENCOUNTERS[key]
        events.append(f'''{eid} = {{
type = character_event
title = {eid}.t
desc = {eid}.desc
theme = {('intrigue' if key == 'manual' else 'learning' if key == 'herbs' else 'martial')}
trigger = {{
    ac_sect_member_trigger = yes
    var:ac_sect_mission ?= scope:ac_mission_contract
    var:ac_sect = scope:ac_mission_contract.var:ac_contract_sect
    scope:ac_mission_contract = {{ NOT = {{ has_variable = ac_resolved }} }}
}}
option = {{
    name = {eid}.careful
    custom_tooltip = ac_sect_job_careful_tt
    set_variable = {{ name = ac_sect_mission_bonus value = 10 }}
    ac_sect_resolve_mission_effect = yes
}}
option = {{
    name = {eid}.expert
    trigger = {{ {skill} >= 15 }}
    custom_tooltip = ac_sect_job_expert_tt
    set_variable = {{ name = ac_sect_mission_bonus value = 20 }}
    ac_sect_resolve_mission_effect = yes
}}
option = {{
    name = {eid}.cultivation
    trigger = {{ {gate} }}
    custom_tooltip = ac_sect_job_cultivation_tt
    set_variable = {{ name = ac_sect_mission_bonus value = 25 }}
    add_stress = 10
    ac_sect_resolve_mission_effect = yes
}}
option = {{ name = ac_sect_mission.0002.abandon ac_sect_cancel_mission_effect = yes }}
}}''')
        loc.update({f'{eid}.t': title, f'{eid}.desc': narrative, f'{eid}.careful': careful,
                    f'{eid}.expert': bold, f'{eid}.cultivation': cultivation,
                    f'ac_sect_{key}': name, f'ac_sect_{key}_contract': name, f'ac_sect_{key}_desc': desc, f'ac_sect_{key}_desc_title': name,
                    f'task_contract_reward_effect_ac_sect_{key}_success_desc': 'Sect service rewarded',
                    f'task_contract_reward_effect_ac_sect_{key}_failure_desc': 'The assignment fails',
                    f'task_contract_reward_effect_ac_sect_{key}_abandoned_desc': 'The assignment is abandoned without reward.',
                    f'ac_sect_{key}_reward_tt': f'Gain {reward} contribution, {reward} Sect Merit and 40 Cultivation XP per difficulty level. The sect treasury gains 20 gold.',
                    f'ac_sect_{key}_request': f'Accept the assignment, arrange travel to its location, and resolve the encounter. Success earns {reward} contribution per difficulty level and 40 Cultivation XP per level. Strong {skill} helps. Failure causes 15 stress; completion or abandonment requires 90 days of rest.'})
        for result in ('success', 'failure', 'abandoned'):
            loc[f'ac_sect_{key}_{result}'] = f'{name}: {result.title()}'
    effects.append('''ac_sect_contract_cleanup_effect = {
save_scope_as = ac_cleaned_contract
clear_saved_scope = ac_cleaned_disciple
if = { limit = { exists = var:ac_contract_disciple } var:ac_contract_disciple = { save_scope_as = ac_cleaned_disciple } }
else = { task_contract_taker ?= { save_scope_as = ac_cleaned_disciple } }
scope:ac_cleaned_disciple ?= {
    remove_list_variable = { name = ac_sect_offers target = scope:ac_cleaned_contract }

''')
    for key, *_ in missions:
        effects.append(f'if = {{ limit = {{ var:ac_sect_offer_{key} ?= scope:ac_cleaned_contract }} remove_variable = ac_sect_offer_{key} }}')
    effects.append('''
    if = {
        limit = { var:ac_sect_mission ?= scope:ac_cleaned_contract }
        remove_variable = ac_sect_mission
        remove_variable = ac_sect_mission_kind
        remove_variable = ac_sect_mission_bonus
        remove_variable = ac_sect_mission_journey
        add_character_flag = { flag = ac_sect_mission_cooldown days = 90 }
    }
}
}
ac_sect_clear_offers_effect = {
''')
    # No iterator mutation: invalidate each named scope, cleanup removes list entry.
    for key, *_ in missions:
        effects.append(f'var:ac_sect_offer_{key} ?= {{ invalidate_contract = yes }}\nremove_variable = ac_sect_offer_{key}')
    effects.append('clear_variable_list = ac_sect_offers\n}')
    for outcome in ('abandoned', 'success', 'failure'):
        effect = 'cancel' if outcome == 'abandoned' else outcome
        effects.append(f'ac_sect_{"cancel_mission" if outcome == "abandoned" else "mission_" + effect}_effect = {{')
        for index, (key, *_) in enumerate(missions):
            branch = 'if' if index == 0 else 'else_if'
            effects.append(f'{branch} = {{ limit = {{ var:ac_sect_mission_kind ?= flag:{key} }} var:ac_sect_mission ?= {{ complete_task_contract = ac_sect_{key}_{outcome} }} }}')
        effects.append('}')
    effects.append('''ac_sect_open_contract_board_effect = {
if = {
    limit = { ac_sect_member_trigger = yes }
    remove_variable = ac_sect_window_open
    remove_variable = ac_sect_estate_open
    # Old timer-based commissions cannot silently resolve under the new rules.
    if = {
        limit = { var:ac_sect_mission ?= { NOT = { has_variable = ac_contract_version } } }
        ac_sect_cancel_mission_effect = yes
        remove_character_flag = ac_sect_mission_cooldown
    }
''')
    effects.extend(f'ac_sect_offer_{key}_effect = yes' for key, *_ in missions)
    effects.append('set_variable = { name = ac_sect_contract_board_open value = 1 }\n}\n}')
    effects.append("""
# Match the native transport-contract pattern: reserve the contract first,
# then travel. This avoids the government-specific travel-to-accept handoff.
ac_sect_depart_for_contract_effect = {
if = {
    limit = { location = var:ac_sect_mission.task_contract_location }
    trigger_event = ac_sect_mission.0003
}
else = {
    start_travel_plan = {
        destination = var:ac_sect_mission.task_contract_location
        players_use_planner = yes return_trip = yes travel_with_domicile = no
        on_arrival_event = ac_sect_mission.0003
        on_arrival_destinations = all
        on_start_event = ac_sect_mission.0005
        on_travel_planner_cancel_event = ac_sect_mission.0004
    }
}
}
""")
    files['common/script_values/ac_sect_contract_rewards.txt'] = '\n'.join(f'ac_sect_{key}_reward_value = {{ value = {reward} multiply = scope:ac_reward_contract.task_contract_tier }}' for key, _, _, _, reward in missions) + '\nac_sect_contract_xp_value = { value = 40 multiply = scope:ac_reward_contract.task_contract_tier }\n'
    files['common/task_contracts/ac_sect_contracts.txt'] = '\n'.join(contracts)
    files['common/scripted_effects/ac_sect_contract_effects.txt'] = '\n'.join(effects)
    files['events/ac_sect_job_events.txt'] = '\n'.join(events)
    # Preserve the old entry event ID for decisions, interactions and saved queues.
    files['events/ac_sect_mission_board.txt'] = '''namespace = ac_sect_mission
ac_sect_mission.0001 = {
type = character_event hidden = yes
trigger = { ac_sect_member_trigger = yes }
immediate = { ac_sect_open_contract_board_effect = yes }
}
'''
    loc.update({'ac_sect_job_careful_tt': 'A careful approach improves the success chance by 10 percentage points.',
                'ac_sect_job_expert_tt': 'Your expertise improves the success chance by 20 percentage points.',
                'ac_sect_job_cultivation_tt': 'The matching cultivation improves the success chance by 25 percentage points, at a cost of 10 stress.'})
    return files
