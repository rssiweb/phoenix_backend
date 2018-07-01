from app import db, rq, logger
from app.models import Student, Branch, Category, Exam, Test, Marks, Subject
from app.utils import report

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail, Attachment

from datetime import date, datetime
from zipfile import ZipFile
from operator import methodcaller
from config import SENDGRID_USERNAME, SENDGRID_DISPLAYNAME
import base64
import time
import csv
import os
import os.path


BASE_REPORT_PATH = os.path.join('gen', 'reports')

EXAM_REPORT_SUBJECT = os.getenv('EXAM_REPORT_SUBJECT', 'RSSI Exam Report')
ATTENDANCE_REPORT_SUBJECT = os.getenv('ATTENDANCE_REPORT_SUBJECT', 'RSSI Attendace Report')

EMAIL_BODY_STRING = 'Please find the {} report generated on {} in attachments.'


class JobMeta(object):
    owner = None


@rq.job
def attendance(meta, ids, categories, branches, month):
    students = db.session.query(Student)\
                         .join(Student.category)\
                         .filter(Student.id.in_(ids))\
                         .order_by(Category.name)\
                         .order_by(Student.name).all()
    if categories:
        categories = db.session.query(Category)\
                               .filter(Category.id.in_(categories)).all()
    else:
        categories = Category.query.all()
    if branches:
        branches = db.session.query(Branch)\
                             .filter(Branch.id.in_(branches)).all()
    else:
        branches = Branch.query.all()
    reportFileName = report.buildReport(students, month, categories, branches)
    to = meta.owner.email
    reportTime = datetime.now().strftime('%b %d %I:%M %p')
    body = EMAIL_BODY_STRING.format('attendace', reportTime)
    response = send_report_email(ATTENDANCE_REPORT_SUBJECT, to, body, attachFileName=reportFileName)
    print response


def send_report_email(subject, to, body, attachFileName=None, mimetype="application/pdf"):
    """Minimum required to send an email"""
    from_email = Email(SENDGRID_USERNAME, SENDGRID_DISPLAYNAME)
    to_email = Email(to)
    content = Content("text/plain", body)
    mail = Mail(from_email, subject, to_email, content)
    attachment = build_attachment(attachFileName, mimetype)
    if attachment:
        mail.add_attachment(attachment)
    sg = SendGridAPIClient()
    response = sg.client.mail.send.post(request_body=mail.get())
    return response


def build_attachment(attachmentFileName, mimetype):
    """Build attachment mock."""
    if not os.path.exists(attachmentFileName):
        logger.error('cannot open attachment %s', attachmentFileName)
        return None
    _, name = os.path.split(attachmentFileName)
    attachment = Attachment()
    attachment.content = base64.b64encode(open(attachmentFileName, 'rb').read())
    attachment.type = mimetype
    attachment.filename = name
    attachment.disposition = "attachment"
    attachment.content_id = "Custom Report"
    return attachment


def examToDict(exam_id):
    exam = Exam.query.get(int(exam_id))
    logger.info('converting exam "%s" to dict', exam.name)
    data = []
    test_ids = [test.id for test in exam.tests]
    marks = Marks.query.filter(Marks.test_id.in_(test_ids)).all()
    std_ids = set([mark.student_id for mark in marks])
    students = Student.query.filter(Student.id.in_(std_ids)).all()
    for std in students:
        std_data = dict()
        std_data['Name'] = std.name
        std_data['Student ID'] = std.student_id
        std_data['Category'] = std.category.name
        std_data['Age'] = (date.today() - std.dob).days / 360

        std_marks = Marks.query.filter(Marks.test_id.in_(test_ids),
                                       Marks.student_id == std.id).all()
        sumMarks, maxMarks = 0, 0
        for mark in std_marks:
            test = Test.query.get(mark.test_id)
            sub = test.cat_sub_association.subject
            std_data[sub.name] = mark.marks
            sumMarks += mark.marks
            maxMarks += test.max_marks
        std_data['Total'] = sumMarks
        std_data['Percentage'] = float('%.2f' % (float(sumMarks) / maxMarks * 100))
        data.append(std_data)
    logger.info('converted %s students result to dict', len(data))
    return data


def writeDictToCsv(headers, listOfDict, name, order_by=None, reverse=False):
    ext = '.csv'
    name = str(name)
    if not name.endswith(ext):
        name += ext
    filename = os.path.join(BASE_REPORT_PATH, str(name))
    logger.info('writing to csv %s...', filename)
    content = list(listOfDict)
    if order_by and order_by in headers:
        content.sort(key=methodcaller('get', order_by), reverse=reverse)
    with open(filename, 'wb') as csvfile:
        reportwriter = csv.DictWriter(csvfile, delimiter=',',
                                      quotechar='"',
                                      quoting=csv.QUOTE_MINIMAL,
                                      fieldnames=headers)
        reportwriter.writeheader()
        for row in content:
            reportwriter.writerow(row)
    logger.info('written %s lines to csv %s', len(content), filename)
    return filename


def getExamDictFor(catName, examDict):
    data = []
    for row in examDict:
        if row['Category'] == catName:
            data.append(row)
    return data


@rq.job
def exam_report(meta, exam_id):
    owner = meta.owner
    exam = Exam.query.get(exam_id)
    cats = Category.query.filter_by(branch_id=exam.branch_id)
    subs = Subject.query.filter_by(branch_id=exam.branch_id)
    data = examToDict(exam.id)
    header = ['Category', 'Student ID', 'Name', 'Age', ]
    header.extend([sub.name for sub in subs])
    header.append('Total')
    header.append('Percentage')

    csv_filenames = []

    filename = '%s All Category.csv' % exam.name
    filename = writeDictToCsv(header, data, filename, 'Percentage', reverse=True)
    csv_filenames.append(filename)

    for cat in cats:
        cat_data = getExamDictFor(cat.name, data)
        filename = '%s %s.csv' % (exam.name, cat.name)
        filename = writeDictToCsv(header, cat_data, filename, 'Percentage', reverse=True)
        csv_filenames.append(filename)
    logger.info('created report for all categories')

    filename = '%s %s_%s.zip' % (exam.name, owner.name, time.time())
    zip_filename = zipFiles(csv_filenames, name=filename)

    logger.info('sending report email to %s', owner.email)
    reportTime = datetime.now().strftime('%d %b %Y %I:%M:%S %p')
    body = EMAIL_BODY_STRING.format(exam.name, reportTime)
    to = owner.email
    send_report_email(EXAM_REPORT_SUBJECT, to, body, attachFileName=zip_filename, mimetype='application/zip')
    os.remove(zip_filename)


def zipFiles(filenames, name='zipped.zip', deleteAfterZip=True):
    ext = '.zip'
    _, name = os.path.split(name)
    if not name.endswith(ext):
        name += ext
    filename = os.path.join(BASE_REPORT_PATH, str(name))
    with ZipFile(filename, 'w') as myzip:
        for fname in filenames:
            logger.info('zipping %s...', fname)
            _, name = os.path.split(fname)
            myzip.write(fname, name)
    logger.info('zip created %s...', filename)
    if deleteAfterZip:
        for fname in filenames:
            logger.info('deleteing %s...', fname)
            os.remove(fname)
    return filename
