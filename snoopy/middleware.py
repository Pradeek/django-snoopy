from snoopy.core import Snoopy


class SnoopyProfilerMiddleware(object):
    def process_request(self, request):
        Snoopy.register_request(request)

    def process_response(self, request, response):
        Snoopy.record_response(request, response)
        return response
