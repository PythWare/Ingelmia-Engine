import os, shutil, struct, io
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageOps

"""
This script handles the utility logic such as unpacking, mod creation, etc
"""

LILAC = "#C8A2C8"
SIGNATURE = b'\x47\x52\x45\x53'
MOD_SIGNATURE = b'ATTMOD'       # For Mod Packages
BACKUP_FOLDER = "Backups"
LILAC_RGB = (200, 162, 200) # #C8A2C8 in RGB

# used for truncating, disabling all mods to be precise
PAK0_SIZE = 1_241_888_384
PAK1_SIZE = 91_153_649

# used during truncating, revering metadata to original values by grabbing the data from Backups
PAK0_METADATA_SIZE = 999_476
PAK1_METADATA_SIZE = 7_220

def ensure_backups():
    """
    Creates a Backups folder and copies original game containers
    """
    
    containers = ["Resource0.pak", "Resource1.pak"]
    
    if not os.path.exists(BACKUP_FOLDER):
        try:
            os.makedirs(BACKUP_FOLDER)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Could not create Backup folder: {e}")
            return
        
    for pak in containers:
        dest = os.path.join(BACKUP_FOLDER, pak)
        if os.path.exists(pak) and not os.path.exists(dest):
            try:
                # copy2 preserves file metadata (dates/permissions)
                shutil.copy2(pak, dest)
            except Exception as e:
                messagebox.showerror("Backup Error", f"Failed to back up {pak}: {e}")

ensure_backups()

def setup_lilac_styles(root: tk.Misc) -> ttk.Style:
    """
    Create/refresh lilac ttk styles for the given Tk interpreter
    """
    style = ttk.Style(master=root)
    
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Lilac.TFrame", background=LILAC)
    style.configure("Lilac.TLabel", background=LILAC, foreground="black", padding=0)
    style.map("Lilac.TLabel", background=[("active", LILAC)])

    return style

def apply_lilac_to_root(root: tk.Misc) -> None:
    """For plain tk widgets (tk.Frame/tk.Label/etc) that rely on root bg"""
    try:
        root.configure(bg=LILAC)
    except tk.TclError:
        pass

def lilac_label(*args, **kw) -> tk.Label:
    """
    Backward-compatible helper

    """
    if len(args) == 1:
        parent = args[0]
    elif len(args) >= 2:
        parent = args[1]
    else:
        raise TypeError("lilac_label requires at least (parent)")

    base = dict(bg=LILAC, bd=0, relief="flat", highlightthickness=0, takefocus=0)
    base.update(kw)
    return tk.Label(parent, **base)

def resize_and_pad(image_path):
    with Image.open(image_path) as img:
        # Resizes the image to fit 500x500 while keeping aspect ratio
        # and pads the empty areas with the Lilac color
        img = ImageOps.pad(img, (500, 500), color=LILAC_RGB, centering=(0.5, 0.5))
        return img

class BackgroundUnpacker:
    """
    Handles the unpacking logic in a background thread,
    Communicates progress back to the GUI via a callback function
    """
    def __init__(self, progress_callback):
        self.progress_callback = progress_callback # Function to update the UI

    def unpack_resource(self, pak_path, folder_name, container_id):
        if not os.path.exists(pak_path):
            messagebox.showwarning("File Missing", f"Could not find {pak_path}. Ensure the engine is in the game folder.")
            return
        os.makedirs(folder_name, exist_ok=True)
        
        with open(pak_path, "rb") as f:
            # Validate Signature
            sig = f.read(4)
            if sig != SIGNATURE:
                raise ValueError(f"Invalid signature in {pak_path}")

            f.read(4) # Skip unknown1
            file_count_raw = f.read(4)
            file_count = int.from_bytes(file_count_raw, "little")

            for i in range(file_count):
                # Grab the absolute metadata offset for this entry
                meta_offset = f.tell()
                
                # Read Metadata
                filename_raw = f.read(0x80)
                filename = filename_raw.decode('ascii', errors='ignore').strip('\x00')
                file_offset = int.from_bytes(f.read(4), "little")
                file_size = int.from_bytes(f.read(4), "little")
                
                # Save current position to return to after reading data
                return_pos = f.tell()

                # Extract Data
                f.seek(file_offset)
                file_data = f.read(file_size)

                # Append Taildata
                # Expanded Taildata: 1 + 2 + 4 + 4 = 11 bytes
                taildata = struct.pack(
                    "<BHII", 
                    container_id, 
                    meta_offset & 0xFFFF, 
                    file_offset, 
                    file_size
                )
                
                output_path = os.path.join(folder_name, filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, "wb") as out:
                    out.write(file_data)
                    out.write(taildata)

                # Update GUI
                if self.progress_callback:
                    self.progress_callback(i + 1, file_count, f"Unpacking: {filename}")

                f.seek(return_pos)

