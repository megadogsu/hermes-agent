import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cli import HermesCLI


ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _plain(text: str) -> str:
    return ANSI_RE.sub("", text)


def test_action_event_includes_timestamp_label_icon_and_detail(monkeypatch):
    cli = HermesCLI.__new__(HermesCLI)
    monkeypatch.setattr(HermesCLI, "_action_timestamp", staticmethod(lambda: "12:34:56"))

    rendered = _plain(cli._format_action_event("Starting command", "/status", icon="⚙"))

    assert rendered == "[12:34:56] ⚙ Starting command: /status"


def test_action_preview_collapses_multiline_and_truncates():
    preview = HermesCLI._action_preview("line one\nline two " + "x" * 20, limit=18)

    assert preview == "line one line two…"


def test_action_preview_describes_text_plus_images():
    preview = HermesCLI._action_preview(("inspect this", ["/tmp/a.png", "/tmp/b.png"]))

    assert preview == "inspect this [2 images]"


def test_action_event_strips_user_supplied_ansi(monkeypatch):
    cli = HermesCLI.__new__(HermesCLI)
    monkeypatch.setattr(HermesCLI, "_action_timestamp", staticmethod(lambda: "01:02:03"))

    rendered = _plain(cli._format_action_event("Queued input", "safe \x1b[31mred", icon="＋"))

    assert rendered == "[01:02:03] ＋ Queued input: safe red"
