"""Patch NarratoAI so it works with models that reject `max_tokens`.

Two different failures are fixed:

1. Newer OpenAI models (o-series, gpt-5*) refuse the parameter outright:
       400 Unsupported parameter: 'max_tokens' is not supported with this model.
       Use 'max_completion_tokens' instead.
   -> the request is retried with `max_completion_tokens`.

2. Older models cap the output size, so NarratoAI's default of 65536 is too big:
       400 max_tokens is too large: 65536. This model supports at most
       16384 completion tokens, whereas you provided 65536.
   -> the request is retried without `max_tokens` at all.

It also fixes the "Test Connection" button, which hardcodes max_tokens=20 (text)
and max_tokens=50 (vision) and therefore reports a false failure for models in
group 1. For those probes the parameter is simply dropped - the reply is a short
"connection succeeded" string anyway.

Edited files:
    app/services/llm/openai_compatible_provider.py   (generation path)
    webui/components/basic_settings.py               (Test Connection button)

Safety:
  * a .bak backup is written the first time
  * running it twice is harmless (it detects its own marker)
  * every patched file is compiled afterwards; on any error the backup is restored
  * if an anchor no longer matches (upstream changed) it stops without writing
"""

from __future__ import annotations

import os
import shutil
import sys

MARKER = "_adapt_max_tokens"

PROVIDER = os.path.join("app", "services", "llm", "openai_compatible_provider.py")
WEBUI = os.path.join("webui", "components", "basic_settings.py")
BACKUP_SUFFIX = ".max-tokens-fix.bak"

# ----------------------------------------------------------------- providers

HELPERS = '''

def _is_max_tokens_param_error(message: str) -> bool:
    """True when the API rejected max_tokens for this particular model."""
    text = (message or "").lower()
    if "max_tokens" not in text:
        return False
    return any(
        hint in text
        for hint in ("max_completion_tokens", "too large", "unsupported_parameter",
                     "unsupported parameter")
    )


def _adapt_max_tokens(completion_kwargs: dict, message: str) -> bool:
    """Make the request acceptable to the model. Returns True when changed.

    * model wants max_completion_tokens -> rename the parameter
    * model thinks the value is too big  -> drop the parameter entirely
    """
    if "max_tokens" not in completion_kwargs:
        return False
    text = (message or "").lower()
    if "max_completion_tokens" in text:
        completion_kwargs["max_completion_tokens"] = completion_kwargs.pop("max_tokens")
        return True
    if "too large" in text or "unsupported_parameter" in text or "unsupported parameter" in text:
        completion_kwargs.pop("max_tokens")
        return True
    return False

'''

HELPER_ANCHOR = '''def _is_content_filter_error(message: str) -> bool:
    lowered = (message or "").lower()
    return "content_filter" in lowered or "safety" in lowered
'''

VISION_ANCHOR = """        except OpenAIBadRequestError as exc:
            error_msg = str(exc)
            if _is_content_filter_error(error_msg):
                raise ContentFilterError(f"内容被安全过滤器阻止: {error_msg}")
            raise APICallError(f"请求错误: {error_msg}")"""

VISION_PATCH = """        except OpenAIBadRequestError as exc:
            error_msg = str(exc)
            if _is_max_tokens_param_error(error_msg) and _adapt_max_tokens(completion_options, error_msg):
                logger.warning("模型不接受当前 max_tokens，调整参数后重试")
                retry_response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    **completion_options,
                )
                if retry_response.choices and retry_response.choices[0].message and retry_response.choices[0].message.content:
                    return retry_response.choices[0].message.content
            if _is_content_filter_error(error_msg):
                raise ContentFilterError(f"内容被安全过滤器阻止: {error_msg}")
            raise APICallError(f"请求错误: {error_msg}")"""

TEXT_ANCHOR = """            # 某些网关不支持 response_format，回退到提示词约束模式"""

TEXT_PATCH = """            if _is_max_tokens_param_error(error_msg) and _adapt_max_tokens(completion_kwargs, error_msg):
                logger.warning("模型不接受当前 max_tokens，调整参数后重试")
                retry_response = await client.chat.completions.create(**completion_kwargs)
                if retry_response.choices and retry_response.choices[0].message and retry_response.choices[0].message.content:
                    return retry_response.choices[0].message.content

            # 某些网关不支持 response_format，回退到提示词约束模式"""

