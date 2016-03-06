Django Snoopy
=============

Django Snoopy is a pluggable profiling tool for Django Apps.

Quick Start:
------------
1. Add `snoopy.middleware.SnoopyProfilerMiddleware` to MIDDLEWARE_CLASSES
2. (Optional) Configure Output if you don't want to use the default log file output
3. Profile your code!

Setting Custom Attributes:
--------------------------
In case you want to track something specific to your app, you can do this:
```
from snoopy.request import SnoopyRequest
SnoopyRequest.record_custom_attributes({
    'key': 'value'
})
```
Any value set twice will just be overridden.

**IMPORTANT** The data passed into this MUST be a JSON serializable dictionary.

Settings:
---------
You can set these in your Django settings.py file to configure how Snoopy works

SNOOPY_COLLECT_SQL_QUERIES: True
  - Track all SQL queries done via the Django ORM

SNOOPY_OUTPUT_CLASS: 'snoopy.output.LogOutput'
  - Set the class that defines how the collected info is processed at the end of the request. The options available out of the box are:
    - `snoopy.output.LogOutput`: This will create a file for each request in the folder specified by `SNOOPY_LOG_OUTPUT_DIR`. Defaults to the root folder of the app
    - `snoopy.output.HTTPOutput`: This will make a JSON formatted HTTP POST with the data in `SNOOPY_HTTP_OUTPUT_URL`

  - You can write your own Output class. All you need to do is to extend `snoopy.output.OutputBase` and implement the `save_request_data` method.

SNOOPY_USE_CPROFILE: False
  - Set to True if you want profiling

SNOOPY_CPROFILE_SHOW_ALL_FUNCTIONS: True
  - If this option is set to False, django-snoopy will take the parent directory of the main django settings file as the project root and will only list items in the cProfile output that are files under this directory (your actual app code)


DEFAULT_USE_BUILTIN_PROFILER': False
  - Set to True if you want to use the built-in profiler/tracer

DEFAULT_BUILTIN_PROFILER_SHOW_ALL_FUNCTIONS': True
  - Like the cProfile option counterpart, allows you to specify if you want data about all or just your own code.


TODO:

- [x] Basic request profiling with pluggable outputs
- [x] SQL Query tracking
- [x] Custom attribute tracking
- [x] Make tracking configurable
- [x] Actual Python code profiling
- [x] Lightweight function tracing.
- [ ] Analyzers / Visualizers
- [ ] Tests!

Future Ideas:
- Integrate with [line_profiler](https://github.com/rkern/line_profiler)
- Debugging?
