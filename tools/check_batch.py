"""Static safety checks for the Windows .bat files.

Catches the things that make a batch file close instantly or misbehave:
unbalanced blocks, missing goto targets, unreachable labels, falling through
into error handlers, unescaped special characters inside blocks, and
non-CRLF / BOM / non-ASCII encoding.

Usage: python tools/check_batch.py windows/update-windows.bat windows/start.bat
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LABEL = re.compile(r"^:([A-Za-z0-9_\-]+)")
GOTO = re.compile(r"\bgoto\s+:?([A-Za-z0-9_\-]+)", re.IGNORECASE)
CALL = re.compile(r"\bcall\s+:([A-Za-z0-9_\-]+)", re.IGNORECASE)


def read_lines(path: Path) -> tuple[list[str], bytes]:
    """Read keeping CRLF intact (newline='' disables universal newlines)."""
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        text = handle.read()
    return text.split("\r\n"), path.read_bytes()


def is_comment(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped.upper().startswith("REM ")
        or stripped.upper() == "REM"
        or stripped.startswith("::")
    )


def check_encoding(path: Path, raw: bytes) -> list[str]:
    problems = []
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append("starts with a UTF-8 BOM (breaks cmd parsing)")
    try:
        raw.decode("ascii")
    except UnicodeDecodeError:
        problems.append("contains non-ASCII bytes (console codepage risk)")
    crlf = raw.count(b"\r\n")
    bare = raw.replace(b"\r\n", b"").count(b"\n")
    if crlf == 0:
        problems.append("no CRLF line endings - cmd can misparse goto/labels")
    if bare:
        problems.append(f"{bare} bare LF line(s) mixed in")
    return problems


def strip_quoted(line: str) -> str:
    return re.sub(r'"[^"]*"', '""', line)


def check_parens(lines: list[str]) -> list[str]:
    problems = []
    depth = 0
    for number, line in enumerate(lines, start=1):
        if is_comment(line):
            continue
        code = strip_quoted(line).replace("^(", "").replace("^)", "")
        opens, closes = code.count("("), code.count(")")
        if depth > 0 and line.strip().lower().startswith("echo") and (opens or closes):
            problems.append(
                f"line {number}: unescaped parenthesis in echo inside a block "
                "(must be ^( and ^))"
            )
        depth += opens - closes
        if depth < 0:
            problems.append(f"line {number}: ')' closes a block that was never opened")
            depth = 0
    if depth:
        problems.append(f"file ends with {depth} unclosed '(' block(s)")
    return problems


def analyse_flow(lines: list[str]) -> tuple[set[str], set[str], list[str]]:
    labels = {m.group(1): i for i, l in enumerate(lines) if (m := LABEL.match(l))}
    reached: set[str] = set()
    missing: list[str] = []
    seen: set[int] = set()
    stack = [0]

    depth = 0
    while stack:
        index = stack.pop()
        while 0 <= index < len(lines):
            if index in seen:
                break
            seen.add(index)
            line = lines[index]
            if match := LABEL.match(line):
                reached.add(match.group(1))
            if not is_comment(line):
                for target in GOTO.findall(line) + CALL.findall(line):
                    if target in labels:
                        stack.append(labels[target])
                    else:
                        missing.append(f"line {index + 1}: goto/call to missing :{target}")
                code = strip_quoted(line).replace("^(", "").replace("^)", "")
                opened, closed = code.count("("), code.count(")")
                stripped = line.strip().lower()
                # a jump or exit inside an if(...) block is conditional, so the
                # sequential path must also continue past it
                if depth == 0 and (
                    stripped.startswith("exit /b")
                    or stripped == "exit"
                    or stripped.startswith("goto ")
                ):
                    depth += opened - closed
                    break
                depth += opened - closed
            index += 1

    return set(labels), reached, missing


def main(paths: list[str]) -> int:
    failures = 0
    for path_str in paths:
        path = Path(path_str)
        lines, raw = read_lines(path)
        print(f"=== {path.name} ===")

        problems = check_encoding(path, raw)
        problems += check_parens(lines)

        labels, reached, missing = analyse_flow(lines)
        problems += missing
        unreachable = sorted(labels - reached)
        if unreachable:
            problems.append("unreachable label(s): " + ", ".join(unreachable))

        bare_exit = [n for n, l in enumerate(lines, 1) if l.strip().lower() == "exit"]
        if bare_exit:
            problems.append(f"bare 'exit' closes the window - line(s) {bare_exit}")

        if problems:
            for problem in problems:
                print(f"  FAIL  {problem}")
            failures += 1
        else:
            print(f"  OK    {len(labels)} labels | all reachable | blocks balanced")

        pauses = sum(1 for l in lines if l.strip().lower().startswith("pause"))
        print(
            f"  info  pause: {pauses} | keep-alive wrapper: {'__keepalive__' in ''.join(lines)}"
            f" | lines: {len(lines)}"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
