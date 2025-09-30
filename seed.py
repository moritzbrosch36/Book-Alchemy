from app import app, db
from data_models import Author, Book
from datetime import datetime

def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None

def seed_data():
    with app.app_context():
        # Create authors
        authors = [
            Author(name="George Orwell", birth_date=parse_date("1903-06-25"),
                   date_of_death=parse_date("1950-01-21")),
            Author(name="J.K. Rowling", birth_date=parse_date("1965-07-31")),
            Author(name="J.R.R. Tolkien", birth_date=parse_date("1892-01-03"),
                   date_of_death=parse_date("1973-09-02")),
            Author(name="Harper Lee", birth_date=parse_date("1926-04-28"),
                   date_of_death=parse_date("2016-02-19")),
            Author(name="F. Scott Fitzgerald", birth_date=parse_date("1896-09-24"),
                   date_of_death=parse_date("1940-12-21")),
        ]
        db.session.add_all(authors)
        db.session.commit()

        # Create books (with matching author_id)
        books = [
            Book(isbn="9780451524935", title="1984",
                 publication_year=1949, author_id=1),
            Book(isbn="9780747532743", title="Harry Potter and the Philosopher's Stone",
                 publication_year=1997, author_id=2),
            Book(isbn="9780618260300", title="The Hobbit",
                 publication_year=1937, author_id=3),
            Book(isbn="9780061120084", title="To Kill a Mockingbird",
                 publication_year=1960, author_id=4),
            Book(isbn="9780743273565", title="The Great Gatsby",
                 publication_year=1925, author_id=5),
        ]
        db.session.add_all(books)
        db.session.commit()

        print("✅ Database seeded with authors and books!")


if __name__ == "__main__":
    seed_data()
