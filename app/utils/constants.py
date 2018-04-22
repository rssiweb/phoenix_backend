from collections import namedtuple

StatusErrorValues = namedtuple('StatusErrorValues', 'text type')


class StatusErrors(object):
    BLANK_VALUES_FOR_REQUIRED_FIELDS = StatusErrorValues('BLANK_VALUES_FOR_REQUIRED_FIELDS', list)
