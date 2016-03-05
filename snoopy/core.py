import datetime
from snoopy.helpers import custom_import


class Snoopy:
    DEFAULT_OUTPUT_CLASS = 'snoopy.output.LogOutput'

    @staticmethod
    def register_request(request):
        snoopy_data = {
            'request': request.path,
            'method': request.method,
            'start_time': datetime.datetime.now()
        }
        request._snoopy_data = snoopy_data

    @staticmethod
    def record_response(request, response):
        snoopy_data = request._snoopy_data
        snoopy_data['end_time'] = datetime.datetime.now()
        snoopy_data['total_request_time'] = \
            (snoopy_data['end_time'] - snoopy_data['start_time']).\
            total_seconds()

        from django.conf import settings
        output_cls_name = getattr(
            settings, 'SNOOPY_OUTPUT_CLASS', Snoopy.DEFAULT_OUTPUT_CLASS)
        output_cls = custom_import(output_cls_name)
        output_cls.save_request_data(snoopy_data)
