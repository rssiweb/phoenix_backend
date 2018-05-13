from collections import namedtuple
from operator import methodcaller

StatusErrorValues = namedtuple('StatusErrorValues', 'text type')


class StatusErrors(object):
    BLANK_VALUES_FOR_REQUIRED_FIELDS = StatusErrorValues('BLANK_VALUES_FOR_REQUIRED_FIELDS', list)
    DUPLICATE_ID = StatusErrorValues('DUPLICATE_ID', methodcaller('__getitem__', slice(None, 2)))
