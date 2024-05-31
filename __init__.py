# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    _essential.reload_recursive(var.ADDON_DIR, locals())
else:
    import bpy
    from bpy.props import PointerProperty

    from . import _essential, var

    _essential.check(var.ICONS_DIR)

    from . import (localization, ops_destructive, ops_nondestructive,
                   preferences, ui)


classes = (
    preferences.ToolPropsGroup,
    preferences.Preferences,
    preferences.WmProperties,
    preferences.SceneProperties,
    ui.VIEW3D_MT_booltron,
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
