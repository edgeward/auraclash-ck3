"""Prepare an isolated CK3 user folder and startup smoke-test overlay.

CK3 1.20.1 retail crashes in -nographics even without mods on the reference
installation. This harness uses an ordinary windowed test process and
logs assertions without requiring console/desktop automation. It does not
modify the user's normal CK3 settings or saves. It never starts the game itself.
"""
from pathlib import Path
import argparse
import json
import re
import shutil

import build_event_overrides as script

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/sect-runtime'
OVERLAY = OUT / 'qa-mod'


def extract_tests():
    source = (ROOT / 'AuraClash/tests/ac_sect_tests.txt').read_text(encoding='utf-8-sig')
    tests = {}
    for m in re.finditer(r'^(ac_sect_test_\w+)\s*=\s*\{', source, re.M):
        tests[m[1]] = source[m.start():script.close_brace(source, source.index('{', m.start()))]
    return dict(sorted(tests.items()))


def test_body(name, body, skip_effect=False, only_effect=False, after_effect=False):
    results = []
    seen_effect = False
    for n, field in enumerate(script.fields(body)):
        content = field.body(body)
        if field.key == 'effect':
            seen_effect = True
        if after_effect and not seen_effect:
            continue
        if field.key == 'effect' and not skip_effect:
            results.append(content)
        elif field.key in ('assert', 'expect') and not only_effect:
            condition = re.sub(r'\broot\b', 'title:k_england', content)
            results.append(f'''if = {{
                limit = {{ {condition} }}
                debug_log = "AC_SECT_QA PASS {name}:{n}"
            }} else = {{ debug_log = "AC_SECT_QA FAIL {name}:{n}" }}''')
    return '\n'.join(results)


