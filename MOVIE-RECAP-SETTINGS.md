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
| **Copy Length** | **1850** words | ⚠️ Default is only 500 — that is a ~4-minute video. See the math below and PART 7 |
| **Narration Language** | **English (United States)** | Otherwise the script is written in Chinese |

**Copy Length math:** English narration runs roughly **150 words per minute**. This table is *speaking time only* — the film's own audio adds to it, so the final video is a bit longer (PART 7 has the full table):

| You want this much narration | Set Copy Length to |
|---|---|
| 3.5 minutes | 500 (the default — far too short for a recap) |
| 5 minutes | ~750 |
| 10 minutes | ~1500 |
| **15 minutes** | **~2300** |
| 20 minutes | ~3000 |

Maximum allowed is 5000.

For the 15:31 Movie Recaps reference: **Copy Length 1500 + Original Footage Ratio 30%**, or **Copy Length 1850 + Original Footage Ratio 20%** (the value set above).

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
2. **Left column:** choose **Film/TV Narration**, pick your video file, fill in the title and type, set **Original Footage Ratio = 20**, **Copy Length = 1850**, **Narration Language = English (United States)**
3. Click **Generate Narration Copy** and wait. The AI analyses frames + online plot info and writes the script
4. Read through the script — fix any names or facts it got wrong. This is the cheapest place to fix mistakes
5. **Middle column:** Edge TTS + your chosen English voice
6. **Right column:** Landscape + 1080p
7. Click **"Generate Editing Script"** (the button beside *Generate Narration Copy*) and wait
8. Click **"Edit Video Script"** -> **"Save Script"** in the popup - this creates the real script file
9. Click **Generate Video** at the bottom and wait. Output lands in the `storage` folder

---

## PART 4 — 400 errors from generation parameters

If you see:

```
Error code: 400 ... Unsupported parameter: 'max_tokens' is not supported with this model.
Use 'max_completion_tokens' instead.
```

**This is not your mistake — it is a limitation in NarratoAI's code.** I traced both causes:

- `app/services/llm/openai_compatible_provider.py` always sends `max_tokens`, taken from `text_openai_max_tokens` / `vision_openai_max_tokens` — default **65536**.
- Its error handler only has a fallback for `response_format`. There is **none** for `max_tokens`.

### The three failures, and which parameter causes each

