from flask_sqlalchemy import SQLAlchemy
import re
import unicodedata

db = SQLAlchemy()


def normalize_name(name: str) -> str:
    """
    Normalize author names to a canonical form for duplicate checking.

    Steps performed:
        1. Lowercase the string.
        2. Remove punctuation and diacritics (accents).
        3. Collapse multiple whitespace characters.
        4. Convert "Lastname, Firstname" → "Firstname Lastname".
        5. Merge initials without dots (e.g., "J. K." → "jk").
        6. Keep only letters and spaces.

    Args:
        name (str): The original author name.

    Returns:
        str: Normalized name suitable for duplicate detection.
    """
    if not name:
        return ""

    # Unicode-normalization (ä → a, é → e, etc.)
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Remove periods, commas, apostrophes, extra spaces
    name = re.sub(r"[.,']", " ", name)
    name = re.sub(r"\s+", " ", name).strip().lower()

    # Reverse "lastname, firstname" format
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            name = f"{parts[1]} {parts[0]}"

    # Merge initials
    name = re.sub(r"\b([a-z])\s+([a-z])\b", r"\1\2", name)

    # Keep only letters and spaces
    name = re.sub(r"[^a-z\s]", "", name)

    # Collapse extra spaces again
    name = re.sub(r"\s+", " ", name).strip()

    return name


class Author(db.Model):
    """
    Represents an author in the library database.

    Attributes:
        id (int): Primary key, unique identifier for the author.
        name (str): Full name of the author.
        normalized_name (str): Canonical form of name for duplicate checking.
        birth_date (datetime.date): Author's birth date (optional).
        date_of_death (datetime.date): Author's death date (optional).
        books (list[Book]): List of books written by the author.
    """
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    normalized_name = db.Column(db.String(120), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the Author object.

        Returns:
            str: String with author ID and name.
        """
        return f"<Author {self.id}: {self.name}>"

    def __str__(self) -> str:
        """
        User-friendly representation of the Author object.

        Returns:
            str: Author's name with birth and death years (if available).
        """
        birth = self.birth_date.strftime("%Y-%m-%d") if self.birth_date else "?"
        death = self.date_of_death.strftime("%Y-%m-%d") if self.date_of_death else "?"
        return f"{self.name} ({birth} - {death})"


class Book(db.Model):
    """
    Represents a book in the library database.

    Attributes:
        id (int): Primary key, unique identifier for the book.
        isbn (str): International Standard Book Number, unique per book.
        title (str): Title of the book.
        publication_year (int): Year the book was published (optional).
        author_id (int): Foreign key referencing the author's ID.
        author (Author): Relationship to the Author model.
    """
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the Book object.

        Returns:
            str: String with book ID and title.
        """
        return f"<Book {self.id}: {self.title}>"

    def __str__(self) -> str:
        """
        User-friendly representation of the Book object.

        Returns:
            str: Book's title, publication year, and ISBN.
        """
        return f"'{self.title}' ({self.publication_year}), ISBN: {self.isbn}"
