from flask import request, Blueprint, send_from_directory
from app import db, jsonify, bcrypt
from app.models import Faculty, Student, Attendance, Branch, Category
from datetime import datetime
from app.utils import decorators, parseDate, isValidPassword
from app.utils import report
from sqlalchemy import or_

examapi = Blueprint('examapi', __name__, url_prefix='/api/exam')


@examapi.route('/', methods=['GET'])
def donothing():
    return 'haha'
