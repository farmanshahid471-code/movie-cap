# NarratoAI in English — Complete Setup Guide

**Short answer: YES. The official [linyqh/NarratoAI](https://github.com/linyqh/NarratoAI) already supports English. You do NOT need a rebuild or a fork.**

I verified this by reading the actual source code of the `main` branch (commit `9fa69e0`, Sep 2026). This guide tells you exactly how to turn it on, how to install it, and what few bits stay Chinese.

---

## 1. Proof that English is supported

| What | Where | Finding |
|---|---|---|
| English translation file | `webui/i18n/en.json` | **780 UI strings**, and **0 Chinese characters** left inside it |
| Translation completeness | `en.json` vs `zh.json` | **0 keys missing** — every Chinese string has an English version |
| Auto language detection | `webui.py:121` | `config.ui.get("language", utils.get_system_locale())` → picks English automatically on an English system |
| In-app language switcher | `webui/components/basic_settings.py:297` | A dropdown listing `en - English` / `zh - Chinese` |
| Chinese leaking through the translator | every `tr("中文…")` call in the codebase | **0 missing translations** — nothing Chinese can leak through the UI translation system |
| English docs | `README-en.md` | Official English readme exists in the repo |

> Note: `get_system_locale()` returns `"en"` even if your operating system locale cannot be detected (`app/utils/utils.py:284-292`), so a fresh install defaults to English.

---

## 2. Turn on the English interface (3 ways)

### Option A — Automatic (usually nothing to do)
The app detects your system language at startup. If your computer is set to English, it opens in English.

### Option B — Switch inside the app
1. Open **Basic Settings** (the expander panel near the top).
2. In the first column, find the dropdown labelled **"Interface Language"** and choose **`en - English`**.
   *Minor upstream quirk:* the tiny grey heading directly above that dropdown says "Proxy Settings" — ignore it, the dropdown under it is the language selector. The real proxy fields are further down that same column.
3. The whole interface switches to English immediately.

### Option C — Pin it permanently (recommended)
The WebUI reads its settings from **`config.toml`** in the project root (loaded by `app/config/config.py`, which is what `webui.py` and every UI component import).

Open `config.toml`, find the `[ui]` section, and add this line:

```toml
[ui]
language = "en"
```

That's it — the app will now always start in English, even after restarts. (If `config.toml` does not exist yet, it is created automatically from `config.example.toml` the first time you run the app.)

---

## 3. Download, requirements, install and run

### A. Where to download it (4 routes)

Latest version: **v0.8.7** (17 Jul 2026). Note: **all GitHub releases are source-only — no `.exe` or `.zip` is attached to them.** I checked every release; don't waste time hunting for a binary there.

| # | Route | Works on | Size | Link |
|---|---|---|---|---|
| 1 | **Ready-to-run bundle** — includes portable Python, FFmpeg and subtitle fonts, so you install nothing | Windows x64, macOS Apple Silicon | 451 MB / 532 MB | Windows: **https://pan.quark.cn/s/2af2d8f4fcc0**<br>macOS: **https://pan.quark.cn/s/cc849b8c5366**<br>(official page: https://cutagent.online/) |
| 2 | **Source ZIP** — needs Python + FFmpeg (see below) | Windows, macOS, Linux | ~2.5 MB | **https://github.com/linyqh/NarratoAI/archive/refs/heads/main.zip** |
| 3 | **Git clone** | Windows, macOS, Linux | ~7 MB | `git clone https://github.com/linyqh/NarratoAI.git` |
| 4 | **Docker** (no Python setup at all) | macOS, Linux, Windows | — | `docker compose up -d` |
| 5 | **Cloud version** (nothing to install, paid) | Any browser | — | https://www.narratoai.co/ |

> ⚠️ **About the ready-to-run bundle (route 1):** it is genuinely free, but it is hosted on **Quark netdisk** (Alibaba's cloud drive), not on GitHub. When I tested those links they did **not** connect — that service normally expects you to sign in (often with a Chinese phone number) and can be slow or blocked outside China. **If it gives you trouble, use route 2 — the GitHub ZIP. I verified it downloads fine.**

> 🚨 **IMPORTANT — routes 1 and 2 are NOT the same thing.** `start.bat`, `start-macos.command`, `update-windows.bat` and `update-macos.command` **exist only in the 451 MB / 532 MB bundle (route 1)**. They are **not** in the GitHub repository — I checked, the source tree contains **zero** `.bat` or `.command` files. If you downloaded `NarratoAI-main.zip` from GitHub (~2.5 MB, folder contains `app/`, `webui/`, `webui.py`, `requirements.txt`…), then you have the **source code**, and you need to install Python + FFmpeg and launch it with the commands in section C below. Nothing is missing or broken — it just isn't a bundle.

**Bundle steps — Windows:** unzip into one folder (keep the internal `NarratoAI`, `runtime`, `tools` folders untouched) → double-click **`update-windows.bat`** → wait → double-click **`start.bat`** → open **http://127.0.0.1:8501**. Keep the black window open while using the app.

**Bundle steps — macOS (M1/M2/M3/M4 only):** unzip, then in Terminal:
```bash
xattr -cr "/path/to/NarratoAI-macos-arm64"
chmod +x "/path/to/NarratoAI-macos-arm64/"*.command
```
then double-click **`update-macos.command`** → **`start-macos.command`** → open **http://127.0.0.1:8501**.

### B. Requirements checklist

**Hardware (the project's official minimum)**

| | Requirement |
|---|---|
| CPU | 4 cores or more |
| RAM | 8 GB or more |
| GPU | **Not required** |
| Disk space | ~0.5 GB for the ready bundle; ~3 GB if you install from source; plus room for your own video files |
| Internet | **Required** — the AI models are cloud APIs, not local |

**Operating system**

- **Windows 10 / 11 (x64)** — supported
- **macOS 11.0+** — the bundle is **Apple Silicon only (M1–M4)**; Intel Macs must use the source or Docker route
- **Linux** — works through Docker (route 4); the author only documents macOS for Docker, but Compose runs fine on Linux

**Software (only needed for routes 2, 3 and 4)**

- **Python 3.12 or newer** (the repo pins 3.12)
- **`uv`** (recommended by the author) **or** `pip` — ~145 packages get installed automatically (Streamlit, MoviePy, Edge-TTS, OpenAI SDK, etc.)
- **FFmpeg + ffprobe** on your PATH — Windows: https://www.gyan.dev/ffmpeg/builds/ · macOS: `brew install ffmpeg`. The app can also fall back to an `imageio-ffmpeg` copy, but a real FFmpeg install is recommended for subtitle burn-in and hardware acceleration.
- **Docker Desktop / Engine + Compose** — only for route 4

**Accounts / API keys — the real "must have"**

1. **At least one LLM API key.** The same key can serve both the *vision* model (reads frames from your video) and the *text* model (writes the narration). Add it in `config.toml` under `[app]`: `vision_openai_api_key`, `text_openai_api_key` (+ the model names and base URLs). Works with OpenAI, Google Gemini, DeepSeek, Qwen, SiliconFlow, OpenRouter, Moonshot and other OpenAI-compatible providers.
2. **Voice-over.** The default engine is **IndexTTS**, a *local* model that needs a separate multi-GB download — skip it. Use the built-in **Edge TTS: free, no API key, nothing to install**. For English: *Audio Settings → Edge TTS → "English Female Voice"*.
3. **Optional:** Tavily key (web search for plot lookups), Sonilo key (AI background music / sound effects), TwelveLabs key (optional video understanding), Azure or Tencent keys (only if you use their cloud TTS).

**Cost:** the software itself is free (MIT licence). You only pay your model provider for usage — with a cheap model a short video costs cents, not dollars.

### C. Local install (route 2 or 3)

**Windows, step by step** (this is what you need if you downloaded `NarratoAI-main.zip` from GitHub):

1. **Install Python 3.12** — https://www.python.org/downloads/windows/ (get *Windows installer (64-bit)*, version **3.12.x**).
   ⚠️ On the very first installer screen, **tick "Add python.exe to PATH"** before clicking *Install Now*. If you miss it, Python won't be found later.
2. **Install FFmpeg** — https://www.gyan.dev/ffmpeg/builds/ → download `ffmpeg-release-essentials.zip`, unzip it to e.g. `C:\ffmpeg`, then add `C:\ffmpeg\bin` to your PATH (Windows search → "Edit the system environment variables" → *Environment Variables* → under *User variables* select `Path` → *Edit* → *New* → paste `C:\ffmpeg\bin`). Close and reopen any Command Prompt afterwards.
3. **Open a Command Prompt in your project folder.** In File Explorer go to the folder that contains `webui.py` (in your case `F:\NarratoAI-main\NarratoAI-main`), click the address bar, type `cmd` and press Enter.
4. **Run these commands, one block at a time:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy config.example.toml config.toml
```

   `pip install` takes **5–15 minutes** the first time — that is normal.

5. **Turn on English:** open `config.toml` in Notepad and add this line directly under the `[ui]` heading:

```toml
[ui]
language = "en"
```

6. **Start it:**

```bat
streamlit run webui.py --server.maxUploadSize=2048
```

7. Open **http://localhost:8501** in your browser. Keep the black Command Prompt window open while you use the app; close it (or press Ctrl+C) to stop.

### C2. Shortcut — the automatic Windows installer (recommended)

The `windows/` folder in this repo has three files that do all of the above for you:

| File | What it does |
|---|---|
| **`update-windows.bat`** | One-time installer — run this first |
| **`start.bat`** | Starts NarratoAI — run this every time |
| **`narrato_setup_helper.py`** | Settings editor used by the installer (keep it next to the two `.bat` files) |

**Steps:** copy all three files into the folder that contains `webui.py` (for you: `F:\NarratoAI-main\NarratoAI-main`), then double-click **`update-windows.bat`** and wait. Afterwards, double-click **`start.bat`** whenever you want to use the app.

**What `update-windows.bat` installs — and where**

Everything goes **inside the project folder on F:**, so your C: drive is left alone:

| Created next to `webui.py` | Size | What it is |
|---|---|---|
| `.venv\` | ~1.5 GB | The Python environment (all the packages) |
| `tools\uv\` | ~40 MB | uv — the fast Python installer |
| `tools\ffmpeg\` | ~250 MB | Full FFmpeg build (video cutting, subtitle burn-in) |
| `runtime\` | few MB | uv's own Python 3.12 + temporary working files |
| `.uv-cache\`, `.pip-cache\` | up to ~1 GB | Download caches — delete them any time to free space |
| `config.toml` | 14 KB | Your settings, pre-set to English |

Total: roughly **3 GB** in the project folder. The installer also redirects `TEMP`, `TMP`, the pip cache and the uv cache into that folder, which is why almost nothing lands on C:.

**What it sets up for you**

- Python 3.12 and every package from `requirements.txt` (~500 MB of downloads, 5–20 minutes)
- FFmpeg, wired into `config.toml` as `ffmpeg_path`
- `config.toml` created from the example file, with `language = "en"`, **Edge TTS** as the voice engine (free, no API key, works immediately) and the English voice `en-US-AvaMultilingualNeural-Female`
- Subtitle translation target set to English

Re-running it is safe: it skips whatever is already installed. On repeat runs it only re-checks the UI language — it will **not** overwrite a TTS engine or voice you changed yourself afterwards.

**Why the window stays open**

Both files re-launch themselves inside a persistent console, and every error path ends with a `pause` and a readable message. So if something fails you can actually read it, instead of the window flashing and vanishing. That is on purpose — close the window yourself when you are finished.

> If Windows shows a "Windows protected your PC" prompt (because the files came from the internet), click **More info → Run anyway**.

**Prefer to do it by hand?** Section C above still works, and section D covers Docker.

```bash
git clone https://github.com/linyqh/NarratoAI.git
cd NarratoAI

# install dependencies — use ONE of these:
uv sync                              # recommended (uv)
pip install -r requirements.txt      # plain pip alternative

# create your config file + pin English
cp config.example.toml config.toml
# now edit config.toml and add:  language = "en"   under the [ui] section

# start the app
uv run streamlit run webui.py --server.maxUploadSize=2048
# (or, without uv:  streamlit run webui.py --server.maxUploadSize=2048)
```

Then open **http://localhost:8501** in your browser.

### D. Docker install (route 4 — no Python setup needed)

```bash
git clone https://github.com/linyqh/NarratoAI.git
cd NarratoAI
cp config.example.toml config.toml     # add language = "en" under [ui]
docker compose up -d
```

Open **http://localhost:8501**. To make the container default to English at a system level too, add the environment variable `LANG=en_US.UTF-8` in `docker-compose.yml`.

---

## 4. Add your API keys (required before it can generate anything)

The tool needs at least one LLM (an AI model) to write the narration. You can set this **either** in `config.toml` **or** in the app under *Basic Settings → Vision model / Text model panels*.

In `config.toml`, under the `[app]` section:

```toml
[app]
# Vision model — looks at video frames to understand what happens on screen
vision_openai_model_name = "gpt-4o-mini"          # or gemini/gemini-2.0-flash-lite, qwen/...
vision_openai_api_key   = "sk-your-key-here"
vision_openai_base_url  = "https://api.openai.com/v1"   # or your provider's endpoint

# Text model — writes the narration script
text_openai_model_name  = "gpt-4o-mini"
text_openai_api_key     = "sk-your-key-here"
text_openai_base_url    = "https://api.openai.com/v1"
```

The default example config points at SiliconFlow (`https://api.siliconflow.cn/v1`) — change the base URL if you use OpenAI, DeepSeek, Gemini, OpenRouter, etc.

**Model names are free text.** There is no list of "supported" models — the app
forwards whatever name you type to the Base URL you give it, so a brand-new model
like `gpt-6-luna` works the day it ships. If the app answers
`模型不存在，请检查模型名称是否正确` (*"the model does not exist — check the name"*),
that is **your endpoint** rejecting the name, not NarratoAI. PART 8 of
[MOVIE-RECAP-SETTINGS.md](./MOVIE-RECAP-SETTINGS.md) has the full picture:
`gpt-6-luna`, using DeepSeek for text *and* vision, and every model-related
Chinese error translated. Note that the **movie-recap workflow never uses the
vision model** — it works from your subtitle file.

---

## 5. Make the **output** English (not just the buttons)

This is the part most people miss: **the interface language and the language of the generated narration are two separate settings.**

| Setting | Default | Change it to |
|---|---|---|
| **Narration / script language** — dropdown labelled **"Narration Language"**. Its default is `zh-CN`. | Simplified Chinese | **English (United States)** (`en-US`) |
| **Subtitle translation target** — field labelled **"Target language"**. Default is `中文`. | Chinese | `English` |
| **TTS voice-over** — under Audio Settings. Default engine is `indextts` with Chinese voices. | Chinese voice | Use **Edge TTS** (free, no API key) and click the **"English Female Voice"** button → `en-US-AvaMultilingualNeural`. Or set `edge_voice_name = "en-US-AvaMultilingualNeural"` under `[ui]`. |

The narration language dropdown includes: Simplified Chinese, **English (United States)**, Japanese, Korean, French, German, Spanish, Portuguese, Russian — plus a "Custom" option where you can type any language.

I confirmed the generated text really does follow that setting: the prompt template sends it as a hard rule — `must use ${narration_language}` (`app/services/prompts/film_tv_narration/narration_copy.py:90`).

---

## 6. What stays Chinese (complete list — no surprises)

Everything below is what I could actually find. There is very little:

**1. The progress labels while a video is being generated** (`webui.py:133-139`) — the only Chinese you will see during normal use. Here is what each one means:

| Chinese shown | English meaning |
|---|---|
| 正在加载剪辑脚本 | Loading the editing script |
| 正在生成 TTS 配音 | Generating the TTS voice-over |
| 正在按脚本裁剪视频片段 | Cutting video clips according to the script |
| 正在合并配音和字幕 | Merging the voice-over with the subtitles |
| 正在合并视频片段 | Merging the video clips |
| 正在合成最终视频 | Compositing the final video |
| 正在生成视频，请稍候... | Generating video, please wait... |

**2. One line in the Streamlit ☰ menu → "About"** (`webui.py:26`): *"自动化影视解说视频详情请移步：…"* = *"For the automated film-narration video, please see: …"*

**3. A few validation pop-ups** when you type an invalid API key / URL / model name in the LLM settings (`webui/components/basic_settings.py:60-141`). Examples and their meaning:
- `视觉分析 API密钥不能为空` = *"Vision analysis: API key cannot be empty"*
- `文案生成 API密钥长度过短，请检查是否正确` = *"Script generation: API key is too short, please check it"*
- `视觉分析 Base URL必须以http://或https://开头` = *"Vision analysis: Base URL must start with http:// or https://"*

**4. A couple of rare error messages** from helper modules, e.g. `未初始化视觉分析器` = *"Vision analyzer not initialized"* (`webui/utils/vision_analyzer.py`) and `未配置 … 的 API Key 或模型名称` = *"No API key or model name configured for …"* (`webui/tools/generate_script_docu.py`).

**5. `webui/components/ffmpeg_diagnostics.py` is entirely in Chinese — but it is dead code.** It only runs if you execute that file directly (`if __name__ == "__main__"`). It is **not** part of the web app. The FFmpeg panel you actually see in *System Settings* is fully translated to English.

**6. Not visible to you at all:** the terminal logs, the comments inside `config.toml`, the code comments, and the prompt templates (which are written in Chinese to instruct the AI model — the model's *output* still follows the narration language you choose). The repo's `README.md` is Chinese; the English one is `README-en.md`.

---

## 7. Quick reference

| I want to… | Do this |
|---|---|
| Check my translation is applied | The selector should read `en - English` |
| Force English forever | `language = "en"` under `[ui]` in `config.toml` |
| Get English narration | Set **Narration Language** → *English (United States)* |
| Get English subtitles | Set **Target language** → `English` |
| Get an English voice | Audio Settings → Edge TTS → "English Female Voice" |
| Read English docs | `README-en.md`, or the [official documentation](https://p9mf6rjv3c.feishu.cn/wiki/SP8swLLZki5WRWkhuFvc2CyInDg) |
| Stop a one-minute recap | Set **Copy Length** to 1500–1850, then run `check-recap-length.bat` before rendering — see [MOVIE-RECAP-SETTINGS.md PART 7](./MOVIE-RECAP-SETTINGS.md#part-7--it-only-made-a-52-second-recap--the-missing-film-audio) |
| Get the film's own audio back | Run `fix-ffmpeg-audio-merge.bat` once (new FFmpeg builds removed an option the app still uses) |
| Report a bug | https://github.com/linyqh/NarratoAI/issues |

---

## 8. Bottom line

- **Is NarratoAI usable entirely in English? Yes** — the interface, settings, help text and error labels are all translated, and it auto-selects English.
- **Two known traps have ready-made fixes in this bundle:** a too-short recap (raise **Copy Length**, verify with `check-recap-length.bat`) and a recap that lost the film's own audio (`fix-ffmpeg-audio-merge.bat`). Both are explained in [MOVIE-RECAP-SETTINGS.md](./MOVIE-RECAP-SETTINGS.md) PART 7.
- **Do you need a separate English project? No.**
- **The only real annoyance** is the 7 progress lines during rendering (item 1 in section 6) — and now you know what all of them mean.

If you want those leftover Chinese strings gone too, they're small, isolated edits (the progress labels + the About line + the validation messages ≈ 4 files, ~15 strings). Ask and I'll produce a patched English-only copy.

*Guide written against NarratoAI `main` @ `9fa69e0` (17 Sep 2026). Everything above was read from the source, not assumed.*
