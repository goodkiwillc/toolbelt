import typing
import json
import yaml
from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


def str_presenter(dumper, data):
    text_list = [line.rstrip() for line in data.splitlines()]
    fixed_data = "\n".join(text_list)
    if len(text_list) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", fixed_data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", fixed_data)


Dumper.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(
    str, str_presenter
)  # to use with safe_dum


def yaml_load(file_path) -> dict:
    with open(file_path, "r") as f:
        return load(f, Loader=Loader)


def yaml_loads(text) -> dict:
    return load(text, Loader=Loader)


def yaml_dump(data, file_path) -> None:
    with open(file_path, "w") as f:
        dump(data, f, Dumper=Dumper, allow_unicode=True)


def yaml_dumps(data) -> str:
    return dump(data, Dumper=Dumper, allow_unicode=True)


def expand_nested_json(obj) -> dict:
    """Find nested json objects within a dictionary and parse them into objects"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                try:
                    _obj = json.loads(v)
                    obj[k] = expand_nested_json(_obj)
                except ValueError:
                    obj[k] = v
            else:
                obj[k] = expand_nested_json(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                try:
                    _obj = json.loads(v)
                    obj[i] = expand_nested_json(_obj)
                except ValueError:
                    obj[i] = v
            else:
                obj[i] = expand_nested_json(v)
    return obj


# def get_records_from_glob(
#     path: str, limit: int = None, filters: typing.List[typing.Callable] = []
# ) -> typing.List[dict]:
#     records = []
#     for file in glob.glob(path):
#         for record in jsonlines.open(file, loads=orjson.loads):
#             if all([f(record) for f in filters]) or len(filters) == 0:
#                 records.append(record)
#             if limit and len(records) >= limit:
#                 return records

#     return records
