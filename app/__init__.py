from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Define the WSGI application object
app = Flask(__name__)

bcrypt = Bcrypt(app)


# Configurations
app.config.from_object('config')

# Define Database object which is imported by some modules
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify(dict(error=str(error))), 404

from app.api.controllers import mod_api as api_module
from app.ui.controllers import mod_ui as ui_module

app.register_blueprint(api_module)
app.register_blueprint(ui_module)

db.create_all()
