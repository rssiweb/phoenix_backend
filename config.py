import os

# Statement for enabling the development environment
DEBUG = os.getenv('DEBUG', False)

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

SQLALCHEMY_TRACK_MODIFICATIONS = True

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = os.getenv('CSRF_SESSION_KEY', 'abra-kadabra')

# Secret key for signing cookies
SECRET_KEY = os.getenv('SECRET_KEY', 'abra-kadabra')

BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 10))

# default token life to 2 hours
TOKEN_LIFESPAN_SEC = int(os.getenv('TOKEN_LIFESPAN_SEC', 7200))

REPORT_FOLDER = os.getenv('REPORT_FOLDER', 'gen/reports')

REDISTOGO_URL = os.getenv('REDISTOGO_URL')  # default value added for worker process to run
RQ_REDIS_URL = REDISTOGO_URL

SENDGRID_USERNAME = os.getenv('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.getenv('SENDGRID_PASSWORD')
SENDGRID_DISPLAYNAME = os.getenv('SENDGRID_DISPLAYNAME', 'RSSI Mailer')


MARKSHEET_TEMPLATE = os.getenv('MARKSHEET_TEMPLATE')

BASE_REPORT_PATH = os.path.join('gen', 'reports')
