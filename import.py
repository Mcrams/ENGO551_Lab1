import os
import webbrowser
import requests
import csv

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, String, Float

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


def get_attribute(data, attribute, default_value):
    return data.get(attribute) or default_value


@app.route('/')
def index():
    with open('books.csv', 'r') as csvfile:
        bookItems = csv.reader(csvfile,delimiter=",")

        lineCount = 1

        for row in bookItems:
            #Skip over headers
            if lineCount == 1:
                lineCount += 1
            else:
                # Set variables from CSV
                isbn_10 = row[0]
                title = row[1]
                author = row[2]
                year_pub = row[3]

                getURL = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn_10 + "&key=AIzaSyBT8mq4H2KsOKCNw2dW_FBB1Own_LftDbw"

                #Execute JSON request
                res = requests.get(getURL)
                book = res.json()

                #average rating
                if res.status_code == 200:
                    if get_attribute(book, 'items', 0) == 0:
                        rating = 0
                        api_link = None
                        rateCount = 0
                        description = 'No description was found for this book.'
                    else:
                        rating = get_attribute(book['items'][0]['volumeInfo'],'averageRating',0)
                        api_link = get_attribute(book['items'][0],'selfLink',None)
                        rateCount = get_attribute(book['items'][0]['volumeInfo'],'ratingsCount',0)
                        description = get_attribute(book['items'][0]['volumeInfo'],'description','No description was found for this book.')

                        if get_attribute(book['items'][0]['volumeInfo'],'industryIdentifiers', 0) == 0:
                            isbn_13 = "Not Found"
                        else:
                            # Loop through book entries that have multiple identifiers and find ISBN-13
                            identifiers = book['items'][0]['volumeInfo']['industryIdentifiers']
                            # Default value for no ISBN-13
                            isbn_13 = "Not Found"
                            #Loop through all identifiers and overwrite with ISBN-13 value if found
                            for ids in identifiers:
                                if ids['type'] == 'ISBN_13':
                                    isbn_13 = ids['identifier']

                    bookRow = Books(isbn_10, isbn_13, title, author, year_pub, api_link, rateCount, rating, description)
                    #booksToAdd.append(bookRow)
                    db.session.add(bookRow)
                    db.session.commit()

                lineCount += 1

    return "Book Import Successful"

if __name__ == '__main__':
    app.run()
