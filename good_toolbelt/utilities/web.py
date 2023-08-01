import typing
import requests
import urllib.parse
from pathlib import Path


with open(
    Path(__file__).parent.parent.joinpath("data", "short_url_providers.txt"),
    "r",
) as f:
    SHORT_URLS = set(f.read().splitlines())


def is_short_url(url: str) -> bool:
    """Check if a url is a short url"""
    parsed = urllib.parse.urlsplit(url)
    if parsed.netloc in SHORT_URLS:
        return True
    return False


def follow_redirects(
    url, return_redirect_chain=False
) -> typing.Union[str, tuple, None]:
    """Follow redirects for a url"""
    chain = []
    try:
        r = requests.head(str(url), allow_redirects=True, timeout=3)
        chain = [resp.url for resp in r.history]
    except Exception as e:
        r = e  # type: ignore

    if return_redirect_chain:
        return r.request.url, chain

    return r.request.url


class ParsedURL(typing.NamedTuple):
    scheme: str
    netloc: str
    path: str
    query: typing.Dict[str, typing.List[str]]
    fragment: str
    original: str = ""

    def __hash__(self):
        return hash(self.as_string)

    @classmethod
    def from_string(cls, url: str, force_ssl: bool = True):
        parsed = urllib.parse.urlsplit(url)
        return cls(
            scheme="https" if force_ssl else parsed.scheme,
            netloc=parsed.netloc.lower(),
            path=parsed.path,
            query=urllib.parse.parse_qs(parsed.query),
            fragment=parsed.fragment,
            original=url,
        )

    @property
    def as_string(self):
        return urllib.parse.urlunsplit(
            (
                self.scheme,
                self.netloc,
                self.path,
                urllib.parse.urlencode(self.query),
                self.fragment
            )
        )

    @property
    def clean(self):
        ignore_parts = [
            'utm',
            'clid',
            'src',
            'ncid',
            'cmp',
            'cid',
            'share',
            'ref',
            'source',
            'email',
            'smid',
            'type',
            'via',
            'code'
        ]

        ignore_whole = [
            's',
            'feature',
            'amount',
            'sr',
            'mod',
            'm',
            'taid',
            't',
            'mibextid',

        ]

        return urllib.parse.urlunsplit(
            (
                self.scheme,
                self.netloc,
                self.path,
                urllib.parse.urlencode({
                    k: v[0] for k, v in self.query.items()
                    if k.lower() not in ignore_whole and
                    not any(part in k.lower() for part in ignore_parts)
                }),
                ''
            )
        )
