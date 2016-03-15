from collections import defaultdict

import datetime
import json
import re

from snoopy.helpers import default_json_serializer


TRACE_KEY_REGEX = r"([^:]+)::([^:]+):([\d]+)"
PYTHON_DATEFORMAT = "%Y-%m-%dT%H:%M:%S.%f"
TRACE_THRESHOLD = 0 #  Bring config for this in the future


class FunctionCall(object):
    def __init__(self, trace_data, previous=None):
        self.key = trace_data['key']
        self.queries = []
        self.next = []
        self.previous = previous
        self.start_time = datetime.datetime.strptime(trace_data['start_time'], PYTHON_DATEFORMAT)
        self.module, self.function, self.line_number = re.search(TRACE_KEY_REGEX, trace_data['key']).groups()


    def record_return(self, data):
        module, function, line_number = re.search(TRACE_KEY_REGEX, data['key']).groups()
        assert module == self.module
        assert function == self.function
        self.end_time = datetime.datetime.strptime(data['end_time'], PYTHON_DATEFORMAT)
        self.end_line_number = line_number
        self.total_time = (self.end_time - self.start_time).total_seconds()


    def record_query(self, query):
        self.queries.append({
            'start_time': query['start_time'],
            'query_time': query['total_query_time'],
            'query': query['query'],
            'model': query['model'],
            'key': query['function_call_key']
        })


    def to_representation(self):
        result = {}
        result[self.key] = {
            'total_time': self.total_time,
            'queries': self.queries,
            'stats': {
                'call': self.start_time,
                'return': self.end_time,
                'line_numbers': {
                    'start': self.line_number,
                    'end': self.end_line_number
                }
            },
            'next': self.next
        }
        return result


    def __str__(self):
        return json.dumps(self.to_representation(), indent=4, default=default_json_serializer)


class Trace(object):
    """
    Represents an actual trace of a Request.

    For a program like

    def a():
        pass
    def b():
        a()

    b()

    the trace will return

    {
        'b': {
            'total_time': ...,
            'stats': {...},
            'next': [
                {
                    'a': {
                        'total_time': ...,
                        'stats': {...},
                        'next': []
                    }
                }
            ]
        }
    }

    TODO: Combine trace info with SQL timings
    """
    def __init__(self, trace_data, query_data):
        self.raw_data = {
            'trace_data': trace_data,
            'query_data': query_data
        }
        self.root = None

        self.nodes = []
        self.function_calls = defaultdict(list)
        self.current_node = None

        self.process(trace_data, query_data)


    def __str__(self):
        return str(self.root)


    def to_representation(self):
        return self.root


    def process_trace(self, entry):
        event = 'call' if 'start_time' in entry else 'return'
        if event == 'call':
            trace = FunctionCall(entry, previous=self.current_node)
            self.nodes.append(trace)
            self.current_node = trace
        elif event == 'return':
            trace = self.nodes.pop()
            trace.record_return(entry)
            self.function_calls[trace.key].append(trace)
            self.current_node = trace.previous
            if self.current_node:
                if trace.total_time > TRACE_THRESHOLD:
                    self.current_node.next.append(trace)
        return trace


    def find_node(self, key_info):
        key, timestamp = key_info[0], datetime.datetime.strptime(key_info[1], PYTHON_DATEFORMAT)
        for trace in self.function_calls[key]:
            if trace.start_time == timestamp:
                return trace
        return self.root


    def process(self, trace_data, query_data):
        first_entry = trace_data.pop(0)

        # Process traces
        self.root = self.process_trace(first_entry)
        for entry in trace_data:
            self.process_trace(entry)

        # Process queries
        self.current_node = self.root
        for entry in query_data:
            node = self.find_node(entry['function_call_key'])
            node.record_query(entry)

        return self.root


def main():
    data = [
        {
            "start_time": "2016-03-12T20:56:30.812114",
            "key": "snoopy.trace::b:5"
        },
        {
            "start_time": "2016-03-12T20:56:30.815226",
            "key": "snoopy.trace::a:2"
        },
        {
            "end_time": "2016-03-12T20:56:30.815337",
            "key": "snoopy.trace::a:3"
        },
        {
            "end_time": "2016-03-12T20:56:30.815351",
            "key": "snoopy.trace::b:7"
        }
    ]
    query_data = [
        {
            "start_time": "2016-03-12T20:56:30.815310",
            "query": "SELECT * FROM Foo1;"
        },
        {
            "start_time": "2016-03-12T20:56:30.815321",
            "query": "SELECT * FROM Foo2;"
        },
        {
            "start_time": "2016-03-12T20:56:30.815346",
            "query": "SELECT * FROM Foo3;"
        },        {
            "start_time": "2016-03-12T20:56:30.815350",
            "query": "SELECT * FROM Foo4;"
        }

    ]
    print Trace(data, query_data)


if __name__ == '__main__':
    main()
