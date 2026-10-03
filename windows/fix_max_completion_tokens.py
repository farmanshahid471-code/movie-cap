"""Patch NarratoAI so it works with models that reject certain parameters.

NarratoAI always sends the same generation parameters. Several model families
refuse some of them, which makes generation fail with a 400 error:

1. o-series / gpt-5 refuse `max_tokens`:
       400 Unsupported parameter: 'max_tokens' ... Use 'max_completion_tokens'
   -> retried with `max_completion_tokens`.

2. gpt-4o and friends cap the output size, so the 65536 default is too big:
       400 max_tokens is too large: 65536. This model supports at most 16384
   -> retried without `max_tokens` at all.

3. Any non-reasoning model (gpt-4o, gpt-4.1, Gemini, Qwen...) rejects
   `reasoning_effort`, which NarratoAI adds whenever Thinking Level is set to
   low / medium / high:
       400 Unrecognized request argument supplied: reasoning_effort
   -> retried without `reasoning_effort`.

4. Some models also refuse `top_p` or a custom `temperature`
   -> those parameters are dropped on retry.

It also fixes the "Test Connection" button, which hardcodes max_tokens=20
(text) and max_tokens=50 (vision) and therefore reports a false failure for
models in group 1.

Edited files:
    app/services/llm/openai_compatible_provider.py   (generation path)
    webui/components/basic_settings.py               (Test Connection button)

Safety:
  * a .bak backup is written the first time
  * running it twice is harmless (it detects its own marker)
  * if an older version of this patch is present, it restores the .bak first
    and applies the new one
  * every patched file is compiled afterwards; on any error the backup is restored
  * if an anchor no longer matches (upstream changed) it stops without writing
"""

from __future__ import annotations

import os
import shutil
import sys

VERSION_MARKER = "_adapt_request_params"
OLD_MARKER = "_is_max_tokens_param_error"

PROVIDER = os.path.join("app", "services", "llm", "openai_compatible_provider.py")
WEBUI = os.path.join("webui", "components", "basic_settings.py")
BACKUP_SUFFIX = ".max-tokens-fix.bak"

# ----------------------------------------------------------------- providers

HELPERS = '''

def _adapt_request_params(completion_kwargs: dict, message: str) -> bool:
    """Remove or rename parameters this model refused. True when changed.

    Handles the four failures NarratoAI hits in practice:
      * max_tokens not supported at all      -> rename to max_completion_tokens
      * max_tokens value too large           -> drop it
      * reasoning_effort not recognized      -> drop it
      * top_p / temperature not supported    -> drop them
    """
    text = (message or "").lower()
    if not text:
        return False

    changed = False

    if "max_tokens" in text and "max_tokens" in completion_kwargs:
        if "max_completion_tokens" in text:
            completion_kwargs["max_completion_tokens"] = completion_kwargs.pop("max_tokens")
            changed = True
        elif any(hint in text for hint in ("too large", "unsupported_parameter", "unsupported parameter")):
            completion_kwargs.pop("max_tokens")
            changed = True

    if "reasoning_effort" in text:
        extra_body = completion_kwargs.get("extra_body")
        if isinstance(extra_body, dict) and "reasoning_effort" in extra_body:
            extra_body.pop("reasoning_effort")
            if not extra_body:
                completion_kwargs.pop("extra_body")
            changed = True

    for param in ("top_p", "temperature"):
        if param in text and param in completion_kwargs:
            completion_kwargs.pop(param)
            changed = True

    return changed


def _is_adaptable_param_error(message: str) -> bool:
    """True when the failure is one of the parameter problems above."""
    text = (message or "").lower()
    if "unsupported_parameter" in text or "unrecognized request argument" in text:
        return True
    if "max_tokens" in text and ("too large" in text or "max_completion_tokens" in text):
        return True
    if "reasoning_effort" in text:
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
            if _is_adaptable_param_error(error_msg) and _adapt_request_params(completion_options, error_msg):
                logger.warning("模型不接受当前参数，调整后重试")
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

TEXT_PATCH = """            if _is_adaptable_param_error(error_msg) and _adapt_request_params(completion_kwargs, error_msg):
                logger.warning("模型不接受当前参数，调整后重试")
                retry_response = await client.chat.completions.create(**completion_kwargs)
                if retry_response.choices and retry_response.choices[0].message and retry_response.choices[0].message.content:
                    return retry_response.choices[0].message.content

            # 某些网关不支持 response_format，回退到提示词约束模式"""

STREAM_ANCHOR = """            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

STREAM_PATCH = """            if _is_adaptable_param_error(error_msg) and _adapt_request_params(completion_kwargs, error_msg):
                logger.warning("模型不接受当前参数，调整后重试")
                return await collect_stream()

            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

# --------------------------------------------------------------------- webui

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


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def backup(path: str) -> None:
    target = path + BACKUP_SUFFIX
    if not os.path.exists(target):
        shutil.copy2(path, target)
        print(f"[OK] Backup written: {display(target)}")


def verify(path: str, label: str) -> None:
    try:
        compile(read(path), path, "exec")
    except SyntaxError as exc:
        shutil.copy2(path + BACKUP_SUFFIX, path)
        fail(f"{label} did not compile; the original was restored.\n        {exc}")


def restore_old_patch(path: str, label: str) -> None:
    """An older version of this patch is applied - roll it back first."""
    target = path + BACKUP_SUFFIX
    if not os.path.exists(target):
        fail(
            f"{label} already contains an older version of this patch and no backup\n"
            "        was found next to it, so it cannot be upgraded automatically.\n"
            "        Restore that file from your NarratoAI download, then run this again."
        )
    shutil.copy2(target, path)
    if OLD_MARKER in read(path):
        fail(
            f"the backup next to {label} also contains the old patch, so it cannot be\n"
            "        used to roll back. Replace that file with a fresh copy from your\n"
            "        NarratoAI download, then run this again."
        )
    print(f"[OK] Removed the older patch from {display(path)} (restored the backup)")


def patch_provider(root: str) -> bool:
    path = os.path.join(root, PROVIDER)
    if not os.path.isfile(path):
        fail(f"could not find {PROVIDER}\n        Run this script from the NarratoAI folder.")

    text = read(path)
    if VERSION_MARKER in text:
        print(f"[SKIP] {PROVIDER} is already patched")
        return False
    if OLD_MARKER in text:
        restore_old_patch(path, PROVIDER)
        text = read(path)

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
    verify(path, PROVIDER)
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
            continue  # already removed, or upstream changed
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
    verify(path, WEBUI)
    return True


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    print("NarratoAI parameter compatibility fix")
    print("-" * 50)

    changed_provider = patch_provider(root)
    changed_webui = patch_webui(root)

    if not changed_provider and not changed_webui:
        print("\n[OK] Nothing to do - everything is already fixed.")
        return 0

    print()
    print("[DONE] Restart NarratoAI for the change to take effect.")
    print("       These are now handled automatically:")
    print("         max_tokens            -> max_completion_tokens when required")
    print("         max_tokens too large  -> dropped")
    print("         reasoning_effort      -> dropped when unsupported")
    print("         top_p / temperature   -> dropped when unsupported")
    print("       The Test Connection button also works for every model now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
