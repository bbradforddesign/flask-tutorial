import os

from flask import Flask
# application factory
def create_app(test_config=None):
    # create Flask instance
    app = Flask(__name__, instance_relative_config=True)
    # sets default configs
    app.config.from_mapping(
        # secures data. replace with random when deployed
        SECRET_KEY='dev',
        # path of SQLite db file
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # overrides default config with config.py
        app.config.from_pyfile('config.py', silent=True)
    else:
        # set default config from test_config
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        # makes sure that app.instance_path exists
        os.makedirs(app.instance_path)
    except OSError:
        # otherwise, skip
        pass

    # maps address '/hello' to function hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # import function from db.py
    from . import db
    db.init_app(app) 

    # import auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # import blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    # since blog is the main feature, no prefix is needed
    app.add_url_rule('/', endpoint='index')

    return app