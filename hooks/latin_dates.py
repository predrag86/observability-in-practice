"""
mkdocs-git-revision-date-localized-plugin resolves its date locale from
mkdocs-static-i18n's per-page 'locale' attribute when the i18n plugin is
active -- and that always wins over this plugin's own `locale:` config
option (see plugin priority order: i18n page locale > frontmatter locale
> plugin config > theme config > English fallback). Since our i18n locale
code is the plain "sr" (Babel's default Serbian locale, Cyrillic script),
there is no documented way to make the date plugin format in Latin script
while i18n is active -- confirmed against the plugin's own "Specify a
locale" docs, which lists no script-variant override.

This hook is the smallest fix that doesn't touch i18n's locale code
(which would require changing suffix/hreflang semantics site-wide): it
transliterates any Cyrillic left in the date strings the plugin injects
into page.meta, run right before the theme's footer template reads them.
Standard 1:1 Serbian Cyrillic -> Latin (Vukovica) mapping.
"""

_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "đ", "е": "e",
    "ж": "ž", "з": "z", "и": "i", "ј": "j", "к": "k", "л": "l", "љ": "lj",
    "м": "m", "н": "n", "њ": "nj", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "ћ": "ć", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "č",
    "џ": "dž", "ш": "š",
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Ђ": "Đ", "Е": "E",
    "Ж": "Ž", "З": "Z", "И": "I", "Ј": "J", "К": "K", "Л": "L", "Љ": "Lj",
    "М": "M", "Н": "N", "Њ": "Nj", "О": "O", "П": "P", "Р": "R", "С": "S",
    "Т": "T", "Ћ": "Ć", "У": "U", "Ф": "F", "Х": "H", "Ц": "C", "Ч": "Č",
    "Џ": "Dž", "Ш": "Š",
}


def _to_latin(text):
    if not text or not isinstance(text, str):
        return text
    return "".join(_CYR_TO_LAT.get(ch, ch) for ch in text)


def on_page_context(context, page, config, nav):
    for key, value in list(page.meta.items()):
        if key.startswith("git_") and isinstance(value, str):
            page.meta[key] = _to_latin(value)
    return context
