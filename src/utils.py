"""Business logic helper functions for expense filtering and total calculation."""

from typing import List, Dict, Any, Optional


def filter_expenses_by_category(expenses: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """Filter expenses by category name.

    Performs case-insensitive matching and trims whitespace.
    """
    if not category or not category.strip():
        return expenses

    target_category = category.strip().lower()
    return [
        exp for exp in expenses
        if exp.get("category", "").strip().lower() == target_category
    ]


def calculate_total(expenses: List[Dict[str, Any]], category: Optional[str] = None) -> float:
    """Calculate total expense sum overall or for a specific category.

    Rounds total result to 2 decimal places.
    """
    filtered_expenses = expenses
    if category and category.strip():
        filtered_expenses = filter_expenses_by_category(expenses, category)

    total_sum = sum(float(exp.get("amount", 0)) for exp in filtered_expenses)
    return round(total_sum, 2)
