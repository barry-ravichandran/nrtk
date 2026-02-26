"""Sphinx extension: selectively show prev/next navigation links.

Only pages listed in the ``prev_next_flow_pages`` configuration value
display prev/next navigation.  For those pages, links pointing outside
the flow are removed so the navigation forms a closed linear sequence.

All other pages have ``prev`` and ``next`` set to ``None``, which
causes the pydata-sphinx-theme's ``prev-next.html`` component to
render nothing.

Configuration (``conf.py``)::

    prev_next_flow_pages = ["index", "getting_started/quickstart", ...]
"""

from __future__ import annotations

import logging
from typing import Any, cast

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder

logger = logging.getLogger(__name__)


def _filter_prev_next(
    _app: Sphinx,
    _pagename: str,
    _templatename: str,
    context: dict[str, Any],
    _doctree: object,
) -> None:
    """Remove or constrain prev/next links based on the flow allowlist.

    For pages outside the flow, both ``prev`` and ``next`` are set to
    ``None``.  For flow pages, ``prev`` and ``next`` are rebuilt to
    point only to adjacent pages within the flow.
    """
    flow_pages: tuple[str, ...] = tuple(_app.config.prev_next_flow_pages)
    flow_set: frozenset[str] = frozenset(flow_pages)

    if _pagename not in flow_set:
        context["prev"] = None
        context["next"] = None
        return

    builder = cast(StandaloneHTMLBuilder, _app.builder)
    idx = flow_pages.index(_pagename)

    context["prev"] = _build_link(builder, from_page=_pagename, to_page=flow_pages[idx - 1]) if idx > 0 else None
    context["next"] = (
        _build_link(builder, from_page=_pagename, to_page=flow_pages[idx + 1]) if idx < len(flow_pages) - 1 else None
    )


def _build_link(
    builder: StandaloneHTMLBuilder,
    *,
    from_page: str,
    to_page: str,
) -> dict[str, str]:
    """Build a prev/next link dict matching Sphinx's expected format.

    Returns ``{"link": "<relative-url>", "title": "<page-title>"}``
    which is the structure consumed by ``prev-next.html``.
    """
    link = builder.get_relative_uri(from_=from_page, to=to_page)
    title_node = builder.env.titles.get(to_page)
    title = builder.render_partial(title_node)["title"] if title_node else to_page
    return {"link": link, "title": title}


def _validate_flow_pages(
    _app: Sphinx,
    _exception: Exception | None,
) -> None:
    """Warn about flow pages that do not exist in the doctree."""
    if _exception is not None:
        return
    all_docs: set[str] = set(_app.env.all_docs)
    for page in _app.config.prev_next_flow_pages:
        if page not in all_docs:
            logger.warning(
                "selective_prev_next: configured flow page '%s' not found in the doctree",
                page,
            )


def setup(app: Sphinx) -> dict[str, Any]:
    """Register config value and event hooks."""
    app.add_config_value("prev_next_flow_pages", default=(), rebuild="html")
    app.connect(event="html-page-context", callback=_filter_prev_next)
    app.connect(event="build-finished", callback=_validate_flow_pages)
    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
