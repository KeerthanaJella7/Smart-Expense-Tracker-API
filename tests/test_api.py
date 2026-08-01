"""Comprehensive pytest suite for Smart Expense Tracker REST API."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure project root directory is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app
import src.storage as storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_tmp_storage(tmp_path, monkeypatch):
    """Fixture to isolate test storage to a temporary file per test run."""
    test_json_file = tmp_path / "test_expenses.json"
    test_json_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(storage, "DEFAULT_STORAGE_PATH", test_json_file)
    yield


def test_add_expense_success():
    """Test creating a valid expense record."""
    payload = {
        "title": "Grocery Shopping",
        "amount": 45.99,
        "category": "Food",
        "date": "2026-08-01"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Grocery Shopping"
    assert data["amount"] == 45.99
    assert data["category"] == "Food"
    assert data["date"] == "2026-08-01"


def test_add_expense_invalid_amount():
    """Test validation failure for amount <= 0."""
    payload = {
        "title": "Coffee",
        "amount": -5.0,
        "category": "Food",
        "date": "2026-08-01"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_add_expense_empty_title():
    """Test validation failure for empty or whitespace-only title."""
    payload = {
        "title": "   ",
        "amount": 12.0,
        "category": "Food",
        "date": "2026-08-01"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_add_expense_empty_category():
    """Test validation failure for empty category."""
    payload = {
        "title": "Bus Pass",
        "amount": 25.0,
        "category": "",
        "date": "2026-08-01"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_add_expense_invalid_date():
    """Test validation failure for invalid date format."""
    payload = {
        "title": "Movie Ticket",
        "amount": 15.0,
        "category": "Entertainment",
        "date": "01/08/2026"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_get_all_expenses():
    """Test retrieving all expenses."""
    client.post("/expenses", json={"title": "Item A", "amount": 10.0, "category": "CatA", "date": "2026-08-01"})
    client.post("/expenses", json={"title": "Item B", "amount": 20.0, "category": "CatB", "date": "2026-08-02"})

    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Item A"
    assert data[1]["title"] == "Item B"


def test_filter_expenses_by_category():
    """Test filtering expenses by category query parameter."""
    client.post("/expenses", json={"title": "Lunch", "amount": 15.0, "category": "Food", "date": "2026-08-01"})
    client.post("/expenses", json={"title": "Taxi", "amount": 30.0, "category": "Transport", "date": "2026-08-01"})

    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Lunch"
    assert data[0]["category"] == "Food"


def test_overall_total():
    """Test overall expense total calculation."""
    client.post("/expenses", json={"title": "Item 1", "amount": 100.50, "category": "Utility", "date": "2026-08-01"})
    client.post("/expenses", json={"title": "Item 2", "amount": 49.50, "category": "Food", "date": "2026-08-01"})

    response = client.get("/expenses/total")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 150.0
    assert data["category"] is None


def test_category_total():
    """Test category specific expense total calculation."""
    client.post("/expenses", json={"title": "Dinner", "amount": 60.0, "category": "Food", "date": "2026-08-01"})
    client.post("/expenses", json={"title": "Lunch", "amount": 20.0, "category": "Food", "date": "2026-08-02"})
    client.post("/expenses", json={"title": "Subway", "amount": 5.0, "category": "Transport", "date": "2026-08-02"})

    response = client.get("/expenses/total?category=Food")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 80.0
    assert data["category"] == "Food"


def test_delete_expense_success():
    """Test successful expense deletion by ID."""
    res = client.post("/expenses", json={"title": "To Delete", "amount": 12.5, "category": "Other", "date": "2026-08-01"})
    expense_id = res.json()["id"]

    del_res = client.delete(f"/expenses/{expense_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == expense_id

    # Verify expense is gone
    get_res = client.get("/expenses")
    assert len(get_res.json()) == 0


def test_delete_expense_not_found():
    """Test 404 response when attempting to delete non-existent ID."""
    response = client.delete("/expenses/99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["error"].lower()


def test_delete_expense_invalid_id():
    """Test that negative IDs are rejected as invalid input."""
    response = client.delete("/expenses/-1")
    assert response.status_code == 422


def test_static_ui_dashboard():
    """Test that root endpoint / serves the HTML web dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Expense Tracker" in response.text
    assert "<!DOCTYPE html>" in response.text


def test_empty_storage():
    """Test that GET /expenses returns empty list when storage file is empty."""
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_json_payload():
    """Test handling of malformed JSON payloads."""
    response = client.post(
        "/expenses",
        content="invalid json content",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_json_file_persistence(tmp_path, monkeypatch):
    """Test data persistence directly on the storage layer."""
    persistence_file = tmp_path / "persistence_test.json"
    monkeypatch.setattr(storage, "DEFAULT_STORAGE_PATH", persistence_file)

    # Initial load creates empty file
    loaded = storage.load_expenses()
    assert loaded == []

    # Save data
    sample = [{"id": 1, "title": "Coffee", "amount": 4.5, "category": "Food", "date": "2026-08-01"}]
    storage.save_expenses(sample)

    # Reload from disk
    reloaded = storage.load_expenses()
    assert len(reloaded) == 1
    assert reloaded[0]["title"] == "Coffee"


