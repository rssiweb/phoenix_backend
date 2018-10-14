from app import db
from .base import Base
from sqlalchemy.orm import relationship, backref
from .base import Association, Branch
from datetime import datetime

class Exam(Base):
    __tablename__ = 'exam'

    name = db.Column(db.String(100), nullable=False, unique=True)
    start_date = db.Column(db.Date(), nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date(), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=True)

    tests = relationship("Test", back_populates="exam", cascade="all, delete, delete-orphan")

    students = relationship("StudentTestAssociation", cascade="all, delete, delete-orphan")

    def __init__(self, name, branch_id, start_date=None, end_date=None, state=None):
        self.name = name
        if start_date:
            self.start_date = datetime.strptime(start_date, '%d/%m/%Y')
        if end_date:
            self.end_date = datetime.strptime(end_date, '%d/%m/%Y')
        if state:
            self.state = state

        branch_id = int(branch_id)
        branch = Branch.query.get(branch_id)
        if not branch:
            raise ValueError('No Branch with id "%s" found' % branch_id)
        self.branch_id = branch.id

    def serialize(self):
        return dict(id=self.id,
                    name=self.name,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    state=self.state,
                    tests=[test.serialize() for test in self.tests],
                    students=[a.student_id for a in self.students]
                    )


class Test(Base):
    __tablename__ = 'test'

    name = db.Column(db.String(100), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    state = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date(), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    cat_sub_id = db.Column(db.Integer, db.ForeignKey('association.id'))
    evaluator_id = db.Column(db.Integer(), db.ForeignKey('faculty.id'))

    cat_sub_association = relationship("Association")
    exam = relationship("Exam", back_populates="tests")
    evaluator = relationship("Faculty")

    students = relationship("StudentTestAssociation", cascade="all, delete, delete-orphan")

    __table_args__ = (db.UniqueConstraint('name', 'exam_id', name='testcode_in_exam_uc'),)

    def __init__(self, name, max_marks, exam_id, cat_sub_id, test_date, state=None):
        self.name = name
        self.exam_id = int(exam_id)
        self.max_marks = float(max_marks)
        cat_sub_association = Association.query.filter_by(id=int(cat_sub_id)).first()
        if cat_sub_association:
            self.cat_sub_association = cat_sub_association
        if isinstance(test_date, str):
            test_date = datetime.strptime(test_date, '%d/%m/%Y')
        if isinstance(test_date, datetime) or isinstance(test_date, date):
            self.date = test_date
        if state:
            self.state = state

    def serialize(self):
        return dict(id=self.id,
                    name=self.name,
                    max_marks=self.max_marks,
                    exam_id=self.exam_id,
                    date=self.date.strftime('%d/%m/%Y'),
                    state=self.state,
                    subject=self.cat_sub_association.subject.id,
                    category=self.cat_sub_association.category.id,
                    evaluator=self.evaluator_id,
                    students=[std.student_id for std in self.students]
                    )


class StudentTestAssociation(Base):
    __tablename__ = 'std_test_association'

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)

    test = relationship("Test")
    student = relationship("Student")
    exam = relationship("Exam")

    __table_args__ = (db.UniqueConstraint('test_id', 'student_id', 'exam_id', name='std_test_uc'),)


class Grade(Base):

    lower = db.Column(db.Integer, nullable=False)
    upper = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    comment = db.Column(db.String(50), nullable=True)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('lower', 'upper', name='lower_upper_uc'),
                      db.UniqueConstraint('branch_id', 'grade', name='branch_grade_uc'))

    def __init__(self, lower, upper, grade, branch_id, comment=None):
        if lower is not None:
            self.lower = int(lower)
        if upper is not None:
            self.upper = int(upper)
        if grade and isinstance(grade, basestring):
            self.grade = grade
        if comment and isinstance(comment, basestring):
            self.comment = comment

        branch_id = int(branch_id)
        branch = Branch.query.get(branch_id)
        if not branch:
            raise ValueError('No Branch with id "%s" found' % branch_id)
        self.branch_id = branch.id

    def serialize(self):
        return dict(id=self.id,
                    min=self.lower,
                    max=self.upper,
                    grade=self.grade,
                    branch_id=self.branch_id,
                    comment=self.comment
                    )


class Marks(Base):

    marks = db.Column(db.Float, nullable=False)
    comments = db.Column(db.String(50), nullable=True)

    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('test_id', 'student_id', name='student_test_uc'),)

    def __init__(self, test_id, student_id, marks, comments=None):
        self.test_id = int(test_id)
        self.student_id = int(student_id)
        self.marks = float(marks)
        if comments:
            self.comments = str(comments)

    def serialize(self):
        return dict(id=self.id,
                    test_id=self.test_id,
                    student_id=self.student_id,
                    marks=self.marks,
                    comments=self.comments)
