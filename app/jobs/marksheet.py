from app import rq
from app.models import Student, Exam, Marks, Grade, Attendance
from app.jobs.utils import send_report_email, zipFiles
from app.utils import get_grades
from datetime import datetime
from operator import methodcaller


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import copy
import os


MARKSHEET_BODY_STRING = 'Please find the marksheets for {} generated on {} in attachments.'
MARKSHEET_REPORT_SUBJECT = os.getenv('MARKSHEET_REPORT_SUBJECT', 'RSSI Marksheets')

font_filename = 'app/static/fonts/Roboto-Medium.ttf'
bold_font_filename = 'app/static/fonts/Roboto-Black.ttf'

font_size = 40
font = ImageFont.truetype(font_filename, font_size) if font_filename else None
bold_font = ImageFont.truetype(bold_font_filename, font_size) if font_filename else None
txt_rgb = (91, 91, 91)

sub_in_template_order = 'english maths generalscience drawing_handwriting computer'.split()


def get_subject_order(sub):
    # TODO delete this sorting logic
    name = sub.get('name', '')
    name = name.lower().strip()
    if name == 'english':
        return 1
    elif name == 'maths':
        return 2
    elif name == 'computer':
        return 3
    elif name == 'gk':
        return 4
    elif name == 'drawing':
        return 5
    elif name == 'handwriting':
        return 6


def exam_to_dict(examid, att_start, att_end):
    exam = Exam.query.get(int(examid))
    test_ids = [test.id for test in exam.tests]
    marks = Marks.query.filter(Marks.test_id.in_(test_ids)).all()
    std_ids = set([a.student_id for a in exam.students])
    students = Student.query.filter(Student.id.in_(std_ids)).all()
    grades = Grade.query.filter_by(branch_id=exam.branch_id).all()
    all_att = Attendance.query.filter(Attendance.date >= att_start,
                                      Attendance.date <= att_end,
                                      Attendance.punch_in != None).all()
    no_of_days = len(set(att.date for att in all_att))
    data = []  # data to save
    for std in students:
        std_data = {}
        std_data['exam_name'] = exam.name
        std_data['year'] = exam.start_date.strftime('%Y') if exam.start_date else datetime.today().strftime('%Y')
        std_data['name'] = std.name
        std_data['student_id'] = std.student_id
        std_data['category'] = std.category.name
        # subjects
        subjects_data = []
        tests = [test for test in exam.tests if test.cat_sub_association.category == std.category]
        marks = []
        for test in tests:
            sub_data = {}
            sub_data['name'] = test.cat_sub_association.subject.name
            sub_data['total_marks'] = test.max_marks
            mark = Marks.query.filter_by(test_id=test.id, student_id=std.id).first()
            if mark:
                marks.append(mark)
                sub_data['obtained_marks'] = mark.marks
                percent = (float(mark.marks) / test.max_marks) * 100
                sub_data['percent'] = percent
                sub_data['grade'] = get_grades(percent, grades).grade
            else:
                sub_data['obtained_marks'] = 'A'  # Absent
                sub_data['grade'] = ''
                sub_data['percent'] = 0  # for easy sorting
            subjects_data.append(sub_data)

        subjects_data.sort(key=get_subject_order)
        std_data['subjects'] = subjects_data
        # grand total
        total_data = {}
        total_data['total_marks'] = sum(t.max_marks for t in tests)
        total_data['obtained_marks'] = sum(m.marks for m in marks)
        percent = total_data['obtained_marks'] / total_data['total_marks'] * 100
        total_data['percent'] = percent
        total_data['grade'] = get_grades(percent, grades).grade
        std_data['total'] = total_data

        # Attendace data
        std_att = Attendance.query.filter(Attendance.date >= att_start,
                                          Attendance.date <= att_end,
                                          Attendance.student_id == std.id,
                                          Attendance.punch_in != None).all()
        std_data['att_present'] = len(std_att)
        std_data['total_days'] = no_of_days
        std_data['att_percent'] = float(len(std_att)) / no_of_days * 100
        data.append(std_data)

    #  global ranking
    def get_percent(std):
        return std.get('total', {}).get('percent', 0)

    data.sort(key=get_percent, reverse=True)
    for pos, d in enumerate(data):
        d['global_position'] = pos + 1  # 0 based position
        d['no_of_students'] = len(data)

    # category_wise ranking
    all_cat = [d['category'] for d in data]
    for cat in all_cat:
        cat_data = [d for d in data if d['category'] == cat]
        cat_data.sort(key=get_percent, reverse=True)
        for pos, d in enumerate(cat_data):
            d['cat_position'] = pos + 1  # 0 based position
            d['no_of_cat_students'] = len(cat_data)
    return data


