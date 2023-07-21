import typing
import collections


tree = lambda: collections.defaultdict(tree)  # noqa: E731


def deduplicate_dicts(dicts) -> list:
    """Remove duplicate dictionaries from a list of dictionaries"""
    new_dicts = []
    for d in dicts:
        if d not in new_dicts:
            new_dicts.append(d)
    return new_dicts


def merge_lists(lists) -> list:
    merged = []
    for _list in lists:
        for elem in _list:
            if elem not in merged:
                merged.append(elem)
    return merged


def merge_dicts(
    dicts: list[dict],
    keep_unique_values: bool = False,
    keep_unique_value_keys: list = [],
) -> dict:
    merged: typing.Dict = {}
    for d in deduplicate_dicts(dicts):

        for key, value in d.items():
            if isinstance(value, dict):
                if key in merged:
                    # if already existing key is a list, convert it to a dict
                    if isinstance(merged[key], list):
                        merged[key] = {k: v for k, v in enumerate(merged[key])}
                    merged_dict = merge_dicts(
                        [merged[key], value],
                        keep_unique_values=keep_unique_values,
                        keep_unique_value_keys=keep_unique_value_keys,
                    )
                    merged[key] = merged_dict
                else:
                    merged[key] = value
            elif isinstance(value, list):
                if key in merged:
                    # merged_list: typing.List = merged[key]
                    for elem in value:
                        if elem not in merged[key]:
                            merged[key].append(elem)
                else:
                    merged[key] = value
            else:
                if value is not None and value != "":
                    if (
                        keep_unique_values and key in merged
                    ) or key in keep_unique_value_keys:
                        if not isinstance(merged[key], list):
                            merged[key] = [merged[key]]

                        if value not in merged[key]:
                            merged[key].append(value)

                        if len(merged[key]) == 1:
                            merged[key] = merged[key][0]
                    else:
                        merged[key] = value

    return {k: v for k, v in merged.items() if v is not None and v != ""}


def recursive_default(obj, *keys) -> typing.Any:
    for key in keys:
        if key in obj:
            return obj.get(key)
    return None


def recursive_get(obj, *keys) -> typing.Any:
    if obj is None:
        return None
    if len(keys) == 0:
        return obj

    if isinstance(keys[0], list):
        _obj = recursive_default(obj, *keys[0])
        if isinstance(_obj, dict):
            return recursive_get(_obj, *keys[1:])
        else:
            return _obj

    if keys[0] in obj:
        return recursive_get(obj.get(keys[0]), *keys[1:])
    return None


def flatten_list(lst) -> list:
    """Flatten a list of lists"""
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened


def map_object(obj, **mappers) -> dict:
    """Apply a function to the value of specific keys in a dictionary"""
    _new = {}
    for k, v in obj.items():
        if k in mappers and v:
            if callable(mappers[k]):
                _v = mappers[k](v)
                if _v:
                    _new[k] = _v
                else:
                    _new[k] = v
            else:
                _new[k] = v
        else:
            _new[k] = v
    return _new


def recursive_convert_lists(obj: typing.Any) -> typing.Any:
    # find any nested objects that have only numerically indexed keys (stored as strings)
    # and convert them to lists
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and all(
                [isinstance(k, str) and k.isdigit() for k in v.keys()]
            ):
                obj[k] = [recursive_convert_lists(v) for v in v.values()]
            elif isinstance(v, dict):
                obj[k] = recursive_convert_lists(v)
    return obj


def recursive_dict_convert(d):
    if isinstance(d, collections.defaultdict):
        return {k: recursive_dict_convert(v) for k, v in d.items()}
    return d


def array_index_on(collection, field):
    index = collections.defaultdict(set)
    for idx, d in enumerate(collection):
        index[d[field]].add(idx)
    return index


# Tuple Functions

def tuple_get_common_prefix(lst: list[tuple]) -> list[tuple]:
    # Get the minimum length of a tuple in the list
    min_length = min([len(tpl) for tpl in lst])

    # Find the common prefix by iterating through the elements
    # of each tuple and comparing them
    common_prefix = []
    for i in range(min_length):
        element = lst[0][i]
        common = True
        for tuple in lst:
            if tuple[i] != element:
                common = False
                break
        if common:
            common_prefix.append(element)
        else:
            break

    return common_prefix


def tuple_get_common_suffix(lst: list[tuple]) -> list[tuple]:
    # Get the minimum length of a tuple in the list
    min_length = min([len(tpl) for tpl in lst])

    # Find the common suffix by iterating through the elements
    # of each tuple in reverse order and comparing them
    common_suffix = []
    for i in range(min_length):
        element = lst[0][-i - 1]
        common = True
        for tuple in lst:
            if tuple[-i - 1] != element:
                common = False
                break
        if common:
            common_suffix.append(element)
        else:
            break

    # Reverse the common suffix list to get it
    # in the correct order
    common_suffix.reverse()

    return common_suffix
