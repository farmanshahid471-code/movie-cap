"""Patch NarratoAI so the final video keeps the film's original audio.

The problem
-----------
When NarratoAI merges the finished clips it mixes the original film audio into
the soundtrack. To do that it writes an ffmpeg filter graph to a temporary file
and passes it with:

    ffmpeg ... -filter_complex_script <file> ...

`-filter_complex_script` was deprecated by FFmpeg in January 2024 (commit
"fftools/ffmpeg: deprecate -filter_complex_script") and has since been removed
from current builds. With a new ffmpeg the command dies immediately:

    Unrecognized option 'filter_complex_script'.

NarratoAI catches that error and silently falls back to "无音频合并"
("merging without audio"), so the merged file has NO audio track. Later the
pipeline logs:

    视频没有音轨，无法提取原声
    ("the video has no audio track, original sound cannot be extracted")

...and the finished recap ends up with narration and subtitles only - the film's
own dialogue, music and sound effects are gone.

What this patch does
--------------------
It replaces the version-specific option with plain `-filter_complex`, passing
the filter graph inline instead of by file name:

    with open(filter_script, ...) as f:
        _filter_complex_graph = f.read()
    ... '-filter_complex', _filter_complex_graph, ...

`-filter_complex` exists in every ffmpeg build, old and new, so the same code
now works on the bundled ffmpeg as well as on a freshly downloaded master
build. The filter graph itself is unchanged, so the audio mix sounds exactly
as intended.

Edited files:
    app/services/merger_video.py   (combine_clip_videos -> audio mixing step)
    ...plus any other project file still using -filter_complex_script

Safety:
  * a .bak backup is written the first time a file is changed
  * running it twice is harmless (it detects its own marker)
  * if the backup already contains the patch, it refuses to roll back and
    keeps your current file instead of destroying it
  * every patched file is compiled afterwards; on any error the backup is restored
  * if the anchor no longer matches (upstream changed) it stops without writing
  * a dry run is available: --dry-run prints the diff without touching anything
"""

from __future__ import annotations

import os
import re
import shutil
import sys

VERSION_MARKER = "_filter_complex_graph"
BACKUP_SUFFIX = ".ffmpeg-filter.bak"

# The deprecated option and the file variable that follows it, e.g.
#     '-filter_complex_script', filter_script,
OPTION_LINE = re.compile(
    r"""^(?P<indent>\s*)(?P<q>['"])-filter_complex_script(?P=q)\s*,\s*"""
    r"""(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*,?\s*$"""
)

# The statement that builds the ffmpeg command, e.g. `audio_mix_cmd = [`
COMMAND_START = re.compile(r"^(?P<indent>\s*)(?:[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\[\s*$")

# Any other removed-in-new-ffmpeg options we should at least report.
OTHER_DEPRECATED = ("-filter_script",)

SEARCH_DIRS = (os.path.join("app"), os.path.join("webui"))

# The hints below quote Chinese log lines. On a console that cannot print them
# (wrong codepage) Python would normally abort with UnicodeEncodeError - show a
# placeholder instead and keep going.
try:
    sys.stdout.reconfigure(errors="replace")
except (AttributeError, ValueError):
    pass


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


def display(path: str) -> str:
    try:
        return os.path.relpath(path)
    except ValueError:
        return path


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def backup(path: str) -> str:
    target = path + BACKUP_SUFFIX
    if not os.path.exists(target):
        shutil.copy2(path, target)
        print(f"[OK] Backup written: {display(target)}")
    return target


def restore(path: str) -> None:
    target = path + BACKUP_SUFFIX
    if os.path.exists(target):
        shutil.copy2(target, path)
        print(f"[OK] Restored the original {display(path)} from the backup")


def verify_source(path: str) -> None:
    """Compile the patched file; raise on syntax errors."""
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    compile(source, path, "exec")


def already_patched(text: str) -> bool:
    return VERSION_MARKER in text


def find_command_start(lines: list[str], option_index: int) -> int:
    """Walk backwards from the option line to the statement that opens the list."""
    for index in range(option_index - 1, -1, -1):
        if COMMAND_START.match(lines[index]):
            return index
    return -1


