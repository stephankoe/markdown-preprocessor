"""Find-and-replace utility"""
from typing import Iterable, Protocol, TypeVar

import marko
from marko.md_renderer import MarkdownRenderer

from md_preprocessor.bibliography.utils import TreeIterator

_Match = TypeVar("_Match")
_NO_REPLACE = frozenset(('Link', 'CodeSpan', 'CodeBlock', 'FencedCode'))


class _Replacer(Protocol):
    """Find and replace action"""

    def find(self, text: str) -> Iterable[tuple[_Match, int, int]]:
        """
        Find objects of interest in given text
        :param text: input text
        :return: matches
        """

    def replace(self, match: _Match) -> str:
        """
        Replace matches by some other string
        :param match: a single match
        :return: replacement string
        """


def apply_replace(text: str, replacer: _Replacer) -> str:
    """
    Replace the contents of text according to the rules defined in replacer
    :param text: input text
    :param replacer: replacement rules
    :return: text after replacement
    """
    last_end = 0
    output = []
    for match, start, end in replacer.find(text):
        text_before = text[last_end:start]
        if text_before:
            output.append(text_before)
        replacement = replacer.replace(match)
        output.append(replacement)
        last_end = end
    text_remaining = text[last_end:]
    if text_remaining:
        output.append(text_remaining)
    return ''.join(output)


def apply_replace_markdown(markdown: str,
                           replacer: _Replacer,
                           avoid: Iterable[str] = _NO_REPLACE,
                           ) -> str:
    """
    Replace patterns in Markdown text, but ignore links, code blocks, as well
    as backslash escapes
    :param markdown: Markdown document content
    :param replacer: function to apply to each match
    :param avoid: do not replace within these Markdown elements
    :return: Markdown document after the replacement
    """
    markdown_tree = marko.parse(markdown)
    tree_it = TreeIterator(markdown_tree)
    for node in tree_it:
        if not hasattr(node, "get_type"):
            continue
        if node.get_type() == 'RawText':  # raw text
            node.children = apply_replace(node.children, replacer)
            tree_it.prune()
        elif any(node.get_type() == cls_name for cls_name in avoid):
            tree_it.prune()  # don't want to replace its contents
    with MarkdownRenderer() as renderer:
        return renderer.render(markdown_tree)
