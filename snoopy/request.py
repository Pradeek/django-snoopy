import cProfile
import datetime
import pstats
import sys
import StringIO
import threading

from snoopy.helpers import get_app_root


_snoopy_request = threading.local()


def clean_profiler_result(result):
    app_root = _snoopy_request.app_root
    lines = result.split("\n")
    relevant_result = lines[:5] + [line for line in lines[6:] if app_root in line]
    return "\n".join(relevant_result)


def get_trace_data(frame):
    return {
        'function': frame.f_code.co_name,
        'filename': frame.f_code.co_filename,
        'module': frame.f_globals.get('__name__'),
        'line_number': frame.f_lineno
    }


class SnoopyRequest:
    """
    Wrapper for managing Django Requests.
    """

    @staticmethod
    def profile(frame, event, args):
        # This still traces almost everything. Need to investigate how to do this less frequently
        # so that it can even be run on production.
        if event == 'call' or event == 'return':
            if not _snoopy_request.settings['BUILTIN_PROFILER_SHOW_ALL_FUNCTIONS']:
                if not _snoopy_request.app_root in frame.f_code.co_filename:
                    return

            trace_data = {
                'event': event,
                'timestamp': datetime.datetime.now()
            }
            trace_data.update(get_trace_data(frame))
            trace_data['parent_frame'] = get_trace_data(frame.f_back)

            _snoopy_request.data['profiler_traces'].append(trace_data)

    @staticmethod
    def register_request(request, settings):
        snoopy_data = {
            'request': request.path,
            'method': request.method,
            'queries': [],
            'profiler_traces': [],
            'custom_attributes': {},
            'start_time': datetime.datetime.now()
        }
        _snoopy_request.request = request
        _snoopy_request.data = snoopy_data
        _snoopy_request.settings = settings

        app_root = get_app_root()
        _snoopy_request.app_root = app_root

        if _snoopy_request.settings.get('USE_CPROFILE'):
            _snoopy_request.profiler = cProfile.Profile()
            _snoopy_request.profiler.enable()

        if _snoopy_request.settings.get('USE_BUILTIN_PROFILER'):
            sys.setprofile(SnoopyRequest.profile)


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
        if _snoopy_request.settings.get('USE_BUILTIN_PROFILER'):
            sys.setprofile(None)

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
