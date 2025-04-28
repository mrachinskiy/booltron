# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    essentials.reload_recursive(var.ADDON_DIR, locals())
else:
    from . import var
    from .lib import essentials

    essentials.check_integrity(var.ICONS_DIR)

    import bpy
    from bpy.props import PointerProperty

    from . import localization, operators, preferences, ui


classes = essentials.get_classes((preferences, ui, operators))


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
