# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build the macOS .app bundle locally for testing.

Usage:
    uv run _build_local.py          # build into dist/
    uv run _build_local.py -o       # build and open the .app
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def build_mac() -> Path:
    app = DIST / "pyrunner.app" / "Contents"
    for d in (app / "MacOS", app / "Resources"):
        d.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ROOT / "macos" / "Info.plist", app / "Info.plist")
    shutil.copy2(ROOT / "macos" / "icon.icns", app / "Resources" / "icon.icns")

    launch_src = ROOT / "macos" / "launch"
    launch_dst = app / "MacOS" / "launch"
    shutil.copy2(launch_src, launch_dst)
    launch_dst.chmod(0o755)

    # Remove quarantine attribute to avoid Gatekeeper warning
    subprocess.run(["xattr", "-cr", str(app.parent)], check=False)

    print(f"Built: {app.parent}")
    return app.parent


def build_windows() -> Path:
    exe_dir = DIST / "pyrunner-windows"
    exe_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("go") is None:
        print(
            "Error: Go is not installed (needed to build the Windows .exe).",
            file=sys.stderr,
        )
        sys.exit(1)

    subprocess.run(
        ["go", "build", "-ldflags", "-s -w", "-o", str(exe_dir / "pyrunner.exe"), "."],
        cwd=ROOT / "windows",
        check=True,
        env={**__import__("os").environ, "GOOS": "windows", "GOARCH": "amd64"},
    )

    print(f"Built: {exe_dir / 'pyrunner.exe'}")
    return exe_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pyrunner locally for testing.")
    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="Open the .app after building (macOS only)",
    )
    args = parser.parse_args()

    system = platform.system()
    if system == "Darwin":
        result = build_mac()
        if args.open:
            subprocess.run(["open", str(result)])
    elif system == "Windows":
        build_windows()
        if args.open:
            print("Note: --open is only supported on macOS.")
    else:
        print(f"Unsupported platform: {system}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
