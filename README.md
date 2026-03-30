# MLIR TOC

Sublime Text plugin for [MLIR](https://mlir.llvm.org/) files: a three-pane workspace with the source, a table of contents of `// ----- // Section // ----- //` headers, and the currently selected section.

**Requirements:** Sublime Text 4. User packages run in Sublime’s **Python 3.3** plugin host on stable builds, so this plugin avoids Python 3.6+ syntax (e.g. no f-strings). It uses `sublime.list_syntaxes()` / `View.assign_syntax()`. An MLIR syntax package whose grammar is named `MLIR` is recommended for highlighting in the section pane.

## Commands

Open the Command Palette and run:

- **MLIR: Open TOC + Section Workspace** — builds the layout and syncs panes.
- **MLIR: Refresh TOC + Section** — refreshes from the source (also runs on save when the workspace is active).

## Install (manual)

1. Quit Sublime Text.
2. Put this folder in your **Packages** directory (not *Installed Packages*), e.g.  
   `~/.config/sublime-text/Packages/mlir-toc`  
   (or symlink your clone there).
3. Start Sublime again.

**Flatpak / Snap:** use **Preferences → Browse Packages…** in that install to see the real `Packages` path (it is not always `~/.config/sublime-text/`).

## Troubleshooting

- **Commands missing in the Command Palette** — Open **View → Show Console**. If you see a traceback mentioning `mlir_toc`, fix that error. Set `"debug": true` in **Preferences → Settings** and restart; you should see `MLIR TOC: plugin loaded` when the plugin loads. Confirm **Preferences → Browse Packages…** shows `mlir-toc` with `mlir_toc.py` and `mlir_toc.sublime-commands` inside.
- **Package Control → Install Package** — The package only appears there after it is merged into the default channel, or after **Package Control: Add Repository** with your GitHub URL.

In the palette, search for **`MLIR`** or **`TOC Section`**.
