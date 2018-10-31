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


_ru = {
    "*": {
        # Interface
        "Boolean Solver": "Солвер",
        "Correct Position": "Коррекция Позиции",
        "Position Offset": "Сдвиг Позиции",
        "Keep Objects": "Сохранить Объекты",
        # Tooltips
        "Specify solver for boolean operations": "Укажите солвер для булевских операций",
        "BMesh solver is faster, but less stable and cannot handle coplanar geometry": "BMesh солвер быстрее, но менее стабилен и не работает с coplanar геометрией",
        "Carve solver is slower, but more stable and can handle simple cases of coplanar geometry": "Carve солвер медленнее, но более стабилен и работает с простыми случаями coplanar геометрии",
        "Perform mesh cleanup in between boolean operations, enabling this option will greatly affect performance of a boolean operation": "Выполнять mesh cleanup между булевскими операциями, включение этой опции значительно повлияет на производительность булевской операции",
        "Triangulate geometry before boolean operation, in some cases may improve result of a boolean operation": "Триангулировать геометрию перед булевской операцией, в некоторых случаях может улучшить результат булевских операций",
        "Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)": "Сдвинуть объекты на небольшое расстояние, чтобы избежать ошибок с coplanar геометрией во время булевских операций (не влияет на активный объект)",
        "Position offset is randomly generated for each object in range [-x, +x] input value": "Сдвиг позиции генерируется в случайном порядке для каждого объекта в диапазоне [-x, +x] указанного значения",
        "Combine selected objects": "Объединить выделенные объекты",
        "Subtract selected objects from active object": "Вычесть выделенные объекты из активного объекта",
        "Keep the common part of all selected objects": "Оставить общую часть всех выделенных объектов",
        "Slice active object along the volume of selected objects": "Разрезать активный объект по объёму выделенных объектов",
        "Do not remove selected objects after boolean operation (Shortcut: hold Alt when using the tool)": "Не удалять выделенные объекты после булевской операции (Горячая клавиша: удерживайте клавишу Alt при использовании инструмента)",
        # Reports
        "Boolean operation result is non-manifold": "Результат булевской операции non-manifold",
        "At least two objects must be selected": "Как минимум два объекта должны быть выделены",
    },
    "Operator": {
        "Union": "Объединение",
        "Difference": "Разность",
        "Intersect": "Пересечение",
        "Slice": "Разрезать",
    },
}


# Translation dictionary
# -----------------------------


def translation_dict(x):
    d = {}

    for ctxt, msgs in x.items():

        for msg_key, msg_translation in msgs.items():
            d[(ctxt, msg_key)] = msg_translation

    return d


DICTIONARY = {"ru_RU": translation_dict(_ru)}

del _ru
