from collections import defaultdict

from snoopy.helpers import get_app_root, default_json_serializer
from snoopy.trace import Trace

import datetime
import json
import re


DJANGO_DB_QUERY_FILE = "django/db/models/query.py"


class TraceAnalyzer(object):
    def __init__(self, data):
        self.trace_data = data
        self.query_info = {}
        self.profiler_info = {}
        self.app_root = get_app_root()


    def process_builtin_profiler_result(self):
        self.profiler_info['total_traces'] = len(self.trace_data['profiler_traces'])
        if self.profiler_info['total_traces'] == 0:
            return

        # Because it contains both call/return events
        self.profiler_info['total_traces'] /= 2
        self.profiler_info['traces'] = Trace(self.trace_data['profiler_traces'])


    def summarize_profiler_result(self):
        print json.dumps(self.profiler_info['traces'], indent=4, default=default_json_serializer)


    def process_traceback_line(self, line):
        parts = line.strip().split(' ')
        return {
            "file_name": parts[1].split('"')[1],
            "function_name": parts[5].strip(),
            "line_number": parts[3].split(",")[0],
            "line": " ".join(parts[6:]).strip()
        }


    def process_query(self, query):
        query_data = {
            'model': query['model'],
            'total_query_time': query['total_query_time'],
            'query_type': 'read'
        }
        previous_line = ""
        best_non_app_code_line = ""
        best_app_code_line = ""

        for line in reversed(query['traceback']):
            if DJANGO_DB_QUERY_FILE in previous_line and not DJANGO_DB_QUERY_FILE in line:
                best_non_app_code_line = self.process_traceback_line(line)
            if self.app_root in line:
                best_app_code_line = self.process_traceback_line(line)
                break
            previous_line = line

        if best_app_code_line != "":
            best_line = best_app_code_line
        else:
            best_line = best_non_app_code_line
        query_data['code'] = best_line
        return query_data


    def process_queries(self):
        self.query_info['total_queries'] = len(self.trace_data['queries'])
        if self.query_info['total_queries'] == 0:
            return

        self.query_info['stats'] = {
            'query_type': defaultdict(int),
            'model': {},
        }
        self.query_info['total_time_on_queries'] = 0.0
        for query in self.trace_data['queries']:
            query_data = self.process_query(query)
            if not query_data:
                continue
            self.query_info['stats']['query_type'][query_data['query_type']] += 1

            if query_data['model'] not in self.query_info['stats']['model']:
                new_model_info = {
                    'query_type': {
                        query_data['query_type'] : {
                            'count': 0,
                            'total_query_time': 0.0,
                            'max_query_time': 0.0,
                            'max_query_time_code': None
                        }
                    },
                    'total_query_count': 0
                }

            self.query_info['stats']['model'][query_data['model']] = new_model_info

            model_info = self.query_info['stats']['model'][query_data['model']]
            model_info['total_query_count'] += 1
            model_query_type_info = model_info['query_type'][query_data['query_type']]
            model_query_type_info['count'] += 1
            model_query_type_info['total_query_time'] += query_data['total_query_time']

            if model_query_type_info['max_query_time'] < query_data['total_query_time']:
                model_query_type_info['max_query_time'] = query_data['total_query_time']
                model_query_type_info['max_query_time_code'] = query_data['code']

            self.query_info['total_time_on_queries'] += query_data['total_query_time']


    def summarize_queries(self):
        if self.query_info['total_queries'] == 0:
            return

        print "Total SQL Queries: %d" % self.query_info['total_queries']
        print 'Total time on SQL Queries: %0.4f' % self.query_info['total_time_on_queries']
        print 'Stats on SQL Queries:'
        print json.dumps(self.query_info['stats'], indent=4)


    def summarize(self):
        # print "Total Request Time: %0.4f" % self.trace_data['total_request_time']
        # print "URL: " + self.trace_data['request']
        # self.summarize_queries()
        self.summarize_profiler_result()


    def analyze(self):
        self.process_queries()
        self.process_builtin_profiler_result()
        # TODO: Do the cProfiler processing as well
        self.summarize()
