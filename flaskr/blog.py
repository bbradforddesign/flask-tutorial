# blog blueprint
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# verifies that user is logged in
from flaskr.auth import login_required
# allows connection to database
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# view for index
@bp.route('/')
def index():
    db = get_db()
    # show all posts, most recent first. JOIN used so that info from user table may be available
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# view for create
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # requires title for creating post
        if not title:
            error = 'Title is required.'

        # stores error in flash to be displayed
        if error is not None:
            flash(error)
        # if no errors, store created post into database. redirect user to the index
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# get post. will be called by update and delete views
def get_post(id, check_author=True):
    # get information from database about a given post
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # if post doesn't exist, return 404 message
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # if user isn't the post's original author, deny access
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# view for update
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
# id corresponds to the 'id' in the route. passes argument to be used as an int
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title: 
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# view for delete. doesn't have own template
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))