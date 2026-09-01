"""Locate the repository root (and optionally resolve the skills/ directory).

Works whether this module is executed directly (tools/scripts) or imported
from elsewhere in the repository.
"""

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def find_repo_root(source_file: str) -> Path:
    """Walk up from source_file's directory until a `.git` directory is found."""
    current = Path(source_file).resolve().parent
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            return Path.cwd().resolve()  # fallback: current working directory
        current = parent


def find_skills_dir(source_file: str) -> Path:
    """Return <repo-root>/skills if it exists, otherwise <repo-root>/skill-creator."""
    root = find_repo_root(source_file)
    candidates = [root / "skills", root / "skill-creator"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def add_scripts_to_path() -> None:
    """Allow direct imports of sibling modules from this scripts directory."""
    sys.path.insert(0, str(SCRIPT_DIR))