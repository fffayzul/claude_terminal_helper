import os
import platform
import subprocess


def gather() -> dict:
    """Collect OS context to pass to the LLM so it generates correct commands."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "shell": os.environ.get("SHELL", "unknown"),
        "cwd": os.getcwd(),
        "home": str(os.path.expanduser("~")),
        "user": os.environ.get("USER") or os.environ.get("USERNAME", "unknown"),
        "path_entries": os.environ.get("PATH", "").split(os.pathsep)[:8],
        "python_version": platform.python_version(),
        "git_repo": _is_git_repo(),
    }


def _is_git_repo() -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=2
        )
        return result.returncode == 0
    except Exception:
        return False


def summary(ctx: dict) -> str:
    return (
        f"OS: {ctx['os']} {ctx['os_version']}\n"
        f"Shell: {ctx['shell']}\n"
        f"CWD: {ctx['cwd']}\n"
        f"User: {ctx['user']}\n"
        f"Python: {ctx['python_version']}\n"
        f"Inside git repo: {ctx['git_repo']}"
    )
