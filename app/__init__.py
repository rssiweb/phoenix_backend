from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_rq2 import RQ
import config
import os

logger = None

bcrypt = Bcrypt()
db = SQLAlchemy()
rq = RQ(default_timeout=180 * 2)
migrate = Migrate()


def create_app(config_name=None):
    global logger
    
    # Define the WSGI application object
    app = Flask(__name__)

    # Configurations
    app.config.from_object(_get_config_class(config_name))

    logger = app.logger

    # Define Database object which is imported by some modules
    bcrypt.init_app(app)
    rq.init_app(app)
    db.init_app(app)
    
    migrate.init_app(app, db)
    migrate.render_as_batch = True

    # Sample HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(dict(error=str(error))), 404


    from app.api.common import api as commonapi
    from app.api.student import api as studentapi
    from app.api.category import api as categoryapi
    from app.api.branch import api as branchapi
    from app.api.attendance import api as attendanceapi
    from app.api.subject import api as subjectapi
    from app.api.exam import api as examapi
    from app.api.test import api as testapi
    from app.api.marks import api as marksapi
    from app.api.grade import api as gradeapi
    from app.api.report import api as reportapi

    from app.api.admin.attendance import api as admin_attendanceapi
    from app.api.admin.branch import api as admin_branchapi
    from app.api.admin.category import api as admin_catapi
    from app.api.admin.faculty import api as admin_facapi
    from app.api.admin.student import api as admin_stdapi
    from app.api.admin.subject import api as admin_subapi
    from app.api.admin.exam import api as admin_examapi
    from app.api.admin.test import api as admin_testapi
    from app.api.admin.grade import api as admin_gradeapi
    from app.api.admin.marks import api as admin_marksapi
    from app.api.admin.dist_type import api as admin_dist_type

    from app.ui.controllers import ui
    from app.commands import commands


    for api in [commonapi, studentapi, categoryapi, branchapi, attendanceapi,
                examapi, subjectapi, testapi, marksapi, gradeapi, reportapi,

                admin_attendanceapi, admin_branchapi, admin_catapi, admin_facapi,
                admin_stdapi, admin_subapi, admin_examapi, admin_testapi, admin_gradeapi,
                admin_marksapi, admin_dist_type, 

                ui, commands]:
        app.register_blueprint(api)
    return app

########## Private members below

def _get_config_class(config_name=None):
    config_name = config_name and getattr(config, config_name, None)
    if not config_name:
        config_name = os.getenv('config', 'ProdConfig')
    
    config_class = getattr(config, config_name, config.ProdConfig)
    return config_class()