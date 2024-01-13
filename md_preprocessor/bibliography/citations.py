"""Pandoc-style citation handler library"""
import dataclasses
from typing import Iterable
import unicodedata
import warnings

from citeproc import (Citation, CitationItem, CitationStylesBibliography,
                      CitationStylesStyle, formatter)
from citeproc.source.json import CiteProcJSON
from citeproc.string import MixedString
import regex as re

from md_preprocessor.bibliography.utils import Jinja2TemplateLoader, JSON, \
    TemplateParser

# Unicode class for opening/closing brackets
_UNICODE_OPEN_TYPE = unicodedata.category("(")
_CLOSE_BRACKET_TYPE = unicodedata.category(")")


@dataclasses.dataclass
class CitationMatch:
    """A found citation in text"""

    ref_ids: list[str]
    is_running_text: bool


class CitationReplacer:
    """
    Replace Pandoc citations by HTML
    Following https://pandoc.org/MANUAL.html#citation-syntax

    Currently NOT supported:
      - Locator
      - Prefix
      - Suffix
      - Suppress author
    """

    # Patterns
    _REF_ID_OUTSIDE = '[a-zA-Z0-9_]'
    _REF_ID_INSIDE = (r'(?:[a-zA-Z0-9_]|(?P<punct>[:.#$%&+?<>~/-])'
                      r'(?!(?P=punct)))')
    _REF_ID_UNGUARDED = (fr'@(?P<ref_id>{_REF_ID_OUTSIDE}'
                         fr'(?:(?:{_REF_ID_INSIDE})*{_REF_ID_OUTSIDE})?)')
    _REF_ID_GUARDED = r'@\{(?P<ref_id>.+)\}'
    _REF_ID = f'(?:{_REF_ID_UNGUARDED}|{_REF_ID_GUARDED})'
    _REF_ID_PATTERN = re.compile(_REF_ID)
    _CITATION_PATTERN = re.compile(fr'(?<=^|\s)(?:\[)?(?P<all>'
                                   fr'(?:{_REF_ID};\s*)*{_REF_ID})(?:])?')
    _ENCLOSURE_REF = re.compile(r'^[([{（【『].*[)\]}）】』]$')
    _IN_BRACKETS_PATTERN = re.compile(r'^\[.*]$')

    def __init__(self,
                 bibliography: JSON = (),
                 style_name: str = 'harvard1',
                 parse_template: TemplateParser | None = None,
                 locale: str = None,
                 ):
        """
        :param bibliography: bibliography in CSL-JSON format
        :param style_name: style name, cf. https://www.zotero.org/styles/
        :param parse_template: function to parse template
        :param locale: localization
        """
        bib_source = CiteProcJSON(bibliography)
        bib_style = CitationStylesStyle(style_name,
                                        validate=False,
                                        locale=locale)
        self._bibliography = CitationStylesBibliography(bib_style,
                                                        bib_source,
                                                        formatter.html)

        # Templates
        parse_template = parse_template or Jinja2TemplateLoader().get_template
        self._render_bib = parse_template('bibliography')
        self._render_citation = parse_template('citation')

    def find(self, text: str) -> Iterable[tuple[CitationMatch, int, int]]:
        """
        Find Pandoc-style citations
        :param text: Markdown text
        :return: iterable over matches with start and end
        """
        for match in self._CITATION_PATTERN.finditer(text):
            matched_text = match.group().strip()
            ref_ids = []
            for sub_match in self._REF_ID_PATTERN.finditer(match.group("all")):
                ref_ids.append(sub_match.group("ref_id"))

            if not ref_ids:
                warnings.warn(f"Found no ref ID in '{matched_text}'. Please "
                              f"make sure, the pattern is correct. This match "
                              f"is ignored.")
            else:
                is_running_text = self._is_in_parentheses(matched_text)
                yield (CitationMatch(ref_ids, is_running_text),
                       match.start(),
                       match.end())

    def replace(self, match: CitationMatch) -> str:
        """
        Renders citations of the form [@key] and @key to HTML
        :param match: regex match of above pattern
        :return: rendered citation (HTML)
        """
        citation = Citation([CitationItem(ref_id) for ref_id in match.ref_ids])
        self._bibliography.register(citation)
        ref_text = self._bibliography.cite(citation, self._warn_missing)
        texts, before, after = (self._parse_mixedstring(ref_text)
                                if isinstance(ref_text, MixedString)
                                else self._parse_string(ref_text))
        if not match.is_running_text and not before and not after:
            before, after = "()"
        ref_ids = [cite.key for cite in citation.cites]
        citation_data = list(zip(ref_ids, texts))
        return self._render_citation(citations=citation_data,
                                     before=before,
                                     after=after)

    def render_bibliography(self) -> str:
        """
        Renders bibliography to HTML
        :return: rendered bibliography (HTML)
        """
        self._bibliography.sort()
        keys = self._bibliography.keys
        bibliography = self._bibliography.bibliography()
        return self._render_bib(references=[
            (ref_id, str(ref_body))
            for ref_id, ref_body in zip(keys, bibliography)
        ])

    @classmethod
    def _is_in_parentheses(cls, text: str) -> bool:
        return cls._IN_BRACKETS_PATTERN.fullmatch(text) is None

    @staticmethod
    def _parse_mixedstring(text: MixedString,
                           delimiter: str = '; ',
                           ) -> tuple[list[MixedString], str, str]:
        bracket_open, bracket_close = [False] * 2
        keys = []
        current = []
        for i, part in enumerate(text):
            char_category = (unicodedata.category(part)
                             if len(part) == 1
                             else None)
            if i == 0 and char_category == _UNICODE_OPEN_TYPE:
                bracket_open = part
            elif i == len(text) - 1 and char_category == _CLOSE_BRACKET_TYPE:
                bracket_close = part
            elif part == delimiter and current:
                keys.append(MixedString(current))
                current = []
            else:
                current.append(part)
        if current:
            keys.append(MixedString(current))
        return keys, bracket_open, bracket_close

    @staticmethod
    def _parse_string(text: str,
                      delimiter: str = ';',
                      ) -> tuple[list[str], str, str]:
        text = text.strip()
        bracket_open, bracket_close = [""] * 2
        if len(text) >= 2:
            if unicodedata.category(text[0]) == _UNICODE_OPEN_TYPE:
                bracket_open = text[0]
                text = text[1:]
            if unicodedata.category(text[-1]) == _CLOSE_BRACKET_TYPE:
                bracket_close = text[-1]
                text = text[:-1]
        parts = text.split(delimiter)
        return [part.strip() for part in parts], bracket_open, bracket_close

    @staticmethod
    def _warn_missing(citation_item: CitationItem) -> None:
        warnings.warn(f"Reference with key '{citation_item.key}' not found in "
                      f"the bibliography.")
