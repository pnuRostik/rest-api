import random
from locust import HttpUser, task, between

class BookStoreUser(HttpUser):

    wait_time = between(1, 3)

    @task(3)
    def get_books_list(self):
        """Тестуємо отримання списку книг з випадковими фільтрами"""
        limit = 10
        offset = random.randint(0, 20)
        
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        with self.client.get("/books/", params=params, name="/books/ (List)", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Статус код: {response.status_code}")

    @task(1)
    def get_books_with_filter(self):
        authors = ["Taras Shevchenko", "George Orwell", "Unknown"]
        author = random.choice(authors)
        
        self.client.get(f"/books/?author={author}", name="/books/ (Filter by Author)")