<p>
  <img src="docs/images/oddbyte-wordmark.png" alt="Oddbyte" width="280">
</p>

# Oddbyte — CK3 Cheat Menu

A single-player cheat menu and character editor for **Crusader Kings III**. Change your ruler, edit other characters and shape your realm from a movable in-game window.

**[Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3840619967)** · **[Paradox Mods](https://mods.paradoxplaza.com/mods/167826/Any)** · **[Manual download](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/releases/latest)**

[Installation](docs/INSTALLATION.md) · [Feature guide](docs/FEATURES.md) · [Report a bug](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/issues)

**Version 1.6.1 · CK3 1.21.x · English · Single-player**

**Designed for Windows, macOS and Linux — one release ZIP for all three.**

![Oddbyte cheat menu showing character selection and resource controls](docs/images/overview.jpg)

## What you can do

| Tools | Examples |
| --- | --- |
| Resources and character | Gold, prestige, piety, renown, legitimacy, dread, tyranny, stress, skills, age, health and fertility |
| Traits and lifestyles | Trait browser, trait experience, lifestyle experience and perk points |
| Diplomacy and family | Alliances, hooks, opinions, relationships, guardians, education, marriage, adoption and house changes |
| Dynasty | Individual legacy unlocks, with normal track order and required trait choices |
| Realm and titles | Claims, title transfers, vassals, contracts, counties and fast construction |
| Military | Refill existing troops, improve commanders and resolve a selected war |
| Culture and religion | Languages, cultural acceptance, culture/faith/rite changes, innovations, traditions, doctrines and tenets |
| Court and artifacts | Recruitment, council appointments, character creation and artifact tools |

Pin up to eight characters, save favourite actions, search by word start and remove active boosts. Major changes open a confirmation naming the affected people and objects.

## Start playing

Download and extract the [release ZIP](https://github.com/wademanuk/oddbyte-ck3-cheat-menu/releases/latest). Copy the `tw_basic_cheat_menu` folder and adjacent `tw_basic_cheat_menu.mod` file into your platform's CK3 user-data `mod` folder:

| Platform | Default mod folder |
| --- | --- |
| Windows | `%USERPROFILE%\Documents\Paradox Interactive\Crusader Kings III\mod` |
| macOS | `~/Documents/Paradox Interactive/Crusader Kings III/mod` |
| Linux (native game) | `~/.local/share/Paradox Interactive/Crusader Kings III/mod` |

Create `mod` if needed. If Documents or the game's user-data folder is redirected, use its actual location. See the [full installation guide](docs/INSTALLATION.md) for each platform's steps and the Linux/Proton note.

1. Restart the launcher, add **Oddbyte — CK3 Cheat Menu** to the playset you launch, and enable it.
2. Load a single-player game and click **Cheats** near the lower-right map controls. **Decisions → Open Cheat Menu** also opens the window.
3. Check the **Selected character** name before applying a cheat. To edit someone else, right-click their portrait and choose **Cheat Menu: Open Editor**.
4. Open **Tools & editors** for the extended tools. For actions involving two people, choose **Cheat Menu: Set Other Character** on the second person's portrait.

No debug mode or console commands are required. The **Classic menu** remains available inside the window.

## Compatibility and limits

- Designed for the **Windows, macOS and Linux** desktop versions of CK3 **1.21.x**. The mod uses CK3 scripts, GUI definitions and localisation files; it has no platform-specific executable.
- Tested on **1.21.0 on macOS**. Windows and Linux have not been playtested by us. Use a separate save when upgrading a campaign from an earlier CK3 patch.
- Relevant DLC features still require their DLC. The catalog does not include extra choices added by other mods.
- Make a separate save before enabling the mod in an existing campaign or updating CK3. Many changes to titles, family links and religious rules have no undo button.
- Remove unwanted custom boosts before disabling the mod. Added district-slot capacity depends on the mod remaining enabled.
- Multiplayer and combinations with other mods are not verified. No vanilla GUI files are replaced.

See the [feature guide](docs/FEATURES.md) for exact targeting, limits and removal options, and [testing notes](docs/TESTING.md) for verified coverage and remaining checks.

## Source and development

The repository includes the generated mod, its Python generators and regression checks. Players only need the release download; Python is used for development.

[Development guide](docs/DEVELOPMENT.md) · [Changelog](CHANGELOG.md)

Oddbyte makes mods and tools for players. This is an unofficial community mod, not affiliated with Paradox Interactive.