@rq.job
def build_marksheets(meta, examid, att_start, att_end):
    att_start = datetime.strptime(att_start, '%d/%m/%Y').date()
    att_end = datetime.strptime(att_end, '%d/%m/%Y').date()
    owner = meta.owner
    exam = Exam.query.get(examid)
    print(exam, owner)
    if not all([exam, owner]):
        print('Invalid exam/owner')
        return
    students = exam_to_dict(exam.id, att_start, att_end)
    marksheet_filenames = []
    for std in students:
        header, row, rowtotal, footer = map(Image.open, ['app/static/marksheet_header.jpg',
                                                         'app/static/marksheet_marks_row.jpg',
                                                         'app/static/marksheet_marks_row_last.jpg',
                                                         'app/static/marksheet_footer.jpg'
                                                         ])

        max_width = max([item.size[0] for item in (header, row, rowtotal, footer)])

        total_height = sum([item.size[1] for item in (header, rowtotal, footer)])
        total_height += 6 * row.size[1]

        marksheet = Image.new('RGB', (max_width, total_height))

        draw_header_info(header, std)
        marksheet.paste(header, (0, 0))
        y_offset = header.size[1]

        std.get('subjects').sort(key=get_subject_order)
        for sub in std.get('subjects'):
            tmp_row = copy.deepcopy(row)
            draw_marks_row(tmp_row, sub)
            marksheet.paste(tmp_row, (0, y_offset))
            y_offset += tmp_row.size[1]

        draw_total_row(rowtotal, std.get('total'))
        marksheet.paste(rowtotal, (0, y_offset))
        y_offset += rowtotal.size[1]

        for _ in range(max(6 - len(std.get('subjects', [])), 0)):
            tmp_row = Image.open('app/static/marksheet_marks_blank.jpg')
            marksheet.paste(tmp_row, (0, y_offset))
            y_offset += tmp_row.size[1]

        draw_footer(footer, std)
        marksheet.paste(footer, (0, y_offset))
        filename = 'gen/reports/Marksheet ' + std['name'] + '.jpg'
        marksheet.save(filename)
        marksheet_filenames.append(filename)
    zip_filename = zipFiles(marksheet_filenames, name='marksheets.zip')
    reportTime = datetime.now().strftime('%d %b %Y %I:%M:%S %p')
    body = MARKSHEET_BODY_STRING.format(exam.name, reportTime)
    to = owner.email
    send_report_email(MARKSHEET_REPORT_SUBJECT, to, body, attachFileName=zip_filename, mimetype='application/zip')


def draw_header_info(header_img, data, font=font, color=txt_rgb):
    if not any([header_img, data]):
        return
    draw = ImageDraw.Draw(header_img)
    xo, yo = 730, 710
    header = 'Marksheet - {}'.format(data['exam_name'])
    headertxt_width, _ = draw.textsize(header, font=bold_font)
    header_x = (header_img.size[0] - headertxt_width) / 2
    draw.text((header_x, 520), header, fill=color, font=font)

    draw.text((xo, yo), data.get('name', ''), fill=color, font=font)
    draw.text((xo, 100 + yo), data.get('student_id', ''), fill=color, font=font)
    draw.text((xo, 200 + yo), data.get('year', ''), fill=color, font=font)
    draw.text((1100 + xo, 200 + yo), data.get('category', ''), fill=color, font=font)


def draw_marks_row(row_img, data, font=font, color=txt_rgb):
    if not any([row_img, data]):
        return
    draw = ImageDraw.Draw(row_img)
    sub_x = 175
    mm_x = 730
    m_x = mm_x + 370
    p_x = m_x + 430
    g_x = p_x + 310
    y = 30

    max_marks = '{}'.format(data.get('total_marks', ''))
    obtained_marks = '{}'.format(data.get('obtained_marks', ''))

    percent = data.get('percent', '')
    percent = '{0:.2f} %'.format(percent) if percent else ''

    draw.text((sub_x, y), data.get('name', ''), fill=color, font=font)
    draw.text((mm_x, y), max_marks, fill=color, font=font)
    draw.text((m_x, y), obtained_marks, fill=color, font=font)
    draw.text((p_x, y), percent, fill=color, font=font)
    draw.text((g_x, y), data.get('grade', ''), fill=color, font=font)


def draw_total_row(total_img, data, font=font, color=txt_rgb):
    if not any([total_img, data]):
        return
    draw = ImageDraw.Draw(total_img)
    mm_x = 730
    m_x = mm_x + 370
    p_x = m_x + 430
    g_x = p_x + 310
    y = 30
    total_marks = '{}'.format(data.get('total_marks', ''))
    obtained_marks = '{}'.format(data.get('obtained_marks', ''))
    percent = data.get('percent', '')
    percent = '{0:.2f} %'.format(percent) if percent else ''

    draw.text((mm_x, y), total_marks, fill=color, font=font)
    draw.text((m_x, y), obtained_marks, fill=color, font=font)
    draw.text((p_x, y), percent, fill=txt_rgb, font=font)
    draw.text((g_x, y), data.get('grade', ''), fill=txt_rgb, font=font)


def draw_footer(footer_img, data, font=font, color=txt_rgb):
    if not any([footer_img]):
        return
    draw = ImageDraw.Draw(footer_img)

    rank = (670, 165)
    no_stdnts = (850, 270)

    cat_rank = (670, 525)
    no_cat_stdnts = (850, 635)

    attn = (1715, 355)
    attn_percent = (1850, 475)
    wrkng_days = (1930, 200)

    rank_txt = str(data.get('global_position', 0))
    no_stdnts_txt = str(data.get('no_of_students', 0))
    cat_rank_txt = str(data.get('cat_position', 0))
    no_cat_stdnts_txt = str(data.get('no_of_cat_students', 0))
    attn_txt = str(data.get('att_present', 0))
    attn_percent_txt = '{0:.2f} %'.format(data.get('att_percent', 0))
    wrkng_days_txt = str(data.get('total_days', 0))

    draw.text(rank, rank_txt, fill=color, font=font)
    draw.text(no_stdnts, no_stdnts_txt, fill=color, font=font)
    draw.text(cat_rank, cat_rank_txt, fill=color, font=font)
    draw.text(no_cat_stdnts, no_cat_stdnts_txt, fill=color, font=font)
    draw.text(attn, attn_txt, fill=color, font=font)
    draw.text(attn_percent, attn_percent_txt, fill=color, font=font)
    draw.text(wrkng_days, wrkng_days_txt, fill=color, font=font)

