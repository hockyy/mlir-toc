import re
import sublime
import sublime_plugin


def plugin_loaded():
    if sublime.load_settings("Preferences.sublime-settings").get("debug"):
        sublime.log_message("MLIR TOC: plugin loaded")


SECTION_RE = re.compile(r'^\s*//\s*-+\s*//\s*(.*?)\s*//\s*-+\s*//\s*$')
TOC_PREFIX = "MLIR TOC"
SECTION_PREFIX = "MLIR Section"

def assign_mlir_syntax(view):
    # Try to find a syntax literally named "MLIR"
    for syn in sublime.list_syntaxes():
        if syn.name.lower() == "mlir":
            view.assign_syntax(syn)
            return True
    return False

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
        sections.append({
            "title": title,
            "start_row": start_row,
            "end_row": end_row
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


def render_toc(sections):
    if not sections:
        return "(No MLIR section headers found)"
    out = []
    for i, s in enumerate(sections, 1):
        out.append("{:>3}. L{:<6} {}".format(i, s["start_row"] + 1, s["title"]))
    return "\n".join(out)


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

        toc_view = get_view_by_id(self.window, src.settings().get("mlir_toc_view_id"))
        section_view = get_view_by_id(self.window, src.settings().get("mlir_section_view_id"))
        if not toc_view or not section_view:
            return

        # TOC text + map rows -> section index
        toc_text = render_toc(sections)
        set_view_text(toc_view, toc_text)

        row_to_section = list(range(len(sections))) if sections else []
        toc_view.settings().set("mlir_sections", sections)
        toc_view.settings().set("mlir_toc_row_to_section_idx", row_to_section)
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

        sel = view.sel()
        if not sel:
            return

        toc_row, _ = view.rowcol(sel[0].begin())
        if toc_row < 0 or toc_row >= len(sections):
            return

        section = sections[toc_row]

        # Jump source
        jump_to_row(src, section["start_row"])

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
