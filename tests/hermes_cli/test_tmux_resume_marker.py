from pathlib import Path


def test_cli_writes_tmux_resume_marker(tmp_path, monkeypatch):
    import cli

    monkeypatch.setattr(cli, "_hermes_home", tmp_path)
    monkeypatch.chdir(tmp_path)

    agent = cli.HermesCLI(resume="20260629_120000_abcdef")
    marker = tmp_path / "runtime" / "tmux-resurrect" / f"{cli.os.getpid()}.tsv"

    assert marker.exists()
    session_id, cwd, profile = marker.read_text(encoding="utf-8").strip().split("\t")
    assert session_id == "20260629_120000_abcdef"
    assert Path(cwd) == tmp_path
    assert profile

    agent._remove_tmux_resume_marker()
    assert not marker.exists()


def test_cli_updates_tmux_resume_marker_when_session_rotates(tmp_path, monkeypatch):
    import cli

    monkeypatch.setattr(cli, "_hermes_home", tmp_path)
    monkeypatch.chdir(tmp_path)

    agent = cli.HermesCLI(resume="old_session")
    agent._set_session_id("new_session")

    marker = tmp_path / "runtime" / "tmux-resurrect" / f"{cli.os.getpid()}.tsv"
    session_id, cwd, profile = marker.read_text(encoding="utf-8").strip().split("\t")
    assert session_id == "new_session"
    assert Path(cwd) == tmp_path
    assert profile

    agent._remove_tmux_resume_marker()
