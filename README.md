# Ingelmia Engine Info

Ingelmia Engine is a modern modding Toolkit for Ascension To The Throne and the sequel Valkyrie that comes with a GUI for each tool. Ingelmia Engine currently supports unpacking the PAK containers, mod creation with the Mod Creator, and comes with a Mod Manager for applying mods to the containers/disabling mods. Repacking PAK containers to apply mods is no longer needed, Ingelmia Engine will apply mods you make by appending them to the PAK container files. The toolkit also backsup your original PAK containers so that nothing is lost. The toolkit will create the Backups and Mods folder.

Part of the new design is an option to switch between English and Russian for the GUI since the modding community for these games primarily speaks English or Russian.

# What is needed to use Ingelmia Engine

Python 3 installed as well as Pillow. Pillow is an imaging library. To install pillow, open a command prompt and type the command `pip install pillow` , then press enter.

Once you have those installed, place the tools in the game's directory and double click main.pyw or call the script in a command prompt if you prefer. I'd just double click main.pyw, as long as you have python 3 installed then all you have to do is double click main.pyw to run the toolkit. Main.pyw calls the scripts within Ingelmia_Logic as needed, the user (you) only needs to use main.pyw.

# Ingelmia Engine's main GUI

This functions as the main hub you will see before using whatever tool you're needing. As of the current version the tools are Unpacking, Mod Creator, and Mod Manager.

<img width="917" height="648" alt="new1" src="https://github.com/user-attachments/assets/cfa618f8-6b47-40ab-aa8a-78c857e610a2" />

<img width="920" height="650" alt="new2" src="https://github.com/user-attachments/assets/fbbb8b66-970b-4438-9ade-428e717ed62e" />

# Mod Creator

Mod Creator is a GUI tool that turns files you mod (i.e., texture mods, xml mods, model mods, sound mods, etc mods) into a custom mod format (.attmod) I designed to be used with the Mod Manager. You enter metadata like author of the mod, version of mod, description of the mod, etc. You can also select up to 5 preview images to be displayed with your mod by the Mod Manager. It also includes a Transfer Taildata button that is meant to help you transfer taildata from the original files to new files you created. Review Taildata section for better understanding transfer taildata button.

<img width="619" height="794" alt="ing5" src="https://github.com/user-attachments/assets/ff9a8c3d-75e3-4510-9226-a2a7bd10ce15" />

<img width="617" height="792" alt="ing6" src="https://github.com/user-attachments/assets/64339c20-61ec-493d-85fc-931f6223c985" />

# Mod Manager

Mod Manager is a GUI tool that handles mod applying/disabling but has some fancy features to make it pleasant to use. It displays all valid mods (.attmod files created by Mod Creator)) within the Mods folder, allows selecting which mods to apply/disable, displays the mod's metadata (author, version, description, and preview images of the mod), tracks currently enabled mods, and ensures mods applied are displayed differently from mods not enabled by coloring the name of the mods enabled purple and assigning an asterisk prefix. Disable all mods button will truncate modded PAK containers to their original size and apply the original metadata from the unmodded PAK containers stored in Backups folder. So essentially, disable all mods button ensures if you want all file mods disabled it not only disables them but reverts the PAK containers to the original unmodded versions.

<img width="1149" height="777" alt="ing7" src="https://github.com/user-attachments/assets/713614df-b1a9-49ad-9acb-00bf9bd99ebb" />

<img width="1151" height="781" alt="ing8" src="https://github.com/user-attachments/assets/12e336f1-2cc8-421e-9262-5efa89696fb9" />

# Taildata section