STREAM_ANCHOR = """            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

STREAM_PATCH = """            if _is_max_tokens_param_error(error_msg) and _adapt_max_tokens(completion_kwargs, error_msg):
                logger.warning("模型不接受当前 max_tokens，调整参数后重试")
                return await collect_stream()

            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

# --------------------------------------------------------------------- webui

# The Test Connection probes always send a hardcoded max_tokens, which makes
# models in group 1 report a false failure. Dropping it is safe: these are
# connectivity checks with a one-word answer.
WEBUI_EDITS = (
    (
        "            temperature=0.1,\n            max_tokens=20,\n",
        "            temperature=0.1,\n",
        "text Test Connection probe",
    ),
    (
        "            temperature=0.1,\n            max_tokens=50,\n",
        "            temperature=0.1,\n",
        "vision Test Connection probe",
    ),
)


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    sys.exit(1)


def display(path: str) -> str:
    return os.path.relpath(path, os.path.dirname(os.path.abspath(__file__)))


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def backup(path: str) -> None:
    target = path + BACKUP_SUFFIX
    if not os.path.exists(target):
        shutil.copy2(path, target)
        print(f"[OK] Backup written: {display(target)}")


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def verify(path: str, original_path: str, label: str) -> None:
    try:
        compile(read(path), path, "exec")
    except SyntaxError as exc:
        shutil.copy2(original_path, path)
        fail(f"{label} did not compile; the original was restored.\n        {exc}")


def patch_provider(root: str) -> bool:
    path = os.path.join(root, PROVIDER)
    if not os.path.isfile(path):
        fail(f"could not find {PROVIDER}\n        Run this script from the NarratoAI folder.")
    text = read(path)
    if MARKER in text:
        print(f"[SKIP] {PROVIDER} is already patched")
        return False

    eol = "\r\n" if "\r\n" in text else "\n"

    def insert(anchor: str, addition: str, label: str) -> None:
        nonlocal text
        count = text.count(anchor)
        if count != 1:
            fail(
                f"anchor for {label} matched {count} times (expected 1).\n"
                "        The upstream file changed; nothing was written."
            )
        text = text.replace(anchor, addition.replace("\n", eol), 1)

    insert(HELPER_ANCHOR, HELPER_ANCHOR + HELPERS.replace("\n", eol), "helpers")
    insert(VISION_ANCHOR, VISION_PATCH, "vision handler")
    insert(TEXT_ANCHOR, TEXT_PATCH, "text handler")
    insert(STREAM_ANCHOR, STREAM_PATCH, "stream handler")

    backup(path)
    write(path, text)
    verify(path, path + BACKUP_SUFFIX, PROVIDER)
    print(f"[OK] Patched {PROVIDER}")
    return True


def patch_webui(root: str) -> bool:
    path = os.path.join(root, WEBUI)
    if not os.path.isfile(path):
        print(f"[WARN] {WEBUI} not found - skipping the Test Connection fix")
        return False
    text = read(path)
    changed = False
    for old, new, label in WEBUI_EDITS:
        if old not in text:
            # already removed on a previous run, or upstream changed
            continue
        if text.count(old) != 1:
            fail(f"anchor for {label} matched {text.count(old)} times (expected 1).")
        text = text.replace(old, new, 1)
        changed = True
        print(f"[OK] Fixed {label}")

    if not changed:
        print(f"[SKIP] {WEBUI} needs no change")
        return False

    backup(path)
    write(path, text)
    verify(path, path + BACKUP_SUFFIX, WEBUI)
    return True


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    print("NarratoAI max_tokens compatibility fix")
    print("-" * 50)

    changed_provider = patch_provider(root)
    changed_webui = patch_webui(root)

    if not changed_provider and not changed_webui:
        print("\n[OK] Nothing to do - everything is already fixed.")
        return 0

    print()
    print("[DONE] Restart NarratoAI for the change to take effect.")
    print("       Models that need max_completion_tokens now work automatically,")
    print("       and the Test Connection button no longer reports a false error.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
