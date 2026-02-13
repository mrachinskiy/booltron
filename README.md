Booltron—super add-on for superfast booleans for Blender.

:tv: **[Watch Demo VHS](https://youtu.be/3C_hsqLzBcI)**

Features:

* Faster boolean operations with large number of objects.
* Destructive and non-destructive workflows.
* Works with Curve and Text objects.
* Bake modifier result.
* Various adjustment options to get better results from boolean operations.
* Checks for non-manifold.
* Translated to multiple languages:
  * ![100%](https://geps.dev/progress/100) English
  * ![100%](https://geps.dev/progress/100) Russian
  * ![97%](https://geps.dev/progress/97) Spanish
  * ![85%](https://geps.dev/progress/85) French
  * Your language is missing or incomplete? [Contribute translation](#translations).


How to install
==========================

### Available as an [extension](https://extensions.blender.org/add-ons/booltron/)

<details>
  <summary>For Blender 4.1 or older</summary>

  1. Download [Booltron 2.9.0][v2_9_0]
  2. Make sure you have Blender 3.2 or newer.
  3. Open `Preferences` → `Add-ons` category.
  4. Use `Install` to install add-on from downloaded zip archive.
</details>

> [!NOTE]
> For mac users: Safari browser will automatically unpack downloaded zip archive, to prevent that go `Safari` → `Preferences` → `General` and uncheck `Open "safe" files after downloading` option.

> [!WARNING]
> If error occurs on add-on activation, it means you are trying to install add-on repository instead of release. Make sure you download add-on release using link provided in step one of this guide.


Установка
==========================

### Доступно как [расширение](https://extensions.blender.org/add-ons/booltron/)

<details>
  <summary>Для Blender 4.1 или старше</summary>

  1. Загрузите [Booltron 2.9.0][v2_9_0]
  2. Убедитесь, что у вас установлен Blender 3.2 или новее.
  3. Откройте `Preferences` → `Add-ons`
  4. Воспользуйтесь `Install` чтобы установить аддон из загруженного архива.
</details>

> [!NOTE]
> Примечание для пользователей mac: браузер Safari автоматически распаковывает скачиваемые zip архивы, чтобы это предотвратить в настройках `Safari` → `Preferences` → `General` отключите опцию `Open "safe" files after downloading`.

> [!WARNING]
> Если при активации аддона возникает ошибка, значит вы пытаетесь установить репозиторий вместо релиза. Для загрузки релиза используйте ссылку, приведённую в первом шаге данного руководства.


Contributing
==========================

### Did you find a bug?

* Ensure the bug can be reproduced in the latest add-on version.
* [Open new bug report][submit_issue], be sure to include Blender and add-on versions, and screenshot showing the error message.

### Translations

* It is advised that you use a dedicated `.po` editor like [Poedit](https://poedit.net).
  * To create new transltation in Poedit use `File` → `New from POT/PO file`, then pick `.po` file from add-on `localization` folder (doesn't matter which one).
  * To complete existing transltation in Poedit use `File` → `Open`, then pick `.po` file for specific language from add-on `localization` folder.
* After translation is done submit it back through [issues][submit_issue].

> [!TIP]
> * The UI convention for English language is to use Title Case formatting for property names and button titles, to know formatting convention for your language just see how Blender handles it and follow the rule.
> * Preserve empty braces `{}` in translation, they used as placeholders for additional information and will not appear in UI.


[v2_9_0]: https://github.com/mrachinskiy/booltron/releases/download/v2.9.0-blender3.2.0/booltron-2_9_0.zip
[submit_issue]: https://github.com/mrachinskiy/booltron/issues
