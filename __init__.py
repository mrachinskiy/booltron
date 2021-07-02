# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2021  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Booltron",
    "author": "Mikhail Rachinskiy",
    "version": (2, 6, 1),
    "blender": (2, 90, 0),
    "location": "3D View > Sidebar",
    "description": "Super add-on for super fast booleans.",
    "doc_url": "https://github.com/mrachinskiy/booltron#readme",
    "tracker_url": "https://github.com/mrachinskiy/booltron/issues",
    "category": "Object",
}


if "bpy" in locals():
    from types import ModuleType
    from pathlib import Path


    def reload_recursive(path: Path, mods: dict[str, ModuleType]) -> None:
        import importlib

        for child in path.iterdir():

            if child.is_file() and child.suffix == ".py" and not child.name.startswith("__") and child.stem in mods:
                importlib.reload(mods[child.stem])

            elif child.is_dir() and not child.name.startswith((".", "__")):

                if child.name in mods:
                    reload_recursive(child, mods[child.name].__dict__)
                    importlib.reload(mods[child.name])
                    continue

                reload_recursive(child, mods)


    reload_recursive(var.ADDON_DIR, locals())
else:
    import bpy
    from bpy.props import PointerProperty

    from . import (
        localization,
        preferences,
        ops_destructive,
        ops_nondestructive,
        ui,
        var,
        mod_update,
    )


classes = (
    preferences.Preferences,
    preferences.WmProperties,
    ui.VIEW3D_MT_booltron,
    ui.VIEW3D_PT_booltron_update,
    ui.VIEW3D_PT_booltron_destructive,
    ui.VIEW3D_PT_booltron_nondestructive,
    ops_destructive.OBJECT_OT_destructive_union,
    ops_destructive.OBJECT_OT_destructive_difference,
    ops_destructive.OBJECT_OT_destructive_intersect,
    ops_destructive.OBJECT_OT_destructive_slice,
    ops_nondestructive.OBJECT_OT_nondestructive_union,
    ops_nondestructive.OBJECT_OT_nondestructive_difference,
    ops_nondestructive.OBJECT_OT_nondestructive_intersect,
    ops_nondestructive.OBJECT_OT_nondestructive_remove,
    *mod_update.ops,
)


def register():
    if not var.ICONS_DIR.exists():
        integrity_check = FileNotFoundError("!!! READ INSTALLATION GUIDE !!!")
        raise integrity_check

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.booltron = PointerProperty(type=preferences.WmProperties)

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.append(ui.draw_booltron_menu)

    # mod_update
    # ---------------------------

    mod_update.init(
        addon_version=bl_info["version"],
        repo_url="mrachinskiy/booltron",
    )

    # Translations
    # ---------------------------

    bpy.app.translations.register(__name__, localization.DICTIONARY)


def unregister():
    import bpy.utils.previews

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.booltron

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.remove(ui.draw_booltron_menu)

    # Translations
    # ---------------------------

    bpy.app.translations.unregister(__name__)

    # Previews
    # ---------------------------

    for pcoll in var.preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    var.preview_collections.clear()


if __name__ == "__main__":
    register()
