"""Library API — Flask + Flask-RESTful + Flasgger (Swagger)."""

import os

from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from api.books import BookListResource, BookResource
from core.db import close_client

app = Flask(__name__)
api = Api(app)

api.add_resource(BookListResource, "/books", endpoint="book_list")
api.add_resource(BookResource, "/books/<string:book_id>", endpoint="book")

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}
swagger_template = {
    "info": {
        "title": "Library API",
        "description": "API бібліотеки: книги (CRUD, пагінація, фільтри).",
        "version": "1.0.0",
    },
    "tags": [{"name": "books", "description": "Операції з книгами"}],
}
Swagger(app, config=swagger_config, template=swagger_template)


@app.teardown_appcontext
def teardown(exception=None):
    """Close MongoDB client on app context teardown."""
    close_client()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
