# Testing and reporting bugs

## Verified coverage

The **1.6.1 build** passed **108 Python regression tests** and **6,248 native engine checks** against CK3 **1.21.0 on macOS**, with no mod-specific script errors or GUI warnings. The checks include the ruler tools, Florin compatibility changes and the existing gameplay regression suite.

The release mod is designed for **Windows, macOS and Linux**, using the same ZIP on all three. It contains CK3 scripts, GUI definitions and localisation files, with no platform-specific executable. Windows and Linux have not been playtested by us. The optional developer engine-check harness currently runs on macOS only; players do not need that harness or Python.

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

For a release playtest, use a separate save and check:

1. Open, close and drag the window; scroll long pages at your usual UI scale.
2. Select another person, pin them, set Other and verify both names before acting.
3. Try resource/skill edits, traits and an exact-value review. Cancel before applying a major change.
4. Test a war/artifact picker and a title transfer. Confirm the named object and intended person.
5. Check knight preferences, save/reload, succession and compatibility with your usual mods.

## Report a problem

[Open a GitHub issue](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/issues) with:

- Mod version, CK3 version, operating system and other enabled mods.
- Menu/button name and the selected character's relevant status, such as ruler, courtier or prisoner.
- Steps to reproduce, expected result and actual result.
- A screenshot or relevant `twcm` lines from the game's `logs/error.log`, if available.

Review attachments before uploading them and omit private campaign information you do not want to share.
