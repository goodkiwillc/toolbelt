import typing
import base64
import datetime
import json
from dateutil.parser import parse as date_parser
import re

from good_toolbelt.utilities.basic import try_chain
from good_toolbelt.utilities.regex import (
    RE_DOMAIN_NAMES,
    RE_UUID,
    RE_EMAIL,
    RE_HTML,
    RE_PHONE_NUMBER,
    RE_JAVASCRIPT
)


def convert_timestamp(timestamp: str, *formats) -> datetime.datetime:
    for format in formats:
        try:
            return datetime.datetime.strptime(timestamp, format)
        except ValueError:
            pass
    raise ValueError(
        f"Unable to parse timestamp {timestamp} with formats {formats}"
    )


def b64_decode(string) -> str:
    """Decode a base64 string"""

    # check if string is base64
    try:
        if base64.b64encode(
            base64.b64decode(string)
        ).decode("utf-8") == string:
            return base64.b64decode(string).decode("utf-8")
    except Exception:
        pass
    return string


def strptime(format):
    def _strptime(value):
        return datetime.datetime.strptime(value, format)
    return _strptime


def parse_timestamp(
    timestamp: typing.Any,
    *formats,
    raise_error=False,
    as_date=False
) -> typing.Optional[datetime.datetime]:
    if not timestamp:
        return None

    if isinstance(timestamp, datetime.datetime):
        return timestamp

    chain_fns = []

    if len(formats) > 0:
        for fmt in formats:
            chain_fns.append(strptime(fmt))

    chain_fns += [
        strptime("%Y-%m-%dT%H:%M:%S.%fZ"),
        strptime("%Y-%m-%d"),
        lambda x: date_parser.parse(x),
    ]

    output = try_chain(chain_fns, fail=raise_error)(timestamp)
    if output:
        return output.date() if as_date else output
    return None


def type_converter(from_, to_):
    def _converter(value):
        if not value:
            return value
        try:
            match from_, to_:
                case (str, datetime.datetime):
                    return parse_timestamp(value)
                case (str, datetime.date):
                    dt = parse_timestamp(value)
                    return dt.date() if dt else None
                case (str, int):
                    return int(value)
                case (str, float):
                    return float(value)
                case (str, bool):
                    return bool(value)
                case (int, str):
                    return str(value)
                case (float, str):
                    return str(value)
                case (bool, str):
                    return str(value)

        except Exception as e:
            print(e)
            return None
        return value

    return _converter


def to_int(v) -> typing.Optional[int]:
    try:
        return int(v)
    except ValueError:
        return None


def to_float(v) -> typing.Optional[float]:
    try:
        return float(v)
    except ValueError:
        return None



def detect_string_type(string: str):
    # Check for URLs
    if re.match(r"^https?://", string):
        if re.match(r"\.(jpeg|jpg|png|gif|bmp)$", string):
            return "url-image"
        elif re.match(r"\.(mp4|webm|ogv)$", string):
            return "url-video"
        else:
            return "url"

    # Check for UUIDs
    if RE_UUID.match(string):
        return "uuid"

    # # Check for base64-encoded strings
    try:
        if base64.b64encode(base64.b64decode(string)) == string:
            return "base64-encoded-string"
    except Exception:
        pass
    # if re.match(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$', string):
    #   return 'base64-encoded-string'

    # Check for email addresses
    if RE_EMAIL.match(string):
        return "email-address"

    if RE_HTML.match(string):
        return "html"

    # Check for domain names
    if RE_DOMAIN_NAMES.match(string):
        return "domain-name"

    # Check for phone numbers
    if RE_PHONE_NUMBER.match(string):
        return "phone-number"

    # Check for JSON strings
    try:
        json.loads(string)
        return "json-string"
    except ValueError:
        pass

    # Check for JavaScript snippets
    if RE_JAVASCRIPT.match(string):
        return "javascript-snippet"

    # Check for date and timestamp strings
    try:
        datetime.datetime.strptime(string, "%Y-%m-%d")
        return "date-string"
    except ValueError:
        pass
    try:
        date_parser(string)
        return "timestamp-string"
    except Exception:
        pass

    return "unknown"
