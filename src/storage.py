"""File storage operations for Smart Expense Tracker API."""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure project root directory is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import DEFAULT_STORAGE_PATH

logger = logging.getLogger("expense_tracker.storage")


def get_storage_path(custom_path: Optional[str] = None) -> Path:
    """Return the absolute path to the JSON storage file."""
    if custom_path:
        return Path(custom_path)
    return DEFAULT_STORAGE_PATH


def load_expenses(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load expense list from JSON storage file.

    Creates the JSON file with an empty list if it does not exist.
    """
    path = get_storage_path(file_path)

    if not path.exists():
        logger.info(f"Storage file missing at {path}. Auto-creating with empty list.")
        path.parent.mkdir(parents=True, exist_ok=True)
        save_expenses([], str(path))
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                logger.warning(f"Storage file at {path} is empty. Defaulting to empty list.")
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
            logger.warning(f"Data in {path} is not a list. Resetting to empty list.")
            return []
    except (json.JSONDecodeError, OSError) as exc:
        logger.error(f"Failed to decode storage file at {path}: {exc}. Defaulting to empty list.")
        return []


def save_expenses(expenses: List[Dict[str, Any]], file_path: Optional[str] = None) -> None:
    """Save expense list to JSON storage file cleanly with indent formatting."""
    path = get_storage_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2, ensure_ascii=False)
    logger.debug(f"Successfully saved {len(expenses)} expenses to {path}")


def generate_next_id(expenses: List[Dict[str, Any]]) -> int:
    """Generate the next auto-incrementing integer ID."""
    if not expenses:
        return 1
    existing_ids = [exp.get("id", 0) for exp in expenses if isinstance(exp.get("id"), int)]
    if not existing_ids:
        return 1
    return max(existing_ids) + 1
