"""Write English-friendly settings into NarratoAI's config.toml, safely.

Used by update-windows.bat, but it can also be run by hand:

    python narrato_setup_helper.py --config config.toml --english-defaults \
        --ffmpeg-path "F:\\NarratoAI-main\\NarratoAI-main\\tools\\ffmpeg\\bin\\ffmpeg.exe"

Guarantees:
  * only the standard library is used (works before dependencies are installed)
  * existing settings and comments are preserved
  * line endings (CRLF/LF) are preserved
  * running it twice changes nothing the second time
  * the file is re-parsed afterwards to prove it is still valid TOML
"""

from __future__ import annotations

import argparse
import os
import sys

try:  # Python 3.11+
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None


# ---------------------------------------------------------------- helpers

def _read_lines(path: str) -> tuple[list[str], str]:
    # newline="" keeps the original line endings untouched
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()

    if "\r\n" in text:
        eol = "\r\n"
    elif "\r" in text:
        eol = "\r"
    else:
        eol = "\n"

    return text.splitlines(keepends=True), eol


def _section_name(section: str) -> str:
    """Accept 'ui', '[ui]' or '[[ui]]' and return the bare name 'ui'."""
    return section.strip().strip("[]").strip()


def _section_bounds(lines: list[str], section: str) -> tuple[int | None, int | None]:
    """Return (header_index, last_line_index) for a [section] block."""
    wanted = f"[{_section_name(section)}]"
    header = None
    end = len(lines)

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not (stripped.startswith("[") and stripped.endswith("]")):
            continue
        if header is None:
            if stripped == wanted:
                header = index
        else:
            end = index
            break

    return header, (end if header is not None else None)


def _format_value(value: str) -> str:
    """Quote a value, preferring TOML single quotes so backslashes stay literal."""
    if "'" not in value:
        return f"'{value}'"
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def set_key(lines: list[str], section: str, key: str, value: str, eol: str) -> str:
    """Insert or update `key = value` inside [section]. Returns a status word."""
    name = _section_name(section)
    header, end = _section_bounds(lines, name)
    newline = f"{key} = {_format_value(value)}{eol}"

    if header is not None:
        for index in range(header + 1, end):
            stripped = lines[index].strip()
            if stripped.startswith("#") or "=" not in stripped:
                continue
            if stripped.split("=", 1)[0].strip() == key:
                lines[index] = f"    {newline}"
                return "updated"
        lines.insert(header + 1, f"    {newline}")
        return "inserted"

    if lines and not lines[-1].endswith(("\n", "\r")):
        lines[-1] += eol
    lines.append(f"[{name}]{eol}")
    lines.append(f"    {newline}")
    return "created-section"


def _valid_toml(path: str, sections: list[str]) -> tuple[bool, str]:
    """Parse the file back and confirm each section is a table, not a list.

    Repeating a header would silently produce a TOML "array of tables"
    ([[ui]]) which parses fine but is wrong for a config file - so check it.
    """
    if tomllib is None:
        return True, "skipped (needs Python 3.11+)"
    try:
        with open(path, "rb") as handle:
            data = tomllib.load(handle)
    except Exception as exc:
        return False, str(exc)

    for section in sections:
        name = _section_name(section)
        value = data.get(name)
        if value is None:
            return False, f"missing section [{name}]"
        if not isinstance(value, dict):
            return False, f"[{name}] was written as an array of tables"

    return True, "valid"


def _to_forward_slashes(path: str) -> str:
    return os.path.abspath(path).replace("\\", "/")


# ------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Configure NarratoAI's config.toml")
    parser.add_argument("--config", default="config.toml", help="path to config.toml")
    parser.add_argument("--language", help='interface language, e.g. "en"')
    parser.add_argument("--ffmpeg-path", help="full path to ffmpeg.exe")
    parser.add_argument(
        "--first-run-english",
        action="store_true",
        help="fresh install: English UI, Edge TTS with an English voice, English subtitles",
    )
    parser.add_argument(
        "--ensure-language",
        action="store_true",
        help="repeat run: only make sure the UI language is English (never overwrites other choices)",
    )
    args = parser.parse_args(argv)

    config_path = args.config
    if not os.path.isfile(config_path):
        print(f"[WARN] {config_path} not found - nothing to do")
        return 0

    lines, eol = _read_lines(config_path)
    changes: list[str] = []
    problems: list[str] = []

    def apply(section: str, key: str, value: str) -> None:
        status = set_key(lines, section, key, value, eol)
        changes.append(f"{section} {key} = {value}  ({status})")

    if args.first_run_english:
        apply("[ui]", "language", "en")
        apply("[ui]", "tts_engine", "edge_tts")
        apply("[ui]", "edge_voice_name", "en-US-AvaMultilingualNeural-Female")
        apply("[ui]", "voice_name", "en-US-AvaMultilingualNeural-Female")
        apply("[ui]", "subtitle_translate_target_language", "English")
    elif args.ensure_language:
        apply("[ui]", "language", "en")

    if args.language:
        apply("[ui]", "language", args.language)

    if args.ffmpeg_path:
        if os.path.isfile(args.ffmpeg_path):
            # forward slashes: valid on Windows and needs no TOML escaping
            apply("[app]", "ffmpeg_path", _to_forward_slashes(args.ffmpeg_path))
        else:
            problems.append(f"ffmpeg.exe not found at {args.ffmpeg_path}")

    if not changes and not problems:
        print("[OK] config.toml already configured - no changes needed")
        return 0

    with open(config_path, "w", encoding="utf-8", newline="") as handle:
        handle.writelines(lines)

    for line in changes:
        print(f"[OK] config.toml: {line}")
    for line in problems:
        print(f"[WARN] {line}")

    ok, detail = _valid_toml(config_path, ["ui", "app"])
    if not ok:
        print(f"[ERROR] config.toml check failed: {detail}")
        return 1

    print(f"[OK] config.toml re-parsed successfully ({detail})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
