import os, shutil, struct, io
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageOps

"""
Utility logic for Ingelmia Engine
"""

# Theme/UI colors

CYBER_BG = "#080B16"
CYBER_PANEL = "#101827"
CYBER_PANEL_2 = "#172235"
CYBER_TEXT = "#D7F8FF"
CYBER_MUTED = "#7CA6B8"
CYBER_ACCENT = "#55E6FF"
CYBER_ACCENT_2 = "#B06CFF"
CYBER_GOOD = "#58F29A"
CYBER_WARN = "#FFC857"
CYBER_BAD = "#FF5C8A"

LILAC = CYBER_BG
LILAC_RGB = (8, 11, 22)

SIGNATURE = b"\x47\x52\x45\x53"  # GRES
MOD_SIGNATURE = b"ATTMOD"
BACKUP_FOLDER = "Backups"
TAILDATA_V2_MAGIC = b"IGT2"
TAILDATA_V2_SIZE = 17  # magic(4), container_id(1), meta_offset(4), orig_off(4), orig_size(4)
TAILDATA_LEGACY_SIZE = 11  # container_id(1), meta_offset_low16(2), orig_off(4), orig_size(4)

LANGUAGES = {
    "en": {
        "app_title": "Ingelmia Engine",
        "subtitle": "Ascension/Valkyrie Toolkit",
        "choose_game": "Target Game",
        "choose_language": "Language",
        "game_folder": "Game Folder",
        "select_game_folder": "Select Game Folder",
        "select_game_folder_dialog": "Select the folder containing the game's PAK files",
        "ascension": "Ascension",
        "valkyrie": "Valkyrie",
        "english": "English",
        "russian": "Russian",
        "open_creator": "Open Mod Creator",
        "open_manager": "Open Mod Manager",
        "unpack": "Unpack PAK Files",
        "idle": "Idle",
        "ready": "Ready",
        "processing": "Processing",
        "complete": "Unpacking complete.",
        "missing": "Missing",
        "error": "Error",
        "status": "Status",
        "mod_manager": "Mod Manager",
        "mod_creator": "Mod Creator",
        "available_mods": "Available Mods",
        "author": "Author",
        "description": "Description",
        "apply_mod": "Apply Mod",
        "disable_mod": "Disable Mod",
        "disable_all": "Disable All Mods",
        "prev": "< Prev",
        "next": "Next >",
        "no_images": "No Images",
        "confirm_reset": "This will revert metadata and truncate containers to vanilla sizes. Proceed?",
        "add_image": "Add Image",
        "clear_images": "Clear Images",
        "preview_images": "Preview Images",
        "version": "Version",
        "mod_files": "Mod Files",
        "add_files": "Add Files",
        "clear_files": "Clear File List",
        "create_package": "Create Mod Package",
        "transfer_taildata": "Transfer Taildata",
        "warning_no_files": "No files added!",
    },
    "ru": {
        "app_title": "Ingelmia Engine",
        "subtitle": "Инструменты Ascension/Valkyrie",
        "choose_game": "Игра",
        "choose_language": "Язык",
        "game_folder": "Папка игры",
        "select_game_folder": "Выбрать папку игры",
        "select_game_folder_dialog": "Выберите папку с PAK файлами игры",
        "ascension": "Ascension",
        "valkyrie": "Valkyrie",
        "english": "Английский",
        "russian": "Русский",
        "open_creator": "Открыть создатель модов",
        "open_manager": "Открыть менеджер модов",
        "unpack": "Распаковать PAK файлы",
        "idle": "Ожидание",
        "ready": "Готово",
        "processing": "Обработка",
        "complete": "Распаковка завершена.",
        "missing": "Не найден",
        "error": "Ошибка",
        "status": "Статус",
        "mod_manager": "Менеджер модов",
        "mod_creator": "Создатель модов",
        "available_mods": "Доступные моды",
        "author": "Автор",
        "description": "Описание",
        "apply_mod": "Применить мод",
        "disable_mod": "Отключить мод",
        "disable_all": "Отключить все моды",
        "prev": "< Назад",
        "next": "Вперёд >",
        "no_images": "Нет изображений",
        "confirm_reset": "Это восстановит метаданные и обрежет контейнеры до исходных размеров. Продолжить?",
        "add_image": "Добавить изображение",
        "clear_images": "Очистить изображения",
        "preview_images": "Превью изображения",
        "version": "Версия",
        "mod_files": "Файлы мода",
        "add_files": "Добавить файлы",
        "clear_files": "Очистить список файлов",
        "create_package": "Создать пакет мода",
        "transfer_taildata": "Перенести Taildata",
        "warning_no_files": "Файлы не добавлены!",
    },
}


