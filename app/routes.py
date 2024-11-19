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

    if request.method == 'POST':
        userName = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        date_of_birth = request.form['date_of_birth']
        cursor.execute(
            "UPDATE users SET userName=%s, email=%s, password=%s, date_of_birth=%s WHERE userid=%s",
            (userName, email, password, date_of_birth, user_id)
        )
        db.commit()
        return redirect(url_for('main.list_users'))

    cursor.execute("SELECT * FROM users WHERE userid = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('edit_user.html', title="Edit User", user=user)

@main.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE userid=%s", (user_id,))
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



@main.route('/genres/delete/<int:movieid>/<string:genre>', methods=['POST'])
def delete_genre(movieid, genre):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM movie_genre WHERE movieid=%s AND genre=%s", (movieid, genre))
    db.commit()
    return redirect(url_for('main.list_genres'))




