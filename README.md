# Ingelmia Engine Info

Ingelmia Engine is a modern modding Toolkit for Ascension To The Throne and the sequel Valkyrie that comes with a GUI for each tool. Ingelmia Engine currently supports unpacking the PAK containers, mod creation with the Mod Creator, and comes with a Mod Manager for applying mods to the containers/disabling mods. Repacking PAK containers to apply mods is no longer needed, Ingelmia Engine will apply mods you make by appending them to the PAK container files. The toolkit also backsup your original PAK containers so that nothing is lost. The toolkit will create the Backups and Mods folder.

Part of the new design is an option to switch between English and Russian for the GUI since the modding community for these games primarily speaks English or Russian.

# What is needed to use Ingelmia Engine

Python 3 installed as well as Pillow. Pillow is an imaging library. To install pillow, open a command prompt and type the command `pip install pillow` , then press enter.

Once you have those installed, place the tools in the game's directory and double click main.pyw or call the script in a command prompt if you prefer. I'd just double click main.pyw, as long as you have python 3 installed then all you have to do is double click main.pyw to run the toolkit. Main.pyw calls the scripts within Ingelmia_Logic as needed, the user (you) only needs to use main.pyw.

# Ingelmia Engine's main GUI

This functions as the main hub you will see before using whatever tool you're needing. As of the current version the tools are Unpacking, Mod Creator, and Mod Manager.

<img width="915" height="647" alt="ing3" src="https://github.com/user-attachments/assets/d151c21c-4072-44de-ad82-5712ae73914c" />

<img width="920" height="649" alt="ing4" src="https://github.com/user-attachments/assets/4846e499-2c62-4658-a2a4-955b71d4bff7" />

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

# Extra Info

Ingelmia Engine is a referrence to Ingelmia from the mecha anime Argevollen, rad anime!
