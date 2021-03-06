import datetime
import json
import os
import urllib2

from snoopy.helpers import get_app_root, default_json_serializer


class OutputBase:
    @staticmethod
    def save_request_data(request_data):
        raise NotImplementedError()


class LogOutput(OutputBase):
    DEFAULT_FILE_PREFIX = 'snoopy_'

    @staticmethod
    def save_request_data(request_data):
        from django.conf import settings
        file_prefix = LogOutput.DEFAULT_FILE_PREFIX
        file_path = file_prefix + request_data['end_time'].isoformat() + '.log'
        app_root = get_app_root()
        log_dir = getattr(settings, 'SNOOPY_LOG_OUTPUT_DIR', app_root)
        with open(os.path.join(log_dir, file_path), "w") as output:
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


class ElasticsearchOutput(OutputBase):
    @staticmethod
    def save_request_data(request_data):
        from django.conf import settings
        if hasattr(settings, 'SNOOPY_ELASTICSEARCH_OUTPUT_URL'):
            start_time = datetime.datetime.now()
            data = request_data
            index = request_data['start_time'].date().isoformat().replace('-', '.')
            url = settings.SNOOPY_ELASTICSEARCH_OUTPUT_URL + 'snoopy-' + index + '/request/'
            data = json.dumps(request_data, default=default_json_serializer)
            request = urllib2.Request(
                url, data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(request)
            response.read()
            response.close()
            end_time = datetime.datetime.now()
            print 'Posted to Elasticsearch in %0.4f' % ((end_time - start_time).total_seconds())
