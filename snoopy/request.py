import datetime
import threading


_snoopy_request = threading.local()


class SnoopyRequest:
    """
    Wrapper for managing Django Requests.
    """
    @staticmethod
    def register_request(request):
        snoopy_data = {
            'request': request.path,
            'method': request.method,
            'queries': [],
            'start_time': datetime.datetime.now()
        }
        _snoopy_request.request = request
        _snoopy_request.data = snoopy_data


    @staticmethod
    def get_current_request():
        if not hasattr(_snoopy_request, 'request'):
            return None
        else:
            return _snoopy_request.request


    @staticmethod
    def record_query_data(query_data):
        query_data['total_query_time'] = \
            (query_data['end_time'] - query_data['start_time'])
        _snoopy_request.data['queries'].append(query_data)


    @staticmethod
    def register_response(response):
        snoopy_data = _snoopy_request.data
        snoopy_data['end_time'] = datetime.datetime.now()
        snoopy_data['total_request_time'] = \
            (snoopy_data['end_time'] - snoopy_data['start_time'])
        return snoopy_data
