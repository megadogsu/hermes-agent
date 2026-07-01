from queue import Queue

from cli import HermesCLI, _chunk_discord_message


def _make_cli(enabled=True):
    cli = HermesCLI.__new__(HermesCLI)
    cli.discord_mirror_enabled = enabled
    cli.discord_mirror_channel = "12345" if enabled else ""
    cli.discord_mirror_thread_id = ""
    cli.discord_mirror_events = {"user", "assistant", "command", "status", "error", "tool"}
    cli._discord_mirror_queue = Queue(maxsize=10)
    cli._discord_mirror_worker_started = False
    cli._discord_mirror_worker_failed = False
    cli.session_id = "sess-1"

    def _start_worker():
        cli._discord_mirror_worker_started = True

    cli._start_discord_mirror_worker = _start_worker
    return cli


def test_discord_mirror_noops_when_disabled():
    cli = _make_cli(enabled=False)

    cli._discord_mirror("status", "hello")

    assert cli._discord_mirror_queue.empty()
    assert cli._discord_mirror_worker_started is False


def test_discord_mirror_enqueues_label_session_and_body():
    cli = _make_cli(enabled=True)

    cli._discord_mirror("status", "Processing command...")

    payload = cli._discord_mirror_queue.get_nowait()
    assert "Hermes CLI status" in payload
    assert "sess-1" in payload
    assert "Processing command..." in payload


def test_discord_mirror_filters_configured_events():
    cli = _make_cli(enabled=True)
    cli.discord_mirror_events = {"assistant"}

    cli._discord_mirror("tool", "terminal completed")
    cli._discord_mirror("assistant", "Done")

    payload = cli._discord_mirror_queue.get_nowait()
    assert "Hermes CLI assistant" in payload
    assert "Done" in payload
    assert cli._discord_mirror_queue.empty()


def test_format_mirror_user_message_handles_multimodal_payload():
    cli = _make_cli(enabled=True)
    payload = [
        {"type": "text", "text": "hello"},
        {"type": "image", "path": "/tmp/a.png"},
    ]

    text = cli._format_mirror_user_message(payload)

    assert '"type": "text"' in text
    assert '"path": "/tmp/a.png"' in text


def test_discord_message_chunking_stays_under_api_limit():
    chunks = _chunk_discord_message("a" * 4500, limit=1900)

    assert len(chunks) == 3
    assert all(len(chunk) <= 1900 for chunk in chunks)
    assert "".join(chunks) == "a" * 4500
