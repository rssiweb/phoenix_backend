from datetime import datetime
import re

_email_pattern = re.compile(r'[^@]+@[^@]+\.[^@]+')


def parseDate(strDate, format):
    try:
        validDatetime = datetime.strptime(strDate, format)
        return True, validDatetime
    except Exception as ex:
        return False, str(ex)


def validEmail(email):
    if not email:
        return False
    return _email_pattern.match(email)