class ModManagerLogic:
    def __init__(self):
        self.containers = {0: "Resource0.pak", 1: "Resource1.pak"}
        self.ledger_path = "applied_mods.txt"

    def get_applied_mods(self):
        """Returns a set of active mod filenames and cleans up non-existent ones"""
        if not os.path.exists(self.ledger_path):
            return set()
            
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            # Read all lines, strip whitespace, and ignore empty lines
            mods = {line.strip() for line in f if line.strip()}
            
        # Detail Check: Verify that the mod file still exists in the Mods directory
        # This prevents the manager from thinking a mod is applied if the file was deleted manually
        existing_mods = {m for m in mods if os.path.exists(os.path.join("Mods", m))}
        
        # Automatic Sync: If the ledger contains ghost files, rewrite it immediately
        if len(existing_mods) != len(mods):
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                # We sort the list for a consistent ledger pattern
                for m in sorted(list(existing_mods)):
                    f.write(f"{m}\n")
                    
        return existing_mods

    def update_ledger(self, mod_name, add=True):
        """Adds or removes a mod name from the persistent ledger"""
        mods = self.get_applied_mods()
        if add:
            mods.add(mod_name)
        else:
            mods.discard(mod_name)
            
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            for m in sorted(list(mods)):
                f.write(f"{m}\n")

    def get_mod_header(self, mod_path):
        """Reads metadata and images without loading the whole mod payload"""
        with open(mod_path, "rb") as f:
            sig_len = int.from_bytes(f.read(1), "little")
            if f.read(sig_len) != MOD_SIGNATURE:
                return None
            
            file_count = int.from_bytes(f.read(4), "little")
            
            def read_prefixed_string(size_bytes):
                length = int.from_bytes(f.read(size_bytes), "little")
                return f.read(length).decode('utf-8', errors='ignore')

            meta = {
                "author": read_prefixed_string(1),
                "version": read_prefixed_string(1),
                "description": read_prefixed_string(2)
            }

            # Read Images
            img_count = int.from_bytes(f.read(1), "little")
            images = []
            for _ in range(img_count):
                img_size = int.from_bytes(f.read(4), "little")
                images.append(f.read(img_size))
            
            return {"meta": meta, "images": images, "file_count": file_count}

    def apply_mod(self, mod_path):
        """Appends files to PAK and updates metadata"""
        mod_name = os.path.basename(mod_path)
        header = self.get_mod_header(mod_path)
        if not header: return False, "Invalid Mod"

        with open(mod_path, "rb") as mod_f:
            # Seek past header/images to reach file payload
            mod_f.seek(self.calculate_payload_offset(mod_f))

            target_pak = None
            
            for _ in range(header['file_count']):
                file_size = int.from_bytes(mod_f.read(4), "little")
                file_data = mod_f.read(file_size)
                
                # Parse 11 byte Taildata
                taildata = file_data[-11:]
                cont_id, meta_offset, orig_off, orig_size = struct.unpack("<BHII", taildata)
                
                if target_pak is None:
                    target_pak = self.containers.get(cont_id)

                if not target_pak or not os.path.exists(target_pak):
                    return False, f"Missing container: {target_pak}"

                # Append to PAK
                with open(target_pak, "r+b") as pak:
                    pak.seek(0, 2) # Go to end
                    new_offset = pak.tell()
                    pak.write(file_data[:-11]) # Write data minus taildata
                    
                    # Update Metadata in PAK
                    # Metadata format: Name(0x80) + Offset(4) + Size(4)
                    pak.seek(meta_offset + 0x80)
                    pak.write(struct.pack("<II", new_offset, file_size - 11))

        self.update_ledger(mod_name, add=True)
        return True, "Mod Applied"

    def disable_mod(self, mod_path):
        """Reverts PAK metadata to original offsets/sizes"""
        mod_name = os.path.basename(mod_path)
        header = self.get_mod_header(mod_path)
        with open(mod_path, "rb") as mod_f:
            mod_f.seek(self.calculate_payload_offset(mod_f))
            for _ in range(header['file_count']):
                file_size = int.from_bytes(mod_f.read(4), "little")
                file_data = mod_f.read(file_size)
                taildata = file_data[-11:]
                cont_id, meta_offset, orig_off, orig_size = struct.unpack("<BHII", taildata)
                
                target_pak = self.containers.get(cont_id)
                with open(target_pak, "r+b") as pak:
                    pak.seek(meta_offset + 0x80)
                    pak.write(struct.pack("<II", orig_off, orig_size))
        self.update_ledger(mod_name, add=False)
        return True, "Mod Disabled"
    
    def disable_all(self):
        """
        The Hard Reset, it restores metadata blocks from original backups 
        and truncates containers to remove appended data
        """
        meta_sizes = {0: PAK0_METADATA_SIZE, 1: PAK1_METADATA_SIZE}

        for cid, name in self.containers.items():
            backup_path = os.path.join(BACKUP_FOLDER, name)
            
            # Safety check: Cannot restore if the user deleted their backups
            if not os.path.exists(backup_path):
                messagebox.showerror("Error", f"Backup not found for {name}. Cannot restore original metadata.")
                continue

            if os.path.exists(name):
                try:
                    # Grab original metadata block from backup
                    size_to_read = meta_sizes.get(cid)
                    with open(backup_path, "rb") as bf:
                        original_meta = bf.read(size_to_read)

                    # Overwrite active PAK metadata and truncate the file
                    target_size = PAK0_SIZE if cid == 0 else PAK1_SIZE
                    with open(name, "r+b") as f:
                        f.seek(0)
                        f.write(original_meta) # Write pristine metadata
                        f.truncate(target_size) # Slice off all appended mods
                except Exception as e:
                    messagebox.showerror("Hard Reset Failed", f"Failed to restore {name}: {e}")
                    return False

        # Clear the persistent ledger so the UI knows no mods are active
        if os.path.exists(self.ledger_path):
            try:
                os.remove(self.ledger_path)
            except Exception as e:
                messagebox.showwarning("Ledger Warning", f"Could not clear mod ledger: {e}")
            
        messagebox.showinfo("Success", "All mods cleared. Metadata and file sizes restored to vanilla.")
        return True
    
    def calculate_payload_offset(self, f):
        """Helper to skip to the start of file data"""
        f.seek(0)
        sig_len = int.from_bytes(f.read(1), "little")
        f.seek(sig_len, 1)
        f.seek(4, 1) # file count
        for _ in range(2): # author, version
            f.seek(int.from_bytes(f.read(1), "little"), 1)
        f.seek(int.from_bytes(f.read(2), "little"), 1) # description
        img_count = int.from_bytes(f.read(1), "little")
        for _ in range(img_count):
            f.seek(int.from_bytes(f.read(4), "little"), 1)
        return f.tell()

