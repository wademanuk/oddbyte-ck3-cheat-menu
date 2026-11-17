# Development

## Requirements

- Python 3.
- A CK3 installation matching the supported 1.21.x definitions. The checked-in catalogs were built from 1.21.0.

Players do not need Python, the generators or a development checkout.

## Local paths

`tools/project_config.py` holds the display name, version and package name. Its default game path is the standard macOS Steam location. Set `CK3_GAME_DIR` to your game's **game** directory for another location:

```sh
export CK3_GAME_DIR="/path/to/Crusader Kings III/game"
```

For the optional local installer, `CK3_MOD_DIR` overrides the destination user-data `mod` directory. The default is `~/Documents/Paradox Interactive/Crusader Kings III/mod`.

## Build and check

```sh
python3 tools/build_cheat_mod.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/check_cheat_mod.py
python3 tools/package_mod.py
```

The generator reads native definitions for traits, culture, religion, buildings and display names. It writes the mod under `outputs/Oddbyte-CK3-Cheat-Menu/`. Make lasting script/GUI changes in `tools/`; rebuilding replaces generated files. Package documentation is maintained separately.

`package_mod.py` creates versioned and current ZIPs in the ignored `releases/` directory. It checks archive contents and refuses to overwrite a released version with different content. Bump the version before changing a release. Upload the versioned ZIP as the GitHub Release asset.

`package_mod.py --install` additionally stages and verifies a local installation, backs up the existing folder/descriptor and rolls back failed replacements. Local installation reports, backups and test profiles are ignored by Git.

## Native engine checks

```sh
python3 tools/smoke_editor_mod.py --review --timeout 240
```

The current harness launches the macOS CK3 binary with a fresh temporary profile and test-only overlay, generates a 1066 game and exits after history. It does not load a campaign save. Availability and review checks use emitted guards, excluding only the human-player gate because the history fixture is AI controlled.

The harness is macOS-specific; it is not required to play the mod. Logs/results go to ignored local work directories. See [testing notes](TESTING.md) for the scope of evidence.

## Repository layout

- `outputs/Oddbyte-CK3-Cheat-Menu/`: generated, installable mod and packaged instructions.
- `tools/`: generators, checker, engine fixtures and Python tests.
- `docs/`: player and contributor documentation.
- `CHANGELOG.md`: player-facing release notes.

The `twcm` script namespace and `tw_basic_cheat_menu` installation ID are kept for compatibility with earlier saves. They are internal identifiers, not the public display name. The legacy `parity` metadata key groups preset/building tools.

Keep documentation relevant to players or contributors. Local machine details, work-session notes, installation reports, backups and temporary artifacts do not belong in published source or release ZIPs.
