import base64
import os
import six


class FileContent:
    """
    File content
    """
    fields = {
        "filename": "str",
        "base64_encoded": "bool",
        "content": "str"
    }

    def __init__(self):
        self.filename = None
        self.base64_encoded = False
        self.content = None

    def to_dict(self):
        """
        to dict from self instance
        :return:
        """
        result = {}

        for attr, _ in six.iteritems(self.fields):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    @classmethod
    def _validate(cls, _dict: dict):
        """
        validate Request dictionary
        :param _dict:
        :return:
        """
        if type(_dict) != dict:
            raise TypeError('Invalid type. Must input dict type')

        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict: dict):
        """
        to object
        :param _dict: (dict)
        :return:
        """
        cls._validate(_dict)
        instance = cls()

        for key, value in _dict.items():
            setattr(instance, key, value)

        return instance

    @classmethod
    def _is_base64_encoding_required_file(cls, file_path):
        """
        check whether a file is required base64 encoding
        :return: (bool) required
        """
        try:
            f = open(file_path, 'tr')
            f.read()
            return False
        except UnicodeError:
            return True

    @classmethod
    def _is_base64_encoding_required_stream(cls, buffer):
        """
        check whether a stream is required base64 encoding
        :return: (bool) required
        """
        try:
            buffer.decode('utf-8')
        except UnicodeError:
            return True

        return False

    def loads(self, buffer, filename):
        """
        load stream
        :param buffer: (bytes)
        :param filename: (str)
        :return:
        """
        ok = self._is_base64_encoding_required_stream(buffer)
        if ok:
            self.content = base64.b64encode(buffer).decode('utf-8')
            self.base64_encoded = True
            self.set_filename(filename)
            return

        self.content = buffer.decode('utf-8')
        self.base64_encoded = False
        self.set_filename(filename)
        return

    def load(self, file_path):
        """
        load file as utf-8 encoded string
        :param file_path:
        :return:
        """
        ok = self._is_base64_encoding_required_file(file_path)
        filename = os.path.basename(file_path)

        if ok:
            f = open(file_path, 'rb')
            self.content = base64.b64encode(f.read()).decode('utf-8')
            self.base64_encoded = True
            self.set_filename(filename)
            f.close()
            return

        f = open(file_path, 'r')
        self.content = f.read()
        self.base64_encoded = False
        self.set_filename(filename)
        f.close()
        return

    def set_filename(self, filename):
        """
        set filename
        :param filename: (str)
        :return:
        """
        if type(filename) != str:
            raise ValueError('Invalid value for filename')

        self.filename = filename

    def get_filename(self):
        """
        get filename
        :return:
        """
        return self.filename

    def get_file_extension(self):
        """
        get file extension
        :return:
        """
        if not self.filename:
            raise ValueError('Not found file name')

        arr = os.path.splitext(self.filename)
        return arr[1]

    def save(self, save_file_path):
        """
        save file
        :param save_file_path:
        :return: (bool) success
        """
        if save_file_path is None:
            raise ValueError('Invalid file path({})'.format(save_file_path))

        if self.base64_encoded:
            decoded = base64.b64decode(self.content)
            f = open(save_file_path, 'wb')
            f.write(decoded)
            f.close()
        else:
            f = open(save_file_path, 'w')
            f.write(self.content)
            f.close()

        return True
