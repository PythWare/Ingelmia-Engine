import os, queue, threading
import tkinter as tk
from io import BytesIO
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from .ingelmia_supply import (
    CYBER_ACCENT,
    CYBER_ACCENT_2,
    CYBER_BG,
    CYBER_GOOD,
    CYBER_MUTED,
    CYBER_PANEL,
    CYBER_PANEL_2,
    CYBER_TEXT,
    GAME_PROFILES,
    ModManagerLogic,
    ModPacker,
    BackgroundUnpacker,
    apply_lilac_to_root,
    get_profile,
    setup_lilac_styles,
    tr,
)

"""
GUI layer for Ingelmia Engine

The main window is custom drawn with Canvas widgets so it can look more like a
high tech toolkit while still staying pure Tkinter
"""


class CyberButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=230, height=48, accent=CYBER_ACCENT, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=CYBER_BG, **kwargs)
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.accent = accent
        self.hover = False
        self.enabled = True
        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.replace)
        self.bind("<Button-1>", self.click)
        self.draw()

    def configure_text(self, text):
        self.text = text
        self.draw()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.draw()

    def enter(self, _event):
        self.hover = True
        self.draw()

    def replace(self, _event):
        self.hover = False
        self.draw()

    def click(self, _event):
        if self.enabled and self.command:
            self.command()

    def draw(self):
        self.delete("all")
        fill = CYBER_PANEL_2 if self.enabled else "#1A1C24"
        outline = self.accent if self.hover and self.enabled else "#2B3E58"
        text_color = CYBER_TEXT if self.enabled else "#59616D"
        self.create_polygon(
            14, 0, self.width, 0, self.width, self.height - 14, self.width - 14, self.height,
            0, self.height, 0, 14,
            fill=fill, outline=outline, width=2,
        )
        self.create_line(10, self.height - 5, self.width - 20, self.height - 5, fill=self.accent if self.enabled else "#333946")
        self.create_text(self.width // 2, self.height // 2, text=self.text, fill=text_color, font=("Segoe UI", 10, "bold"))


class CyberToggle(tk.Canvas):
    def __init__(self, master, left_text, right_text, variable, left_value, right_value, command=None, width=250, height=44):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=CYBER_BG)
        self.left_text = left_text
        self.right_text = right_text
        self.variable = variable
        self.left_value = left_value
        self.right_value = right_value
        self.command = command
        self.width = width
        self.height = height
        self.bind("<Button-1>", self.click)
        self.draw()

    def configure_texts(self, left_text, right_text):
        self.left_text = left_text
        self.right_text = right_text
        self.draw()

    def click(self, event):
        self.variable.set(self.left_value if event.x < self.width / 2 else self.right_value)
        self.draw()
        if self.command:
            self.command()

    def draw(self):
        self.delete("all")
        self.create_rectangle(0, 0, self.width, self.height, fill=CYBER_PANEL, outline="#2B3E58", width=2)
        active_left = self.variable.get() == self.left_value
        x0 = 3 if active_left else self.width // 2
        x1 = self.width // 2 if active_left else self.width - 3
        self.create_rectangle(x0, 3, x1, self.height - 3, fill="#18354A", outline=CYBER_ACCENT, width=2)
        self.create_text(self.width // 4, self.height // 2, text=self.left_text, fill=CYBER_TEXT if active_left else CYBER_MUTED, font=("Segoe UI", 9, "bold"))
        self.create_text(self.width * 3 // 4, self.height // 2, text=self.right_text, fill=CYBER_TEXT if not active_left else CYBER_MUTED, font=("Segoe UI", 9, "bold"))


class CyberPanel(tk.Canvas):
    def __init__(self, master, width, height, title="", **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=CYBER_BG, **kwargs)
        self.width = width
        self.height = height
        self.title = title
        self.draw()

    def draw(self):
        self.delete("all")
        self.create_polygon(18, 0, self.width, 0, self.width, self.height - 18, self.width - 18, self.height, 0, self.height, 0, 18, fill=CYBER_PANEL, outline="#2B3E58", width=2)
        self.create_line(18, 1, self.width - 40, 1, fill=CYBER_ACCENT, width=2)
        if self.title:
            self.create_text(18, 18, text=self.title, anchor="w", fill=CYBER_TEXT, font=("Segoe UI", 11, "bold"))


class ModManagerWindow(tk.Toplevel):
    def __init__(self, master, profile, language="en", game_folder=None):
        super().__init__(master)
        self.profile = profile
        self.language = language
        self.game_folder = game_folder
        self.title(f"Ingelmia {tr(language, 'mod_manager')}, {profile.display_name}")
        self.geometry("1150x750")
        apply_lilac_to_root(self)

        self.logic = ModManagerLogic(profile, game_folder=self.game_folder)
        self.current_mod_data = None
        self.image_index = 0
        self.tk_img = None
        self.all_mod_files = []

        self.setup_ui()
        self.refresh_mod_list()

    def setup_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.list_frame = ttk.Frame(self, style="Cyber.TFrame", padding=10)
        self.list_frame.grid(row=0, column=0, sticky="nsw")
        ttk.Label(self.list_frame, text=tr(self.language, "available_mods"), font=("Segoe UI", 10, "bold"), style="Cyber.TLabel").pack(pady=(0, 5))
        self.mod_listbox = tk.Listbox(self.list_frame, width=35, height=35, bg="#09111F", fg=CYBER_TEXT, selectbackground="#18445A", selectforeground="white", relief="flat", highlightthickness=1, highlightbackground="#2B3E58")
        self.mod_listbox.pack(fill="both", expand=True)
        self.mod_listbox.bind("<<ListboxSelect>>", self.on_mod_select)

        self.view_frame = ttk.Frame(self, style="Cyber.TFrame", padding=10)
        self.view_frame.grid(row=0, column=1, sticky="nsew")
        self.img_container = tk.Frame(self.view_frame, width=500, height=500, bg=CYBER_PANEL)
        self.img_container.pack_propagate(0)
        self.img_container.pack(pady=20)
        self.img_label = tk.Label(self.img_container, bg=CYBER_PANEL, fg=CYBER_TEXT)
        self.img_label.pack(fill="both", expand=True)

        nav_frame = ttk.Frame(self.view_frame, style="Cyber.TFrame")
        nav_frame.pack()
        ttk.Button(nav_frame, text=tr(self.language, "prev"), style="Cyber.TButton", command=lambda: self.cycle_image(-1)).pack(side="left", padx=10)
        ttk.Button(nav_frame, text=tr(self.language, "next"), style="Cyber.TButton", command=lambda: self.cycle_image(1)).pack(side="left", padx=10)

        self.info_frame = ttk.Frame(self, style="Cyber.TFrame", padding=10)
        self.info_frame.grid(row=0, column=2, sticky="nsew")
        self.lbl_author = ttk.Label(self.info_frame, text=f"{tr(self.language, 'author')}:", font=("Segoe UI", 11, "bold"), style="Cyber.TLabel")
        self.lbl_author.pack(anchor="w", pady=(0, 10))
        ttk.Label(self.info_frame, text=f"{tr(self.language, 'description')}:", style="Cyber.TLabel").pack(anchor="w")
        self.txt_desc = tk.Text(self.info_frame, height=15, width=45, state="disabled", wrap="word", font=("Segoe UI", 9), bg="#09111F", fg=CYBER_TEXT, insertbackground=CYBER_TEXT, relief="flat", highlightthickness=1, highlightbackground="#2B3E58")
        self.txt_desc.pack(pady=(0, 20))
        ttk.Button(self.info_frame, text=tr(self.language, "apply_mod"), style="Cyber.TButton", command=self.apply_selected).pack(fill="x", pady=2)
        ttk.Button(self.info_frame, text=tr(self.language, "disable_mod"), style="Cyber.TButton", command=self.disable_selected).pack(fill="x", pady=2)
        ttk.Button(self.info_frame, text=tr(self.language, "disable_all"), style="Cyber.TButton", command=self.disable_all_mods).pack(fill="x", side="bottom", pady=20)

    def refresh_mod_list(self):
        os.makedirs("Mods", exist_ok=True)
        self.mod_listbox.delete(0, tk.END)
        applied_mods = self.logic.get_applied_mods()
        self.all_mod_files = []
        for f in os.listdir("Mods"):
            if f.endswith(".attmod"):
                display_name = f"[*] {f}" if f in applied_mods else f
                self.mod_listbox.insert(tk.END, display_name)
                self.all_mod_files.append(f)
                if f in applied_mods:
                    self.mod_listbox.itemconfig(self.mod_listbox.size() - 1, fg=CYBER_GOOD)

    def on_mod_select(self, _event):
        selection = self.mod_listbox.curselection()
        if not selection:
            return
        actual_filename = self.all_mod_files[selection[0]]
        path = os.path.join("Mods", actual_filename)
        data = self.logic.get_mod_header(path)
        if data:
            self.current_mod_data = data
            self.current_mod_path = path
            self.image_index = 0
            self.update_display()

    def update_display(self):
        if not self.current_mod_data:
            return
        self.lbl_author.config(text=f"{tr(self.language, 'author')}: {self.current_mod_data['meta']['author']}")
        self.txt_desc.config(state="normal")
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", self.current_mod_data["meta"]["description"])
        self.txt_desc.config(state="disabled")
        self.cycle_image(0)

    def cycle_image(self, delta):
        if not self.current_mod_data or not self.current_mod_data["images"]:
            self.img_label.config(image="", text=tr(self.language, "no_images"))
            return
        self.image_index = (self.image_index + delta) % len(self.current_mod_data["images"])
        raw_data = self.current_mod_data["images"][self.image_index]
        try:
            img = Image.open(BytesIO(raw_data))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img, text="")
        except Exception as e:
            self.img_label.config(image="", text=f"Error loading image: {e}")

    def apply_selected(self):
        if hasattr(self, "current_mod_path"):
            success, msg = self.logic.apply_mod(self.current_mod_path)
            if success:
                self.refresh_mod_list()
            messagebox.showinfo(tr(self.language, "status"), msg)

    def disable_selected(self):
        if hasattr(self, "current_mod_path"):
            success, msg = self.logic.disable_mod(self.current_mod_path)
            if success:
                self.refresh_mod_list()
            messagebox.showinfo(tr(self.language, "status"), msg)

    def disable_all_mods(self):
        if messagebox.askyesno("Confirm", tr(self.language, "confirm_reset")):
            success, msg = self.logic.disable_all()
            messagebox.showinfo(tr(self.language, "status"), msg)
            if success:
                self.refresh_mod_list()


class ModCreatorWindow(tk.Toplevel):
    def __init__(self, master, language="en"):
        super().__init__(master)
        self.language = language
        self.title(f"Ingelmia {tr(language, 'mod_creator')}")
        self.geometry("620x760")
        self.resizable(False, False)
        apply_lilac_to_root(self)

        self.packer = ModPacker()
        self.files_to_pack = []
        self.image_paths = []
        self.setup_ui()

    def setup_ui(self):
        frame_meta = ttk.Frame(self, style="Cyber.TFrame")
        frame_meta.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_meta, text=f"{tr(self.language, 'author')}:", style="Cyber.TLabel").grid(row=0, column=0, sticky="w")
        self.ent_author = ttk.Entry(frame_meta, width=42)
        self.ent_author.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_meta, text=f"{tr(self.language, 'version')}:", style="Cyber.TLabel").grid(row=1, column=0, sticky="w")
        self.ent_version = ttk.Entry(frame_meta, width=42)
        self.ent_version.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame_meta, text=f"{tr(self.language, 'description')}:", style="Cyber.TLabel").grid(row=2, column=0, sticky="nw")
        self.text_desc = tk.Text(frame_meta, wrap=tk.WORD, height=4, width=42, bg="#09111F", fg=CYBER_TEXT, insertbackground=CYBER_TEXT, relief="flat", highlightthickness=1, highlightbackground="#2B3E58")
        self.text_desc.grid(row=2, column=1, padx=5, pady=2)

        frame_img = ttk.Frame(self, style="Cyber.TFrame")
        frame_img.pack(pady=5, fill="x", padx=10)
        ttk.Label(frame_img, text=f"{tr(self.language, 'preview_images')}:", style="Cyber.TLabel").pack(anchor="w")
        ttk.Button(frame_img, text=tr(self.language, "add_image"), style="Cyber.TButton", command=self.add_image).pack(side="left", pady=2)
        ttk.Button(frame_img, text=tr(self.language, "clear_images"), style="Cyber.TButton", command=self.clear_images).pack(side="left", padx=5, pady=2)
        self.list_img = tk.Listbox(frame_img, height=3, bg="#09111F", fg=CYBER_TEXT, relief="flat")
        self.list_img.pack(fill="x", pady=2)

        frame_files = ttk.Frame(self, style="Cyber.TFrame")
        frame_files.pack(pady=10, fill="both", expand=True, padx=10)
        ttk.Label(frame_files, text=f"{tr(self.language, 'mod_files')}:", style="Cyber.TLabel").pack(anchor="w")
        ttk.Button(frame_files, text=tr(self.language, "add_files"), style="Cyber.TButton", command=self.add_files).pack(anchor="w")
        self.listbox = tk.Listbox(frame_files, bg="#09111F", fg=CYBER_TEXT, relief="flat")
        self.listbox.pack(fill="both", expand=True, pady=5)
        ttk.Button(frame_files, text=tr(self.language, "clear_files"), style="Cyber.TButton", command=self.clear_files).pack(anchor="w")
        ttk.Button(self, text=tr(self.language, "create_package"), style="Cyber.TButton", command=self.create_mod).pack(pady=12)
        ttk.Button(self, text=tr(self.language, "transfer_taildata"), style="Cyber.TButton", command=self.transfer_taildata_gui).pack(pady=5)
        ttk.Button(self, text=tr(self.language, "batch_update_files"), style="Cyber.TButton", command=self.batch_update_files_gui).pack(pady=5)

    def batch_update_files_gui(self):
        target_folder = filedialog.askdirectory(title="Step 1: Select the New/Modded folder that needs taildata")
        if not target_folder:
            return

        source_folder = filedialog.askdirectory(title="Step 2: Select the Original folder to copy taildata from")
        if not source_folder:
            return

        success_count, skipped_count, errors = self.packer.batch_transfer_taildata_by_filename(target_folder, source_folder)
        result_msg = f"Successfully updated {success_count} files."
        if skipped_count:
            result_msg += f"\nSkipped/failed {skipped_count} files."
        if errors:
            preview = "\n".join(errors[:40])
            if len(errors) > 40:
                preview += f"\n...and {len(errors) - 40} more."
            result_msg += "\n\nDetails:\n" + preview
        messagebox.showinfo("Batch Update Result", result_msg)

    def transfer_taildata_gui(self):
        targets = filedialog.askopenfilenames(title="Step 1: Select the New/Modded files in order")
        if not targets:
            return
        sources = filedialog.askopenfilenames(title=f"Step 2: Select {len(targets)} original files. Must match Step 1 order.")
        if not sources:
            return
        if len(targets) != len(sources):
            messagebox.showerror("Count Mismatch", f"You selected {len(targets)} edited files but {len(sources)} original files. They must be paired 1 to 1.")
            return

        success_count, errors = 0, []
        for target, source in zip(targets, sources):
            success, msg = self.packer.transfer_taildata(target, source)
            if success:
                success_count += 1
            else:
                errors.append(f"{os.path.basename(target)}: {msg}")
        result_msg = f"Successfully updated {success_count} files."
        if errors:
            result_msg += "\n\nErrors:\n" + "\n".join(errors)
        messagebox.showinfo("Transfer Result", result_msg)

    def add_image(self):
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
            messagebox.showwarning("Warning", tr(self.language, "warning_no_files"))
            return
        out_path = filedialog.asksaveasfilename(defaultextension=".attmod", filetypes=[("ATT Mod", "*.attmod")])
        if not out_path:
            return
        meta = {
            "author": self.ent_author.get(),
            "version": self.ent_version.get(),
            "description": self.text_desc.get("1.0", tk.END).strip(),
        }
        success, msg = self.packer.create_package(meta, self.files_to_pack, out_path, self.image_paths)
        if success:
            messagebox.showinfo("Success", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)


