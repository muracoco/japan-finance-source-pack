from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

JST = timezone(timedelta(hours=9))
USER_AGENT = "japan-finance-source-pack/0.1"


class RetrievalError(RuntimeError):
    """A remote retrieval failure safe to include in pack limitations."""


def _error_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc.rsplit("@", 1)[-1], parts.path, "", ""))


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def make_url(base: str, params: dict[str, Any]) -> str:
    clean = {key: value for key, value in params.items() if value not in (None, "")}
    if not clean:
        return base
    return f"{base}?{urlencode(clean)}"


def http_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> dict[str, Any]:
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        exc.close()
        error = f"HTTP {exc.code} for {_error_url(url)}"
    except (URLError, OSError, HTTPException) as exc:
        error = f"Network retrieval failed for {_error_url(url)} ({type(exc).__name__})"
    except (json.JSONDecodeError, UnicodeDecodeError):
        error = f"Invalid JSON response for {_error_url(url)}"
    else:
        if not isinstance(payload, dict):
            raise RetrievalError(f"Expected a JSON object from {_error_url(url)}")
        return payload
    # Raise outside the handler so the original URL, reason and body are not chained.
    raise RetrievalError(error) from None


def http_text(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> str:
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        exc.close()
        error = f"HTTP {exc.code} for {_error_url(url)}"
    except (URLError, OSError, HTTPException) as exc:
        error = f"Network retrieval failed for {_error_url(url)} ({type(exc).__name__})"
    raise RetrievalError(error) from None


def source(
    *,
    source_name: str,
    source_type: str,
    source_url: str,
    is_primary_source: bool,
    data_delay_note: str,
    limitations: list[str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "source_name": source_name,
        "source_type": source_type,
        "source_url": source_url,
        "retrieved_at": now_jst(),
        "is_primary_source": is_primary_source,
        "data_delay_note": data_delay_note,
        "limitations": limitations or [],
    }
    item.update(extra)
    return item


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
