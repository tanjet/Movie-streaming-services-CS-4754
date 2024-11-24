from flask import Blueprint, request, render_template, redirect, url_for
from .db import get_db

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    return render_template('dashboard.html', title="Admin Dashboard")


# Movie Routes
@main.route('/movies') 
def list_movies():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT movieid, title, release_date, duration, description FROM movies")
    movies = cursor.fetchall()
    return render_template('movies.html', movies=movies)

@main.route('/movies/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        release_date = request.form['release_date']
        duration = request.form['duration']
        description = request.form['description']

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO movies (title, release_date, duration, description) VALUES (%s, %s, %s, %s)",
            (title, release_date, duration, description)
        )
        db.commit()
        return redirect(url_for('main.list_movies'))

    return render_template('add_movie.html', title="Add Movie")

@main.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        release_date = request.form['release_date']
        duration = request.form['duration']
        description = request.form['description']
        cursor.execute(
            "UPDATE movies SET title=%s, release_date=%s, duration=%s, description=%s WHERE movieid=%s",
            (title, release_date, duration, description, movie_id)
        )
        db.commit()
        return redirect(url_for('main.list_movies'))

    cursor.execute("SELECT * FROM movies WHERE movieid = %s", (movie_id,))
    movie = cursor.fetchone()
    return render_template('edit_movie.html', title="Edit Movie", movie=movie)

@main.route('/movies/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM movies WHERE movieid=%s", (movie_id,))
    db.commit()
    return redirect(url_for('main.list_movies'))


# User Routes
@main.route('/users')
def list_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT userid, userName, email, password, date_of_birth FROM users")
    users = cursor.fetchall()
    return render_template('users.html', title="Users", users=users)

@main.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        userName = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        date_of_birth = request.form['date_of_birth']

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (userName, email, password, date_of_birth) VALUES (%s, %s, %s, %s)",
            (userName, email, password, date_of_birth)
        )
        db.commit()
        return redirect(url_for('main.list_users'))

    return render_template('add_user.html', title="Add User")

@main.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch user data
    cursor.execute("SELECT * FROM users WHERE userID = %s", (user_id,))
    user = cursor.fetchone()

    # Handle case where the user is not found
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        # Get data from form
        userName = request.form.get('userName')
        email = request.form.get('email')
        password = request.form.get('password')
        date_of_birth = request.form.get('date_of_birth')

        # Validate input fields
        if not all([userName, email, password, date_of_birth]):
            return "All fields are required", 400

        # Update the user in the database
        cursor.execute(
            """
            UPDATE users
            SET userName = %s, email = %s, password = %s, date_of_birth = %s
            WHERE userID = %s
            """,
            (userName, email, password, date_of_birth, user_id)
        )
        db.commit()
        return redirect(url_for('main.list_users'))

    return render_template('edit_user.html', title="Edit User", user=user)




@main.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE userID=%s", (user_id,))
    db.commit()
    return redirect(url_for('main.list_users'))


