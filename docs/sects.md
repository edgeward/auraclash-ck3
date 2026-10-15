# Cultivation sects

Sects are persistent provincial societies. Their members can also hold secular titles. Open **Decisions → Cultivation → Consult the Sect Register** to express interest in joining a sect or manage your existing membership.

## Geography and membership

Each eligible de-jure kingdom receives one sect at its historical capital county. The kingdom does not need to exist as a held title. Titular kingdoms, titles without a populated capital, and titles sharing a province already assigned to a sect are skipped. The headquarters remains in its original province through conquest and changes of master. Existing saves initialize on the next quarterly playable-character pulse; a new game is recommended for testing.

A new sect starts with one Master, eight Upper Disciples and sixteen Lower Disciples. Recruitment can fill the ten upper and twenty lower places. All members are adult cultivators. A mortal who passes admission awakens as a cultivator. Joining preserves an existing foundation, style and elements; an untrained recruit learns the sect's lineage. A cultivator belongs to one sect at a time. Leaving clears contribution and merit and prevents rejoining for one year.

The geographic policy is isolated in `ac_sect_kingdom_eligible_trigger` and the initialization on-action. Replace that policy when the custom map is introduced, while retaining the society and province data model.

## Martial identities

These are initial templates, not unique global organizations. A kingdom name distinguishes sects sharing a template.

| Lineage | Elements | Style | Foundation |
|---|---|---|---|
| Ember Peak | Fire, Earth | Akakiru | Tiger |
| Mirror Tide | Water, Ice | Aoyusumu | Crane |
| Thunder Hoof | Storm, Wind | Kiihakai | Stallion |
| Jade Mountain | Earth, Light | Midorikatai | Ox |
| Veiled Moon | Darkness, Ice | Kurokonton | Snake |
| Dawn Lotus | Light, Water | Aoyusumu | Dragon |
| Ashen Blade | Fire, Darkness | Akakiru | Wolf |
| Sky Palm | Wind, Storm | Midorikatai | Monkey |

## Provincial estate

The sect estate is a **native CK3 domicile**, with an illustrated landscape, clickable building plots and a native construction queue. Open it with the round **Sect Domicile** button beside the bottom-left portrait, or through **Decisions → Cultivation → Consult the Sect Register → Open the sect domicile**. Its ring displays native construction progress; a second button opens sect contracts. Both shortcuts appear only for sect members and leave the normal personal-domicile button available. Its sect-specific controls address the exact title domicile: CK3's stock editor assumes the owner's government-selected personal domicile and displays a secondary sect estate as a prototype. This interface leaves the personal domicile and vanilla window intact. The separate roster and records screen displays contribution, merit, disciples and relationships.

Each sect has its own county-tier **landless Sect Master title**, created through CK3 1.20.1.1's `create_domicile_title` API. The title carries the domicile and follows the sect's chosen Master. It is not a noble-family title, a county holding, or a change to the Master’s landed government. A ruler can keep their secular titles, government and existing personal estate while holding this office. A new landless founder uses the Sect Leadership government; when a domicile must be created for an existing ruler, a landless steward creates the title before its transfer, avoiding a government switch for that ruler.

The headquarters remains fixed in its province; moving the realm capital or changing Master does not move the domicile. Succession and voluntary handover transfer the same title and domicile, including buildings and active construction. The landless Sect Leadership government has a native non-dynastic fallback succession order. The story’s merit-based successor choice remains authoritative, with a delayed title-gain repair for native succession finishing after story processing. This never changes a landed Master’s realm succession laws. The society continues to track members, martial identity, diplomacy and its shared treasury.

Buildings have three levels. Each upgrade costs 100 × the new level in **sect gold**, charged once when native construction starts. The illustrated estate shows the treasury, current levels, project progress and costs. Cancelling removes the exact unfinished native building and refunds the recorded expenditure once through its native callback, preserving an earlier completed level when cancelling an upgrade. Base construction time is 180 days, subject to native construction modifiers. Only one project can run at a time. Construction completion updates sect training and mission benefits; monthly maintenance reconciles building removal or downgrades. The treasury starts at 300, receives 60 annually and gains mission proceeds and donations. Annual maintenance caps accumulated reserves at 2,000.

Existing saves create the native domicile on the next monthly sect-maintenance pass, or when opening the estate. Completed building levels are copied into native buildings. A project already paid for under the previous event-based estate system retains its timer and finishes once, without a second charge; new native construction is blocked until it finishes.

The landscape is original generated artwork in the style of CK3’s Chinese domiciles. Building sprites and masks reference installed Chinese estate assets; no Paradox textures are redistributed. The PNG, generation prompt and DDS packaging tool are retained under `assets/sect-domicile` and `tools/build_sect_landscape.py`.

| Building | Benefit |
|---|---|
| Cultivation Hall | 20 Cultivation lifestyle XP per level annually |
| Alchemy Pavilion | Unlocks medicinal pills in the exchange |
| Martial Training Ground | Power Core XP per level annually; battle strength |
| Scripture Library | 20 Cultivation lifestyle XP per level annually; manual exchange |
| Spirit Garden | Fortitude Core XP per level annually |
| Formation Hall | Agility Core XP per level annually; battle strength |

