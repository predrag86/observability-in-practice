"""
Injects the book's glossary (Dodatak B / Appendix B) as `abbr`-extension
tooltip definitions on every page, in the right language.

Why a hook instead of pymdownx.snippets' `auto_append`: auto_append takes
a single static list of files applied identically to every locale build,
but our glossary terms differ by language (e.g. "kardinalnost" vs
"cardinality") -- appending the same file to both the sr and en builds
would tooltip the wrong-language term text. mkdocs-static-i18n's
`docs_structure: suffix` means each page's source file is unambiguously
named foo.md (sr, default) or foo.en.md (en), so we just check that
suffix directly rather than depending on any i18n-plugin-internal
attribute (same "introspect the actual mechanism" approach as
hooks/latin_dates.py).

Definitions live in includes/abbreviations.md (sr) and
includes/abbreviations.en.md (en) -- edit those, not this file, to
add/change glossary terms.
"""

from pathlib import Path

_INCLUDES_DIR = Path(__file__).parent.parent / "includes"
_GLOSSARY = {
    "sr": (_INCLUDES_DIR / "abbreviations.md").read_text(encoding="utf-8"),
    "en": (_INCLUDES_DIR / "abbreviations.en.md").read_text(encoding="utf-8"),
}


def on_page_markdown(markdown, page, config, files):
    locale = "en" if page.file.src_uri.endswith(".en.md") else "sr"
    return markdown + "\n\n" + _GLOSSARY[locale]
