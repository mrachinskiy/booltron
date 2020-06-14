# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2020  Mikhail Rachinskiy
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
    "version": (2, 4, 2),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar",
    "description": "Super add-on for super fast booleans.",
    "wiki_url": "https://github.com/mrachinskiy/booltron#readme",
    "tracker_url": "https://github.com/mrachinskiy/booltron/issues",
    "category": "Object",
}


if "bpy" in locals():

    def walk(path, parent_dir=None):
        import importlib

        for entry in os.scandir(path):

            if entry.is_file() and entry.name.endswith(".py"):
                filename, _ = os.path.splitext(entry.name)
                is_init = filename == "__init__"

                if parent_dir:
                    module = parent_dir if is_init else f"{parent_dir}.{filename}"
                else:
                    if is_init:
                        continue
                    module = filename

                importlib.reload(eval(module))

            elif entry.is_dir() and not entry.name.startswith((".", "__")):
                dirname = f"{parent_dir}.{entry.name}" if parent_dir else entry.name
                walk(entry.path, parent_dir=dirname)

    walk(var.ADDON_DIR)

else:
    import os

    import bpy
    import bpy.utils.previews
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
    preferences.BooltronPreferences,
    preferences.WmProperties,
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
    mod_update.WM_OT_update_check,
    mod_update.WM_OT_update_download,
    mod_update.WM_OT_update_whats_new,
)


def register():
    if not os.path.exists(var.ICONS_DIR):
        integrity_check = FileNotFoundError("!!! READ INSTALLATION GUIDE !!!")
        raise integrity_check

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.booltron = PointerProperty(type=preferences.WmProperties)

    # Translations
    # ---------------------------

    for k, v in mod_update.dict_init().items():
        if k in localization.DICTIONARY.keys():
            localization.DICTIONARY[k].update(v)
        else:
            localization.DICTIONARY[k] = v

    bpy.app.translations.register(__name__, localization.DICTIONARY)

    # Previews
    # ---------------------------

    pcoll = bpy.utils.previews.new()

    for entry in os.scandir(var.ICONS_DIR):
        if entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith(".png"):
                    name = entry.name + os.path.splitext(subentry.name)[0]
                    pcoll.load(name.upper(), subentry.path, "IMAGE")

    var.preview_collections["icons"] = pcoll

    # mod_update
    # ---------------------------

    mod_update.init(
        addon_version=bl_info["version"],
        url_releases="https://api.github.com/repos/mrachinskiy/booltron/releases",
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.booltron

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
