from flask import render_template, Blueprint, redirect

ui = Blueprint("ui", __name__, url_prefix="")


@ui.route("/")
def login():
    return render_template("login.html")


@ui.route("/attendance")
def attendance():
    return redirect("/me")
    # return render_template("attendance.html", page=1)


@ui.route("/students")
def students():
    return render_template("students.html", page=2)


@ui.route("/faculties")
def faculties():
    return render_template("faculties.html", page=3)


@ui.route("/me")
def me():
    return render_template("myprofile.html", page=4)


@ui.route("/report")
def report():
    return render_template("report.html", page=5)


@ui.route("/exam/marks")
def exam():
    return render_template("exam_marks.html", page=6)


@ui.route("/exam/result")
def result():
    return render_template("exam_result.html", page=8)


@ui.route("/adminactions")
def admin_actions():
    return render_template("admin_actions.html", page=7)


@ui.route("/branch_details/<int:branchid>")
def admin_branch_details(branchid):
    return render_template("branch_details.html", page=7, branchid=branchid)


@ui.route("/exams_details/<int:branchid>/<int:examid>")
def admin_exam_details(branchid, examid):
    return render_template(
        "exam_details.html", page=7, examid=examid, branchid=branchid
    )


@ui.route("/distribution")
def distribution():
    return render_template("distribution.html", page=8)