def tr(lang: str, key: str) -> str:
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, LANGUAGES["en"].get(key, key))


@dataclass(frozen=True)
class ContainerProfile:
    cid: int
    name: str
    output_folder: str
    vanilla_size: Optional[int] = None
    metadata_size: Optional[int] = None


@dataclass(frozen=True)
class GameProfile:
    key: str
    display_name: str
    title: str
    containers: Tuple[ContainerProfile, ...]
    entry_name_size: int = 0x80
    signature: bytes = SIGNATURE
    encoding: str = "ascii"

    @property
    def container_map(self) -> Dict[int, ContainerProfile]:
        return {c.cid: c for c in self.containers}


GAME_PROFILES: Dict[str, GameProfile] = {
    "ascension": GameProfile(
        key="ascension",
        display_name="Ascension",
        title="Ascension to the Throne",
        containers=(
            ContainerProfile(0, "Resource0.pak", "Pak0_Files", 1_241_888_384, 999_476),
            ContainerProfile(1, "Resource1.pak", "Pak1_Files", 91_153_649, 7_220),
        ),
    ),
    "valkyrie": GameProfile(
        key="valkyrie",
        display_name="Valkyrie",
        title="Valkyrie",
        containers=(
            ContainerProfile(0, "Resource0.pak", "Valkyrie_Pak0_Files", 1_289_661_958, 682_188),
            ContainerProfile(1, "Resource1.pak", "Valkyrie_Pak1_Files", 99_703_436, 124_860),
        ),
    ),
}


def get_profile(game_key: str) -> GameProfile:
    return GAME_PROFILES.get(game_key, GAME_PROFILES["ascension"])

def project_path(*parts: str) -> str:
    """
    Returns a path relative to the current working/project root
    """
    return os.path.join(os.getcwd(), *parts)


def game_path(game_folder: Optional[str], *parts: str) -> str:
    """
    Returns a path inside the selected game folder, falls back to project root if no folder was selected
    """
    base = game_folder or os.getcwd()
    return os.path.join(base, *parts)

def shorten_display_path(path: str, max_len: int = 70) -> str:
    path = os.path.normpath(path)
    if len(path) <= max_len:
        return path
    return "..." + path[-max_len:]

# Tk style helpers

