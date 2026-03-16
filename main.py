from fastapi import FastAPI
from api.book import router as book_router
from api.auth import router as auth_router   

app = FastAPI(
    title="Library REST API",
    description="API for library management with MongoDB and JWT Authentication",
    version="4.0.0"  
)

 
app.include_router(auth_router)
app.include_router(book_router)