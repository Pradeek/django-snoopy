from django.db.models.sql.compiler import SQLCompiler, SQLInsertCompiler

from snoopy.helpers import custom_import
from snoopy.query_tracker import execute_sql, execute_insert_sql
from snoopy.request import SnoopyRequest


class Snoopy:
    DEFAULT_SETTINGS = {
        'DEFAULT_USE_CPROFILE': False,
        'DEFAULT_CPROFILE_SHOW_ALL_FUNCTIONS': True,
        'DEFAULT_COLLECT_SQL_QUERIES': True,
        'DEFAULT_OUTPUT_CLASS': 'snoopy.output.LogOutput'
    }

    @staticmethod
    def get_setting(setting):
        from django.conf import settings
        default_setting = 'DEFAULT_' + setting
        custom_setting = 'SNOOPY_' + setting
        value = getattr(
            settings, custom_setting, Snoopy.DEFAULT_SETTINGS[default_setting])
        return value


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
        if Snoopy.get_setting('COLLECT_SQL_QUERIES'):
            Snoopy._injectSQLTrackers()

        SnoopyRequest.register_request(request, {
            'USE_CPROFILE': Snoopy.get_setting('USE_CPROFILE'),
            'CPROFILE_SHOW_ALL_FUNCTIONS': Snoopy.get_setting('CPROFILE_SHOW_ALL_FUNCTIONS')
        })


    @staticmethod
    def record_response(request, response):
        snoopy_data = SnoopyRequest.register_response(response)
        output_cls_name = Snoopy.get_setting('OUTPUT_CLASS')
        output_cls = custom_import(output_cls_name)
        output_cls.save_request_data(snoopy_data)
