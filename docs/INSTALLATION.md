# Installation

**Designed for Windows, macOS and Linux. Use the same release ZIP on all three platforms.** The mod uses CK3 scripts, GUI definitions and localisation files. No Python, console commands or platform-specific installer are needed to play.

Built for CK3 **1.21.x**, including the latest Florin hotfix. Playtested on **macOS and Windows**. See the [testing notes](TESTING.md) for coverage and limits. Back up a campaign separately before upgrading it across CK3 versions.

## 1. Download and extract

Download the named **Oddbyte-CK3-Cheat-Menu-vVERSION.zip** from the [latest release](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/releases/latest), then extract it. On Windows, right-click the ZIP and choose **Extract All**; on macOS, double-click it; on Linux, use your archive manager's **Extract** action. `VERSION` is the release number shown on the download page.

Use the named mod ZIP. GitHub's automatically generated “Source code” downloads are development snapshots.

Close CK3 and the launcher before copying the files.

## 2. Open your mod folder

Use the CK3 **user-data** folder, where local saves and settings live. Choose the instructions for your platform below. Create the `mod` folder if it does not exist. If you have never run CK3, launch it once to the main menu and quit so it can create its user-data folders.

### Windows

The default destination is:

```text
%USERPROFILE%\Documents\Paradox Interactive\Crusader Kings III\mod
```

Press **Win + R**, enter `shell:Personal`, and press **Enter** to open your actual Documents folder. Open `Paradox Interactive`, then `Crusader Kings III`, then `mod`. This also helps when Documents is redirected to OneDrive or another location.

### macOS

The default destination is:

```text
~/Documents/Paradox Interactive/Crusader Kings III/mod
```

In Finder, press **Command + Shift + G**, paste `~/Documents/Paradox Interactive/Crusader Kings III`, and press **Return**. Open or create `mod` there. `~` means your home folder.

### Linux

For the **native Linux version** of CK3, the default destination is:

```text
~/.local/share/Paradox Interactive/Crusader Kings III/mod
```

In your file manager, press **Ctrl + L**, enter the path, and press **Enter**. If `mod` does not exist, open its parent `Crusader Kings III` folder and create it. `.local` is hidden; **Ctrl + H** usually shows hidden files. `~` means your home folder.

**Using the Windows version through Proton?** Use that game's Windows user-data folder inside its Proton prefix instead of the native Linux path. Find the prefix under `steamapps/compatdata/1158310/pfx/` in the Steam library containing CK3, then look under `drive_c/users/steamuser/Documents/Paradox Interactive/Crusader Kings III/mod`. Some prefixes use a `My Documents` link. See [Valve's Proton FAQ](https://github.com/ValveSoftware/Proton/wiki/Proton-FAQ#how-does-proton-manage-wine-prefixes) for prefix locations.

If your game uses a custom user-data location, place the mod in that location's `mod` folder instead.

## 3. Copy the mod files

From the extracted ZIP, copy **both** the `tw_basic_cheat_menu` folder and the adjacent `tw_basic_cheat_menu.mod` file into the destination above. The result should look like this:

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

Keep the folder and adjacent `.mod` filename as supplied, including letter case. Copy the files out of the ZIP; the launcher cannot use them while they are still inside it.

## 4. Enable and play

1. Open the Paradox launcher. Find **Oddbyte — CK3 Cheat Menu** under **All installed mods**.
2. Add it to the playset you will launch, and enable it in that playset.
3. Start CK3 using that playset and load a single-player game.
4. Click **Cheats** near the lower-right map controls, or use **Decisions → Open Cheat Menu**.

Make a separate save before trying major edits. See the [feature guide](FEATURES.md) for targeting and individual tools.

## Update an existing installation

Close CK3 first. Back up the existing mod folder and adjacent `.mod` file, then replace both with the new release. Enable only one copy in your playset.

The installation folder and script identifiers are retained from earlier versions so existing selections, favourites and custom boosts can remain associated with saved games. The launcher display name is now **Oddbyte — CK3 Cheat Menu**.

## If the mod does not appear

- Check that the `.mod` file sits beside `tw_basic_cheat_menu`, not inside another extracted wrapper folder.
- Use the CK3 user-data `mod` directory, not the Steam game installation directory.
- Restart the launcher after copying the files, and check the playset used to launch the game.
- If the launcher cannot resolve the portable path, open the adjacent `.mod` file in a text editor and set its `path=` to the full location of `tw_basic_cheat_menu`, using forward slashes. Leave `descriptor.mod` inside the folder unchanged.

## If the Cheats button is missing in a campaign

1. From the campaign map, press **F9** (the default Decisions shortcut), scroll down and choose **Open Cheat Menu → Open window**. If the decision panel is cut off, lower **GUI Scaling** in the game settings. If the window still doesn't appear, try **Open Classic Cheat Menu** in Decisions; it uses a regular game event.
2. If neither decision appears, restart CK3 with a new playset containing only one copy of **Oddbyte — CK3 Cheat Menu**. Check the mod version in the launcher and test in a fresh single-player game so your main save stays untouched.
3. If the Decisions entry opens the window but the map button is still missing, include your screen resolution, in-game GUI scaling, and a screenshot of the lower-right map area in your [bug report](TESTING.md#report-a-problem). Say whether the issue also happens with Oddbyte as the only enabled mod.

## Saves and removal

Make a separate save before trying major cheats. Resources, skills, age, claims, family links, ownership and other permanent edits stay when saved. Removing the mod does not reverse them.

Remove unwanted character/county boosts using their removal buttons before disabling the mod. Custom traits and expanded district capacity depend on the mod's definitions. Keep an unchanged save if you want to return to a campaign without the mod.
