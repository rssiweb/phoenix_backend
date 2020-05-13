import click
from flask import Blueprint
from app.models import Faculty, Branch
from app import db


commands = Blueprint("users", __name__)


@commands.cli.command("create")
@click.argument("facultyId")
@click.argument("email")
@click.argument("password")
@click.argument("name")
@click.argument("gender")
@click.argument("branch_name")
def create(facultyid, email, password, name, gender, branch_name):
    faculty = Faculty.query.filter_by(facultyId=facultyid).first()
    branch = Branch.query.filter_by(name=branch_name).first()
    if not faculty:
        try:
            faculty = Faculty(
                facultyId=facultyid,
                name=name,
                email=email,
                password=password,
                gender=gender,
                branch_id=branch.id,
                contact=None,
                image=None,
            )
            faculty.admin = True
            faculty.superUser = True
            # insert the user
            db.session.add(faculty)
            db.session.commit()
            print("create user done!", faculty)
        except Exception as ex:
            print(ex)
    else:
        print(f"{facultyid} already exists!")
