"""Patch NarratoAI so it works with models that reject `max_tokens`.

Some newer OpenAI models (the o-series and gpt-5) refuse the `max_tokens`
parameter and demand `max_completion_tokens` instead:

    400 Unsupported parameter: 'max_tokens' is not supported with this model.
    Use 'max_completion_tokens' instead.

NarratoAI always sends `max_tokens`, and only has a fallback for
`response_format` - so those models fail.

This script adds an automatic retry: when the API complains about
`max_tokens`, the request is repeated with `max_completion_tokens`.

It edits app/services/llm/openai_compatible_provider.py next to this file.

  * a .bak backup is written the first time
  * running it twice is harmless (it detects its own marker)
  * the patched file is compiled afterwards to prove it is still valid Python
  * if the file has changed upstream the anchors will not match and the script
    stops with a clear message instead of corrupting anything
"""

from __future__ import annotations

import os
import shutil
import sys

MARKER = "_is_max_tokens_param_error"
TARGET = os.path.join("app", "services", "llm", "openai_compatible_provider.py")
BACKUP_SUFFIX = ".max-tokens-fix.bak"

HELPERS = '''

def _is_max_tokens_param_error(message: str) -> bool:
    """True when the API rejected max_tokens and asked for max_completion_tokens."""
    text = (message or "").lower()
    return "max_completion_tokens" in text and "max_tokens" in text


def _use_max_completion_tokens(completion_kwargs: dict) -> bool:
    """Rename max_tokens -> max_completion_tokens in place.

    Returns True when something was actually renamed.
    """
    if "max_tokens" not in completion_kwargs:
        return False
    completion_kwargs["max_completion_tokens"] = completion_kwargs.pop("max_tokens")
    return True

'''

# anchor -> inserted text, matched exactly once
VISION_ANCHOR = """        except OpenAIBadRequestError as exc:
            error_msg = str(exc)
            if _is_content_filter_error(error_msg):
                raise ContentFilterError(f"内容被安全过滤器阻止: {error_msg}")
            raise APICallError(f"请求错误: {error_msg}")"""

VISION_PATCH = """        except OpenAIBadRequestError as exc:
            error_msg = str(exc)
            if _is_max_tokens_param_error(error_msg) and _use_max_completion_tokens(completion_options):
                logger.warning("模型不接受 max_tokens，改用 max_completion_tokens 重试")
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

TEXT_PATCH = """            if _is_max_tokens_param_error(error_msg) and _use_max_completion_tokens(completion_kwargs):
                logger.warning("模型不接受 max_tokens，改用 max_completion_tokens 重试")
                retry_response = await client.chat.completions.create(**completion_kwargs)
                if retry_response.choices and retry_response.choices[0].message and retry_response.choices[0].message.content:
                    return retry_response.choices[0].message.content

            # 某些网关不支持 response_format，回退到提示词约束模式"""

STREAM_ANCHOR = """            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

STREAM_PATCH = """            if _is_max_tokens_param_error(error_msg) and _use_max_completion_tokens(completion_kwargs):
                logger.warning("模型不接受 max_tokens，改用 max_completion_tokens 重试")
                return await collect_stream()

            if response_format == "json" and _is_response_format_error(error_msg):
                logger.warning("目标网关不支持流式 response_format，回退为提示词约束 JSON 输出")"""

HELPER_ANCHOR = '''def _is_content_filter_error(message: str) -> bool:
    lowered = (message or "").lower()
    return "content_filter" in lowered or "safety" in lowered
'''


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    sys.exit(1)


def main() -> int:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), TARGET)
    if not os.path.isfile(path):
        fail(
            f"could not find {TARGET}\n"
            "        Put this script next to webui.py (the NarratoAI folder) and run it again."
        )

    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()

    if MARKER in text:
        print("[OK] Already patched - nothing to do.")
        return 0

    eol = "\r\n" if "\r\n" in text else "\n"

    def insert(anchor: str, addition: str, label: str) -> str:
        nonlocal text
        found = text.count(anchor)
        if found != 1:
            fail(
                f"anchor for {label} matched {found} times (expected exactly 1).\n"
                "        The upstream file has changed; no changes were made."
            )
        addition = addition.replace("\n", eol)
        text = text.replace(anchor, addition, 1)
        return text

    text = insert(HELPER_ANCHOR, HELPER_ANCHOR + HELPERS.replace("\n", eol), "helpers")
    text = insert(VISION_ANCHOR, VISION_PATCH, "vision handler")
    text = insert(TEXT_ANCHOR, TEXT_PATCH, "text handler")
    text = insert(STREAM_ANCHOR, STREAM_PATCH, "stream handler")

    backup = path + BACKUP_SUFFIX
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
        print(f"[OK] Backup written: {os.path.basename(backup)}")

    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)

    try:
        compile(text, path, "exec")
    except SyntaxError as exc:
        shutil.copy2(backup, path)
        fail(f"patched file did not compile, original restored.\n        {exc}")

    print("[OK] Patched successfully.")
    print("     max_tokens is now retried as max_completion_tokens automatically.")
    print("     Restart NarratoAI for the change to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