On a master's death, the available Upper Disciple with the greatest merit, prowess and learning succeeds. A Lower Disciple can succeed if no upper is available. A caretaker preserves the sect if no member can serve. The estate title, buildings and construction pass to the new Master; the treasury and diplomacy remain with the society. The successor retains their secular titles. Masters can voluntarily hand over to an upper disciple. An upper disciple with 400 lifetime merit and 200 available contribution can petition an AI master, with a 60% success chance and a five-year cooldown.

## Trials

For a nonmember, **Consult the Sect Register** records interest in joining. It does not select an activity location, start a trial, or charge a hosting fee. Interested players receive announcements of trials within diplomatic reach and can review the invitation in the native activity screen, then choose whether to travel. They may withdraw interest through the register. Expressing interest through a particular master's character interaction instead requests news from that sect.

**Sect Masters host trials.** NPC masters consider opening one every three months, with a 30% random chance when a Lower Disciple place is available or an eligible disciple has requested promotion to a vacant Upper Disciple place. This schedule runs independently of player interest. A sect has a one-year trial cooldown and one activity or pending activity plan at a time. A player who becomes Sect Master can host through **Activities → Sect Trial**; ordinary disciples and applicants cannot host it.

The sect treasury pays 50 gold when a trial is created. Applicants do not pay a hosting fee. All three phases use the same permanent headquarters, selected once by a player Master or automatically by the NPC master's planner. Native invitations and travel remain in use; the examinations test understanding, martial form and spiritual control.

Admission requires 40 points and a lower-disciple vacancy. Promotion requires 55 points, a vacancy among upper disciples, a promotion request and 150 contribution. Candidates compete by examination score for available places. Promotions are resolved first, freeing lower-disciple places for admission. The fee is charged when the examination begins. An interrupted or invalid promotion trial refunds it once. A completed failed examination consumes the fee. Candidates have a one-year cooldown after a completed trial. A successful upper disciple can learn another sect element while respecting the mod's two-element limit.

Native AI planning needs a ruler controller, so an unlanded master can use a ruler member, the ruler at the headquarters, or an available ruler in that realm or kingdom to arrange the activity. This also works when a player personally owns the headquarters. Once the activity exists, its actual host is transferred to the Sect Master. The society retains its buildings, membership and treasury. A request can be deferred by the ruler's other activity plans; an unfulfilled plan expires after 90 days so the master can try again.

## Missions and contribution

Lower Disciples, Upper Disciples and Sect Masters can all take missions. The **Sect Contracts** HUD button and register open a board of persistent native task-contract offers. Each job opens CK3's normal contract letter with its employer, difficulty, destination, potential rewards and failure consequences. **Take Contract** reserves the job and opens the normal route planner, following the native adventurer transport-contract pattern. Reaching the job location starts a mission-specific encounter; elapsed time alone cannot award contribution. The landed ruler keeps their titles and government. The planned trip includes a return journey. Cancelling the planner or aborting the mission journey abandons the assignment.

Six jobs are posted for the member at inhabited county capitals within the sect's kingdom. Reopening the board retains existing offers. Lower Disciples receive difficulty 1, Upper Disciples difficulty 2, and Masters difficulty 3. Difficulty adds 10 percentage points of challenge per level above 1 and multiplies contribution and Cultivation XP by the level. The board displays the actual numeric difficulty used for rewards and success chances.

| Mission | Main skill | Base contribution |
|---|---|---:|
| Patrol the Sect Roads | Prowess | 50 |
| Gather Spiritual Herbs | Learning | 50 |
| Recover a Lost Manual | Intrigue | 70 |
| Settle a Local Dispute | Diplomacy | 40 |
| Aid the Local Villages | Stewardship | 50 |
| Guard a Sect Delegation | Martial | 70 |

Each encounter offers a careful approach (+10 percentage points), an expert approach at 15 in the relevant skill (+20), a suitable cultivation technique (+25, costs 10 stress), and withdrawal. Success also grants 40 Cultivation XP per difficulty level and adds 20 gold to the sect treasury. Failure causes 15 stress. The relevant skill contributes to the success chance; Upper Disciples receive an additional 10 percentage points. Completion, failure or abandonment starts 90 days of rest. A disciple may undertake only one native task contract at a time, including ordinary adventurer contracts. Leaving cancels the active sect contract and removes its offers. The exact contract identity and a resolved marker prevent stale events from paying twice. Old timer-based commissions are retired without rewards or a new cooldown when the board opens or their old timer expires.

Contribution and Sect Merit are saved separately on each member; they do not use the native Merit currency. Contribution is spendable. Sect Merit records contribution earned during the current membership and supports succession. Spending contribution does not reduce Sect Merit. Both totals appear in the Sect Register; the roster and records screen shows contribution and lists member merit. Missions have skill-based success chances, cultivation benefits, failure consequences and cooldowns.

