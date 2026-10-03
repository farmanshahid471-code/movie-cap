# LLM API Key + Settings for Movie-Recap Videos

Everything below was read from the actual NarratoAI source (`main`, commit `9fa69e0`) — labels matches what you see in the English interface exactly.

Your example video is a **"Movie Recaps"** style video: 15:31 long, landscape 16:9, one continuous English narrator over the film's footage, with the film's own dialogue and sound left audible underneath. This guide configures that style.

---

## PART 1 — Where to enter the LLM API key

You need **two** models. Both can come from the same provider and even the same key:

| Panel | Column | What it does | Needs vision? |
|---|---|---|---|
| **Vision Model Settings** | middle column | Watches frames from your video to understand what happens on screen | **Yes** — must be a vision model |
| **Text Model Settings** | right column | Writes the narration script | No |

### Option A — inside the app (easiest)

1. Run `start.bat` and open http://localhost:8501
2. At the top, click the **"Basic Settings"** expander to open it
3. You now see three columns:
   - **Middle column → "Vision Model Settings"** → fill in **Vision Model Name**, **Vision API Key**, **Vision Base URL**
   - **Right column → "Text Model Settings"** → fill in **High-Reasoning Model Name**, **Text API Key**, **Text Base URL**
4. Click the **"Test Connection"** button under each panel — it must say the connection succeeded
5. The app saves to `config.toml` automatically

### Option B — edit `config.toml` directly

Open `config.toml` in Notepad (next to `webui.py`) and edit the `[app]` section:

```toml
[app]
    # ---- Vision model: understands the picture ----
    vision_openai_model_name = "gpt-4o-mini"
    vision_openai_api_key    = "sk-put-your-key-here"
    vision_openai_base_url   = "https://api.openai.com/v1"

    # ---- Text model: writes the narration ----
    text_openai_model_name   = "gpt-4o-mini"
    text_openai_api_key      = "sk-put-your-key-here"
    text_openai_base_url     = "https://api.openai.com/v1"
```

Save the file, then restart with `start.bat`.

### Provider examples

Pick a row, use the same key for both panels. **The base URL must match the provider.**

| Provider | Base URL | Vision model | Text model |
|---|---|---|---|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` or `gpt-4o` | `gpt-4o-mini` or `gpt-4o` |
| **Google Gemini** | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini/gemini-2.0-flash` | `gemini/gemini-2.0-flash` |
| **OpenRouter** (one key, many models) | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` | `openai/gpt-4o-mini` |
| **DeepSeek** | `https://api.deepseek.com/v1` | ⚠️ no vision — pair with another provider for the vision panel | `deepseek/deepseek-chat` |
| **Qwen / DashScope** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-vl-max` | `qwen-plus` |
| **SiliconFlow** (the default in the file) | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-VL-32B-Instruct` | `deepseek-ai/DeepSeek-V3` |

**Rules that matter**

- The **vision** model must be able to see images. DeepSeek's chat models cannot — that is the most common mistake.
- Model names are **case-sensitive**, especially on SiliconFlow and Qwen.
- If you use a Chinese provider's endpoint, model names are usually written as `vendor/model`.
- Only pay for what you use — with a cheap model, a 15-minute recap costs cents.

---

## PART 2 — Full settings profile for the Movie-Recaps style

Open the app and set these. Left-to-right matches the three columns on screen.

### Top: Basic Settings

| Setting | Value | Why |
|---|---|---|
| **Interface Language** (left column) | `en - English` | Already set for you |
| **Vision Model** panel | your vision model + key | Reads the footage |
| **Text Model** panel | your text model + key | Writes the script |

### Left column: Script panel

