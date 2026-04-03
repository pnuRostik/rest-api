import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_get_books_returns_200_and_paginated(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_get_book_by_id_returns_404_when_not_found(client):
    response = client.get("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_book_returns_201_and_created_book(client):
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
    response = client.delete("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 204