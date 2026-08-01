"""Pydantic data models and schemas for Smart Expense Tracker API."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Ensure project root directory is in python path for clean package imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import (
    DATE_FORMAT,
    ERR_TITLE_EMPTY,
    ERR_CATEGORY_EMPTY,
    ERR_AMOUNT_POSITIVE,
    ERR_DATE_FORMAT,
)


class ExpenseBase(BaseModel):
    """Base schema for expense payload validation."""

    title: str = Field(..., description="Title of the expense")
    amount: float = Field(..., gt=0, description="Expense amount, must be greater than 0")
    category: str = Field(..., description="Expense category")
    date: str = Field(..., description="Date of expense in YYYY-MM-DD format")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError(ERR_TITLE_EMPTY)
        return trimmed

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is not empty or whitespace only."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError(ERR_CATEGORY_EMPTY)
        return trimmed

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is greater than zero."""
        if v <= 0:
            raise ValueError(ERR_AMOUNT_POSITIVE)
        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format is strictly YYYY-MM-DD."""
        trimmed = v.strip()
        try:
            parsed_date = datetime.strptime(trimmed, DATE_FORMAT)
            return parsed_date.strftime(DATE_FORMAT)
        except ValueError:
            raise ValueError(ERR_DATE_FORMAT)


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""
    pass


class Expense(ExpenseBase):
    """Complete expense model including auto-generated id."""

    id: int = Field(..., description="Auto-generated unique integer identifier")


class ExpenseTotalResponse(BaseModel):
    """Response schema for total expenses calculation."""

    total: float = Field(..., description="Sum total of expenses")
    category: Optional[str] = Field(None, description="Category filter applied, if any")


class ExpenseDeleteResponse(BaseModel):
    """Response schema for expense deletion success."""

    message: str = Field(..., description="Status message")
    id: int = Field(..., description="ID of deleted expense")