| Setting | Value | Why |
|---|---|---|
| **Mode** (the dropdown at the top) | **"Film/TV Narration"** | This is the movie-recap mode. ("Short Drama Summary" is for short vertical dramas.) |
| **Video File** | your movie file (mp4/mkv) | The source footage |
| **Film/TV Title** | the real film name, e.g. `The Peasants' Revolt 1381` | Better title = better web-search context = a more accurate story |
| **Film/TV Type** | `History / War` for your example | There are 7 types + Custom. `Drama / Emotion` is the default |
| **Original Footage Ratio** | **20%** (or 30% for more dialogue) | Share of the final runtime where the film's **own audio** plays and the narrator pauses. Movie Recaps keeps the actors' voices at big moments |
| **Copy Length** | **2300** words | ⚠️ Default is only 500 — that is a ~3.5-minute video. See the math below |
| **Narration Language** | **English (United States)** | Otherwise the script is written in Chinese |

**Copy Length math:** English narration runs roughly **150 words per minute**. So:

| You want | Set Copy Length to |
|---|---|
| 5 minutes | ~750 |
| 10 minutes | ~1500 |
| **15:30 (your example)** | **~2300** |
| 20 minutes | ~3000 |

Maximum allowed is 5000. Start with 2300 and adjust.

Then click **"Generate Narration Copy"**. Read the script it produces and edit it in the box if you want — this is what the video will be built around.

### Middle column: Audio panel (the voice)

| Setting | Value | Why |
|---|---|---|
| **Select TTS Engine** | **Edge TTS** | Free, no API key, no downloads. (The default, IndexTTS, needs a multi-GB local model — skip it.) |
| **Voice Selection** | a male US voice for the Movie Recaps feel: **`en-US-AndrewMultilingual-Male`** or **`en-US-BrianMultilingual-Male`** (also `en-US-Guy-Male`) | Movie Recaps uses a calm male narrator. Note the dropdown hides the word "Neural", so the entry is shown as `en-US-AndrewMultilingual-Male` even though the real voice id is `en-US-AndrewMultilingualNeural-Male` |
| **Voice Volume** | 1.0 | Default is fine |
| **Voice Rate** | 1.0 (try 1.05–1.1 if you want a faster, punchier read) | Default 1.0 |
| **Background Music Source** | **"No Background Music"** | Movie Recaps has **no** music — just narration over the film's own sound. Choose "Random Background Music" only if you want a bed under it |
| **Background music volume** | 0.3 if you do use music | Default |

You can click **Preview Voice Synthesis** to hear the voice before committing.

### Right column: Video panel

| Setting | Value | Why |
|---|---|---|
| **Video Ratio** | **`Landscape 16:9 (Xigua Video)`** | This is plain 16:9 — ignore the "Xigua Video" wording, it's just the label. (The other choice is `Portrait 9:16 (TikTok Video)`, which is the **default** — so **you must change it**) |
| **Video Quality** | **Full HD (1080p)** | Default, matches YouTube |
| **Original Volume** | 1.2 (default) or 1.0 | Volume of the film's own audio. Lower it slightly if the dialogue drowns out the narrator |

### Right column: Subtitle panel

| Setting | Value | Why |
|---|---|---|
| **Enable Subtitles** | **off** for an exact Movie Recaps look — they burn in no subtitles | If you want subtitles for engagement, turn it on |
| **Font Name** (if enabled) | leave the default `SourceHanSansCN-Regular.otf` | It contains full Latin letters too, so English text renders correctly |
| **Font Size** | 60 (default) | Range is 20–160 |
| **Text foreground colour** | `#FFFFFF` white | Default |
| **Border/stroke colour** | `#000000` black | Default — needed for readability over video |

Leave the **Subtitle Mask** settings alone unless the film has burned-in subtitles you want to hide.

### Right column: System panel

Leave everything at the default. This is where FFmpeg is reported — it should show FFmpeg as available, because the installer set it up.

### Bottom of the page

| Button | What it does |
|---|---|
| **Generate Video** | Builds the final video. Takes a while — the progress lines are the Chinese ones listed in the main guide. Output goes to the `storage` folder next to `webui.py` |
| **Export to Jianying Draft** | Only useful if you use CapCut/Jianying — ignore it |

---

## PART 3 — Step-by-step workflow

