# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy
from bpy.types import ImagePreview

from .. import var

_previews = {}
_cache = {}


def clear_previews() -> None:
    import bpy.utils.previews

    for pcoll in _previews.values():
        bpy.utils.previews.remove(pcoll)

    _previews.clear()
    _cache.clear()


def icon(name: str) -> int:
    return _icon(name, bpy.context.preferences.themes[0].user_interface.wcol_tool.inner[:])


def icon_menu(name: str) -> int:
    return _icon(name, bpy.context.preferences.themes[0].user_interface.wcol_menu_item.inner[:])


def _icon(name: str, color: tuple[float, ...]) -> int:
    if (iid := _cache.get((name, color))) is not None:
        return iid

    theme = "DARK" if _luma(color) < 0.5 else "LIGHT"
    iid = _cache[(name, color)] = _scan_icons("icons", var.ICONS_DIR)[theme + name].icon_id

    if len(_cache) > 30:
        del _cache[next(iter(_cache))]

    return iid


def _luma(rgb: tuple[float, float, float, ...]) -> float:
    r, g, b, *a = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _scan_icons(pcoll_name: str, folder: Path) -> dict[str, ImagePreview]:
    pcoll = _previews.get(pcoll_name)
    if pcoll is not None:
        return pcoll

    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    for child in folder.iterdir():
        if child.is_dir():
            for subchild in child.iterdir():
                if subchild.is_file() and subchild.suffix == ".png":
                    pname = child.name + subchild.stem
                    pcoll.load(pname.upper(), str(subchild), "IMAGE")

    _previews[pcoll_name] = pcoll
    return pcoll
