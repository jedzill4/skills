"""Textual TUI to review scaffolding rule-proposal issues.

List view: issues sorted by priority, filterable by any label / text and by state/type.
Detail view: read the proposal body + comments and approve / decline / had-comments / comment.
"""

from __future__ import annotations

import sys
import webbrowser
from typing import ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Markdown, TextArea

from review import gh
from review.gh import Issue, IssueDetail

STATE_CYCLE = [None, "proposal", "had-comments", "approved", "declined"]
TYPE_CYCLE = ["proposal", None, "bug", "feature", "build", "question"]


class CommentModal(ModalScreen[str | None]):
    """Prompt for a comment body."""

    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="comment-box"):
            yield TextArea(id="comment-text")
            yield Button("Submit (ctrl+s)", id="submit", variant="primary")

    def on_mount(self) -> None:
        self.query_one(TextArea).focus()

    def key_ctrl_s(self) -> None:
        self.dismiss(self.query_one(TextArea).text.strip() or None)

    def on_button_pressed(self, _: Button.Pressed) -> None:
        self.dismiss(self.query_one(TextArea).text.strip() or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class FilterModal(ModalScreen[str | None]):
    """Prompt for a label/text filter."""

    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="filter-box"):
            yield Input(placeholder="filter by label or title text…", id="filter-input")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)


