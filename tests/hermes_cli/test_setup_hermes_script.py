from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = REPO_ROOT / "setup-hermes.sh"


def test_setup_hermes_script_is_valid_shell():
    result = subprocess.run(["bash", "-n", str(SETUP_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_setup_hermes_script_has_termux_path():
    content = SETUP_SCRIPT.read_text(encoding="utf-8")

    assert "is_termux()" in content
    assert ".[termux]" in content
    assert "constraints-termux.txt" in content
    assert "$PREFIX/bin" in content


def test_setup_hermes_reload_instruction_is_bash_zsh_gated():
    content = SETUP_SCRIPT.read_text(encoding="utf-8")

    assert 'SHELL_NAME="$(basename "${SHELL:-}"' in content
    assert '[[ "$SHELL_NAME" == "zsh" ]]' in content
    assert '[[ "$SHELL_NAME" == "bash" ]]' in content
    assert 'if [ -n "$SHELL_CONFIG" ]; then\n        echo "  1. Reload your shell:"' in content
    assert 'source $SHELL_CONFIG' in content
    assert "Fallback to checking existing files" not in content
