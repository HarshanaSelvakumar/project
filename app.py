import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
import jinja2
import markupsafe

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base model class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database to use SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///job_portal.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with extensions
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

# Add custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    result = jinja2.escape(text)
    result = result.replace('\n', markupsafe.Markup('<br>'))
    return markupsafe.Markup(result)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import routes after models are loaded
    import routes  # noqa: F401
    
    # Call the create_admin function to ensure admin user exists
    routes.create_admin()
