import json
from urllib.parse import urlparse, parse_qs

from gw_agent.common.error import get_exception_traceback
from gw_agent.settings import get_logger
from mqtt.model.request import Request
from mqtt.urls import urlpatterns


class Dispatcher:
    """
    MQTT Request dispatcher from CEdge-center
    """
    _route = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._logger = get_logger(__name__)
        return cls._instance

    @classmethod
    def _parse_path(cls, path):
        values = path.split('/')
        values = list(filter(len, values))
        rule = []

        for value in values:
            if type(value) == str and len(value) > 0:
                if value[0] == ':':
                    rule.append({
                        'type': 'parameter',
                        'name': value.replace(':', '')
                    })
                else:
                    rule.append({
                        'type': 'resource',
                        'name': value
                    })

        return rule

    def register_router(self):
        """
        register consume message router
        :return:
        """
        for pattern in urlpatterns:
            self._register(*pattern)

    def _register(self, url, callback):
        """
        register route
        :param url: (str)
        :param callback: method
        :return:
        """
        # example /cluster/:cluster_id/node/:node_id/
        result = urlparse(url)
        path = result.path

        self._route[url] = {
            'match_rule': self._parse_path(path),
            'callback': callback
        }

    def _get_route(self, url):
        """
        get route entry
        :param url: (str)
        :return:
        """
        values = url.split('/')
        values = list(filter(len, values))
        path_variables = {}
        not_matched = True
        route = None

        for item in self._route.values():
            match_rule = item['match_rule']
            if len(match_rule) == len(values):
                not_matched = False
                path_variables = {}
                for i in range(0, len(match_rule)):
                    if match_rule[i]['type'] == 'resource':
                        if match_rule[i]['name'] != values[i]:
                            not_matched = True
                            break
                    else:
                        path_variables[match_rule[i]['name']] = values[i]
                if not_matched:
                    continue
                else:   # matched
                    route = item
                    break

        if not_matched:
            return False, None, None

        return True, route, path_variables

    def dispatch(self, data: bytes):
        """
        dispatch request message
        :param data:
        :return:
        """
        decoded = data.decode('utf-8')

        try:
            body = json.loads(decoded)
        except json.decoder.JSONDecodeError:
            self._logger.error('Invalid request: raw message: \'{}\''.format(decoded))
            return

        # dispatch
        try:
            request = Request.to_object(body)
        except Exception as exc:
            self._logger.error('Failed to Request.to_object(body), caused by ' + get_exception_traceback(exc))

        ok, route, arguments = self._get_route(request.get_path())

        if ok:
            request.set_arguments(arguments)

        # call callback method
        route['callback'](request)