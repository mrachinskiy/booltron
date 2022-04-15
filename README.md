Booltron—super add-on for super fast booleans for Blender.

Features:

* Faster boolean operations with large number of objects.
* Destructive and non-destructive workflows.
* Works with Curve and Text objects.
* Various adjustment options to get better results from boolean operations.
* Checks for non-manifold.

**[Watch demo video.](https://youtu.be/KxbJSUQpw7I)**


How to install
==========================

1. Download [Booltron 2.7.0][v_latest].<sup>1</sup>
2. Make sure you have Blender 2.93 or newer.
3. Open `Preferences` → `Add-ons` category.
4. Use `Install` to install add-on from downloaded zip archive.<sup>2</sup>
5. Read [quick tips](#quick-tips).

<sup>1</sup> Note for mac users: Safari browser will automatically unpack downloaded zip archive, so in order to install the add-on, you have to pack folder with add-on files back into zip archive. Or use a different browser to download add-on.

<sup>2</sup> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

1. Загрузите [Booltron 2.7.0][v_latest].<sup>1</sup>
2. Убедитесь, что у вас установлен Blender 2.93 или новее.
3. Откройте `Preferences` → `Add-ons`.
4. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.<sup>2</sup>
5. Ознакомьтесь с [кратким руководством](#краткое-руководство).

<sup>1</sup> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, поэтому, чтобы установить аддон, необходимо запаковать папку с файлами аддона обратно в zip архив. Или используйте другой браузер для скачивания аддона.

<sup>2</sup> Если при активации аддона возникает ошибка, значит вы пытаетесь установить репозиторий вместо релиза. Для загрузки релиза используйте ссылку, приведённую в первом шаге данного руководства.


Quick tips
==========================

Destructive:

* Supports Text and Curve objects.
* `Ctrl + tool`: invoke tool settings popup before execution.
* `Alt + tool`: execute tool with `Keep Objects` setting enabled.

Non-destructive:

* Supports only Mesh objects.
* Unifies secondary boolean objects into one combined object for faster boolean operations.


Краткое руководство
==========================

Деструктивные:

* Поддерживают Text и Curve объекты.
* `Ctrl + инструмент`: вызвать всплывающее меню настроек инструмента перед его использованием.
* `Alt + инструмент`: использовать инструмент с настройкой `Сохранить объекты`.

Недеструктивные:

* Поддерживают только Mesh объекты.
* Объединяют вспомогательные булевы объекты в один комбинированный объект для более быстрых булевых операций.


Contributing
==========================

### Did you find a bug?

* Ensure the bug can be reproduced in the latest add-on version.
* If error occurs on add-on installation or activation you probably trying to install add-on repository instead of release, check [how to install](#how-to-install) guide for proper installation process.
* [Open new bug report][new_bug_report], be sure to include Blender and add-on versions, and screenshot showing the error message.


[v_latest]: https://github.com/mrachinskiy/booltron/releases/download/v2.7.0-blender2.93.0/booltron-2_7_0.zip
[new_bug_report]: https://github.com/mrachinskiy/booltron/issues/new?template=bug_report.md