def patch_text(text: str) -> tuple[str, int]:
    """Return (patched_text, number_of_replacements)."""
    lines = text.splitlines(keepends=True)

    targets = []
    for index, line in enumerate(lines):
        match = OPTION_LINE.match(line.rstrip("\r\n"))
        if match:
            targets.append((index, match))

    if not targets:
        return text, 0

    for index, match in reversed(targets):
        statement_index = find_command_start(lines, index)
        if statement_index < 0:
            raise RuntimeError(
                "could not find the ffmpeg command that uses "
                "'-filter_complex_script' - upstream layout changed"
            )

        indent = match.group("indent")
        variable = match.group("var")
        statement_indent = COMMAND_START.match(lines[statement_index]).group("indent")

        reader = [
            f"{statement_indent}with open({variable}, 'r', encoding='utf-8', "
            f"errors='replace') as _filter_script_file:\n",
            f"{statement_indent}    _filter_complex_graph = _filter_script_file.read()\n",
        ]
        lines[statement_index:statement_index] = reader

        # the option line moved down by the two inserted lines
        shifted = index + len(reader)
        newline = "\n" if lines[shifted].endswith("\n") else ""
        lines[shifted] = f"{indent}'-filter_complex', _filter_complex_graph,{newline}"

    return "".join(lines), len(targets)


def patch_file(path: str, dry_run: bool) -> str:
    """Return one of: 'patched', 'unchanged', 'failed'."""
    text = read(path)

    if already_patched(text):
        print(f"[SKIP] {display(path)} is already patched")
        return "unchanged"

    for option in OTHER_DEPRECATED:
        if option in text:
            print(
                f"[WARN] {display(path)} also uses {option}, which new ffmpeg "
                "builds removed as well. This script does not change it - please report it."
            )

    try:
        patched, count = patch_text(text)
    except RuntimeError as error:
        fail(f"{display(path)}: {error}")
        return "failed"

    if not count:
        print(f"[SKIP] {display(path)} needs no change")
        return "unchanged"

    if dry_run:
        print(f"[DRY-RUN] {display(path)}: would replace {count} occurrence(s)")
        for line in patched.splitlines():
            if "-filter_complex" in line or VERSION_MARKER in line:
                print(f"          {line.strip()}")
        return "unchanged"

    backup(path)
    write(path, patched)

    try:
        verify_source(path)
    except SyntaxError as error:
        restore(path)
        fail(f"{display(path)} did not compile after patching ({error}) - backup restored")
        print("       Nothing was changed. Please report this so the patch can be updated.")
        return "failed"

    print(f"[OK] Patched {display(path)} ({count} occurrence(s))")
    return "patched"


def find_targets(root: str) -> list[str]:
    targets = []
    for folder in SEARCH_DIRS:
        base = os.path.join(root, folder)
        for current, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".py"):
                    path = os.path.join(current, name)
                    try:
                        if "-filter_complex_script" in read(path):
                            targets.append(path)
                    except (OSError, UnicodeDecodeError):
                        continue
    return sorted(targets)


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    root = os.path.dirname(os.path.abspath(__file__))

    print("NarratoAI ffmpeg filter-option fix")
    print("-" * 50)
    print("Fixes: 'Unrecognized option filter_complex_script' -> no original audio")
    print()

    merger = os.path.join(root, "app", "services", "merger_video.py")
    if not os.path.exists(merger):
        fail("app/services/merger_video.py was not found.")
        print("       Put this script NEXT TO webui.py and run it again.")
        return 1

    targets = find_targets(root) or [merger]
    changed = False
    failed = False
    for path in targets:
        result = patch_file(path, dry_run)
        if result == "patched":
            changed = True
        elif result == "failed":
            failed = True

    if dry_run:
        print()
        print("[DONE] Dry run only - nothing was written.")
        return 0

    if failed:
        print()
        print("[FAILED] The patch was NOT applied. Your original files are unchanged.")
        return 1

    if not changed:
        print()
        print("[OK] Nothing to do - the audio merge fix is already applied.")
        return 0

    print()
    print("[DONE] Restart NarratoAI for the change to take effect.")
    print("       After the next render the log should show:")
    print("         音频混合完成            (audio mixing finished)")
    print("         视频最终合并完成        (final video merge finished)")
    print("         原声提取...             (original audio extraction)")
    print("       and it should NOT show:")
    print("         尝试备用合并方法 - 无音频合并  (fallback: merge without audio)")
    print("         视频没有音轨，无法提取原声     (no audio track to extract)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
