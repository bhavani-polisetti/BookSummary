from fastapi import FastAPI
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import ClassVar

# PostgresDB connection settings
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "admin"
POSTGRES_HOST = "localhost"
POSTGRES_DB = "postgres"
POSTGRES_PORT = "5432"

# Create engine and session
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class for declarative models
Base = declarative_base()

# Define the User model
class Books(Base):
    __tablename__ = "books"
    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    author = Column(String, index=True)
    genre = Column(Integer, index=True)
    year_published = Column(Integer, index=True)
    summary = Column(String, index=True)

    # def __repr__(self):
    #     return f"User(id={self.id}, name={self.name}, email={self.email})"

class Reviews(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    review_text = Column(String, index=True)
    rating = Column(String, index=True)

    # def __repr__(self):
    #     return f"User(id={self.id}, name={self.name}, email={self.email})"

# Create the tables in the database
Base.metadata.create_all(engine)

# Define the FastAPI app
app = FastAPI()

# Define the Pydantic models for request and response
class BookRequest(BaseModel):
    book_id: ClassVar[int]
    title: ClassVar[str]
    author: ClassVar[str]
    genre: ClassVar[str]
    year_published: ClassVar[str]
    summary: ClassVar[str]

class BookResponse(BaseModel):
    review_id: ClassVar[int]
    book_id: ClassVar[int]
    user_id: ClassVar[str]
    review_text: ClassVar[str]
    rating: ClassVar[str]

@app.get("/")
def welcome_to_bookstore():
    return "Hello, world"

# CRUD operations
@app.post("/book/", response_model=BookResponse)
def add_book(book: BookRequest):
    db = SessionLocal()
    new_book= Book(book_id = book.book_id,title = book.title,author = book.author,genre = book.genre,
                    year_published = book.year_published,summary = book.summary)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books/", response_model=list[BookResponse])
def read_books():
    db = SessionLocal()
    books = db.query(Book).all()
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(user_id: int):
    db = SessionLocal()
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookRequest):
    db = SessionLocal()
    existing_book = db.query(Book).get(book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    existing_book.name = book.name
    existing_book.email = book.email
    db.commit()
    db.refresh(existing_book)
    return existing_book

@app.delete("/books/{book_id}")
def delete_user(book_id: int):
    db = SessionLocal()
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)