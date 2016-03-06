import cProfile
import datetime
import pstats
import StringIO
import threading

from snoopy.helpers import get_app_root


_snoopy_request = threading.local()


def clean_profiler_result(result):
    app_root = get_app_root()

    lines = result.split("\n")
    relevant_result = lines[:5] + [line for line in lines[6:] if app_root in line]
    return "\n".join(relevant_result)


class SnoopyRequest:
    """
    Wrapper for managing Django Requests.
    """
    @staticmethod
    def register_request(request, settings):
        snoopy_data = {
            'request': request.path,
            'method': request.method,
            'queries': [],
            'custom_attributes': {},
            'start_time': datetime.datetime.now()
        }
        _snoopy_request.request = request
        _snoopy_request.data = snoopy_data
        _snoopy_request.settings = settings

        if _snoopy_request.settings.get('USE_CPROFILE'):
            _snoopy_request.profiler = cProfile.Profile()
            _snoopy_request.profiler.enable()


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
    def record_custom_attributes(custom_data):
        """
        `custom_data` must be JSON serializable dict.
        datetime / timedelta objects are handled.
        """
        _snoopy_request.data['custom_attributes'].update(custom_data)

    @staticmethod
    def register_response(response):
        snoopy_data = _snoopy_request.data
        snoopy_data['end_time'] = datetime.datetime.now()
        snoopy_data['total_request_time'] = \
            (snoopy_data['end_time'] - snoopy_data['start_time'])

        if _snoopy_request.settings.get('USE_CPROFILE'):
            _snoopy_request.profiler.disable()
            profiler_result = StringIO.StringIO()
            profiler_stats = pstats.Stats(
                _snoopy_request.profiler, stream=profiler_result).sort_stats('cumulative')
            profiler_stats.print_stats()

            result = profiler_result.getvalue()
            if not _snoopy_request.settings.get('CPROFILE_SHOW_ALL_FUNCTIONS'):
                result = clean_profiler_result(result)
            snoopy_data['profiler_result'] = result
        return snoopy_data
