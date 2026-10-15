"""Isolated UI fixture for native sect contract letters/travel and HUD buttons.

Launch the printed CK3 command, review and accept a contract, start travel,
resolve its encounter, then click Audit. The player's normal saves/settings
are untouched. Startup also checks all six native reward objects.
"""
from pathlib import Path
import subprocess
import sys

import prepare_sect_engine_checks as harness
import build_sect_content as content

ROOT = harness.ROOT
OUT = ROOT / 'output/sect-contract-ui'


def main():
    subprocess.run([sys.executable, str(ROOT / 'tools/prepare_sect_engine_checks.py'),
                    '--estate-ui', '--out', str(OUT)], check=True)
    overlay = OUT / 'qa-mod'
    # No old construction/activity audits in this independent fixture.
    for relative in ('events/ac_sect_qa_estate.txt', 'common/scripted_guis/ac_sect_qa_estate.txt',
                     'gui/ac_sect_qa_estate.gui', 'gui/scripted_widgets/ac_sect_qa_estate.txt',
                     'common/script_values/ac_sect_qa_estate.txt'):
        path = overlay / relative
        if path.exists():
            path.write_text('', encoding='utf-8-sig')
    (overlay / 'common/task_contracts/ac_sect_contracts.txt').unlink(missing_ok=True)
    (overlay / 'common/on_action/ac_sect_qa_startup.txt').write_text('''
on_game_start_after_lobby = { on_actions = { ac_sect_qa_startup } }
ac_sect_qa_startup = { effect = {
 title:k_wales.var:ac_kingdom_sect = { save_scope_as = ac_join_sect }
 title:k_england.holder = {
  ac_sect_join_effect = yes
  every_character_war = { end_war = white_peace }
  set_variable = { name = ac_qa_contribution_before value = var:ac_sect_contribution }
  ac_sect_open_contract_board_effect = yes
  if = {
   limit = { num_taken_task_contracts = 0 has_variable = ac_sect_offer_patrol has_variable = ac_sect_offer_herbs }
   debug_log = "AC_CONTRACT_QA PASS offers_posted_without_accepting"
  } else = { debug_log = "AC_CONTRACT_QA FAIL offers_posted_without_accepting" }
  ac_sect_open_contract_board_effect = yes
  if = {
   limit = { any_in_list = { variable = ac_sect_offers count = 6 } }
   debug_log = "AC_CONTRACT_QA PASS reopening_keeps_six_offers"
  } else = { debug_log = "AC_CONTRACT_QA FAIL reopening_keeps_six_offers" }
 }
} }
''', encoding='utf-8-sig')
    # Run every native reward object on a disposable NPC. Its arrival event
    # is suppressed below so an immediate AI choice cannot resolve the job
    # before the explicit reward and duplicate-payment assertions.
    checks = ['title:k_wales.var:ac_kingdom_sect = { random_in_list = { variable = ac_members limit = { has_trait = ac_sect_lower_disciple is_ai = yes } save_scope_as = ac_contract_test_agent } }',
              'scope:ac_contract_test_agent = { add_character_flag = ac_contract_qa_reward_probe set_variable = { name = ac_sect_contribution value = 0 } set_variable = { name = ac_sect_merit value = 0 }']
    expected = 0
    for key, _, _, _, reward in content.MISSIONS:
        expected += reward
        checks.append(f'''remove_character_flag = ac_sect_mission_cooldown
create_task_contract = {{ task_contract_type = ac_sect_{key} task_contract_tier = 1 task_contract_employer = var:ac_sect.story_owner location = location save_scope_as = ac_test_local_contract }}
accept_task_contract = scope:ac_test_local_contract
var:ac_sect_mission = {{ complete_task_contract = ac_sect_{key}_success }}
ac_sect_resolve_mission_effect = yes
if = {{ limit = {{ var:ac_sect_contribution = {expected} var:ac_sect_merit = {expected} NOT = {{ has_variable = ac_sect_mission }} }} debug_log = "AC_CONTRACT_QA PASS {key}_reward_once" }} else = {{ debug_log = "AC_CONTRACT_QA FAIL {key}_reward_once" }}''')
    checks += ['''remove_character_flag = ac_sect_mission_cooldown
create_task_contract = { task_contract_type = ac_sect_patrol task_contract_tier = 1 task_contract_employer = var:ac_sect.story_owner location = location save_scope_as = ac_test_local_contract }
accept_task_contract = scope:ac_test_local_contract
ac_sect_cancel_mission_effect = yes
ac_sect_resolve_mission_effect = yes
if = { limit = { var:ac_sect_contribution = 330 has_character_flag = ac_sect_mission_cooldown NOT = { has_variable = ac_sect_mission } } debug_log = "AC_CONTRACT_QA PASS abandonment_no_reward" } else = { debug_log = "AC_CONTRACT_QA FAIL abandonment_no_reward" }
ac_sect_clear_offers_effect = yes
if = { limit = { NOT = { has_variable = ac_sect_offer_patrol } NOT = { any_in_list = { variable = ac_sect_offers } } } debug_log = "AC_CONTRACT_QA PASS offers_cleared" } else = { debug_log = "AC_CONTRACT_QA FAIL offers_cleared" }
}''']
    path = overlay / 'common/on_action/ac_sect_qa_startup.txt'
    source = path.read_text(encoding='utf-8-sig').replace('ac_sect_qa_startup = { effect = {', 'ac_sect_qa_startup = { effect = {\n' + '\n'.join(checks))
    path.write_text(source, encoding='utf-8-sig')
    # NPCs choose event options synchronously. Suppress only the probe NPC's
    # arrival dispatcher so each explicit native reward can be tested once;
    # player journeys and all contract callbacks/reward effects stay unchanged.
    source = (ROOT / 'AuraClash/events/ac_sect_mission_events.txt').read_text(encoding='utf-8-sig')
    source = source.replace(
        'exists = var:ac_sect_mission\n  location =',
        'exists = var:ac_sect_mission\n  NOT = { has_character_flag = ac_contract_qa_reward_probe }\n  location =')
    (overlay / 'events/ac_sect_mission_events.txt').write_text(source, encoding='utf-8-sig')
    path = overlay / 'common/scripted_guis/ac_sect_qa_contracts.txt'
    path.write_text('''ac_sect_qa_contracts = {
 scope = character
 is_shown = { ac_sect_member_trigger = yes }
 effect = {
  if = {
   limit = { primary_title = title:k_england has_government = feudal_government }
   debug_log = "AC_CONTRACT_QA PASS ruler_keeps_titles_and_government"
  } else = { debug_log = "AC_CONTRACT_QA FAIL ruler_keeps_titles_and_government" }
  if = {
   limit = { has_character_flag = ac_sect_mission_cooldown NOT = { has_variable = ac_sect_mission } num_taken_task_contracts = 0 }
   debug_log = "AC_CONTRACT_QA PASS contract_resolved_and_cleaned"
  } else = { debug_log = "AC_CONTRACT_QA FAIL contract_resolved_and_cleaned" }
  if = {
   limit = { var:ac_sect_contribution > var:ac_qa_contribution_before var:ac_sect_merit = var:ac_sect_contribution }
   debug_log = "AC_CONTRACT_QA PASS contribution_and_merit_awarded"
  } else = { debug_log = "AC_CONTRACT_QA RESULT no_success_reward" }
 }
}''', encoding='utf-8-sig')
    (overlay / 'gui/ac_sect_qa_contracts.gui').write_text('''window = {
 name = "ac_sect_qa_contracts" layer = windows_layer
 parentanchor = bottom|hcenter size = { 340 40 } position = { 0 -45 }
 button_standard = { size = { 340 40 } raw_text = "Audit contract state (test only)"
 onclick = "[GetScriptedGui('ac_sect_qa_contracts').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }
}''', encoding='utf-8-sig')
    (overlay / 'gui/scripted_widgets/ac_sect_qa_contracts.txt').write_text(
        'gui/ac_sect_qa_contracts.gui = ac_sect_qa_contracts\n', encoding='utf-8-sig')


if __name__ == '__main__':
    main()
