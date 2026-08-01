"""Application constants for Smart Expense Tracker API."""

from pathlib import Path

# File System Paths
DEFAULT_STORAGE_FILENAME = "expenses.json"
DEFAULT_STORAGE_PATH = Path(__file__).parent / DEFAULT_STORAGE_FILENAME

# Validation Formats
DATE_FORMAT = "%Y-%m-%d"
DATE_REGEX_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

# Error Messages
ERR_TITLE_EMPTY = "title cannot be empty"
ERR_CATEGORY_EMPTY = "category cannot be empty"
ERR_AMOUNT_POSITIVE = "amount must be greater than zero"
ERR_DATE_FORMAT = "date must be YYYY-MM-DD"
ERR_EXPENSE_NOT_FOUND = "Expense with id {id} not found"