# Genre Routes
@main.route('/genres')
def list_genres():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT mg.movieid, m.title, mg.movie_genre
        FROM movie_genre mg
        JOIN movies m ON mg.movieid = m.movieid
    """)
    genres = cursor.fetchall()
    return render_template('genres.html', title="Genres", genres=genres)


@main.route('/genres/add', methods=['GET', 'POST'])
def add_genre():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        movieid = request.form['movieid']
        movie_genre = request.form['movie_genre']
        cursor.execute("INSERT INTO movie_genre (movieid, movie_genre) VALUES (%s, %s)", (movieid, movie_genre))
        db.commit()
        return redirect(url_for('main.list_genres'))

    # Fetch movies for the dropdown
    cursor.execute("SELECT movieid, title FROM movies")
    movies = cursor.fetchall()
    return render_template('add_genre.html', title="Add Genre", movies=movies)

@main.route('/genres/edit/<int:movieid>/<string:movie_genre>', methods=['GET', 'POST'])
def edit_genre(movieid, movie_genre):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        new_genre = request.form['movie_genre']
        cursor.execute(
            "UPDATE movie_genre SET movie_genre=%s WHERE movieid=%s AND movie_genre=%s",
            (new_genre, movieid, movie_genre)
        )
        db.commit()
        return redirect(url_for('main.list_genres'))

    # Fetch the current genre and movie details
    cursor.execute("""
        SELECT mg.movieid, m.title, mg.movie_genre
        FROM movie_genre mg
        JOIN movies m ON mg.movieid = m.movieid
        WHERE mg.movieid=%s AND mg.movie_genre=%s
    """, (movieid, movie_genre))
    genre_entry = cursor.fetchone()
    return render_template('edit_genre.html', title="Edit Genre", genre_entry=genre_entry)



@main.route('/genres/delete/<int:movieid>/<string:movie_genre>', methods=['POST'])
def delete_genre(movieid, movie_genre):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM movie_genre WHERE movieid=%s AND movie_genre=%s", (movieid, movie_genre))
    db.commit()
    return redirect(url_for('main.list_genres'))

@main.route('/subscriptions')
def list_subscriptions():  # Display a list of all Subscriptions.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT subscription_id, userID, startdate, end_Date, subscription_status FROM subscriptions")
    subscriptions = cursor.fetchall()
    return render_template('subscriptions.html', subscriptions=subscriptions)

@main.route('/subscriptions/add', methods=['GET', 'POST'])
def add_subscription(): # add a new subscription to the database
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Retrieve form data
        userID = request.form['userID']
        startdate = request.form['startdate']
        end_date = request.form['end_Date']
        subscription_status = request.form['subscription_status']

        try:
            # Insert the subscription into the database
            cursor.execute("""
                INSERT INTO subscriptions (userID, startdate, end_Date, subscription_status)
                VALUES (%s, %s, %s, %s)
            """, (userID, startdate, end_date, subscription_status))
            db.commit()

            # Redirect to the subscriptions list page after successful insertion
            return redirect(url_for('main.list_subscriptions'))
        except Exception as e:
            db.rollback()
            print(f"Error adding subscription: {e}")
            return "An error occurred while adding the subscription.", 500

    # Fetch users for the dropdown menu
    cursor.execute("SELECT userID, userName FROM users")
    users = cursor.fetchall()

    # Render the add_subscription.html template for GET requests
    return render_template('add_subscription.html', users=users)

@main.route('/subscriptions/edit/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch subscription details
    cursor.execute("SELECT * FROM subscriptions WHERE subscription_id = %s", (subscription_id,))
    subscription = cursor.fetchone()

    if not subscription:
        return "Subscription not found", 404

    if request.method == 'POST':
        userID = request.form['userID']
        startdate = request.form['startdate']
        end_date = request.form['end_Date']
        subscription_status = request.form['subscription_status']

        cursor.execute(
            """
            UPDATE subscriptions
            SET userID = %s, startdate = %s, end_Date = %s, subscription_status = %s
            WHERE subscription_id = %s
            """,
            (userID, startdate, end_date, subscription_status, subscription_id)
        )
        db.commit()
        return redirect(url_for('main.list_subscriptions'))

    return render_template('edit_subscription.html', title="Edit Subscription", subscription=subscription)

@main.route('/subscriptions/delete/<int:subscription_id>', methods=['POST'])
def delete_subscription(subscription_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE subscription_id = %s", (subscription_id,))
    db.commit()
    return redirect(url_for('main.list_subscriptions'))

@main.route('/payments', methods=['GET', 'POST'])
def list_payments(): # Display a list of payments from the database
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch payment data
    cursor.execute("""
        SELECT p.payment_id, p.payment_amount, p.card_no, p.payment_date, p.payment_method, s.subscription_id
        FROM payments p
        JOIN subscriptions s ON p.subscription_id = s.subscription_id
    """)
    payments = cursor.fetchall()

    # Render the payments.html template
    return render_template('payments.html', payments=payments)

@main.route('/payments/add', methods=['GET', 'POST'])
def add_payment(): # Route to add a new payment to the database.
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Get form data
        payment_amount = request.form['payment_amount']
        card_no = request.form['card_no']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        subscription_id = request.form['subscription_id']

        try:
            # Insert data into the payments table
            cursor.execute("""
                INSERT INTO payments (payment_amount, card_no, payment_date, payment_method, subscription_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (payment_amount, card_no, payment_date, payment_method, subscription_id))
            db.commit()

            # Redirect to the payments list page after success
            return redirect(url_for('main.list_payments'))
        except Exception as e:
            db.rollback()
            print(f"Error adding payment: {e}")
            return "An error occurred while adding the payment.", 500

    # Fetch subscriptions for the dropdown menu
    cursor.execute("SELECT subscription_id FROM subscriptions")
    subscriptions = cursor.fetchall()

    # Render the add_payment.html template for GET requests
    return render_template('add_payment.html', subscriptions=subscriptions)