| Error message | Cause | Which model |
|---|---|---|
| `Unrecognized request argument supplied: reasoning_effort` | NarratoAI adds `reasoning_effort` whenever **Thinking Level** is `low` / `medium` / `high` | Any **non-reasoning** model: `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, Gemini, Qwen, DeepSeek |
| `Unsupported parameter: 'max_tokens' ... Use 'max_completion_tokens'` | The model dropped `max_tokens` entirely | o-series (`o1`, `o3`, `o4-mini`), `gpt-5*` |
| `max_tokens is too large: 65536` | NarratoAI's default 65536 exceeds the model's output cap | `gpt-4o` (cap 16,384), older snapshots (4,096) |

**Fastest fix for all three — set these in both model panels:**

| Setting | Value | Why |
|---|---|---|
| **Thinking Level** | **`auto`** or **`off`** | Only `low`/`medium`/`high` send `reasoning_effort`. `auto` and `off` send nothing — verified in the source |
| **Max Output Tokens** | **`0`** | `max_tokens` is only sent when the value is greater than 0 |
| Sampling Temperature | `1.0` | Some models reject a custom temperature |
| Top P | `1.0` | Some models reject `top_p` |

With those four values, **every** model above works — no patching needed.

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

- renames `max_tokens` to `max_completion_tokens` when the model demands it
- drops `max_tokens` when the model says the value is too large
- drops `reasoning_effort` when the model does not recognise it
- drops `top_p` / `temperature` when a model refuses those
- removes the hardcoded probe so the Test button works for every model

Put `fix-max-tokens.bat` and `fix_max_completion_tokens.py` next to `webui.py`, double-click the `.bat`, then restart with `start.bat`.

Tested against all four real error messages: the gpt-5 one → renamed to `max_completion_tokens` (value kept); the "too large" one → parameter dropped; `reasoning_effort` → removed from the request; `top_p` → dropped. Unrelated 400s are left untouched, so it cannot misfire. It also upgrades cleanly over the earlier version of the patch. It backs up first, compiles both files afterwards, restores the backups on any failure, and refuses to write if an anchor moved.

### ✅ Or simply use models that behave

`gpt-4o` / `gpt-4o-mini` work with **Max Output Tokens = 0**. Gemini, Qwen and DeepSeek models also accept `max_tokens` normally — just keep the value at 0 or a modest number like 4096 and they are all happy.

### FunASR / `[WinError 10061] 127.0.0.1:7860` — safe to ignore

If your log also shows a connection error to **port 7860**, that is only the optional local **FunASR-Pack** service used by the *"transcribe subtitles"* button. You already have a subtitle file, so you never need it. Just do not click that button — it has nothing to do with script generation. To use it you would have to install and start FunASR-Pack separately.

---

## PART 5 — If something looks wrong

| Symptom | Fix |
|---|---|
| Narration comes out in Chinese | **Narration Language** is still `zh-CN`. Set it to English (United States) |
| Only a 3-minute video instead of 15 | **Copy Length** is still 500. Raise it to ~1850 and re-read PART 7 |
| Video is vertical | **Video Ratio** is still Portrait. Set it to Landscape |
| "API key cannot be empty" / connection test fails | Key copied with a trailing space, or the base URL does not match the provider, or you put a **text-only** model in the vision panel |
| `Unsupported parameter: 'max_tokens'` — or `max_tokens is too large` | See **Part 4** above — set **Max Output Tokens to 0** in both panels, then run `fix-max-tokens.bat` |
| `Unrecognized request argument supplied: reasoning_effort` | **Thinking Level** is not `auto`/`off` on a non-reasoning model — see **Part 4**. Set Thinking Level = `auto` in both panels |
| `max_tokens is too large` | Set **Max Output Tokens = 0** in both panels — see **Part 4** |
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

---

## PART 7 — "It only made a 52-second recap" + the missing film audio

Two separate things went wrong in that render. Both are fixed below, and both
are things you can see **before** spending an hour rendering next time.

### 7A — Why the video was only 52 seconds

The render itself was fine. **The length of a recap is decided by the editing
script, not by the renderer.** Two facts from your log:

- the script contained only **6 items**
- those 6 items came to **52.867 seconds**

Here is the arithmetic the app uses for every item:

| Item type | How long the clip is |
|---|---|
| **OST = 0** (narration) | exactly as long as the **spoken voice-over** of that item |
| **OST = 1** (film audio) | exactly the **timestamp range** you see in the script |

So a script with six short items *must* produce a ~1-minute video, no matter
what encoder, quality or ratio you pick. The renderer obeyed the script.

Why the script was so small:

1. **Copy Length was left at the default 500.** Your narration copy came out at
   roughly 550 words — about **3.5 minutes of speech**. That is the default, not
   your fault: nothing warns you.
2. **The matching step is allowed to compress.** The prompt used for
   "Generate Editing Script" explicitly permits the model to merge narration
   into fewer bridges (so that the film's own audio can breathe). Given a short
   copy it collapsed everything into 6 items.

> **The rule to remember: what the narrator actually says is how long the video
> is.** More narration copy = longer recap. Nothing else moves the needle.

### 7B — The settings that give a ~15-minute recap

Set **Copy Length** and **Original Footage Ratio** together. Total length is
approximately `narration minutes ÷ (1 − ratio)`:

| Copy Length (words) | Narration alone | @ 20% film audio | @ 30% | @ 50% |
|---|---|---|---|---|
| 500 (default) | 3:20 | 4:10 | 4:45 | 6:40 |
| 1000 | 6:40 | 8:20 | 9:30 | 13:20 |
| 1500 | 10:00 | 12:30 | 14:15 | 20:00 |
| 1850 | 12:20 | **15:25** | 17:35 | 24:40 |
| 2300 | 15:20 | 19:10 | 21:55 | 30:40 |

(150 words per minute, the speed of the Edge TTS voices at rate 1.0.)

**For the 15:31 Movie Recaps reference, use either:**

- **Copy Length 1500 + Original Footage Ratio 30%** → about 14–15 minutes, or
- **Copy Length 1850 + Original Footage Ratio 20%** → about 15–15½ minutes (this
  is the PART 2 profile)

Then:

1. Click **Generate Narration Copy**.
2. **Count the words.** The box should hold roughly the number you asked for
   (1 word ≈ 6 characters with the spaces). If it is a few hundred words, stop —
   the copy is too short and the video will be too short. Edit the box or
   generate again.
3. Click **Generate Editing Script**, then **Save Script**.
4. Run **`check-recap-length.bat`** (next section) *before* rendering.

### 7C — `check-recap-length.bat` — never render a 52-second video again

New tool in this bundle. Double-click it **after Save Script** and **before
Generate Video**:

```
   NarratoAI recap length check
   --------------------------------------------------
   Script      : resource\scripts\2026-1003-150000.json
   Items       : 150  (113 narration / 37 original sound)
   Narration   : 3204 words  =  about 21:22 at 150 wpm
   Film audio  : 3:05
   Original footage ratio: 13%

   ESTIMATED LENGTH : 24:27   (target 15:00)
   --------------------------------------------------
   [LONG] This will run noticeably longer than your target.
