from flask import Blueprint, request, render_template, redirect, url_for
from .db import get_db
from .queries import (
    get_all_payments,
    add_payment,
    get_payment_by_id,
    update_payment,
    delete_payment,
    get_all_subscriptions
)
main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total Users
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    # Monthly Revenue
    cursor.execute("""
        SELECT SUM(payment_amount) AS monthly_revenue 
        FROM payments 
        WHERE MONTH(payment_date) = MONTH(CURDATE())
    """)
    monthly_revenue = cursor.fetchone()['monthly_revenue']

    # Total Subscriptions
    cursor.execute("SELECT COUNT(*) AS total_subscriptions FROM subscriptions")
    total_subscriptions = cursor.fetchone()['total_subscriptions']

    # Most Reviewed Movie
    cursor.execute("""
        SELECT m.title, COUNT(r.movieid) AS review_count
        FROM movies m
        JOIN ratings r ON m.movieid = r.movieid
        GROUP BY m.movieid
        ORDER BY review_count DESC
        LIMIT 1
    """)
    most_reviewed_movie = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('dashboard.html', 
                           total_users=total_users, 
                           monthly_revenue=monthly_revenue, 
                           total_subscriptions=total_subscriptions,
                           most_reviewed_movie=most_reviewed_movie)




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
    cursor.execute("""
        SELECT userid, userName, email, date_of_birth
        FROM users
        ORDER BY userid DESC;  -- Sort by userID in descending order (newest first)
    """)
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

    # Debugging output to verify fetched data
    print(f"User ID from URL: {user_id}")
    print(f"Fetched User from Database: {user}")

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

    try:
        # Delete associated ratings first
        cursor.execute("DELETE FROM ratings WHERE userID = %s", (user_id,))

        # Now delete the user
        cursor.execute("DELETE FROM users WHERE userID = %s", (user_id,))
        db.commit()

        return redirect(url_for('main.list_users'))
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {e}")
        return "An error occurred while deleting the user.", 500



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

    try:
        # Delete related payments first
        cursor.execute("DELETE FROM payments WHERE subscription_id = %s", (subscription_id,))
        
        # Now delete the subscription
        cursor.execute("DELETE FROM subscriptions WHERE subscription_id = %s", (subscription_id,))
        db.commit()

        return redirect(url_for('main.list_subscriptions'))
    except Exception as e:
        db.rollback()
        print(f"Error deleting subscription: {e}")
        return "An error occurred while deleting the subscription.", 500

# Payment Routes
@main.route('/payments')
def list_payments():
    payments = get_all_payments()
    return render_template('payments.html', title="Payments", payments=payments)

@main.route('/payments/add', methods=['GET', 'POST'])
def add_payment_route():
    if request.method == 'POST':
        payment_amount = request.form['payment_amount']
        card_no = request.form['card_no']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        subscription_id = request.form['subscription_id']  # User-selected ID from form
        add_payment(payment_amount, card_no, payment_date, payment_method, subscription_id)

        return redirect(url_for('main.list_payments'))
    
    # Fetch all subscription IDs for the dropdown
    subscriptions = get_all_subscriptions()
    return render_template('add_payment.html', title="Add Payment", subscriptions=subscriptions)

@main.route('/payments/edit/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    if request.method == 'POST':
        payment_amount = request.form['payment_amount']
        card_no = request.form['card_no']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        subscription_id = request.form['subscription_id']
        update_payment(payment_id, payment_amount, card_no, payment_date, payment_method, subscription_id)
        return redirect(url_for('main.list_payments'))

    payment = get_payment_by_id(payment_id)
    return render_template('edit_payment.html', title="Edit Payment", payment=payment)

@main.route('/payments/delete/<int:payment_id>', methods=['POST'])
def delete_payment_route(payment_id):
    delete_payment(payment_id)
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

@main.route('/reports')
def reports():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Query for Active vs. Inactive Users
    cursor.execute("""
        SELECT subscription_status, COUNT(*) AS total_users
        FROM subscriptions
        GROUP BY subscription_status;
    """)
    active_inactive_users = cursor.fetchall()

    # Query for Revenue from Subscriptions
    cursor.execute("""
        SELECT SUM(payment_amount) AS total_revenue
        FROM payments;
    """)
    revenue_from_subscriptions = cursor.fetchone()['total_revenue']

    # Query for Top-Rated Movies
    cursor.execute("""
        SELECT m.title, ROUND(AVG(r.ratingScore), 2) AS avg_rating, COUNT(r.ratingScore) AS total_ratings
        FROM movies m
        JOIN ratings r ON m.movieid = r.movieid
        GROUP BY m.movieid
        HAVING total_ratings > 5
        ORDER BY avg_rating DESC
        LIMIT 10;
    """)
    top_rated_movies = cursor.fetchall()

    # Query for Top Movies by Genre (limit 5 per genre)
    cursor.execute("""
        SELECT mg.movie_genre, m.title, ROUND(AVG(r.ratingScore), 2) AS avg_rating
        FROM movie_genre mg
        JOIN movies m ON mg.movieid = m.movieid
        JOIN ratings r ON m.movieid = r.movieid
        GROUP BY mg.movie_genre, m.movieid
        ORDER BY mg.movie_genre, avg_rating DESC;
    """)
    top_movies_by_genre_raw = cursor.fetchall()

    # Organize and limit top movies by genre
    top_movies_by_genre = {}
    for row in top_movies_by_genre_raw:
        genre = row['movie_genre']
        movie = {'title': row['title'], 'avg_rating': row['avg_rating']}
        if genre not in top_movies_by_genre:
            top_movies_by_genre[genre] = []
        if len(top_movies_by_genre[genre]) < 5:  # Limit to 5 movies per genre
            top_movies_by_genre[genre].append(movie)

    # Close connection
    cursor.close()
    db.close()

    return render_template(
        'reports.html',
        active_inactive_users=active_inactive_users,
        revenue_from_subscriptions=revenue_from_subscriptions,
        top_rated_movies=top_rated_movies,
        top_movies_by_genre=top_movies_by_genre
    )

