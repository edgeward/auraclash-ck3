"""Native sect domicile definitions; consumed by build_sect_content.render.

Buildings reference installed Chinese domicile sprites without redistributing
Paradox textures. The original landscape lives in assets/sect-domicile.
"""

GOVERNMENTS = (
    'feudal', 'republic', 'theocracy', 'clan', 'tribal', 'mercenary',
    'holy_order', 'monastic_holy_order', 'administrative', 'landless_adventurer',
    'nomad', 'herder', 'celestial', 'japan_administrative', 'japan_feudal',
    'mandala', 'wanua', 'meritocratic', 'steppe_admin', 'ecclesiastical',
)

# Sprite names refer to game/gfx/interface/window_domiciles.
SPRITES = {
    'cultivation_hall': ('manor', 'estate', 'grand_estate'),
    'alchemy_pavilion': ('herb_hall',) * 3,
    'training_ground': ('barracks',) * 3,
    'scripture_library': ('mansion',) * 3,
    'spirit_garden': ('garden',) * 3,
    'formation_hall': ('ancestral_shrine',) * 3,
}


def render(buildings):
    files = {}
    files['common/defines/ac_sect_domicile_defines.txt'] = (
        '# CK3 1.20.1.1: preserve every native government modifier registration.\n'
        'NGovernment = { GOVERNMENT_TYPES = {\n'
        + '\n'.join(f'"{g}_government"' for g in GOVERNMENTS)
        + '\n"ac_sect_government"\n} }\n'
    )
    files['common/governments/ac_sect_government.txt'] = '''
# Only the landless sect office uses this government. Landed Masters retain
# their existing government; the title is created on a landless steward.
ac_sect_government = {
    government_rules = {
        landless_playable = yes
        inherit_from_dynastic_government = no
        rulers_should_have_dynasty = no
        create_cadet_branches = no
    }
    domicile_type = ac_sect_estate
    primary_holding = castle_holding
    mechanic_type = feudal
    can_get_government = { has_trait = ac_sect_master is_landed = no }
    color = { 60 110 85 }
    flags = { government_is_settled government_uses_domicile_but_not_adventurer }
}
'''
    files['common/flavorization/ac_sect_domicile_flavor.txt'] = """domicile_ac_sect_estate = {
        type = domicile domicile_type = ac_sect_estate priority = 100
        flavourization_rules = { top_liege = no }
    }
    ac_sect_master_holder = {
        type = character special = holder tier = county priority = 500
        governments = { ac_sect_government }
        flavourization_rules = { top_liege = no spouse_takes_title = no }
    }"""
    files['common/laws/ac_sect_office_laws.txt'] = """ac_sect_office_succession_law = {
        law_group_type = succession_order_laws
        index = 1000
        can_realm_have = { has_government = ac_sect_government }
        can_keep = { always = yes }
        can_have = { always = yes }
        should_start_with = { has_government = ac_sect_government }
        potential = { has_government = ac_sect_government }
        succession = {
            order_of_succession = generate
            pool_character_config = ac_sect_office_pool
            gender_law = equal
            resign_outside_realm = no
        }
    }"""
    files['common/pool_character_selectors/ac_sect_office_pool.txt'] = """ac_sect_office_pool = {
        # Native fallback only. The society's owner-death handler selects from
        # the entire membership, including landed disciples outside the court.
        valid_character = {
            ac_sect_member_trigger = yes
            ac_sect_available_trigger = yes
            trigger_if = { limit = { exists = scope:base.var:ac_sect } var:ac_sect = scope:base.var:ac_sect }
            trigger_else = { always = no }
        }
        character_score = {
            base = 1
            compare_modifier = { value = ac_sect_successor_score }
            modifier = { add = 1000000 has_trait = ac_sect_upper_disciple }
        }
        config = { background = commander age = { 25 60 } }
        court = yes
        gender = random
        selection_count = 1
    }"""
    # Positions match the six clear plots of the generated landscape.
    slots = [
        ('main_slot', 'main', '37% 1%', '27% 40%'),
        ('alchemy_plot', 'external', '12% 15%', '24% 36%'),
        ('library_plot', 'external', '61% 10%', '24% 36%'),
        ('training_plot', 'external', '17% 39%', '24% 36%'),
        ('formation_plot', 'external', '51% 35%', '24% 36%'),
        ('garden_plot', 'external', '31% 61%', '24% 32%'),
    ]
    domicile = ['''ac_sect_estate = {
    # Title transfer/death processing can briefly run before the rank trait
    # changes. Access is controlled by the sect title, not a house-head check.
    allowed_for_character = { always = yes }
    illustration = "gfx/interface/illustrations/event_scenes/tgp_asia_estate.dds"
    icon = "gfx/interface/icons/flat_icons/domicile_japan.dds"
    map_pin_texture = "gfx/interface/icons/map_icons/map_icon_japanese_manor.dds"
    map_pin_anchor = up
    map_pin_lobby = no
    can_move_manually = no
    move_with_realm_capital = no
    provisions = no
    travel = no
    base_external_slots = 5
    construction_soundeffect = "event:/SFX/UI/Unique/Construction/Building/sfx_ui_unique_construction_building_generic"
    domicile_building_slots = {''']
    for name, kind, position, size in slots:
        domicile.append(f'''{name} = {{
            slot_type = {kind}
            position = {{ {position} }} size = {{ {size} }}
            empty_slot_asset = {{
                icon = "gfx/interface/icons/flat_icons/plus.dds"
                texture = "gfx/interface/window_domiciles/yurt_empty_slot_01.dds"
                intersectionmask_texture = "gfx/interface/window_domiciles/yurt_empty_slot_01_mask.png"
            }}
            construction_slot_asset = {{
                icon = "gfx/interface/icons/flat_icons/plus.dds"
                texture = "gfx/interface/window_domiciles/estate_building_construction_chinese.dds"
                intersectionmask_texture = "gfx/interface/window_domiciles/estate_building_construction_chinese_mask.png"
            }}
        }}''')
    domicile += ['''}
    domicile_asset = {
        background = "gfx/interface/window_domiciles/ac_sect_landscape.dds"
        ambience = "event:/DLC/EP3/SFX/Ambience/2D/Domicile/ep3_amb_2d_domicile_green_lands"
    }
}''']
    files['common/domiciles/types/ac_sect_estate.txt'] = '\n'.join(domicile)
    native, sync, refresh, builders = [], [], [], []
    loc = {
        'ac_sect_government': 'Sect Leadership',
        'ac_sect_master_holder': 'Sect Master',
        'ac_sect_government_adjective': 'Sect',
        'ac_sect_government_realm': 'Cultivation Sect',
        'ac_sect_government_desc': 'A landless cultivation office whose title carries the sect domicile. A landed Master retains their secular government.',
        'ac_sect_estate_domicile_type': 'Sect Estate',
        'ac_sect_estate_domicile_type_possessive': "Sect Estate's",
        'ac_sect_estate_domicile_type_tooltip': 'The permanent headquarters of a cultivation sect. Its buildings and construction pass with the Sect Master title.',
        'ac_sect_native_title_name': "[ac_domicile_kingdom.GetNameNoTier] Sect",
        'ac_sect_native_title_adj': 'Sect',
        'domicile_ac_sect_estate': "[CHARACTER.MakeScope.Var('ac_sect').Story.MakeScope.Var('ac_kingdom').Title.GetNameNoTier] Sect Estate",
        'ac_sect_native_master_required_tt': 'Only this sect\'s Master can commission construction.',
        'ac_sect_native_no_legacy_queue_tt': 'No other sect building is under construction.',
        'ac_sect_open_native_estate': 'Open the sect domicile.',
        'ac_sect_office_succession_law': 'Sect Succession',
        'ac_sect_office_succession_law_desc': 'The sect appoints its most qualified available Upper Disciple, then a Lower Disciple. The office and domicile pass together, independently of secular succession.',
        'ac_sect_estate.0002.t': 'Sect Office Continuity',
    }
    for key, name, description, benefit in buildings:
        refresh.append(f'var:ac_estate_title.title_domicile = {{')
        for level in (3, 2, 1):
            refresh.append(f"{'if' if level == 3 else 'else_if'} = {{ limit = {{ has_domicile_building_or_higher = ac_sect_{key}_{level:02} }} var:ac_domicile_sect = {{ set_variable = {{ name = ac_{key} value = {level} }} }} }}")
        refresh.append(f'else = {{ var:ac_domicile_sect = {{ set_variable = {{ name = ac_{key} value = 0 }} }} }} }}')
        sync.append(f'''if = {{
            limit = {{ var:ac_estate_title = {{ exists = title_domicile }} }}
            var:ac_estate_title.title_domicile = {{''')
        for level in (3, 2, 1):
            sync.append(f'''{'if' if level == 3 else 'else_if'} = {{
                limit = {{ var:ac_domicile_sect.var:ac_{key} = {level} NOT = {{ has_domicile_building_or_higher = ac_sect_{key}_{level:02} }} }}
                add_domicile_building = ac_sect_{key}_{level:02}
            }}''')
        sync += ['}', '}']
        builders.append(f'''ac_sect_build_{key}_effect = {{
            if = {{
                limit = {{
                    ac_sect_master_trigger = yes
                    var:ac_sect = {{ NOT = {{ has_variable = ac_building }} var:ac_{key} < 3 exists = var:ac_estate_title.title_domicile }}
                    var:ac_sect.var:ac_treasury >= ac_sect_{key}_cost
                    var:ac_sect.var:ac_estate_title.title_domicile = {{ NOT = {{ has_ongoing_domicile_construction = yes }} }}
                }}
                var:ac_sect.var:ac_estate_title.title_domicile = {{''')
        for old_level in (0, 1, 2):
            builders.append(f'''{'if' if old_level == 0 else 'else_if'} = {{
                limit = {{ var:ac_domicile_sect.var:ac_{key} = {old_level} }}
                construct_domicile_building = ac_sect_{key}_{old_level + 1:02}
            }}''')
        builders += ['}', '}', '}']
        for level in (1, 2, 3):
            building = f'ac_sect_{key}_{level:02}'
            sprite = SPRITES[key][level - 1]
            loc[building] = name
            loc[building + '_domicile_building'] = name
            loc[building + '_domicile_building_desc'] = f'{description} {benefit} Costs {100 * level} sect gold, paid from the sect treasury. Base construction time: 180 days.'
            funds = building + '_funds_tt'
            loc[funds] = f'The sect treasury has at least {100 * level} gold.'
            native.append(f'''{building} = {{
                slot_type = {'main' if key == 'cultivation_hall' else 'external'}
                allowed_domicile_types = {{ ac_sect_estate }}
                construction_time = 180
                {'previous_building = ac_sect_' + key + '_' + f'{level - 1:02}' if level > 1 else ''}
                can_construct_potential = {{ OR = {{ ac_sect_master_trigger = yes has_variable = ac_native_migration }} }}
                can_construct = {{
                  OR = {{
                    has_variable = ac_native_migration
                    AND = {{
                    custom_tooltip = {{ text = ac_sect_native_master_required_tt ac_sect_master_trigger = yes var:ac_sect.var:ac_estate_title.holder = this }}
                    custom_tooltip = {{ text = {funds} var:ac_sect.var:ac_treasury >= {100 * level} }}
                    custom_tooltip = {{ text = ac_sect_native_no_legacy_queue_tt var:ac_sect = {{ NOT = {{ has_variable = ac_building }} }} }}
                    }}
                  }}
                }}
                # Native costs charge the character's wallet. Sect funds are
                # charged once in on_start instead, including scripted AI builds.
                cost = {{ gold = 0 }}
                refund = {{ gold = 0 }}
                on_start = {{
                  if = {{ limit = {{ scope:owner = {{ NOT = {{ has_variable = ac_native_migration }} }} }}
                    set_variable = {{ name = ac_native_build_cost value = {100 * level} }}
                    var:ac_domicile_sect = {{
                        change_variable = {{ name = ac_treasury subtract = {100 * level} }}
                        set_variable = {{ name = ac_building value = flag:{key} }}
                        set_variable = {{ name = ac_building_timer value = 1 days = 180 }}
                        set_variable = {{ name = ac_native_construction value = 1 }}
                    }}
                  }}
                }}
                on_cancelled = {{
                    if = {{
                        limit = {{ has_variable = ac_native_build_cost }}
                        save_scope_as = ac_cancelled_domicile
                        var:ac_domicile_sect = {{
                            change_variable = {{ name = ac_treasury add = scope:ac_cancelled_domicile.var:ac_native_build_cost }}
                            remove_variable = ac_building
                            remove_variable = ac_building_timer
                            remove_variable = ac_native_construction
                        }}
                        remove_variable = ac_native_build_cost
                    }}
                }}
                on_complete = {{
                    if = {{ limit = {{ has_variable = ac_domicile_sect }} var:ac_domicile_sect = {{
                        set_variable = {{ name = ac_{key} value = {level} }}
                        if = {{
                            limit = {{ has_variable = ac_native_construction }}
                            remove_variable = ac_building
                            remove_variable = ac_building_timer
                            remove_variable = ac_native_construction
                        }}
                    }} }}
                    remove_variable = ac_native_build_cost
                }}
                ai_value = {{ value = 0 }}
                asset = {{
                    icon = "gfx/interface/icons/flat_icons/domicile_japan.dds"
                    texture = "gfx/interface/window_domiciles/estate_building_{sprite}_chinese.dds"
                    intersectionmask_texture = "gfx/interface/window_domiciles/estate_building_{sprite}_chinese_mask.png"
                }}
            }}''')
    files['common/domiciles/buildings/ac_sect_domicile_buildings.txt'] = '\n'.join(native)
    files['common/scripted_effects/ac_sect_native_building_effects.txt'] = (
        '\n'.join(builders) + '\n\n# Story scope; used only when creating/migrating a domicile.\n'
        + 'ac_sect_migrate_building_levels_effect = {\n'
        + 'save_scope_as = ac_domicile_sect\n'
        + 'var:ac_estate_title.title_domicile.owner = { set_variable = { name = ac_native_migration value = 1 } }\n'
        + '\n'.join(sync)
        + '\nvar:ac_estate_title.title_domicile.owner = { remove_variable = ac_native_migration }\n}\n'
        + 'ac_sect_refresh_native_building_levels_effect = { save_scope_as = ac_domicile_sect\n' + '\n'.join(refresh) + '\n}\n'
    )
    import build_sect_domicile_gui
    files.update(build_sect_domicile_gui.render(buildings, SPRITES))
    files['localization/english/ac_sect_domicile_l_english.yml'] = 'l_english:\n' + '\n'.join(
        f' {key}:0 "{value}"' for key, value in loc.items()) + '\n'
    return files
