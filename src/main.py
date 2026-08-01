"""Smart Expense Tracker REST API main FastAPI application module."""

import logging
import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root directory is in python path for clean package imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Query, Path as FastAPIPath, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from src.constants import ERR_EXPENSE_NOT_FOUND
from src.models import (
    Expense,
    ExpenseCreate,
    ExpenseTotalResponse,
    ExpenseDeleteResponse
)
from src.storage import load_expenses, save_expenses, generate_next_id
from src.utils import filter_expenses_by_category, calculate_total

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("expense_tracker.main")

app = FastAPI(
    title="Smart Expense Tracker API",
    description="Production-ready REST API for managing personal expenses with local JSON storage.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Custom Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return custom 422 JSON error format for Pydantic/FastAPI validation failures."""
    logger.warning(f"Validation failure on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "error": "Validation Error",
            "status_code": 422,
            "details": exc.errors()
        })
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return clean custom JSON format for HTTP exceptions (400, 404, etc.)."""
    logger.warning(f"HTTP {exc.status_code} exception on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all internal server error 500 exception handler."""
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "status_code": 500,
            "message": str(exc)
        }
    )


@app.post(
    "/expenses",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new expense",
    description="Validate and persist a new expense record into local storage."
)
def add_expense(expense_in: ExpenseCreate) -> Expense:
    """Add a new expense to storage and return the created record with ID."""
    expenses = load_expenses()
    next_id = generate_next_id(expenses)

    new_expense_data = expense_in.model_dump()
    new_expense_data["id"] = next_id

    expenses.append(new_expense_data)
    save_expenses(expenses)
    logger.info(f"Added new expense with ID {next_id}: '{expense_in.title}' (${expense_in.amount})")

    return Expense(**new_expense_data)


@app.get(
    "/expenses",
    response_model=List[Expense],
    status_code=status.HTTP_200_OK,
    summary="View all expenses",
    description="Retrieve all recorded expenses, with optional category filtering."
)
def get_expenses(
    category: Optional[str] = Query(
        None,
        description="Filter expenses by category (e.g. Food, Transportation)"
    )
) -> List[Expense]:
    """Retrieve all expenses, optionally filtered by category."""
    expenses = load_expenses()
    if category:
        expenses = filter_expenses_by_category(expenses, category)
    return [Expense(**exp) for exp in expenses]


@app.get(
    "/expenses/total",
    response_model=ExpenseTotalResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate total expenses",
    description="Return overall total expense amount, or total amount for a specific category."
)
def get_total_expenses(
    category: Optional[str] = Query(
        None,
        description="Category name to filter sum by"
    )
) -> ExpenseTotalResponse:
    """Calculate and return total expense sum."""
    expenses = load_expenses()
    normalized_category = category.strip() if category and category.strip() else None
    total_val = calculate_total(expenses, category=normalized_category)
    return ExpenseTotalResponse(
        total=total_val,
        category=normalized_category
    )


@app.delete(
    "/expenses/{id}",
    response_model=ExpenseDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an expense by ID",
    description="Remove an expense record by its unique integer identifier. Returns 404 if not found."
)
def delete_expense(id: int = FastAPIPath(..., gt=0)) -> ExpenseDeleteResponse:
    """Delete an expense record by ID."""
    expenses = load_expenses()
    target_index = None

    for idx, exp in enumerate(expenses):
        if exp.get("id") == id:
            target_index = idx
            break

    if target_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERR_EXPENSE_NOT_FOUND.format(id=id)
        )

    expenses.pop(target_index)
    save_expenses(expenses)
    logger.info(f"Deleted expense with ID {id}")

    return ExpenseDeleteResponse(
        message="Expense deleted successfully",
        id=id
    )


# Mount Static Dashboard Assets
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