class ModPacker:
    """
    Handles the creation of .attmod packages
    """
    def __init__(self):
        pass

    def validate_taildata(self, file_path):
        if os.path.getsize(file_path) < 11:
            return False
        return True

    def transfer_taildata(self, target_path, source_path):
        """
        Extracts 11 byte taildata from source and appends to target,
        Returns bool, message
        """
        try:
            if not os.path.exists(source_path):
                return False, f"Source missing: {os.path.basename(source_path)}"
            
            if os.path.getsize(source_path) < 11:
                return False, f"Source too small: {os.path.basename(source_path)}"

            # Read the last 11 bytes from source
            with open(source_path, "rb") as s:
                s.seek(-11, 2)
                taildata = s.read(11)

            # Append those bytes to the target
            with open(target_path, "ab") as t:
                t.write(taildata)

            return True, "OK"
        except Exception as e:
            return False, str(e)

    def create_package(self, meta, files, output_path, image_paths=[]):
        """
        image_paths: List of strings (paths to images)
        """
        try:
            with open(output_path, "wb") as f:
                # Header
                f.write(len(MOD_SIGNATURE).to_bytes(1, "little"))
                f.write(MOD_SIGNATURE)
                f.write(len(files).to_bytes(4, "little"))
                
                # Author
                author_bytes = meta.get('author', '').encode('utf-8')
                f.write(len(author_bytes).to_bytes(1, "little"))
                f.write(author_bytes)
                
                # Version
                ver_bytes = meta.get('version', '').encode('utf-8')
                f.write(len(ver_bytes).to_bytes(1, "little"))
                f.write(ver_bytes)
                
                # Description
                desc_bytes = meta.get('description', '').encode('utf-8')
                f.write(len(desc_bytes).to_bytes(2, "little"))
                f.write(desc_bytes)

                # Image Section
                # Write Count (1 byte)
                valid_image_paths = image_paths[:5]
                f.write(len(valid_image_paths).to_bytes(1, "little"))

                for img_p in valid_image_paths:
                    if os.path.exists(img_p):
                        try:
                            with Image.open(img_p) as img:
                                # Convert to RGB if it's RGBA/P (prevents errors with JPEGs/Specific formats)
                                if img.mode in ("RGBA", "P"):
                                    img = img.convert("RGB")
                                
                                # Resize and Pad to exactly 500x500
                                # Use (200, 162, 200) to match Lilac UI theme
                                img = ImageOps.pad(img, (500, 500), color=(200, 162, 200))
                                
                                # Save to a byte buffer as JPEG (highly compressed for speed)
                                img_byte_arr = io.BytesIO()
                                img.save(img_byte_arr, format='JPEG', quality=85)
                                img_data = img_byte_arr.getvalue()
                                
                                f.write(len(img_data).to_bytes(4, "little"))
                                f.write(img_data)
                        except Exception as e:
                            print(f"Skipping image {img_p}: {e}")
                            
                # File Payload
                for file_path in files:
                    if not self.validate_taildata(file_path):
                        print(f"Warning: {os.path.basename(file_path)} might differ from Ingelmia format.")
                    
                    size = os.path.getsize(file_path)
                    f.write(size.to_bytes(4, "little"))
                    
                    with open(file_path, "rb") as source:
                        f.write(source.read())
                        
            return True, f"Successfully created {os.path.basename(output_path)}"
        except Exception as e:
            return False, str(e)
