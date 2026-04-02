# MLIR TOC

Sublime Text plugin for [MLIR](https://mlir.llvm.org/) files: a three-pane workspace with the source, a table of contents of `// ----- // Section // ----- //` headers, and the currently selected section.

For local development (editors, tooling, or any scripts you run outside Sublime), Python **3.8** is pinned in **`.python-version`** for pyenv, asdf, and similar tools. That does not change the runtime inside Sublime Text.

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

- **Commands missing in the Command Palette** — Open **View → Show Console**. If you see a traceback mentioning `mlir_toc`, fix that error. Set `"debug": true` in **Preferences → Settings** and restart; you should see `MLIR TOC: plugin loaded` when the plugin loads. Confirm **Preferences → Browse Packages…** shows `mlir-toc` with `mlir_toc.py`, `mlir_toc.sublime-commands`, and `mlir.sublime-syntax` inside.
- **Package Control → Install Package** — The package only appears there after it is merged into the default channel, or after **Package Control: Add Repository** with your GitHub URL.

In the palette, search for **`MLIR`** or **`TOC Section`**.

## License

This project is released under the [MIT License](LICENSE).

`mlir.sublime-syntax` is derived from [rrbutani/sublime-mlir-syntax](https://github.com/rrbutani/sublime-mlir-syntax) (MIT). Rahul Butani’s copyright (2020) appears in `LICENSE` alongside this project’s; the syntax file header points to the upstream repo.
