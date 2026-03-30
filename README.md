# MLIR TOC

Sublime Text plugin for [MLIR](https://mlir.llvm.org/) files: a three-pane workspace with the source, a table of contents of `// ----- // Section // ----- //` headers, and the currently selected section.

**Requirements:** Sublime Text 4 (uses `sublime.list_syntaxes()` / `View.assign_syntax()`). An MLIR syntax package whose syntax is named `MLIR` is recommended for highlighting in the section pane.

## Commands

Open the Command Palette and run:

- **MLIR: Open TOC + Section Workspace** — builds the layout and syncs panes.
- **MLIR: Refresh TOC + Section** — refreshes from the source (also runs on save when the workspace is active).

## Package Control (for maintainers)

1. Push this repository to GitHub (package files live at the **repository root**).
2. Create an annotated release tag with [semantic versioning](https://semver.org/), e.g. `v1.0.0` or `1.0.0` (Package Control expects version tags).
3. Fork [sublimehq/package_control_channel](https://github.com/sublimehq/package_control_channel).
4. In `repository/m.json`, insert the following object **in alphabetical order** by `"name"` — it belongs **after** `"MLFi"` and **before** `"Moai Debugger"` (adjust if the channel file changed):

```json
{
	"name": "MLIR TOC",
	"details": "https://github.com/YOUR_USER/mlir-toc",
	"labels": ["mlir", "navigation", "text manipulation"],
	"releases": [
		{
			"sublime_text": ">=4000",
			"tags": true
		}
	]
}
```

Replace `YOUR_USER/mlir-toc` with your real repo path.

5. Install [ChannelRepositoryTools](https://packagecontrol.io/packages/ChannelRepositoryTools) in Sublime Text, run **ChannelRepositoryTools: Test Default Channel** (against your fork if needed), then open a pull request to `sublimehq/package_control_channel`.

Official checklist: [Submitting a package](https://packagecontrol.io/docs/submitting_a_package).
