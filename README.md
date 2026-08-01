# Smart Expense Tracker API

This project is a lightweight REST API for managing personal expenses with FastAPI, Pydantic validation, and JSON file persistence. It follows the assignment requirements for adding, viewing, filtering, totaling, and deleting expenses while keeping the implementation simple and easy to review.

## Project Overview

The Smart Expense Tracker API allows a user to:

- add a new expense
- list all expenses
- filter expenses by category
- calculate the total for all expenses or a specific category
- delete an expense by ID

The application stores expenses in a local JSON file so it remains self-contained and does not require a database.

## Features

- REST API built with FastAPI
- JSON-based persistent storage in the local file system
- Input validation for title, category, amount, and date
- Case-insensitive category filtering
- Automatic ID generation for new expenses
- Test coverage with pytest and FastAPI TestClient
- Swagger and ReDoc documentation available at runtime

## Folder Structure

```text
README.md
AI_NOTES.md
requirements.txt
src/
    constants.py
    expenses.json
    main.py
    models.py
    storage.py
    utils.py
    static/
        app.js
        index.html
        styles.css
tests/
    test_api.py
```

## Installation

Create and activate a virtual environment:

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

The application uses a local storage file at [src/expenses.json](src/expenses.json). If the file does not exist, it will be created automatically on first use.

## Running the Application

Start the API with:

```bash
uvicorn src.main:app --reload
```

Then open:

- http://127.0.0.1:8000/docs for Swagger UI
- http://127.0.0.1:8000/redoc for ReDoc

## Testing

Run the test suite with:

```bash
pytest
```

## API Endpoints

| Method | Endpoint | Description | Status Codes |
| --- | --- | --- | --- |
| POST | /expenses | Create a new expense | 201, 422 |
| GET | /expenses | Retrieve all expenses or filter by category | 200 |
| GET | /expenses/total | Retrieve total expense amount | 200 |
| DELETE | /expenses/{id} | Delete an expense by ID | 200, 404, 422 |

## Example Requests

### Add an expense

```bash
curl -X POST "http://127.0.0.1:8000/expenses" -H "Content-Type: application/json" -d "{\"title\":\"Groceries\",\"amount\":45.5,\"category\":\"Food\",\"date\":\"2026-08-01\"}"
```

### List expenses

```bash
curl "http://127.0.0.1:8000/expenses"
```

### Filter expenses by category

```bash
curl "http://127.0.0.1:8000/expenses?category=Food"
```

### Get totals

```bash
curl "http://127.0.0.1:8000/expenses/total"
```

### Delete an expense

```bash
curl -X DELETE "http://127.0.0.1:8000/expenses/1"
```

## Example Responses

### Create expense response

```json
{
  "id": 1,
  "title": "Groceries",
  "amount": 45.5,
  "category": "Food",
  "date": "2026-08-01"
}
```

### Total response

```json
{
  "total": 45.5,
  "category": null
}
```

## Swagger Documentation

FastAPI exposes interactive documentation automatically:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Design Decisions

- JSON storage was chosen to match the assignment requirement and keep the project dependency-light.
- Pydantic models are used for validation so invalid payloads fail clearly and consistently.
- The storage layer is separated from the API layer to improve maintainability and testability.

## Future Improvements

- Add user authentication and per-user expense isolation.
- Support pagination and date-range filtering.
- Move storage from JSON files to a database in a future version.
- Add richer analytics and budget alerts.
