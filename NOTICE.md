# Notice: licensing of files in this repository

This repository contains material under three sets of terms. Use the table below to find which one applies to a file. If a path matches more than one row, the **most specific** row applies.

## License map

| Path | License | Notes |
|---|---|---|
| `AuraClash.mod` | MIT ([LICENSE](LICENSE)) | |
| `AuraClash/descriptor.mod` | MIT ([LICENSE](LICENSE)) | |
| `AuraClash/common/` | MIT ([LICENSE](LICENSE)) | Aura Clash names inside these files are excepted; see below |
| `AuraClash/events/` | MIT ([LICENSE](LICENSE)) | Same exception |
| `AuraClash/events/ac_vanilla_*_options.txt` | © Paradox Interactive; our modifications are MIT | Individual vanilla event definitions with added cultivation choices |
| `tools/` | MIT ([LICENSE](LICENSE)) | Build scripts, option specifications, source hashes and regression checks; Aura Clash names are excepted |
| `AuraClash/gui/window_character_lifestyle.gui` | © Paradox Interactive; our modifications are MIT | See *Files derived from Crusader Kings III* |
| `AuraClash/gui/ac_sect_window.gui`, `AuraClash/gui/scripted_widgets/ac_sect_widgets.txt`, `AuraClash/tests/` | MIT ([LICENSE](LICENSE)) | Original sect interface code and integration scenarios; Aura Clash names are excepted |
| `docs/sects.md` | All rights reserved | Sect mechanics and development documentation |
| `AuraClash/localization/` | Aura Clash Setting Content ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)) | All player-facing text |
| `AuraClash/gfx/` | Aura Clash Setting Content ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)) | All icons and illustrations |
| `assets/trait-icons/` | Aura Clash Setting Content ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)) | Approved trait artwork masters and preview |
| `docs/`, `outputs/aura-clash-events/` | Mixed: underlying CK3 event titles remain © Paradox Interactive; Aura Clash text follows [LICENSE-CONTENT.md](LICENSE-CONTENT.md); our script logic is MIT | Generated event and option registers |
| `README.md`, `NOTICE.md`, `LICENSE`, `LICENSE-CONTENT.md` | All rights reserved | Documentation; may be quoted when crediting this mod |

## Aura Clash names inside code
The MIT license covers the **code**: its structure, logic and mechanics. It does **not** grant rights to Aura Clash Setting Content that appears inside code files. That content includes:
- the setting name **Aura Clash**
- Martial Arts Style names: **Akakiru, Aoyusumu, Kiihakai, Kurokonton, Midorikatai**
- the setting's definitions of its Combat Cores (Soul, Agility, Power, Fortitude), Foundation tiers, Immortal Core and Elements
- any lore text, comments or identifiers built from those names (for example `ac_style_akakiru`)

Inside a mod or submod of this mod, those names may be used and changed under [LICENSE-CONTENT.md](LICENSE-CONTENT.md). To reuse the code anywhere else, remove or replace them.

## Files derived from Crusader Kings III
`AuraClash/gui/window_character_lifestyle.gui` is a modified copy of the vanilla CK3 file of the same name. The original is © Paradox Interactive and is included under Paradox's terms for user-generated content. Only our modifications, each marked with an `# AC:` comment, are offered under the MIT license.

`AuraClash/events/ac_vanilla_*_options.txt` contains selected event definitions derived from CK3 1.20.1. The original event logic remains © Paradox Interactive. Added cultivation choices and their supporting code are MIT, subject to the Aura Clash setting-content exception above. The generated files identify their sources and are rebuilt by `tools/build_event_overrides.py`; they do not replace entire vanilla event files.

The domicile notification fallbacks retain six original CK3 localization strings, © Paradox Interactive, alongside conditional wording for Sect Masters. The mod also references vanilla game assets by path, such as decision illustrations, progress-bar textures and Chinese domicile building sprites/masks. These referenced textures are not included in this repository and remain © Paradox Interactive. The original generated sect-domicile landscape is included under `assets/sect-domicile` with its generation prompt.

## Trademarks and affiliation
"Aura Clash" is a trademark of Aurillian Productions LLC. None of the licenses in this repository grant trademark rights.

Crusader Kings III and Paradox Interactive are trademarks of Paradox Interactive AB. This mod is unofficial and is not affiliated with or endorsed by Paradox Interactive.

## Credit
When redistributing a mod or submod that uses Aura Clash Setting Content, credit:

> Aura Clash setting content by Banished Tales (www.banishedtales.com), © Banished Tales.
