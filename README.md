# juv-launcher

A standalone desktop launcher for **Jupyter notebooks** — double-click to run any `.ipynb` file that has inline dependencies, no Python installation required.

Notebooks must declare their dependencies using the [PEP 723](https://peps.python.org/pep-0723/) inline script metadata format. The launcher uses [juv](https://github.com/manzt/juv) + [uv](https://docs.astral.sh/uv/) to read those dependencies and create an isolated environment automatically.

## Download

| macOS | Windows |
|---|---|
| [Download .app](https://github.com/fdrgsp/juv-launcher/releases/download/latest/juv-launcher-latest-mac.zip) | [Download .exe](https://github.com/fdrgsp/juv-launcher/releases/download/latest/juv-launcher-latest-windows.zip) |

## How it works

1. Download and unzip the file for your platform
2. Double-click the executable (`.app` on macOS, `.exe` on Windows)
3. A file picker appears — select a `.ipynb` file
4. The notebook opens in your browser

**Shortcut:** place the `.app`/`.exe` next to a `.ipynb` file and it will run that notebook directly, skipping the file picker.

**First run only:** `uv` and all packages are downloaded and cached automatically. Subsequent runs are fast.

## Preparing your notebook

The launcher runs notebooks using `uvx juv run`, which requires each notebook to declare its dependencies inline using [PEP 723](https://peps.python.org/pep-0723/) script metadata.

### Option 1: Use `juv add` (recommended)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then add dependencies to your notebook:

```bash
uvx juv add my_notebook.ipynb numpy pandas matplotlib
```

This writes a hidden `# /// script` cell into the notebook. You can verify it works locally:

```bash
uvx juv run my_notebook.ipynb
```

### Option 2: Add the metadata manually

Add a code cell at the top of your notebook with:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=1.26",
#   "pandas>=2.0",
#   "matplotlib>=3.8",
# ]
# ///
```

This cell tells `juv` which packages to install in the isolated environment.

## Platform notes

> **macOS Gatekeeper warning:** on first launch macOS may show a popup with only "Delete" or "Done" as options and block the app from opening. If this happens:

> 1. Open **System Settings → Privacy & Security**
> 2. Scroll to the bottom of the page
> 3. You will see a message about the app being blocked — click **"Open Anyway"**

> **Windows SmartScreen warning:** on first launch Windows may show a warning that the app is from an unknown publisher. If this happens:

> 1. Click **"More info"** on the warning dialog
> 2. Click **"Run anyway"**

## What users need

- An internet connection on first run (to fetch `uv` and packages — cached locally after that)
- Nothing else — no Python, no conda, no pip

## Looking to distribute notebooks to others?

Check out [personal-juv-launcher](https://github.com/fdrgsp/personal-juv-launcher) — a GitHub template for packaging notebooks as self-contained `.app`/`.exe` downloads with an auto-generated landing page.