class DetailScreen(Screen):
    """Read one proposal and act on it."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("j", "nav(1)", "Next"),
        Binding("k", "nav(-1)", "Prev"),
        Binding("a", "set_state('approved')", "Approve"),
        Binding("d", "set_state('declined')", "Decline"),
        Binding("h", "set_state('had-comments')", "Had-comments"),
        Binding("c", "comment", "Comment"),
        Binding("w", "web", "Open in browser"),
    ]

    def __init__(self, issue: Issue) -> None:
        super().__init__()
        self.issue = issue

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Markdown("_loading…_", id="body")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_title()
        self.load_body()

    def _refresh_title(self) -> None:
        i = self.issue
        self.title = f"#{i.number}  [{i.state}]  {i.title}"
        self.sub_title = f"{i.area} · {i.enforcer_text} · priority:{i.priority}"

    @staticmethod
    def _format_detail(detail: IssueDetail) -> str:
        body = detail.body or "_(no body)_"
        parts = [body, "---", f"## Comments ({len(detail.comments)})"]
        if not detail.comments:
            parts.append("_no comments yet_")
        for c in detail.comments:
            parts.append(f"**@{c.author}** · {c.when}\n\n{c.body}")
        return "\n\n".join(parts)

    @work(thread=True)
    def load_body(self) -> None:
        try:
            md = self._format_detail(gh.issue_detail(self.issue.number))
        except gh.GhError as exc:
            md = f"**error loading issue:** {exc}"
        self.app.call_from_thread(self.query_one("#body", Markdown).update, md)

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_nav(self, delta: int) -> None:
        nxt = self.app.neighbor(self.issue.number, delta)
        if nxt is None:
            self.notify("end of list" if delta > 0 else "start of list")
            return
        self.issue = nxt
        self._refresh_title()
        self.query_one("#body", Markdown).update("_loading…_")
        self.load_body()

    @work(thread=True)
    def action_set_state(self, new_state: str) -> None:
        try:
            gh.set_state(self.issue, new_state)
        except gh.GhError as exc:
            self.app.call_from_thread(self.notify, f"failed: {exc}", severity="error")
            return
        self.issue.state = new_state
        self.issue.is_open = new_state != "declined"
        self.issue.labels = [
            name for name in self.issue.labels if not name.startswith("state:")
        ] + [f"state:{new_state}"]
        self.app.call_from_thread(self._refresh_title)
        self.app.call_from_thread(self.app.refresh_row, self.issue)
        self.app.call_from_thread(self.notify, f"#{self.issue.number} → {new_state}")

    def action_comment(self) -> None:
        def after(body: str | None) -> None:
            if body:
                self._post_comment(body)

        self.app.push_screen(CommentModal(), after)

    @work(thread=True)
    def _post_comment(self, body: str) -> None:
        try:
            gh.add_comment(self.issue.number, body)
        except gh.GhError as exc:
            self.app.call_from_thread(self.notify, f"comment failed: {exc}", severity="error")
            return
        self.app.call_from_thread(self.notify, "comment added")
        self.app.call_from_thread(self.load_body)  # refresh to show the new comment

    def action_web(self) -> None:
        webbrowser.open(gh.web_url(self.issue.number))


class ReviewApp(App):
    """Top-level review app: the issue list."""

    CSS = """
    #comment-box, #filter-box { align: center middle; width: 80%; height: auto;
        background: $panel; border: tall $primary; padding: 1; }
    #comment-text { height: 12; }
    DataTable { height: 1fr; }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("enter", "open", "Open"),
        Binding("o", "open", "Open"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("slash", "filter", "Filter"),
        Binding("x", "clear_filter", "Clear filter"),
        Binding("s", "cycle_state", "State filter"),
        Binding("t", "cycle_type", "Type filter"),
        Binding("r", "reload", "Reload"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.issues: list[Issue] = []
        self.query: str = ""
        self.state_filter: int = 0
        self.type_filter: int = 0  # 0 = proposal

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        table = DataTable(cursor_type="row", zebra_stripes=True)
        table.add_columns("#", "pri", "state", "area", "enforcer", "title")
        yield table
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()
        self.reload()

    @work(thread=True)
    def reload(self) -> None:
        try:
            issues = gh.list_issues()
        except gh.GhError as exc:
            self.app.call_from_thread(self.notify, f"gh error: {exc}", severity="error")
            return
        self.issues = issues
        self.app.call_from_thread(self._rebuild)

    def _visible(self) -> list[Issue]:
        state = STATE_CYCLE[self.state_filter]
        itype = TYPE_CYCLE[self.type_filter]
        q = self.query.lower()
        out = []
        for i in self.issues:
            if itype and i.type != itype:
                continue
            if state and i.state != state:
                continue
            if q and q not in i.title.lower() and not any(q in lab.lower() for lab in i.labels):
                continue
            out.append(i)
        return out

    def _rebuild(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for i in self._visible():
            table.add_row(
                str(i.number),
                i.priority,
                i.state,
                i.area,
                i.enforcer_text,
                i.title,
                key=str(i.number),
            )
        state = STATE_CYCLE[self.state_filter] or "all"
        itype = TYPE_CYCLE[self.type_filter] or "all"
        self.sub_title = (
            f"{len(self._visible())}/{len(self.issues)} · type:{itype} · state:{state}"
            + (f" · filter:'{self.query}'" if self.query else "")
        )
        self.title = "proposal review"

    def refresh_row(self, issue: Issue) -> None:
        self._rebuild()

    def action_cursor_down(self) -> None:
        self.query_one(DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(DataTable).action_cursor_up()

    def neighbor(self, number: int, delta: int) -> Issue | None:
        """Return the next/prev issue in the current filtered+sorted view."""
        vis = self._visible()
        nums = [i.number for i in vis]
        if number not in nums:
            return None
        target = nums.index(number) + delta
        return vis[target] if 0 <= target < len(vis) else None

    def _open_issue(self, key: str | None) -> None:
        issue = next((i for i in self.issues if str(i.number) == key), None)
        if issue:
            self.push_screen(DetailScreen(issue))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # DataTable consumes `enter` and posts this instead of firing the app binding.
        self._open_issue(event.row_key.value)

    def action_open(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        self._open_issue(key)

    def action_filter(self) -> None:
        def after(value: str | None) -> None:
            if value is not None:
                self.query = value
                self._rebuild()

        self.push_screen(FilterModal(), after)

    def action_clear_filter(self) -> None:
        self.query = ""
        self.state_filter = 0
        self.type_filter = 0
        self._rebuild()

    def action_cycle_state(self) -> None:
        self.state_filter = (self.state_filter + 1) % len(STATE_CYCLE)
        self._rebuild()

    def action_cycle_type(self) -> None:
        self.type_filter = (self.type_filter + 1) % len(TYPE_CYCLE)
        self._rebuild()

    def action_reload(self) -> None:
        self.reload()


def _plain() -> int:
    """Non-TUI smoke test: print the sorted list."""
    issues = gh.list_issues()
    print(f"{len(issues)} issues on {gh.REPO} (sorted by priority):\n")
    for i in issues:
        print(
            f"  #{i.number:<4} {i.priority:<7} {i.state:<13} "
            f"{i.area:<14} {i.enforcer_text:<22} {i.title[:50]}"
        )
    return 0


def main() -> int:
    if "--plain" in sys.argv:
        return _plain()
    ReviewApp().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
