import os
import re
import sublime
import sublime_plugin


def plugin_loaded():
    if sublime.load_settings("Preferences.sublime-settings").get("debug"):
        sublime.log_message("MLIR TOC: plugin loaded")


SECTION_RE = re.compile(r'^\s*//\s*-+\s*//\s*(.*?)\s*//\s*-+\s*//\s*$')
FUNC_RE = re.compile(r'^\s*func\.func\b.*@([^\s(@]+)')
TOC_PREFIX = "MLIR TOC"
SECTION_PREFIX = "MLIR Section"
TOC_SYNTAX = "Packages/mlir-toc/mlir_toc.sublime-syntax"

# TOC display glyphs (keep ASCII-free lines stable for sublime-syntax matching)
GLYPH_SECTION = "\u25b8"       # ▸
GLYPH_FUNCTION_HDR = "\u25be"  # ▾
GLYPH_CHILD = "\u2514\u2500"   # └─
GLYPH_REF = "\u21b3"           # ↳
GLYPH_IN = "\u2192"            # →
GLYPH_SEP = "\u00b7"           # ·
SEC_MARK = "\u00a7"            # §


def assign_mlir_syntax(view):
    for syn in sublime.list_syntaxes():
        if syn.name.lower() == "mlir":
            view.assign_syntax(syn)
            return True
    return False


def assign_toc_syntax(view):
    for syn in sublime.list_syntaxes():
        if syn.name == "MLIR TOC":
            view.assign_syntax(syn)
            return True
    toc_path = os.path.join(sublime.packages_path(), "mlir-toc", "mlir_toc.sublime-syntax")
    if os.path.isfile(toc_path):
        view.assign_syntax(toc_path)
        return True
    view.assign_syntax(TOC_SYNTAX)
    return True

def get_view_by_id(window, vid):
    if not window or not vid:
        return None
    for v in window.views():
        if v.id() == vid:
            return v
    return None


def parse_sections(view):
    """
    Returns list of dicts:
    {
      "title": str,
      "start_row": int,     # header row
      "end_row": int,       # inclusive
    }
    """
    text = view.substr(sublime.Region(0, view.size()))
    lines = text.splitlines()
    headers = []

    for row, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            headers.append((row, (m.group(1) or "").strip() or "(untitled section)"))

    sections = []
    for i, (start_row, title) in enumerate(headers):
        if i + 1 < len(headers):
            end_row = headers[i + 1][0] - 1
        else:
            end_row = max(0, len(lines) - 1)
        functions = []
        seen_names = set()
        for row in range(start_row + 1, end_row + 1):
            m = FUNC_RE.match(lines[row])
            if not m:
                continue
            fn_name = m.group(1)
            if fn_name in seen_names:
                continue
            seen_names.add(fn_name)
            functions.append({
                "name": fn_name,
                "row": row
            })
        sections.append({
            "title": title,
            "start_row": start_row,
            "end_row": end_row,
            "functions": functions
        })
    return sections


def row_range_to_region(view, start_row, end_row):
    start_pt = view.text_point(start_row, 0)
    if end_row < start_row:
        end_pt = start_pt
    else:
        # end at end of end_row line
        end_line_region = view.line(view.text_point(end_row, 0))
        end_pt = end_line_region.end()
    return sublime.Region(start_pt, end_pt)


def jump_to_row(view, row):
    pt = view.text_point(row, 0)
    view.sel().clear()
    view.sel().add(sublime.Region(pt))
    view.show_at_center(pt)


def get_toc_config(src_view):
    package_settings = sublime.load_settings("MLIRTOC.sublime-settings")
    prefs = sublime.load_settings("Preferences.sublime-settings")
    mode = src_view.settings().get(
        "mlir_toc_group_by",
        package_settings.get(
            "mlir_toc_group_by",
            prefs.get("mlir_toc_group_by", "section")
        )
    )
    if mode not in ("section", "function"):
        mode = "section"
    show_functions = src_view.settings().get(
        "mlir_toc_show_functions",
        package_settings.get(
            "mlir_toc_show_functions",
            prefs.get("mlir_toc_show_functions", False)
        )
    )
    return {
        "group_by": mode,
        "show_functions": bool(show_functions)
    }


