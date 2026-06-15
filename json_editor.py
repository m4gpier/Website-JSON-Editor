"""
JSON Editor — multi-module (Regalia lore + Art portfolio + future additions)

Folder structure assumed from project root:
  src/regaila/data/   — all Regalia lore JSON files
  src/art/data/       — art.json
"""

import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


# ============================================================
# MODULE & SCHEMA CONFIG
# ============================================================

REGALIA_SCHEMAS = {
    "chapters": {
        "filename": "chapters.json",
        "key": "chapters",
        "image_folder": None,
        "id_prefix": "ch",
        "fields": [
            ("number", "number"),
            ("title", "text"),
            ("summary", "longtext"),
            ("characters", "char_multi"),
            ("isPublic", "bool"),
            ("url", "url_list"),
        ],
    },
    "characters": {
        "filename": "characters.json",
        "key": "characters",
        "image_folder": "/images/characters/",
        "fields": [
            ("id", "text"),
            ("name", "text"),
            ("scale", "float"),
            ("bounce", "bounce"),
            ("firstAppearance", "chapter_ref"),
            ("description", "longtext"),
            ("birthdate", "date"),
            ("bloodType", "text"),
            ("stats", "stats"),
            ("anchors", "anchors"),
            ("dialogue", "string_list"),
            ("relationships", "relationships"),
        ],
    },
    "history": {
        "filename": "history.json",
        "key": "history",
        "image_folder": "/images/history/",
        "fields": [
            ("id", "text"),
            ("name", "text"),
            ("firstAppearance", "chapter_ref"),
            ("description", "longtext"),
        ],
    },
    "items": {
        "filename": "items.json",
        "key": "items",
        "image_folder": "/images/items/",
        "fields": [
            ("id", "text"),
            ("name", "text"),
            ("bounce", "bounce"),
            ("firstAppearance", "chapter_ref"),
            ("description", "longtext"),
        ],
    },
    "places": {
        "filename": "places.json",
        "key": "places",
        "image_folder": "/images/places/",
        "fields": [
            ("id", "text"),
            ("name", "text"),
            ("firstAppearance", "chapter_ref"),
            ("description", "longtext"),
            ("mapPosition", "map_position"),
        ],
    },
}

ART_SCHEMAS = {
    "art": {
        "filename": "art.json",
        "key": "pieces",
        "image_folder": None,
        "fields": [
            ("id", "text"),
            ("title", "text"),
            ("category", "art_category"),
            ("image", "text"),
            ("thumbnail", "text"),
            ("year", "text"),
            ("medium", "text"),
            ("description", "longtext"),
            ("featured", "bool"),
            ("tags", "string_list"),
        ],
    },
}

WRITING_SCHEMAS = {
    "writing": {
        "filename": "writing.json",
        "key": "books",
        "image_folder": None,
        "fields": [
            ("id", "text"),
            ("title", "text"),
            ("type", "writing_type"),
            ("cover", "text"),
            ("spineColor", "text"),
            ("spineTextColor", "text"),
            ("blurb", "longtext"),
            ("links", "writing_links"),
            ("chapters", "writing_chapters"),
            ("year", "text"),
            ("status", "writing_status"),
            ("tags", "string_list"),
        ],
    },
}

# Each module: label shown in UI, subfolder under project root, schemas, extra files.
MODULES = {
    "regalia": {
        "label": "Regalia",
        "subfolder": os.path.join("src", "regaila", "data"),
        "schemas": REGALIA_SCHEMAS,
        "extra_files": ["codes.json", "timeline.json"],
    },
    "art": {
        "label": "Art Portfolio",
        "subfolder": os.path.join("src", "art", "data"),
        "schemas": ART_SCHEMAS,
        "extra_files": [],
    },
    "writing": {
        "label": "Writing",
        "subfolder": os.path.join("src", "writing", "data"),
        "schemas": WRITING_SCHEMAS,
        "extra_files": [],
    },
}

CODES_FILENAME = "codes.json"
TIMELINE_FILENAME = "timeline.json"

# Fields that are optional for art pieces (not shown as required, omitted if blank)
ART_OPTIONAL_FIELDS = {"thumbnail", "medium", "description", "tags"}

# Fields that are optional for writing books (omitted from JSON if blank)
WRITING_OPTIONAL_FIELDS = {"cover", "spineColor", "spineTextColor", "tags", "chapters"}
WRITING_TYPE_OPTIONS = ["serial", "kindle"]
WRITING_STATUS_OPTIONS = ["ongoing", "complete", "hiatus"]

BOUNCE_OPTIONS = ["default", "quick", "slow", "continuous", "sigh", "shake", "rise", "flinch", "float", "none"]
BOUNCE_DESCRIPTIONS = {
    "default": "Default bounce",
    "quick": "Fast sharp bounce",
    "slow": "Big slow bounce",
    "continuous": "Loops forever until swapped",
    "sigh": "Slow squish down then settle back up",
    "shake": "Quick side-to-side wiggle",
    "rise": "Rotates up, holds briefly, returns",
    "flinch": "Quick recoil/pull-back motion",
    "float": "Drifts/bobs continuously",
    "none": "Clicking does nothing (cursor stays default too)",
}

RELATIONSHIP_CATEGORIES = ["Friendly", "Romantic", "Enemy", "Neutral"]


class Tooltip:
    """Simple tooltip that appears on hover."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text, justify="left",
                       background="#1f2937", foreground="white",
                       relief="solid", borderwidth=1,
                       font=("Segoe UI", 9), padx=8, pady=4)
        lbl.pack()

    def _hide(self, _):
        if self.tip:
            self.tip.destroy()
            self.tip = None

    def update_text(self, new_text):
        self.text = new_text


# ============================================================
# JSON I/O
# ============================================================

def load_json(folder, filename):
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        messagebox.showerror("JSON Error", f"Could not parse {filename}:\n{e}")
        return None


def save_json(folder, filename, data):
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_entries(data, key):
    """Handles {"key": [...]}, bare [...], single dict, or None."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if key and key in data and isinstance(data[key], list):
            return data[key]
        for v in data.values():
            if isinstance(v, list):
                return v
        return [data]
    return []


def save_entries(folder, filename, key, entries, original_data):
    if isinstance(original_data, list):
        save_json(folder, filename, entries)
    elif isinstance(original_data, dict) and key in original_data:
        original_data[key] = entries
        save_json(folder, filename, original_data)
    else:
        save_json(folder, filename, {key: entries})


def get_art_categories(folder):
    """Return top-level categories from art.json, excluding 'all'."""
    data = load_json(folder, "art.json")
    if not isinstance(data, dict):
        return []
    cats = data.get("categories", [])
    return [c for c in cats if isinstance(c, str) and c.lower() != "all"]


def get_chapter_lookup(folder):
    data = load_json(folder, "chapters.json")
    lookup = {}
    for ch in get_entries(data, "chapters"):
        num = ch.get("number")
        if num is not None:
            raw_url = ch.get("url", "")
            if isinstance(raw_url, list):
                urls = [u for u in raw_url if u]
            elif isinstance(raw_url, str):
                urls = [raw_url] if raw_url else []
            else:
                urls = []
            lookup[num] = (f"Chapter {num}", urls)
    return lookup


def get_character_ids(folder):
    data = load_json(folder, "characters.json")
    return [c.get("id", "") for c in get_entries(data, "characters") if c.get("id")]


# ============================================================
# Theme
# ============================================================

BG = "#f5f5f7"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#6b7280"


# ============================================================
# Drag-to-reorder helper for Treeview
# ============================================================

