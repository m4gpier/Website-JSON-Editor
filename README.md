# Website JSON Editor

A purpose-built desktop GUI for managing the structured JSON data that powers [m4gpier.com](https://m4gpier.com) — a multi-subdomain React site covering a creative writing project (Regalia), an art portfolio, and a writing library.

Built with Python and Tkinter. No web server, no database — edits go straight to the JSON files the React frontend reads.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Why

The site's content lives in structured JSON across multiple subdomains and data schemas. Editing it by hand meant navigating deeply nested files, keeping IDs consistent, and remembering field formats — slow, error-prone, and easy to break. This tool replaces that with a dedicated editor that knows the schemas and enforces the rules.

---

## Features

### Multi-module support
Three independent content modules, each with their own schemas and data folders:
- **Regalia** — lore content: chapters, characters, items, places, history, codes, and a timeline
- **Art Portfolio** — artwork entries with category validation and image path checking
- **Writing** — books/serials with chapter management, spine colour config, and link fields

### Schema-aware editing
Each content type has typed fields with appropriate widgets:
- Dropdowns for constrained fields (bounce animations, relationship categories, art categories, writing status/type)
- Sliders for integer stats (0–6 scale)
- Multi-row editors for lists, relationships, and URL sets
- Date fields with a "Before Heaven" toggle for in-universe dating
- Inline validation warnings (duplicate IDs, malformed paths, mismatched fields)

### Drag-to-reorder
All list views support drag-and-drop row reordering. A **SORT** button writes the current visual order back to the JSON file.

### Visual anchor editor
Character entries have pixel-precise anchor points (face, hands, etc.) used by the frontend for UI overlays. The anchor editor opens the character's sprite, lets you click to place or drag to move anchors, and writes coordinates back to JSON.

### Map position picker
Place entries include an `x/y` map position. A visual picker overlays the timeline map image so positions can be clicked rather than guessed.

### Chapter cascade update
When a chapter's URL is edited, an optional cascade scan finds every character, item, place, and history entry whose `firstAppearance` matches that chapter and syncs their `firstAppearanceUrl` automatically.

### Tab autocomplete
ID fields in relationship editors, character lists, and timeline entries autocomplete from the live data — cycling through matches on repeated Tab presses.

---

## Project structure expected

```
project-root/
├── src/
│   ├── regaila/data/       ← chapters, characters, items, places, history, codes, timeline
│   ├── art/data/           ← art.json
│   └── writing/data/       ← writing.json
└── public/
    └── images/
        └── characters/     ← <id>.png files (used by anchor editor)
```

The app prompts you to select the project root on launch and validates the expected structure. Missing files produce a warning but don't block use — they're created on first save.

---

## Requirements

```
Python 3.x
Pillow       ← optional; needed for the visual anchor editor and map picker
```

Install Pillow if you want the visual editors:
```bash
pip install Pillow
```

The core editor works without it.

---

## Usage

```bash
python json_editor.py
```

1. Select your project root folder when prompted.
2. Choose a module and content type from the main menu.
3. Add, edit, delete, or reorder entries. All saves write directly to the JSON files.

---

## Notes

- Packaged as a standalone `.exe` with PyInstaller for personal use; build output is excluded from this repo via `.gitignore`.
- The schema definitions at the top of `json_editor.py` are the single source of truth for field types and file locations — adding a new content type means adding a schema block and pointing it at a folder.
