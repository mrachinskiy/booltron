Booltron—super add-on for super fast booleans.

Features:

* Faster boolean operations with large number of objects.
* Destructive and non-destructive workflows.
* Works with Curve and Text objects.
* Various adjustment options to get better results from boolean operations.
* Checks for non-manifold.

**[Watch demo video.](https://youtu.be/KxbJSUQpw7I)**


How to install
==========================

1. Download the add-on:<sup>1</sup>
    * [**Blender 2.80** Booltron v2.4.2][v_latest]
    * [**Blender 2.79** Booltron v2.3.1][v_legacy]
2. Open `Preferences` → `Add-ons` category.
3. Use `Install` to install add-on from downloaded zip archive.
4. Read [quick tips](#quick-tips).

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, so in order to install the add-on, you have to pack folder with add-on files back into zip archive. Or use a different browser to download add-on.


Установка
==========================

1. Загрузите аддон:<sup>1</sup>
    * [**Blender 2.80** Booltron v2.4.2][v_latest]
    * [**Blender 2.79** Booltron v2.3.1][v_legacy]
2. Откройте `Preferences` → `Add-ons`.
3. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.
4. Ознакомьтесь с [советами](#советы).

<sup>1</sup> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, поэтому, чтобы установить аддон, необходимо запаковать папку с файлами аддона обратно в zip архив. Или используйте другой браузер для скачивания аддона.


Quick tips
==========================

Destructive:

* Supports Text and Curve objects.
* `Ctrl + tool`: invoke tool settings popup before execution.
* `Alt + tool`: execute tool with `Keep Objects` setting enabled.

Non-destructive:

* Supports Mesh only objects.
* Unifies secondary boolean objects into one combined object for faster boolean operations.


Советы
==========================

Деструктивные:

* Поддерживают Text и Curve объекты.
* `Ctrl + инструмент`: вызвать всплывающее меню настроек инструмента перед его использованием.
* `Alt + инструмент`: использовать инструмент с настройкой `Сохранить объекты`.

Недеструктивные:

* Поддерживают только Mesh объекты.
* Объединяют вспомогательные булевские объекты в один комбинированный объект для более быстрых булевых операций.


Contributing
==========================

### Did you find a bug?

* Ensure the bug can be reproduced in the latest add-on version.
* If error occurs on add-on installation or activation you probably trying to install add-on repository instead of release, check [how to install](#how-to-install) guide for proper installation process.
* [Open new bug report][new_bug_report], be sure to include Blender and add-on versions, and screenshot showing the error message.


[v_latest]: https://github.com/mrachinskiy/booltron/releases/download/v2.4.2/booltron-2_4_2.zip
[v_legacy]: https://github.com/mrachinskiy/booltron/releases/download/v2.3.1/booltron-2_3_1.zip
[new_bug_report]: https://github.com/mrachinskiy/booltron/issues/new?template=bug_report.md
