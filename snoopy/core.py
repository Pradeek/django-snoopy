from django.db.models.sql.compiler import SQLCompiler, SQLInsertCompiler

from snoopy.helpers import custom_import
from snoopy.query_tracker import execute_sql, execute_insert_sql
from snoopy.request import SnoopyRequest

class Snoopy:
    DEFAULT_OUTPUT_CLASS = 'snoopy.output.LogOutput'

    @staticmethod
    def _injectSQLTrackers():
        """
        Need to patch each of these SQL Compilers which override the execute_sql method
        """
        if not hasattr(SQLCompiler, '_snoopy_execute_sql'):
            SQLCompiler._snoopy_execute_sql = SQLCompiler.execute_sql
            SQLCompiler.execute_sql = execute_sql
        if not hasattr(SQLInsertCompiler, '_snoopy_execute_insert_sql'):
            SQLInsertCompiler._snoopy_execute_insert_sql = SQLInsertCompiler.execute_sql
            SQLInsertCompiler.execute_sql = execute_insert_sql


    @staticmethod
    def register_request(request):
        Snoopy._injectSQLTrackers()
        SnoopyRequest.register_request(request)


    @staticmethod
    def record_response(request, response):
        snoopy_data = SnoopyRequest.register_response(response)
        from django.conf import settings
        output_cls_name = getattr(
            settings, 'SNOOPY_OUTPUT_CLASS', Snoopy.DEFAULT_OUTPUT_CLASS)
        output_cls = custom_import(output_cls_name)
        output_cls.save_request_data(snoopy_data)