Taildata for Ingelmia Engine is 11 bytes of metadata for Ascension to the throne and 17 bytes for Valkyrie applied to the end of each unpacked file. The reason taildata is created is to ensure mods are safely and properly applied to the PAK containers without ever shifting the original file data (an inefficient method in ascension to the throne's case, it's something that you'd have to do if you wanted to repack containers instead of appending). By appending mods to the end of the container and only updating the metadata sections in PAK containers, original file data is never lost. Ingelmia Engine does not rebuild PAK containers because it's an old and inefficient way to apply mods. Instead it relies on taildata created by the toolkit. It's essential you don't remove/alter the taildata of unpacked files unless you know what you're doing. Files having taildata does not impact modding/viewing of said files.

To explain the purpose of the transfer taildata button, it's meant to transfer taildata for you if your mods are new files. For example, let's say you wanted to mod a texture in gimp or something else if not texture modding. Gimp/said software would create a new file but without the taildata. So to ensure you don't lose taildata and can safely apply/disable mods, you select files lacking taildata and then select the original files that have the taildata that you're modding (i.e., buttonsmainmenu1.tga being the new texture modded file created from exporting with gimp while buttonsmainmenu.tga is the original unmodded texture, you'd use transfer taildata button to ensure the new file has the taildata from the original).

# Batch Update Files

Batch Update Files button is for if you need many files to have taildata. For example, let's say you created 40 new textures and want to replace the game's 40 texture images. Click Batch Update Files button, select the folder that has files that need taildata (what you're using to replace the game's files), select the folder that contains the game's unpacked files you're replacing, and then the tool will tell you if the new files were updated. After that, use Mod Creator to turn your new files into a packaged mod. The transfer taildata button in Mod Creator doesn't need to be used if you used the Batch Update Files button, transfer taildata button is only needed if all you need is 1 file to have taildata.

# Extra Info

Ingelmia Engine is a referrence to Ingelmia from the mecha anime Argevollen, rad anime!

# Russian Translation/Guide

# Информация об Ingelmia Engine

Ingelmia Engine — это современный набор инструментов для моддинга Ascension To The Throne и его сиквела Valkyrie. Каждый инструмент имеет собственный GUI. На данный момент Ingelmia Engine поддерживает распаковку PAK-контейнеров, создание модов через Mod Creator, а также включает Mod Manager для применения модов к контейнерам и отключения модов.

Для применения модов больше не нужно перепаковывать PAK-контейнеры. Ingelmia Engine применяет созданные вами моды, добавляя их в конец PAK-файлов. Инструмент также создаёт резервные копии оригинальных PAK-контейнеров, чтобы данные не были потеряны. При работе Ingelmia Engine создаёт папки Backups и Mods.

Часть нового дизайна — возможность переключать язык GUI между английским и русским, так как сообщество моддеров этих игр в основном говорит на английском или русском.

# Что нужно для использования Ingelmia Engine

Необходимо установить Python 3 и Pillow. Pillow — это библиотека для работы с изображениями. Чтобы установить Pillow, откройте командную строку, введите команду `pip install pillow`, затем нажмите Enter.

После установки поместите инструменты в папку игры и дважды щёлкните по `main.pyw`. Также можно запустить скрипт через командную строку, если вам так удобнее. Проще всего просто дважды щёлкнуть `main.pyw`: если Python 3 установлен, этого достаточно для запуска набора инструментов. `main.pyw` вызывает нужные скрипты из папки `Ingelmia_Logic`, а пользователю нужно запускать только `main.pyw`.

# Главное окно Ingelmia Engine

Это главный центр управления, который вы увидите перед использованием нужного инструмента. В текущей версии доступны инструменты для распаковки, Mod Creator и Mod Manager.

# Mod Creator

Mod Creator — это GUI-инструмент, который превращает изменённые вами файлы, например текстуры, XML-файлы, модели, звуки и другие модификации, в специальный формат модов `.attmod`, разработанный для использования с Mod Manager.

Вы можете указать метаданные: автора мода, версию мода, описание и другую информацию. Также можно выбрать до 5 изображений предпросмотра, которые будут отображаться в Mod Manager вместе с вашим модом.

В Mod Creator также есть кнопка Transfer Taildata. Она нужна для переноса taildata из оригинальных файлов в новые файлы, которые вы создали. Для лучшего понимания этой функции смотрите раздел Taildata.

# Mod Manager

Mod Manager — это GUI-инструмент для применения и отключения модов. В нём также есть удобные функции, которые делают работу с модами приятнее.

Он отображает все действительные моды, то есть `.attmod` файлы, созданные через Mod Creator, находящиеся в папке Mods. С его помощью можно выбирать, какие моды применять или отключать. Mod Manager показывает метаданные мода: автора, версию, описание и изображения предпросмотра. Он также отслеживает включённые моды и визуально отличает применённые моды от отключённых: у активных модов имя выделяется фиолетовым цветом и получает префикс со звёздочкой.

Кнопка Disable All Mods обрезает изменённые PAK-контейнеры до их оригинального размера и восстанавливает оригинальные метаданные из неизменённых PAK-контейнеров, сохранённых в папке Backups. По сути, эта кнопка не только отключает все файловые моды, но и возвращает PAK-контейнеры к оригинальному неизменённому состоянию.

# Раздел Taildata

Taildata в Ingelmia Engine — это служебные метаданные, добавляемые в конец каждого распакованного файла. Для Ascension To The Throne размер taildata составляет 11 байт, а для Valkyrie — 17 байт.

Taildata создаётся для того, чтобы моды можно было безопасно и корректно применять к PAK-контейнерам, не сдвигая оригинальные данные файлов внутри контейнера. В случае Ascension To The Throne сдвиг оригинальных данных был бы неэффективным методом, который понадобился бы при перепаковке контейнеров вместо добавления данных в конец.

Так как моды добавляются в конец контейнера, а в самом PAK-контейнере обновляются только секции метаданных, оригинальные данные файлов не теряются. Ingelmia Engine не пересобирает PAK-контейнеры, потому что это старый и неэффективный способ применения модов. Вместо этого инструмент использует taildata, созданную при распаковке.

Важно не удалять и не изменять taildata у распакованных файлов, если вы не уверены в том, что делаете. Наличие taildata не мешает моддингу, просмотру или редактированию этих файлов.

Кнопка Transfer Taildata нужна для переноса taildata в новые файлы. Например, если вы хотите изменить текстуру в GIMP или другой программе, экспортированный файл будет новым и не будет содержать taildata. Чтобы не потерять taildata и иметь возможность безопасно применять и отключать моды, выберите файл без taildata, а затем выберите оригинальный файл, из которого был сделан мод и в котором taildata уже есть.

Например, `buttonsmainmenu1.tga` может быть новой изменённой текстурой, экспортированной из GIMP, а `buttonsmainmenu.tga` — оригинальной неизменённой текстурой. В таком случае кнопка Transfer Taildata позволит перенести taildata из оригинального файла в новый файл.

# Пакетное обновление файлов

Кнопка «Пакетное обновление файлов» (Batch Update Files) предназначена для случаев, когда вам необходимо добавить «taildata» сразу во множество файлов. Например, предположим, вы создали 40 новых текстур и хотите заменить ими 40 текстурных изображений в игре. Нажмите кнопку «Пакетное обновление файлов», выберите папку с файлами, требующими добавления taildata (теми, которые вы используете для замены игровых файлов), затем выберите папку, содержащую распакованные игровые файлы, которые вы заменяете; после этого инструмент сообщит вам, были ли новые файлы успешно обновлены. Затем используйте Mod Creator, чтобы преобразовать ваши новые файлы в готовый пакет модификации. Кнопку «Перенос taildata» (Transfer taildata) в Mod Creator использовать не нужно, если вы уже воспользовались функцией пакетного обновления; эта кнопка требуется лишь в тех случаях, когда вам необходимо добавить taildata только в один-единственный файл.

# Дополнительная информация

Название Ingelmia Engine — это отсылка к Ингельмии из меха-аниме Argevollen. Отличное аниме!
