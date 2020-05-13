from collections import namedtuple
from operator import methodcaller

StatusErrorValues = namedtuple("StatusErrorValues", "text type")


class StatusErrors(object):
    # MISSING_REQUIRED_FIELDS values missing, list of keys that is missing
    MISSING_REQUIRED_FIELDS = StatusErrorValues("MISSING_REQUIRED_FIELDS", list)
    # INVALID_FORMAT (required format, received)
    INVALID_FORMAT = StatusErrorValues(
        "INVALID_FORMAT", methodcaller("__getitem__", slice(None, 2))
    )
    # BLANK_VALUES_FOR_REQUIRED_FIELDS list of keys having blank values
    BLANK_VALUES_FOR_REQUIRED_FIELDS = StatusErrorValues(
        "BLANK_VALUES_FOR_REQUIRED_FIELDS", list
    )
    # DUPLICATE_ID, ['key', 'value']
    DUPLICATE_ID = StatusErrorValues(
        "DUPLICATE_ID", methodcaller("__getitem__", slice(None, 2))
    )
    # INVALID_VALUE_TYPE, ['expected (must be a string like 'number','decimal','string')', 'received value']
    INVALID_VALUE_TYPE = StatusErrorValues(
        "INVALID_VALUE_TYPE", methodcaller("__getitem__", slice(None, 2))
    )

    # CUSTOM_ERROR custom error message
    CUSTOM_ERROR = StatusErrorValues("CUSTOM_ERROR", str)
