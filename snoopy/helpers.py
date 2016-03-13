import datetime
import importlib
import os


def default_json_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if hasattr(obj, 'to_representation'):
        return obj.to_representation()
    raise TypeError('Not sure how to serialize %s %s' % (type(obj),obj,))


def custom_import(cls_path):
    module_name, class_name = cls_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


def get_app_root():
    settings_module = __import__(os.environ['DJANGO_SETTINGS_MODULE'])
    settings_path = settings_module.__path__[0]
    app_root = os.path.abspath(os.path.join(settings_path, os.pardir))
    return app_root
