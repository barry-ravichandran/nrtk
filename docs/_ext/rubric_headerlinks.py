"""Sphinx extension: add permalink anchors to ``.. rubric::`` directives.

Sphinx automatically adds ``#`` headerlinks to section headings (h1-h6)
but **not** to ``.. rubric::`` directives.  This extension post-processes
the rendered HTML to inject a permalink anchor into every ``<p>`` element
that has both ``class="rubric"`` and an ``id`` attribute::

    <p class="rubric" id="my-label">
        Title Text
        <a class="rubric-permalink" href="#my-label" title="Link to this heading">#</a>
    </p>

A custom ``rubric-permalink`` class is used instead of Sphinx's
``headerlink`` class to avoid inherited CSS from ``basic.css`` and the
pydata-sphinx-theme that causes display issues inside dropdown cards.

Styling (show-on-hover via opacity) is handled by the rules in
``_static/css/custom.css``.
"""

from __future__ import annotations

import re
from typing import Any

from sphinx.application import Sphinx

# Matches: <p class="rubric" id="SOME-ID">...CONTENT...</p>
# and injects the permalink anchor before </p>.
_RUBRIC_RE = re.compile(
    r'(<p\s+class="rubric"\s+id="([^"]+)">)(.*?)(</p>)',
    re.DOTALL,
)


def _inject_headerlinks(
    _app: Sphinx,
    _pagename: str,
    _templatename: str,
    context: dict[str, Any],
    _doctree: object,
) -> None:
    """Post-process the rendered body HTML to add rubric permalink anchors."""
    body = context.get("body")
    if not body:
        return

    def _add_link(m: re.Match[str]) -> str:
        open_tag = m.group(1)  # <p class="rubric" id="...">
        anchor_id = m.group(2)  # the id value
        content = m.group(3)  # inner text/HTML
        close_tag = m.group(4)  # </p>
        link = f'<a class="rubric-permalink" href="#{anchor_id}" title="Link to this heading">#</a>'
        return f"{open_tag}{content}{link}{close_tag}"

    new_body = _RUBRIC_RE.sub(repl=_add_link, string=body)
    if new_body != body:
        context["body"] = new_body


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the html-page-context hook."""
    app.connect(event="html-page-context", callback=_inject_headerlinks)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
