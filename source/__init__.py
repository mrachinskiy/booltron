# SPDX-FileCopyrightText: 2014-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    from . import var
    essentials.reload_recursive(var.ADDON_DIR, locals())  # noqa: F821
else:
    import bpy
    from bpy.props import PointerProperty

    from . import localization, operators, preferences, ui
    from .lib import essentials


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
    from .lib import previewlib

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

    previewlib.clear_previews()


if __name__ == "__main__":
    register()