def main():
    global OUT, OVERLAY
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--out', type=Path, help='Use a separate isolated output folder for a concurrent fixture.')
    arguments.add_argument('--master-ui', action='store_true', help='Prepare a player Sect Master for manual activity-planner verification.')
    arguments.add_argument('--estate-ui', action='store_true', help='Open a player Master native domicile for UI verification.')
    args = arguments.parse_args()
    if args.out:
        OUT = args.out.resolve()
        if not OUT.is_relative_to(ROOT / 'output'):
            raise SystemExit('QA output must stay inside the workspace output directory.')
        OVERLAY = OUT / 'qa-mod'
    args.master_ui = args.master_ui or args.estate_ui
    tests = extract_tests()
    action = ['on_game_start_after_lobby = { on_actions = { ac_sect_qa_startup } }',
              'ac_sect_qa_startup = { effect = { debug_log = "AC_SECT_QA BEGIN" title:k_england = {']
    for name, body in tests.items():
        if '_06_' in name:
            for field in script.fields(body):
                if field.key == 'effect':
                    effect = field.body(body)
                    effect = effect.replace('story_owner = { death = natural }', '''
                        set_global_variable = { name = ac_qa_inherited_sect value = this }
                        set_global_variable = { name = ac_qa_expected_master value = scope:ac_test_ruler }
                        set_global_variable = { name = ac_qa_inherited_domicile value = scope:ac_inherited_domicile }
                        set_global_variable = { name = ac_qa_ally_master value = scope:recipient }
                        story_owner = { death = natural }
                    ''')
                    action.append(effect)
            break
        action.append(test_body(name, body))
    action += ['} } }']
    path = OVERLAY / 'common/on_action/ac_sect_qa_startup.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(action), encoding='utf-8-sig')

    # Audit real owner-death processing at the end of the production successor
    # effect. The test overlay copies the production file and only appends the
    # audit; the shipping story hook and succession code execute unchanged.
    core = (ROOT / 'AuraClash/common/scripted_effects/ac_sect_core_effects.txt').read_text(encoding='utf-8-sig')
    marker = core.index('ac_sect_succession_effect = {')
    end = script.close_brace(core, core.index('{', marker)) - 1
    sixth = next((k, v) for k, v in tests.items() if '_06_' in k)
    remaining = [(k, v) for k, v in tests.items() if int(k.split('_')[3]) in (7, 9, 13, 14, 15, 16)]
    check = test_body(*sixth, skip_effect=True)
    for old, new in {'ac_test_ruler': 'ac_qa_expected_master', 'ac_inherited_sect': 'ac_qa_inherited_sect', 'recipient': 'ac_qa_ally_master', 'ac_inherited_domicile': 'ac_qa_inherited_domicile'}.items():
        check = check.replace('scope:' + old, 'global_var:' + new)
    audit = '''
    if = {
        limit = { has_global_variable = ac_qa_inherited_sect this = global_var:ac_qa_inherited_sect }
        title:k_england = { ''' + check + '\n' + '\n'.join(test_body(k, v) for k, v in remaining) + ''' }
        remove_global_variable = ac_qa_inherited_sect
        title:k_england.holder = { trigger_event = { id = ac_sect_qa.0001 days = 1 } }
    }
'''
    path = OVERLAY / 'common/scripted_effects/ac_sect_core_effects.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(core[:end] + audit + core[end:], encoding='utf-8-sig')

    # AI activity planning is an asynchronous request. Submit after the startup
    # tick, then check it on a later daily tick instead of expecting immediate
    # creation from inside a story-owner-death callback.
    eighth = next((k, v) for k, v in tests.items() if '_08_' in k)
    eleventh = next((k, v) for k, v in tests.items() if '_11_' in k)
    tenth = next((k, v) for k, v in tests.items() if '_10_' in k)
    twelfth = next((k, v) for k, v in tests.items() if '_12_' in k)
    qa_events = '''namespace = ac_sect_qa
ac_sect_qa.0001 = {
    type = character_event hidden = yes
    immediate = {
        title:k_england.holder = { set_variable = { name = ac_sect_application value = title:k_england.var:ac_kingdom_sect } }
        title:k_england = { ''' + test_body(*eighth, only_effect=True) + ''' }
        title:k_denmark = { ''' + test_body(*eleventh, only_effect=True) + ''' }
        title:k_bohemia = { ''' + test_body(*twelfth, only_effect=True) + '''
            if = { limit = { has_variable = ac_kingdom_sect } debug_log = "AC_SECT_QA JOINT society exists" }
            var:ac_kingdom_sect.var:ac_headquarters.county.holder = {
                if = { limit = { is_available = yes } debug_log = "AC_SECT_QA JOINT local ruler available" }
                if = { limit = { has_variable = ac_sect_patronage } debug_log = "AC_SECT_QA JOINT patron assigned" }
                if = { limit = { can_host_activity = activity_ac_sect_joint_training } debug_log = "AC_SECT_QA JOINT host eligible" }
            }
        }
        trigger_event = { id = ac_sect_qa.0002 days = 45 }
    }
}
ac_sect_qa.0002 = {
    type = character_event hidden = yes
    immediate = {
        if = { limit = { title:k_england.var:ac_kingdom_sect.var:ac_estate_title = { holder = title:k_scotland.holder title_domicile = global_var:ac_qa_inherited_domicile } title:k_scotland.holder = { has_government = feudal_government } }
            debug_log = "AC_SECT_QA PASS native_estate_persists_after_owner_death"
        } else = { debug_log = "AC_SECT_QA FAIL native_estate_persists_after_owner_death" }
        title:k_england = { ''' + test_body(*eighth, skip_effect=True, after_effect=True) + '\n' + test_body(*tenth) + ''' }
        title:k_denmark = { ''' + test_body(*eleventh, skip_effect=True, after_effect=True) + ''' }
        title:k_bohemia = { ''' + test_body(*twelfth, skip_effect=True, after_effect=True) + ''' }
        random_activity = {
            limit = { has_activity_type = activity_ac_sect_trials var:ac_trial_sect ?= title:k_denmark.var:ac_kingdom_sect }
            save_scope_as = ac_qa_trial
            activity_host = {
                create_character = {
                    gender_female_chance = 50 age = 25 learning = 100 prowess = 100
                    culture = this.culture faith = this.faith location = scope:ac_qa_trial.activity_location
                    save_scope_as = ac_qa_natural_candidate
                }
            }
            scope:ac_qa_natural_candidate = {
                add_to_activity_without_travel = scope:ac_qa_trial
                set_global_variable = { name = ac_qa_natural_candidate value = this }
            }
        }
        trigger_event = { id = ac_sect_qa.0003 days = 220 }
    }
}
ac_sect_qa.0003 = {
    type = character_event hidden = yes
    immediate = {
        if = {
            limit = {
                global_var:ac_qa_natural_candidate = {
                    has_trait = ac_sect_lower_disciple
                    var:ac_sect ?= title:k_denmark.var:ac_kingdom_sect
                    NOT = { has_variable = ac_sect_trial_activity }
                }
            }
            debug_log = "AC_SECT_QA PASS natural_trial_full_lifecycle"
        } else = {
            debug_log = "AC_SECT_QA FAIL natural_trial_full_lifecycle"
            global_var:ac_qa_natural_candidate = {
                if = { limit = { is_alive = yes } debug_log = "AC_SECT_QA candidate alive" }
                if = { limit = { has_variable = ac_sect } debug_log = "AC_SECT_QA candidate has sect" }
                if = { limit = { has_variable = ac_sect_trial_activity } debug_log = "AC_SECT_QA candidate still in trial" }
                if = { limit = { has_character_flag = ac_sect_trial_cooldown } debug_log = "AC_SECT_QA candidate completed trial" }
            }
        }
        if = {
            limit = { title:k_bohemia.var:ac_kingdom_sect = { has_variable = ac_joint_drill } }
            debug_log = "AC_SECT_QA PASS joint_training_full_lifecycle"
        } else = { debug_log = "AC_SECT_QA FAIL joint_training_full_lifecycle" }
        if = { limit = { title:k_england.var:ac_kingdom_sect = { var:ac_alchemy_pavilion = 1 var:ac_estate_title.title_domicile = { has_domicile_building = ac_sect_alchemy_pavilion_01 NOT = { has_ongoing_domicile_construction = yes } NOT = { has_variable = ac_native_build_cost } } } }
            debug_log = "AC_SECT_QA PASS native_construction_completes_after_succession"
        } else = { debug_log = "AC_SECT_QA FAIL native_construction_completes_after_succession" }
        debug_log = "AC_SECT_QA COMPLETE"
    }
}
'''
    path = OVERLAY / 'events/ac_sect_qa.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(qa_events, encoding='utf-8-sig')

    # Trace real phase transitions; no timing or scoring is altered.
    activities = (ROOT / 'AuraClash/common/activities/activity_types/ac_sect_activities.txt').read_text(encoding='utf-8-sig')
    activities = activities.replace('on_phase_active_activity = {', 'on_phase_active_activity = { debug_log = "AC_SECT_QA PHASE"')
    activities = activities.replace('on_complete = {', 'on_complete = { debug_log = "AC_SECT_QA COMPLETION CALLBACK"')
    activities = activities.replace('on_start = {', 'on_start = { debug_log = "AC_SECT_QA ACTIVITY CREATED"')
    activities = activities.replace('on_invalidated = {', 'on_invalidated = { debug_log = "AC_SECT_QA ACTIVITY INVALIDATED"')
    path = OVERLAY / 'common/activities/activity_types/ac_sect_activities.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(activities, encoding='utf-8-sig')

    # Report the native host-eligibility result at the exact request, so an AI
    # scheduling refusal can be distinguished from a missing society or host.
    ai = (ROOT / 'AuraClash/common/scripted_effects/ac_sect_ai_effects.txt').read_text(encoding='utf-8-sig')
    ai = ai.replace('ai_attempt_to_host_activity = $ACTIVITY$', '''
        if = { limit = { can_host_activity = $ACTIVITY$ } debug_log = "AC_SECT_QA ELIGIBLE HOST" }
        else = { debug_log = "AC_SECT_QA INELIGIBLE HOST" }
        ai_attempt_to_host_activity = $ACTIVITY$''')
    path = OVERLAY / 'common/scripted_effects/ac_sect_ai_effects.txt'
    path.write_text(ai, encoding='utf-8-sig')

    if args.master_ui:
        # Keep this UI fixture separate from the applicant/lifecycle suite.
        # The player remains King of England and becomes Master of the Welsh
        # sect, whose headquarters is safely outside the opening invasion.
        (OVERLAY / 'common/on_action/ac_sect_qa_startup.txt').write_text('''
on_game_start_after_lobby = { on_actions = { ac_sect_qa_startup } }
ac_sect_qa_startup = { effect = {
    title:k_england.holder = { save_scope_as = ac_player_master }
    title:k_wales.var:ac_kingdom_sect = {
        save_scope_as = ac_join_sect
        story_owner = { save_scope_as = ac_old_master }
    }
    scope:ac_player_master = { ac_sect_join_effect = yes }
    scope:ac_old_master = { remove_trait = ac_sect_master add_trait = ac_sect_upper_disciple }
    scope:ac_player_master = {
        remove_trait = ac_sect_lower_disciple add_trait = ac_sect_master
        var:ac_sect = { make_story_owner = scope:ac_player_master set_variable = { name = ac_master value = scope:ac_player_master } ac_sect_ensure_domicile_effect = yes ac_sect_recount_effect = yes }
        if = { limit = { can_host_activity = activity_ac_sect_trials } debug_log = "AC_SECT_QA PASS player_master_can_host" }
        else = { debug_log = "AC_SECT_QA FAIL player_master_can_host" }
    }
} }
''', encoding='utf-8-sig')
        (OVERLAY / 'common/scripted_effects/ac_sect_core_effects.txt').write_text(core, encoding='utf-8-sig')
        if not args.estate_ui:
            activities = activities.replace('on_start = {', 'on_start = { scope:host = { if = { limit = { is_ai = no } trigger_event = { id = ac_sect_qa.0010 days = 2 } } }')
        (OVERLAY / 'common/activities/activity_types/ac_sect_activities.txt').write_text(activities, encoding='utf-8-sig')
        (OVERLAY / 'events/ac_sect_qa.txt').write_text('''namespace = ac_sect_qa
ac_sect_qa.0010 = { type = character_event hidden = yes immediate = {
    if = {
        limit = {
            scope:activity = {
                activity_host = title:k_england.holder
                activity_location = title:k_wales.var:ac_kingdom_sect.var:ac_headquarters
                var:ac_trial_master = title:k_england.holder
            }
        }
        debug_log = "AC_SECT_QA PASS player_master_planner_created_trial_at_headquarters"
    } else = { debug_log = "AC_SECT_QA FAIL player_master_planner_created_trial_at_headquarters" }
} }
''', encoding='utf-8-sig')

    if args.estate_ui:
        # This fixture does not exercise the activity planner; do not retain
        # its unused event or attach its assertions to unrelated NPC trials.
        (OVERLAY / 'events/ac_sect_qa.txt').write_text('namespace = ac_sect_qa\n', encoding='utf-8-sig')
        path = OVERLAY / 'common/on_action/ac_sect_qa_startup.txt'
        source = path.read_text(encoding='utf-8-sig').replace('if = { limit = { can_host_activity', '''
        every_character_war = { end_war = white_peace }
        set_variable = { name = ac_qa_estate_step value = 0 }
        set_variable = { name = ac_qa_estate_gold value = gold }
        set_variable = { name = ac_qa_estate_treasury value = var:ac_sect.var:ac_treasury }
        ac_sect_open_estate_effect = yes
        if = { limit = { can_host_activity''')
        estate_checks = [(name, body) for name, body in tests.items() if int(name.split('_')[3]) in (15, 16)]
        source = source.replace('every_character_war =', 'title:k_wales = { ' + '\n'.join(test_body(*check) for check in estate_checks) + ' }\n        every_character_war =')
        path.write_text(source, encoding='utf-8-sig')
        # Manual fixture: construct Alchemy Pavilion I in the native UI, audit,
        # cancel it in the native UI, audit, then construct/audit and unpause.
        (OVERLAY / 'events/ac_sect_qa_estate.txt').write_text('''namespace = ac_sect_qa
ac_sect_qa.0020 = { type = character_event hidden = yes immediate = {
    if = {
        limit = { OR = { var:ac_qa_estate_step = 0 var:ac_qa_estate_step = 2 } }
        if = {
            limit = {
                primary_title = title:k_england has_government = feudal_government
                gold = var:ac_qa_estate_gold
                var:ac_sect.var:ac_treasury = ac_qa_estate_after_cost
                var:ac_sect.var:ac_estate_title.title_domicile = { has_domicile_construction = ac_sect_alchemy_pavilion_01 var:ac_native_build_cost = 100 }
            }
            debug_log = "AC_SECT_QA PASS native_UI_build_spends_only_sect_gold"
            change_variable = { name = ac_qa_estate_step add = 1 }
            if = { limit = { var:ac_qa_estate_step = 3 } trigger_event = { id = ac_sect_qa.0021 days = 200 } }
        } else = { debug_log = "AC_SECT_QA FAIL native_UI_build_spends_only_sect_gold" }
    }
    else_if = {
        limit = { var:ac_qa_estate_step = 1 }
        if = {
            limit = {
                gold = var:ac_qa_estate_gold
                var:ac_sect.var:ac_treasury = var:ac_qa_estate_treasury
                var:ac_sect = { NOT = { has_variable = ac_building } NOT = { has_variable = ac_native_construction } }
                var:ac_sect.var:ac_estate_title.title_domicile = { NOT = { has_ongoing_domicile_construction = yes } NOT = { has_variable = ac_native_build_cost } }
            }
            debug_log = "AC_SECT_QA PASS native_UI_cancel_refunds_sect_gold_once"
            set_variable = { name = ac_qa_estate_step value = 2 }
        } else = { debug_log = "AC_SECT_QA FAIL native_UI_cancel_refunds_sect_gold_once" }
    }
} }
ac_sect_qa.0021 = { type = character_event hidden = yes immediate = {
    if = {
        limit = {
            var:ac_sect.var:ac_alchemy_pavilion = 1
            var:ac_sect.var:ac_treasury = ac_qa_estate_after_cost
            var:ac_sect.var:ac_estate_title = { holder = root title_domicile = { has_domicile_building = ac_sect_alchemy_pavilion_01 NOT = { has_ongoing_domicile_construction = yes } } }
        }
        debug_log = "AC_SECT_QA PASS native_UI_project_completes_and_updates_sect"
    } else = { debug_log = "AC_SECT_QA FAIL native_UI_project_completes_and_updates_sect" }
    set_variable = { name = ac_qa_ui_completed value = 1 }
    ac_sect_open_estate_effect = yes
    debug_log = "AC_SECT_QA UI COMPLETE"
} }
''', encoding='utf-8-sig')
        path = OVERLAY / 'common/script_values/ac_sect_qa_estate.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('ac_qa_estate_after_cost = { value = var:ac_qa_estate_treasury subtract = 100 }\n', encoding='utf-8-sig')
        path = OVERLAY / 'common/scripted_guis/ac_sect_qa_estate.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('''ac_sect_qa_audit = {
    scope = character
    is_shown = { has_variable = ac_qa_estate_step NOT = { has_variable = ac_qa_ui_completed } }
    effect = { trigger_event = ac_sect_qa.0020 }
}''', encoding='utf-8-sig')
        path = OVERLAY / 'gui/ac_sect_qa_estate.gui'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('''window = {
    name = "ac_sect_qa_estate" layer = windows_layer
    parentanchor = bottom|hcenter size = { 340 40 } position = { 0 -45 }
    visible = "[GetScriptedGui('ac_sect_qa_audit').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
    button_standard = { size = { 340 40 } text = "ac_sect_qa_audit_button" onclick = "[GetScriptedGui('ac_sect_qa_audit').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }
}''', encoding='utf-8-sig')
        path = OVERLAY / 'gui/scripted_widgets/ac_sect_qa_estate.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('gui/ac_sect_qa_estate.gui = ac_sect_qa_estate\n', encoding='utf-8-sig')
        path = OVERLAY / 'localization/english/ac_sect_qa_estate_l_english.yml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('l_english:\n ac_sect_qa_audit_button:0 "Audit native estate state (test only)"\n', encoding='utf-8-sig')

    if not args.estate_ui:
        for relative in (
            'events/ac_sect_qa_estate.txt', 'common/scripted_guis/ac_sect_qa_estate.txt',
            'common/script_values/ac_sect_qa_estate.txt', 'gui/ac_sect_qa_estate.gui',
            'gui/scripted_widgets/ac_sect_qa_estate.txt', 'localization/english/ac_sect_qa_estate_l_english.yml',
        ):
            (OVERLAY / relative).unlink(missing_ok=True)

    (OUT / 'mod').mkdir(parents=True, exist_ok=True)
    for name, directory in [('ac_sect_test', ROOT / 'AuraClash'), ('ac_sect_qa', OVERLAY)]:
        (OUT / 'mod' / (name + '.mod')).write_text(f'name="{name}"\npath="{directory.as_posix()}"\nsupported_version="1.20.*"\n', encoding='utf-8')
    (OUT / 'dlc_load.json').write_text(json.dumps({'enabled_mods': ['mod/ac_sect_test.mod', 'mod/ac_sect_qa.mod'], 'disabled_dlcs': []}), encoding='utf-8')
    settings = OUT / 'pdx_settings.txt'
    if settings.exists():
        s = settings.read_text(encoding='utf-8-sig')
        s = re.sub(r'("display_mode"=\{\s*version=\d+\s*value=")[^"]+', r'\1windowed', s)
        s = re.sub(r'("windowed_resolution"=\{\s*version=\d+\s*value=")[^"]+', r'\g<1>1920x1080', s)
        s = re.sub(r'("scale"=\{\s*version=\d+\s*value=")[^"]+', r'\g<1>1', s)
        settings.write_text(s, encoding='utf-8')
    print(f'Prepared {OUT}. Launch CK3 with -debug_mode -skip -bookmark=bm_1066_hastings -play=k_england -userdir="{OUT}"')
    print('Read AC_SECT_QA entries in logs/debug.log. COMPLETE and no FAIL are required.')


if __name__ == '__main__':
    main()