```

It reads the newest saved script (or one you name with
`check-recap-length.bat --script resource\scripts\FILE.json`) and prints
`[TOO SHORT]`, `[A BIT SHORT]`, `[OK]` or `[LONG]`. `[TOO SHORT]` means: do not
render, raise **Copy Length**, regenerate. It also accepts `--target 20` and
`--wpm 145` if you want other numbers.

**Rule of thumb:** a 15-minute recap needs roughly **100–200 items** in the
script. Six items means six seconds of nothing happening.

You can also check by eye, without any tool: the **Video Script** section in the
app shows a row count. A recap-length script has well over a hundred rows.

### 7D — The film's own audio was missing

Symptom: the finished video had your narration and subtitles, but none of the
film's dialogue, music or sound effects.

**Cause.** `update-windows.bat` downloads FFmpeg from the BtbN "master" build.
FFmpeg **deprecated the option `-filter_complex_script` in January 2024** and
current builds no longer accept it. NarratoAI uses that option when it mixes the
film's audio into the merged video, and when ffmpeg rejects it the app **silently
falls back to an audio-less merge** — it keeps going, so you only notice at the
end.

The three log lines that prove it (in your log's language, with the English
meaning):

| Chinese in the log | English meaning |
|---|---|
| `Unrecognized option 'filter_complex_script'` | (already English) your ffmpeg removed this option |
| `尝试备用合并方法 - 无音频合并` | "trying the backup merge method — merging without audio" |
| `视频没有音轨，无法提取原声` | "the video has no audio track, the original sound cannot be extracted" |

**Fix — `fix-ffmpeg-audio-merge.bat`.** Double-click it (close the app first, or
at least restart it afterwards). It changes the single line in
`app/services/merger_video.py` so the filter graph is passed inline with
`-filter_complex`, which works on **every** ffmpeg build, old and new. The audio
mix itself is unchanged, so the result sounds exactly as intended.

- it writes a backup `merger_video.py.ffmpeg-filter.bak` before touching anything
- running it twice is harmless ("already patched")
- if the file does not compile afterwards it restores the backup automatically
- if the app's code has changed too much it stops and tells you, without writing

**You do not have to run it by hand.** `update-windows.bat` now applies this
patch automatically at step 4b, so a fresh install is fixed too.

After the fix, render again. The log should show the audio mix and the final
merge finishing, and it should **not** contain the two Chinese warnings above.
Then check the finished file has audio:

```
tools\ffmpeg\bin\ffprobe.exe -show_streams "your_output.mp4" | findstr codec_type
```

You want to see two lines: `codec_type=video` **and** `codec_type=audio`.

### 7E — Checklist for the next render

- [ ] **Copy Length** raised to 1500–1850 (not 500)
- [ ] **Original Footage Ratio** 20–30%
- [ ] **Narration Language** = English (United States)
- [ ] Narration copy **word count checked** (≈ the number you set)
- [ ] Editing script generated, **Save Script** clicked
- [ ] `check-recap-length.bat` says `[OK]` (or `[A BIT SHORT]` you accept)
- [ ] `fix-ffmpeg-audio-merge.bat` applied once (or `update-windows.bat` re-run)
- [ ] Render, then confirm the output has **both** a video and an audio stream

---

## PART 8 — Choosing models: `gpt-6-luna`, DeepSeek, and "the model does not exist"

### 8A — How NarratoAI picks a model (there is no dropdown)

In **Basic Settings** there are three model fields, each with its **own API key and
own Base URL**:

| Field (English label in the app) | Used for | Used by a movie recap? |
|---|---|---|
| **Vision Model Name** | looks at video frames | **No** — the recap workflow works from your subtitle file. Only the Documentary mode uses it |
| **High Reasoning Model Name** | plot analysis, narration copy, editing script | **Yes — this is the one that matters** |
| **High Efficiency Model Name** | subtitle translation / calibration. If left empty it falls back to the reasoning model | Only if you use those features |

The provider field is **locked to "OpenAI compatible"** — it is a label, not a
choice. That is good news: *any* service that speaks the OpenAI API works, you
just paste its **Base URL + API key + model name**. Model names are **free text**;
NarratoAI does not keep a list of "known" models, it forwards whatever you type to
the endpoint you configured.

### 8B — The Chinese errors, translated

Because model choice is decided by your endpoint, these are the messages you get
back. The second one is the "it doesn't recognise the model" error:

| Chinese message | English meaning |
|---|---|
| `模型不存在，请检查模型名称是否正确` | **"The model does not exist — check that the model name is correct."** This is your *endpoint* answering 404/not-found. NarratoAI is passing your name straight through |
| `认证失败，请检查 API Key 是否正确` | "Authentication failed — check that the API key is correct." |
| `超出速率限制，请稍后重试` | "Rate limit exceeded — try again later." |
| `连接失败: ...` | "Connection failed: ..." (the reason is appended) |
| `OpenAI 兼容模型返回空响应` | "The model returned an empty response." Usually a wrong model name or a blocked account |
| `OpenAI 兼容文本/视觉模型连接成功 (name)` | "Connection successful (name)" — this is the *good* one |

If you get the first row, the model name is not served by **the Base URL you set**.
Check what that endpoint actually offers:

```
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"
```

(swap the URL for your provider's; Windows 10/11 already includes `curl.exe`).
If your name is not in that list, the endpoint cannot serve it no matter what you
type in the app — that is a provider/account matter, not a NarratoAI limitation.

### 8C — Can you use `gpt-6-luna`? Yes

`gpt-6-luna` is a real OpenAI model (shipped 2026-09-22, the efficient tier of the
GPT-6 family). What matters for NarratoAI:

| Property | Value | Why it matters here |
|---|---|---|
| Inputs | **text + image** | It can serve **all three** fields — including the vision panel |
| Context | 1,050,000 tokens | Your subtitles are ~61 cues, so no concern |
| Max output | 128,000 tokens | A 1500-word narration copy is ~2000 tokens — plenty |
| Reasoning | yes, effort levels `none → max` | It **accepts** `reasoning_effort`, unlike gpt-4o |
| API | Chat Completions | Exactly what NarratoAI uses |

**Settings to use with it:**

- Base URL: `https://api.openai.com/v1`, your OpenAI key
- **Thinking Level: `auto`** (it supports effort control, but `auto` is the
  safest — the app only injects `reasoning_effort` on low/medium/high)
