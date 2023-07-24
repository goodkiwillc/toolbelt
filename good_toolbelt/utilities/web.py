import typing
import requests
import urllib.parse


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

    @classmethod
    def from_string(cls, url: str, force_ssl: bool = True):
        parsed = urllib.parse.urlsplit(url)
        return cls(
            scheme="https" if force_ssl else parsed.scheme,
            netloc=parsed.netloc.lower(),
            path=parsed.path,
            query=urllib.parse.parse_qs(parsed.query),
            fragment=parsed.fragment,
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
        keep_params = ('q', 'id',)
        return urllib.parse.urlunsplit(
            (
                self.scheme,
                self.netloc,
                self.path,
                urllib.parse.urlencode({
                    k: v[0] for k, v in self.query.items()
                    if k in keep_params
                }),
                ''
            )
        )
