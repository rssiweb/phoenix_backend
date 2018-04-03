from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from app import db
from app.models import Attendance
from datetime import datetime, timedelta
import copy
import calendar
import os


def draw_row(srno, draw, student, month):
    print os.listdir('.')
    font = ImageFont.truetype("app/Ubuntu-M.ttf", 60)
    text_y = 25
    vals = []

    # Index
    col_width = 170
    text_width, text_height = draw.textsize(str(srno), font=font)
    text_x = 230 + (col_width - text_width) / 2
    draw.text((text_x, text_y), str(srno), font=font)

    # Category
    draw.text((460, text_y), student.category.name, font=font)

    # Name
    draw.text((850, text_y), student.name, font=font)

    # Attendace
    # Start position
    x_offset = 1870
    col_width = 140
    col_gap = 7

    _, no_of_days = calendar.monthrange(month.year, month.month)
    for d in range(1, 32):
        if d <= no_of_days:
            curr_date = month + timedelta(days=d)
            attendance = Attendance.query.filter_by(student_id=student.id, date=curr_date).first()
            val = 'A'
            if attendance and attendance.punch_in and attendance.punch_in.strip():
                val = 'P'
            vals.append(val)
            text_width, text_height = draw.textsize(val, font=font)
            text_x = x_offset + (col_width - text_width) / 2
            draw.text((text_x, text_y), val, font=font)
        x_offset += col_width + col_gap

    # Total A and P
    total_a = sum([v == 'A' for v in vals])
    total_p = sum([v == 'P' for v in vals])

    col_width = 141
    text_width, text_height = draw.textsize(str(total_p), font=font)
    text_x = x_offset + (col_width - text_width) / 2
    draw.text((text_x, text_y), str(total_p), font=font)

    x_offset += col_width + col_gap

    col_width = 173
    text_width, text_height = draw.textsize(str(total_a), font=font)
    text_x = x_offset + (col_width - text_width) / 2
    draw.text((text_x, text_y), str(total_a), font=font)


def draw_header(header2, month, categories, branches):
    font = ImageFont.truetype("Ubuntu-M.ttf", 60)
    draw = ImageDraw.Draw(header2)
    # Group (Categories)
    draw.text((1175, 290), ', '.join([cat.name for cat in categories]), font=font)
    # Location (Branches)
    draw.text((4300, 290), ', '.join([b.name for b in branches]), font=font)
    # Time
    draw.text((4300, 110), datetime.today().strftime('%H:%M:%S %p'), font=font)
    # Month 6020 110
    draw.text((6020, 110), month.strftime('%B'), font=font)
    # YEAR 6020 290
    draw.text((6020, 290), month.strftime('%Y'), font=font)

def buildReport(students, month, categories, branches):
    month = datetime.strptime(month, '%B %Y')
    import os
    print os.listdir('.')
    header1, header2, row, footer = map(Image.open, ['./monthly_report/header1.jpg','./monthly_report/header2.jpg','./monthly_report/row.jpg','./monthly_report/footer.jpg'])

    max_width = max([item.size[0] for item in (header1, header2, row, footer)])

    total_height = sum([item.size[1] for item in (header1, header2, row, footer)])

    total_height += (len(students) - 1) * row.size[1]

    att_sheet = Image.new('RGB', (max_width, total_height))

    att_sheet.paste(header1, (0, 0))
    draw_header(header2, month, categories, branches)
    att_sheet.paste(header2, (0, header1.size[1]))

    y_offset = header1.size[1] + header2.size[1]
    for index, student in enumerate(students):
        tmp_row = copy.deepcopy(row)
        draw_row(index + 1, ImageDraw.Draw(tmp_row), student, month)
        att_sheet.paste(tmp_row, (0, y_offset))
        y_offset += row.size[1]
    att_sheet.paste(footer, (0, y_offset))
    att_sheet.save('app/report.jpg')
    return 'report.jpg'
