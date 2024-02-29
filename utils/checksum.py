import hashlib
import os

from utils.fileutils import FileUtil


class MD5Checksum:
    @classmethod
    def get_checksum(cls, filename: str) -> str:
        """
        get checksum for file
        :param filename: (str) file path
        :return:
        """
        if not filename or type(filename) != str or len(filename) <= 0:
            raise ValueError('Invalid param \'filename\' value({})'.format(filename))

        if not os.path.isfile(filename):
            raise FileNotFoundError('Not found file({})'.format(filename))

        content = FileUtil.read_text_file(filename)

        if content:
            return hashlib.md5(content).hexdigest()

        return None

    @classmethod
    def get_checksums(cls, content: str) -> str:
        """
        get checksum for str
        :param content: (str)
        :return: (str)
        """
        if not content or type(content) != str or len(content) <= 0:
            raise ValueError('Invalid param \'content\' value({})'.format(content))

        return hashlib.md5(content).hexdigest()

    @classmethod
    def validate_checksums(cls, content: str, checksum: str) -> bool:
        """
        validate checksum for str
        :param content: (str) validating content
        :param checksum: (str) checksum
        :return: (bool) True - valid, False - not valid
        """
        if not content or type(content) != str or len(content) <= 0:
            raise ValueError('Invalid param \'content\' value({})'.format(content))

        if not checksum or type(checksum) != str or len(checksum) <= 0:
            raise ValueError('Invalid param \'checksum\' value({})'.format(checksum))

        # calculate checksum
        content_checksum = cls.get_checksums(content)

        if content_checksum != checksum:
            return False

        return True

    @classmethod
    def validate_checksum(cls, filename: str, checksum: str) -> bool:
        """
        validate checksum for str
        :param filename: (str) validating filename
        :param checksum: (str) checksum
        :return: (bool) True - valid, False - not valid
        """
        if not filename or type(filename) != str or len(filename) <= 0:
            raise ValueError('Invalid param \'filename\' value({})'.format(filename))

        if not os.path.isfile(filename):
            raise FileNotFoundError('Not found file({})'.format(filename))

        if not checksum or type(checksum) != str or len(checksum) <= 0:
            raise ValueError('Invalid param \'checksum\' value({})'.format(checksum))

        content = FileUtil.read_text_file(filename)

        # calculate checksum
        content_checksum = cls.get_checksums(content)

        if content_checksum != checksum:
            return False

        return True
