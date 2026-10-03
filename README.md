# movie-cap

Setup files for running [NarratoAI](https://github.com/linyqh/NarratoAI) — the AI film-narration and auto-editing tool — **fully in English**.

---

## 📦 One-click download: the complete English bundle

**Everything in a single ZIP** — the full NarratoAI source with the English launcher already in place.

### ⬇️ [Download NarratoAI-ENGLISH-WINDOWS.zip](./dist/NarratoAI-ENGLISH-WINDOWS.zip) · 2.6 MB

On that page click **Download**. Direct link:

```
https://github.com/farmanshahid471-code/movie-cap/raw/arena/01a1034a-movie-cap/dist/NarratoAI-ENGLISH-WINDOWS.zip
```

**How to use it**

1. Extract it onto your **F:** drive so you end up with **`F:\NarratoAI\`** — keep the path short, because Windows has a 260-character path limit.
2. Double-click **`update-windows.bat`**. Wait for *"Installation complete"* (5–20 minutes the first time; it downloads Python, ~500 MB of packages and FFmpeg).
3. Double-click **`start.bat`**. Your browser opens at http://localhost:8501.

**What's inside**

| Path | What it is |
|---|---|
| `NarratoAI/` | Full NarratoAI source (upstream `main`, MIT, © 2024 linyq) |
| `NarratoAI/update-windows.bat` | One-time installer — puts Python 3.12, all packages and FFmpeg **inside `F:\NarratoAI`**, so drive C: stays clean |
| `NarratoAI/start.bat` | Launch the web UI |
| `NarratoAI/narrato_setup_helper.py` | Config editor (English defaults, wires up FFmpeg) |
| `NarratoAI/START-HERE-ENGLISH.txt` | Plain-English instructions + troubleshooting |
| `NarratoAI/NARRATOAI-ENGLISH-SETUP.md` | The full setup guide |
| `NarratoAI/MOVIE-RECAP-SETTINGS.md` | **Where to put the API key + the exact settings for a Movie-Recaps style video** |

English is configured automatically: `language = "en"`, Edge TTS (free voice, no API key) with `en-US-AvaMultilingualNeural-Female`, and English subtitles. Then set **Narration Language → English (United States)** inside the app so the *script* is English too.

**Before it can make videos** you need to add an LLM API key (OpenAI, Gemini, DeepSeek, Qwen, OpenRouter…) in `config.toml` or in the app under *Basic Settings*. Details in the guide.

---

## Where everything gets installed

Everything lands **inside the project folder**, so drive C: is left alone:

| Created next to `webui.py` | Size | What it is |
|---|---|---|
| `.venv\` | ~1.5 GB | The Python environment (all packages) |
| `tools\ffmpeg\` | ~250 MB | A full FFmpeg build (video cutting, subtitle burn-in) |
| `tools\uv\` | ~40 MB | uv — the fast Python installer |
| `runtime\` | few MB | uv's Python 3.12 + temporary working files |
| `.uv-cache\`, `.pip-cache\` | up to ~1 GB | Download caches — delete any time |
| `config.toml` | 14 KB | Your settings (English by default) |

Total ≈ **3 GB**, all on the same drive as the folder.

---

## Or: just the launcher files

Already have the NarratoAI source? Copy the three files from [`windows/`](./windows) into the folder containing `webui.py`:

| File | What it does |
|---|---|
| [`windows/update-windows.bat`](./windows/update-windows.bat) | One-time installer. Skips anything already installed, so it is safe to re-run. |
| [`windows/start.bat`](./windows/start.bat) | Starts the web interface and opens http://localhost:8501. Refuses to run with a readable message if the install is missing. |
| [`windows/narrato_setup_helper.py`](./windows/narrato_setup_helper.py) | Settings editor used by the installer; can also be run by hand. |

### About the "window closes instantly" problem

Both `.bat` files re-launch themselves inside a persistent console, and **every** error path ends with a `pause` and a readable message — so a failure can never flash past. That behaviour is deliberate; close the window yourself when you are done.

### What was verified

- **CRLF line endings**, confirmed byte-for-byte in the pushed GitHub blob *and* after a ZIP round-trip (LF-only `.bat` files silently break `goto`), no BOM, ASCII-only.
- **Control flow:** balanced blocks, all 20 + 2 jump labels exist and are reachable, no bare `exit`, no unescaped parentheses in `echo` — checked by [`tools/check_batch.py`](./tools/check_batch.py).
- **Dependencies:** every pinned requirement resolves on PyPI with a Windows/Python 3.12 wheel (`pysrt` has no wheel but builds from sdist via setuptools).
- **Download URLs:** both return real assets — uv 18,043,715 bytes, FFmpeg 200,163,050 bytes.
- **The bundle ZIP:** CRC check passes (192 files), longest extracted path is 81 characters, and the copy on GitHub is byte-identical to the verified local build (sha256 `46abccc8f72db2a1630defc4554eb504953dad48377582f3cc5ebcec0b8bbc1a`).

*Not verified: the `.bat` files have never been executed on real Windows — this sandbox is Linux. The checks above are static analysis plus live HTTP/PyPI verification. If something does fail, the window will stay open and show you the error.*

---

📖 **[Full setup guide → NARRATOAI-ENGLISH-SETUP.md](./NARRATOAI-ENGLISH-SETUP.md)** — downloads, requirements, install options, API keys, and the exact list of strings that stay Chinese (with translations).
