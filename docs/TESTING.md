# Testing and reporting bugs

## Verified coverage

The **1.5.2 release** passed **93 Python regression tests** and **5,520 native engine checks** against CK3 **1.20.1.2 on macOS**. It retains the reviewed gameplay effects while updating the branding, documentation and build configuration.

Coverage includes:

- Selection, pins, favourites, numeric input, expired references and confirmation snapshots.
- Traits, age limits and XP tracks; static culture/faith catalogs and dynamic culture/rite copying.
- Appointments, prison/family tools, character creation, contracts and title transfers with vassals.
- Artifacts, native visual-selection context, DLC requirements and removable boosts.
- Twelve controlled war outcomes for both primary leaders and both ally sides, with an unrelated war left active.
- Changed ownership, dynasty or capital during review; Cancel and death of either party.
- Script/localization references, all 424 classic action adapters, building placement and packaging rollback.

The final gameplay review recorded no mod-specific script errors or GUI warnings. Engine checks use fresh test profiles and generated campaigns; they do not load player saves. Test fixtures are not included in the release mod.

## Limits and manual checks

These checks do not cover every campaign state, DLC combination, screen size, other-mod combination or long-term succession. Saved Force/Forbid knight preference should still be inspected in the normal Knights window; command execution and native values are checked by the harness. Multiplayer is not verified.

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
