from app import rq
from app.models import Student, Faculty

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from collections import namedtuple
import copy
import itertools
import os

Person = namedtuple('Person', 'name type contact image')


@rq.job
def build_card(meta, branch_id):
    branch_id = int(branch_id)
    students = Student.query.filter(Student.isActive!=False, Student.branch_id==branch_id).all()
    faculties = Faculty.query.filter(Student.isActive!=False, Student.branch_id==branch_id).all()
    persons = []
    f_contacts = {
    'VLKO17001': '9831233994',
    'VLKO17002': '8267927080',
    'VLKO17003': '8574143794',
    'VLKO17004': '9456649746',
    'VLKO17005': '9176075155',
    'VLKO18006': '7044064067',
    'VLKO18007': '8726535702',
    'VLKO18008': '8765339655',
    'VLKO18009': '9458761831',
    'VLKO18010': '8318597683',
    'VLKO18011': '8009959431',
    'VLKO18012': '8932061116',
    'VLKO18013': '9918868804',
    }
    for user in itertools.chain(students, faculties):
        user_type = "Student" if isinstance(user, Student) else "Faculty"
        user_id = getattr(user, 'student_id', getattr(user, 'facultyId', '')).upper()
        persons.append(Person(user.name,
                              user_type,
                              getattr(user, 'contact', f_contacts.get(user_id, '          ')),
                              'app/static/img/user/{}.jpg'.format(user_id)
                              ))
    generate_cards(persons)


def generate_cards(persons):
    font_path = "app/static/fonts/Ubuntu-M.ttf"
    font = ImageFont.truetype(font_path, 70)
    img = Image.open("app/static/card_template.jpg")
    width, _ = img.size

    for person in persons:
        dp = Image.open(person.image) if os.path.exists(person.image) else None

        tmp_img = copy.copy(img)
        draw = ImageDraw.Draw(tmp_img)

        text_width, _ = draw.textsize(person.name, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1334), person.name, (0, 0, 0), font=font)

        font = ImageFont.truetype(font_path, 60)

        text_width, _ = draw.textsize(person.type, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1434), person.type, (0, 0, 0), font=font)

        font = ImageFont.truetype(font_path, 70)

        number = 'Contact: +91 ' + person.contact
        text_width, _ = draw.textsize(number, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 1534), number, (0, 0, 0), font=font)

        if dp:
            x_off = (width - dp.size[0]) / 2
            tmp_img.paste(dp, (x_off, 790))

        tmp_img.save('gen/id_cards/%s_card.jpg' % person.name)
