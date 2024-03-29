# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

bl_info = {
    "name": "Booltron",
    "author": "Mikhail Rachinskiy",
    "version": (2, 8, 3),
    "blender": (3, 2, 0),
    "location": "3D View > Sidebar",
    "description": "Super add-on for super fast booleans.",
    "doc_url": "https://github.com/mrachinskiy/booltron#readme",
    "tracker_url": "https://github.com/mrachinskiy/booltron/issues",
    "category": "Object",
}


if "bpy" in locals():
    _essential.reload_recursive(var.ADDON_DIR, locals())
else:
    import bpy
    from bpy.props import PointerProperty

    from . import _essential, var

    _essential.check(var.ICONS_DIR, bl_info["blender"])

    from . import (
        localization,
        mod_update,
        preferences,
        ops_destructive,
        ops_nondestructive,
        ui,
    )


classes = (
    preferences.ToolPropsGroup,
    preferences.Preferences,
    preferences.WmProperties,
    preferences.SceneProperties,
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
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.booltron = PointerProperty(type=preferences.WmProperties)
    bpy.types.Scene.booltron = PointerProperty(type=preferences.SceneProperties)

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.append(ui.draw_booltron_menu)
    bpy.types.VIEW3D_MT_edit_mesh.append(ui.draw_booltron_menu)
    bpy.types.VIEW3D_MT_edit_curve.append(ui.draw_booltron_menu)

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
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.booltron
    del bpy.types.Scene.booltron

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.remove(ui.draw_booltron_menu)
    bpy.types.VIEW3D_MT_edit_mesh.remove(ui.draw_booltron_menu)
    bpy.types.VIEW3D_MT_edit_curve.remove(ui.draw_booltron_menu)

    # Translations
    # ---------------------------

    bpy.app.translations.unregister(__name__)

    # Previews
    # ---------------------------

    ui.clear_previews()


if __name__ == "__main__":
    register()
