=============
Django Snoopy
=============

Django Snoopy is a pluggable profiling tool for Django Apps

-----------
Quick Start
-----------

1. Add `snoopy.middleware.SnoopyProfilerMiddleware` to MIDDLEWARE_CLASSES
2. (Optional) Configure Output if you don't want to use the default log file output
3. Profile your code!

--------------------------
Setting Custom Attributes:
--------------------------
In case you want to track something specific to your app, you can do this:

from snoopy.request import SnoopyRequest
SnoopyRequest.record_custom_attributes({'key': 'value'})

Any value set twice will just be overridden.

IMPORTANT: The data passed into this MUST be a JSON serializable dictionary.
