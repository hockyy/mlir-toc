# MLIR TOC

Sublime Text plugin for [MLIR](https://mlir.llvm.org/) files: a three-pane workspace with the source, a table of contents of `// ----- // Section // ----- //` headers, and the currently selected section.

**Requirements:** Sublime Text 4 (uses `sublime.list_syntaxes()` / `View.assign_syntax()`). An MLIR syntax package whose syntax is named `MLIR` is recommended for highlighting in the section pane.

## Commands

Open the Command Palette and run:

- **MLIR: Open TOC + Section Workspace** — builds the layout and syncs panes.
- **MLIR: Refresh TOC + Section** — refreshes from the source (also runs on save when the workspace is active).
