from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status


app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: float
    published_year: int

    def __init__(self, id, title, author, description, rating, published_year):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year


class BookRequest(BaseModel):
    id: Optional[int] = Field(
        description="No need to pass ID on creation", default=None
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: float = Field(ge=0, le=5)
    published_year: int = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "description": (
                    "A novel set in the American South during the"
                    " 1930s, focusing on themes of"
                    "r acial injustice and moral growth."
                ),
                "rating": 4.8,
                "published_year": 2012,
            }
        }
    }


BOOKS = [
    Book(
        **{
            "id": 1,
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "description": (
                "A novel set in the American South during the"
                " 1930s, focusing on themes of racial injustice"
                " and moral growth."
            ),
            "rating": 4.8,
            "published_year": 2010,
        }
    ),
    Book(
        **{
            "id": 2,
            "title": "1984",
            "author": "George Orwell",
            "description": (
                "A dystopian novel depicting a totalitarian regime"
                " that uses surveillance and propaganda to control"
                " its citizens."
            ),
            "rating": 4.7,
            "published_year": 2012,
        }
    ),
    Book(
        **{
            "id": 3,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": (
                "A story about the enigmatic Jay Gatsby and his"
                " unrequited love for Daisy Buchanan, set in the"
                " Roaring Twenties."
            ),
            "rating": 4.6,
            "published_year": 2010,
        }
    ),
    Book(
        **{
            "id": 4,
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": (
                "A romantic novel that explores the themes of "
                "love, class, and societal expectations through"
                " the story of Elizabeth Bennet and Mr. Darcy."
            ),
            "rating": 4.9,
            "published_year": 2012,
        }
    ),
    Book(
        **{
            "id": 5,
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "description": (
                "A coming-of-age novel following the experiences "
                "of Holden Caulfield, a disillusioned teenager in"
                " New York City."
            ),
            "rating": 4.4,
            "published_year": 2012,
        }
    ),
    Book(
        **{
            "id": 6,
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "description": (
                "A fantasy novel about Bilbo Baggins' adventurous "
                "journey to reclaim a treasure guarded by the "
                "dragon Smaug."
            ),
            "rating": 4.8,
            "published_year": 2009,
        }
    ),
    Book(
        **{
            "id": 7,
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "description": (
                "A philosophical tale about Santiago, a shepherd "
                "boy, who embarks on a journey to find a treasure,"
                " learning about the importance of following one's"
                " dreams."
            ),
            "rating": 4.7,
            "published_year": 2020,
        }
    ),
    Book(
        **{
            "id": 8,
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "description": (
                "A dystopian novel set in a future society "
                "characterized by technological advancements and "
                "the loss of individuality."
            ),
            "rating": 4.5,
            "published_year": 2012,
        }
    ),
]


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(ge=1)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_filtering(
    rating: float | None = Query(default=None, ge=0, le=5),
    published_year: int | None = Query(default=None, ge=1990, le=2030),
):
    print(rating, published_year)
    filtered_books = BOOKS
    if rating:
        filtered_books = [
            book for book in filtered_books if book.rating == rating
        ]
    if published_year:
        filtered_books = [
            book
            for book in filtered_books
            if book.published_year == published_year
        ]
    return filtered_books


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(new_book: BookRequest):
    book_obj = Book(**new_book.model_dump())
    BOOKS.append(find_book_id(book_obj))
    return book_obj


def find_book_id(book: Book):
    book.id = 1 if not BOOKS else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(update_book: BookRequest):
    book_changed = False
    for i, book in enumerate(BOOKS):
        if book.id == update_book.id:
            BOOKS[i] = update_book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(ge=1)):
    book_changed = False
    for i, book in enumerate(BOOKS):
        if book.id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")
