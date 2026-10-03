"""Check a saved script BEFORE rendering, so you never render a 52-second recap.

Why this exists
---------------
The length of the finished recap is decided by the editing script, not by the
renderer. Every narration item (OST=0) is cut to the length of its spoken
voice-over, and every original-sound item (OST=1) is cut to its timestamp
range. If the script only holds a handful of items, the finished video will be
a minute long no matter what else you change.

Run this on the saved script (resource/scripts/*.json) and it tells you, in
plain English, roughly how long the video will be - before you spend an hour
rendering.

Usage (normally run through check-recap-length.bat):
    python check_recap_length.py
    python check_recap_length.py --target 15
    python check_recap_length.py --script resource/scripts/2026-1003-144737.json
    python check_recap_length.py --wpm 145

The estimate for narration items is words / words-per-minute. The default is
150 words per minute, which matches the Edge TTS voices at rate 1.0. Original
sound items use their exact timestamp length.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

DEFAULT_WPM = 150.0
DEFAULT_TARGET_MINUTES = 15.0
TIMESTAMP = re.compile(
    r"^\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-\s*"
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*$"
)


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


def to_seconds(hours: str, minutes: str, seconds: str, millis: str) -> float:
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis.ljust(3, "0")) / 1000.0
    )


def parse_span(value: str) -> float | None:
    match = TIMESTAMP.match(str(value or ""))
    if not match:
        return None
    start = to_seconds(*match.groups()[:4])
    end = to_seconds(*match.groups()[4:])
    return max(0.0, end - start)


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", str(text or "")))


def find_script(root: str, given: str | None) -> str | None:
    if given:
        return given if os.path.isfile(given) else None
    base = os.path.join(root, "resource", "scripts")
    candidates = glob.glob(os.path.join(base, "**", "*.json"), recursive=True)
    if not candidates:
        return None
    # The file names are timestamps (YYYY-MMDD-HHMMSS.json), so the name breaks
    # ties when two scripts were written within the same clock tick.
    return max(candidates, key=lambda path: (os.path.getmtime(path), os.path.basename(path)))


def format_time(seconds: float) -> str:
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}:{secs:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate the length of the recap from the saved script."
    )
    parser.add_argument("--script", help="path to a script JSON (default: newest)")
    parser.add_argument(
        "--target",
        type=float,
        default=DEFAULT_TARGET_MINUTES,
        help=f"target length in minutes (default: {DEFAULT_TARGET_MINUTES:g})",
    )
    parser.add_argument(
        "--wpm",
        type=float,
        default=DEFAULT_WPM,
        help=f"narration speed in words per minute (default: {DEFAULT_WPM:g})",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))

    print("NarratoAI recap length check")
    print("-" * 50)

    script_path = find_script(root, args.script)
    if not script_path:
        fail("No script JSON found.")
        print("       Generate the editing script first, click Save Script,")
        print("       then run this check again. You can also pass a path:")
        print("         check-recap-length.bat --script resource\\scripts\\NAME.json")
        return 1

    try:
        with open(script_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        fail(f"Could not read {script_path}: {error}")
        return 1

    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        fail("The script contains no items - nothing would be rendered.")
        return 1

    narration_seconds = 0.0
    narration_words = 0
    original_seconds = 0.0
    bad_timestamps = 0
    narration_items = 0
    original_items = 0
    longest_item = 0.0

    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            ost = int(item.get("OST", 0))
        except (TypeError, ValueError):
            ost = 0
        span = parse_span(item.get("timestamp"))
        if span is None:
            bad_timestamps += 1
            span = 0.0

        if ost == 1:
            original_items += 1
            original_seconds += span
            longest_item = max(longest_item, span)
        else:
            narration_items += 1
            words = count_words(item.get("narration"))
            narration_words += words
            seconds = words / (args.wpm / 60.0) if args.wpm > 0 else 0.0
            narration_seconds += seconds
            longest_item = max(longest_item, seconds)

    total = narration_seconds + original_seconds
    target_seconds = args.target * 60.0
    ratio = (original_seconds / total * 100.0) if total else 0.0

    print(f"Script      : {os.path.relpath(script_path)}")
    print(f"Items       : {len(items)}  ({narration_items} narration / {original_items} original sound)")
    print(f"Narration   : {narration_words} words  =  about {format_time(narration_seconds)} at {args.wpm:g} wpm")
    print(f"Film audio  : {format_time(original_seconds)}")
    print(f"Original footage ratio: {ratio:.0f}%")
    if bad_timestamps:
        print(f"[WARN] {bad_timestamps} item(s) have an unreadable timestamp.")
    print()
    print(f"ESTIMATED LENGTH : {format_time(total)}   (target {format_time(target_seconds)})")
    print("-" * 50)

    if total < target_seconds * 0.6:
        print("[TOO SHORT] Do NOT render this script yet.")
        print()
        print("The script is far shorter than your target. This is decided by the")
        print("script, not by the renderer, so rendering now would waste an hour.")
        print()
        print("Fix it like this:")
        print("  1. In the app, open the script panel for your mode.")
        print("  2. Raise 'Copy Length' (default 500 = about 3.5 minutes of speech).")
        print(f"     For roughly {args.target:g} minutes with 30% film audio, use about")
        print(f"     {int(args.target * 0.7 * args.wpm / 50) * 50} words: words ~= target_minutes x 0.7 x {args.wpm:g}.")
        print("  3. Click 'Generate Narration Copy' and check the text is long.")
        print("  4. Click 'Generate Editing Script' again, then 'Save Script'.")
        print("  5. Run this check again - it should reach the target before rendering.")
        return 1

    if total < target_seconds * 0.85:
        print("[A BIT SHORT] Close to the target. Rendering is safe if you are happy")
        print("             with it - or raise Copy Length slightly for more detail.")
        return 0

    if total > target_seconds * 1.6:
        print("[LONG] This will run noticeably longer than your target.")
        print("       That is fine if you want it - otherwise lower Copy Length.")
        return 0

    print("[OK] This script should produce a video of about the length you want.")
    print("     If the item count looks too small, compare it with the speech:")
    print("     roughly 25-35 words of narration per item is normal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
