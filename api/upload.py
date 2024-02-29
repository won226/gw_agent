import os
from django.core.files.base import ContentFile
from datetime import datetime
from gw_agent import settings
from gw_agent.common.error import APIError
from gw_agent.common.type import ErrorType
from utils.fileutils import FileUtil


class Upload:
    """
    class Upload
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()
        return cls._instance

    def _config(self):
        self._temp_directory = settings.TEMP_DIRECTORY

    @staticmethod
    def validate_http_upload_request(request, attrs):
        """
        validate http file upload request
        :param request:
        :param attrs: (list[str]); http upload file attributes
        :return:
        """
        for attr in attrs:
            try:
                file_object = request.FILES[attr]
            except Exception:
                desc = '{} attribute is none'.format(attr)
                raise APIError(ErrorType.HTTP_UPLOAD_INVALID_FILE_ATTRIBUTE_ERROR, desc)
            if file_object is None:
                desc = '{} attribute is none'.format(attr)
                raise APIError(ErrorType.HTTP_UPLOAD_INVALID_FILE_ATTRIBUTE_ERROR, desc)
            if file_object.size > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
                desc = 'exceed file upload size limit. ' \
                       'upload file={}, limit={}'.format(file_object.size, settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
                raise APIError(ErrorType.HTTP_UPLOAD_EXCEED_FILE_SIZE_LIMIT_ERROR, desc)
            if file_object.name is None:
                desc = 'upload file name is none'
                raise APIError(ErrorType.HTTP_UPLOAD_INVALID_FILE_VALUE_ERROR, desc)

    def http_upload_files(self, request, attrs):
        """
        upload http files for upload request
        :param request:
        :param attrs: (list[str]); http upload file attributes
        :return: dict; {{(str):(str)}, ...}; {{'http body key': 'local temp filename'}}
        """
        Upload.validate_http_upload_request(request, attrs)
        result = {}

        for attr in attrs:
            file_object = request.FILES[attr]
            file_content = ContentFile(file_object.read())
            file_name = '{}.{}'.format(file_object.name, str(datetime.now().timestamp()))
            file_name = os.path.join(self._temp_directory, file_name)
            FileUtil.save_file_content_to_bin_file(file_name, file_content)
            result[attr] = file_name

        return result
