from datetime import datetime


def parseDate(strDate, format):
    try:
        validDatetime = datetime.strptime(strDate, format)
        return True, validDatetime
    except Exception as ex:
        return False, str(ex)
