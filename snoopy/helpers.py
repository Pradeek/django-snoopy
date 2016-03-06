import os
import importlib


def custom_import(cls_path):
    module_name, class_name = cls_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


def get_app_root():
    settings_module = __import__(os.environ['DJANGO_SETTINGS_MODULE'])
    settings_path = settings_module.__path__[0]
    app_root = os.path.abspath(os.path.join(settings_path, os.pardir))
    return app_root
