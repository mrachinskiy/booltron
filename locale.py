lc_main = {
	# Interface
	'Boolean Solver': 'Солвер',
	'Boolean Solver:': 'Солвер:',
	'Boolean Method': 'Метод',
	'Boolean Method:': 'Метод:',
	'Optimized': 'Оптимизированный',
	'Batch': 'Поочерёдный',
	'Batch + Mesh Cleanup': 'Поочерёдный + Mesh Cleanup',
	'Adjustments:': 'Корректировки:',
	'Correct Position': 'Коррекция Позиции',
	'Position Offset': 'Сдвиг Позиции',

	# Tooltips
	'Specify solver for boolean operations': 'Укажите солвер для булевских операций',
	'BMesh solver is faster, but less stable and cannot handle coplanar geometry': 'BMesh солвер быстрее, но менее стабилен и не работает с coplanar геометрией',
	'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry': 'Carve солвер медленнее, но более стабилен и работает с простыми случаями coplanar геометрии',
	'Specify boolean method for Union, Difference and Intersect tools (Intersect tool does not support optimized method and will use batch method instead)': 'Укажите метод для инструментов Union (Объединение), Difference (Разность) и Intersect (Пересечение); инструмент Intersect (Пересечение) не поддерживает оптимизированный метод и вместо него будет использовать поочерёдный метод',
	'A single boolean operation with all objects at once, fastest, but in certain cases gives unpredictable result': 'Одна булевская операция со всеми объектами сразу, наиболее быстрый метод, но в определённых случаях выдаёт непредсказуемый результат',
	'Boolean operation for each selected object one by one, much slower, but overall gives more predictable result': 'Булевская операция поочерёдно для каждого объекта, гораздо медленнее, но выдаёт более предсказуемый результат',
	'Perform mesh cleanup operation in between boolean operations, slowest, but gives better result in cases where simple batch method fails': 'Выполнять операцию mesh cleanup между булевскими операциями, наиболее медленный метод, но даёт лучший результат в случаях, где не справляется простой поочерёдный метод',
	'Triangulate geometry before boolean operation (in certain cases may improve result of a boolean operation)': 'Триангулировать геометрию перед булевской операцией (в некоторых случаях может улучшить результат булевских операций)',
	'Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)': 'Сдвинуть объекты на небольшое расстояние, чтобы избежать ошибок с coplanar геометрией во время булевских операций (не влияет на активный объект)',
	'Position offset is randomly generated for each object in range [-x, +x] input value': 'Сдвиг позиции генерируется в случайном порядке для каждого объекта в диапазоне [-x, +x] указанного значения',
	'Combine selected objects': 'Объединить выделенные объекты',
	'Subtract selected objects from active object': 'Вычесть выделенные объекты из активного объекта',
	'Keep the common part of all selected objects': 'Оставить общую часть всех выделенных объектов',
	'Slice active object along the volume of selected object': 'Разрезать активный объект по объёму выделенного объекта',
	"Subtract selected object from active object, subtracted object won't be removed": 'Вычесть выделенный объект из активного объекта, вычитаемый объект не будет удалён',

	# Reports
	'Not available on this version of Blender': 'Недоступно в этой версии Blender',
	'Boolean operation result is non-manifold': 'Результат булевской операции non-manifold',
	}

lc_btn = {
	'Union': 'Объединение',
	'Difference': 'Разность',
	'Intersect': 'Пересечение',
	'Slice': 'Разрезать',
	}


lc_ru = {}

for k, v in lc_main.items():
	lc_ru[('*', k)] = v

for k, v in lc_btn.items():
	lc_ru[('Operator', k)] = v


lc_reg = {'ru_RU': lc_ru}

del lc_main
del lc_btn