| Exchange | Contribution | Requirement and result |
|---|---:|---|
| Medicinal pill | 50 | Alchemy Pavilion; consume through a decision for stress relief, Fortitude XP and six months of improved health; six-month use cooldown |
| Manual study | 75 | Scripture Library; 150 Cultivation lifestyle XP; six-month cooldown |
| Stipend | 50 | 40 gold transferred from the sect treasury |

## Relationships, battle and joint training

Alliances and rivalries link societies, so they survive a master's succession. Masters negotiate through character interactions or the ledger's neighboring-sect menu. An alliance replaces a rivalry; declaring rivalry ends an alliance. NPC sects occasionally form relationships with neighboring kingdoms' sects.

A master may challenge a rival sect to battle. The clash resolves after 30 days on monthly maintenance, using available disciples' prowess, buildings, allied support and joint-training preparation. Winners earn contribution and Power XP, and take up to 75 gold from the defeated treasury. Participants risk nonfatal wounds. Both sects receive a two-year battle cooldown. An ally of both sides remains neutral. These are group sect clashes, without territorial conquest or the separate single-combat system.

**Joint Sect Training** costs 75 gold and has a two-year cooldown. It invites the host sect and allied disciples for two phases at the host's headquarters. Completing it alongside an actual allied attendee grants 30 contribution, 100 Cultivation lifestyle XP, 5 Power Core XP, +2 prowess for two years and a temporary formation advantage. Attendance from a former ally does not qualify.

## Development and validation

`tools/build_sect_content.py` generates repeated identities, native domicile types and buildings, estate upgrades, contracts and localization. `tools/build_sect_landscape.py --check` verifies the DDS against the original PNG. Lifecycle, activities, diplomacy and their event choices remain hand-authored. Balance values live in `common/script_values/ac_sect_values.txt`.

Run the repository checks with `python -m unittest discover -s tools -p "test_*.py"`. Generate with `python tools/build_sect_content.py`; verify generated content with `--check`.

`AuraClash/tests/ac_sect_tests.txt` contains sixteen native CK3 integration scenarios. The tests deliberately alter England's, Scotland's, Wales's, Denmark's, Bohemia's and Bavaria's sects, a master, rulers and a Byzantine ruler's estate. `tools/prepare_sect_engine_checks.py` prepares an isolated user folder and a QA-only startup overlay; `--out` supports a separate folder for concurrent fixtures. Launch with the command it prints, then unpause the disposable game so the AI planner and delayed checks can run. The overlay is never enabled in the normal installed mod. Its log distinguishes actual PASS and FAIL conditions. Activity requests are asynchronous; the complete suite uses this staged harness rather than a single immediate console call. Individual scenarios can also be invoked with `scripted_tests <scenario_name>` after their prerequisites are established. Use `--estate-ui` to open a player Master's illustrated sect domicile. Its audit sequence is: commission Alchemy Pavilion I, audit, cancel, audit, commission again, audit, then unpause for 200 days. Use `--master-ui` for a separate activity-planner fixture: open Activities, plan a Sect Trial, select the Welsh headquarters once and start it. Its delayed assertion checks the actual host and headquarters after creation.

The design references the installed CK3 1.20.1.1 examination activities, administrative estate rules, task contracts and story cycles. [Monks and Mystics v1.5.2](https://steamcommunity.com/sharedfiles/filedetails/?id=3786025000) informed the society concept through its public description; no code or assets from that mod are included.

The domicile implementation was verified against the installed CK3 1.20.1.1 build: all 67 repository checks, 42 native integration assertions and 15 assertions in the estate UI fixture passed. Native coverage includes actual owner death, retained secular government and titles, coexistence with a personal administrative estate, inherited construction, prepaid migration, upgrade cancellation without losing the earlier level, native contracts, a full ranked admission trial and completed allied training. Actual estate clicks verified construction, an unchanged personal wallet, a single sect-treasury refund and completed native construction updating the painted building and sect benefits. The interest register, invitation flow, player Master activity planner and mission board were inspected in-game in the earlier recruitment checks; player hosting was started after selecting the headquarters once. The event override generator also accepts 1.20.1.1: all 143 referenced native event blocks are unchanged from the reviewed 1.20.1 versions. Long-campaign balance and multiplayer still need broader testing.

The contract/HUD update passes all 69 repository checks. A separate clean native fixture passes 12 assertions covering all six reward paths, duplicate-payment protection, abandonment without rewards, clearing offers, persistent unaccepted offers, and actual player cancellation with retained feudal government/titles. The final fixture's error log is empty. A landed Lower Disciple also completed an actual native-planned round trip, resolved the patrol encounter through cultivation, and received contribution and Sect Merit; its audit confirmed cleanup and retained titles. Actual HUD clicks opened both the member's contract board and the correct sect domicile. Use `python tools/prepare_sect_contract_checks.py` to reproduce the isolated contract fixture; its audit button checks a completed or abandoned contract. NPC reward probes suppress only their arrival dispatcher so the native rewards can be asserted deterministically. Player travel and encounters use the shipping scripts.
