import datetime
import traceback

from django.db.models.sql.compiler import SQLUpdateCompiler, SQLDeleteCompiler
from django.db.models.sql.datastructures import EmptyResultSet


QUERY_TYPE_READ = 'read'
QUERY_TYPE_WRITE = 'write'
QUERY_TYPE_UPDATE = 'update'
QUERY_TYPE_DELETE = 'delete'


def execute_sql(self, *args, **kwargs):
    """
    Adapted from django/db/models/sql/compiler.py:SQLCompiler:execute_sql

    Run the query against the database and returns the result(s). The
    return value is a single data item if result_type is SINGLE, or an
    iterator over the results if the result_type is MULTI.

    result_type is either MULTI (use fetchmany() to retrieve all rows),
    SINGLE (only retrieve a single row), or None. In this last case, the
    cursor is returned if any query is executed, since it's used by
    subclasses such as InsertQuery). It's possible, however, that no query
    is needed, as the filters describe an empty set. In that case, None is
    returned, to avoid any unnecessary database interaction.
    """
    try:
        sql, params = self.as_sql()
        if not sql:
            raise EmptyResultSet
    except EmptyResultSet:
        if len(args) == 1:
            # result_type is usually passed as the first argument
            result_type = args[0]
        else:
            # Current implementation (as of Django 1.9) has 'multi' as the default value
            result_type = kwargs.get('result_type', 'multi')
        if result_type == 'multi':
            return iter([])
        else:
            return

    # There should be a flag to decide whether or not to pass the params through
    # Useful in order to find generic types of queries
    sql_query = sql % params

    if isinstance(self, SQLUpdateCompiler):
        query_type = QUERY_TYPE_UPDATE
    elif isinstance(self, SQLDeleteCompiler):
        query_type = QUERY_TYPE_DELETE
    else:
        query_type = QUERY_TYPE_READ

    stack_trace = traceback.format_stack()
    query_dict = {
        'query': sql_query,
        'query_type': query_type,
        'traceback': stack_trace,
        'model': "%s.%s" % (self.query.model.__module__, self.query.model.__name__),
        'start_time': datetime.datetime.now(),
    }
    try:
        return self._snoopy_execute_sql(*args, **kwargs)
    finally:
        # This gets called just before the `return`
        query_dict['end_time'] = datetime.datetime.now()
        # TODO: Fix circular import
        from snoopy.core import Snoopy
        Snoopy.record_query(query_dict)


def execute_insert_sql(self, *args, **kwargs):
    stack_trace = traceback.format_stack()
    query_dict = {
        'query': [],
        'query_type': QUERY_TYPE_WRITE,
        'traceback': stack_trace,
        'model': "%s.%s" % (self.query.model.__module__, self.query.model.__name__),
        'start_time': datetime.datetime.now(),
    }
    for sql, params in self.as_sql():
        query_dict['query'].append(sql % params)

    try:
        return self._snoopy_execute_insert_sql(*args, **kwargs)
    finally:
        # This gets called just before the `return`
        query_dict['end_time'] = datetime.datetime.now()
        # TODO: Fix circular import
        from snoopy.core import Snoopy
        Snoopy.record_query(query_dict)
