from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------ DATABASE ------------------ #
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------ USER MODEL ------------------ #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ------------------ BOOK MODEL ------------------ #
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=3)  # 1–5 stars

# ------------------ REVIEW MODEL ------------------ #
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    user = db.relationship('User', backref='reviews')
    book = db.relationship('Book', backref='reviews')

# ------------------ SEEDING FUNCTION ------------------ #
def seed_books():
    Book.query.delete()
    db.session.commit()

    sample_books = [
        Book(title="The Hobbit", author="J.R.R. Tolkien",
             summary="A fantasy adventure with Bilbo Baggins.", price=12.99,
             image="hobbit.jpg", rating=5),
        Book(title="1984", author="George Orwell",
             summary="A dystopian novel about surveillance and control.", price=9.99,
             image="1984.jpg", rating=5),
        Book(title="Dune", author="Frank Herbert",
             summary="Epic sci-fi saga set on desert planet Arrakis.", price=14.50,
             image="dune.jpg", rating=4),
        Book(title="Pride and Prejudice", author="Jane Austen",
             summary="A timeless romance and social commentary masterpiece.", price=10.99,
             image="pride.jpg", rating=4),
        Book(title="The Great Gatsby", author="F. Scott Fitzgerald",
             summary="A story of wealth, love, and the American dream.", price=11.50,
             image="gatsby.jpg", rating=4),
        Book(title="To Kill a Mockingbird", author="Harper Lee",
             summary="A novel about justice and race in the Deep South.", price=12.00,
             image="mockingbird.jpg", rating=5),
        Book(title="Harry Potter and the Philosopher's Stone", author="J.K. Rowling",
             summary="The magical beginning of Harry Potter’s journey.", price=8.99,
             image="hp1.jpg", rating=5),
        Book(title="Harry Potter and the Chamber of Secrets", author="J.K. Rowling",
             summary="The chamber is opened again.", price=9.50,
             image="hp2.jpg", rating=4),
        Book(title="Harry Potter and the Prisoner of Azkaban", author="J.K. Rowling",
             summary="Sirius Black escapes Azkaban.", price=10.25,
             image="hp3.jpg", rating=5),
        Book(title="Harry Potter and the Goblet of Fire", author="J.K. Rowling",
             summary="The Triwizard Tournament begins.", price=11.00,
             image="hp4.jpg", rating=5),
        Book(title="The Catcher in the Rye", author="J.D. Salinger",
             summary="Holden Caulfield’s story of teenage angst.", price=9.75,
             image="catcher.jpg", rating=3),
        Book(title="The Lord of the Rings: Fellowship of the Ring", author="J.R.R. Tolkien",
             summary="The quest to destroy the One Ring begins.", price=13.99,
             image="lotr1.jpg", rating=5),
        Book(title="The Lord of the Rings: Two Towers", author="J.R.R. Tolkien",
             summary="The fellowship is broken, battles rage.", price=14.50,
             image="lotr2.jpg", rating=5),
        Book(title="The Lord of the Rings: Return of the King", author="J.R.R. Tolkien",
             summary="The final battle for Middle-earth.", price=15.00,
             image="lotr3.jpg", rating=5),
        Book(title="The Name of the Wind", author="Patrick Rothfuss",
             summary="An epic fantasy tale of magic and adventure.", price=17.95,
             image="namewind.jpg", rating=5),
        Book(title="The Silent Patient", author="Alex Michaelides",
             summary="A shocking psychological thriller with a twist.", price=13.95,
             image="silent.jpg", rating=4),
        Book(title="Project Hail Mary", author="Andy Weir",
             summary="A thrilling space adventure with heart and humor.", price=18.95,
             image="hailmary.jpg", rating=5),
        Book(title="The Seven Husbands of Evelyn Hugo", author="Taylor Jenkins Reid",
             summary="A captivating story of Hollywood’s golden age.", price=15.95,
             image="sevenhusbands.jpg", rating=4),
        Book(title="The Midnight Library", author="Matt Haig",
             summary="A touching novel about choices and regrets.", price=14.95,
             image="midnight.jpg", rating=4),
        Book(title="Brave New World", author="Aldous Huxley",
             summary="A dystopian vision of a controlled society.", price=12.50,
             image="bravenew.jpg", rating=4),
    ]

    db.session.add_all(sample_books)
    db.session.commit()

# ------------------ ROUTES ------------------ #
@app.route("/")
def home():
    books = Book.query.limit(6).all()
    return render_template("index.html", books=books, user=session.get("user"))

@app.route("/books")
def books():
    books = Book.query.all()
    return render_template("books.html", books=books, user=session.get("user"))

@app.route("/book/<int:id>", methods=["GET", "POST"])
def book_details(id):
    print("book_details route hit:", request.method, id)  # <-- add this line

    book = Book.query.get_or_404(id)
    user = session.get("user")

    if request.method == "POST":
        if not user:
            flash("You must be logged in to add a review", "warning")
            return redirect(url_for("login"))

        user_obj = User.query.filter_by(username=user).first()
        if not user_obj:
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for("login"))

        rating = int(request.form["rating"])
        text = request.form["text"]

        new_review = Review(rating=rating, text=text, user_id=user_obj.id, book_id=book.id)
        db.session.add(new_review)
        db.session.commit()

        flash("Review added successfully!", "success")
        return redirect(url_for("book_details", id=book.id))

    reviews = Review.query.filter_by(book_id=book.id).all()
    return render_template("book_details.html", book=book, reviews=reviews, user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid login details", "danger")
    return render_template("login.html", user=session.get("user"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You may now login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", user=session.get("user"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("home"))

@app.route("/account")
def account():
    user = session.get("user")
    if not user:
        flash("You must be logged in to access your account", "warning")
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    reviews = Review.query.filter_by(user_id=user_obj.id).all()
    return render_template("account.html", user=user_obj.username, reviews=reviews)


# ------------------ RUN ------------------ #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_books()
    app.run(debug=True)

