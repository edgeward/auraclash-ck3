# Aura Clash — Crusader Kings III Mod

Bring the cultivation system of **Aura Clash**, an eastern-fantasy (xianxia/wuxia) setting, into Crusader Kings III. Awaken as a Cultivator, train your four Combat Cores, temper your Foundation in battle, master a Martial Arts Style and two Elements, and condense an Immortal Core.

**Version:** 0.4.0 · **Event integrations target:** CK3 1.20.1 · **Status:** early and playable; many perks are still placeholders

---

## Installation

### Manual
1. Download or clone this repository.
2. Copy **both** `AuraClash.mod` and the `AuraClash/` folder into your CK3 mod directory:
   - Windows: `Documents\Paradox Interactive\Crusader Kings III\mod\`
   - Linux: `~/.local/share/Paradox Interactive/Crusader Kings III/mod/`
   - macOS: `~/Documents/Paradox Interactive/Crusader Kings III/mod/`
3. Enable **Aura Clash** in your launcher playset.

The final layout should be:
```
mod/
├── AuraClash.mod
└── AuraClash/
    ├── descriptor.mod
    ├── common/ events/ gui/ gfx/ localization/
```

### Compatibility
- **Start a new game** when updating from an earlier version. v0.3 replaces the Foundation trait, and v0.2 renamed the tree and perk keys.
- `AuraClash/gui/window_character_lifestyle.gui` **replaces** the vanilla lifestyle window. It will conflict with other mods that edit that window, including Princes of Darkness and most UI overhauls.
- One vanilla option-display define is changed: unavailable options can remain visible until **6** options are shown (vanilla is 4). This does not cap the number of available choices.
- Cultivation integration overrides **143 individual vanilla events** using `id_override_priority = 10`, targeting CK3 **1.20.1 / 1.20.1.1**: **269 added choices in 141 events**, plus two linked tournament outcome events. Mods changing those same events need a compatibility patch. Original event files are not replaced; normal choices and cleanup are preserved, with guarded resolution for successful cultivation interventions. The generator includes required file-local helpers and constants alongside relocated events. Fully restart CK3 after updating: event priority overrides do not support hot reload.
- Native sect domiciles add a landless Sect Master title and register its government in `NGovernment.GOVERNMENT_TYPES`, retaining all 20 native entries. Mods replacing that list need a merged compatibility definition.
- Six construction-notification localization keys use generic wording for Sect Masters because native messages assume a personal domicile. Other characters keep vanilla wording; mods replacing those same keys need a localization merge.
- Its on_actions (including a hook on hunts) are appended to vanilla's.

---

## Features

### Trait artwork
All 28 cultivation, Foundation, Style and Element traits have replacement painted icons. Akakiru uses a katana with a straight hilt. [Preview and approved PNG masters](assets/trait-icons/README.md) are included; runtime textures retain their original filenames and 120 × 120 DDS format. With Pillow installed, `python tools/build_trait_icons.py --check` verifies all 28 textures against their sources.

### Cultivation choices in vanilla events
Cultivators aged 16+ can use relevant affinities, styles, trained Cores and perks in existing events:
- **Travel:** White Squall, Person Overboard, The Flood, Not a Drop, A Fire in the Night, Snowbound, Avalanche, Familiar Trees, On a Mountain Trail, Bandits on the Bridge, Flawed Fare and Rainstorm.
- **Bridge bandits:** Midorikatai overpowers the leader; Akakiru disarms the bandits; Storm frightens them away; Darkness conceals the crossing.
- **Healing:** three wound-treatment events offer the existing one-tier Chi Healing effect. This shares a six-month cooldown with the character interaction and does not cure infection or gangrene. The healer must be physically present with the patient.
- **Hunts:** a trained Midorikatai or Akakiru cultivator can stop a charging animal; sword techniques, protective wards or Blinding Flash can interrupt an attack on another hunter.
- **Court:** cultivation can support three-year agricultural relief and patrol projects in the petitioning county. These cost money and do not instantly remove famine, epidemics or all unrest.
- **Fatal outcomes:** Dangers of the Deep checks for Water, Wind or Storm cultivation before executing its death effects. A poisoned visitor can intervene using Toxicology, Grandmaster Alchemist, Flame Purge, Purifying Light, an Immortal Core or at least ten Fortitude Core dots. The normal fatal outcome remains available if the rescue is declined; characters without a qualifying ability follow vanilla behavior.
- **More travel:** retrieve a sliding artifact chest; treat frostbite or a snakebite; subdue or frighten a beast; free muddy wagons; rescue plantation workers and a companion trapped in a forest fire. Frostbite treatment updates native severity and modifiers without restoring lost limbs.
- **Disaster relief:** funded food distribution, rubble rescue, medical assistance and nonlethal responses to looting complete existing governor contracts. A ruined farmhouse can be rebuilt with cultivation support. These checks use the actual destination and preserve the contract's rewards and cleanup.
- **Plagues and alchemy:** funded capital defenses, an alchemical medical book, emergency burials or cremation, containment of a diseased siege projectile, and treatment of the child in Healing Hands. These do not erase a county's epidemic. Cremation costs piety when it conflicts with the ruler's faith's funeral doctrine.
- **Tournaments and intrigue:** Wind-Guided Arrows changes archery score; Treasure Refining preserves a chipped weapon; Akakiru, Midorikatai, Kurokonton and Aoyusumu can interrupt a lethal tournament encounter. The delayed wound/death resolver honors these choices. Scrying and Shadow Step improve use of a secret tunnel; trained alchemists can send poisoned gifts without accidentally poisoning their own household.
- **Aoyusumu:** named techniques calm a coronation stampede, perform an Exorcist's Rite, reassure people facing plague or earthquake, and resolve Haunted by the Past through meditation. Precognition averts the hunt attack and the tournament assault, and guides a safe disaster retreat. Meditation has a three-year cooldown and six months of reduced diplomacy/stewardship duties; it does not add exertion stress.
- **Kiihakai:** Barrier of Chi protects the family members present during Selfless Acts; Ward shelters a disaster rallying point; Runic Empowerment repairs a wagon wheel or neglected artifact; Scrying Sphere inspects a secret tunnel. Named Mending Chi options appear in all three wound-treatment events and disaster medical relief, sharing the normal healing cooldown.
- **Prison:** captive cultivators can purify an infected wound or use Wallbreaker, Vanishing Arts or Stone Shaping after a failed escape. Captive-specific triggers permit these techniques while imprisoned. Successful escapes retain vanilla release, memory, opinion and notification effects.
- **Tournament combat:** Akakiru and Midorikatai gain techniques in melee, tournament duels and jousting; Midorikatai also gains grappling stances, pin reversals and a safe escape from the lethal headlock. Skill and Core training affect contest rolls, and cultivating opponents resist more effectively. Techniques change native contest progress rather than declaring a winner. Ordinary one-on-one duels and tour sparring are unchanged.
- **Recitals and races:** Aoyusumu can steady a performance, answer insults and anticipate the audience; Kiihakai can draw on academy training or shelter a recital with a barrier. Race preparation preserves all three jockey candidates. Techniques during the Final Lap require the actual jockey's cultivation, and charge that rider's exertion. Owners can provide coaching, reassurance, wards or treatment when physically present.
- **Board games:** Precognition supplies one strong supported move per day while preserving native counters, stakes and resolution. An opposing practitioner of Precognition reduces its advantage. Tournament board games also gain foresight choices.
- **More activities:** track game with Scrying Sphere or Earthsense, escape a hunting pit before the fall injury, coach a child's ordinary archery, settle tournament fans, aid pilgrims, repair the exact damage from a feast brawl, escape a murder feast, reach precarious prey during a tour, and comfort a fellow mourner. Murder-feast escapes retain the normal survivor bookkeeping and the original fates of other guests and companions.
- **Examinations, debates and festivals:** trained techniques assist native examination attempts and scholarly argument rolls, cleansing rites, strength contests and a guest's wish. Preparation advantages are temporary; native scores, political consequences and final promotion checks remain in control.
- **Adventurers and imperial defenses:** find water for a parched camp, protect a stormbound convoy, repel a night attack, free a contract prisoner without single combat, assist paid watermill construction, and prevent catastrophic friendly fire during an opposed Greek-fire attack. A chariot-crash rescue saves the actual drivers with nonfatal injuries and retains race standings.
- **Herds and commissions:** protect migrating herds at a river or difficult passage, treat surviving livestock after blight, and tend an injured messenger while retaining the message delay. Support an artisan's forge or composure, handle an exotic court animal, and answer riddles with a trained mind.
- **Households, towns and accidents:** comfort a distressed spouse, provide temporary refrigeration or fund icehouse repairs, treat an ordinarily ill wet nurse, rescue residents from a town fire, assist paid wall improvements, obstruct witch trials, save a threatened artifact, and ease religious nightmares. Five physical-harm events gain ways to prevent the new accident's incapacity; existing incapacity is not cured.

The complete sorted register is available as an [Excel workbook](outputs/aura-clash-events/AuraClash-event-tracker.xlsx), an [event table](docs/events.csv), and an [option table](docs/event-options.csv). The workbook has filterable Events and Options tabs. It records event IDs, content families, added choices, ability references, outcomes, exertion and source locations. [The registry JSON](docs/event-registry.json) retains exact eligibility and effect scripts; the ability index is a readable index, not a replacement for AND/OR, presence and cooldown checks. Dynamic title placeholders depend on the save. Content families identify source content rather than asserting that every associated event requires owning a DLC.

Travel techniques can be performed by the ruler or a qualified cultivator in the actual entourage. The practitioner gains 25 Cultivation XP, 15 stress and three months of Spent Chi (-2 prowess, +10% stress gain). An avalanche rescue or fatal-outcome intervention instead grants 100 XP, 40 stress and six months of Overextended Chi (-4 prowess, -0.25 health, +20% stress gain). Poison survivors also recover for six months with a further -0.25 health.

### Cultivation sects

One provincial sect is seeded per eligible de-jure kingdom, with a Master, up to ten Upper Disciples and twenty Lower Disciples. Rulers can join while keeping their titles. Each sect has two elements, a martial style and a foundation, plus a persistent estate that passes to the next master.

Use **Decisions → Cultivation → Consult the Sect Register** for membership, six estate building lines, mission contracts and the contribution exchange. Public **Sect Trial** activities admit mortals and cultivators and examine disciples for promotion. Sects can form alliances and rivalries, fight group battles and host **Joint Sect Training**. See the [sect guide](docs/sects.md) for costs, succession, geography and testing.

The estate is a native CK3 domicile attached to a separate landless Sect Master title, with an original Chinese-inspired landscape and six building chains. It passes with sect leadership while rulers keep their lands, government and personal estate. The sect register opens illustrated building plots and sect-aware controls for the native construction queue; the vanilla editor assumes a ruler's personal domicile. Sect battles resolve as group clashes; they do not use ordinary single combat or conquer territory.

### Cultivator
A trait that grants **+0.5 health, +20 life expectancy, +10 years of fertility and +4 prowess**, and unlocks everything below.
- Children inherit it **25%** of the time.
- Newborns and generated characters get it at random **0.5%** of the time.
- It's available in the ruler designer for 80 points.
- **Awaken Cultivation** (decision): costs 100 prestige, usable once per year. It's a Martial + Learning check with a 5–85% chance. Failure leaves you wounded, but never kills you.
- **AI rulers** only attempt Awaken Cultivation if they are warrior-like or hardworking. That means any of: Ambitious, Brave, Diligent, Martial or Prowess education rank 3+, Strong, Hale, Robust, Herculean, Berserker, Blademaster, Populist Leader, Adventurer, Military Order member, Crusader or Holy Warrior, Warrior of the Faith, Raider, Varangian, or 3+ commander traits.
- **Legendary conquerors:** the fame traits **Conqueror**, **Despoiler of Byzantium** and **Greatest of Khans** grant the Cultivator trait if the character doesn't have it, plus **5 / 10 / 20** randomly distributed Core dots. Characters who are already Cultivators still get the dots, up to the Cores' caps. This happens once per trait.
- Cultivation only advances from **age 16**: Core training, Foundations, Styles, Elements, perks and the lifestyle tab all wait until then.

### Decisions
All Cultivation decisions appear in their own **Cultivation** group in the decisions panel.

### Mortal Core Training
- **Mortal Core Training** (decision → event): costs 100 prestige, once per year. It raises one Combat Core, which raises its linked skill by 1, up to +20 per Core:

| Core | Skill |
|---|---|
| Soul | Learning |
| Agility | Intrigue |
| Power | Martial |
| Fortitude | Stewardship |

- Every dot also has milestone bonuses:
  - dots **5 and 15**: +2 prowess each
  - dots **10 and 20**: +0.25 health and +5 years of life expectancy each
- Core progress shows as track bars on the Cultivator trait tooltip.
- All four options stay visible but greyed out until the yearly cooldown ends.
- **Auto-training:** a toggle in the same event repeats your last choice each year, whenever you can pay. Open the decision again to turn it off.

### Foundations
When a character becomes a Cultivator, or turns 16 as one, they choose **one of twelve zodiac Foundations**. The choice popup has two pages of six. Each Foundation gives +1 to a skill and a minor bonus. Fighting as a **commander or knight** tempers it through the tiers **Mortal → Iron → Jade → Golden → Heavenly**. Each tier strengthens that Foundation's own bonus, and Jade and Heavenly also add +5% knight effectiveness (Wolf gets +1 prowess there instead).

| Foundation | Base | Each tier adds |
|---|---|---|
| Dragon | +1 Diplomacy, +0.5 monthly prestige | +0.25 monthly prestige |
| Rabbit | +1 Diplomacy, +15% fertility | +5% fertility, +2 attraction opinion |
| Tiger | +1 Martial, +3 prowess | +1 prowess |
| Snake | +1 Intrigue, +5 hostile scheme success | +2 hostile scheme success |
| Stallion | +1 Martial, +10% army movement | +5% army movement |
| Ram | +1 Learning, +0.5 monthly piety | +0.25 monthly piety |
| Monkey | +1 Intrigue, +5% lifestyle XP | +2.5% lifestyle XP |
| Crane | +1 Learning, +5 years life expectancy | +2 years life expectancy |
| Wolf | +1 Martial, +10% knight effectiveness | +5% knight effectiveness |
| Boar | +1 Stewardship, +0.25 health | +0.1 health |
| Rat | +1 Stewardship, +0.5 monthly gold | +0.25 monthly gold |
| Ox | +1 Stewardship, −5% building cost | −2.5% building cost |

### Immortal Core
- **Immortal Core Advancement** (decision): costs 150 piety, once per year. It's a Learning + Martial check with a 5–75% chance.
- Each failure adds **+5% Insight** to the next attempt, and high Foundation tiers add more.
- Success grants **+20 life expectancy and +0.5 health**, plus **20 Cultivation lifestyle XP every month**, whatever your current focus.

### Martial Arts Styles and Elements
- **Study a Martial Arts Style** (decision): costs 150 prestige. Choose Akakiru, Aoyusumu, Kiihakai, Kurokonton or Midorikatai. Styles are exclusive.
- **Awaken Elemental Affinity** (decision): costs 100 piety. Attune to up to **two** of Darkness, Earth, Fire, Ice, Light, Storm, Water and Wind. The choice popup has two pages of four.
- **Learning isn't guaranteed.** The chance is **4% per point** of the deciding skill, so 25 is certain. A failure refunds the cost but wounds you.
  - **Styles:** Akakiru = Stewardship, Aoyusumu = Diplomacy, Kiihakai = Learning, Kurokonton = Intrigue, Midorikatai = Martial.
  - **Elements** use the higher of two skills: Darkness = Intrigue or Learning, Earth = Stewardship or Diplomacy, Fire = Martial or Learning, Ice = Stewardship or Martial, Light = Learning or Intrigue, Storm = Learning or Stewardship, Water = Diplomacy or Martial, Wind = Martial or Intrigue.
- Each Style and Element grants +5 prowess and unlocks its own perk tree.
- Attempting a Style **or** an Element starts a shared **1-year cooldown**.

### Preserved Youth (game rule: *Cultivator Aging*, default **Slowed**)
Cultivators stay young-looking much longer, shown by the **Preserved Youth** trait.
- **When it starts:** age 22, or later if they awaken after 22. Nobody's appearance changes before then.
- **How it works:** from that point the portrait ages only **5 visible years** over as many real years as their **longevity bonus**, then ages normally from there.
- **Default** (+20 years): characters who are cultivators by 22 look **22–27 from age 22 to 42**. Every extra year of longevity (Cores, Immortal Core, Crane Foundation, Alchemy) stretches that window.
- **Late awakeners** keep their current age as the starting point. Someone who awakens at 40 looks 40–45 until about 60.
- **Fertility:** cultivators stay fertile longer, because CK3 bases fertility on apparent age while this effect is active.

**The Death Spiral:** at age **60 + their longevity bonus**, or whenever their health drops below 1 for a lasting reason, Preserved Youth ends. Low health from wounds or a passing illness (ill, pneumonia, typhus, plague, smallpox, measles, dysentery, ergotism, lover's pox) or pregnancy doesn't count.

**Still mortal:** CK3's way of keeping a portrait young also stops natural death, so the mod runs its own low-health death check for these characters. A small hidden check runs every 90 days, or every 30 days when health is below 3, only while Preserved Youth is active. It uses the vanilla odds: a monthly death chance of 25% × ((3 − health) / 3)², which is 25% at 0 health. Death is reported with the illness or wound as the cause. A cultivator who dies of measles at 42 still looks young. Their true age catches up at once and they age and die like a mortal. Cultivators whose growing strength (longevity from Cores, Immortal Core, Foundation and perks) outpaces the years can hold this off longer. Set the rule to *Normal* to turn the effect off.

### AI cultivators
Adult AI cultivators run **one short routine per year**, on a random day, through `random_yearly_everyone_pulse`. There are no constant scripts and no per-character timers. Each year, an AI cultivator:
- **Trains a Core** (one picked at random, skipping maxed ones) if it has more than 300 prestige.
- Has a **15% chance** to learn a Style (150 prestige), or else an Element (100 piety). This is subject to the shared yearly cooldown.
- Has a **30% chance** to attempt an Immortal Core, if it has 150 piety and Martial + Learning of at least 16.
- **With an Immortal Core**, banks 240 Cultivation XP. Each time the bank passes 1,000, it unlocks its next perk in this order: Style, then Elements, then Alchemy, then Handseals.

Non-cultivators only cost a single trait check, so the load is negligible.

### Train in Cultivation
A character interaction (right-click a character). It needs a Cultivator aged 16+ as the trainer and a target who isn't a Cultivator.
- **Who you can train:** your **courtiers**, your **vassals**, or your **children within diplomatic range**. Anyone else shows the option greyed out.
- **Cost:** 250 piety and 250 prestige. Each person can be trained at most once per year.
- **Success chance:** 1% per point of the target's Martial and Learning, plus 1% per Combat Core dot you've unlocked (up to 100%).
- **Failure** wounds the target.
- The AI does not use this interaction.

### Perk-unlocked interactions (right-click a character)
- **Chi Healing:** unlocked by *Water: Healing Waters*, *Kiihakai: Mending Chi* or *Aoyusumu Mastery*. It mends one level of wounds on anyone, including yourself, with a 6-month cooldown.
- **Scry:** unlocked by *Kiihakai: Scrying Sphere*. Costs 100 piety, with a 3-year cooldown. The success chance is your Learning + Intrigue as a percentage. On success, all of the target's secrets are revealed to you.
- **Hex:** unlocked by *Kurokonton: Hex*. Costs 100 prestige. Pick one of the target's Diplomacy, Martial, Stewardship, Intrigue, Learning or Prowess. It drops by **1, plus 1 per 5 of your Intrigue** (maximum 12) for a year. You can hex the same person once per year.
- **Copy Technique:** unlocked by *Kurokonton: Malocchio Eyes*. Costs 100 piety, with a 1-year cooldown. The target must be **your prisoner** with an education trait. You gain 1 perk point in the lifestyle matching their education (Martial and Prowess educations both give Martial).

### Cultivation Lifestyle
A seventh lifestyle tab, visible only to Cultivators aged 16+, with a gold XP bar.
- **Focuses:** Deep Meditation and Physical Training.
- **Trees shown, in order:** Alchemy, then Handseals, then your Style, then your Element(s) alphabetically. Trees you haven't unlocked stay hidden.
- The window scrolls sideways when the trees don't fit on screen.

#### Perk trees
Every tree has **10 perks**:
- **Row 1:** two roots.
- **Row 2:** two perks continuing them.
- **Row 3:** a central perk that needs both.
- **Row 4:** four perks, each with a **secondary bonus**.
- **Capstone.**

Each Style and Element also favours specific men-at-arms:
- **Styles:** Akakiru → pikemen and heavy infantry (cheaper too), Aoyusumu → siege weapons, Kiihakai → archers, Kurokonton → skirmishers, Midorikatai → cavalry.
- **Elements:** Darkness → skirmishers, Earth → heavy infantry, Fire → heavy cavalry, Ice → pikemen, Light → archers, Storm → siege weapons, Water → light cavalry, Wind → archers.

| Tree | Perks (row 1 / row 2 / centre / row 4 / capstone) |
|---|---|
| **Alchemy** | Herb Lore (+0.15 health) · Poison Craft (+5 hostile scheme success)<br>Herbal Remedies (+10 epidemic resistance) · Toxicology (+5 hostile scheme success, +1 Stewardship)<br>Pill Refinement (+5% lifestyle XP)<br>Treasure Refining (-15% artifact decay, +0.25 monthly gold) · Elixir of Vigor (+0.15 health, +5% fertility) · Calming Draughts (+10% stress loss, +1 Learning) · Battlefield Salves (-5% own fatalities, +5 epidemic resistance)<br>**Grandmaster Alchemist (+5 yrs life expectancy, +0.25 health, +0.25 health-penalty negation, +1 Stewardship)** |
| **Handseals** | Craft Shard (+0.5 monthly gold) · Reinforcement (+3 holding defense, +10% garrison)<br>Counterseal (-10 enemy scheme success vs you) · Sealing Formations (-10% build time, -10% building cost)<br>Silent Seals (+1 Intrigue, +5 scheme secrecy)<br>Four Winds Enhancement (+10% stress loss, +1 Learning, +1 Diplomacy) · Warding Circles (+2 holding defense, +3 county opinion) · Binding Formations (+0.1 monthly control, +5% tax) · Shard Hoard (+0.5 monthly gold, -5% build cost)<br>**Thousand Seal Mastery (+1 Diplomacy, +1 Martial, +1 Stewardship, +1 Intrigue, +1 Learning)** |
| **Akakiru** | Crimson Edge (+5% enemy fatalities, +2 prowess) · Code of the Blade (+10% prestige gain, +10% legitimacy gain)<br>Pike Wall (+15% pikemen damage, +15% pikemen toughness, -10% pikemen maintenance) · Iron Ranks (+15% heavy infantry damage, +15% heavy infantry toughness, -10% heavy infantry maintenance)<br>Scorched Path (+5% enemy fatalities, +10% pursuit)<br>Bladed Lands Armory (-15% artifact decay, +10% knight effectiveness, -15% pikemen recruitment cost, -15% heavy infantry recruitment cost, +2 prowess) · Duelist's Honor (+5% prestige gain, +5% knight effectiveness) · Edge of Space (+10% travel speed, +5% army movement) · Severing Cut (+5% enemy fatalities, +5% pursuit)<br>**Akakiru Mastery (+2 Stewardship, +4 prowess, +10% enemy fatalities, +1 knight, +10% travel speed)** |
| **Aoyusumu** | Prayer Engine (+10% piety gain, +5 clergy opinion) · Calming Current (+10% stress loss, +5 vassal opinion)<br>Mirror Mind (+15% counter efficiency, -10 enemy scheme success vs you) · Flowing Retreat (-15% retreat losses, +2 prowess)<br>Shelter the Common Folk (+5 county opinion, +0.1 monthly control, +10 epidemic resistance)<br>Siege Prayer Engines (+20% siege weapon siege value, +15% siege weapon toughness, -10% siege weapon maintenance, +10% siege weapon damage) · Exorcist's Rite (+10 epidemic resistance, +5 same-faith opinion) · Hear the Prayers (+0.5 monthly piety, +5 clergy opinion) · Precognition (+10% counter efficiency, -5 enemy scheme success vs you)<br>**Aoyusumu Mastery (+2 Diplomacy, +4 prowess, +5 same-faith opinion, **unlocks Chi Healing**)** |
| **Kiihakai** | Fertile Fields (+0.2 capital development growth) · Ward (+4 holding defense, +10% garrison)<br>Mending Chi (-10% own fatalities, +2 prowess, **unlocks Chi Healing**) · Scrying Sphere (-10 enemy scheme success vs you, **unlocks Scry**)<br>Binding Wards (+0.2 monthly control, +10% innovation spread)<br>Sun Barrage (+20% archers damage, +10% archers toughness, -10% siege phase time, +10% archers pursuit) · Runic Empowerment (-10% artifact decay, -5% build time) · Mystic Academy (+5% lifestyle XP, +1 Learning) · Barrier of Chi (+5% army toughness, +2 defender adv.)<br>**Kiihakai Mastery (+2 Learning, +4 prowess, +10% lifestyle XP, +5% army damage)** |
| **Kurokonton** | Shadow Step (+10 hostile scheme success) · Yin Aura (+10 scheme secrecy, -10 days per scheme phase)<br>Hex (+5 dread, **unlocks Hex**) · Vanishing Arts (-20% retreat losses, +10 travel safety)<br>Malocchio Eyes (+1 Intrigue, **unlocks Copy Technique**)<br>Shadow Skirmishers (+20% skirmishers damage, +15% skirmishers toughness, +15% skirmishers pursuit, +10% raid speed) · Thousand-Face Mask (+5 travel safety, +5 scheme secrecy) · Curse Mastery (+10% dread gain, +3 dread) · Assassin's Patience (+5 hostile scheme success, -5 days per scheme phase)<br>**Kurokonton Mastery (+2 Intrigue, +4 prowess, +1 hostile scheme slot, +15% dread gain)** |
| **Midorikatai** | Iron Body (+0.25 health, +2 prowess) · Beast Clans (+2 hills adv., +2 forest adv., +2 mountains adv.)<br>Unbreaking Line (-10% own fatalities) · Strengthen the Weak (+10% levy size, +10% levy reinforcement, +5% army toughness)<br>Subjugation Domain (+25% Hunter XP, **+10% hunt success**)<br>Beast Riders (+15% light cavalry damage, +15% light cavalry toughness, +15% heavy cavalry damage, +15% heavy cavalry toughness, +10% light cavalry pursuit) · Wallbreaker (-10% siege phase time, +10% heavy infantry siege value) · Warrior-King (+1 knight, +5% knight effectiveness) · Volcanic Endurance (+0.15 health, +0.15 health-penalty negation)<br>**Midorikatai Mastery (+2 Martial, +4 prowess, +15% knight effectiveness, +5% army toughness)** |
| **Darkness Element** | Veil of Night (+10 scheme secrecy) · Shadow Ambush (+10% counter efficiency, +10% pursuit)<br>Dread Aura (+5 dread) · Devouring Dark (+5% enemy fatalities, +10% dread gain)<br>Absorption (+5 hostile scheme success)<br>Night Raiders (+15% skirmishers damage, +10% skirmishers toughness, +10% raid speed) · Snuff the Light (+5 scheme secrecy, -5 enemy scheme success vs you) · Drink the Sound (+5% counter efficiency, -10% retreat losses) · Yin Hunger (+3 dread, +5% dread gain)<br>**Darkness Avatar (+2 Intrigue, +4 prowess, +10 dread, +5 hostile scheme success)** |
| **Earth Element** | Stone Shaping (-10% build time) · Fortress Ground (+3 defender adv., +10% garrison)<br>Mineral Skin (+0.25 health, +5% army toughness) · Rich Soil (+0.15 capital development growth, +5% levy size)<br>Earthsense (+10% counter efficiency)<br>Stone Legion (+15% heavy infantry damage, +15% heavy infantry toughness, +10% heavy infantry siege value) · Walls of Stone (+3 holding defense, +5% garrison) · Fertile Plains (+5% levy size, +5% tax) · Mountain's Endurance (+0.1 health, +2 mountains adv.)<br>**Earth Avatar (+2 Stewardship, +4 prowess, -10% building cost)** |
| **Fire Element** | Wildfire (+10% enemy fatalities) · Burning Blood (+10 epidemic resistance)<br>Passion (+5 attraction opinion, +10% fertility) · Searing Advance (+3 attacker adv.)<br>Raiding Flame (+20% raid speed)<br>Blazing Charge (+15% heavy cavalry damage, +10% heavy cavalry toughness, +10% heavy cavalry pursuit) · Consuming Flames (+5% enemy fatalities, +5% dread gain) · More Fuel (+5% army damage, +2 prowess) · Flame Purge (+5 epidemic resistance, +0.1 health)<br>**Fire Avatar (+2 Martial, +4 prowess, +5% enemy fatalities)** |
| **Ice Element** | Frozen March (+3 winter adv., +10% winter movement) · Preserved Stores (+25% supply duration)<br>Frost Seal (-10% own fatalities) · Stillness (+10% stress loss)<br>Freeze the Rivers (+10% army movement)<br>Glacier Wall (+15% pikemen damage, +15% pikemen toughness, +10% pikemen screen) · Deep Freeze (+10% supply capacity, +10% supply duration) · Slowed Blood (+5% counter efficiency, +5% enemy fatalities) · Preservation (+0.15 health-penalty negation, +2 yrs life expectancy)<br>**Ice Avatar (+2 Learning, +4 prowess, +0.25 health-penalty negation)** |
| **Light Element** | Radiant Presence (+10% piety gain) · Beacon of Light (+15% diplomatic range, +5 other-culture opinion)<br>Purifying Light (+10 epidemic resistance) · Glory (+10% prestige gain)<br>Inspiring Aura (+3 court grandeur)<br>Searing Rays (+15% archers damage, +10% archers toughness, +10% archers pursuit) · Revelation (-5 enemy scheme success vs you, +5% diplomatic range) · Blinding Flash (+10% counter efficiency, +5% pursuit) · Radiant Court (+3 general opinion, +2 court grandeur)<br>**Light Avatar (+2 Diplomacy, +4 prowess, +5 other-culture opinion, +10% diplomatic range)** |
| **Storm Element** | Thunderous Charge (+15% army movement) · Thunderclap (+20% pursuit)<br>Unsubtle (+10% dread gain, +0.5 monthly prestige) · Shock Assault (+3 attacker adv.)<br>Lightning Siege (-10% siege phase time)<br>Thunder Engines (+20% siege weapon damage, +15% siege weapon siege value, +10% siege weapon toughness) · Rolling Thunder (+10% raid speed, +5% army movement) · Deafening Roar (+5% enemy fatalities, +3 dread) · Storm Front (+2 attacker adv., +3% army damage)<br>**Storm Avatar (+2 Martial, +4 prowess, +20% raid speed)** |
| **Water Element** | Healing Waters (-5% own fatalities, +2 prowess, **unlocks Chi Healing**) · Sailor's Grace (+15% naval speed, -15% embark cost, +3 coastal adv.)<br>Tidal Mending (-10% own fatalities) · Adaptation (+2 hills adv., +2 forest adv., +10% supply duration)<br>Inevitability (+0.15 monthly control)<br>Flowing Flank (+15% light cavalry damage, +10% light cavalry toughness, +10% light cavalry pursuit) · Redirect Force (+10% counter efficiency, -10% retreat losses) · Wave Walker (+10% naval speed, -10% embark cost) · River's Patience (+5 vassal opinion, +5% stress loss)<br>**Water Avatar (+2 Diplomacy, +4 prowess, +5 vassal opinion)** |
| **Wind Element** | Swift Winds (+15% travel speed) · Courier Winds (+15% diplomatic range)<br>Scout's Eye (+10% army movement, +10% counter efficiency) · Carried on the Wind (+10 travel safety)<br>Freedom (+10% stress loss)<br>Wind-Guided Arrows (+15% archers damage, +15% archers pursuit, +10% archers toughness) · Skyward Leap (+5% army movement, +10% pursuit) · Cushioned Fall (-15% retreat losses, +0.1 health) · Blades of Air (+5% enemy fatalities, +2 prowess)<br>**Wind Avatar (+2 Intrigue, +4 prowess, -20% retreat losses)** |

---

## Testing (console, launch with `-debug_mode`)
```
add_trait ac_cultivator
effect = { add_prestige = 1000 add_piety = 1000 }
effect = { add_ac_cultivation_lifestyle_xp = 5000 }
```
Problems are logged to `Documents/Paradox Interactive/Crusader Kings III/logs/error.log`; search it for `ac_`.

The vanilla event overrides are generated from the installed CK3 event definitions. Edit `tools/event_option_specs.py`, `tools/event_expansion_specs.py`, `tools/event_activity_specs.py` or `tools/event_dlc_specs.py`, then run:
```
python tools/build_event_overrides.py --game-root "C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game"
python tools/build_event_overrides.py --check
python tools/build_event_tracker.py
python tools/build_event_tracker.py --check
python -m unittest discover -s tools -p "test_*.py" -v
```
The builder refuses game versions other than 1.20.1 until their upstream changes are reviewed. `tools/event_override_sources.json` records the source event hashes. Regression checks verify preserved vanilla options and cleanup, fatal intervention gates, linked tournament outcomes, captive eligibility, native event references, file-local helper dependencies, healing cooldowns and localization. Activity checks also cover jockey eligibility, deferred fall injuries, board-game resolution, exact brawl repairs, murder-feast bookkeeping and the exclusion of ordinary duels. They do not replace an in-game playtest: use a separate debug save to test travel, disaster contracts, plagues, prison, school techniques, tournaments, hunts, court petitions and fatal outcomes with and without the required abilities. Most of these events require scopes supplied by their normal gameplay chains; firing a bare event ID from the console is insufficient.

To refresh the Excel workbook after generating the registry, run `node tools/build_event_tracker.mjs` with `@oai/artifact-tool` available through the external workspace runtime (`tools/node_modules` may be a junction to that runtime's `node_modules`). The workbook is generated from `docs/event-registry.json`; make persistent changes in the event specifications. Tracker checks verify complete coverage, sorting and source locations. DLC checks also cover restored examination preparation, the palace multiplier, noncombat rescue follow-ups, paid construction, native herd losses, driver scopes and the exclusion of catastrophic Greek-fire flags. CK3 Tiger 1.19 does not recognize several native 1.20.1 religious stress/fulfillment tokens, so its diagnostics require review rather than a blanket pass/fail claim.

---

## Repository layout
| Path | Contents |
|---|---|
| `AuraClash.mod` | Launcher descriptor |
| `AuraClash/descriptor.mod` | In-folder descriptor |
| `AuraClash/common/` | Traits, decisions, lifestyle, perks, focuses, interactions, on_actions, game rule, scripted triggers/effects/values/GUIs |
| `AuraClash/events/` | Events (Mortal Core Training, Style, Element and Foundation choice) |
| `AuraClash/gui/` | Lifestyle window (modified copy of vanilla) |
| `AuraClash/gfx/` | Icons and illustrations |
| `AuraClash/localization/` | English text |

All script keys use the `ac_` prefix to avoid clashing with vanilla or other mods.

---

## Roadmap
- Lore-accurate refinements of the current perks, plus capstone traits
- Prayer Talisman requirement for Aoyusumu's Chi Healing
- Cultivator gained through a good tutor, or a childhood event when raised by a cultivator
- Additional artwork for perks, decisions and interface elements

---

## License
This repository uses more than one license. **[NOTICE.md](NOTICE.md) lists which license covers which files.**
- **Code:** MIT. See [LICENSE](LICENSE).
- **Aura Clash setting content** (names, lore, localization text and artwork): all rights reserved, with permission to use it in CK3 mods and submods of this mod, non-commercially, with credit. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md).
- **Files derived from Crusader Kings III** remain © Paradox Interactive.

"Aura Clash" is a trademark of Aurillian Productions LLC. This is an unofficial mod and is not affiliated with or endorsed by Paradox Interactive.

More Aura Clash: [auraclash.com](https://www.auraclash.com) · [banishedtales.com](https://www.banishedtales.com)
