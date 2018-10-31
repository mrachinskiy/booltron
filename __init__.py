# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2014-2018  Mikhail Rachinskiy
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
    "version": (2, 2, 0),
    "blender": (2, 76, 0),
    "location": "3D View > Tool Shelf",
    "description": "Super add-on for super fast booleans.",
    "wiki_url": "https://github.com/mrachinskiy/booltron#readme",
    "tracker_url": "https://github.com/mrachinskiy/booltron/issues",
    "category": "Object",
}


if "bpy" in locals():
    import importlib

    importlib.reload(versioning)
    importlib.reload(translations)
    importlib.reload(preferences)
    importlib.reload(mesh_utils)
    importlib.reload(boolean_methods)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    import os

    import bpy
    import bpy.utils.previews

    from . import translations, preferences, operators, ui, addon_updater_ops


classes = (
    preferences.BooltronPreferences,
    ui.VIEW3D_PT_booltron_update,
    ui.VIEW3D_PT_booltron_options,
    ui.VIEW3D_PT_booltron_tools,
    operators.OBJECT_OT_booltron_union,
    operators.OBJECT_OT_booltron_difference,
    operators.OBJECT_OT_booltron_intersect,
    operators.OBJECT_OT_booltron_slice,
)


def register():
    addon_updater_ops.register(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.translations.register(__name__, translations.DICTIONARY)

    # Previews
    # ---------------------------

    ADDON_DIR = os.path.dirname(__file__)
    ICONS_DIR = os.path.join(ADDON_DIR, "icons")

    pcoll = bpy.utils.previews.new()

    for entry in os.scandir(ICONS_DIR):

        if entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            pcoll.load(name, entry.path, "IMAGE")

    ui.preview_collections["icons"] = pcoll


def unregister():
    addon_updater_ops.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(__name__)

    # Previews
    # ---------------------------

    for pcoll in ui.preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    ui.preview_collections.clear()


if __name__ == "__main__":
    register()
