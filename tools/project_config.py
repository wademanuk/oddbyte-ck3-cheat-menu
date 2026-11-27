"""Public identity and local paths shared by the build, checks and packager."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
NAME = 'Oddbyte — CK3 Cheat Menu'
VERSION = '1.7.0'
SUPPORTED_VERSION = '1.21.*'
ARCHIVE_STEM = 'Oddbyte-CK3-Cheat-Menu'
PACKAGE = ROOT / 'outputs' / ARCHIVE_STEM
# Keep the existing installation ID and script namespace for save compatibility.
MOD = PACKAGE / 'tw_basic_cheat_menu'
GAME = Path(os.environ.get('CK3_GAME_DIR', str(
    Path.home() / 'Library/Application Support/Steam/steamapps/common/Crusader Kings III/game'
))).expanduser()
GAME_ROOT = GAME.parent
USERMOD = Path(os.environ.get('CK3_MOD_DIR', str(
    Path.home() / 'Documents/Paradox Interactive/Crusader Kings III/mod'
))).expanduser()