def _toc_banner(label):
    return "\u2500\u2500 {} \u2500\u2500".format(label)


def render_section_grouped_toc(sections, show_functions):
    out = [_toc_banner("{} sections".format(len(sections)))]
    row_targets = [None]
    for i, s in enumerate(sections, 1):
        out.append("{:>3} {} L{:<6}  {}".format(
            i, GLYPH_SECTION, s["start_row"] + 1, s["title"]))
        row_targets.append({
            "section_idx": i - 1,
            "target_row": s["start_row"]
        })
        if show_functions:
            for fn in s.get("functions", []):
                out.append("      {} L{:<6}  @{}".format(
                    GLYPH_CHILD, fn["row"] + 1, fn["name"]))
                row_targets.append({
                    "section_idx": i - 1,
                    "target_row": fn["row"]
                })
    return "\n".join(out), row_targets


def render_function_grouped_toc(sections):
    by_function = {}
    for idx, section in enumerate(sections):
        for fn in section.get("functions", []):
            by_function.setdefault(fn["name"], []).append({
                "section_idx": idx,
                "func_row": fn["row"]
            })

    if not by_function:
        return "\u2298 No func.func entries found in indexed sections", []

    function_names = sorted(by_function.keys())
    out = [_toc_banner("{} functions".format(len(function_names)))]
    row_targets = [None]
    for fn_name in function_names:
        out.append("{} @{}".format(GLYPH_FUNCTION_HDR, fn_name))
        row_targets.append(None)
        for entry in by_function[fn_name]:
            section = sections[entry["section_idx"]]
            out.append(
                "    {} L{:<6}  {} {}{:>3} {} L{:<6}  {}".format(
                    GLYPH_REF,
                    entry["func_row"] + 1,
                    GLYPH_IN,
                    SEC_MARK,
                    entry["section_idx"] + 1,
                    GLYPH_SEP,
                    section["start_row"] + 1,
                    section["title"]
                )
            )
            row_targets.append({
                "section_idx": entry["section_idx"],
                "target_row": entry["func_row"]
            })
    return "\n".join(out), row_targets


def render_toc(sections, config):
    if not sections:
        return "\u2298 No MLIR section headers found", []
    if config["group_by"] == "function":
        return render_function_grouped_toc(sections)
    return render_section_grouped_toc(sections, config["show_functions"])


def set_view_text(view, text):
    view.set_read_only(False)
    view.run_command("select_all")
    view.run_command("right_delete")
    view.run_command("append", {"characters": text, "force": True, "scroll_to_end": False})
    view.set_read_only(True)