class Core_Tools:
    def __init__(self, root):
        self.root = root
        self.root.title("Ingelmia Engine")
        self.root.geometry("920x620")
        self.root.resizable(False, False)

        setup_lilac_styles(self.root)
        apply_lilac_to_root(self.root)

        self.game_var = tk.StringVar(value="ascension")
        self.language_var = tk.StringVar(value="en")
        self.game_folder_var = tk.StringVar(value=os.getcwd())
        self.status_var = tk.StringVar(value=tr("en", "idle"))
        self.progress_var = tk.DoubleVar(value=0)
        self.ui_queue = queue.Queue()
        self.is_working = False
        self.mod_creator_window = None
        self.mod_manager_window = None

        self.gui_setup()
        self.root.after(80, self.process_ui_queue)

    @property
    def language(self):
        return self.language_var.get()

    @property
    def profile(self):
        return get_profile(self.game_var.get())

    def gui_setup(self):
        self.bg = tk.Canvas(self.root, width=920, height=620, bg=CYBER_BG, highlightthickness=0)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.draw_background()

        self.title_id = self.bg.create_text(42, 36, text=tr(self.language, "app_title"), anchor="w", fill=CYBER_TEXT, font=("Segoe UI", 24, "bold"))
        self.subtitle_id = self.bg.create_text(44, 72, text=tr(self.language, "subtitle"), anchor="w", fill=CYBER_MUTED, font=("Segoe UI", 10))

        self.profile_panel = CyberPanel(self.root, 830, 165, "")
        self.profile_panel.place(x=45, y=110)

        self.game_label = ttk.Label(self.root, text=tr(self.language, "choose_game"), style="Cyber.TLabel", font=("Segoe UI", 10, "bold"))
        self.game_label.place(x=78, y=134)
        self.game_toggle = CyberToggle(self.root, tr(self.language, "ascension"), tr(self.language, "valkyrie"), self.game_var, "ascension", "valkyrie", command=self.on_profile_changed)
        self.game_toggle.place(x=78, y=162)

        self.lang_label = ttk.Label(self.root, text=tr(self.language, "choose_language"), style="Cyber.TLabel", font=("Segoe UI", 10, "bold"))
        self.lang_label.place(x=370, y=134)
        self.lang_toggle = CyberToggle(self.root, tr(self.language, "english"), tr(self.language, "russian"), self.language_var, "en", "ru", command=self.on_language_changed)
        self.lang_toggle.place(x=370, y=162)

        self.folder_label = ttk.Label(
            self.root,
            text=tr(self.language, "game_folder"),
            style="Cyber.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.folder_label.place(x=78, y=220)

        self.folder_btn = CyberButton(
            self.root,
            tr(self.language, "select_game_folder"),
            self.select_game_folder,
            width=250,
            height=42,
            accent=CYBER_ACCENT_2,
        )
        self.folder_btn.place(x=190, y=210)

        self.folder_text_id = self.profile_panel.create_text(
            425,
            121,
            text=self.shorten_path(self.game_folder_var.get()),
            anchor="w",
            fill=CYBER_MUTED,
            font=("Segoe UI", 8),
            width=390,
        )

        self.creator_btn = CyberButton(self.root, tr(self.language, "open_creator"), self.open_mod_creator_window, width=250, accent=CYBER_ACCENT)
        self.creator_btn.place(x=75, y=290)
        self.manager_btn = CyberButton(self.root, tr(self.language, "open_manager"), self.open_mod_manager_window, width=250, accent=CYBER_ACCENT_2)
        self.manager_btn.place(x=335, y=290)
        self.unpack_btn = CyberButton(self.root, tr(self.language, "unpack"), self.start_unpacking, width=250, accent=CYBER_GOOD)
        self.unpack_btn.place(x=595, y=290)

        self.batch_update_btn = CyberButton(
            self.root,
            tr(self.language, "batch_update_files"),
            self.batch_update_files_gui,
            width=250,
            accent=CYBER_ACCENT,
        )
        self.batch_update_btn.place(x=335, y=355)

        self.status_label = ttk.Label(self.root, textvariable=self.status_var, style="Cyber.TLabel", font=("Segoe UI", 10))
        self.status_label.place(x=80, y=448)
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100, length=760, mode="determinate", style="Cyber.Horizontal.TProgressbar")
        self.progress.place(x=80, y=480)

        self.on_profile_changed()

    def shorten_path(self, path, max_len=58):
        path = os.path.normpath(path)
        if len(path) <= max_len:
            return path
        return "..." + path[-max_len:]


    def select_game_folder(self):
        folder = filedialog.askdirectory(
            title=tr(self.language, "select_game_folder_dialog"),
            initialdir=self.game_folder_var.get() or os.getcwd(),
        )
        if not folder:
            return

        self.game_folder_var.set(folder)
        self.profile_panel.itemconfig(self.folder_text_id, text=self.shorten_path(folder))

        if self.mod_manager_window is not None and self.mod_manager_window.winfo_exists():
            self.mod_manager_window.destroy()
            self.mod_manager_window = None

    def draw_background(self):
        self.bg.delete("grid")
        for x in range(0, 930, 40):
            self.bg.create_line(x, 0, x - 180, 620, fill="#0F1726", tags="grid")
        for y in range(0, 640, 40):
            self.bg.create_line(0, y, 920, y, fill="#0C1422", tags="grid")
        self.bg.create_rectangle(20, 20, 900, 600, outline="#1E3750", width=2)
        self.bg.create_line(30, 92, 890, 92, fill=CYBER_ACCENT)

    def on_profile_changed(self):
        self.game_toggle.draw()

    def on_language_changed(self):
        lang = self.language
        self.root.title(f"{tr(lang, 'app_title')}, {self.profile.title}")
        self.bg.itemconfig(self.title_id, text=tr(lang, "app_title"))
        self.bg.itemconfig(self.subtitle_id, text=tr(lang, "subtitle"))
        self.game_label.config(text=tr(lang, "choose_game"))
        self.lang_label.config(text=tr(lang, "choose_language"))
        self.game_toggle.configure_texts(tr(lang, "ascension"), tr(lang, "valkyrie"))
        self.lang_toggle.configure_texts(tr(lang, "english"), tr(lang, "russian"))
        self.creator_btn.configure_text(tr(lang, "open_creator"))
        self.manager_btn.configure_text(tr(lang, "open_manager"))
        self.unpack_btn.configure_text(tr(lang, "unpack"))
        self.batch_update_btn.configure_text(tr(lang, "batch_update_files"))

        self.folder_btn.configure_text(tr(lang, "select_game_folder"))
        self.folder_label.config(text=tr(lang, "game_folder"))

        if not self.is_working:
            self.status_var.set(tr(lang, "idle"))
        self.on_profile_changed()

    def open_mod_manager_window(self):
        if self.mod_manager_window is None or not self.mod_manager_window.winfo_exists():
            self.mod_manager_window = ModManagerWindow(
                self.root,
                self.profile,
                self.language,
                game_folder=self.game_folder_var.get(),
            )
        else:
            self.mod_manager_window.lift()
            self.mod_manager_window.focus_force()

    def open_mod_creator_window(self):
        if self.mod_creator_window is None or not self.mod_creator_window.winfo_exists():
            self.mod_creator_window = ModCreatorWindow(self.root, self.language)
        else:
            self.mod_creator_window.lift()
            self.mod_creator_window.focus_force()

    def batch_update_files_gui(self):
        target_folder = filedialog.askdirectory(title="Step 1: Select the New/Modded folder that needs taildata")
        if not target_folder:
            return

        source_folder = filedialog.askdirectory(title="Step 2: Select the Original folder to copy taildata from")
        if not source_folder:
            return

        packer = ModPacker()
        success_count, skipped_count, errors = packer.batch_transfer_taildata_by_filename(target_folder, source_folder)
        result_msg = f"Successfully updated {success_count} files."
        if skipped_count:
            result_msg += f"\nSkipped/failed {skipped_count} files."
        if errors:
            preview = "\n".join(errors[:40])
            if len(errors) > 40:
                preview += f"\n...and {len(errors) - 40} more."
            result_msg += "\n\nDetails:\n" + preview
        messagebox.showinfo("Batch Update Result", result_msg)

    def set_working(self, working: bool):
        self.is_working = working
        self.unpack_btn.set_enabled(not working)
        self.batch_update_btn.set_enabled(not working)
        self.game_toggle.unbind("<Button-1>") if working else self.game_toggle.bind("<Button-1>", self.game_toggle.click)

    def queue_progress(self, done, total, note=None):
        self.ui_queue.put(("progress", done, total, note))

    def process_ui_queue(self):
        try:
            while True:
                event = self.ui_queue.get_nowait()
                if event[0] == "progress":
                    _kind, done, total, note = event
                    pct = (done / max(1, total)) * 100
                    self.progress_var.set(pct)
                    self.status_var.set(note or f"Working {done}/{total} ({int(pct)}%)")
                elif event[0] == "done":
                    self.progress_var.set(100)
                    self.status_var.set(tr(self.language, "complete"))
                    self.set_working(False)
                elif event[0] == "error":
                    self.set_working(False)
                    self.status_var.set(f"{tr(self.language, 'error')}: {event[1]}")
                    messagebox.showerror(tr(self.language, "error"), str(event[1]))
        except queue.Empty:
            pass
        self.root.after(80, self.process_ui_queue)

    def start_unpacking(self):
        if self.is_working:
            return
        self.set_working(True)
        self.progress_var.set(0)
        self.status_var.set(f"{tr(self.language, 'processing')}: {self.profile.title}")
        profile = self.profile
        game_folder = self.game_folder_var.get()
        thread = threading.Thread(target=self.run_unpack_task, args=(profile, game_folder), daemon=True)
        thread.start()

    def run_unpack_task(self, profile, game_folder):
        try:
            unpacker = BackgroundUnpacker(
                progress_callback=self.queue_progress,
                profile=profile,
                game_folder=game_folder,
            )
            unpacker.unpack_all()
            self.ui_queue.put(("done",))
        except Exception as e:
            self.ui_queue.put(("error", e))
