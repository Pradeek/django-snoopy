import datetime
import json
import os
import urllib2


def default_json_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    raise TypeError('Not sure how to serialize %s' % (obj,))


class OutputBase:
    @staticmethod
    def save_request_data(request_data):
        raise NotImplementedError()


class LogOutput(OutputBase):
    DEFAULT_FILE_PREFIX = 'snoopy_'

    @staticmethod
    def save_request_data(request_data):
        from django.conf import settings
        file_prefix = getattr(
            settings, 'SNOOPY_FILE_PREFIX', LogOutput.DEFAULT_FILE_PREFIX)
        file_path = file_prefix + request_data['end_time'].isoformat() + '.log'
        with open(os.path.join(settings.LOGS_DIR, file_path), "w") as output:
            result = json.dumps(request_data, default=default_json_serializer)
            output.write(result)


# Example for extension.
# Future uses: Post to Elasticsearch / InfluxDB / StatsD
class HTTPOutput(OutputBase):
    @staticmethod
    def save_request_data(request_data):
        from django.conf import settings
        if hasattr(settings, 'SNOOPY_HTTP_OUTPUT_URL'):
            url = settings.SNOOPY_HTTP_OUTPUT_URL
            data = json.dumps(request_data, default=default_json_serializer)
            request = urllib2.Request(
                url, data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(request)
            response.read()
            response.close()
