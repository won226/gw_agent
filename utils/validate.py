import dateutil
import re
from dateutil.parser import parse

class Validator:
    ip_pattern = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

    @staticmethod
    def is_int(val):
        if val is None:
            return False
        if type(val) == int:
            return True
        else:
            return False

    @staticmethod
    def is_float(val):
        if val is None:
            return False
        if type(val) == float:
            return True
        else:
            return False

    @staticmethod
    def is_str(val):
        if val is None:
            return False
        if type(val) == str:
            return True
        else:
            return False

    @staticmethod
    def is_ip_address(val):
        if val is None:
            return False
        if type(val) != str:
            return False
        if re.search(Validator.ip_pattern, val):
            return True
        else:
            return False

    @staticmethod
    def is_dateformat(val):
        if val is None:
            return False
        try:
            parse(val)
        except dateutil.parser.ParserError:
            return False
        return True

    @staticmethod
    def is_enable_cast_to_int(val):
        if val is None:
            return False
        try:
            int(val)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_enable_cast_to_float(val):
        if val is None:
            return False
        try:
            float(val)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_enable_cast_to_bool(val):
        if val is None:
            return False
        if type(val) != str:
            return False
        return val.lower() in ["true", "false"]

    @staticmethod
    def cast_to_bool(val):
        lower_val = val.lower()
        if val is None:
            raise ValueError('val is None')
        if type(val) != str:
            raise ValueError('val(type={}) is not str type'.format(type(val)))
        if lower_val == "true":
            return True
        elif lower_val == "false":
            return False
        else:
            raise ValueError('Invalid str value({}) to cast bool'.format(val))

# if __name__ == '__main__':
#     test_bool = 'True1'
#     if Validator.is_enable_cast_to_bool(test_bool):
#         print(Validator.cast_to_bool(test_bool))
#
#     test_ip = '10.0.0.11231'
#     print(Validator.is_ip_address(test_ip))
#     test_val = '131111.1'
#     print(Validator.is_enable_cast_to_int(test_val))
#     # print(Validator.is_enable_cast_to_float(test_val))
#     test_date = '2020-11-13'
#     print(Validator.is_dateformat(test_date))