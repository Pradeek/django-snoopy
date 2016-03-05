import importlib


def custom_import(cls_path):
    module_name, class_name = cls_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)