1. Enter your API keys in **Basic Settings** → click **Test Connection** on both panels
2. **Left column:** choose **Film/TV Narration**, pick your video file, fill in the title and type, set **Original Footage Ratio = 20**, **Copy Length = 2300**, **Narration Language = English (United States)**
3. Click **Generate Narration Copy** and wait. The AI analyses frames + online plot info and writes the script
4. Read through the script — fix any names or facts it got wrong. This is the cheapest place to fix mistakes
5. **Middle column:** Edge TTS + your chosen English voice
6. **Right column:** Landscape + 1080p
7. Click **"Generate Editing Script"** (the button beside *Generate Narration Copy*) and wait
8. Click **"Edit Video Script"** -> **"Save Script"** in the popup - this creates the real script file
9. Click **Generate Video** at the bottom and wait. Output lands in the `storage` folder

---

## PART 4 — Error: "Unsupported parameter: 'max_tokens'"

If you see:

```
Error code: 400 ... Unsupported parameter: 'max_tokens' is not supported with this model.
Use 'max_completion_tokens' instead.
```

**This is not your mistake — it is a limitation in NarratoAI's code.** I traced both causes:

- `app/services/llm/openai_compatible_provider.py` always sends `max_tokens`, taken from `text_openai_max_tokens` / `vision_openai_max_tokens` — default **65536**.
- Its error handler only has a fallback for `response_format`. There is **none** for `max_tokens`.

### ⚠️ Two traps you will hit

**Trap 1 — the Test Connection button is misleading.** The button does not use your settings. It sends a hardcoded probe:

| Probe | What it actually sends |
|---|---|
| Text model test | `temperature=0.1, max_tokens=20` |
| Vision model test | `temperature=0.1, max_tokens=50` |

So your **green tick for `gpt-4o` does not prove generation will work** — see trap 2. And for a gpt-5 model the test stays **red even after you fix the config**, because the probe ignores your "Max Output Tokens" setting entirely.

**Trap 2 — `gpt-4o` will fail later with a different error.** NarratoAI's default 65536 exceeds what most models allow for output. With `gpt-4o` left at 65536, real generation fails with:

```
400 max_tokens is too large: 65536. This model supports at most 16384 completion tokens
```

`gpt-4o` accepts `max_tokens`, but only up to **16,384** (older snapshots: 4,096). The test passed only because it asked for 20.

### ✅ Fix — set Max Output Tokens to 0

The app sends `max_tokens` **only when the value is greater than zero**. Setting 0 removes it from the request, and each model then uses its own default. This fixes **both** traps at once.

In the app: **Basic Settings → Generation Settings → "Max Output Tokens" = 0** — for **both** the Vision and the Text panels.

Or in `config.toml`, then restart:

```toml
[app]
    text_openai_max_tokens = 0
    vision_openai_max_tokens = 0
```

*Verified by executing the real `_build_chat_completion_options` from the source: at 65536 the request is `{'temperature': 1.0, 'top_p': 0.95, 'max_tokens': 65536}`; at 0 it is `{'temperature': 1.0, 'top_p': 0.95}` — no `max_tokens` key at all.*

### ✅ Also: run `fix-max-tokens.bat`

Setting 0 fixes generation, but the **Test Connection button will still show red** for gpt-5 models. `fix-max-tokens.bat` (in the `windows/` folder / bundle root) fixes that too:

- retries a request with `max_completion_tokens` when the model demands it
- drops `max_tokens` when the model says the value is too large
- removes the hardcoded probe so the Test button works for every model

Put `fix-max-tokens.bat` and `fix_max_completion_tokens.py` next to `webui.py`, double-click the `.bat`, then restart with `start.bat`.

Tested against both real error messages: gpt-5-style → renamed to `max_completion_tokens` (value kept); gpt-4o-style → parameter dropped; unrelated errors (e.g. `temperature`) → left untouched, so it cannot misfire. It backs up first, compiles both files afterwards, restores the backups on any failure, and refuses to write if an anchor moved.

### ✅ Or simply use models that behave

`gpt-4o` / `gpt-4o-mini` work with **Max Output Tokens = 0**. Gemini, Qwen and DeepSeek models also accept `max_tokens` normally — just keep the value at 0 or a modest number like 4096 and they are all happy.

### If the next error names `top_p` or `temperature`

