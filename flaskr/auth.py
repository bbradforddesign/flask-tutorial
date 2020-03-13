# handles authentication related tasks
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creates blueprint named auth, defined at __name__. url_prefix prepended to all associated URLS
bp = Blueprint('auth', __name__, url_prefix='/auth')

# associates /register with register view function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # if submitted form, method will be POST. start validation
    if request.method == 'POST':
        # map submitted form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validates that username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password: 
            error = 'Password is required.'
        # validate that username is not already registered
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # if validation succeeds, insert new user data into db
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # stores messages to be retrieved when rendering template
        flash(error)

    # renders HTML template
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # query user first. store in variable for later use
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # hash submitted password, and verify match with stored password
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is an object that stores data across requests. 
            # make way for new data
            session.clear()
            # store user's id as user_id in cookie for use across subsequent requests
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# register function that runs before view function
@bp.before_app_request
def load_logged_in_user():
    # checks if user_id is stored in session
    user_id = session.get('user_id')

    # if no user_id, then set g.user to None
    if user_id is None:
        g.user = None
    else: 
        # if user_id is stored, retrieve that user's data from the database. store on g.user
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# to log out, remove user id from session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# creating, editing, and deleting posts require users to be logged in.
# use when writing views requiring login
# returns new view function wrapping original view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # checks if user is loaded. redirects to login page if not
        if g.user is None:
            return redirect(url_for('auth.login'))

        # if user is loaded, call original view. proceed as normal
        return view(**kwargs)

    return wrapped_view