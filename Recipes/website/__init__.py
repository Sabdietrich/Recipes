from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from neo4j import GraphDatabase

db = SQLAlchemy()
DB_NAME = "database_local_markets.db"


NEO4J_URI = "neo4j+s://11537547.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "JuzZ2vIjLf4Kw4JVdwxIJTZcW9JshEpoomrn_QdozOc"

# Create a new Driver instance
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a senha secreta eh senhasecreta blubblub'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .ing import ing


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(ing, url_prefix='/')


    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

