# SPDX-FileCopyrightText: 2014-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path


ADDON_ID = __package__
ADDON_DIR = Path(__file__).parent
ICONS_DIR = ADDON_DIR / "assets" / "icons"
ASSET_NODES_FILEPATH = ADDON_DIR / "assets" / "nodes.blend"
