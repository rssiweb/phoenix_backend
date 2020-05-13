from flask import request, Blueprint, make_response
from app import db, jsonify
from app.models import Student, Branch, Category
from datetime import datetime
from operator import itemgetter
from app.utils import decorators
from app.utils.constants import StatusErrors as error
import csv

api = Blueprint("admin_student_api", __name__, url_prefix="/api/admin/student")


@api.route("/<string:action>", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def add_update_student(action):
    res = dict(status="fail")
    res_code = 200
    if action not in ["add", "update"]:
        res["message"] = "Invalid url"
        return jsonify(res), 401

    required_fields = "dob name category id contact branch".split()

    data = request.json or request.data or request.form
    print(data)
    if not data:
        res["message"] = "No data received."
        return make_response(jsonify(res)), res_code

    if not set(required_fields).issubset(set(data.keys())):
        res["message"] = "expected atleast {0} got only {1}".format(
            required_fields, data.keys()
        )
        return jsonify(res), res_code

    required_values = [data.get(f).strip() for f in required_fields]

    if not all(required_values):
        blanks = [f for f, v in zip(required_fields, required_values) if not v]
        res["message"] = "%s cannot have blank values" % ", ".join(blanks)
        res["statusText"] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res["statusData"] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(blanks)
        return jsonify(res), res_code

    dob, name, category_id, student_id, contact, branch = required_values

    try:
        dob = datetime.strptime(dob, "%Y-%m-%d")
    except Exception:
        res["message"] = "Invalid date: {0}".format(dob)
        return jsonify(res), res_code

    student = Student.query.filter_by(student_id=student_id).first()
    category = Category.query.filter_by(id=category_id).first()
    branch = Branch.query.filter_by(id=branch).first()
    if action == "add":
        if student is not None:
            # res['message'] = 'Duplicate Student ID %s, consider changing Student ID'.format(student_id)
            res["statusText"] = error.DUPLICATE_ID.text
            res["statusData"] = error.DUPLICATE_ID.type(["id", student_id])
            res_code = 201
        elif not category:
            res["message"] = "Category %s not found".format(category)
            res_code = 201
        elif not branch:
            res["message"] = "Branch %s not found".format(branch)
            res_code = 201
        else:
            try:
                student = Student(
                    name=name,
                    student_id=student_id,
                    category=category.id,
                    contact=contact,
                    dob=dob,
                    branch=branch.id,
                )
                # insert the user
                db.session.add(student)
                db.session.commit()
                res["message"] = "{0} Successfully registered.".format(student.name)
                res["status"] = True
                res["student"] = student.serialize()
                res_code = 201
            except Exception as e:
                print(e)
                res["message"] = "Some error occurred. Please try again."
    elif action == "update":
        student.name = name
        student.dob = dob
        student.category = category
        student.contact = contact
        db.session.commit()
        res["status"] = "success"
        res["student"] = student.serialize()
    return jsonify(res), res_code


@api.route("/import", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def import_students():
    res = dict(status="fail")
    file = request.files.get("studentsListFile")
    csvreader = csv.reader(file, delimiter=",", quotechar='"')
    # TODO: check type of file
    heading = [title.strip().lower() for title in next(csvreader)]
    required_headers = (
        "name of the student",
        "category",
        "student id",
        "date of birth",
        "telephone number",
        "preferred branch",
        "effective from",
    )
    missing_headers = set(required_headers) - set(heading)
    if missing_headers:
        res["message"] = 'Missing "%s" required column(s)' % '", "'.join(
            missing_headers
        )
        return jsonify(res), 200

    getName = itemgetter(heading.index("name of the student"))
    getCategory = itemgetter(heading.index("category"))
    getStudentId = itemgetter(heading.index("student id"))
    getDob = itemgetter(heading.index("date of birth"))
    getContact = itemgetter(heading.index("telephone number"))
    getBranch = itemgetter(heading.index("preferred branch"))
    getStatus = itemgetter(heading.index("status"))
    getEndDate = itemgetter(heading.index("effective from"))
    getPhotoUrl = itemgetter(heading.index("photo url"))

    added = []
    updated = []
    for row in csvreader:
        student = Student.query.filter_by(student_id=getStudentId(row)).first()
        category_name, student_id = getCategory(row), getStudentId(row)
        name, contact = getName(row), getContact(row)
        dob = datetime.strptime(getDob(row), "%d/%m/%Y").date()
        branch_name, image_url = getBranch(row), getPhotoUrl(row)
        # if there is any thing in the status we assume the student to be inactive
        active = getStatus(row) != "R"
        effective_end_date = getEndDate(row)

        if effective_end_date:
            effective_end_date = datetime.strptime(
                effective_end_date, "%d/%m/%Y"
            ).date()
        else:
            effective_end_date = None

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            res["message"] = "Unknown category %s for student %s" % (
                category_name,
                name,
            )
            return jsonify(res), 200
        branch = Branch.query.filter_by(name=branch_name).first()
        if not branch:
            res["message"] = "Unknown branch %s for student %s" % (branch_name, name)
            return jsonify(res), 200
        if student:
            unchanged = all(
                [
                    student.category == category,
                    student.dob == dob,
                    student.name == name,
                    student.contact == contact,
                    student.branch == branch,
                    student.isActive == active,
                    student.effective_end_date == effective_end_date,
                    student.image == image_url,
                ]
            )
            if not unchanged:
                student.category = category
                student.dob = dob
                student.name = name
                student.contact = contact
                student.branch = branch
                student.isActive = active
                student.effective_end_date = effective_end_date
                student.image = image_url
                updated.append(student)
        else:
            student = Student(
                student_id=student_id,
                category=category.name,
                dob=dob,
                name=name,
                contact=contact,
                branch=branch.name,
                isActive=active,
                effective_end_date=effective_end_date,
                image=image_url,
            )
            db.session.add(student)
            added.append(student)
    db.session.commit()
    res["status"] = "success"
    res["added"] = [std.serialize() for std in added]
    res["updated"] = [std.serialize() for std in updated]
    res["message"] = "Added {0} student(s), Udpated {1} student(s)".format(
        len(added), len(updated)
    )
    return jsonify(res), 200
