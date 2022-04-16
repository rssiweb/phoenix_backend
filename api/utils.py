def safe_date_format(datetime_obj, format):
    if datetime_obj:
        return datetime_obj.strftime(format)
