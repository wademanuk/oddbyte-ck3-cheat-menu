# Installation

## Install a release

1. Download **Oddbyte-CK3-Cheat-Menu-v1.5.2.zip** from the [latest release](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/releases/latest). The automatically generated GitHub “Source code” downloads are development snapshots; use the named mod ZIP.
2. Open the CK3 **user-data** folder, which contains your `save games` folder, then open or create its `mod` folder. On standard Windows/macOS setups it is under `Documents/Paradox Interactive/Crusader Kings III/mod`. Use your actual Documents location if it is redirected.
3. Copy these two items from the ZIP into that `mod` folder:

   ```text
   mod/
   ├── tw_basic_cheat_menu/
   │   ├── descriptor.mod
   │   ├── common/
   │   ├── events/
   │   ├── gui/
   │   └── localization/
   └── tw_basic_cheat_menu.mod
   ```

4. Restart the Paradox launcher, add **Oddbyte — CK3 Cheat Menu** to the playset you launch, and enable it.
5. Start CK3, load a single-player game and click **Cheats** near the lower-right map controls.

The ZIP contains a ready-to-use mod, not an installer. Keep the folder and adjacent `.mod` filename as supplied.

## Update an existing installation

Close CK3 first. Back up the existing mod folder and adjacent `.mod` file, then replace both with the new release. Enable only one copy in your playset.

The installation folder and script identifiers are retained from earlier versions so existing selections, favourites and custom boosts can remain associated with saved games. The launcher display name is now **Oddbyte — CK3 Cheat Menu**.

## If the mod does not appear

- Check that the `.mod` file sits beside `tw_basic_cheat_menu`, not inside another extracted wrapper folder.
- Use the CK3 user-data `mod` directory, not the Steam game installation directory.
- Restart the launcher after copying the files, and check the playset used to launch the game.
- If the launcher cannot resolve the portable path, open the adjacent `.mod` file in a text editor and set its `path=` to the full location of `tw_basic_cheat_menu`, using forward slashes. Leave `descriptor.mod` inside the folder unchanged.

## Saves and removal

Make a separate save before trying major cheats. Resources, skills, age, claims, family links, ownership and other permanent edits stay when saved. Removing the mod does not reverse them.

Remove unwanted character/county boosts using their removal buttons before disabling the mod. Custom traits and expanded building-slot capacity depend on the mod's definitions. Keep an unchanged save if you want to return to a campaign without the mod.
