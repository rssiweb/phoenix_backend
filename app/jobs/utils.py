from zipfile import ZipFile
from operator import methodcaller
from config import SENDGRID_USERNAME, SENDGRID_DISPLAYNAME
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail, Attachment
from config import BASE_REPORT_PATH

import logging as logger
import base64
import itertools
import csv
import os


class JobMeta(object):
    owner = None


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


def writeDictToCsv(headers, listOfDict, name, order_by=None, reverse=False, sub_headers=None):
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
        if not sub_headers:
            sub_headers = []
        for row in itertools.chain(sub_headers, content):
            reportwriter.writerow(row)
    logger.info('written %s lines to csv %s', len(content), filename)
    return filename


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