class TreeDragReorder:
    def __init__(self, tree):
        self.tree = tree
        self._dragging = False
        self._press_y = None
        self._press_iid = None
        self._indicator_frame = tk.Frame(tree.master, bg="#3b82f6", height=2)

        tree.bind("<ButtonPress-1>", self._on_press, add="+")
        tree.bind("<B1-Motion>", self._on_motion, add="+")
        tree.bind("<ButtonRelease-1>", self._on_release, add="+")

    def _on_press(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self._press_y = event.y
        self._press_iid = iid
        self._dragging = False

    def _on_motion(self, event):
        if self._press_iid is None:
            return
        if not self._dragging:
            if abs(event.y - self._press_y) < 5:
                return
            self._dragging = True
            sel = self.tree.selection()
            if self._press_iid not in sel:
                self.tree.selection_set(self._press_iid)
        target_iid = self.tree.identify_row(event.y)
        self._show_indicator(event.y, target_iid)

    def _on_release(self, event):
        if not self._dragging:
            self._press_iid = None
            self._press_y = None
            self._hide_indicator()
            return
        try:
            self._do_drop(event.y)
        finally:
            self._dragging = False
            self._press_iid = None
            self._press_y = None
            self._hide_indicator()

    def _show_indicator(self, y, target_iid):
        tree = self.tree
        if target_iid:
            bbox = tree.bbox(target_iid)
            if bbox:
                bx, by, bw, bh = bbox
                line_y = by if y < by + bh / 2 else by + bh
                self._indicator_frame.place(
                    x=tree.winfo_x() + bx, y=tree.winfo_y() + line_y,
                    width=bw, height=2)
                return
        children = tree.get_children("")
        if children:
            last_bbox = tree.bbox(children[-1])
            if last_bbox:
                bx, by, bw, bh = last_bbox
                self._indicator_frame.place(
                    x=tree.winfo_x() + bx, y=tree.winfo_y() + by + bh,
                    width=bw, height=2)

    def _hide_indicator(self):
        self._indicator_frame.place_forget()

    def _do_drop(self, y):
        tree = self.tree
        moving = list(tree.selection())
        if not moving:
            return
        all_children = list(tree.get_children(""))
        moving_in_order = [iid for iid in all_children if iid in set(moving)]
        target_iid = tree.identify_row(y)
        if target_iid:
            bbox = tree.bbox(target_iid)
            drop_before = (y < bbox[1] + bbox[3] / 2) if bbox else True
            target_index = all_children.index(target_iid)
            if not drop_before:
                target_index += 1
        else:
            target_index = len(all_children)
        remaining = [iid for iid in all_children if iid not in set(moving_in_order)]
        original_target_iid = all_children[target_index] if 0 <= target_index < len(all_children) else None
        if original_target_iid is None:
            new_index = len(remaining)
        else:
            new_index = remaining.index(original_target_iid) if original_target_iid in remaining else len(remaining)
        new_order = remaining[:new_index] + moving_in_order + remaining[new_index:]
        for i, iid in enumerate(new_order):
            tree.move(iid, "", i)
        tree.selection_set(moving_in_order)


# ============================================================
# App
# ============================================================

class JSONEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project JSON Editor")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG)
        self.project_root = None  # the folder the user picks

        self._setup_styles()
        self.build_folder_picker()

    def module_folder(self, module_key):
        """Resolve the data folder for a given module."""
        return os.path.join(self.project_root, MODULES[module_key]["subfolder"])

    def _regalia_folder(self):
        return self.module_folder("regalia")

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT,
                        font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED,
                        font=("Segoe UI", 10))
        style.configure("Heading.TLabel", background=CARD, foreground=TEXT,
                        font=("Segoe UI", 14, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Sort.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8),
                        foreground="#ffffff", background="#16a34a")
        style.map("Sort.TButton",
                  background=[("active", "#15803d"), ("pressed", "#15803d")])
        style.configure("Module.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 12, "bold"))
        style.configure("TCheckbutton", background=CARD)

    # ============================================================
    # Folder picker
    # ============================================================
    def build_folder_picker(self):
        self.clear_root()
        outer = ttk.Frame(self.root, padding=40)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Project JSON Editor", style="Title.TLabel").pack(pady=(40, 8))
        ttk.Label(outer, text="Select the project root folder.",
                  style="Subtitle.TLabel").pack(pady=(0, 4))
        ttk.Label(outer, text="Expected layout:  src/regaila/data/   •   src/art/data/",
                  style="Subtitle.TLabel").pack(pady=(0, 20))
        ttk.Button(outer, text="Choose Project Root…",
                   style="Accent.TButton", command=self.pick_folder).pack()

        if self.project_root:
            ttk.Label(outer, text=f"Last: {self.project_root}",
                      style="Subtitle.TLabel").pack(pady=(20, 0))

    def pick_folder(self):
        while True:
            folder = filedialog.askdirectory(title="Select project root folder")
            if not folder:
                return

            missing_by_module = {}
            for mk, mod in MODULES.items():
                mfolder = os.path.join(folder, mod["subfolder"])
                expected = (
                    [s["filename"] for s in mod["schemas"].values()] +
                    mod["extra_files"]
                )
                missing = [f for f in expected if not os.path.exists(os.path.join(mfolder, f))]
                if missing:
                    missing_by_module[mod["label"]] = missing

            if not missing_by_module:
                self.project_root = folder
                self.build_main_menu()
                return

            lines = []
            for label, files in missing_by_module.items():
                lines.append(f"  [{label}]  {', '.join(files)}")
            msg = ("Missing expected files:\n\n" + "\n".join(lines) +
                   "\n\nYes = use anyway (missing created on save)\n"
                   "No = pick different folder\nCancel = quit")
            choice = messagebox.askyesnocancel("Missing files", msg)
            if choice is True:
                self.project_root = folder
                self.build_main_menu()
                return
            if choice is None:
                return

    # ============================================================
    # Main menu — grouped by module
    # ============================================================
    def build_main_menu(self):
        self.clear_root()
        container = ttk.Frame(self.root, padding=30)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Project JSON Editor", style="Title.TLabel").pack(anchor="w")
        ttk.Label(container, text=self.project_root, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 24))

        for mk, mod in MODULES.items():
            section = ttk.Frame(container)
            section.pack(fill="x", pady=(0, 16))

            ttk.Label(section, text=mod["label"], style="Module.TLabel").pack(anchor="w", pady=(0, 6))
            ttk.Separator(section, orient="horizontal").pack(fill="x", pady=(0, 8))

            grid = ttk.Frame(section)
            grid.pack(fill="x")

            buttons = [
                (f"{fk}.json", lambda fk=fk, mk=mk: self.open_list_view(mk, fk))
                for fk in mod["schemas"]
            ]
            if mk == "regalia":
                buttons.append(("codes.json", self.open_codes_view))
                buttons.append(("timeline.json", self.open_timeline_view))

            for i, (label, cmd) in enumerate(buttons):
                b = ttk.Button(grid, text=label, command=cmd, width=22, style="Accent.TButton")
                b.grid(row=i // 3, column=i % 3, padx=6, pady=4, sticky="ew")
            for c in range(3):
                grid.columnconfigure(c, weight=1)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(8, 12))
        ttk.Button(container, text="Change Folder",
                   command=self.build_folder_picker).pack(anchor="w")

    # ============================================================
    # List view
    # ============================================================
    def open_list_view(self, module_key, file_key):
        self.clear_root()
        mod = MODULES[module_key]
        schema = mod["schemas"][file_key]
        folder = self.module_folder(module_key)
        data = load_json(folder, schema["filename"])
        entries = get_entries(data, schema["key"])

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Back", command=self.build_main_menu).pack(side="left")
        ttk.Label(header, text=f"{mod['label']}  /  {file_key}.json",
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)
        ttk.Label(header, text=f"{len(entries)} entries",
                  style="Subtitle.TLabel").pack(side="left")

        if not entries:
            ttk.Label(container,
                      text="No entries in this file yet. Click '+ Add New' below.",
                      style="Subtitle.TLabel").pack(pady=10)

        list_card = ttk.Frame(container, style="Card.TFrame", padding=10)
        list_card.pack(fill="both", expand=True, pady=(0, 15))

        is_chapters = file_key == "chapters"
        is_art = file_key == "art"
        is_writing = file_key == "writing"

        if is_art:
            third_col_label = "Category"
            third_col_key = "category"
        elif is_writing:
            third_col_label = "Type / Status"
            third_col_key = "type"
        elif is_chapters:
            third_col_label = "Summary"
            third_col_key = "summary"
        else:
            third_col_label = "First Appearance"
            third_col_key = "firstAppearance"

        cols = ("id", "name", "third")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=18,
                            selectmode="extended")
        tree.heading("id", text="ID / Number",
                     command=lambda: self._sort_tree(tree, "id", False))
        tree.heading("name", text="Name / Title",
                     command=lambda: self._sort_tree(tree, "name", False))
        tree.heading("third", text=third_col_label,
                     command=lambda: self._sort_tree(tree, "third", False))
        tree.column("id", width=120, anchor="w")
        tree.column("name", width=250, anchor="w")
        tree.column("third", width=450, anchor="w")

        sb = ttk.Scrollbar(list_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def snippet(text, words=12):
            if not text:
                return ""
            parts = text.split()
            if len(parts) <= words:
                return text
            return " ".join(parts[:words]) + "…"

        for idx, e in enumerate(entries):
            identifier = e.get("id") or e.get("number") or "?"
            name = e.get("name") or e.get("title") or ""
            if is_writing:
                third_val = f"{e.get('type', '')}  •  {e.get('status', '')}"
            else:
                third_val = e.get(third_col_key, "")
            if is_chapters:
                third_val = snippet(third_val)
            tree.insert("", "end", iid=str(idx), values=(identifier, name, third_val))

        TreeDragReorder(tree)

        def on_double_click(ev, mk=module_key, fk=file_key, t=tree):
            if t.identify_region(ev.x, ev.y) != "cell":
                return
            self._edit_tree_selection(mk, fk, t, silent=True)
        tree.bind("<Double-1>", on_double_click)

        def do_sort():
            if not messagebox.askyesno(
                "Sort JSON",
                f"This will rewrite {schema['filename']} so entries appear in "
                f"the order shown in the list above.\n\nProceed?"
            ):
                return
            iid_order = list(tree.get_children(""))
            new_entries = [entries[int(iid)] for iid in iid_order]
            save_entries(folder, schema["filename"], schema["key"],
                         new_entries, data)
            messagebox.showinfo(
                "Sorted",
                f"{schema['filename']} reordered ({len(new_entries)} entries)."
            )
            self.open_list_view(module_key, file_key)

        btns = ttk.Frame(container)
        btns.pack(fill="x")
        ttk.Button(btns, text="+ Add New", style="Accent.TButton",
                   command=lambda: self.open_entry_editor(module_key, file_key, None)).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Edit Selected",
                   command=lambda: self._edit_tree_selection(module_key, file_key, tree)).pack(side="left", padx=6)
        ttk.Button(btns, text="Delete Selected",
                   command=lambda: self._delete_tree_selection(module_key, file_key, tree)).pack(side="left", padx=6)
        ttk.Button(btns, text="⇅ SORT", style="Sort.TButton",
                   command=do_sort).pack(side="right")

        ttk.Label(container,
                  text="Tip: double-click to edit • drag rows to reorder "
                       "• Shift/Ctrl-click for multi-select • SORT writes the "
                       "current order to JSON",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(10, 0))

    def _edit_tree_selection(self, module_key, file_key, tree, silent=False):
        sel = tree.selection()
        if not sel:
            if not silent:
                messagebox.showinfo("No selection", "Pick an entry first.")
            return
        self.open_entry_editor(module_key, file_key, int(sel[0]))

    def _delete_tree_selection(self, module_key, file_key, tree):
        sel = tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Delete", "Delete this entry?"):
            return
        mod = MODULES[module_key]
        schema = mod["schemas"][file_key]
        folder = self.module_folder(module_key)
        data = load_json(folder, schema["filename"])
        entries = get_entries(data, schema["key"])
        del entries[int(sel[0])]
        save_entries(folder, schema["filename"], schema["key"], entries, data)
        self.open_list_view(module_key, file_key)

    # ============================================================
    # Entry editor
    # ============================================================
    def open_entry_editor(self, module_key, file_key, index):
        self.clear_root()
        mod = MODULES[module_key]
        schema = mod["schemas"][file_key]
        folder = self.module_folder(module_key)
        data = load_json(folder, schema["filename"])
        entries = get_entries(data, schema["key"])

        is_new = index is None
        entry = {} if is_new else dict(entries[index])

        # Regalia-specific lookups (no-ops for other modules)
        regalia_folder = self.module_folder("regalia")
        chapter_lookup = get_chapter_lookup(regalia_folder)
        char_ids = get_character_ids(regalia_folder)
        art_categories = get_art_categories(folder) if file_key == "art" else []

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Cancel",
                   command=lambda: self.open_list_view(module_key, file_key)).pack(side="left")
        title = f"New {file_key}" if is_new else f"Edit: {entry.get('id') or entry.get('number')}"
        ttk.Label(header, text=title, font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        form = ttk.Frame(canvas, style="Card.TFrame", padding=20)
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(form_window, width=event.width)
        canvas.bind("<Configure>", on_configure)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        widgets = {}
        row = 0

        for field, wtype in schema["fields"]:
            is_optional = (
                (file_key == "art" and field in ART_OPTIONAL_FIELDS) or
                (file_key == "writing" and field in WRITING_OPTIONAL_FIELDS)
            )
            label_text = f"{field} (optional)" if is_optional else field

            ttk.Label(form, text=label_text, style="Card.TLabel",
                      font=("Segoe UI", 10, "bold")).grid(
                row=row, column=0, sticky="nw", padx=(0, 15), pady=(10, 2))
            value = entry.get(field, "")

            if wtype == "text":
                var = tk.StringVar(value=str(value) if value else "")

                if field == "id":
                    sub = ttk.Frame(form, style="Card.TFrame")
                    sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                    ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    warn_lbl = tk.Label(sub, text="", bg=CARD, fg="#dc2626",
                                        font=("Segoe UI", 9, "bold"))
                    warn_lbl.pack(side="left", padx=8)

                    existing_ids = {e.get("id", "") for i, e in enumerate(entries)
                                    if (is_new or i != index) and e.get("id")}

                    def check_dup(*_, v=var, w=warn_lbl):
                        val = v.get().strip()
                        if val and val in existing_ids:
                            w.config(text=f"⚠ ID '{val}' already exists!")
                        else:
                            w.config(text="")
                    var.trace_add("write", check_dup)
                    check_dup()

                elif file_key == "art" and field == "image":
                    sub = ttk.Frame(form, style="Card.TFrame")
                    sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                    ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    img_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                    img_warn.pack(side="left", padx=8)

                    def check_image_path(*_, v=var, w=img_warn):
                        val = v.get().strip()
                        w.config(text="⚠ Path should start with /art/" if (val and not val.startswith("/art/")) else "")
                    var.trace_add("write", check_image_path)
                    check_image_path()

                elif file_key == "art" and field == "thumbnail":
                    sub = ttk.Frame(form, style="Card.TFrame")
                    sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                    ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    thumb_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                    thumb_warn.pack(side="left", padx=8)
                    ttk.Label(sub, text="(falls back to image if blank)",
                              style="Card.TLabel", foreground=MUTED).pack(side="left", padx=4)

                    def check_thumb_path(*_, v=var, w=thumb_warn):
                        val = v.get().strip()
                        w.config(text="⚠ Path should start with /art/" if (val and not val.startswith("/art/")) else "")
                    var.trace_add("write", check_thumb_path)
                    check_thumb_path()

                elif file_key == "writing" and field == "cover":
                    sub = ttk.Frame(form, style="Card.TFrame")
                    sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                    ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    cover_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                    cover_warn.pack(side="left", padx=8)

                    def check_cover_path(*_, v=var, w=cover_warn):
                        val = v.get().strip()
                        w.config(text="⚠ Path should start with /writing/" if (val and not val.startswith("/writing/")) else "")
                    var.trace_add("write", check_cover_path)
                    check_cover_path()

                elif file_key == "writing" and field in ("spineColor", "spineTextColor"):
                    sub = ttk.Frame(form, style="Card.TFrame")
                    sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                    ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10), width=12).pack(side="left")
                    ttk.Label(sub, text="(hex, e.g. #1a0a2e — leave blank to auto-generate)",
                              style="Card.TLabel", foreground=MUTED).pack(side="left", padx=8)

                else:
                    ttk.Entry(form, textvariable=var, font=("Segoe UI", 10)).grid(
                        row=row, column=1, sticky="ew", pady=(10, 2))

                widgets[field] = lambda v=var: v.get()

            elif wtype == "art_category":
                # Dropdown from top-level categories (excluding 'all'), with warning if not found
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                current_cat = str(value) if value else ""
                cat_var = tk.StringVar(value=current_cat)

                if art_categories:
                    combo = ttk.Combobox(sub, textvariable=cat_var, values=art_categories,
                                         font=("Segoe UI", 10), width=25)
                    combo.pack(side="left")
                else:
                    ttk.Entry(sub, textvariable=cat_var, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    ttk.Label(sub, text="(no categories found in art.json)",
                              style="Card.TLabel", foreground=MUTED).pack(side="left", padx=4)

                cat_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                cat_warn.pack(side="left", padx=8)

                def check_category(*_, v=cat_var, w=cat_warn, cats=art_categories):
                    val = v.get().strip()
                    if val and cats and val not in cats:
                        w.config(text=f"⚠ '{val}' not in categories list")
                    else:
                        w.config(text="")
                cat_var.trace_add("write", check_category)
                check_category()

                widgets[field] = lambda v=cat_var: v.get()

            elif wtype == "int":
                var = tk.StringVar(value=str(value) if value != "" else "")
                ttk.Entry(form, textvariable=var, font=("Segoe UI", 10), width=15).grid(
                    row=row, column=1, sticky="w", pady=(10, 2))
                widgets[field] = lambda v=var: int(v.get()) if v.get().strip() else None

            elif wtype == "number":
                var = tk.StringVar(value=str(value) if value != "" else "")
                ttk.Entry(form, textvariable=var, font=("Segoe UI", 10), width=15).grid(
                    row=row, column=1, sticky="w", pady=(10, 2))

                def num_getter(v=var):
                    s = v.get().strip()
                    if not s:
                        return None
                    try:
                        f = float(s)
                        return int(f) if f.is_integer() else f
                    except ValueError:
                        return None
                widgets[field] = num_getter

            elif wtype == "longtext":
                txt = scrolledtext.ScrolledText(form, height=6, wrap="word",
                                                font=("Segoe UI", 10))
                txt.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                if value:
                    txt.insert("1.0", value)
                widgets[field] = lambda t=txt: t.get("1.0", "end").strip()

            elif wtype == "bool":
                var = tk.BooleanVar(value=bool(value))
                ttk.Checkbutton(form, variable=var).grid(
                    row=row, column=1, sticky="w", pady=(10, 2))
                widgets[field] = lambda v=var: v.get()

            elif wtype == "bounce":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                current = value if value in BOUNCE_OPTIONS else "default"
                var = tk.StringVar(value=current)
                combo = ttk.Combobox(sub, textvariable=var, values=BOUNCE_OPTIONS,
                                     state="readonly", font=("Segoe UI", 10), width=15)
                combo.pack(side="left")
                desc_lbl = ttk.Label(sub, text=BOUNCE_DESCRIPTIONS.get(current, ""),
                                     style="Card.TLabel", foreground=MUTED)
                desc_lbl.pack(side="left", padx=10)
                tip = Tooltip(combo, BOUNCE_DESCRIPTIONS.get(current, ""))

                def update_desc(*_, v=var, d=desc_lbl, t=tip):
                    text = BOUNCE_DESCRIPTIONS.get(v.get(), "")
                    d.config(text=text)
                    t.update_text(text)
                var.trace_add("write", update_desc)
                widgets[field] = lambda v=var: v.get()

            elif wtype == "float":
                var = tk.StringVar(value=str(value) if value != "" else "1.0")
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="w", pady=(10, 2))
                ttk.Entry(sub, textvariable=var, font=("Segoe UI", 10), width=10).pack(side="left")
                ttk.Label(sub, text="(decimal, e.g. 1.0)",
                          style="Card.TLabel", foreground=MUTED).pack(side="left", padx=8)

                def float_getter(v=var):
                    s = v.get().strip()
                    if not s:
                        return None
                    try:
                        return float(s)
                    except ValueError:
                        return None
                widgets[field] = float_getter

            elif wtype == "date":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="w", pady=(10, 2))
                raw_value = str(value) if value else ""
                is_bh = raw_value.startswith("B")
                date_part = raw_value[1:] if is_bh else raw_value
                date_var = tk.StringVar(value=date_part)
                bh_var = tk.BooleanVar(value=is_bh)
                ttk.Entry(sub, textvariable=date_var, font=("Segoe UI", 10), width=15).pack(side="left")
                ttk.Label(sub, text="(YYYY-MM-DD)",
                          style="Card.TLabel", foreground=MUTED).pack(side="left", padx=8)
                ttk.Checkbutton(sub, text="BH (Before Heaven)",
                                variable=bh_var).pack(side="left", padx=8)
                preview = ttk.Label(sub, text="", style="Card.TLabel", foreground=MUTED)
                preview.pack(side="left", padx=8)

                def update_preview(*_, dv=date_var, bv=bh_var, p=preview):
                    d = dv.get().strip()
                    if not d:
                        p.config(text="")
                        return
                    if bv.get():
                        parts = d.split("-")
                        year = parts[0].lstrip("0") or "0"
                        rest = "-".join(parts[1:])
                        p.config(text=f"→ {year}{('-' + rest) if rest else ''} BH")
                    else:
                        p.config(text=f"→ {d}")
                date_var.trace_add("write", update_preview)
                bh_var.trace_add("write", update_preview)
                update_preview()

                def date_getter(dv=date_var, bv=bh_var):
                    d = dv.get().strip()
                    if not d:
                        return None
                    return ("B" + d) if bv.get() else d
                widgets[field] = date_getter

            elif wtype == "stats":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                stat_names = ["strength", "speed", "intelligence", "magic"]
                stat_vars = {}
                current_stats = value if isinstance(value, dict) else {}
                for sname in stat_names:
                    row_frame = ttk.Frame(sub, style="Card.TFrame")
                    row_frame.pack(fill="x", pady=2)
                    ttk.Label(row_frame, text=f"{sname}:", style="Card.TLabel",
                              width=13, anchor="w").pack(side="left")
                    sv = tk.IntVar(value=int(current_stats.get(sname, 0)))
                    scale = tk.Scale(row_frame, from_=0, to=6, orient="horizontal",
                                     variable=sv, length=200, resolution=1,
                                     bg=CARD, highlightthickness=0, showvalue=True)
                    scale.pack(side="left")
                    stat_vars[sname] = sv
                ttk.Label(sub, text="(each stat 0–6)",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(4, 0))
                widgets[field] = lambda sv=stat_vars: {k: v.get() for k, v in sv.items()}

            elif wtype == "anchors":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                anchor_state = {}
                if isinstance(value, dict):
                    for aname, coord in value.items():
                        if isinstance(coord, dict):
                            try:
                                anchor_state[aname] = {
                                    "x": int(coord.get("x", 0)),
                                    "y": int(coord.get("y", 0)),
                                }
                            except (TypeError, ValueError):
                                pass
                ttk.Label(sub, text="One per line: name x y   (e.g. face 300 120)",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w")
                anchor_txt = tk.Text(sub, height=4, wrap="word", font=("Consolas", 10))
                anchor_txt.pack(fill="x")

                def refresh_text(_txt=anchor_txt, _state=anchor_state):
                    _txt.delete("1.0", "end")
                    lines = [f"{n} {c['x']} {c['y']}" for n, c in _state.items()]
                    _txt.insert("1.0", "\n".join(lines))
                refresh_text()

                btn_frame = ttk.Frame(sub, style="Card.TFrame")
                btn_frame.pack(anchor="w", pady=(6, 0))

                def get_current_id():
                    if "id" in widgets:
                        try:
                            v = widgets["id"]()
                            if v:
                                return v
                        except Exception:
                            pass
                    return entry.get("id", "")

                def open_visual_editor(_state=anchor_state, _refresh=refresh_text):
                    eid = get_current_id()
                    if not eid:
                        messagebox.showerror("No ID", "Please set an ID first.")
                        return
                    self._open_anchor_editor(eid, _state, on_done=_refresh)

                ttk.Button(btn_frame, text="🖼  Open Visual Editor",
                           command=open_visual_editor).pack(side="left")

                def anchor_getter(t=anchor_txt, state=anchor_state):
                    result = {}
                    for ln in t.get("1.0", "end").splitlines():
                        parts = ln.strip().split()
                        if len(parts) == 3:
                            try:
                                result[parts[0]] = {
                                    "x": int(parts[1]),
                                    "y": int(parts[2]),
                                }
                            except ValueError:
                                pass
                    state.clear()
                    state.update(result)
                    return result
                widgets[field] = anchor_getter

            elif wtype == "url_list":
                if isinstance(value, list):
                    url_initial = [str(u) for u in value if u]
                elif isinstance(value, str) and value.strip():
                    url_initial = [value.strip()]
                else:
                    url_initial = []

                url_frame = ttk.Frame(form, style="Card.TFrame")
                url_frame.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                url_rows_container = ttk.Frame(url_frame, style="Card.TFrame")
                url_rows_container.pack(fill="x")
                url_rows = []

                def add_url_row(initial="", rc=url_rows_container, rows=url_rows):
                    r = ttk.Frame(rc, style="Card.TFrame")
                    r.pack(fill="x", pady=2)
                    v = tk.StringVar(value=initial)
                    ttk.Entry(r, textvariable=v, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    rd = {"var": v, "frame": r}
                    def remove(_rd=rd):
                        _rd["frame"].destroy()
                        rows.remove(_rd)
                    ttk.Button(r, text="✕", width=3, command=remove).pack(
                        side="left", padx=(4, 0))
                    rows.append(rd)

                for u in url_initial:
                    add_url_row(u)
                if not url_initial:
                    add_url_row("")

                ttk.Button(url_frame, text="+ Add URL",
                           command=lambda: add_url_row("")).pack(anchor="w", pady=(4, 0))
                ttk.Label(url_frame,
                          text="One URL per row. Saved as a list, even with a single URL.",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(2, 0))

                def url_list_getter(rows=url_rows):
                    return [r["var"].get().strip() for r in rows if r["var"].get().strip()]
                widgets[field] = url_list_getter

            elif wtype == "string_list":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                ttk.Label(sub, text="One line per entry",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w")
                txt = tk.Text(sub, height=5, wrap="word", font=("Segoe UI", 10))
                txt.pack(fill="x")
                if isinstance(value, list):
                    txt.insert("1.0", "\n".join(str(x) for x in value))
                widgets[field] = lambda t=txt: [
                    ln for ln in t.get("1.0", "end").splitlines() if ln.strip()
                ]

            elif wtype == "relationships":
                rel_frame = ttk.Frame(form, style="Card.TFrame")
                rel_frame.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                ttk.Label(rel_frame,
                          text="Press Tab in the ID field to autocomplete from characters.json",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w")
                rows_container = ttk.Frame(rel_frame, style="Card.TFrame")
                rows_container.pack(fill="x", pady=(4, 4))
                hdr = ttk.Frame(rows_container, style="Card.TFrame")
                hdr.pack(fill="x", pady=(0, 4))
                ttk.Label(hdr, text="Character ID", style="Card.TLabel",
                          font=("Segoe UI", 9, "bold"), width=18).pack(side="left")
                ttk.Label(hdr, text="Category", style="Card.TLabel",
                          font=("Segoe UI", 9, "bold"), width=14).pack(side="left", padx=4)
                ttk.Label(hdr, text="Tier", style="Card.TLabel",
                          font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)
                rel_rows = []

                def add_row(rid="", category="Neutral", tier=""):
                    row_frame = ttk.Frame(rows_container, style="Card.TFrame")
                    row_frame.pack(fill="x", pady=2)
                    id_var = tk.StringVar(value=rid)
                    id_entry = ttk.Entry(row_frame, textvariable=id_var,
                                         font=("Segoe UI", 10), width=18)
                    id_entry.pack(side="left")
                    cycle_state = {"stem": None, "matches": [], "idx": -1}

                    def on_tab(event, v=id_var, e=id_entry, st=cycle_state):
                        cur = v.get()
                        if st["matches"] and cur in st["matches"]:
                            st["idx"] = (st["idx"] + 1) % len(st["matches"])
                            v.set(st["matches"][st["idx"]])
                            e.icursor("end")
                        else:
                            stem = cur.strip()
                            if not stem:
                                return "break"
                            matches = [c for c in char_ids if c.startswith(stem)]
                            if matches:
                                st["stem"] = stem
                                st["matches"] = matches
                                st["idx"] = 0
                                v.set(matches[0])
                                e.icursor("end")
                        return "break"

                    def on_key(event, st=cycle_state):
                        if event.keysym not in ("Tab", "Shift_L", "Shift_R"):
                            st["matches"] = []
                            st["idx"] = -1

                    id_entry.bind("<Tab>", on_tab)
                    id_entry.bind("<KeyPress>", on_key, add="+")
                    cat = category if category in RELATIONSHIP_CATEGORIES else "Neutral"
                    cat_var = tk.StringVar(value=cat)
                    cat_combo = ttk.Combobox(row_frame, textvariable=cat_var,
                                             values=RELATIONSHIP_CATEGORIES,
                                             state="readonly",
                                             font=("Segoe UI", 10), width=12)
                    cat_combo.pack(side="left", padx=4)
                    tier_var = tk.StringVar(value=tier)
                    tier_entry = ttk.Entry(row_frame, textvariable=tier_var,
                                           font=("Segoe UI", 10))
                    tier_entry.pack(side="left", fill="x", expand=True, padx=4)
                    row_data = {"id_var": id_var, "cat_var": cat_var,
                                "tier_var": tier_var, "frame": row_frame}

                    def remove_this(rd=row_data):
                        rd["frame"].destroy()
                        rel_rows.remove(rd)
                    ttk.Button(row_frame, text="✕", width=3,
                               command=remove_this).pack(side="left")
                    rel_rows.append(row_data)

                if isinstance(value, dict):
                    for rid, info in value.items():
                        if isinstance(info, dict):
                            add_row(rid,
                                    info.get("category", "Neutral"),
                                    info.get("tier", ""))
                add_btn_frame = ttk.Frame(rel_frame, style="Card.TFrame")
                add_btn_frame.pack(anchor="w")
                ttk.Button(add_btn_frame, text="+ Add Relationship",
                           command=lambda: add_row()).pack(side="left")

                def relationship_getter():
                    result = {}
                    for r in rel_rows:
                        rid = r["id_var"].get().strip()
                        if not rid:
                            continue
                        result[rid] = {
                            "category": r["cat_var"].get(),
                            "tier": r["tier_var"].get().strip(),
                        }
                    return result
                widgets[field] = relationship_getter

            elif wtype == "map_position":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                init_x = 0
                init_y = 0
                if isinstance(value, dict):
                    try:
                        init_x = int(value.get("x", 0))
                        init_y = int(value.get("y", 0))
                    except (TypeError, ValueError):
                        pass
                x_var = tk.StringVar(value=str(init_x))
                y_var = tk.StringVar(value=str(init_y))
                row1 = ttk.Frame(sub, style="Card.TFrame")
                row1.pack(fill="x")
                ttk.Label(row1, text="x:", style="Card.TLabel").pack(side="left")
                ttk.Entry(row1, textvariable=x_var, font=("Segoe UI", 10), width=8).pack(side="left", padx=(4, 12))
                ttk.Label(row1, text="y:", style="Card.TLabel").pack(side="left")
                ttk.Entry(row1, textvariable=y_var, font=("Segoe UI", 10), width=8).pack(side="left", padx=4)

                def open_map_picker(xv=x_var, yv=y_var):
                    try:
                        cx = int(xv.get())
                        cy = int(yv.get())
                    except ValueError:
                        cx, cy = 0, 0
                    result = self._open_map_picker(cx, cy)
                    if result is not None:
                        nx, ny = result
                        xv.set(str(nx))
                        yv.set(str(ny))

                ttk.Button(row1, text="🗺  Pick on Map",
                           command=open_map_picker).pack(side="left", padx=12)

                def map_pos_getter(xv=x_var, yv=y_var):
                    try:
                        return {"x": int(xv.get()), "y": int(yv.get())}
                    except ValueError:
                        return {"x": 0, "y": 0}
                widgets[field] = map_pos_getter

            elif wtype == "chapter_ref":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                stored_label = ""
                stored_urls = []
                if isinstance(value, str) and value.strip():
                    stored_label = value.strip()
                    raw_stored_url = entry.get(field + "Url", "")
                    if isinstance(raw_stored_url, list):
                        stored_urls = [u for u in raw_stored_url if u]
                    elif isinstance(raw_stored_url, str) and raw_stored_url:
                        stored_urls = [raw_stored_url]
                label_var = tk.StringVar(value=stored_label)
                row1 = ttk.Frame(sub, style="Card.TFrame")
                row1.pack(fill="x")
                ttk.Label(row1, text="Chapter #:", style="Card.TLabel").pack(side="left")
                num_var = tk.StringVar()
                if stored_label.lower().startswith("chapter "):
                    try:
                        tail = stored_label.split(None, 1)[1].strip()
                        float(tail)
                        num_var.set(tail)
                    except (IndexError, ValueError):
                        pass
                num_entry = ttk.Entry(row1, textvariable=num_var, width=8,
                                      font=("Segoe UI", 10))
                num_entry.pack(side="left", padx=(4, 8))
                autofill_status = ttk.Label(row1, text="", style="Card.TLabel",
                                            foreground=MUTED)
                autofill_status.pack(side="left")
                row2 = ttk.Frame(sub, style="Card.TFrame")
                row2.pack(fill="x", pady=(6, 0))
                ttk.Label(row2, text="Text:", style="Card.TLabel", width=6).pack(side="left")
                ttk.Entry(row2, textvariable=label_var, font=("Segoe UI", 10)).pack(
                    side="left", fill="x", expand=True, padx=4)
                ttk.Label(sub, text="URLs:", style="Card.TLabel",
                          font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
                url_rows_container = ttk.Frame(sub, style="Card.TFrame")
                url_rows_container.pack(fill="x")
                url_rows = []

                def add_url_row(initial="", rc=url_rows_container, rows=url_rows):
                    r = ttk.Frame(rc, style="Card.TFrame")
                    r.pack(fill="x", pady=2)
                    v = tk.StringVar(value=initial)
                    ttk.Entry(r, textvariable=v, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    rd = {"var": v, "frame": r}
                    def remove(_rd=rd):
                        _rd["frame"].destroy()
                        rows.remove(_rd)
                    ttk.Button(r, text="✕", width=3, command=remove).pack(
                        side="left", padx=(4, 0))
                    rows.append(rd)

                for u in stored_urls:
                    add_url_row(u)
                if not stored_urls:
                    add_url_row("")

                ttk.Button(sub, text="+ Add URL",
                           command=lambda: add_url_row("")).pack(anchor="w", pady=(4, 0))
                ttk.Label(sub,
                          text="Enter a chapter # to autofill text+URLs, or fill manually",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(4, 0))

                def autofill(*_, nv=num_var, lv=label_var, rows=url_rows,
                             rc=url_rows_container, st=autofill_status,
                             cl=chapter_lookup):
                    raw = nv.get().strip()
                    if not raw:
                        st.config(text="")
                        return
                    try:
                        f = float(raw)
                        n = int(f) if f.is_integer() else f
                        if n in cl:
                            ch_label, ch_urls = cl[n]
                            lv.set(ch_label)
                            for rd in list(rows):
                                rd["frame"].destroy()
                            rows.clear()
                            for u in ch_urls:
                                add_url_row(u, rc=rc, rows=rows)
                            if not ch_urls:
                                add_url_row("", rc=rc, rows=rows)
                            st.config(text="✓ autofilled", foreground="#059669")
                            return
                    except ValueError:
                        pass
                    st.config(text="✗ not found", foreground="#dc2626")

                num_var.trace_add("write", autofill)

                def getter(lv=label_var, rows=url_rows):
                    lbl = lv.get().strip()
                    urls = [r["var"].get().strip() for r in rows if r["var"].get().strip()]
                    return (lbl or None, urls)
                widgets[field] = getter

            elif wtype == "char_multi":
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                ttk.Label(sub, text="One character ID per line (press Tab to autocomplete)",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w")
                txt = tk.Text(sub, height=5, wrap="word", font=("Segoe UI", 10))
                txt.pack(fill="x")
                if isinstance(value, list):
                    txt.insert("1.0", "\n".join(value))
                cm_cycle = {"line": None, "stem": None, "matches": [], "idx": -1}

                def autocomplete(event, t=txt, st=cm_cycle):
                    idx = t.index("insert")
                    line_start = t.index(f"{idx} linestart")
                    current = t.get(line_start, idx)
                    same_line = (st["line"] == line_start)
                    on_a_match = (same_line and st["matches"] and
                                  current in st["matches"])
                    if on_a_match:
                        st["idx"] = (st["idx"] + 1) % len(st["matches"])
                        t.delete(line_start, idx)
                        t.insert(line_start, st["matches"][st["idx"]])
                    else:
                        stem = current.strip()
                        if not stem:
                            return "break"
                        matches = [c for c in char_ids if c.startswith(stem)]
                        if matches:
                            st["line"] = line_start
                            st["stem"] = stem
                            st["matches"] = matches
                            st["idx"] = 0
                            t.delete(line_start, idx)
                            t.insert(line_start, matches[0])
                    return "break"
                txt.bind("<Tab>", autocomplete)

                def cm_on_key(event, st=cm_cycle):
                    if event.keysym not in ("Tab", "Shift_L", "Shift_R"):
                        st["matches"] = []
                        st["idx"] = -1
                        st["line"] = None
                txt.bind("<KeyPress>", cm_on_key, add="+")

                if char_ids:
                    ttk.Label(sub, text=f"Available: {', '.join(char_ids)}",
                              style="Card.TLabel", foreground=MUTED,
                              wraplength=600).pack(anchor="w", pady=(4, 0))

                widgets[field] = lambda t=txt: [
                    ln.strip() for ln in t.get("1.0", "end").splitlines() if ln.strip()
                ]

            elif wtype == "writing_type":
                # Dropdown: serial / kindle, with inline warning if unrecognised
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                type_var = tk.StringVar(value=str(value) if value else "")
                combo = ttk.Combobox(sub, textvariable=type_var,
                                     values=WRITING_TYPE_OPTIONS,
                                     font=("Segoe UI", 10), width=12)
                combo.pack(side="left")
                type_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                type_warn.pack(side="left", padx=8)

                def check_type(*_, v=type_var, w=type_warn):
                    val = v.get().strip()
                    w.config(text=f"⚠ Must be 'serial' or 'kindle'" if (val and val not in WRITING_TYPE_OPTIONS) else "")
                type_var.trace_add("write", check_type)
                check_type()
                widgets[field] = lambda v=type_var: v.get()

            elif wtype == "writing_status":
                # Dropdown: ongoing / complete / hiatus, with inline warning
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                status_var = tk.StringVar(value=str(value) if value else "")
                combo = ttk.Combobox(sub, textvariable=status_var,
                                     values=WRITING_STATUS_OPTIONS,
                                     font=("Segoe UI", 10), width=12)
                combo.pack(side="left")
                status_warn = tk.Label(sub, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9))
                status_warn.pack(side="left", padx=8)

                def check_status(*_, v=status_var, w=status_warn):
                    val = v.get().strip()
                    w.config(text=f"⚠ Must be one of: ongoing, complete, hiatus" if (val and val not in WRITING_STATUS_OPTIONS) else "")
                status_var.trace_add("write", check_status)
                check_status()
                widgets[field] = lambda v=status_var: v.get()

            elif wtype == "writing_links":
                # Three optional URL fields: read, buy, preview
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))
                link_fields = ["read", "buy", "preview"]
                link_vars = {}
                existing = value if isinstance(value, dict) else {}
                for lf in link_fields:
                    row_frame = ttk.Frame(sub, style="Card.TFrame")
                    row_frame.pack(fill="x", pady=2)
                    ttk.Label(row_frame, text=f"{lf}:", style="Card.TLabel",
                              width=8, anchor="w").pack(side="left")
                    lv = tk.StringVar(value=str(existing.get(lf, "") or ""))
                    ttk.Entry(row_frame, textvariable=lv, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)
                    link_vars[lf] = lv
                ttk.Label(sub, text="(leave blank for null)",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(4, 0))

                def links_getter(lvs=link_vars):
                    return {k: (v.get().strip() or None) for k, v in lvs.items()}
                widgets[field] = links_getter

            elif wtype == "writing_chapters":
                # Dynamic list of {title, file} rows
                sub = ttk.Frame(form, style="Card.TFrame")
                sub.grid(row=row, column=1, sticky="ew", pady=(10, 2))

                # Header
                hdr = ttk.Frame(sub, style="Card.TFrame")
                hdr.pack(fill="x", pady=(0, 4))
                ttk.Label(hdr, text="Title", style="Card.TLabel",
                          font=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x")
                ttk.Label(hdr, text="File path", style="Card.TLabel",
                          font=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x", padx=(4, 28))

                chapter_rows = []  # list of {title_var, file_var, frame}

                def add_chapter_row(ch_title="", ch_file=""):
                    rf = ttk.Frame(sub, style="Card.TFrame")
                    rf.pack(fill="x", pady=2)

                    tv = tk.StringVar(value=ch_title)
                    ttk.Entry(rf, textvariable=tv, font=("Segoe UI", 10)).pack(
                        side="left", fill="x", expand=True)

                    fv = tk.StringVar(value=ch_file)
                    file_entry = ttk.Entry(rf, textvariable=fv, font=("Segoe UI", 10))
                    file_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

                    path_warn = tk.Label(rf, text="", bg=CARD, fg="#f59e0b", font=("Segoe UI", 9), width=2)
                    path_warn.pack(side="left", padx=(2, 0))

                    def check_path(*_, v=fv, w=path_warn):
                        val = v.get().strip()
                        w.config(text="⚠" if (val and not val.startswith("/writing/chapters/")) else "")
                    fv.trace_add("write", check_path)
                    check_path()

                    rd = {"title_var": tv, "file_var": fv, "frame": rf}

                    def remove(r=rd):
                        r["frame"].destroy()
                        chapter_rows.remove(r)
                    ttk.Button(rf, text="✕", width=3, command=remove).pack(side="left", padx=(4, 0))
                    chapter_rows.append(rd)

                existing_chapters = value if isinstance(value, list) else []
                for ch in existing_chapters:
                    add_chapter_row(ch.get("title", ""), ch.get("file", ""))

                ttk.Button(sub, text="+ Add Chapter",
                           command=lambda: add_chapter_row("", "")).pack(anchor="w", pady=(6, 0))
                ttk.Label(sub, text="File paths should follow /writing/chapters/filename.txt",
                          style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(4, 0))

                def chapters_getter(rows=chapter_rows):
                    return [
                        {"title": r["title_var"].get().strip(), "file": r["file_var"].get().strip()}
                        for r in rows
                    ]
                widgets[field] = chapters_getter

            row += 1

        form.columnconfigure(1, weight=1)

        def save():
            new_entry = {}
            for field, wtype in schema["fields"]:
                if wtype == "chapter_ref":
                    label, url = widgets[field]()
                    if label is None:
                        messagebox.showerror("Error", f"{field}: text cannot be empty.")
                        return
                    new_entry[field] = label
                    new_entry[field + "Url"] = url
                else:
                    new_entry[field] = widgets[field]()

            # ── Art-specific validation ──────────────────────────────────
            if file_key == "art":
                # Required fields
                for required_field in ("id", "title", "image", "year"):
                    val = str(new_entry.get(required_field, "")).strip()
                    if not val:
                        messagebox.showerror("Error", f"'{required_field}' is required.")
                        return

                # id uniqueness check
                final_id = str(new_entry.get("id", "")).strip()
                for i, e in enumerate(entries):
                    if (is_new or i != index) and e.get("id") == final_id:
                        messagebox.showerror(
                            "Duplicate ID",
                            f"An entry with id '{final_id}' already exists."
                        )
                        return

                # image path format check
                img_val = str(new_entry.get("image", "")).strip()
                if img_val and not img_val.startswith("/art/"):
                    if not messagebox.askyesno(
                        "Path Warning",
                        f"Image path '{img_val}' doesn't start with /art/.\n\nSave anyway?"
                    ):
                        return

                # thumbnail path format check (optional)
                thumb_val = str(new_entry.get("thumbnail", "")).strip()
                if thumb_val and not thumb_val.startswith("/art/"):
                    if not messagebox.askyesno(
                        "Path Warning",
                        f"Thumbnail path '{thumb_val}' doesn't start with /art/.\n\nSave anyway?"
                    ):
                        return

                # category required, but only warn if not in list (don't block save)
                cat_val = str(new_entry.get("category", "")).strip()
                if not cat_val:
                    messagebox.showerror("Error", "'category' is required.")
                    return
                if art_categories and cat_val not in art_categories:
                    messagebox.showwarning(
                        "Category Warning",
                        f"Category '{cat_val}' is not in the top-level categories list.\n\n"
                        f"Valid categories: {', '.join(art_categories)}\n\n"
                        f"Saving anyway — add it to categories in art.json if needed."
                    )

                # Strip empty optional fields so they don't appear in the JSON
                for opt_field in ("thumbnail", "medium", "description"):
                    if not str(new_entry.get(opt_field, "")).strip():
                        new_entry.pop(opt_field, None)
                if not new_entry.get("tags"):
                    new_entry.pop("tags", None)

            elif file_key == "writing":
                # Required: id, title, type, blurb, year, status
                for required_field in ("id", "title", "type", "blurb", "year", "status"):
                    if not str(new_entry.get(required_field, "")).strip():
                        messagebox.showerror("Error", f"'{required_field}' is required.")
                        return

                # id uniqueness
                final_id = str(new_entry.get("id", "")).strip()
                for i, e in enumerate(entries):
                    if (is_new or i != index) and e.get("id") == final_id:
                        messagebox.showerror("Duplicate ID",
                                             f"An entry with id '{final_id}' already exists.")
                        return

                warnings = []

                # type must be serial or kindle
                type_val = str(new_entry.get("type", "")).strip()
                if type_val and type_val not in WRITING_TYPE_OPTIONS:
                    warnings.append(f"type '{type_val}' is not 'serial' or 'kindle'.")

                # status must be ongoing / complete / hiatus
                status_val = str(new_entry.get("status", "")).strip()
                if status_val and status_val not in WRITING_STATUS_OPTIONS:
                    warnings.append(f"status '{status_val}' is not one of: ongoing, complete, hiatus.")

                # cover path format
                cover_val = str(new_entry.get("cover", "") or "").strip()
                if cover_val and not cover_val.startswith("/writing/"):
                    warnings.append(f"cover path '{cover_val}' doesn't start with /writing/.")

                # spineColor and spineTextColor must both be set or both be null
                sc = str(new_entry.get("spineColor", "") or "").strip()
                stc = str(new_entry.get("spineTextColor", "") or "").strip()
                if bool(sc) != bool(stc):
                    warnings.append("spineColor and spineTextColor should both be set or both be empty.")

                # chapters validation — optional but each entry needs title + file
                chapters_val = new_entry.get("chapters", []) or []
                for ci, ch in enumerate(chapters_val):
                    ch_title = str(ch.get("title", "")).strip()
                    ch_file = str(ch.get("file", "")).strip()
                    if not ch_title:
                        warnings.append(f"Chapter {ci + 1} is missing a title.")
                    if not ch_file:
                        warnings.append(f"Chapter {ci + 1} is missing a file path.")
                    elif not ch_file.startswith("/writing/chapters/"):
                        warnings.append(f"Chapter {ci + 1} file '{ch_file}' doesn't start with /writing/chapters/.")

                if warnings:
                    messagebox.showwarning(
                        "Validation Warnings",
                        "Saving with the following warnings:\n\n• " + "\n• ".join(warnings)
                    )

                # Strip empty optional fields
                for opt_field in WRITING_OPTIONAL_FIELDS:
                    val = new_entry.get(opt_field)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        new_entry.pop(opt_field, None)
                if not new_entry.get("tags"):
                    new_entry.pop("tags", None)
                # Strip empty chapters list
                if not new_entry.get("chapters"):
                    new_entry.pop("chapters", None)
                # Normalise null link values
                if "links" in new_entry and isinstance(new_entry["links"], dict):
                    new_entry["links"] = {
                        k: (v if v else None)
                        for k, v in new_entry["links"].items()
                    }

            else:
                # Original logic for non-art schemas
                if schema.get("id_prefix"):
                    num = new_entry.get("number")
                    if num is None:
                        messagebox.showerror("Error", "Number is required.")
                        return
                    num_str = str(num).replace(".", "-")
                    new_entry["id"] = f"{schema['id_prefix']}{num_str}"

                if schema.get("image_folder"):
                    eid = str(new_entry.get("id", "")).strip()
                    if not eid:
                        messagebox.showerror("Error", "id is required.")
                        return
                    new_entry["image"] = f"{schema['image_folder']}{eid}.png"

                final_id = str(new_entry.get("id", "")).strip()
                if final_id:
                    for i, e in enumerate(entries):
                        if (is_new or i != index) and e.get("id") == final_id:
                            messagebox.showerror(
                                "Duplicate ID",
                                f"An entry with id '{final_id}' already exists. "
                                f"Please choose a different id."
                            )
                            return

            # Build ordered output
            ordered = {}
            if "id" in new_entry:
                ordered["id"] = new_entry.pop("id")
            for field, _ in schema["fields"]:
                if field in new_entry:
                    ordered[field] = new_entry[field]
                if field == "name" and "image" in new_entry:
                    ordered["image"] = new_entry["image"]
                if field == "firstAppearance" and field + "Url" in new_entry:
                    ordered[field + "Url"] = new_entry[field + "Url"]
            for k, v in new_entry.items():
                if k not in ordered:
                    ordered[k] = v

            if is_new:
                entries.append(ordered)
            else:
                entries[index] = ordered

            # Preserve top-level structure for files that wrap their list
            if file_key in ("art", "writing") and isinstance(data, dict):
                data[schema["key"]] = entries
                save_json(folder, schema["filename"], data)
            else:
                save_entries(folder, schema["filename"], schema["key"], entries, data)

            cascade_msg = ""
            if file_key == "chapters" and cascade_var is not None and cascade_var.get():
                chapter_num = ordered.get("number")
                new_urls = ordered.get("url", [])
                if not isinstance(new_urls, list):
                    new_urls = [new_urls] if new_urls else []
                if chapter_num is not None:
                    chapter_label = f"Chapter {chapter_num}"
                    summary = self._cascade_update_chapter_urls(chapter_label, new_urls)
                    if summary:
                        total = sum(summary.values())
                        parts = [f"{c} in {fn}" for fn, c in summary.items()]
                        cascade_msg = (f"\n\nCascade: updated {total} entr"
                                       f"{'y' if total == 1 else 'ies'} "
                                       f"across {len(summary)} file"
                                       f"{'' if len(summary) == 1 else 's'} "
                                       f"({', '.join(parts)}).")

            messagebox.showinfo("Saved", f"Saved to {schema['filename']}{cascade_msg}")
            self.open_list_view(module_key, file_key)

        # Cascade toggle (chapters only)
        cascade_var = None
        if file_key == "chapters":
            cascade_var = tk.BooleanVar(value=True)
            cascade_row = ttk.Frame(form, style="Card.TFrame")
            cascade_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(15, 0))
            ttk.Checkbutton(
                cascade_row,
                text="Auto-update firstAppearanceUrl on linked entries when saving",
                variable=cascade_var,
            ).pack(anchor="w")
            ttk.Label(
                cascade_row,
                text="(scans characters/items/places/history for entries whose "
                     "firstAppearance matches this chapter, syncs their URL list)",
                style="Card.TLabel", foreground=MUTED,
            ).pack(anchor="w", padx=(22, 0))
            row += 1

        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ttk.Button(btn_row, text="Save", style="Accent.TButton",
                   command=save).pack(side="right", padx=4)
        ttk.Button(btn_row, text="Cancel",
                   command=lambda: self.open_list_view(module_key, file_key)).pack(side="right", padx=4)

    # ============================================================
    # codes.json  (Regalia only)
    # ============================================================
    def _regalia_folder(self):
        return self.module_folder("regalia")

    def _load_codes_flat(self):
        raw = load_json(self._regalia_folder(), CODES_FILENAME) or {}
        states = {}
        origin = {}
        if isinstance(raw, dict):
            for k, v in raw.items():
                if k == "codes" and isinstance(v, dict):
                    for sk, sv in v.items():
                        if isinstance(sv, dict):
                            states[sk] = sv
                            origin[sk] = "codes"
                elif isinstance(v, dict) and "label" in v:
                    states[k] = v
                    origin[k] = "top"
        self._codes_origin = origin
        return states

    def _save_codes_flat(self, states, new_state_origins=None):
        origin = dict(getattr(self, "_codes_origin", {}))
        if new_state_origins:
            origin.update(new_state_origins)
        top_level = {}
        nested = {}
        for k, v in states.items():
            where = origin.get(k, "codes")
            if where == "top":
                top_level[k] = v
            else:
                nested[k] = v
        out = {}
        for k, v in top_level.items():
            out[k] = v
        out["codes"] = nested
        save_json(self._regalia_folder(), CODES_FILENAME, out)
        self._codes_origin = origin

    def open_codes_view(self):
        self.clear_root()
        data = self._load_codes_flat()

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Back", command=self.build_main_menu).pack(side="left")
        ttk.Label(header, text="codes.json",
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)
        ttk.Label(header, text=f"{len(data)} states",
                  style="Subtitle.TLabel").pack(side="left")

        list_card = ttk.Frame(container, style="Card.TFrame", padding=10)
        list_card.pack(fill="both", expand=True, pady=(0, 15))

        cols = ("key", "label")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=18)
        tree.heading("key", text="State Key",
                     command=lambda: self._sort_tree(tree, "key", False))
        tree.heading("label", text="Label",
                     command=lambda: self._sort_tree(tree, "label", False))
        tree.column("key", width=200)
        tree.column("label", width=600)

        sb = ttk.Scrollbar(list_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for k in data.keys():
            tree.insert("", "end", iid=k, values=(k, data[k].get("label", "")))

        def on_code_double_click(ev, t=tree):
            if t.identify_region(ev.x, ev.y) != "cell":
                return
            self._edit_code_selection(t, silent=True)
        tree.bind("<Double-1>", on_code_double_click)

        btns = ttk.Frame(container)
        btns.pack(fill="x")
        ttk.Button(btns, text="+ Add New State", style="Accent.TButton",
                   command=lambda: self.open_code_editor(None)).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Edit Selected",
                   command=lambda: self._edit_code_selection(tree)).pack(side="left", padx=6)
        ttk.Button(btns, text="Delete Selected",
                   command=lambda: self._delete_code_selection(tree)).pack(side="left", padx=6)

    def _edit_code_selection(self, tree, silent=False):
        sel = tree.selection()
        if not sel:
            if not silent:
                messagebox.showinfo("No selection", "Pick a state first.")
            return
        self.open_code_editor(sel[0])

    def _delete_code_selection(self, tree):
        sel = tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Delete", f"Delete state '{sel[0]}'?"):
            return
        states = self._load_codes_flat()
        states.pop(sel[0], None)
        if hasattr(self, "_codes_origin"):
            self._codes_origin.pop(sel[0], None)
        self._save_codes_flat(states)
        self.open_codes_view()

    def open_code_editor(self, state_key):
        self.clear_root()
        data = self._load_codes_flat()
        is_new = state_key is None
        if is_new:
            default = data.get("default", {})
            state = {
                "background": default.get("background", ""),
                "headerBackground": default.get("headerBackground", ""),
                "buttonSet": default.get("buttonSet", ""),
            }
        else:
            state = dict(data.get(state_key, {}))

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Cancel", command=self.open_codes_view).pack(side="left")
        ttk.Label(header, text=("New state" if is_new else f"Edit: {state_key}"),
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        form = ttk.Frame(canvas, style="Card.TFrame", padding=20)
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(form_window, width=event.width)
        canvas.bind("<Configure>", on_configure)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        ttk.Label(form, text="State key", style="Card.TLabel",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 15), pady=(0, 2))
        key_var = tk.StringVar(value=state_key or "")
        ttk.Entry(form, textvariable=key_var, width=30, font=("Segoe UI", 10)).grid(
            row=0, column=1, sticky="w", pady=(0, 2))

        simple_fields = [
            ("label", state.get("label", "")),
            ("background", state.get("background", "")),
            ("headerBackground", state.get("headerBackground", "")),
            ("buttonSet", state.get("buttonSet", "")),
        ]
        simple_vars = {}
        for i, (fname, fval) in enumerate(simple_fields, start=1):
            ttk.Label(form, text=fname, style="Card.TLabel",
                      font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", padx=(0, 15), pady=(10, 2))
            v = tk.StringVar(value=fval)
            ttk.Entry(form, textvariable=v, font=("Segoe UI", 10)).grid(
                row=i, column=1, sticky="ew", pady=(10, 2))
            simple_vars[fname] = v

        list_fields = [
            ("loreCharacterIds", state.get("loreCharacterIds", [])),
            ("loreItemIds", state.get("loreItemIds", [])),
            ("lorePlaceIds", state.get("lorePlaceIds", [])),
            ("loreHistoryIds", state.get("loreHistoryIds", [])),
        ]
        list_widgets = {}
        base_row = len(simple_fields) + 1
        for i, (fname, fval) in enumerate(list_fields):
            r = base_row + i
            ttk.Label(form, text=f"{fname}\n(one per line)", style="Card.TLabel",
                      font=("Segoe UI", 10, "bold")).grid(row=r, column=0, sticky="nw", padx=(0, 15), pady=(10, 2))
            txt = tk.Text(form, height=4, wrap="word", font=("Segoe UI", 10))
            txt.grid(row=r, column=1, sticky="ew", pady=(10, 2))
            if fval:
                txt.insert("1.0", "\n".join(fval))
            list_widgets[fname] = txt

        form.columnconfigure(1, weight=1)

        def save():
            new_key = key_var.get().strip()
            if not new_key:
                messagebox.showerror("Error", "State key required.")
                return
            new_state = {fname: var.get() for fname, var in simple_vars.items()}
            for fname, txt in list_widgets.items():
                new_state[fname] = [ln.strip() for ln in txt.get("1.0", "end").splitlines() if ln.strip()]
            states = self._load_codes_flat()
            if not is_new and new_key != state_key:
                states.pop(state_key, None)
                if hasattr(self, "_codes_origin") and state_key in self._codes_origin:
                    self._codes_origin[new_key] = self._codes_origin.pop(state_key)
            states[new_key] = new_state
            self._save_codes_flat(states)
            messagebox.showinfo("Saved", f"Saved state '{new_key}'.")
            self.open_codes_view()

        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.grid(row=base_row + len(list_fields), column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ttk.Button(btn_row, text="Save", style="Accent.TButton",
                   command=save).pack(side="right", padx=4)
        ttk.Button(btn_row, text="Cancel",
                   command=self.open_codes_view).pack(side="right", padx=4)

    # ============================================================
    # timeline.json
    # ============================================================
    def _load_timeline(self):
        raw = load_json(self._regalia_folder(), TIMELINE_FILENAME)
        if not isinstance(raw, dict):
            raw = {}
        if "map" not in raw or not isinstance(raw["map"], dict):
            raw["map"] = {
                "image": "/images/timeline/map-placeholder.png",
                "width": 1600,
                "height": 1000,
            }
        if "days" not in raw or not isinstance(raw["days"], list):
            raw["days"] = []
        return raw

    def _save_timeline(self, data):
        save_json(self._regalia_folder(), TIMELINE_FILENAME, data)

    def _find_timeline_map(self):
        data = self._load_timeline()
        rel = data.get("map", {}).get("image", "/images/timeline/map-placeholder.png").lstrip("/")
        candidates = [
            os.path.join(self.project_root, "public", rel),
            os.path.join(self.project_root, "..", "public", rel),
            os.path.join(self._regalia_folder(), rel),
        ]
        for p in candidates:
            real = os.path.normpath(p)
            if os.path.exists(real):
                return real
        return None

    def open_timeline_view(self):
        self.clear_root()
        data = self._load_timeline()

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Back", command=self.build_main_menu).pack(side="left")
        ttk.Label(header, text="timeline.json",
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)

        map_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        map_card.pack(fill="x", pady=(0, 10))
        ttk.Label(map_card, text="Map", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        m = data["map"]
        img_var = tk.StringVar(value=m.get("image", ""))
        w_var = tk.StringVar(value=str(m.get("width", 1600)))
        h_var = tk.StringVar(value=str(m.get("height", 1000)))

        ttk.Label(map_card, text="image:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(map_card, textvariable=img_var, font=("Segoe UI", 10)).grid(row=1, column=1, columnspan=3, sticky="ew", pady=2)
        ttk.Label(map_card, text="width:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=2)
        ttk.Entry(map_card, textvariable=w_var, font=("Segoe UI", 10), width=10).grid(row=2, column=1, sticky="w")
        ttk.Label(map_card, text="height:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=(15, 8))
        ttk.Entry(map_card, textvariable=h_var, font=("Segoe UI", 10), width=10).grid(row=2, column=3, sticky="w")
        map_card.columnconfigure(1, weight=1)

        days_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        days_card.pack(fill="both", expand=True, pady=(0, 10))

        days_header = ttk.Frame(days_card, style="Card.TFrame")
        days_header.pack(fill="x", pady=(0, 8))
        ttk.Label(days_header, text="Days", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(side="left")
        ttk.Label(days_header, text=f"({len(data['days'])} days)",
                  style="Card.TLabel", foreground=MUTED).pack(side="left", padx=8)

        tv_frame = ttk.Frame(days_card, style="Card.TFrame")
        tv_frame.pack(fill="both", expand=True)

        cols = ("day", "label", "entries")
        tree = ttk.Treeview(tv_frame, columns=cols, show="headings", height=12,
                            selectmode="extended")
        tree.heading("day", text="Day",
                     command=lambda: self._sort_tree(tree, "day", False))
        tree.heading("label", text="Label",
                     command=lambda: self._sort_tree(tree, "label", False))
        tree.heading("entries", text="# Entries")
        tree.column("day", width=80, anchor="w")
        tree.column("label", width=400, anchor="w")
        tree.column("entries", width=100, anchor="center")
        sb = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for i, day in enumerate(data["days"]):
            tree.insert("", "end", iid=str(i), values=(
                day.get("day", "?"),
                day.get("label", ""),
                len(day.get("entries", []))
            ))

        TreeDragReorder(tree)

        def on_dbl(ev, t=tree):
            if t.identify_region(ev.x, ev.y) != "cell":
                return
            sel = t.selection()
            if sel:
                self._save_timeline_meta(data, img_var, w_var, h_var)
                self.open_timeline_day_editor(int(sel[0]))
        tree.bind("<Double-1>", on_dbl)

        btns = ttk.Frame(container)
        btns.pack(fill="x")

        def add_day():
            self._save_timeline_meta(data, img_var, w_var, h_var)
            d = self._load_timeline()
            next_num = max([day.get("day", 0) for day in d["days"]] + [0]) + 1
            d["days"].append({"day": next_num, "label": "", "entries": []})
            self._save_timeline(d)
            self.open_timeline_view()

        def edit_day():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("No selection", "Pick a day first.")
                return
            self._save_timeline_meta(data, img_var, w_var, h_var)
            self.open_timeline_day_editor(int(sel[0]))

        def del_day():
            sel = tree.selection()
            if not sel:
                return
            if not messagebox.askyesno("Delete", "Delete this day?"):
                return
            self._save_timeline_meta(data, img_var, w_var, h_var)
            d = self._load_timeline()
            del d["days"][int(sel[0])]
            self._save_timeline(d)
            self.open_timeline_view()

        def save_meta_only():
            self._save_timeline_meta(data, img_var, w_var, h_var)
            messagebox.showinfo("Saved", "Map config saved.")

        def do_sort():
            if not messagebox.askyesno(
                "Sort timeline.json",
                "This will rewrite timeline.json so days appear in the order "
                "shown in the list above.\n\nProceed?"
            ):
                return
            iid_order = list(tree.get_children(""))
            new_days = [data["days"][int(iid)] for iid in iid_order]
            self._save_timeline_meta(data, img_var, w_var, h_var)
            d = self._load_timeline()
            d["days"] = new_days
            self._save_timeline(d)
            messagebox.showinfo(
                "Sorted",
                f"timeline.json reordered ({len(new_days)} days)."
            )
            self.open_timeline_view()

        ttk.Button(btns, text="+ Add Day", style="Accent.TButton",
                   command=add_day).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Edit Selected Day", command=edit_day).pack(side="left", padx=6)
        ttk.Button(btns, text="Delete Selected", command=del_day).pack(side="left", padx=6)
        ttk.Button(btns, text="Save Map Config", command=save_meta_only).pack(side="left", padx=6)
        ttk.Button(btns, text="⇅ SORT", style="Sort.TButton",
                   command=do_sort).pack(side="right")

        ttk.Label(container,
                  text="Tip: drag rows to reorder • Shift/Ctrl-click for "
                       "multi-select • click the Day column header to sort by "
                       "day • SORT writes the current order to JSON",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(8, 0))

    def _save_timeline_meta(self, data, img_var, w_var, h_var):
        try:
            w = int(w_var.get())
        except ValueError:
            w = 1600
        try:
            h = int(h_var.get())
        except ValueError:
            h = 1000
        data["map"] = {
            "image": img_var.get().strip(),
            "width": w,
            "height": h,
        }
        self._save_timeline(data)

    def open_timeline_day_editor(self, day_index):
        self.clear_root()
        data = self._load_timeline()
        day = dict(data["days"][day_index])

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))
        ttk.Button(header, text="← Cancel",
                   command=self.open_timeline_view).pack(side="left")
        ttk.Label(header, text=f"Day {day.get('day', '?')}",
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)

        form_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        form_card.pack(fill="x", pady=(0, 10))

        ttk.Label(form_card, text="day #:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        day_var = tk.StringVar(value=str(day.get("day", "")))
        ttk.Entry(form_card, textvariable=day_var, font=("Segoe UI", 10), width=10).grid(row=0, column=1, sticky="w", pady=2)
        ttk.Label(form_card, text="label:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=(15, 8))
        label_var = tk.StringVar(value=day.get("label", ""))
        ttk.Entry(form_card, textvariable=label_var, font=("Segoe UI", 10)).grid(row=0, column=3, sticky="ew", pady=2)
        form_card.columnconfigure(3, weight=1)

        entries_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        entries_card.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Label(entries_card, text="Entries", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        hdr = ttk.Frame(entries_card, style="Card.TFrame")
        hdr.pack(fill="x", pady=(0, 4))
        ttk.Label(hdr, text="Character ID", style="Card.TLabel",
                  font=("Segoe UI", 9, "bold"), width=18).pack(side="left")
        ttk.Label(hdr, text="Place ID", style="Card.TLabel",
                  font=("Segoe UI", 9, "bold"), width=18).pack(side="left", padx=4)
        ttk.Label(hdr, text="Chapter ID", style="Card.TLabel",
                  font=("Segoe UI", 9, "bold"), width=14).pack(side="left", padx=4)

        char_ids = get_character_ids(self._regalia_folder())
        place_ids = [p.get("id", "") for p in get_entries(load_json(self._regalia_folder(), "places.json"), "places") if p.get("id")]
        chapter_ids = [c.get("id", "") for c in get_entries(load_json(self._regalia_folder(), "chapters.json"), "chapters") if c.get("id")]

        scroll_container = ttk.Frame(entries_card)
        scroll_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        rows_box = ttk.Frame(canvas, style="Card.TFrame")
        canvas.create_window((0, 0), window=rows_box, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        rows_box.bind("<Configure>", on_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        entry_rows = []

        def make_autocomplete(entry_widget, var, options):
            cycle_state = {"matches": [], "idx": -1}

            def on_tab(_, v=var, e=entry_widget, opts=options, st=cycle_state):
                cur = v.get()
                if st["matches"] and cur in st["matches"]:
                    st["idx"] = (st["idx"] + 1) % len(st["matches"])
                    v.set(st["matches"][st["idx"]])
                    e.icursor("end")
                else:
                    stem = cur.strip()
                    if stem:
                        matches = [o for o in opts if o.startswith(stem)]
                        if matches:
                            st["matches"] = matches
                            st["idx"] = 0
                            v.set(matches[0])
                            e.icursor("end")
                return "break"

            def on_key(event, st=cycle_state):
                if event.keysym not in ("Tab", "Shift_L", "Shift_R"):
                    st["matches"] = []
                    st["idx"] = -1

            entry_widget.bind("<Tab>", on_tab)
            entry_widget.bind("<KeyPress>", on_key, add="+")

        def add_entry(cid="", pid="", chid=""):
            f = ttk.Frame(rows_box, style="Card.TFrame")
            f.pack(fill="x", pady=2)

            cv = tk.StringVar(value=cid)
            ce = ttk.Entry(f, textvariable=cv, font=("Segoe UI", 10), width=18)
            ce.pack(side="left")
            make_autocomplete(ce, cv, char_ids)

            pv = tk.StringVar(value=pid)
            pe = ttk.Entry(f, textvariable=pv, font=("Segoe UI", 10), width=18)
            pe.pack(side="left", padx=4)
            make_autocomplete(pe, pv, place_ids)

            chv = tk.StringVar(value=chid)
            che = ttk.Entry(f, textvariable=chv, font=("Segoe UI", 10), width=14)
            che.pack(side="left", padx=4)
            make_autocomplete(che, chv, chapter_ids)

            row_data = {"char_var": cv, "place_var": pv, "chap_var": chv, "frame": f}

            def remove(rd=row_data):
                rd["frame"].destroy()
                entry_rows.remove(rd)

            ttk.Button(f, text="✕", width=3, command=remove).pack(side="left")
            entry_rows.append(row_data)

        for e in day.get("entries", []):
            add_entry(e.get("characterId", ""), e.get("placeId", ""), e.get("chapterId", ""))

        ttk.Button(entries_card, text="+ Add Entry",
                   command=lambda: add_entry()).pack(anchor="w", pady=(8, 0))

        ttk.Label(entries_card, text="Tab to autocomplete from characters / places / chapters",
                  style="Card.TLabel", foreground=MUTED).pack(anchor="w", pady=(4, 0))

        def save():
            try:
                day_num = int(day_var.get())
            except ValueError:
                messagebox.showerror("Error", "Day number must be an integer.")
                return
            new_entries = []
            for r in entry_rows:
                cid = r["char_var"].get().strip()
                pid = r["place_var"].get().strip()
                chid = r["chap_var"].get().strip()
                if not (cid or pid or chid):
                    continue
                new_entries.append({
                    "characterId": cid,
                    "placeId": pid,
                    "chapterId": chid,
                })
            d = self._load_timeline()
            new_day = {"day": day_num, "entries": new_entries}
            lbl = label_var.get().strip()
            if lbl:
                new_day = {"day": day_num, "label": lbl, "entries": new_entries}
            d["days"][day_index] = new_day
            self._save_timeline(d)
            messagebox.showinfo("Saved", f"Day {day_num} saved.")
            self.open_timeline_view()

        btns = ttk.Frame(container)
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", style="Accent.TButton",
                   command=save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel",
                   command=self.open_timeline_view).pack(side="right", padx=4)

    # ============================================================
    # Map picker
    # ============================================================
    def _open_map_picker(self, current_x, current_y):
        timeline = self._load_timeline()
        map_w = int(timeline.get("map", {}).get("width", 1600))
        map_h = int(timeline.get("map", {}).get("height", 1000))
        img_path = self._find_timeline_map()

        try:
            from PIL import Image, ImageTk
            has_pil = True
        except ImportError:
            has_pil = False

        win = tk.Toplevel(self.root)
        win.title("Map Position Picker")
        win.configure(bg=BG)
        win.transient(self.root)

        info = ttk.Frame(win, padding=10)
        info.pack(fill="x")
        ttk.Label(info,
                  text=(f"Click on the map to place this point.  "
                        f"Map size: {map_w}×{map_h} px"),
                  style="Subtitle.TLabel").pack(side="left")

        max_dim = 900
        if has_pil and img_path:
            try:
                pil_img = Image.open(img_path)
                orig_w, orig_h = pil_img.size
            except Exception:
                pil_img = None
                orig_w, orig_h = map_w, map_h
        else:
            pil_img = None
            orig_w, orig_h = map_w, map_h

        coord_w, coord_h = map_w, map_h
        scale = min(max_dim / coord_w, max_dim / coord_h, 1.0)
        disp_w = int(coord_w * scale)
        disp_h = int(coord_h * scale)

        canvas = tk.Canvas(win, width=disp_w, height=disp_h,
                           bg="#222", highlightthickness=0)
        canvas.pack(padx=10, pady=5)

        if pil_img is not None:
            try:
                disp_img = pil_img.resize((disp_w, disp_h), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(disp_img)
                canvas.create_image(0, 0, anchor="nw", image=tk_img)
                canvas.image_ref = tk_img
            except Exception as e:
                canvas.create_text(disp_w / 2, disp_h / 2,
                                   text=f"(could not load image: {e})",
                                   fill="white")
        else:
            msg = "(map image not found)" if not img_path else "(install Pillow to preview the map)"
            canvas.create_text(disp_w / 2, disp_h / 2, text=msg, fill="white")

        chosen = {"x": current_x, "y": current_y}
        marker_id = [None]

        def draw_marker():
            if marker_id[0] is not None:
                canvas.delete(marker_id[0])
            x = chosen["x"] * scale
            y = chosen["y"] * scale
            marker_id[0] = canvas.create_oval(x - 8, y - 8, x + 8, y + 8,
                                              fill="#ef4444", outline="white", width=2)
        if 0 <= current_x <= coord_w and 0 <= current_y <= coord_h:
            draw_marker()

        readout_var = tk.StringVar(value=f"x={chosen['x']}, y={chosen['y']}")
        ttk.Label(win, textvariable=readout_var,
                  style="Subtitle.TLabel").pack()

        def on_click(ev):
            mx = max(0, min(coord_w, int(ev.x / scale)))
            my = max(0, min(coord_h, int(ev.y / scale)))
            chosen["x"] = mx
            chosen["y"] = my
            draw_marker()
            readout_var.set(f"x={mx}, y={my}")

        canvas.bind("<Button-1>", on_click)

        result = {"value": None}

        def confirm():
            result["value"] = (chosen["x"], chosen["y"])
            win.destroy()

        def cancel():
            win.destroy()

        btns = ttk.Frame(win, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", command=cancel).pack(side="right", padx=4)
        ttk.Button(btns, text="Use This Position", style="Accent.TButton",
                   command=confirm).pack(side="right", padx=4)

        win.protocol("WM_DELETE_WINDOW", cancel)
        win.grab_set()
        self.root.wait_window(win)
        return result["value"]

    # ============================================================
    # Visual anchor editor
    # ============================================================
    def _find_character_image(self, char_id):
        if not char_id:
            return None
        filename = f"{char_id}.png"
        candidates = [
            os.path.join(self.project_root, "public", "images", "characters", filename),
            os.path.join(self.project_root, "..", "public", "images", "characters", filename),
            os.path.join(self._regalia_folder(), "images", "characters", filename),
        ]
        for p in candidates:
            real = os.path.normpath(p)
            if os.path.exists(real):
                return real
        return None

    def _open_anchor_editor(self, char_id, anchor_state, on_done):
        img_path = self._find_character_image(char_id)
        if not img_path:
            messagebox.showerror(
                "Image not found",
                f"Could not find {char_id}.png in any of the expected locations:\n"
                f"  ../../../public/images/characters/\n"
                f"  ../public/images/characters/\n"
                f"  ./public/images/characters/\n"
                f"  ./images/characters/"
            )
            return

        try:
            from PIL import Image, ImageTk
        except ImportError:
            messagebox.showerror(
                "Missing dependency",
                "The visual anchor editor needs Pillow.\n"
                "Run in terminal: pip install Pillow"
            )
            return

        win = tk.Toplevel(self.root)
        win.title(f"Anchor Editor — {char_id}")
        win.configure(bg=BG)
        win.transient(self.root)

        try:
            pil_img = Image.open(img_path)
        except Exception as e:
            messagebox.showerror("Image error", f"Could not open image:\n{e}")
            win.destroy()
            return

        orig_w, orig_h = pil_img.size
        max_dim = 800
        scale = min(max_dim / orig_w, max_dim / orig_h, 1.0)
        disp_w, disp_h = int(orig_w * scale), int(orig_h * scale)
        if scale < 1.0:
            disp_img = pil_img.resize((disp_w, disp_h), Image.LANCZOS)
        else:
            disp_img = pil_img
        tk_img = ImageTk.PhotoImage(disp_img)

        info = ttk.Frame(win, padding=10)
        info.pack(fill="x")
        ttk.Label(info, text=f"Image: {os.path.basename(img_path)}  "
                             f"({orig_w}×{orig_h} px)  "
                             f"{'— scaled to fit' if scale < 1.0 else ''}",
                  style="Subtitle.TLabel").pack(side="left")

        canvas = tk.Canvas(win, width=disp_w, height=disp_h,
                           bg="#222", highlightthickness=0)
        canvas.pack(padx=10, pady=5)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        canvas.image_ref = tk_img

        anchor_items = {}
        COLORS = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#a855f7", "#ec4899"]

        def color_for(name):
            return COLORS[abs(hash(name)) % len(COLORS)]

        def redraw():
            for dot, lbl in anchor_items.values():
                canvas.delete(dot)
                canvas.delete(lbl)
            anchor_items.clear()
            for name, coord in anchor_state.items():
                x, y = coord["x"] * scale, coord["y"] * scale
                c = color_for(name)
                dot = canvas.create_oval(x - 7, y - 7, x + 7, y + 7,
                                         fill=c, outline="white", width=2)
                lbl = canvas.create_text(x + 12, y - 10, text=name,
                                         fill="white", anchor="w",
                                         font=("Segoe UI", 10, "bold"))
                bbox = canvas.bbox(lbl)
                if bbox:
                    bg_rect = canvas.create_rectangle(
                        bbox[0] - 2, bbox[1] - 1, bbox[2] + 2, bbox[3] + 1,
                        fill="#000000", outline="")
                    canvas.tag_lower(bg_rect, lbl)
                anchor_items[name] = (dot, lbl)

        redraw()

        drag = {"name": None, "offset": (0, 0)}

        def hit_test(cx, cy):
            for name, coord in anchor_state.items():
                x, y = coord["x"] * scale, coord["y"] * scale
                if (cx - x) ** 2 + (cy - y) ** 2 <= 10 ** 2:
                    return name
            return None

        def on_left_press(ev):
            name = hit_test(ev.x, ev.y)
            if name:
                drag["name"] = name
                ax = anchor_state[name]["x"] * scale
                ay = anchor_state[name]["y"] * scale
                drag["offset"] = (ev.x - ax, ev.y - ay)
            else:
                new_name = _prompt_anchor_name(win, anchor_state)
                if new_name:
                    anchor_state[new_name] = {
                        "x": int(ev.x / scale),
                        "y": int(ev.y / scale),
                    }
                    redraw()

        def on_left_drag(ev):
            if drag["name"]:
                nx = (ev.x - drag["offset"][0]) / scale
                ny = (ev.y - drag["offset"][1]) / scale
                nx = max(0, min(orig_w, nx))
                ny = max(0, min(orig_h, ny))
                anchor_state[drag["name"]] = {"x": int(nx), "y": int(ny)}
                redraw()

        def on_left_release(ev):
            drag["name"] = None

        def on_right_click(ev):
            name = hit_test(ev.x, ev.y)
            if not name:
                return
            menu = tk.Menu(win, tearoff=0)
            menu.add_command(label=f"Rename '{name}'",
                             command=lambda: rename_anchor(name))
            menu.add_command(label=f"Delete '{name}'",
                             command=lambda: delete_anchor(name))
            menu.tk_popup(ev.x_root, ev.y_root)

        def rename_anchor(old_name):
            new_name = _prompt_anchor_name(win, anchor_state, initial=old_name,
                                           exclude_self=old_name)
            if new_name and new_name != old_name:
                anchor_state[new_name] = anchor_state.pop(old_name)
                redraw()

        def delete_anchor(name):
            if messagebox.askyesno("Delete anchor",
                                   f"Delete anchor '{name}'?", parent=win):
                anchor_state.pop(name, None)
                redraw()

        canvas.bind("<Button-1>", on_left_press)
        canvas.bind("<B1-Motion>", on_left_drag)
        canvas.bind("<ButtonRelease-1>", on_left_release)
        canvas.bind("<Button-3>", on_right_click)

        controls = ttk.Frame(win, padding=10)
        controls.pack(fill="x")
        ttk.Label(controls,
                  text="Click empty space to add • Drag dot to move • "
                       "Right-click dot to rename/delete",
                  style="Subtitle.TLabel").pack(side="left")

        def done():
            win.destroy()
            on_done()

        ttk.Button(controls, text="Done", style="Accent.TButton",
                   command=done).pack(side="right")

        win.protocol("WM_DELETE_WINDOW", done)

    def _cascade_update_chapter_urls(self, chapter_label, new_urls):
        if not chapter_label:
            return {}
        regalia_folder = self._regalia_folder()
        targets = [
            (fk, sch) for fk, sch in REGALIA_SCHEMAS.items()
            if any(f == "firstAppearance" for f, _ in sch["fields"])
        ]
        summary = {}
        for _fk, sch in targets:
            data = load_json(regalia_folder, sch["filename"])
            entries = get_entries(data, sch["key"])
            if not entries:
                continue
            count = 0
            for ent in entries:
                if ent.get("firstAppearance") == chapter_label:
                    if ent.get("firstAppearanceUrl") != new_urls:
                        ent["firstAppearanceUrl"] = new_urls
                        count += 1
            if count:
                save_entries(regalia_folder, sch["filename"], sch["key"], entries, data)
                summary[sch["filename"]] = count
        return summary

    def _sort_tree(self, tree, col, descending):
        items = [(tree.set(k, col), k) for k in tree.get_children("")]

        def sort_key(val_iid):
            v = val_iid[0]
            import re
            m = re.search(r"-?\d+\.?\d*", v)
            if m:
                try:
                    return (0, float(m.group()), v.lower())
                except ValueError:
                    pass
            return (1, 0.0, v.lower())

        items.sort(key=sort_key, reverse=descending)
        for i, (_, k) in enumerate(items):
            tree.move(k, "", i)
        tree.heading(col, command=lambda: self._sort_tree(tree, col, not descending))

    def clear_root(self):
        try:
            self.root.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        for w in self.root.winfo_children():
            w.destroy()


def _prompt_anchor_name(parent, anchor_state, initial="", exclude_self=None):
    dlg = tk.Toplevel(parent)
    dlg.title("Anchor name")
    dlg.transient(parent)
    dlg.grab_set()
    dlg.configure(bg=BG)

    frm = ttk.Frame(dlg, padding=20)
    frm.pack()
    ttk.Label(frm, text="Name for this anchor:").pack(anchor="w")
    var = tk.StringVar(value=initial)
    entry = ttk.Entry(frm, textvariable=var, font=("Segoe UI", 11), width=25)
    entry.pack(pady=8)
    entry.focus_set()
    entry.select_range(0, "end")

    result = {"value": None}

    def ok():
        name = var.get().strip()
        if not name:
            return
        if name != exclude_self and name in anchor_state:
            messagebox.showerror("Duplicate",
                                 f"Anchor '{name}' already exists.",
                                 parent=dlg)
            return
        result["value"] = name
        dlg.destroy()

    def cancel():
        dlg.destroy()

    btns = ttk.Frame(frm)
    btns.pack()
    ttk.Button(btns, text="OK", command=ok).pack(side="right", padx=4)
    ttk.Button(btns, text="Cancel", command=cancel).pack(side="right", padx=4)
    dlg.bind("<Return>", lambda e: ok())
    dlg.bind("<Escape>", lambda e: cancel())

    parent.wait_window(dlg)
    return result["value"]


def main():
    root = tk.Tk()
    JSONEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()