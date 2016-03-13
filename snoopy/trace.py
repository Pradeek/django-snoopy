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


    def to_representation(self):
        result = {}
        result[self.key] = {
            'total_time': self.total_time,
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
    def __init__(self, data):
        self.raw_data = data
        self.root = None

        self.nodes = []
        self.current_node = None

        self.process(data)


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
            self.current_node = trace.previous
            if self.current_node:
                if trace.total_time > TRACE_THRESHOLD:
                    self.current_node.next.append(trace)
        return trace


    def process(self, data):
        first_entry = data.pop(0)
        self.root = self.process_trace(first_entry)
        for entry in data:
            self.process_trace(entry)
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
    print Trace(data)


if __name__ == '__main__':
    main()
