lc_main = {
	# Interface
	'Boolean Solver': 'Солвер',
	'Adjustments': 'Корректировки',
	'Correct Position': 'Коррекция Позиции',
	'Position Offset': 'Сдвиг Позиции',

	# Tooltips
	'Specify solver for boolean operations': 'Укажите солвер для булевских операций',
	'BMesh solver is faster, but less stable and cannot handle coplanar geometry': 'BMesh солвер быстрее, но менее стабильный и не справляется с coplanar геометрией',
	'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry': 'Carve солвер медленнее, но более стабильный и работает с простыми случаями coplanar геометрии',
	'Triangulate geometry before boolean operation (can sometimes improve result of a boolean operation)': 'Триангулировать геометрию перед булевской операцией (в некоторых случаях может улучшить результат булевских операций)',
	'Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)': 'Сдвинуть объекты на небольшое расстояние, чтобы избежать ошибок с coplanar геометрией во время булевских операций (не влияет на активный объект)',
	'Position offset is randomly generated for each object in range [-x, +x] input value': 'Сдвиг позиции генерируется в случайном порядке для каждого объекта в диапазоне [-x, +x] указанного значения',
	'Combine selected objects': 'Объединить выделенные объекты',
	'Subtract selected objects from active object': 'Вычесть выделенные объекты из активного объекта',
	'Keep the common part of all selected objects': 'Оставить общую часть всех выделенных объектов',
	'Slice active object along the volume of selected object': 'Разрезать активный объект по объёму выделенного объекта',
	"Subtract selected object from active object, subtracted object won't be removed": 'Вычесть выделенный объект из активного объекта, вычитаемый объект не будет удалён',

	# Reports
	'BMesh solver works only with Blender 2.78 or newer': 'BMesh солвер работает только с Blender 2.78 или новее',
	'Boolean operation result is non-manifold': 'Результат булевской операции non-manifold',
	}

lc_btn = {
	'Union': 'Объединение',
	'Difference': 'Разница',
	'Intersect': 'Пересечение',
	'Slice': 'Разрезать',
	}

lc_ru = {}

for k, v in lc_main.items():
	lc_ru[('*', k)] = v

for k, v in lc_btn.items():
	lc_ru[('Operator', k)] = v

lc_reg = {'ru_RU': lc_ru}
