# Testing and reporting bugs

## Verified coverage

The **1.6.1 build** passed **108 Python regression tests** and **6,248 native engine checks** against CK3 **1.21.0 on macOS**, with no mod-specific script errors or GUI warnings. The checks include the ruler tools, Florin compatibility changes and the existing gameplay regression suite.

The release mod is designed for **Windows, macOS and Linux**, using the same ZIP on all three. It contains CK3 scripts, GUI definitions and localisation files, with no platform-specific executable. Windows coverage is limited to the manual checks below; Linux has not been playtested by us. The optional developer engine-check harness currently runs on macOS only; players do not need that harness or Python.

Routine release and game patch checks run on macOS. We test on Windows when investigating a reported Windows-specific bug.

Coverage includes:

- Selection, pins, favourites, numeric input, expired references and confirmation snapshots.
- Traits, age limits and XP tracks; static culture/faith catalogs and dynamic culture/rite copying.
- Appointments, prison/family tools, character creation, contracts and title transfers with vassals.
- Artifacts, native visual-selection context, DLC requirements and removable boosts.
- Twelve controlled war outcomes for both primary leaders and both ally sides, with an unrelated war left active.
- Changed ownership, dynasty or capital during review; Cancel and death of either party.
- Script/localization references, all 424 classic action adapters, building placement and packaging rollback.
- Settlement size increases and decreases, seven district slots without repeat stacking, free district
  construction and eligible upgrades through the confirmation flow, and a removable popular-opinion boost.
- An open confirmation from an older mod build cannot apply after an update.
- Legitimacy adjustments, ruler-only dread controls, dread limits and tyranny removal.
- Language learning, shared acceptance limits, campaign-created cultures and changed-culture review rejection.
- All 120 native legacy definitions, available trait choices, prerequisite order, duplicate/eligibility checks,
  renown balance and dynasty-level preservation, and changed-dynasty review rejection. DLC-specific actions
  are exercised when eligible in the test configuration; otherwise their disabled state is checked.
- Reciprocal guardianship, guardian replacement/removal protection, the two-ward limit, pending offers,
  age bounds and all five native education-focus callbacks.
- Reciprocal alliance creation/breaking, recreation after a break, Cancel, liege-chain/unlanded exclusions
  and death of Other while a review is open.
- Local Workshop ID preservation during installation, portable-package isolation and rollback.

The final gameplay review recorded no mod-specific script errors or GUI warnings. Engine checks use fresh test profiles and generated campaigns; they do not load player saves. Test fixtures are not included in the release mod.

## Limits and manual checks

These checks do not cover every campaign state, DLC combination, screen size, other-mod combination or long-term succession. The native harness checks effects, eligibility and parsed GUI definitions; it does not click through the rendered window or perform save/reload playtests. Saved Force/Forbid knight preference should still be inspected in the normal Knights window; command execution and native values are checked by the harness. Multiplayer is not verified.

A separate manual check used the published Steam 1.6.1 download as the only mod in a fresh CK3 1.21.0 campaign on macOS, with debug mode off. The lower-right **Cheats** button and **Decisions → Open Cheat Menu** both opened the movable window, and **Open Classic Cheat Menu** opened the original event menu.

All three entry points also worked with Oddbyte 1.6.1 on CK3 1.21.0 in a Windows Shadow PC session at 3024×1900, 150% GUI Scaling and DirectX 11. This was an existing paused campaign using its current playset. The reported missing button did not occur in that configuration.

A second Windows 11 pass used the published 1.6.1 ZIP as the only mod in a fresh CK3 1.21.0 campaign, in a 1920×1080 window at 100% GUI Scaling with DirectX 11. The Cheats button opened normally. Manual checks covered resources, exact-value Apply and Cancel, portrait targeting, Search, pins, favourites, legitimacy and dread, instant district construction, the construction boost, opinion, alliances, and language learning. Resource changes, pins, the favourite and the construction boost survived a save and reload. No Oddbyte entries appeared in the error log and the GUI warning log was empty.

In 1.6.1, the floating **Cheats** button can cover part of a row in **Decisions** and receive clicks meant for that row. Click the exposed label on the left of the row if you use 1.6.1. Version 1.6.2 hides the button while Decisions is open. The separate report of a missing button on the campaign map was not reproduced.

The fix was checked in windowed CK3 1.21.0 on macOS and Windows 11. On Windows at 1920×1080, clicking the previously covered part of the **Open Classic Cheat Menu** row now selects that decision. Both Decisions entries still work. Closing Decisions brings back the floating button, which still opens Oddbyte.

Oddbyte is compatible with the November 18 Florin hotfix (CK3 1.21.0, Steam build 26757580). All 108 Python tests and 6,248 in-game checks passed, with no mod-specific script errors or GUI warnings. A separate test confirmed that refilling men-at-arms twice restores existing regiments to capacity without changing regiment counts, capacity or gold. In the rendered game, the **Cheats** button hid while **Decisions** was open. The previously covered part of the classic decision row accepted clicks, and both the main decision and the restored map button opened Oddbyte.

For a release playtest, use a separate save and check:

1. Open, close and drag the window; scroll long pages at your usual UI scale. Open and close Decisions and check that the floating **Cheats** button hides and returns without intercepting clicks on its rows.
2. Select another person, pin them, set Other and verify both names before acting.
3. Try resource/skill edits, traits and an exact-value review. Cancel before applying a major change.
4. Test a war/artifact picker and a title transfer. Confirm the named object and intended person.
5. Check knight preferences, save/reload, succession and compatibility with your usual mods.

## Report a problem

[Open a GitHub issue](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/issues) with:

- Mod version, CK3 version, operating system and other enabled mods.
- Menu/button name and the selected character's relevant status, such as ruler, courtier or prisoner.
- Steps to reproduce, expected result and actual result.
- For a missing Cheats button, include the screen resolution, GUI scaling, and whether either entry in [Decisions](INSTALLATION.md#if-the-cheats-button-is-missing-in-a-campaign) appears and opens.
- A screenshot or relevant `twcm` lines from the game's `logs/error.log`, if available.

Review attachments before uploading them and omit private campaign information you do not want to share.
