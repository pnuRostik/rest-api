
from fastapi import FastAPI

from api.books import router as books_router


app = FastAPI(
    title="Library API",
    description="API для бібліотеки. Сутність: Book.",
    version="1.0.0",
)

app.include_router(books_router)


