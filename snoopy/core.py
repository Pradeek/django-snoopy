import datetime

from django.db.models.sql.compiler import SQLCompiler, SQLInsertCompiler

from snoopy.helpers import custom_import
from snoopy.query_tracker import execute_sql, execute_insert_sql


class Snoopy:
    DEFAULT_OUTPUT_CLASS = 'snoopy.output.LogOutput'
    # NOT THREAD-SAFE!!!
    current_request = None

    @classmethod
    def _injectSQLTrackers(cls):
        """
        Need to patch each of these SQL Compilers which override the execute_sql method
        """
        if not hasattr(SQLCompiler, '_snoopy_execute_sql'):
            SQLCompiler._snoopy_execute_sql = SQLCompiler.execute_sql
            SQLCompiler.execute_sql = execute_sql
        if not hasattr(SQLInsertCompiler, '_snoopy_execute_insert_sql'):
            SQLInsertCompiler._snoopy_execute_insert_sql = SQLInsertCompiler.execute_sql
            SQLInsertCompiler.execute_sql = execute_insert_sql

    @classmethod
    def register_request(cls, request):
        snoopy_data = {
            'request': request.path,
            'method': request.method,
            'queries': [],
            'start_time': datetime.datetime.now()
        }
        request._snoopy_data = snoopy_data
        cls._injectSQLTrackers()
        cls.current_request = request

    @classmethod
    def record_query(cls, query_data):
        query_data['total_query_time'] = \
            (query_data['end_time'] - query_data['start_time'])
        cls.current_request._snoopy_data['queries'].append(query_data)

    @classmethod
    def record_response(cls, request, response):
        snoopy_data = request._snoopy_data
        snoopy_data['end_time'] = datetime.datetime.now()
        snoopy_data['total_request_time'] = \
            (snoopy_data['end_time'] - snoopy_data['start_time'])

        from django.conf import settings
        output_cls_name = getattr(
            settings, 'SNOOPY_OUTPUT_CLASS', Snoopy.DEFAULT_OUTPUT_CLASS)
        output_cls = custom_import(output_cls_name)
        output_cls.save_request_data(snoopy_data)
