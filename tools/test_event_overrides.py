"""Regression checks for option preservation, fatal gates and mod references.

These checks inspect CK3 scripts; they do not replace an in-game playtest.
"""
import json
from pathlib import Path
import re
import unittest

import build_event_overrides as builder
from event_option_specs import LOCALIZATION, SPECS
from event_activity_specs import SETUP_CHANGES, OPTION_CHANGES


def normalized(text):
    return re.sub(r'\s+', '', builder.masked(text))


def event_from_file(path, event_id):
    text = path.read_text(encoding='utf-8-sig')
    match = re.search(r'^' + re.escape(event_id) + r'\s*=\s*\{', text, re.M)
    assert match, event_id
    event = text[match.start():builder.close_brace(text, text.index('{', match.start()))]
    return builder.canonical_inline_symbols(event)


class ScriptParserTests(unittest.TestCase):
    def test_braces_in_text_and_comments_are_not_structure(self):
        text = 'test.1 = {\n desc = "A { and escaped \\" bracket" # }\n option = { name = first nested = { value = 1 } }\n\toption = { name = second }\n after = { }\n}'
        self.assertEqual([field.key for field in builder.fields(text)], ['option', 'option', 'after'])

    def test_unbalanced_scripts_are_rejected(self):
        with self.assertRaises(ValueError):
            builder.fields('test.1 = { option = { }')


class EventRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vanilla = {}
        cls.generated = {}
        for event_id, group, options in SPECS:
            cls.vanilla[event_id] = builder.load_event(builder.DEFAULT_GAME, event_id)[0]
            cls.generated[event_id] = event_from_file(builder.ROOT / f'AuraClash/events/ac_vanilla_{group}_options.txt', event_id)

    def test_all_generated_files_are_current(self):
        for path, data in builder.render(builder.DEFAULT_GAME).items():
            self.assertEqual(path.read_bytes(), data, str(path))

    def test_reviewed_events_and_required_resolvers_are_overridden(self):
        self.assertEqual(len(self.generated), 143)
        self.assertEqual(len(self.generated), len(SPECS))
        for text in self.generated.values():
            self.assertEqual(text.count('id_override_priority = 10'), 1)

    def test_vanilla_options_remain_byte_for_byte_unchanged(self):
        for event_id, group, _ in SPECS:
            if group == 'fatal' or event_id in OPTION_CHANGES:
                continue
            before = [self.vanilla[event_id][field.start:field.end] for field in builder.fields(self.vanilla[event_id]) if field.key == 'option']
            after = [self.generated[event_id][field.start:field.end] for field in builder.fields(self.generated[event_id]) if field.key == 'option']
            original_after = [option for option in after if not re.search(r'\bname\s*=\s*ac_event_', builder.masked(option))]
            self.assertEqual(before, original_after, event_id)

    def test_normal_event_setup_and_cleanup_are_unchanged(self):
        for event_id, group, _ in SPECS:
            for key in ('trigger', 'after', 'immediate'):
                if key == 'immediate' and (group == 'fatal' or event_id == 'contest_events.1132' or event_id in SETUP_CHANGES):
                    continue
                before = [self.vanilla[event_id][field.start:field.end] for field in builder.fields(self.vanilla[event_id]) if field.key == key]
                after = [self.generated[event_id][field.start:field.end] for field in builder.fields(self.generated[event_id]) if field.key == key]
                self.assertEqual(before, after, f'{event_id}: {key}')

    def test_cultivation_choices_are_before_normal_choices(self):
        for event_id, group, choices in SPECS:
            if not choices:
                continue  # Outcome-only overrides do not add a choice.
            text = self.generated[event_id]
            first = next(field for field in builder.fields(text) if field.key == 'option')
            self.assertRegex(builder.masked(text[first.start:first.end]), r'\bname\s*=\s*ac_event_')

    def test_bridge_includes_midorikatai_and_other_distinct_paths(self):
        text = self.generated['travel_events.3070']
        for key in ('bridge_mido', 'bridge_akakiru', 'bridge_storm', 'bridge_darkness'):
            self.assertIn('name = ac_event_' + key, text)
        self.assertIn('ABILITY = bridge_mido', text)

    def test_storm_deaths_only_run_in_the_ineligible_branch_before_choice(self):
        text = self.generated['travel_danger_events.6020']
        immediate = builder.one(text, 'immediate').body(text)
        # Wrapping the body lets the same parser inspect its direct children.
        wrapper = 'wrapper = {' + immediate + '}'
        condition = next(field for field in builder.fields(wrapper) if field.key == 'if')
        fallback = next(field for field in builder.fields(wrapper) if field.key == 'else')
        self.assertIn('ABILITY = sea_rescue', wrapper[condition.start:condition.end])
        self.assertNotRegex(builder.masked(wrapper[condition.start:condition.end]), r'\bdeath\s*=')
        original_fatal = self.vanilla['travel_danger_events.6020'].split('# For correct order', 1)[1].split('\n\toption =', 1)[0]
        # The original immediate's final closing brace is outside the copied body.
        original_fatal = original_fatal[:original_fatal.rfind('}')]
        self.assertEqual(normalized(fallback.body(wrapper)), normalized(original_fatal))

    def test_poison_death_and_success_log_stay_in_ineligible_branch(self):
        text = self.generated['host_dinner_events.1091']
        immediate = builder.one(text, 'immediate').body(text)
        wrapper = 'wrapper = {' + immediate + '}'
        condition = next(field for field in builder.fields(wrapper) if field.key == 'if')
        fallback = next(field for field in builder.fields(wrapper) if field.key == 'else')
        self.assertIn('ac_event_poison_survival_trigger', wrapper[condition.start:condition.end])
        self.assertNotIn('i_was_murdered_log', wrapper[condition.start:condition.end])
        self.assertEqual(normalized(fallback.body(wrapper)), normalized(builder.one(self.vanilla['host_dinner_events.1091'], 'immediate').body(self.vanilla['host_dinner_events.1091'])))

    def test_declining_fatal_rescues_still_executes_original_death(self):
        for event_id in ('travel_danger_events.6020', 'host_dinner_events.1091'):
            text = self.generated[event_id]
            options = [text[field.start:field.end] for field in builder.fields(text) if field.key == 'option']
            self.assertNotRegex(builder.masked(options[0]), r'\bdeath\s*=')
            self.assertIn('death = {', options[-1])
            self.assertIn('_rescue_pending', options[-1])

    def test_hunt_rescue_uses_safe_existing_follow_up(self):
        text = self.generated['hunt.4007']
        first = next(field for field in builder.fields(text) if field.key == 'option')
        option = text[first.start:first.end]
        self.assertIn('save_scope_as = rampant_scare', option)
        self.assertNotIn('save_scope_as = rampant_hunter', option)
        self.assertIn('id = hunt.4900', builder.one(text, 'after').body(text))

    def test_healing_never_removes_infection_or_gangrene(self):
        for event_id in ('health.4000', 'health.4001', 'health.4002'):
            text = self.generated[event_id]
            field = next(field for field in builder.fields(text) if field.key == 'option')
            option = text[field.start:field.end]
            self.assertIn('ac_heal_one_wound_effect = yes', option)
            self.assertNotIn('remove_character_modifier', option)
            self.assertIn('ac_event_chi_healing_cooldown_effect', option)

    def test_healing_interaction_and_events_share_cooldown(self):
        trigger = (builder.ROOT / 'AuraClash/common/scripted_triggers/ac_event_triggers.txt').read_text()
        interaction = (builder.ROOT / 'AuraClash/common/character_interactions/ac_cultivation_interactions.txt').read_text(encoding='utf-8-sig')
        self.assertIn('NOT = { has_character_flag = ac_chi_healing_cooldown }', trigger)
        self.assertIn('NOT = { has_character_flag = ac_chi_healing_cooldown }', interaction)
        self.assertIn('ac_event_chi_healing_cooldown_effect = yes', interaction)

    def test_all_custom_references_and_dynamic_abilities_exist(self):
        common = '\n'.join(path.read_text(encoding='utf-8-sig') for path in (builder.ROOT / 'AuraClash/common').rglob('*.txt'))
        definitions = set(re.findall(r'^(ac_\w+)\s*=\s*\{', common, re.M))
        text = common + '\n' + '\n'.join(self.generated.values())
        for ability in re.findall(r'\bABILITY\s*=\s*(\w+)', text):
            self.assertIn('ac_event_' + ability + '_trigger', definitions)
        for reference in re.findall(r'\b(ac_\w+_(?:trigger|effect))\s*=', text):
            self.assertIn(reference, definitions)
        for reference in re.findall(r'\bhas_(?:perk|trait)\s*=\s*(ac_\w+)', text):
            self.assertIn(reference, definitions)

    def test_generated_localization_has_bom_and_all_option_labels(self):
        path = builder.ROOT / 'AuraClash/localization/english/ac_event_options_l_english.yml'
        self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'))
        loc = path.read_text(encoding='utf-8-sig')
        keys = re.findall(r'^\s+(\w+):0', loc, re.M)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(set(keys), set(LOCALIZATION))
        for text in self.generated.values():
            for reference in re.findall(r'\b(?:name|custom_tooltip|desc|title|flavor)\s*=\s*(ac_event_\w+)', text):
                if reference in {'ac_event_sea_rescue_pending', 'ac_event_poison_rescue_pending', 'ac_event_contest_resolved'}:
                    continue  # Names of saved scope values, not localization keys.
                self.assertIn(reference, keys)

    def test_added_event_references_are_live_installed_definitions(self):
        live = builder.event_sources(builder.DEFAULT_GAME)
        for event_id, group, choices in SPECS:
            for reference in re.findall(r'(?:trigger_event\s*=|\bid\s*=)\s*(\w+\.\d+)', choices):
                self.assertIn(reference, live, f'{event_id}: {reference}')

    def test_all_new_modifiers_have_names_and_descriptions(self):
        path = builder.ROOT / 'AuraClash/common/modifiers/ac_event_expansion_modifiers.txt'
        for key in re.findall(r'^(ac_\w+)\s*=\s*\{', path.read_text(encoding='utf-8-sig'), re.M):
            self.assertIn(key, LOCALIZATION)
            self.assertIn(key + '_desc', LOCALIZATION)

    def test_captive_choices_do_not_use_the_free_character_gate(self):
        text = (builder.ROOT / 'AuraClash/common/scripted_triggers/ac_event_expansion_triggers.txt').read_text()
        captive = text[text.index('ac_event_captive_trigger ='):]
        self.assertIn('is_imprisoned = yes', captive)
        self.assertNotIn('ac_event_practitioner_trigger = yes', captive)
        self.assertIn('escape_from_prison_effect = yes', self.generated['prison.9501'])
        self.assertIn('prison.9499', self.generated['prison.9501'])

    def test_frostbite_treatment_updates_native_severity_before_cleanup(self):
        options = next(choices for event, _, choices in SPECS if event == 'travel_danger_events.1011')
        self.assertIn('name = frostbite_severity subtract = 6', options)
        self.assertIn('change_frostbite_modifier_with_severity_effect', options)
        for permanent in ('maimed', 'one_legged', 'disfigured'):
            self.assertNotIn('remove_trait = ' + permanent, options)

    def test_tournament_intervention_guards_the_delayed_lethal_roll(self):
        vanilla = self.vanilla['contest_events.1132']
        generated = self.generated['contest_events.1132']
        wrapper = 'wrapper = {' + builder.one(generated, 'immediate').body(generated) + '}'
        first = next(f for f in builder.fields(wrapper) if f.key == 'hidden_effect')
        branches = 'wrapper = {' + first.body(wrapper) + '}'
        fallback = builder.one(branches, 'else').body(branches)
        vanilla_wrap = 'wrapper = {' + builder.one(vanilla, 'immediate').body(vanilla) + '}'
        original = builder.one(vanilla_wrap, 'hidden_effect').body(vanilla_wrap)
        self.assertEqual(normalized(fallback), normalized(original))
        # Both injury and explicit death live under the same negative guard.
        start = generated.index('\t\tscope:agency_loser = {')
        opening = generated.index('{', start)
        loser = generated[opening:builder.close_brace(generated, opening)]
        guard = builder.one('wrapper = ' + loser, 'if')
        guarded = guard.body('wrapper = ' + loser)
        self.assertIn('NOT = { exists = scope:ac_event_contest_resolved }', guarded)
        self.assertIn('increase_wounds_effect', guarded)
        self.assertIn('death = {', guarded)
        self.assertIn('trigger_event = contest_events.1133', loser[guard.end - len('wrapper = '):])

    def test_archery_scores_directly_without_arming_a_second_roll(self):
        options = next(choices for event, _, choices in SPECS if event == 'contest_events.0710')
        self.assertIn('SCORE = increase_major', options)
        self.assertIn('success_pivotal_flag', options)
        self.assertNotIn('add_character_flag = prowess_', options)

    def test_named_mending_uses_shared_healing_cooldown(self):
        for event in ('health.4000', 'health.4001', 'health.4002'):
            options = next(choices for eid, _, choices in SPECS if eid == event)
            self.assertIn('name = ac_event_kiihakai_mend_wounds', options)
            self.assertIn('ac_event_kiihakai_mending_trigger = yes', options)
            self.assertIn('ac_event_chi_healing_cooldown_effect = yes', options)

    def test_meditation_relieves_stress_without_adding_exertion(self):
        choices = next(choices for event, _, choices in SPECS if event == 'stress_threshold.2311')
        self.assertIn('add_stress = -40', choices)
        self.assertIn('ac_event_meditation_cooldown years = 3', choices)
        self.assertNotIn('ac_event_exertion_effect', choices)

    def test_poison_response_receives_its_sender_and_cremation_checks_faith(self):
        gift = next(choices for event, _, choices in SPECS if event == 'intrigue_scheme_ongoing.5005')
        self.assertLess(gift.index('save_scope_as = owner'), gift.index('trigger_event = intrigue_scheme_ongoing.5006'))
        burials = next(choices for event, _, choices in SPECS if event == 'epidemic_events.1110')
        self.assertIn('faith = { has_doctrine = doctrine_funeral_cremation }', burials)

    def test_precognition_is_a_real_defense_in_both_attack_events(self):
        for event in ('hunt.4010', 'contest_events.1131'):
            choices = next(choices for eid, _, choices in SPECS if eid == event)
            self.assertIn('ac_event_precognition_trigger = yes', choices)
        follow_up = self.generated['contest_events.1132']
        for who in ('contest_opponent_a', 'contest_opponent_b'):
            self.assertIn('scope:' + who + ' = { remove_character_flag = ac_event_contest_safe }', follow_up)

    def test_travel_helpers_cannot_be_recruited_remotely(self):
        text = (builder.ROOT / 'AuraClash/common/scripted_triggers/ac_event_triggers.txt').read_text()
        self.assertIn('any_entourage_character', text)
        self.assertNotIn('any_courtier', text)
        self.assertNotIn('any_living_character', text)

    def test_activity_batch_has_all_approved_contest_and_social_events(self):
        expected = {
            'board_games.0001', 'contest_events.0863', 'contest_events.5520', 'contest_events.5530',
            'contest_events.0610', 'contest_events.0860', 'contest_events.0861', 'contest_events.0862',
            'contest_events.0711', 'contest_events.0510', 'contest_events.3010',
            'contest_events.5000', 'contest_events.5020', 'contest_events.5030',
            'jason_first_race_event.1', 'hunt.8050', 'hunt.8580',
            'hunt_events_anna.0010', 'hunt_events_anna.0015', 'tournament_events.1410',
            'pilgrimage.1100', 'pilgrimage.2008', 'pilgrimage.3201', 'pilgrimage.6532',
            'feast_default.6351', 'feast_default.8004', 'tour_grounds_events.3003', 'funeral.1060',
        } | {'ep2_tournament_events.' + suffix for suffix in (
            '0010', '0011', '1003', '1007', '1017', '2001', '2501', '2502', '2506',
            '4001', '4003', '4004', '4008', '4500', '5501', '5503', '5504')}
        actual = {eid for eid, group, _ in SPECS if group == 'activities'}
        self.assertEqual(actual, expected)

    def test_ordinary_duels_and_tour_sparring_are_excluded(self):
        for eid in self.generated:
            self.assertFalse(eid.startswith('single_combat.'))
        self.assertNotIn('tour_grounds_events.6300', self.generated)
        common = (builder.ROOT / 'AuraClash/common/scripted_effects/ac_activity_effects.txt').read_text()
        self.assertNotIn('trigger_event', common)
        self.assertNotIn('single_combat.', common)

    def test_main_contest_techniques_do_not_arm_the_delayed_vanilla_roll(self):
        for eid in ('contest_events.0610', 'contest_events.0711', 'contest_events.0510'):
            choices = next(c for e, _, c in SPECS if e == eid)
            self.assertIn('ac_activity_contest_technique_effect', choices)
            self.assertNotRegex(choices, r'add_character_flag\s*=\s*\w+_pivotal_duel')
        effect = (builder.ROOT / 'AuraClash/common/scripted_effects/ac_activity_effects.txt').read_text()
        self.assertIn('SCORE = increase_$GAIN$', effect)
        self.assertIn('SCORE = decrease_minor', effect)
        self.assertIn('success_pivotal_flag', effect)
        self.assertIn('failure_pivotal_flag', effect)
        self.assertNotRegex(builder.masked(effect), r'\b(?:death|set_winner|tournament_contest_knocked_out_effect)\s*=')

    def test_jockey_techniques_use_the_rider_and_preparation_preserves_selection(self):
        choices = next(c for e, _, c in SPECS if e == 'contest_events.0510')
        for field in builder.fields('wrapper = {\n' + choices + '\n}'):
            body = field.body('wrapper = {\n' + choices + '\n}')
            self.assertIn('scope:jockey = { ac_', body)
            self.assertIn('location = root.location', body)
            self.assertIn('PRACTITIONER = scope:jockey', body)
            self.assertIn('scope:jockey = { save_scope_as = ac_event_practitioner }', body)
            self.assertIn('scope:ac_event_practitioner = { ac_event_exertion_effect', body)
        prepared = next(c for e, _, c in SPECS if e == 'ep2_tournament_events.4500')
        wrapper = 'wrapper = {' + prepared + '}'
        for field in builder.fields(wrapper):
            body = field.body(wrapper)
            self.assertIn('tournament_choose_jockey_effect = yes', body)
            self.assertIn('location = root.location', body)
        self.assertEqual(len(builder.fields(wrapper)), 9)

    def test_pit_protection_precedes_injury_and_declining_keeps_native_cost(self):
        eid = 'hunt_events_anna.0010'
        text = self.generated[eid]
        wrapper = 'wrapper = {' + builder.one(text, 'immediate').body(text) + '}'
        fallback = builder.one(wrapper, 'else').body(wrapper)
        injury = builder.one(self.vanilla[eid], 'immediate').body(self.vanilla[eid])
        self.assertEqual(normalized(fallback), normalized(injury))
        for field in [f for f in builder.fields(text) if f.key == 'option']:
            body = field.body(text)
            if 'name = ac_event_' in body:
                self.assertNotIn('increase_wounds', body)
                continue
            # Remove only the guarded original landing injury, then require the
            # entire original option to be preserved.
            wrapped = 'wrapper = {' + body + '}'
            guard = next(f for f in builder.fields(wrapped) if f.key == 'if')
            self.assertIn('exists = scope:ac_activity_pit_pending', guard.body(wrapped))
            self.assertIn(normalized(injury), normalized(guard.body(wrapped)))
            remaining = wrapped[:guard.start] + wrapped[guard.end:]
            old_options = [f.body(self.vanilla[eid]) for f in builder.fields(self.vanilla[eid]) if f.key == 'option']
            self.assertIn(normalized(remaining[len('wrapper = {'):-1]), [normalized(b) for b in old_options])
            if 'duel = {' in body:
                self.assertLess(body.index('ac_activity_pit_pending'), body.index('duel = {'))

    def test_wrestling_escape_avoids_both_fatal_and_permanent_native_outcomes(self):
        eid = 'ep2_tournament_events.2506'
        choices = next(c for e, _, c in SPECS if e == eid)
        self.assertIn('ac_activity_mido_body_trigger = yes', choices)
        self.assertNotRegex(builder.masked(choices), r'\b(?:death|add_trait|remove_variable)\s*=')
        self.assertIn('ac_event_activity_wrestle_desc', self.generated[eid])
        self.assertIn('death_reason = death_tournament_roundhouse', self.generated[eid])
        self.assertIn('add_trait = disfigured', self.generated[eid])

    def test_board_foresight_uses_a_supported_move_and_native_resolution(self):
        text = self.generated['board_games.0001']
        choices = next(c for e, _, c in SPECS if e == 'board_games.0001')
        for skill in ('diplomacy', 'martial', 'stewardship', 'intrigue', 'learning', 'prowess'):
            self.assertIn('scope:bg_skill_a = flag:' + skill, choices)
            self.assertIn('name = bg_defender_move value = flag:' + skill, choices)
            self.assertIn('name = bg_attacker_move value = flag:' + skill, choices)
        self.assertNotIn('bg_current_score', choices)
        self.assertNotIn('bg_victor', choices)
        self.assertIn('scope:bg_opponent = { ac_event_precognition_trigger = yes }', choices)
        self.assertIn('flag = ac_activity_board_foresight days = 1', choices)
        self.assertEqual(builder.one(text, 'after').body(text), builder.one(self.vanilla['board_games.0001'], 'after').body(self.vanilla['board_games.0001']))

    def test_murder_feast_escape_retains_all_native_nonplayer_fates(self):
        from event_activity_specs import native_block
        eid = 'feast_default.8004'
        original = builder.one(self.vanilla[eid], 'option').body(self.vanilla[eid])
        duel = native_block(original, 'duel')
        tail = original[original.index(duel) + len(duel):]
        choices = next(c for e, _, c in SPECS if e == eid)
        wrapper = 'wrapper = {' + choices + '}'
        for field in builder.fields(wrapper):
            body = field.body(wrapper)
            self.assertIn(normalized(tail), normalized(body))
            for marker in ('murder_feast_murder_failure_var', 'murder_feast_murder_failure_me_var',
                           'murder_feast_goh_survivor', 'murder_feast_entourage_survivor', 'bloody_murder_fail'):
                self.assertIn(marker, body)
            # The choice retains the companions' outcomes, but never sends the
            # player down the original random success/death roll.
            self.assertNotIn('duel = {', body)
            self.assertNotIn('death_reason = death_murder_feast', body)

    def test_brawl_repair_records_one_damage_roll_and_restores_only_that_amount(self):
        eid = 'feast_default.6351'
        before = builder.one(self.vanilla[eid], 'immediate').body(self.vanilla[eid])
        after = builder.one(self.generated[eid], 'immediate').body(self.generated[eid])
        self.assertEqual(after.count('integer_range'), before.count('integer_range'))
        self.assertIn('name = ac_activity_brawl_damage', after)
        self.assertIn('add_durability = { value = scope:ac_activity_brawl_damage multiply = -1 }', after)
        choices = next(c for e, _, c in SPECS if e == eid)
        self.assertIn('add_durability = scope:ac_activity_brawl_damage', choices)
        self.assertNotIn('subtract = artifact_durability', choices)

    def test_activity_healing_uses_cooldown_and_child_training_is_not_cultivation(self):
        choices = next(c for e, _, c in SPECS if e == 'contest_events.3010')
        self.assertIn('scope:jockey = { ac_heal_one_wound_effect = yes }', choices)
        self.assertIn('ac_event_chi_healing_cooldown_effect = yes', choices)
        self.assertIn('location = root.location', choices)
        child = next(c for e, _, c in SPECS if e == 'hunt_events_anna.0015')
        wrapper = 'wrapper = {' + child + '}'
        opening = child.index('scope:child_with_bow = {', child.index('save_scope_as'))
        effect = child[opening:builder.close_brace(child, child.index('{', opening))]
        self.assertIn('trait = lifestyle_hunter', effect)
        self.assertNotIn('ac_cultivation', effect)
        self.assertNotIn('ac_cultivator', effect)

    def test_dlc_batch_covers_42_events(self):
        self.assertEqual(sum(group == 'dlc' for _, group, _ in SPECS), 42)

    def test_examinations_restore_prior_preparation_after_native_attempt(self):
        for eid in ('imperial_examination.5000', 'imperial_examination.5100',
                    'imperial_examination.5160', 'imperial_examination.5170'):
            choices = next(c for e, _, c in SPECS if e == eid)
            self.assertIn('name = ac_dlc_prior_exam_advantage value = var:has_exam_advantage', choices)
            self.assertIn('imperial_examination_exam_duel_effect = { EXAM = ', choices)
            self.assertIn('name = has_exam_advantage value = scope:ac_dlc_prior_exam_advantage', choices)
            self.assertIn('else = { remove_variable = has_exam_advantage }', choices)
            self.assertNotIn('activity_tournament_change_contestant_score_effect', choices)

    def test_greek_fire_keeps_native_resolver_but_excludes_catastrophic_flag(self):
        choices = next(c for e, _, c in SPECS if e == 'ep3_emperor_yearly.3011')
        self.assertIn('scope:city_defender = root location = root.capital_province', choices)
        self.assertIn('flag = used_fire_dromons days = 30', choices)
        self.assertIn('trigger_event = ep3_emperor_yearly.3012', choices)
        self.assertNotIn('add_character_flag = crit_failed_greek_fire_attack', choices)
        self.assertIn('add_character_flag = failed_greek_fire_attack', choices)
        self.assertIn('compare_modifier', choices)

    def test_palace_essay_initializes_the_native_advantage_multiplier(self):
        choices = next(c for e, _, c in SPECS if e == 'imperial_examination.5300')
        wrapper = 'wrapper = {' + choices + '}'
        for field in builder.fields(wrapper):
            body = field.body(wrapper)
            self.assertLess(body.index('imperial_examination_set_up_exam_advantage_scope = yes'),
                            body.index('factor = scope:exam_advantage_mult'))

    def test_prisoner_rescue_uses_noncombat_contract_resolution(self):
        choices = next(c for e, _, c in SPECS if e == 'ep3_contract_event.0570')
        self.assertIn('add_character_flag = contract_success_flag', choices)
        self.assertIn('id = ep3_contract_event.0575 days = 1', choices)
        self.assertNotIn('single_combat', choices)
        self.assertNotRegex(builder.masked(choices), r'\bdeath\s*=')

    def test_watermill_is_paid_and_building_creation_is_only_a_tooltip(self):
        choices = next(c for e, _, c in SPECS if e == 'ep3_laamp_decision_event.1133')
        self.assertIn('gold >= 160', choices)
        self.assertIn('remove_short_term_gold = 160', choices)
        self.assertIn('add_character_flag = laamp_city_builder_mill_upgrade', choices)
        self.assertEqual(choices.count('add_building = watermills_03'),
                         choices.count('show_as_tooltip = { scope:city_location = { add_building = watermills_03 } }'))

    def test_chariot_rescue_helps_actual_drivers_with_nonfatal_wounds(self):
        choices = next(c for e, _, c in SPECS if e == 'chariot_race.3040')
        self.assertIn('scope:charioteer_1 = {', choices)
        self.assertIn('scope:charioteer_2 = {', choices)
        self.assertIn('increase_wounds_no_death_effect', choices)
        self.assertEqual(choices.count('ac_heal_one_wound_effect = yes'), 1)
        self.assertIn('ac_event_chi_healing_cooldown_effect = yes', choices)
        self.assertNotIn('remove_trait = incapable', choices)

    def test_herd_treatment_does_not_restore_lost_animals_or_heal_character_wounds(self):
        eid = 'mpo_migration_travel_events.0030'
        choices = next(c for e, _, c in SPECS if e == eid)
        self.assertNotIn('ac_heal_one_wound_effect', choices)
        self.assertNotIn('add_herd', choices)
        self.assertNotIn('delay_travel_plan', choices)
        self.assertEqual(builder.one(self.generated[eid], 'immediate').body(self.generated[eid]),
                         builder.one(self.vanilla[eid], 'immediate').body(self.vanilla[eid]))

    def test_harm_choices_prevent_new_incapacity_without_curing_it(self):
        for eid in ('harm.0511', 'harm.0521', 'harm.0561', 'harm.0581', 'harm.0591'):
            choices = next(c for e, _, c in SPECS if e == eid)
            self.assertNotRegex(builder.masked(choices), r'\b(?:remove_trait|add_trait|death)\s*=')
            self.assertIn('ac_event_practitioner', choices)

    def test_direct_plague_barrier_requires_presence_in_reported_county(self):
        choices = next(c for e, _, c in SPECS if e == 'epidemic_events.1064')
        self.assertIn('location.county = scope:witch_trial_county', choices)
        self.assertNotIn('remove_epidemic', choices)

    def test_file_local_constants_follow_relocated_events(self):
        for group in {g for _, g, _ in SPECS}:
            generated = (builder.ROOT / f'AuraClash/events/ac_vanilla_{group}_options.txt').read_text(encoding='utf-8-sig')
            declared = set(re.findall(r'(?m)^(@\w+)\s*=', generated))
            if declared:
                namespace_start = generated.index('namespace =')
                self.assertTrue(all(m.start() < namespace_start for m in re.finditer(r'(?m)^@\w+\s*=', generated)))
            for eid, candidate, _ in SPECS:
                if candidate != group:
                    continue
                _, relative, _ = builder.load_event(builder.DEFAULT_GAME, eid)
                source = (builder.DEFAULT_GAME / relative).read_text(encoding='utf-8-sig')
                source_constants = set(re.findall(r'(?m)^\s*(@\w+)\s*=', source))
                references = set(re.findall(r'@\w+', builder.masked(generated)))
                self.assertTrue(references.intersection(source_constants) <= declared, eid)

    def test_relocated_events_include_their_file_local_helpers(self):
        path = builder.ROOT / 'AuraClash/events/ac_vanilla_activities_options.txt'
        text = builder.canonical_inline_symbols(path.read_text(encoding='utf-8-sig'))
        for name in ('bg_play_move_type_effect', 'pilgrimage_st_elmo_success_effect',
                     'feast_default_6351_fighter_1_trigger', 'feast_default_6351_fighter_2_trigger',
                     'feast_default_6351_gold_amount_based_on_rarity_effect',
                     'jason_first_race_event_1_opponent_trigger'):
            self.assertEqual(len(re.findall(r'^scripted_(?:effect|trigger) ' + name + r'\s*=', text, re.M)), 1)
        # Every referenced inline helper from a source file must be declared in
        # the generated file too, including helpers called by other helpers.
        groups = {group for _, group, _ in SPECS}
        for group in groups:
            actual = (builder.ROOT / f'AuraClash/events/ac_vanilla_{group}_options.txt').read_text(encoding='utf-8-sig')
            actual_names = re.findall(r'^scripted_(?:effect|trigger)\s+(\w+)\s*=', actual, re.M)
            self.assertTrue(all(name.startswith(f'ac_vanilla_{group}_') for name in actual_names))
            generated = builder.canonical_inline_symbols(actual)
            references = set(re.findall(r'\b(\w+)\s*=', builder.masked(generated)))
            declared = set(re.findall(r'^scripted_(?:effect|trigger)\s+(\w+)\s*=', generated, re.M))
            for eid, candidate, _ in SPECS:
                if candidate != group:
                    continue
                _, relative, _ = builder.load_event(builder.DEFAULT_GAME, eid)
                for name, definition in builder.inline_helpers(builder.DEFAULT_GAME, relative).items():
                    if name in references:
                        self.assertIn(name, declared, f'{eid}: {name}')
                        self.assertIn(definition, generated)


if __name__ == '__main__':
    unittest.main()
