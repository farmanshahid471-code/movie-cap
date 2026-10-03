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
7. Click **Generate Video** at the bottom and wait. Output lands in the `storage` folder

---

## PART 4 — If something looks wrong

| Symptom | Fix |
|---|---|
| Narration comes out in Chinese | **Narration Language** is still `zh-CN`. Set it to English (United States) |
| Only a 3-minute video instead of 15 | **Copy Length** is still 500. Raise it to ~2300 |
| Video is vertical | **Video Ratio** is still Portrait. Set it to Landscape |
| "API key cannot be empty" / connection test fails | Key copied with a trailing space, or the base URL does not match the provider, or you put a **text-only** model in the vision panel |
| Voice-over missing / silent video | TTS engine is still IndexTTS without a local model. Switch to **Edge TTS** |
| Script invents plot that is not in the film | Turn on **Tavily search** in Basic Settings (needs a free Tavily key) so it can look up the real plot, and edit the script before generating |
| Subtitles show as boxes/blank squares | Font name does not contain Latin glyphs — switch back to the default `SourceHanSansCN-Regular.otf` |

---

*Source-verified against NarratoAI `main` @ `9fa69e0`. Every label in this document is the exact English string the app renders (`webui/i18n/en.json`).*
