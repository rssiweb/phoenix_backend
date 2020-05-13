from datetime import datetime
import re
import math

_email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")


def parseDate(strDate, format):
    try:
        validDatetime = datetime.strptime(strDate, format)
        return True, validDatetime
    except Exception as ex:
        return False, str(ex)


def validEmail(email):
    if not email:
        return False
    return bool(_email_pattern.match(email))


def isValidPassword(password):
    if not password and len(password) < 5:
        return False, "Min length should be 5 chars"
    if not re.search("[A-Z]", password):
        return False, "Must contain one capital case letter"
    if not re.search("[a-z]", password):
        return False, "Must contain one small case letter"
    if not re.search("[!@#$%&*]", password):
        return (
            False,
            "Must contain one special character out of '!', '@', '#', '$', '%', '&', '*'",
        )
    return True, "Strong Password"


def get_grades(percent, grade_rules):
    for rule in grade_rules:
        percent = round(percent, 0)
        if rule.lower <= percent and percent <= rule.upper:
            return rule
    return ""


def slice_by(itr, n):
    no_slices = int(math.ceil(len(itr) / float(n)))
    for i in range(no_slices):
        yield itr[n * i : n * i + n]