- **Max Output Tokens: `0`** (omit the cap; the app's 65536 default is unnecessary)
- **Temperature 1.0, Top P 1.0** — reasoning models reject custom values

If `fix-max-tokens.bat` (v2) is applied, the parameter differences are handled
automatically anyway: unsupported `max_tokens` forms, `reasoning_effort`,
`temperature` and `top_p` are retried without the offending parameter.

> If you reach OpenAI through a relay or aggregator, and it answers "model does
> not exist", that relay simply does not carry `gpt-6-luna`. Nothing in NarratoAI
> stops you using the name — the relay does.

### 8D — Can you use DeepSeek for both text and visuals? Yes (with one caveat)

DeepSeek changed in 2026: **V4.1 Flash (`deepseek-flash`) accepts image input
natively**, and the API is OpenAI-compatible.

| Panel | Model name to type | Notes |
|---|---|---|
| **High Reasoning Model Name** | `deepseek-v4-pro` | V4 Pro, 1M context, thinking mode |
| **High Efficiency Model Name** | `deepseek-flash` | V4.1 Flash — cheap and fast |
| **Vision Model Name** | `deepseek-flash` | V4.1 Flash has native image input. The older `deepseek-v4-flash-vision-exp` id now routes to the same model |
| **Base URL** (both panels) | `https://api.deepseek.com` | `https://api.deepseek.com/v1` also works |

- API key: from **https://platform.deepseek.com/api_keys**
- Use the **V4 names**. The old `deepseek-chat` / `deepseek-reasoner` ids were
  retired/redirected — using them is what usually produces "model does not exist".
- DeepSeek V4 turns **thinking on by default**. That is fine, but it costs tokens
  and time; if a generation feels slow, set Thinking Level as you prefer.
- **Caveat on the vision side:** DeepSeek's image path is built for cost — images
  are downscaled and billed in a very small token budget (the vision variant
  capped at 384 tokens per image). Film frames are busy; small faces and on-screen
  text may be lost. Test it on a few frames before relying on it.

**But remember 8A:** the recap workflow never calls the vision model. If you only
make movie recaps from subtitles, DeepSeek's text models are all you need — the
Vision panel can be pointed at the same DeepSeek model purely to keep it valid for
the other modes.

### 8E — Which combination should you pick?

| | Cheapest | Balanced | Best quality |
|---|---|---|---|
| High Reasoning | `deepseek-v4-pro` | `gpt-6-luna` | `gpt-6-luna` (high effort) |
| High Efficiency | `deepseek-flash` | `deepseek-flash` | `gpt-6-luna` |
| Vision | `deepseek-flash` | `gpt-6-luna` | `gpt-6-luna` or Gemini |

Two practical warnings:

1. **Mixing providers is normal** — each panel has its own key and Base URL, so
   text on DeepSeek and vision on OpenAI is perfectly valid.
2. **Long inputs cost money on the reasoning model.** The recap pipeline sends the
   whole subtitle file + narration copy to the High Reasoning model. Very large
   films with 1M-token contexts are exactly where the cheap tier earns its place.