class MlirTocSectionWorkspaceCommand(sublime_plugin.WindowCommand):
    """
    Creates 3-pane workspace:
      group 0: source
      group 1: TOC
      group 2: selected section only
    """
    def run(self):
        src = self.window.active_view()
        if not src:
            return

        # If invoked while TOC/section view focused, recover source.
        if src.settings().get("mlir_toc_view"):
            src_id = src.settings().get("mlir_source_view_id")
            real_src = get_view_by_id(self.window, src_id)
            if real_src:
                src = real_src

        # 2 columns, right column split into top/bottom
        self.window.set_layout({
            "cols": [0.0, 0.68, 1.0],
            "rows": [0.0, 0.5, 1.0],
            "cells": [
                [0, 0, 1, 2],  # left full-height source
                [1, 0, 2, 1],  # top-right toc
                [1, 1, 2, 2],  # bottom-right section
            ]
        })

        toc_view = get_view_by_id(self.window, src.settings().get("mlir_toc_view_id"))
        section_view = get_view_by_id(self.window, src.settings().get("mlir_section_view_id"))
        if not toc_view:
            toc_view = self.window.new_file()
            toc_view.set_scratch(True)
            toc_view.set_name("{} — {}".format(TOC_PREFIX, src.name() or "untitled"))
            toc_view.settings().set("mlir_toc_view", True)
            toc_view.settings().set("mlir_source_view_id", src.id())
            toc_view.settings().set("gutter", False)
            toc_view.settings().set("line_numbers", True)

        if not section_view:
            section_view = self.window.new_file()
            section_view.set_scratch(True)
            section_view.set_name("{} — {}".format(SECTION_PREFIX, src.name() or "untitled"))
            section_view.settings().set("mlir_section_view", True)
            section_view.settings().set("mlir_source_view_id", src.id())
            section_view.settings().set("word_wrap", False)

        assign_mlir_syntax(src)
        assign_toc_syntax(toc_view)
        assign_mlir_syntax(section_view)

        src.settings().set("mlir_toc_view_id", toc_view.id())
        src.settings().set("mlir_section_view_id", section_view.id())

        # Put views in correct panes
        self.window.set_view_index(toc_view, 1, 0)
        self.window.set_view_index(section_view, 2, 0)

        self.refresh_for_source(src)

        # keep focus on source
        self.window.focus_view(src)

    def refresh_for_source(self, src):
        sections = parse_sections(src)
        toc_config = get_toc_config(src)

        toc_view = get_view_by_id(self.window, src.settings().get("mlir_toc_view_id"))
        section_view = get_view_by_id(self.window, src.settings().get("mlir_section_view_id"))
        if not toc_view or not section_view:
            return

        # TOC text + map rows -> section index
        toc_text, row_targets = render_toc(sections, toc_config)
        set_view_text(toc_view, toc_text)
        assign_toc_syntax(toc_view)

        toc_view.settings().set("mlir_sections", sections)
        toc_view.settings().set("mlir_toc_row_targets", row_targets)
        toc_view.settings().set("mlir_source_view_id", src.id())
        section_view.settings().set("mlir_source_view_id", src.id())

        # Show first section by default
        if sections:
            self.show_section(src, section_view, sections[0])

    def show_section(self, src, section_view, section):
        region = row_range_to_region(src, section["start_row"], section["end_row"])
        content = src.substr(region)
        header = "// Section: {}  (lines {}-{})\n\n".format(
            section["title"], section["start_row"] + 1, section["end_row"] + 1)
        set_view_text(section_view, header + content)


class MlirTocSectionRefreshCommand(sublime_plugin.WindowCommand):
    def run(self):
        v = self.window.active_view()
        if not v:
            return

        # Resolve source view
        src = v
        if v.settings().get("mlir_toc_view") or v.settings().get("mlir_section_view"):
            src_id = v.settings().get("mlir_source_view_id")
            src = get_view_by_id(self.window, src_id)

        if not src:
            return
        self.window.run_command("mlir_toc_section_workspace")


class MlirTocClickListener(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view):
        if not view.settings().get("mlir_toc_view"):
            return

        win = view.window()
        if not win:
            return

        src = get_view_by_id(win, view.settings().get("mlir_source_view_id"))
        if not src:
            return

        sections = view.settings().get("mlir_sections") or []
        if not sections:
            return
        row_targets = view.settings().get("mlir_toc_row_targets") or []

        sel = view.sel()
        if not sel:
            return

        toc_row, _ = view.rowcol(sel[0].begin())
        if toc_row < 0 or toc_row >= len(row_targets):
            return

        target = row_targets[toc_row]
        if not target:
            return

        section_idx = target.get("section_idx")
        if section_idx is None or section_idx < 0 or section_idx >= len(sections):
            return
        target_row = target.get("target_row")
        section = sections[section_idx]

        # Jump source
        jump_to_row(src, target_row if isinstance(target_row, int) else section["start_row"])

        # Update section-only pane
        section_view = get_view_by_id(win, src.settings().get("mlir_section_view_id"))
        if section_view:
            region = row_range_to_region(src, section["start_row"], section["end_row"])
            content = src.substr(region)
            header = "// Section: {}  (lines {}-{})\n\n".format(
                section["title"], section["start_row"] + 1, section["end_row"] + 1)
            set_view_text(section_view, header + content)


class MlirTocAutoRefreshOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        if view.settings().get("mlir_toc_view") or view.settings().get("mlir_section_view"):
            return
        if view.settings().get("mlir_toc_view_id") or view.settings().get("mlir_section_view_id"):
            win = view.window()
            if win:
                win.run_command("mlir_toc_section_workspace")
