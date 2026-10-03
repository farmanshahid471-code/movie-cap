# movie-cap

Setup files for running [NarratoAI](https://github.com/linyqh/NarratoAI) — the AI film-narration and auto-editing tool — **fully in English**.

📖 **[Full setup guide → NARRATOAI-ENGLISH-SETUP.md](./NARRATOAI-ENGLISH-SETUP.md)**

---

## Windows: automatic installer for the GitHub source ZIP

If you downloaded `NarratoAI-main.zip` from GitHub, it contains **no** `start.bat` — the official one-click launcher only ships inside the separate 451 MB bundle. These files replace it.

**How to use them**

1. Download the three files from the [`windows/`](./windows) folder.
2. Put them in the **same folder as `webui.py`** (e.g. `F:\NarratoAI-main\NarratoAI-main`).
3. Double-click **`update-windows.bat`** and wait. Do this once.
4. Double-click **`start.bat`** every time you want to use NarratoAI.

| File | What it does |
|---|---|
| [`windows/update-windows.bat`](./windows/update-windows.bat) | One-time installer. Installs Python 3.12 (via uv), all ~145 Python packages and FFmpeg — **all inside this folder**, so drive C: is not filled up. Also creates `config.toml` and switches it to English with a working English voice. Safe to run again later. |
| [`windows/start.bat`](./windows/start.bat) | Starts the web interface and opens http://localhost:8501. Refuses to run with a readable message if the install is missing. |
| [`windows/narrato_setup_helper.py`](./windows/narrato_setup_helper.py) | Settings editor used by the installer. Can also be run by hand to switch language or point the app at an FFmpeg copy. |

**Everything is installed inside the project folder** (`F:\...`), so drive C: gets almost nothing:

| Created next to `webui.py` | Size | What it is |
|---|---|---|
| `.venv\` | ~1.5 GB | The Python environment |
| `tools\uv\` | ~40 MB | uv (the fast Python installer) |
| `tools\ffmpeg\` | ~250 MB | A full FFmpeg build (video cutting, subtitles) |
| `runtime\` | few MB | uv's Python 3.12 + temporary files |
| `.uv-cache\`, `.pip-cache\` | up to ~1 GB | Download caches (safe to delete later) |
| `config.toml` | 14 KB | Your settings (English by default) |

**About the "window closes instantly" problem:** both `.bat` files re-launch themselves inside a persistent console and `pause` on every error path, so you always get to read what happened. That behaviour is deliberate — close the window yourself when you are done.

**Verified before publishing:** CRLF line endings, no BOM, ASCII-only, balanced blocks, all 20 + 2 jump labels exist and are reachable, no bare `exit`, no unescaped parentheses in `echo`, every pinned package on PyPI resolves with a Windows/Python 3.12 wheel, and both download URLs serve real files (uv 18 MB, FFmpeg 200 MB). See [`tools/check_batch.py`](./tools/check_batch.py).
