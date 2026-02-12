import os, threading, tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk, filedialog, messagebox
from .ingelmia_supply import LILAC, setup_lilac_styles, apply_lilac_to_root, BackgroundUnpacker, ModPacker, ModManagerLogic

"""
This script handles the GUI logic of Ingelmia Engine, calling functions as needed from Ingelmia_Supply
"""

class ModManagerWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ingelmia Mod Manager")
        self.geometry("1150x750")
        
        apply_lilac_to_root(self)
        
        self.logic = ModManagerLogic()
        self.current_mod_data = None
        self.image_index = 0
        self.tk_img = None # Reference to prevent garbage collection
        
        self.setup_ui()
        self.refresh_mod_list()

    def setup_ui(self):
        # Configure Grid weights so columns behave correctly
        self.columnconfigure(0, weight=0) # List stays fixed width
        self.columnconfigure(1, weight=1) # Center (Image) expands
        self.columnconfigure(2, weight=0) # Info stays fixed width
        self.rowconfigure(0, weight=1)

        # Left Column: Mod List
        self.list_frame = ttk.Frame(self, style="Lilac.TFrame", padding=10)
        self.list_frame.grid(row=0, column=0, sticky="nsw")
        
        ttk.Label(self.list_frame, text="Available Mods", font=("Segoe UI", 10, "bold"), style="Lilac.TLabel").pack(pady=(0, 5))
        self.mod_listbox = tk.Listbox(self.list_frame, width=35, height=35)
        self.mod_listbox.pack(fill="both", expand=True)
        self.mod_listbox.bind("<<ListboxSelect>>", self.on_mod_select)

        # Center Column: Image Viewer
        self.view_frame = ttk.Frame(self, style="Lilac.TFrame", padding=10)
        self.view_frame.grid(row=0, column=1, sticky="nsew")
        
        # Change bg from black to LILAC
        self.img_container = tk.Frame(self.view_frame, width=500, height=500, bg=LILAC)
        self.img_container.pack_propagate(0) 
        self.img_container.pack(pady=20)
        
        # Change bg from black to LILAC
        self.img_label = tk.Label(self.img_container, bg=LILAC)
        self.img_label.pack(fill="both", expand=True)
        
        # Navigation Buttons
        nav_frame = ttk.Frame(self.view_frame, style="Lilac.TFrame")
        nav_frame.pack()
        ttk.Button(nav_frame, text=" < Prev ", command=lambda: self.cycle_image(-1)).pack(side="left", padx=10)
        ttk.Button(nav_frame, text=" Next > ", command=lambda: self.cycle_image(1)).pack(side="left", padx=10)

        # Right Column: Info and Actions
        self.info_frame = ttk.Frame(self, style="Lilac.TFrame", padding=10)
        self.info_frame.grid(row=0, column=2, sticky="nsew")
        
        self.lbl_author = ttk.Label(self.info_frame, text="Author:", font=("Segoe UI", 11, "bold"), style="Lilac.TLabel")
        self.lbl_author.pack(anchor="w", pady=(0, 10))
        
        ttk.Label(self.info_frame, text="Description:", style="Lilac.TLabel").pack(anchor="w")
        self.txt_desc = tk.Text(self.info_frame, height=15, width=45, state="disabled", wrap="word", font=("Segoe UI", 9))
        self.txt_desc.pack(pady=(0, 20))
        
        # Buttons
        ttk.Button(self.info_frame, text="Apply Mod", command=self.apply_selected).pack(fill="x", pady=2)
        ttk.Button(self.info_frame, text="Disable Mod", command=self.disable_selected).pack(fill="x", pady=2)
        
        # Spacer
        tk.Label(self.info_frame, bg=LILAC, height=2).pack()
        
        ttk.Button(self.info_frame, text="Disable All Mods", command=self.disable_all_mods).pack(fill="x", side="bottom", pady=20)

    def refresh_mod_list(self):
        if not os.path.exists("Mods"):
            os.makedirs("Mods")
            
        self.mod_listbox.delete(0, tk.END)
        applied_mods = self.logic.get_applied_mods()
        
        self.all_mod_files = [] # Track actual filenames separately from display names
        
        for f in os.listdir("Mods"):
            if f.endswith(".attmod"):
                display_name = f
                is_active = f in applied_mods
                
                if is_active:
                    display_name = f"[*] {f}"
                
                self.mod_listbox.insert(tk.END, display_name)
                self.all_mod_files.append(f)
                
                # Highlight active mods in a darker lilac or bold
                if is_active:
                    idx = self.mod_listbox.size() - 1
                    self.mod_listbox.itemconfig(idx, fg="#5e2f5e") # Darker purple for contrast

    def on_mod_select(self, event):
        selection = self.mod_listbox.curselection()
        if not selection: return
        
        # Map back from display name to actual filename
        actual_filename = self.all_mod_files[selection[0]]
        path = os.path.join("Mods", actual_filename)
        
        data = self.logic.get_mod_header(path)
        if data:
            self.current_mod_data = data
            # Store the actual path for logic calls
            self.current_mod_path = path 
            self.image_index = 0
            self.update_display()

    def update_display(self):
        if not self.current_mod_data: return
        
        # Meta Update
        self.lbl_author.config(text=f"Author: {self.current_mod_data['meta']['author']}")
        self.txt_desc.config(state="normal")
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", self.current_mod_data['meta']['description'])
        self.txt_desc.config(state="disabled")
        
        # Trigger image draw
        self.cycle_image(0)

    def cycle_image(self, delta):
        if not self.current_mod_data or not self.current_mod_data['images']:
            self.img_label.config(image='', text="No Images")
            return
            
        self.image_index = (self.image_index + delta) % len(self.current_mod_data['images'])
        raw_data = self.current_mod_data['images'][self.image_index]
        
        try:
            from io import BytesIO
            img = Image.open(BytesIO(raw_data))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img, text="")
        except Exception as e:
            self.img_label.config(image='', text=f"Error loading image: {e}")

    def apply_selected(self):
        if hasattr(self, 'current_mod_path'):
            success, msg = self.logic.apply_mod(self.current_mod_path)
            if success:
                self.refresh_mod_list() # Sync UI
            messagebox.showinfo("Status", msg)

    def disable_selected(self):
        if hasattr(self, 'current_mod_path'):
            success, msg = self.logic.disable_mod(self.current_mod_path)
            if success:
                self.refresh_mod_list() # Sync UI
            messagebox.showinfo("Status", msg)

    def disable_all_mods(self):
        if messagebox.askyesno("Confirm", "This will revert all metadata and truncate containers to original sizes. Proceed?"):
            success, msg = self.logic.disable_all()
            messagebox.showinfo("Status", msg)

class ModCreatorWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ingelmia Mod Creator")
        self.geometry("600x750") # Slightly taller for image list
        self.resizable(False, False)
        
        apply_lilac_to_root(self)
        
        self.packer = ModPacker()
        self.files_to_pack = []
        self.image_paths = []
        
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self)
        style.configure("Lilac.TLabel", background=LILAC)
        
        # Metadata Inputs
        frame_meta = ttk.Frame(self, style="Lilac.TFrame")
        frame_meta.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_meta, text="Author:", style="Lilac.TLabel").grid(row=0, column=0, sticky="w")
        self.ent_author = ttk.Entry(frame_meta, width=40)
        self.ent_author.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_meta, text="Version:", style="Lilac.TLabel").grid(row=1, column=0, sticky="w")
        self.ent_version = ttk.Entry(frame_meta, width=40)
        self.ent_version.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame_meta, text="Description:", style="Lilac.TLabel").grid(row=2, column=0, sticky="nw")
        self.text_desc = tk.Text(frame_meta, wrap=tk.WORD, height=4, width=40)
        self.text_desc.grid(row=2, column=1, padx=5, pady=2)

        # Image Selection
        frame_img = ttk.Frame(self, style="Lilac.TFrame")
        frame_img.pack(pady=5, fill="x", padx=10)
        
        lbl_img = ttk.Label(frame_img, text="Preview Images:", style="Lilac.TLabel")
        lbl_img.pack(anchor="w")

        btn_img = ttk.Button(frame_img, text="Add Image", command=self.add_image)
        btn_img.pack(side="left", pady=2)
        
        btn_clr_img = ttk.Button(frame_img, text="Clear Images", command=self.clear_images)
        btn_clr_img.pack(side="left", padx=5, pady=2)

        self.list_img = tk.Listbox(frame_img, height=3)
        self.list_img.pack(fill="x", pady=2)

        # File List
        frame_files = ttk.Frame(self, style="Lilac.TFrame")
        frame_files.pack(pady=10, fill="both", expand=True, padx=10)
        
        ttk.Label(frame_files, text="Mod Files:", style="Lilac.TLabel").pack(anchor="w")

        btn_add = ttk.Button(frame_files, text="Add Files", command=self.add_files)
        btn_add.pack(anchor="w")
        
        self.listbox = tk.Listbox(frame_files)
        self.listbox.pack(fill="both", expand=True, pady=5)
        
        btn_clear = ttk.Button(frame_files, text="Clear File List", command=self.clear_files)
        btn_clear.pack(anchor="w")

        # Create Button
        btn_create = ttk.Button(self, text="Create Mod Package", command=self.create_mod)
        btn_create.pack(pady=20)

        # Transfer Taildata Button
        self.btn_transfer = ttk.Button(
            self,
            text="Transfer Taildata",
            command=self.transfer_taildata_gui
        )
        self.btn_transfer.pack(pady=5)

    def transfer_taildata_gui(self):
        # Select Edited Files
        targets = filedialog.askopenfilenames(
            title="Step 1: Select the New/Modded files in order"
        )
        if not targets:
            return

        # Select Original Files
        sources = filedialog.askopenfilenames(
            title=f"Step 2: Select {len(targets)} original files. Must match Step 1 order."
        )
        if not sources:
            return

        # Validate Count
        if len(targets) != len(sources):
            messagebox.showerror(
                "Count Mismatch", 
                f"You selected {len(targets)} edited files but {len(sources)} original files.\n\n"
                "They must be paired 1 to 1."
            )
            return

        #  Process the Batch
        success_count = 0
        errors = []

        # zip() pairs them: (targets[0], sources[0]), (targets[1], sources[1]), etc
        for target, source in zip(targets, sources):
            success, msg = self.packer.transfer_taildata(target, source)
            if success:
                success_count += 1
            else:
                errors.append(f"{os.path.basename(target)}: {msg}")

        # Final Feedback
        result_msg = f"Successfully updated {success_count} files."
        if errors:
            result_msg += "\n\nErrors:\n" + "\n".join(errors)
        
        messagebox.showinfo("Transfer Result", result_msg)

    def add_image(self):
        # Allow multiple selection
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")])
        for p in paths:
            if p not in self.image_paths:
                self.image_paths.append(p)
                self.list_img.insert(tk.END, os.path.basename(p))

    def clear_images(self):
        self.image_paths.clear()
        self.list_img.delete(0, tk.END)

    def add_files(self):
        files = filedialog.askopenfilenames()
        for f in files:
            if f not in self.files_to_pack:
                self.files_to_pack.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def clear_files(self):
        self.files_to_pack.clear()
        self.listbox.delete(0, tk.END)

    def create_mod(self):
        if not self.files_to_pack:
            messagebox.showwarning("Warning", "No files added!")
            return

        out_path = filedialog.asksaveasfilename(defaultextension=".attmod", filetypes=[("ATT Mod", "*.attmod")])
        if not out_path:
            return

        meta = {
            'author': self.ent_author.get(),
            'version': self.ent_version.get(),
            'description': self.text_desc.get("1.0", tk.END).strip()
        }

        # Pass the list of images
        success, msg = self.packer.create_package(meta, self.files_to_pack, out_path, self.image_paths)
        
        if success:
            messagebox.showinfo("Success", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
        
class Core_Tools():
    def __init__(self, root):
        self.root = root
        self.root.title("Ingelmia Engine, Ascension To The Throne Modding Tools")
        self.mod_creator_window = None
        self.mod_manager_window = None
        self.root.geometry("800x800")
        self.root.resizable(False, False)

        setup_lilac_styles(self.root)
        apply_lilac_to_root(self.root)

        self.progress = None  # will hold progress bar + text
        self.mod_creator_window = None # Initialize tracker
        self.mod_manager_window = None # Initialize tracker
        
        self.gui_setup()
        self.init_progress()   # set up status bar + progress bar

    def gui_setup(self):
        self.bg = ttk.Frame(self.root, style="Lilac.TFrame")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.explainer_1 = ttk.Label(
            self.bg,
            text="Click the button you wish to use.",
            style="Lilac.TLabel"
        )
        self.explainer_1.place(x=50, y=20)

        # Status line (text messages)
        self.status_label = ttk.Label(
            self.bg,
            text="",
            style="Lilac.TLabel",
            foreground="green"
        )
        self.status_label.place(x=100, y=400)

        # Mod Creator launcher
        tools_btn = ttk.Button(
            self.bg,
            text="Open Mod Creator",
            command=self.open_mod_creator_window
        )
        tools_btn.place(x=50, y=60)

        # Mod Manager launcher
        manager_btn = ttk.Button(
            self.bg,
            text="Open Mod Manager",
            command=self.open_mod_manager_window
        )
        manager_btn.place(x=50, y=100)

        # Unpacker button
        unpack_btn = ttk.Button(
            self.bg,
            text="Unpack PAK Files",
            command=self.start_unpacking
        )
        unpack_btn.place(x=50, y=140)

    def open_mod_manager_window(self):
        """
        Singleton Pattern, only opens if not already open
        """
        if self.mod_manager_window is None or not self.mod_manager_window.winfo_exists():
            self.mod_manager_window = ModManagerWindow(self.root)
        else:
            self.mod_manager_window.lift() # Bring to front
            self.mod_manager_window.focus_force()

    def open_mod_creator_window(self):
        """
        Singleton Pattern, only opens if not already open
        """
        if self.mod_creator_window is None or not self.mod_creator_window.winfo_exists():
            self.mod_creator_window = ModCreatorWindow(self.root)
        else:
            self.mod_creator_window.lift() # Bring to front
            self.mod_creator_window.focus_force()

    # Progress/status bar setup

    def init_progress(self):
        """
        Create a progress bar + label at the bottom of the window
        """
        self.progress = {}
        self.progress["var"] = tk.StringVar(value="Idle")

        # Progress bar
        bar = ttk.Progressbar(self.bg, mode="determinate", length=600)
        bar.place(x=100, y=600)
        self.progress["bar"] = bar

        # Progress text label
        prog_label = ttk.Label(
            self.bg,
            textvariable=self.progress["var"],
            style="Lilac.TLabel"
        )
        prog_label.place(x=100, y=630)

    def set_progress(self, done, total, note=None):
        """
        Update the progress bar and text
        """
        if self.progress is None:
            return

        bar = self.progress["bar"]
        var = self.progress["var"]

        total = max(1, int(total))
        done = min(int(done), total)

        if int(bar["maximum"] or 0) != total:
            bar.configure(maximum=total)

        bar["value"] = done

        if note is None:
            pct = (done * 100) // total
            var.set(f"Working {done}/{total} ({pct}%)")
        else:
            var.set(note)

        # Keep UI responsive without reentering mainloop
        self.root.update_idletasks()

    def start_unpacking(self):
        """Triggered by a button click"""
        # Disable buttons so user doesn't click twice
        thread = threading.Thread(target=self.run_unpack_task, daemon=True)
        thread.start()

    def run_unpack_task(self):
        """The actual work loop running in the thread"""
        unpacker = BackgroundUnpacker(progress_callback=self.set_progress)
        
        try:
            # Unpack Resource0
            self.status_label.config(text="Processing Resource0.pak", foreground="blue")
            unpacker.unpack_resource("Resource0.pak", "Pak0_Files", 0)
            
            # Unpack Resource1
            self.status_label.config(text="Processing Resource1.pak", foreground="blue")
            unpacker.unpack_resource("Resource1.pak", "Pak1_Files", 1)
            
            self.status_label.config(text="Unpacking Complete.", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Unpacking failed: {e}")
