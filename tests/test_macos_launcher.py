"""Tests for macos/launch.sh — calls the real bash functions via subprocess."""

import os
import subprocess

import pytest

LAUNCH_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "macos", "launch.sh")


def _bash(cmd: str) -> str:
    result = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    return result.stdout.strip()


def _call(func: str, *args: str) -> str:
    quoted = " ".join(f'"{a}"' for a in args)
    return _bash(f'source "{LAUNCH_SCRIPT}" && {func} {quoted}')


# ── select_runner ──────────────────────────────────────────────────────────────

select_runner_cases = [
    ("ipynb uses juv", "notebook.ipynb", "", "uvx juv run"),
    (
        "py with marimo dep edit mode",
        "nb.py",
        '# /// script\n# dependencies = [\n#   "marimo",\n# ]\n#\n# [pyrunner]\n# marimo-mode = "edit"\n# ///\n',
        "uvx marimo edit --sandbox",
    ),
    (
        "py with marimo dep run mode",
        "nb.py",
        '# /// script\n# dependencies = [\n#   "marimo",\n# ]\n#\n# [pyrunner]\n# marimo-mode = "run"\n# ///\n',
        "uvx marimo run --sandbox",
    ),
    (
        "py without marimo",
        "script.py",
        '# dependencies = [\n#   "numpy",\n# ]',
        "uv run",
    ),
    ("py empty content", "script.py", "", "uv run"),
    (
        "py with marimo version spec edit mode",
        "nb.py",
        '# /// script\n# dependencies = [\n#   "marimo>=0.1",\n# ]\n#\n# [pyrunner]\n# marimo-mode = "edit"\n# ///\n',
        "uvx marimo edit --sandbox",
    ),
    (
        "py with single-quoted marimo edit mode",
        "nb.py",
        "# /// script\n# dependencies = [\n#   'marimo',\n# ]\n#\n# [pyrunner]\n# marimo-mode = \"edit\"\n# ///\n",
        "uvx marimo edit --sandbox",
    ),
    (
        "py with unrelated marimo mention",
        "script.py",
        "# this is not marimo_extra related",
        "uv run",
    ),
    (
        "py with marimo dep no pyrunner section defaults to edit",
        "nb.py",
        '# /// script\n# dependencies = [\n#   "marimo",\n# ]\n# ///\n',
        "uvx marimo edit --sandbox",
    ),
]


@pytest.mark.parametrize("desc,filename,content,expected", select_runner_cases)
def test_select_runner(tmp_path, desc, filename, content, expected):
    path = tmp_path / filename
    path.write_text(content)
    actual = _call("select_runner", str(path))
    assert actual == expected


# ── marimo_mode ────────────────────────────────────────────────────────────────

marimo_mode_cases = [
    ("no script block", '# dependencies = [\n#   "marimo",\n# ]', ""),
    ("run mode", '# /// script\n# [pyrunner]\n# marimo-mode = "run"\n# ///\n', "run"),
    (
        "edit mode",
        '# /// script\n# [pyrunner]\n# marimo-mode = "edit"\n# ///\n',
        "edit",
    ),
    (
        "single-quoted run mode",
        "# /// script\n# [pyrunner]\n# marimo-mode = 'run'\n# ///\n",
        "run",
    ),
    (
        "no pyrunner section",
        '# /// script\n# dependencies = [\n#   "marimo",\n# ]\n# ///\n',
        "",
    ),
    (
        "section without marimo-mode",
        '# /// script\n# [pyrunner]\n# other_key = "value"\n# ///\n',
        "",
    ),
    (
        "marimo-mode after other keys",
        '# /// script\n# [pyrunner]\n# other = "x"\n# marimo-mode = "run"\n# ///\n',
        "run",
    ),
]


@pytest.mark.parametrize("desc,content,expected", marimo_mode_cases)
def test_marimo_mode(tmp_path, desc, content, expected):
    path = tmp_path / "nb.py"
    path.write_text(content)
    actual = _call("marimo_mode", str(path))
    assert actual == expected
