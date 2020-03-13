# connect to database
import sqlite3

import click
# current_app is object referencing Flask application handling request, g is reusable object accessed by multiple functions
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        # establishes connection to file
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # tells connection to return rows behaving like dictionaries, eg access columns by name
        g.db.row_factory = sqlite3.Row
    
    return g.db

# checks if connection exists. if so, closes it
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # returns database connection
    db = get_db()

    # opens file relative to flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# defines command line command calling init_db and displays message
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data, and create new tables"""
    init_db()
    click.echo('Initialized the database.')

# register with the application
def init_app(app):
    # tells Flask to call function when cleaning up after returning response
    app.teardown_appcontext(close_db)
    # adds new command that can be called with flask command
    app.cli.add_command(init_db_command)