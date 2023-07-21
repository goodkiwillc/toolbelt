import typing


def try_chain(
    fns: typing.List[typing.Callable],
    fail=False,
    default_value=None
) -> typing.Callable:
    def _try_chain(value):
        for fn in fns:
            try:
                return fn(value)
            except Exception:
                continue
        if fail:
            raise ValueError(f"Could not process {value}")
        return default_value

    return _try_chain