Some reasoning models also refuse those. Set **Sampling Temperature = 1.0**, **Top P = 1.0** and **Thinking Level = auto** — `auto` and `off` send no `reasoning_effort` at all, while `low`/`medium`/`high` do. Tell me if you hit it and I will extend the patch.

---

## PART 5 — If something looks wrong

| Symptom | Fix |
|---|---|
| Narration comes out in Chinese | **Narration Language** is still `zh-CN`. Set it to English (United States) |
| Only a 3-minute video instead of 15 | **Copy Length** is still 500. Raise it to ~2300 |
| Video is vertical | **Video Ratio** is still Portrait. Set it to Landscape |
| "API key cannot be empty" / connection test fails | Key copied with a trailing space, or the base URL does not match the provider, or you put a **text-only** model in the vision panel |
| `Unsupported parameter: 'max_tokens'` — or `max_tokens is too large` | See **Part 4** above — set **Max Output Tokens to 0** in both panels, then run `fix-max-tokens.bat` |
| Test Connection red, but the model name is right | The button hardcodes `max_tokens=20`, so gpt-5 models always fail the test — see **Part 4**, trap 1. Add `max_tokens = 0` and run `fix-max-tokens.bat` |
| Voice-over missing / silent video | TTS engine is still IndexTTS without a local model. Switch to **Edge TTS** |
| Script invents plot that is not in the film | Turn on **Tavily search** in Basic Settings (needs a free Tavily key) so it can look up the real plot, and edit the script before generating |
| Subtitles show as boxes/blank squares | Font name does not contain Latin glyphs — switch back to the default `SourceHanSansCN-Regular.otf` |

---

*Source-verified against NarratoAI `main` @ `9fa69e0`. Every label in this document is the exact English string the app renders (`webui/i18n/en.json`).*

## PART 6 — "解说脚本文件不存在！" (script file does not exist)

**Translation:** *"The narration script file does not exist! Please click the [Save Script] button to save the script before generating the video."*

### Why it happens

NarratoAI stores the script location in one variable called `video_clip_json_path`. When you simply **pick a mode** from the dropdown, that variable is set to the *mode name* (`film_summary`) instead of a file path. Because a mode name is a non-empty string, the "script is empty" check passes, the render starts, and then the app tries to open a file literally named `film_summary` — which does not exist. Hence the error.

So: nothing is broken, you just have not saved a script file yet.

### The two clicks you are missing

In **Film/TV Narration** mode the panel has **two** buttons side by side:

| Button | What it does |
|---|---|
| **Generate Narration Copy** | Writes the narration text only. It does **not** create a script file. |
| **Generate Editing Script** | Builds the timestamped script (narration matched to footage) — but still only in memory |

After clicking **Generate Editing Script**, the **"Video Script"** section above shows a row count like *"42 script rows"*. That is only in memory — **you must save it**:

1. Click **"Edit Video Script"** — a large popup opens with a table of the script
2. Click **"Save Script"** inside that popup

That writes the real file to `resource/scripts/<timestamp>.json`, sets the path correctly, and shows *"✅ Script format validated and saved successfully!"*.

**Good sign:** after saving, the mode dropdown switches itself to **"Select/Upload Script"** and your new `.json` appears in the file list. That is expected — it is now pointing at a real file.

Only now does **Generate Video** work.

### Checklist before pressing Generate Video

- [ ] Subtitle file loaded (you have one — make sure it is selected, not just the video)
- [ ] **Generate Narration Copy** → review the text in the box
- [ ] **Generate Editing Script** → wait for "Video script generated successfully"
- [ ] **"Video Script"** section shows a row count **greater than 0**
- [ ] **Edit Video Script → Save Script** → green "validated and saved successfully"
- [ ] Only then: **Generate Video**

### If the row count stays at 0

The script generation failed silently. Open the black console window running NarratoAI and scroll up — the real reason is printed there (usually: subtitle file missing, no API key, or the JSON produced by the model could not be parsed).

### Reusing an existing script

You can skip generation entirely: choose the mode **"Select/Upload Script"** and pick a previously saved `.json` from the list. Handy for making several videos from one script.

---
