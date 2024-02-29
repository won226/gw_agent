import time
from datetime import datetime

from backports.zoneinfo import ZoneInfo
from pytz import timezone


class DateFormatter:

    @staticmethod
    def from_string(time_str):
        """
        desc: get datetime object with time string formatted as '%Y-%m-%d %H:%M:%S'
        arg0: (string) time
        ex) datetime object
        print(date_time.year)
        print(date_time.month)
        print(date_time.day)
        print(date_time.hour)
        print(date_time.minute)
        print(date_time.second)
        """
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def current_datetime():
        """
        desc: get current datetime
        return: (string) datetime formatted as '%Y-%m-%d %H:%M:%S'
        :return:
        """
        dt = datetime.now(timezone('Asia/Seoul'))

        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def current_datetime_object():
        """
        current datetime object
        :return: (datetime.datetime)
        """
        return datetime.now(timezone('Asia/Seoul'))

    @staticmethod
    def to_datetime(dt: str):
        """
        to datetime
        :param dt: (str) format '%Y-%m-%dT%H:%M:%SZ'
        :return:
        """
        return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def current_datetime_ms():
        """
        desc: get current datetime with decimal point in second
        return: (string) datetime formatted as '%Y-%m-%d %H:%M:%S.%f'
        :return:
        """
        dt = datetime.now(timezone('Asia/Seoul'))
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def get_elapsed_time(v1, v2):
        """
        desc: get elapsed time between v1, v2(past)
        arg0: (datetime) v1
        arg1: (datetime) v2
        return: (float) time difference as seconds
        :param v1:
        :param v2:
        :return:
        """
        elapsed_time = v1 - v2
        return elapsed_time.total_seconds()

    @staticmethod
    def datetime_to_str(val):
        """
        convert datetime to str
        :param val: (datetime)
        :return: (str) formatted as '%Y-%m-%d %H:%M:%S.%f'
        """
        if val is None:
            return None

        if type(val) != datetime:
            raise TypeError('Invalid val type. You must input datetime as val')
        return val.strftime('%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def timestamp_to_str(timestamp):
        """
        desc: to datetime text format with timestamp(time.time())
        arg0: (Epoch from time.time()) timestamp
        return: (str) datetime(i.e., '2021-06-07 14:23:46.973204')
        :param timestamp:
        :return:
        """
        return datetime.fromtimestamp(timestamp).astimezone(tz=ZoneInfo('localtime')).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def to_timestamp(val: str):
        """
        convert to timestamp(time.time())
        :param val:
        :return: time.time()
        """
        return time.mktime(datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ').timetuple())

    @staticmethod
    def get_datetime_format(datetime_string: str):
        """
        get datetime format
        :param datetime_string: (str) datetime string
        :return:
        """
        datetime_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d',
            '%Y/%m/%dT%H:%M:%S',
            '%Y/%m/%dT%H:%M:%SZ',
            '%Y/%m/%dT%H:%M:%S.%f',
            '%Y/%m/%dT%H:%M:%S.%fZ',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S.%f',
        ]

        for datetime_format in datetime_formats:
            try:
                datetime.strptime(datetime_string, datetime_format)
                return datetime_format
            except ValueError:
                continue

        return None

    @staticmethod
    def get_elapsed_seconds(datetime_string: str) -> int:
        """
        get elapsed seconds from datetime_string
        :return: (int) elapsed seconds
        """
        time_format = DateFormatter.get_datetime_format(datetime_string)
        if not time_format:
           raise ValueError('Invalid datetime format string')

        base_dt = datetime.strptime(datetime_string, time_format)

        # now datetime
        current_time_string = DateFormatter.current_datetime()
        time_format = DateFormatter.get_datetime_format(current_time_string)
        now_dt = datetime.strptime(current_time_string, time_format)

        elapsed_datetime = now_dt - base_dt

        return elapsed_datetime.total_seconds()
