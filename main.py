#!/usr/bin/env python3
"""
AI Terminal Assistant
---------------------
Type what you want to do in plain English.
The assistant translates it to a shell command, explains it, and asks before running.

Usage:
    python main.py

Special commands:
    scan <path>     — use the C extension to list files in a directory
    quit / exit     — leave the REPL
"""

import sys
from assistant import context, interpreter, executor

BLUE  = "\033[94m"
RESET = "\033[0m"


def try_load_scanner():
    """Try to import the compiled C extension. Graceful fallback if not built."""
    try:
        sys.path.insert(0, "scanner")
        import scanner
        return scanner
    except ImportError:
        return None


def handle_scan(scanner, args: str) -> None:
    path = args.strip() or "."
    min_bytes_str = ""
    parts = path.split()
    if len(parts) >= 2:
        path, min_bytes_str = parts[0], parts[1]

    min_bytes = int(min_bytes_str) if min_bytes_str.isdigit() else 0

    print(f"\nScanning '{path}' (min size: {min_bytes} bytes) using C extension...\n")
    files = scanner.scan(path, min_bytes)
    files.sort(key=lambda f: f["size"], reverse=True)

    for f in files[:50]:
        size_kb = f["size"] / 1024
        print(f"  {size_kb:8.1f} KB   {f['path']}")

    if len(files) > 50:
        print(f"\n  ... and {len(files) - 50} more files.")
    print(f"\n  Total: {len(files)} files\n")


def main():
    ctx = context.gather()
    ctx_summary = context.summary(ctx)
    scanner = try_load_scanner()

    print("=" * 55)
    print("  AI Terminal Assistant  |  powered by Claude")
    print(f"  {ctx['os']} | {ctx['cwd']}")
    if scanner:
        print("  C file scanner: loaded")
    print("  Type what you want to do, or 'quit' to exit")
    print("=" * 55)

    while True:
        try:
            user_input = input(f"\n{BLUE}>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        low = user_input.lower()
        if low in {"quit", "exit", "q"}:
            print("Bye!")
            break

        if low.startswith("scan") and scanner:
            handle_scan(scanner, user_input[4:])
            continue

        result = interpreter.interpret(user_input, ctx_summary)

        if not result.get("command"):
            print(f"\n  {result.get('explanation', 'Could not parse a command.')}\n")
            continue

        executor.run(
            command=result["command"],
            dangerous=result.get("dangerous", False),
            explanation=result.get("explanation", ""),
        )

        # Update CWD in case the command changed it
        ctx = context.gather()
        ctx_summary = context.summary(ctx)


if __name__ == "__main__":
    main()
