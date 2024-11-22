from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db

main = Blueprint('main', __name__)

@main.route('/')
def dashboard(): # Display the admin dashboard.
    return render_template('dashboard.html', title="Admin Dashboard")


@main.route('/movies')
def list_movies(): # Display a list of all movies.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT movieid, title, release_date, duration, description FROM movies")
    movies = cursor.fetchall()
    return render_template('movies.html', movies=movies)


@main.route('/subscriptions')
def list_subscriptions():  # Display a list of all Subscriptions.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT subscription_id, userID, startdate, end_Date, subscription_status FROM subscriptions")
    subscriptions = cursor.fetchall()
    return render_template('subscriptions.html', subscriptions=subscriptions)


@main.route('/payments')
def list_payments(): # Display a list of all payments.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT payment_id, payment_amount, card_no, payment_date, payment_method, subscription_id FROM payments")
    payments = cursor.fetchall()
    return render_template('payments.html', payments=payments)


@main.route('/ratings')
def list_ratings():  # Display a list of all ratings.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT userID, movieid, ratingScore, review, ratingDate FROM ratings")

    ratings = cursor.fetchall()
    return render_template('ratings.html', ratings=ratings)

@main.route('/genres')
def list_genres(): # Display a list of genres.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT movie_genre, movieid FROM movie_genre")
    genres = cursor.fetchall()
    return render_template('genres.html', genres=genres)

@main.route('/users')
def list_users(): # Display a list of users.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT userID, userName, email, date_of_birth FROM users")
    users = cursor.fetchall()
    return render_template('users.html', users=users)



@main.route('/reports')
def list_reports(): # Display reports, for now a list of movies and ratings.
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Report query for best 5 Movies
    cursor.execute("""
        SELECT title, AVG(ratingScore) AS avg_rating
        FROM ratings
        JOIN movies ON ratings.movieid = movies.movieid
        GROUP BY ratings.movieid
        ORDER BY avg_rating DESC
        LIMIT 5
    """)
    top_movies = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_subscriptions FROM subscriptions")
    total_subscriptions = cursor.fetchone()

    return render_template(
        'reports.html', 
        top_movies=top_movies, 
        total_subscriptions=total_subscriptions
    )
