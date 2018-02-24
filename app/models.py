import jwt
from app import db, app, bcrypt
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship, backref


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class User(Base):
    __abstract__ = True

    name = db.Column(db.String(128))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        return dict(name=self.name)


class Faculty(User):
    __tablename__ = 'faculty'

    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean(), default=False)

    def __init__(self, name, email, password):
        super(Faculty, self).__init__(name)
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def __repr__(self):
        return '<Faculty %r>' % self.name

    def serialize(self):
        return dict(id=self.id,
                    name=self.name,
                    email=self.email,
                    admin=self.admin,
                    )

    @staticmethod
    def encode_auth_token(email):
        """
        Generates the Auth Token
        :return: string
        """
        token_life = app.config.get('TOKEN_LIFESPAN_SEC')
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=token_life),
            'iat': datetime.utcnow(),
            'sub': email
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']


class Student(User):
    __tablename__ = 'student'

    student_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date(), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    branch = db.Column(db.String(50), nullable=True)

    def __init__(self, student_id, category, name=None,
                 dob=None, contact=None, branch=None):
        super(Student, self).__init__(name)
        self.student_id = student_id
        self.category = category
        if isinstance(dob, basestring):
            self.dob = datetime.strptime(dob, '%Y-%m-%d').date()
        else:
            self.dob = dob
        self.contact = contact
        self.branch = branch

    def __repr__(self):
        return '<Student %r>' % self.name

    def serialize(self):
        return dict(id=self.id,
                    name=self.name,
                    dob=self.dob,
                    category=self.category,
                    student_id=self.student_id,
                    contact=self.contact,
                    branch=self.branch,
                    )


class Attendance(Base):
    __tablename__ = 'attendance'

    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    punchIn = db.Column(db.String(50), nullable=False)
    punchOut = db.Column(db.String(50))
    comments = db.Column(db.String(100))
    location = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    student = relationship('Student', backref=backref("person", cascade="all, delete-orphan"))

    def __init__(self, date, student_id, punchIn, punchOut=None, comments=None, location=None):
        self.date = date
        self.student_id = student_id

        if punchIn:
            datetime.strptime(punchIn, '%H:%M:%S')
        self.punchIn = punchIn

        if punchOut:
            datetime.strptime(punchOut, '%H:%M:%S')
        self.punchOut = punchOut
        self.comments = comments
        self.location = location

    def serialize(self):
        return dict(id=self.id,
                    student=self.student.serialize(),
                    comments=self.comments,
                    punchIn=self.punchIn,
                    punchOut=self.punchOut)