@main.route('/payments/edit/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch payment details
    cursor.execute("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
    payment = cursor.fetchone()

    if not payment:
        return "Payment not found", 404

    if request.method == 'POST':
        payment_amount = request.form['payment_amount']
        card_no = request.form['card_no']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        subscription_id = request.form['subscription_id']

        cursor.execute(
            """
            UPDATE payments
            SET payment_amount = %s, card_no = %s, payment_date = %s, payment_method = %s, subscription_id = %s
            WHERE payment_id = %s
            """,
            (payment_amount, card_no, payment_date, payment_method, subscription_id, payment_id)
        )
        db.commit()
        return redirect(url_for('main.list_payments'))

    return render_template('edit_payment.html', title="Edit Payment", payment=payment)

@main.route('/payments/delete/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
    db.commit()
    return redirect(url_for('main.list_payments'))


@main.route('/ratings')
def list_ratings():  # Display a list of all ratings.
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT userID, movieid, ratingScore, review, ratingDate FROM ratings")

    ratings = cursor.fetchall()
    return render_template('ratings.html', ratings=ratings)

@main.route('/ratings/add', methods=['GET', 'POST'])
def add_rating(): # add new rating to the database.
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Get form data
        userID = request.form['userID']
        movieID = request.form['movieID']
        ratingScore = request.form['ratingScore']
        review = request.form['review']
        ratingDate = request.form['ratingDate']

        # Insert data into the ratings table
        cursor.execute("""
            INSERT INTO ratings (userID, movieID, ratingScore, review, ratingDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (userID, movieID, ratingScore, review, ratingDate))
        db.commit()

        # Redirect to the ratings list page
        return redirect(url_for('main.list_ratings'))

    # Fetch users and movies for dropdowns
    cursor.execute("SELECT userid, username FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT movieid, title FROM movies")
    movies = cursor.fetchall()

    # Render the add_rating.html template for GET requests
    return render_template('add_rating.html', users=users, movies=movies)

@main.route('/ratings/edit/<int:movie_id>/<int:user_id>', methods=['GET', 'POST'])
def edit_rating(movie_id, user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch rating details
    cursor.execute("SELECT * FROM ratings WHERE movieid = %s AND userID = %s", (movie_id, user_id))
    rating = cursor.fetchone()

    if not rating:
        return "Rating not found", 404

    if request.method == 'POST':
        ratingScore = request.form['ratingScore']
        review = request.form['review']
        ratingDate = request.form['ratingDate']

        cursor.execute(
            """
            UPDATE ratings
            SET ratingScore = %s, review = %s, ratingDate = %s
            WHERE movieid = %s AND userID = %s
            """,
            (ratingScore, review, ratingDate, movie_id, user_id)
        )
        db.commit()
        return redirect(url_for('main.list_ratings'))

    return render_template('edit_rating.html', title="Edit Rating", rating=rating)


@main.route('/ratings/delete/<int:movie_id>/<int:user_id>', methods=['POST'])
def delete_rating(movie_id, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ratings WHERE movieid = %s AND userID = %s", (movie_id, user_id))
    db.commit()
    return redirect(url_for('main.list_ratings'))
