"""Unit tests for /books endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
 
    with TestClient(app) as c:
        yield c

def test_get_books_returns_200_and_page_paginated(client):
    """GET /books — returns 200 and page-based response (items, page, size, total, total_pages)."""
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "size" in data
    assert "total" in data
    assert "total_pages" in data
    assert isinstance(data["items"], list)


def test_get_book_by_id_returns_404_when_not_found(client):
    """GET /books/{id} — returns 404 for a non-existent id."""
    response = client.get("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_book_returns_201_and_created_book(client):
    """POST /books — returns 201 and book fields in response body."""
    payload = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "",
        "status": "available",
        "year": 2020,
    }
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert "id" in data


def test_delete_book_returns_204(client):
    """DELETE /books/{id} — returns 204 (idempotent)."""
    response = client.delete("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 204
