from rest_framework import status
from rest_framework.response import Response

class HttpResponse:
    @staticmethod
    def http_return_202_accepted(content):
        """
        http response with HTTP 200 status(ACCEPTED)
        :param content: (str)
        :return: (rest_framework.response.Response)
        """
        if content is None: content = ''

        http_body = {
            'success': True,
            'content': content,
            'error': 'no_error'
        }

        return Response(data=http_body, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def http_return_200_ok(content):
        """
        http response with HTTP 200(OK)
        :param content: (str)
        :return: (rest_framework.response.Response)
        """
        if content is None: content = ''
        http_body = {
            'success': True,
            'content': content,
            'error': 'no_error'
        }

        return Response(data=http_body, status=status.HTTP_200_OK)

    @staticmethod
    def http_return_400_bad_request(error_message):
        """
        http response with HTTP 400 status(BAD REQUEST)
        :param error_message:
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'success': False,
            'content': '',
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def http_return_409_conflict(error_message):
        """
        http response with HTTP 409 status(CONFLICT)
        :param error_message:
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'success': False,
            'content': '',
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_409_CONFLICT)

    @staticmethod
    def http_return_500_internal_server_error(error_message):
        """
        http response with HTTP 500 status(INTERNAL_SERVER_ERROR)
        :param error_message: (str) error message
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'success': False,
            'content': '',
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def http_return_503_service_unavailable(error_message):
        """
        http response with HTTP 503 status(SERVICE_UNAVAILABLE)
        :param error_message: (str) error message
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'success': False,
            'content': '',
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_503_SERVICE_UNAVAILABLE)