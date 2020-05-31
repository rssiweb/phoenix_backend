from zipfile import ZipFile
from operator import methodcaller
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail, Attachment, To, FileContent, FileName, FileType, Disposition, ContentId

import logging as logger
import base64
import itertools
import csv
import os


class JobMeta(object):
    owner = None


def zipFiles(filenames, name="zipped.zip", deleteAfterZip=True):
    ext = ".zip"
    _, name = os.path.split(name)
    if not name.endswith(ext):
        name += ext
    base_report_path = current_app.config.get("BASE_REPORT_PATH")
    filename = os.path.join(base_report_path, str(name))
    with ZipFile(filename, "w") as myzip:
        for fname in filenames:
            logger.info("zipping %s...", fname)
            _, name = os.path.split(fname)
            myzip.write(fname, name)
    logger.info("zip created %s...", filename)
    if deleteAfterZip:
        for fname in filenames:
            logger.info("deleteing %s...", fname)
            os.remove(fname)
    return filename


def writeDictToCsv(
    headers, listOfDict, name, order_by=None, reverse=False, sub_headers=None
):
    ext = ".csv"
    name = str(name)
    if not name.endswith(ext):
        name += ext
    base_report_path = current_app.config.get("BASE_REPORT_PATH")
    filename = os.path.join(base_report_path, str(name))
    logger.info("writing to csv %s...", filename)
    content = list(listOfDict)
    if order_by and order_by in headers:
        content.sort(key=methodcaller("get", order_by), reverse=reverse)
    with open(filename, "w") as csvfile:
        reportwriter = csv.DictWriter(
            csvfile,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            fieldnames=headers,
        )
        reportwriter.writeheader()
        if not sub_headers:
            sub_headers = []
        for row in itertools.chain(sub_headers, content):
            reportwriter.writerow(row)
    logger.info("written %s lines to csv %s", len(content), filename)
    return filename


def build_attachment(attachmentFileName, mimetype):
    """Build attachment mock."""
    if not os.path.exists(attachmentFileName):
        logger.error("cannot open attachment %s", attachmentFileName)
        return None
    _, name = os.path.split(attachmentFileName)
    attachment = Attachment()
    attachment.file_content = FileContent(base64.b64encode(open(attachmentFileName, "rb").read()).decode())
    attachment.file_type = FileType(mimetype)
    attachment.file_name = FileName(name)
    attachment.disposition = Disposition("attachment")
    attachment.content_id = ContentId("Custom Report")
    return attachment


def send_report_email(
    subject, to, body, attachFileName=None, mimetype="application/pdf"
):
    """Minimum required to send an email"""
    username = current_app.config.get("SENDGRID_USERNAME")
    display_name = current_app.config.get("SENDGRID_DISPLAYNAME")
    from_email = Email(username, display_name)
    to_email = To(to)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)
    attachment = build_attachment(attachFileName, mimetype)
    if attachment:
        mail.attachment = attachment
    sg = SendGridAPIClient()
    body = mail.get()
    print(body)
    response = None
    try:
        response = sg.client.mail.send.post(request_body=body)
    except Exception as ex:
        print(ex)
    return response
