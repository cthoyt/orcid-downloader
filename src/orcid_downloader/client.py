"""A web-based client for ORCID."""

import re
from typing import Any, Literal

import requests
from lxml import etree
from pystow.constants import TimeoutHint

from .version import VERSION

__all__ = [
    "get_orcid_dict",
    "get_orcid_xml",
]

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def get_orcid_dict(orcid: str, *, timeout: TimeoutHint = None) -> dict[str, Any]:
    """Get ORCID as JSON."""
    return _get(orcid, format="json", timeout=timeout).json()  # type:ignore


def get_orcid_xml(orcid: str, *, timeout: TimeoutHint = None) -> etree.Element:
    """Get ORCID as JSON."""
    res = _get(orcid, format="xml", timeout=timeout)
    return etree.fromstring(res.content)


def _get(
    orcid: str, *, format: Literal["json", "xml"], timeout: TimeoutHint = None
) -> requests.Response:
    """Get an ORCID record from the public API."""
    if not ORCID_RE.match(orcid):
        raise ValueError(f"Invalid ORCID: {orcid}")
    if timeout is not None:
        timeout = 5
    res = requests.get(
        f"https://orcid.org/{orcid}",
        headers={"Accept": f"application/{format}", "User-Agent": f"orcid-downloader v{VERSION}"},
        timeout=timeout,
    )
    res.raise_for_status()
    return res