def setup_lilac_styles(root):

    style = ttk.Style(master=root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Lilac.TFrame", background=CYBER_BG)
    style.configure("Lilac.TLabel", background=CYBER_BG, foreground=CYBER_TEXT, padding=0)
    style.configure("Cyber.TFrame", background=CYBER_BG)
    style.configure("CyberPanel.TFrame", background=CYBER_PANEL)
    style.configure("Cyber.TLabel", background=CYBER_BG, foreground=CYBER_TEXT)
    style.configure("CyberMuted.TLabel", background=CYBER_BG, foreground=CYBER_MUTED)
    style.configure("Cyber.TButton", background=CYBER_PANEL_2, foreground=CYBER_TEXT, borderwidth=0, focusthickness=0, padding=(12, 8))
    style.map("Cyber.TButton", background=[("active", CYBER_ACCENT_2)], foreground=[("active", "white")])
    style.configure("Cyber.Horizontal.TProgressbar", troughcolor=CYBER_PANEL, background=CYBER_ACCENT, bordercolor=CYBER_PANEL, lightcolor=CYBER_ACCENT, darkcolor=CYBER_ACCENT)
    return style


def apply_lilac_to_root(root) -> None:
    try:
        root.configure(bg=CYBER_BG)
    except Exception:
        pass


def resize_and_pad(image_path):
    with Image.open(image_path) as img:
        img = ImageOps.pad(img, (500, 500), color=LILAC_RGB, centering=(0.5, 0.5))
        return img

# Backups/Taildata

def ensure_backups(profile: GameProfile, game_folder: Optional[str] = None) -> None:
    os.makedirs(project_path(BACKUP_FOLDER), exist_ok=True)
    game_backup_folder = project_path(BACKUP_FOLDER, profile.key)
    os.makedirs(game_backup_folder, exist_ok=True)

    for container in profile.containers:
        source = game_path(game_folder, container.name)
        dest = os.path.join(game_backup_folder, container.name)

        if os.path.exists(source) and not os.path.exists(dest):
            try:
                shutil.copy2(source, dest)
            except Exception as e:
                messagebox.showerror("Backup Error", f"Failed to back up {source}: {e}")


def pack_taildata(container_id: int, meta_offset: int, file_offset: int, file_size: int) -> bytes:
    return TAILDATA_V2_MAGIC + struct.pack("<BIII", container_id, meta_offset, file_offset, file_size)


def unpack_taildata(file_data: bytes) -> Tuple[int, int, int, int, int]:
    """
    Returns container_id, meta_offset, original_offset, original_size, tail_size
    """
    if len(file_data) >= TAILDATA_V2_SIZE and file_data[-TAILDATA_V2_SIZE:-TAILDATA_V2_SIZE + 4] == TAILDATA_V2_MAGIC:
        cid, meta_offset, orig_off, orig_size = struct.unpack("<BIII", file_data[-13:])
        return cid, meta_offset, orig_off, orig_size, TAILDATA_V2_SIZE

    if len(file_data) >= TAILDATA_LEGACY_SIZE:
        cid, meta_offset_low, orig_off, orig_size = struct.unpack("<BHII", file_data[-TAILDATA_LEGACY_SIZE:])
        return cid, meta_offset_low, orig_off, orig_size, TAILDATA_LEGACY_SIZE

    raise ValueError("File does not contain valid Ingelmia taildata.")


class BackgroundUnpacker:
    def __init__(
        self,
        progress_callback: Optional[Callable] = None,
        profile: Optional[GameProfile] = None,
        game_folder: Optional[str] = None,
    ):
        self.progress_callback = progress_callback
        self.profile = profile or GAME_PROFILES["ascension"]
        self.game_folder = game_folder

    def unpack_all(self) -> None:
        ensure_backups(self.profile, self.game_folder)
        for container in self.profile.containers:
            self.unpack_resource(container)

    def unpack_resource(self, container: ContainerProfile) -> None:
        pak_path = game_path(self.game_folder, container.name)
        folder_name = project_path(container.output_folder)
        container_id = container.cid

        if not os.path.exists(pak_path):
            messagebox.showwarning("File Missing", f"Could not find {pak_path}. Select the folder containing the game's PAK files.")
            return

        os.makedirs(folder_name, exist_ok=True)

        with open(pak_path, "rb") as f:
            sig = f.read(4)
            if sig != self.profile.signature:
                raise ValueError(f"Invalid signature in {pak_path}: expected {self.profile.signature!r}, got {sig!r}")

            f.read(4)
            file_count = int.from_bytes(f.read(4), "little")

            for i in range(file_count):
                meta_offset = f.tell()
                filename_raw = f.read(self.profile.entry_name_size)
                clean_bytes = filename_raw.split(b"\x00", 1)[0]
                filename = clean_bytes.decode(self.profile.encoding, errors="ignore") or f"unnamed_{i:06d}.bin"
                file_offset = int.from_bytes(f.read(4), "little")
                file_size = int.from_bytes(f.read(4), "little")
                return_pos = f.tell()

                f.seek(file_offset)
                file_data = f.read(file_size)
                taildata = pack_taildata(container_id, meta_offset, file_offset, file_size)

                output_path = os.path.join(folder_name, filename)
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

                with open(output_path, "wb") as out:
                    out.write(file_data)
                    out.write(taildata)

                if self.progress_callback:
                    self.progress_callback(
                        i + 1,
                        file_count,
                        f"{container.name}: {shorten_display_path(filename)}",
                    )

                f.seek(return_pos)


class ModManagerLogic:
    def __init__(self, profile: Optional[GameProfile] = None, game_folder: Optional[str] = None):
        self.profile = profile or GAME_PROFILES["ascension"]
        self.game_folder = game_folder
        self.ledger_path = project_path(f"applied_mods_{self.profile.key}.txt")
        ensure_backups(self.profile, self.game_folder)

    @property
    def containers(self) -> Dict[int, str]:
        return {c.cid: game_path(self.game_folder, c.name) for c in self.profile.containers}

    def get_applied_mods(self) -> set:
        if not os.path.exists(self.ledger_path):
            return set()

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            mods = {line.strip() for line in f if line.strip()}

        existing_mods = {m for m in mods if os.path.exists(project_path("Mods", m))}
        if len(existing_mods) != len(mods):
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                for m in sorted(existing_mods):
                    f.write(f"{m}\n")
        return existing_mods

    def update_ledger(self, mod_name: str, add: bool = True) -> None:
        mods = self.get_applied_mods()
        if add:
            mods.add(mod_name)
        else:
            mods.discard(mod_name)
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            for m in sorted(mods):
                f.write(f"{m}\n")

    def get_mod_header(self, mod_path: str):
        with open(mod_path, "rb") as f:
            sig_len_raw = f.read(1)
            if not sig_len_raw:
                return None
            sig_len = int.from_bytes(sig_len_raw, "little")
            if f.read(sig_len) != MOD_SIGNATURE:
                return None

            file_count = int.from_bytes(f.read(4), "little")

            def read_prefixed_string(size_bytes):
                length = int.from_bytes(f.read(size_bytes), "little")
                return f.read(length).decode("utf-8", errors="ignore")

            meta = {
                "author": read_prefixed_string(1),
                "version": read_prefixed_string(1),
                "description": read_prefixed_string(2),
            }

            img_count = int.from_bytes(f.read(1), "little")
            images = []
            for _ in range(img_count):
                img_size = int.from_bytes(f.read(4), "little")
                images.append(f.read(img_size))

            return {"meta": meta, "images": images, "file_count": file_count}

    def calculate_payload_offset(self, f) -> int:
        f.seek(0)
        sig_len = int.from_bytes(f.read(1), "little")
        f.seek(sig_len, 1)
        f.seek(4, 1)  # file count
        for _ in range(2):
            f.seek(int.from_bytes(f.read(1), "little"), 1)
        f.seek(int.from_bytes(f.read(2), "little"), 1)
        img_count = int.from_bytes(f.read(1), "little")
        for _ in range(img_count):
            f.seek(int.from_bytes(f.read(4), "little"), 1)
        return f.tell()

    def apply_mod(self, mod_path: str):
        mod_name = os.path.basename(mod_path)
        header = self.get_mod_header(mod_path)
        if not header:
            return False, "Invalid Mod"

        with open(mod_path, "rb") as mod_f:
            mod_f.seek(self.calculate_payload_offset(mod_f))

            for _ in range(header["file_count"]):
                file_size = int.from_bytes(mod_f.read(4), "little")
                file_data = mod_f.read(file_size)
                cont_id, meta_offset, orig_off, orig_size, tail_size = unpack_taildata(file_data)
                target_pak = self.containers.get(cont_id)

                if not target_pak or not os.path.exists(target_pak):
                    return False, f"Missing container for id {cont_id}: {target_pak}"

                payload = file_data[:-tail_size]
                with open(target_pak, "r+b") as pak:
                    pak.seek(0, 2)
                    new_offset = pak.tell()
                    pak.write(payload)
                    pak.seek(meta_offset + self.profile.entry_name_size)
                    pak.write(struct.pack("<II", new_offset, len(payload)))

        self.update_ledger(mod_name, add=True)
        return True, "Mod Applied"

    def disable_mod(self, mod_path: str):
        mod_name = os.path.basename(mod_path)
        header = self.get_mod_header(mod_path)
        if not header:
            return False, "Invalid Mod"

        with open(mod_path, "rb") as mod_f:
            mod_f.seek(self.calculate_payload_offset(mod_f))
            for _ in range(header["file_count"]):
                file_size = int.from_bytes(mod_f.read(4), "little")
                file_data = mod_f.read(file_size)
                cont_id, meta_offset, orig_off, orig_size, _tail_size = unpack_taildata(file_data)
                target_pak = self.containers.get(cont_id)
                if not target_pak or not os.path.exists(target_pak):
                    return False, f"Missing container for id {cont_id}: {target_pak}"
                with open(target_pak, "r+b") as pak:
                    pak.seek(meta_offset + self.profile.entry_name_size)
                    pak.write(struct.pack("<II", orig_off, orig_size))

        self.update_ledger(mod_name, add=False)
        return True, "Mod Disabled"

    def disable_all(self):
        game_backup_folder = project_path(BACKUP_FOLDER, self.profile.key)

        for container in self.profile.containers:
            backup_path = os.path.join(game_backup_folder, container.name)

            if not os.path.exists(backup_path):
                messagebox.showerror("Error", f"Backup not found for {container.name}. Cannot restore original metadata.")
                continue

            target_container = game_path(self.game_folder, container.name)

            if not os.path.exists(target_container):
                continue

            if container.metadata_size is None or container.vanilla_size is None:
                messagebox.showwarning(
                    "Profile Incomplete",
                    f"{self.profile.display_name} profile needs metadata_size and vanilla_size for {container.name} before Disable All can truncate safely.",
                )
                continue

            try:
                with open(backup_path, "rb") as bf:
                    original_meta = bf.read(container.metadata_size)
                with open(target_container, "r+b") as f:
                    f.seek(0)
                    f.write(original_meta)
                    f.truncate(container.vanilla_size)
            except Exception as e:
                messagebox.showerror("Hard Reset Failed", f"Failed to restore {container.name}: {e}")
                return False, str(e)

        if os.path.exists(self.ledger_path):
            os.remove(self.ledger_path)

        return True, "All mods cleared. Metadata and file sizes restored where profile sizes were available."


class ModPacker:
    def validate_taildata(self, file_path: str) -> bool:
        if os.path.getsize(file_path) < TAILDATA_LEGACY_SIZE:
            return False
        with open(file_path, "rb") as f:
            data = f.read()
        try:
            unpack_taildata(data)
            return True
        except Exception:
            return False

    def transfer_taildata(self, target_path: str, source_path: str):
        try:
            if not os.path.exists(source_path):
                return False, f"Source missing: {os.path.basename(source_path)}"
            with open(source_path, "rb") as s:
                data = s.read()
            _cid, _meta, _off, _size, tail_size = unpack_taildata(data)
            taildata = data[-tail_size:]
            with open(target_path, "ab") as t:
                t.write(taildata)
            return True, "OK"
        except Exception as e:
            return False, str(e)

    def create_package(self, meta, files: Iterable[str], output_path: str, image_paths: List[str] = None):
        image_paths = image_paths or []
        try:
            with open(output_path, "wb") as f:
                f.write(len(MOD_SIGNATURE).to_bytes(1, "little"))
                f.write(MOD_SIGNATURE)
                files = list(files)
                f.write(len(files).to_bytes(4, "little"))

                author_bytes = meta.get("author", "").encode("utf-8")[:255]
                f.write(len(author_bytes).to_bytes(1, "little"))
                f.write(author_bytes)

                ver_bytes = meta.get("version", "").encode("utf-8")[:255]
                f.write(len(ver_bytes).to_bytes(1, "little"))
                f.write(ver_bytes)

                desc_bytes = meta.get("description", "").encode("utf-8")[:65535]
                f.write(len(desc_bytes).to_bytes(2, "little"))
                f.write(desc_bytes)

                valid_image_paths = image_paths[:5]
                f.write(len(valid_image_paths).to_bytes(1, "little"))

                for img_p in valid_image_paths:
                    if not os.path.exists(img_p):
                        continue
                    try:
                        with Image.open(img_p) as img:
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img = ImageOps.pad(img, (500, 500), color=LILAC_RGB)
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format="JPEG", quality=85)
                            img_data = img_byte_arr.getvalue()
                            f.write(len(img_data).to_bytes(4, "little"))
                            f.write(img_data)
                    except Exception as e:
                        print(f"Skipping image {img_p}: {e}")

                for file_path in files:
                    if not self.validate_taildata(file_path):
                        print(f"Warning: {os.path.basename(file_path)} does not contain valid Ingelmia taildata.")
                    size = os.path.getsize(file_path)
                    f.write(size.to_bytes(4, "little"))
                    with open(file_path, "rb") as source:
                        shutil.copyfileobj(source, f)

            return True, f"Successfully created {os.path.basename(output_path)}"
        except Exception as e:
            return False, str(e)
