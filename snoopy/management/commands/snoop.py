from django.core.management.base import BaseCommand

import json
from optparse import make_option

from snoopy.trace_analyzer import TraceAnalyzer


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--trace-file-path',
                    help='trace output file location'),
    )

    def handle(self, trace_file_path, **kwargs):
        request_data = json.loads(open(trace_file_path).read())
        analyzer = TraceAnalyzer(request_data)
        analyzer.analyze()
