from app import rq
from app.models import Student, Faculty
from app.jobs.utils import send_report_email, zipFiles

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from collections import namedtuple
from datetime import datetime
import copy
import itertools
import os
import time
import cStringIO, urllib

Person = namedtuple('Person', 'name type contact image')

CARD_BODY_STRING = 'Please find the I cards generated on {} in attachments.'
CARD_REPORT_SUBJECT = os.getenv('MARKSHEET_REPORT_SUBJECT', 'RSSI I-Cards')

@rq.job
def build_card(meta, branch_id):
    owner = meta.owner
    branch_id = int(branch_id)
    students = Student.query.filter(Student.isActive!=False, Student.branch_id==branch_id).all()
    faculties = Faculty.query.filter(Student.isActive!=False, Student.branch_id==branch_id).all()
    persons = []
    for user in itertools.chain(students, faculties):
        user_type = "Student" if isinstance(user, Student) else "Faculty"
        user_id = getattr(user, 'student_id', getattr(user, 'facultyId', '')).upper()
        persons.append(Person(user.name,
                              user_type,
                              getattr(user, 'contact', None),
                              user.image
                              ))
    card_img_files = generate_cards(persons)
    zip_filename = zipFiles(card_img_files, name='i-cards {}.zip'.format(int(time.time())), deleteAfterZip=True)
    reportTime = datetime.now().strftime('%d %b %Y %I:%M:%S %p')
    body = CARD_BODY_STRING.format(reportTime)
    to = owner.email
    send_report_email(CARD_REPORT_SUBJECT, to, body, attachFileName=zip_filename, mimetype='application/zip')


def generate_cards(persons):
    font_path = "app/static/fonts/Ubuntu-M.ttf"
    font = ImageFont.truetype(font_path, 70)
    img = Image.open("app/static/card_template.jpg")
    width, _ = img.size
    card_files = []
    for person in persons:
        try:
            dp_content = urllib.urlopen(person.image).read() if person.image else None
        except Exception as e:
            print e
            dp_content = None
        dp = Image.open(cStringIO.StringIO(dp_content)) if dp_content else None
        tmp_img = copy.copy(img)
        draw = ImageDraw.Draw(tmp_img)

        text_width, _ = draw.textsize(person.name, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1399), person.name, (0, 0, 0), font=font)

        font = ImageFont.truetype(font_path, 60)

        text_width, _ = draw.textsize(person.type, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1499), person.type, (0, 0, 0), font=font)

        font = ImageFont.truetype(font_path, 70)

        contact = person.contact if person.contact else (' ' * 20)
        number = 'Contact: +91 %10s' % str(contact)
        text_width, _ = draw.textsize(number, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1599), number, (0, 0, 0), font=font)

        if dp:
            x_off = (width - dp.size[0]) / 2
            tmp_img.paste(dp, (x_off, 855))
        
        card_filename = 'card_{}_{}.jpg'.format(person.name, int(time.time()))
        card_filepath = os.path.join('gen/reports', card_filename)
        tmp_img.save(card_filepath, quality=95)
        card_files.append(card_filepath)
    return card_files