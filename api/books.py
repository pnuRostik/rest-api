"""Books API resources (Flask-RESTful) with Swagger (Flasgger)."""

from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from core.db import get_books_collection
from models.book import BookStatus
from repository.book_repository import BookRepository
from schemas.book import BookCreate
from services.book_service import BookService


def _get_book_service() -> BookService:
    collection = get_books_collection()
    return BookService(BookRepository(collection))


class BookListResource(Resource):
    """GET /books — list with pagination; POST /books — create book."""

    def get(self):
        """
        Get books with page-based pagination.
        ---
        tags:
          - books
        parameters:
          - name: status
            in: query
            type: string
            enum: [available, borrowed]
            description: Filter by status
          - name: author
            in: query
            type: string
            description: Filter by author (exact match)
          - name: sort_by
            in: query
            type: string
            enum: [title, year]
            description: Sort field
          - name: sort_order
            in: query
            type: string
            enum: [asc, desc]
            default: asc
            description: Sort order
          - name: page
            in: query
            type: integer
            minimum: 1
            default: 1
            description: Page number (1-based)
          - name: size
            in: query
            type: integer
            minimum: 1
            maximum: 100
            default: 10
            description: Items per page
        responses:
          200:
            description: Paginated list of books
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      id: { type: string }
                      title: { type: string }
                      author: { type: string }
                      description: { type: string }
                      status: { type: string }
                      year: { type: integer }
                page: { type: integer }
                size: { type: integer }
                total: { type: integer }
                total_pages: { type: integer }
          400:
            description: Invalid sort_by (must be title or year)
        """
        service = _get_book_service()
        status_raw = request.args.get("status")
        try:
            status = BookStatus(status_raw) if status_raw else None
        except ValueError:
            return {"message": "status must be 'available' or 'borrowed'"}, 400
        author = request.args.get("author") or None
        sort_by = request.args.get("sort_by") or None
        sort_order = request.args.get("sort_order", "asc")
        try:
            page = int(request.args.get("page", 1))
            size = int(request.args.get("size", 10))
        except ValueError:
            page, size = 1, 10
        if page < 1:
            page = 1
        if size < 1:
            size = 10
        if size > 100:
            size = 100
        if sort_by is not None and sort_by not in ("title", "year"):
            return {"message": "sort_by must be 'title' or 'year'"}, 400
        data = service.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            size=size,
        )
        return data, 200

    def post(self):
        """
        Create a new book.
        ---
        tags:
          - books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - title
                - author
                - year
              properties:
                title:
                  type: string
                  minLength: 1
                  maxLength: 500
                author:
                  type: string
                  minLength: 1
                  maxLength: 300
                description:
                  type: string
                  maxLength: 2000
                  default: ""
                status:
                  type: string
                  enum: [available, borrowed]
                  default: available
                year:
                  type: integer
                  minimum: 0
        responses:
          201:
            description: Book created
            schema:
              type: object
              properties:
                id: { type: string }
                title: { type: string }
                author: { type: string }
                description: { type: string }
                status: { type: string }
                year: { type: integer }
          400:
            description: Validation error (invalid payload)
        """
        service = _get_book_service()
        payload = request.get_json(silent=True)
        if not payload:
            return {"message": "JSON body required"}, 400
        try:
            body = BookCreate.model_validate(payload)
        except ValidationError as e:
            return {"message": "Validation error", "errors": e.errors()}, 400
        book = service.create(body)
        return book, 201


class BookResource(Resource):
    """GET /books/<id> — get one; DELETE /books/<id> — delete (idempotent)."""

    def get(self, book_id: str):
        """
        Get a book by ID.
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: Book ID (MongoDB ObjectId string)
        responses:
          200:
            description: Book found
            schema:
              type: object
              properties:
                id: { type: string }
                title: { type: string }
                author: { type: string }
                description: { type: string }
                status: { type: string }
                year: { type: integer }
          404:
            description: Book not found
        """
        service = _get_book_service()
        book = service.get_by_id(book_id)
        if book is None:
            return {"message": "Book not found"}, 404
        return book, 200

    def delete(self, book_id: str):
        """
        Delete a book by ID (idempotent).
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: Book ID (MongoDB ObjectId string)
        responses:
          204:
            description: Book deleted or was already absent
        """
        service = _get_book_service()
        service.delete(book_id)
        return "", 204
