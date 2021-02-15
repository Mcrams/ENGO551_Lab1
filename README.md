# Project 1

## ENGO 551 - Lab 1

Online Book Review System using Python, Flask, PostGreSQL, and SQLAlchemy

## Instructions
1. Install both Python and pip before starting
2. To get this project running, navigate to the project folder in a terminal window and run the following commands in order (Windows):
`pip install -r requirements.txt`
`set DATABASE_URL=postgres://kyxosfmrnetkpt:245cb60a39c842afaadda41435d0596bf340afcd6313107c474fdda6d357cb55@ec2-35-174-118-71.compute-1.amazonaws.com:5432/d4000k75vbnprr`
`set FLASK_APP=application.py`
`set FLASK_DEBUG=1`
`python -m flask run`

3. Navigate to 127.0.0.1:5000 on a web browser.
4. The project is now running!

***

## Project Files
### application.py
Main Python file for app, contains all database models and site-essential functions such as login, registration, and book searching.

### import.py
Standalone Python program to import the book list from books.csv into the database. This has already been run for the connected database.

### templates/index.html
Main landing page of the site. Contains the login, registration and search functionality of the site.

### templates/book.html
Page template for showing individual books and their associated reviews. Also allows for posting reviews

### templates/404.html
For items not found.

### templates/api.json
Outputs a JSON string if the user runs a GET request by going to /api/isbn_10, where isbn_10 is a 10-digit isbn code for a book in the database. Outputs to 404.html if not found
