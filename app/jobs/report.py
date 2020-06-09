from app import db, rq, logger
from app.models import Student, Branch, Category, Exam, Test, Marks, Subject, Grade
from app.utils import report
from app.jobs.utils import send_report_email, writeDictToCsv, zipFiles
from app.utils import get_grades
from datetime import date, datetime
import time

import os
import os.path


EXAM_REPORT_SUBJECT = os.getenv("EXAM_REPORT_SUBJECT", "RSSI Exam Report")
ATTENDANCE_REPORT_SUBJECT = os.getenv(
    "ATTENDANCE_REPORT_SUBJECT", "RSSI Attendace Report"
)

EMAIL_BODY_STRING = "Please find the {} report generated on {} in attachments."


@rq.job
def attendance(meta, ids, categories, branches, month):
    students = (
        db.session.query(Student)
        .join(Student.category)
        .filter(Student.id.in_(ids))
        .order_by(Category.name)
        .order_by(Student.name)
        .all()
    )
    if categories:
        categories = (
            db.session.query(Category).filter(Category.id.in_(categories)).all()
        )
    else:
        categories = Category.query.all()
    if branches:
        branches = db.session.query(Branch).filter(Branch.id.in_(branches)).all()
    else:
        branches = Branch.query.all()
    reportFileName = report.buildReport(students, month, categories, branches)
    to = meta.owner.email
    reportTime = datetime.now().strftime("%b %d %I:%M %p")
    body = EMAIL_BODY_STRING.format("attendace", reportTime)
    response = send_report_email(
        ATTENDANCE_REPORT_SUBJECT, to, body, attachFileName=reportFileName
    )
    print(response)


def examToDict(exam_id):
    exam = Exam.query.get(int(exam_id))
    logger.info('converting exam "%s" to dict', exam.name)
    data = []
    test_ids = [test.id for test in exam.tests]
    std_ids = [a.student_id for a in exam.students]
    students = Student.query.filter(Student.id.in_(std_ids)).all()
    grades = Grade.query.filter_by(branch_id=exam.branch_id).all()
    sub_header = []
    sub_header_data = {
        test.cat_sub_association.subject.name: test.max_marks for test in exam.tests
    }
    sub_header_data["Category"] = "Max Marks"
    sub_header.append(sub_header_data)
    # warming up cache
    Marks.query.filter(Marks.test_id.in_(test_ids)).all()
    for std in students:
        std_data = dict()
        std_data["Name"] = std.name
        std_data["Student ID"] = std.student_id
        std_data["Category"] = std.category.name
        std_data["Age"] = (date.today() - std.dob).days / 360

        std_tests = [t for t in exam.tests if std in [a.student for a in t.students]]
        totalMarks, maxMarks = -1, 0
        for test in std_tests:
            mark = Marks.query.filter(
                Marks.test_id == test.id, Marks.student_id == std.id
            ).first()
            maxMarks += test.max_marks
            if mark:
                if totalMarks == -1:
                    totalMarks = 0
                sub = test.cat_sub_association.subject
                std_data[sub.name] = mark.marks
                totalMarks += mark.marks
        std_data["Total"] = totalMarks if totalMarks > -1 else None
        std_data["Max Marks"] = maxMarks
        if totalMarks > -1:
            percent = float("%.2f" % (float(totalMarks) / maxMarks * 100))
            std_data["Percentage"] = percent
            grade = get_grades(percent, grades)
            std_data["Grade"] = grade.grade
            std_data["Grade Description"] = grade.comment
        data.append(std_data)
    logger.info("converted %s students result to dict", len(data))
    return data, sub_header


def getExamDictFor(catName, examDict):
    data = []
    for row in examDict:
        if row["Category"] == catName:
            data.append(row)
    return data


@rq.job
def exam_report(meta, exam_id):
    owner = meta.owner
    exam = Exam.query.get(exam_id)
    subs = [test.cat_sub_association.subject for test in exam.tests]
    data, sub_headers = examToDict(exam.id)
    header = [
        "Category",
        "Student ID",
        "Name",
        "Age",
    ]
    header.extend(set([sub.name for sub in subs]))
    header.append("Total")
    header.append("Max Marks")
    header.append("Percentage")
    header.append("Grade")
    header.append("Grade Description")

    csv_filenames = []

    filename = "%s All Category.csv" % exam.name
    filename = writeDictToCsv(
        header, data, filename, "Percentage", reverse=True, sub_headers=sub_headers, default_sort_value=0
    )
    csv_filenames.append(filename)
    logger.info("created report for all categories")

    filename = "%s %s_%s.zip" % (exam.name, owner.name, time.time())
    zip_filename = zipFiles(csv_filenames, name=filename)

    logger.info("sending report email to %s", owner.email)
    reportTime = datetime.now().strftime("%d %b %Y %I:%M:%S %p")
    body = EMAIL_BODY_STRING.format(exam.name, reportTime)
    to = owner.email
    send_report_email(
        EXAM_REPORT_SUBJECT,
        to,
        body,
        attachFileName=zip_filename,
        mimetype="application/zip",
    )
    os.remove(zip_filename)
