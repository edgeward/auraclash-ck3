"""Sect-aware controls for the native title domicile.

The stock domicile editor assumes the owner's government-selected personal
domicile. These controls address the sect title's exact native object instead.
"""


def render(buildings, sprites):
    player = 'GetPlayer.MakeScope'
    society = player + ".Var('ac_sect').Story.MakeScope"
    dom = society + ".Var('ac_estate_domicile').Domicile"
    scope = 'GuiScope.SetRoot(GetPlayer.MakeScope).End'
    shown = lambda key: f"[GetScriptedGui('{key}').IsShown({scope})]"
    execute = lambda key: f"[GetScriptedGui('{key}').Execute({scope})]"
    guis = ['''ac_sect_native_estate_info = {
        scope = character
        is_shown = { ac_sect_member_trigger = yes has_variable = ac_sect_estate_open }
        effect = { remove_variable = ac_sect_estate_open remove_variable = ac_sect_estate_selected }
    }''', '''ac_sect_estate_cancel = { scope = character
        is_shown = { ac_sect_master_trigger = yes }
        is_valid = { ac_sect_master_trigger = yes var:ac_sect.var:ac_estate_domicile = { has_ongoing_domicile_construction = yes } }
        effect = { hidden_effect = { var:ac_sect.var:ac_estate_domicile = { ac_sect_cancel_native_construction_effect = yes } } }
    }''', '''ac_sect_estate_close_panel = { scope = character is_shown = { ac_sect_member_trigger = yes } effect = { remove_variable = ac_sect_estate_selected } }''']
    cancel = []
    loc = {
        'ac_sect_domicile_heading': "[GetPlayer.MakeScope.Var('ac_sect').Var('ac_kingdom').Title.GetNameNoTier] Sect Estate",
        'ac_sect_domicile_budget': "Sect treasury: #P [GetPlayer.MakeScope.Var('ac_sect').Var('ac_treasury').GetValue|0]#! gold",
        'ac_sect_domicile_commission': 'Commission construction',
        'ac_sect_domicile_cancel': 'Cancel project (refund sect gold)',
        'ac_sect_domicile_project': 'Under construction: [GetPlayer.MakeScope.Var(\'ac_sect\').Var(\'ac_estate_domicile\').Domicile.GetBuildingUnderConstruction.GetNameNoTooltip]',
        'ac_sect_domicile_rules': 'Master only. Levels I / II / III cost 100 / 200 / 300 sect gold. One project; 180 base days.',
        'ac_sect_domicile_close': 'Close',
        # Native messages resolve through Character.GetDomicile, which cannot
        # identify a secondary sect estate. Keep ordinary characters' wording
        # and use an accurate generic message for a Master's cancellations.
        'msg_domicile_building_cancelled.title': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_cancelled_title', 'ac_sect_vanilla_cancelled_title' )]",
        'msg_domicile_building_cancelled.desc': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_cancelled_desc', 'ac_sect_vanilla_cancelled_desc' )]",
        'ac_sect_domicile_cancelled_title': 'Domicile Construction Canceled',
        'ac_sect_domicile_cancelled_desc': 'An unfinished domicile building project has been canceled.',
        'ac_sect_vanilla_cancelled_title': '#high [CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetNameNoTooltip]#! Canceled',
        'ac_sect_vanilla_cancelled_desc': '[CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetName] [domicile_building|E] under construction in [CHARACTER.GetDomicile.GetType.GetTitleText( CHARACTER.Self )] has been canceled',
        'msg_domicile_building_started.title': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_started_title', 'ac_sect_vanilla_started_title' )]",
        'msg_domicile_building_started.desc': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_started_desc', 'ac_sect_vanilla_started_desc' )]",
        'ac_sect_domicile_started_title': 'Domicile Construction Started',
        'ac_sect_domicile_started_desc': 'Construction has begun on a domicile building project.',
        'ac_sect_vanilla_started_title': '#high [CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetName]#! Started',
        'ac_sect_vanilla_started_desc': '[CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetName] [domicile_building|E] is under construction in [CHARACTER.GetDomicile.GetType.GetTitleText( CHARACTER.Self )]',
        'msg_domicile_building_completed.title': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_completed_title', 'ac_sect_vanilla_completed_title' )]",
        'msg_domicile_building_completed.desc': "[SelectLocalization( CHARACTER.HasTraitByKey('ac_sect_master'), 'ac_sect_domicile_completed_desc', 'ac_sect_vanilla_completed_desc' )]",
        'ac_sect_domicile_completed_title': 'Domicile Construction Completed',
        'ac_sect_domicile_completed_desc': 'A domicile building project has finished construction.',
        'ac_sect_vanilla_completed_title': '#high [CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetNameNoTooltip]#! Completed',
        'ac_sect_vanilla_completed_desc': 'The [CHARACTER.GetDomicile.GetBuildingUnderConstruction.GetName] [domicile_building|E] has finished constructing in your [CHARACTER.GetDomicile.GetType.GetTitleText( CHARACTER.Self )]',
    }
    plots, panels = [], []
    positions = [('36% 0%', '30% 40%'), ('10% 6%', '27% 32%'),
                 ('59% 8%', '28% 38%'), ('15% 36%', '28% 34%'),
                 ('49% 33%', '28% 38%'), ('36% 61%', '28% 30%')]
    # The original background's plots are deliberately spacious; each chain has
    # a stable painted position independent of the engine's free-slot ordering.
    places = {'cultivation_hall': 0, 'alchemy_pavilion': 1,
              'scripture_library': 2, 'training_ground': 3,
              'formation_hall': 4, 'spirit_garden': 5}
    for key, name, description, benefit in buildings:
        for level in (1, 2, 3):
            cancel.append(f"if = {{ limit = {{ has_domicile_construction = ac_sect_{key}_{level:02} }} remove_domicile_building_no_refund = ac_sect_{key}_{level:02} }}")
        select = f'ac_sect_estate_select_{key}'
        build = f'ac_sect_estate_commission_{key}'
        pending = f'ac_sect_estate_pending_{key}'
        guis += [f'''{select} = {{ scope = character
            is_shown = {{ ac_sect_member_trigger = yes }}
            effect = {{ set_variable = {{ name = ac_sect_estate_selected value = flag:{key} }} }}
        }}''', f'''{select}_panel = {{ scope = character is_shown = {{ ac_sect_member_trigger = yes var:ac_sect_estate_selected ?= flag:{key} }} }}''', f'''{build} = {{ scope = character
            is_shown = {{ ac_sect_master_trigger = yes }}
            is_valid = {{
                ac_sect_master_trigger = yes
                var:ac_sect = {{ NOT = {{ has_variable = ac_building }} var:ac_{key} < 3 }}
                var:ac_sect.var:ac_treasury >= ac_sect_{key}_cost
                var:ac_sect.var:ac_estate_domicile = {{ NOT = {{ has_ongoing_domicile_construction = yes }} }}
            }}
            effect = {{ ac_sect_build_{key}_effect = yes }}
        }}''', f'''{pending} = {{ scope = character
            is_shown = {{ var:ac_sect = {{ has_variable = ac_native_construction var:ac_building ?= flag:{key} }} }}
        }}''']
        pos, size = positions[places[key]]
        label_y = 36 if key == 'formation_hall' else 0
        # Architectural canvases are 812x512; the other native sprites are
        # square. Fit each canvas without stretching its painted footprint.
        slot_width, slot_height = (float(n.rstrip('%')) for n in size.split())
        max_width, max_height = 1206 * slot_width / 100 * .88, 556 * slot_height / 100 * .88
        images = []
        for level in (1, 2, 3):
            sprite = sprites[key][level - 1]
            native_width = 812 if sprite in ('manor', 'estate', 'grand_estate', 'mansion') else 512
            scale = min(max_width / native_width, max_height / 512)
            image_size = f'{round(native_width * scale)} {round(512 * scale)}'
            condition = f"{dom}.HasBuildingOrHigherTier(GetDomicileBuilding('ac_sect_{key}_{level:02}'))"
            if level < 3:
                condition = f"And({condition}, Not({dom}.HasBuildingOrHigherTier(GetDomicileBuilding('ac_sect_{key}_{level + 1:02}'))))"
            images.append(f'''icon = {{ parentanchor = bottom|hcenter position = {{ 0 -6 }} size = {{ {image_size} }} alwaystransparent = yes visible = "[{condition}]"
                texture = "gfx/interface/window_domiciles/estate_building_{sprites[key][level - 1]}_chinese.dds" }}''')
        images.append(f'''icon = {{ parentanchor = bottom|hcenter position = {{ 0 -6 }} size = {{ 88% 88% }} alwaystransparent = yes
            visible = "[Not({dom}.HasBuildingOrHigherTier(GetDomicileBuilding('ac_sect_{key}_01')))]"
            texture = "gfx/interface/window_domiciles/yurt_empty_slot_01.dds" }}''')
        images.append(f'''icon = {{ parentanchor = bottom|hcenter position = {{ 0 -6 }} size = {{ {round(min(max_width, max_height))} {round(min(max_width, max_height))} }} alwaystransparent = yes visible = "{shown(pending)}"
            texture = "gfx/interface/window_domiciles/estate_building_construction_chinese.dds" }}''')
        loc[f'ac_sect_plot_{key}'] = f"{name}  [GetPlayer.MakeScope.Var('ac_sect').Var('ac_{key}').GetValue|0]/3"
        loc[f'ac_sect_panel_{key}'] = f'{description}\\n\\n{benefit}\\n\\n$ac_sect_domicile_rules$'
        plots.append(f'''button = {{ position = {{ {pos} }} size = {{ {size} }}
            allow_outside = yes
            onclick = "{execute(select)}" tooltip = "ac_sect_panel_{key}"
            {chr(10).join(images)}
            widget = {{ parentanchor = top|hcenter position = {{ 0 {label_y} }} size = {{ 310 34 }} alwaystransparent = yes
                icon = {{ size = {{ 100% 100% }} alwaystransparent = yes
                    texture = "gfx/interface/window_domiciles/domicile_header_background.dds" }}
                text_single = {{ parentanchor = center widgetanchor = center size = {{ 286 34 }}
                    autoresize = no align = vcenter|nobaseline|center fontsize = 20 margin_bottom = 0
                    alwaystransparent = yes text = "ac_sect_plot_{key}" default_format = "#light_background" }}
            }}
        }}''')
        panels.append(f'''widget = {{ visible = "{shown(select + '_panel')}" parentanchor = top|right
            position = {{ -50 110 }} size = {{ 410 480 }} using = Window_Background using = Window_Decoration
                text_single = {{ position = {{ 45 15 }} size = {{ 240 40 }} autoresize = no text = "ac_sect_plot_{key}" using = Font_Size_Medium }}
                button_standard = {{ position = {{ 295 15 }} size = {{ 70 35 }} text = "ac_sect_domicile_close" onclick = "{execute('ac_sect_estate_close_panel')}" }}
                text_multi = {{ position = {{ 45 70 }} size = {{ 320 245 }} text = "ac_sect_panel_{key}" }}
                text_single = {{ position = {{ 45 335 }} size = {{ 320 35 }} autoresize = no text = "ac_sect_domicile_budget" }}
                button_standard = {{ position = {{ 45 390 }} size = {{ 320 44 }} text = "ac_sect_domicile_commission"
                    visible = "{shown(build)}"
                    enabled = "[GetScriptedGui('{build}').IsValid({scope})]"
                    onclick = "{execute(build)}" tooltip = "ac_sect_domicile_rules" }}
        }}''')
    window = f'''window = {{
        name = "ac_sect_estate_info" layer = windows_layer parentanchor = center size = {{ 1390 790 }}
        using = Window_Movable
        datacontext = "[GetPlayer]"
        visible = "{shown('ac_sect_native_estate_info')}"
        widget = {{ position = {{ 92 80 }} size = {{ 1206 556 }}
            background = {{ texture = "gfx/interface/window_domiciles/ac_sect_landscape.dds" }}
            {chr(10).join(plots)}
        }}
        icon = {{ position = {{ 58 46 }} size = {{ 1274 624 }} alwaystransparent = yes
            texture = "gfx/interface/window_domiciles/domicile_frame_asia.dds" }}
        widget = {{ parentanchor = top|hcenter position = {{ 0 34 }} size = {{ 500 66 }}
            background = {{ texture = "gfx/interface/window_domiciles/domicile_header_background.dds" }}
            text_single = {{ size = {{ 500 66 }} autoresize = no align = center text = "ac_sect_domicile_heading" default_format = "#light_background" using = Font_Type_Flavor using = Font_Size_Big }}
        }}
        button_standard = {{ parentanchor = top|right position = {{ -70 50 }} size = {{ 100 40 }}
            text = "ac_sect_domicile_close" onclick = "{execute('ac_sect_native_estate_info')}" }}
        widget = {{ position = {{ 92 676 }} size = {{ 1206 90 }} using = Window_Background
            text_single = {{ position = {{ 45 8 }} text = "ac_sect_domicile_budget" }}
            text_single = {{ position = {{ 45 42 }} text = "ac_sect_domicile_rules" }}
        }}
        widget = {{ position = {{ 92 620 }} size = {{ 1206 50 }}
            visible = "[{dom}.IsConstructing]" using = Window_Background
            text_single = {{ position = {{ 20 8 }} text = "ac_sect_domicile_project" }}
            progressbar = {{ position = {{ 20 34 }} size = {{ 660 10 }} value = "[{dom}.GetConstructionProgress]" max = 1
                progresstexture = "gfx/interface/progressbars/progress_grandeur.dds" noprogresstexture = "gfx/interface/progressbars/progress_black.dds" }}
            button_standard = {{ parentanchor = right position = {{ -10 0 }} size = {{ 430 40 }}
                text = "ac_sect_domicile_cancel" enabled = "[GetScriptedGui('ac_sect_estate_cancel').IsValid({scope})]"
                onclick = "{execute('ac_sect_estate_cancel')}" }}
        }}
        {chr(10).join(panels)}
    }}'''
    loc = {k: v.replace(".Var('ac_sect').Var(", ".Var('ac_sect').Story.MakeScope.Var(") for k, v in loc.items()}
    overrides = {k: loc.pop(k) for k in list(loc) if k.startswith('msg_domicile_building_')}
    return {
        'gui/ac_sect_estate_info.gui': window,
        'common/scripted_guis/ac_sect_estate_info.txt': '\n'.join(guis),
        'localization/english/ac_sect_estate_gui_l_english.yml': 'l_english:\n' + '\n'.join(f' {k}:0 "{v}"' for k, v in loc.items()) + '\n',
        'localization/replace/ac_sect_messages_l_english.yml': 'l_english:\n' + '\n'.join(f' {k}:0 "{v}"' for k, v in overrides.items()) + '\n',
        'common/scripted_effects/ac_sect_cancel_native_construction.txt': 'ac_sect_cancel_native_construction_effect = {\n' + '\n'.join(cancel) + '\n}\n',
    }
