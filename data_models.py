from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()


import re
import unicodedata

def normalize_name(name: str) -> str:
    """
    Normalize author names to a canonical form for duplicate checking.
    - Lowercases
    - Removes punctuation and diacritics (accents)
    - Collapses whitespace
    - Converts "Rowling, J. K." -> "jk rowling"
    - Removes dots between initials
    - Keeps consistent order: initials first, then last name
    """

    if not name:
        return ""

    # 1️⃣ Unicode-normalization (ä -> a, é -> e, etc.)
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # 2️⃣ Remove periods, commas, double spaces
    name = re.sub(r"[.,']", " ", name)
    name = re.sub(r"\s+", " ", name).strip().lower()

    # 3️⃣ If name is in the format "lastname, firstname" -> reverse
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            name = f"{parts[1]} {parts[0]}"

    # 4️⃣ Merge initials: "j k rowling" -> "jk rowling"
    name = re.sub(r"\b([a-z])\s+([a-z])\b", r"\1\2", name)

    # 5️⃣ Keep only letters and spaces
    name = re.sub(r"[^a-z\s]", "", name)

    # 6️⃣ Smooth spaces again
    name = re.sub(r"\s+", " ", name).strip()

    return name


class Author(db.Model):
    """
    Represents an author in the library system.

    Attributes:
        id (int): Primary key, unique identifier for the author.
        name (str): Full name of the author (must be unique).
        birth_date (datetime.date): Birth date of the author (optional).
        date_of_death (datetime.date): Date of death of the author (optional).
        books (list[Book]): List of books written by the author.
    """
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # ✅ Name is now unique
    name = db.Column(db.String(120), nullable=False, unique=True)
    normalized_name = db.Column(db.String(120), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        """
        Return a developer-friendly string representation of the Author instance.

        Returns:
            str: Representation of the author including ID and name.
        """
        return f"<Author {self.id}: {self.name}>"

    def __str__(self):
        """
        Return a user-friendly string representation of the Author instance.

        Returns:
            str: Author's name with birth and death dates.
        """
        birth = self.birth_date.strftime("%Y-%m-%d") if self.birth_date else "?"
        death = self.date_of_death.strftime("%Y-%m-%d") if self.date_of_death else "?"
        return f"{self.name} ({birth} - {death})"


class Book(db.Model):
    """
    Represents a book in the library system.

    Attributes:
        id (int): Primary key, unique identifier for the book.
        isbn (str): International Standard Book Number, unique for each book.
        title (str): Title of the book.
        publication_year (int): Year the book was published (optional).
        author_id (int): Foreign key referencing the author's ID.
        author (Author): The author who wrote the book.
    """
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def __repr__(self):
        """
        Return a developer-friendly string representation of the Book instance.

        Returns:
            str: Representation of the book including ID and title.
        """
        return f"<Book {self.id}: {self.title}>"

    def __str__(self):
        """
        Return a user-friendly string representation of the Book instance.

        Returns:
            str: Book's title, publication year, and ISBN.
        """
        return f"'{self.title}' ({self.publication_year}), ISBN: {self.isbn}"
