from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.secret_key = "supersecretkey"  # necessary for flash messages

from data_models import db, Author, Book, normalize_name

db.init_app(app)


with app.app_context():
    db.create_all()


def parse_iso_date(s: str):
    """Convert a date string in 'YYYY-MM-DD' format to a datetime.date object."""
    if not s:
        return None
    s = s.strip()
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


@app.route("/", methods=["GET"])
def home():
    """Render the home page with a list of books."""
    sort_by = request.args.get("sort", "title")
    keyword = request.args.get("keyword", "").strip()

    query = Book.query.join(Author)

    if keyword:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{keyword}%"),
                Author.name.ilike(f"%{keyword}%")
            )
        )

    if sort_by == "author":
        query = query.order_by(Author.name.asc())
    else:
        query = query.order_by(Book.title.asc())

    books = query.all()

    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Display form for adding a new author and handle form submission."""
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        b_raw = (request.form.get("birth_date") or "").strip()
        d_raw = (request.form.get("date_of_death") or "").strip()

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("add_author"))

        # ✅ Normalize the name for duplicate checking
        normalized_name = normalize_name(name)
        existing_author = Author.query.filter_by(normalized_name=normalized_name).first()

        if existing_author:
            flash(f"Author '{existing_author.name}' already exists.", "error")
            return redirect(url_for("add_author"))

        birth_date = parse_iso_date(b_raw)
        date_of_death = parse_iso_date(d_raw)

        invalid = []
        if b_raw and birth_date is None:
            invalid.append("Birth Date")
        if d_raw and date_of_death is None:
            invalid.append("Date of Death")
        if invalid:
            flash(
                f"Invalid date for: {', '.join(invalid)}. Please use the format YYYY-MM-DD.",
                "error"
            )
            return redirect(url_for("add_author"))

        new_author = Author(
            name=name,
            normalized_name=normalized_name,
            birth_date=birth_date,
            date_of_death=date_of_death,
        )

        db.session.add(new_author)

        # ✅ Safe commit with error handling
        try:
            db.session.commit()
            flash(f"Author '{name}' successfully added!", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f"Author '{name}' already exists in the database.", "error")

        return redirect(url_for("add_author"))

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Display form for adding a new book and handle form submission."""
    authors = Author.query.all()

    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id,
        )
        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' successfully added!", "success")
        return redirect(url_for("add_book"))

    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book by ID and possibly its author if they have no other books."""
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"Book '{book.title}' and author '{author.name}' deleted!", "success")
    else:
        flash(f"Book '{book.title}' deleted!", "success")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
