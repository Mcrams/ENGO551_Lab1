import os
import webbrowser
import json

from flask import Flask, session, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, String, literal, or_

#Do before starting app
# set DATABASE_URL =
# postgres://kyxosfmrnetkpt:245cb60a39c842afaadda41435d0596bf340afcd6313107c474fdda6d357cb55@ec2-35-174-118-71.compute-1.amazonaws.com:5432/d4000k75vbnprr
# set FLASK_DEBUG=1
# set FLASK

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Create a secret key for secrets
secretKey = os.urandom(12).hex()

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = secretKey

db = SQLAlchemy(app)


#Define how database objects are stored
class Users(db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "<Username: {}>".format(self.username)

class Books(db.Model):
    __tablename__ = 'Books'

    book_id = db.Column(db.Integer, primary_key=True)
    isbn_10 = db.Column(db.String, unique=True)
    isbn_13 = db.Column(db.String, unique=True)
    title = db.Column(db.String, unique=False)
    author = db.Column(db.String, unique=False)
    year_pub = db.Column(db.Integer, unique=False)
    api_link = db.Column(db.String, unique=False)
    review_count = db.Column(db.Integer, unique=False)
    average_rating = db.Column(db.Float, unique=False)
    description = db.Column(db.String, unique=False)

    def __init__(self, isbn_10, isbn_13, title, author, year_pub, api_link, review_count, average_rating, description):
        self.isbn_10 = isbn_10
        self.isbn_13 = isbn_13
        self.title = title
        self.author = author
        self.year_pub = year_pub
        self.api_link = api_link
        self.review_count = review_count
        self.average_rating = average_rating
        self.description = description

class Reviews(db.Model):
    __tablename__ = "Reviews"

    rev_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False)
    book_id = db.Column(db.Integer, unique=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    review_text = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)

    def __init__(self, user_id, book_id, rating, review_text, username):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.review_text = review_text
        self.username = username

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    user = request.form.get("newUname")
    password = request.form.get("newPass")
    newUser = Users(user,password)
    db.session.add(newUser)
    db.session.commit()
    flash("Welcome to Buuk! Please log in to continue")

    return redirect("/")


@app.route("/login", methods=["GET","POST"])
def login():

    user = request.form.get("existingUname")
    password = request.form.get("existingPass")
    error = None

    userCheck = Users.query.filter_by(username=user).first()

    if userCheck is None:
        error = "This user doesn't exist"
    elif password != userCheck.password:
        error = "The password is incorrect"

    if error is None:
        session.clear()
        session['user_id'] = userCheck.user_id
        session['username'] = userCheck.username
        error = "Logged in successfully as " + userCheck.username + ". Book searching has now been enabled"


    flash(error)

    #Reset forms to prevent duplicate data posts
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have sucessfully logged out.")
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
def search():
    qry = str(request.form.get("searchText"))

    results = Books.query.filter((Books.isbn_10.contains(qry)) | (Books.isbn_13.contains(qry)) | (Books.title.contains(qry)) | (Books.author.contains(qry))).all()
    selection = results

    return render_template("index.html", query=qry, selection=selection)


@app.route("/api/<string:isbn>", methods = ["GET", "POST"])
def api(isbn):
    current_book = Books.query.filter(Books.isbn_10.like(isbn)).first()
    if current_book==None:
        return render_template("404.html")

    book = {
        "title": current_book.title,
        "author": current_book.author,
        "year": current_book.year_pub,
        "isbn_10": current_book.isbn_10,
        "isbn_13": current_book.isbn_13,
        "review_count": current_book.review_count,
        "average_score": current_book.average_rating
    }

    api = json.dumps(book)

    return render_template("api.json", api=api)

@app.route('/book/<string:isbn>', methods = ["GET", "POST"])
def book_page(isbn):

    current_book = Books.query.filter(Books.isbn_10.contains(isbn)).first()
    bookID = int(current_book.book_id)

    average_rating = current_book.average_rating
    ratings_count = current_book.review_count
    #allReviews = Reviews.query.filter(Reviews.book_id.contains(bookID)).all()
    allReviews = Reviews.query.filter_by(book_id=bookID).all()

    hasReviewed = False

    if not session.get('user_id'):
        return render_template("index.html")

    if request.method=="POST":
        #check_review = Reviews.query.filter(Reviews.user_id.like(session.get('user_id')), Reviews.book_id.like(bookID)).first()
        for x in allReviews:
            if x.user_id == session.get('user_id') and x.book_id == current_book.book_id:
                hasReviewed = True

        if not hasReviewed:
            text = request.form.get("reviewText")
            rating = int(request.form.get("rating"))

            newReview = Reviews(session.get('user_id'), bookID, rating, text, session.get('username'))

            db.session.add(newReview)
            db.session.commit()

            flash('Review successfully submitted!')

            allReviews.append(newReview)

            return render_template("book.html", current_book=current_book, average_rating=average_rating, ratings_count=ratings_count, allReviews=allReviews, hasReviewed=hasReviewed)
        else:
            hasReviewed = True
            flash('You already have a review for this book')
            return render_template("book.html", current_book=current_book, average_rating=average_rating, ratings_count=ratings_count, allReviews=allReviews, hasReviewed=hasReviewed)

    return render_template("book.html", current_book=current_book, average_rating=average_rating, ratings_count=ratings_count, allReviews=allReviews, hasReviewed=hasReviewed)

@app.route('/reset')
def reset():
    return render_template("index.html", query=qry, selection=selection)
