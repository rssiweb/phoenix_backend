from collections import UserDict


class GradesDict(UserDict):

    def __getitem__(self, key):
        if key == 'X':
            return key
        key = math.ceil(float(key))
        for low, high in self.data.keys():
            if key >= low and key <= high:
                return self.data[(low, high)]
        print(key, 'Unknown Grade')
        return 'Unknown Grade'


GRADES_DICT = GradesDict(dict((91, 100)='O',
                              (81, 90)='E',
                              (71, 80)='A+',
                              (61, 70)='A',
                              (51, 60)='B+',
                              (41, 50)='B',
                              (31, 40)='C+',
                              (25, 30)='C',
                              (0, 24)='F'))
