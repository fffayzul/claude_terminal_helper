import subprocess
import sys


DANGER_COLOUR = "\033[91m"  # red
WARN_COLOUR = "\033[93m"    # yellow
OK_COLOUR = "\033[92m"      # green
RESET = "\033[0m"


def run(command: str, dangerous: bool, explanation: str) -> None:
    """Print the proposed command, ask for confirmation if needed, then execute."""
    print(f"\n  {WARN_COLOUR}Command:{RESET}     {command}")
    print(f"  {WARN_COLOUR}What it does:{RESET} {explanation}")

    if dangerous:
        print(f"\n  {DANGER_COLOUR}⚠  This command may be irreversible.{RESET}")

    confirm = input("\n  Run it? [y/N] ").strip().lower()
    if confirm != "y":
        print("  Skipped.\n")
        return

    print(f"\n{'-' * 50}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print(f"{'-' * 50}")
        if result.returncode != 0:
            print(f"  {DANGER_COLOUR}Exited with code {result.returncode}{RESET}\n")
        else:
            print(f"  {OK_COLOUR}Done.{RESET}\n")
    except KeyboardInterrupt:
        print("\n  Interrupted.\n")
