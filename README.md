Django Snoopy
=============

Django Snoopy is a pluggable profiling tool for Django Apps.

Quick Start:
------------
1. Add `snoopy.middleware.SnoopyProfilerMiddleware` to MIDDLEWARE_CLASSES
2. (Optional) Configure Output if you don't want to use the default log file output
3. Profile your code!


TODO:

- [x] Basic request profiling with pluggable outputs
- [x] SQL Query tracking
- [ ] Custom attribute tracking
- [ ] Actual Python code profiling
- [ ] Lightweight function tracing. See [Dropbox and Nylas blog posts](https://news.ycombinator.com/item?id=10811373)
- [ ] Analyzers / Visualizers
