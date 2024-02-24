"""Project-wide utility functions"""
import collections
import json
import os
import re
from typing import Any, Callable

import jinja2

JSON = None | bool | int | float | str | list["_Json"] | dict[str, "_Json"]
TemplateParser = Callable[[str], str]
_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
_DEFAULT_TEMPLATE_DIR = os.path.join(_ROOT_PATH, 'assets', 'templates')
_METADATA_BLOCK = re.compile("^[^\\S\n\r]*(?P<meta>(?:^|[\n\r])[+-]{3}[\n\r]"
                             ".*?"
                             "[\n\r][+-]{3}(?:[\n\r]+|$))"
                             "(?P<body>.*)$", re.DOTALL)


class TreeIterator:
    """Iterate over all nodes of a generic tree structure"""

    def __init__(self, document: Any, children_prop: str = "children"):
        self._queue = collections.deque()
        self._queue.append(document)
        self._current_subtree = ()
        self._children_prop = children_prop

    def __iter__(self):
        return self

    def __next__(self):
        self._queue.extendleft(self._current_subtree)
        if not self._queue:
            raise StopIteration
        next_element = self._queue.pop()
        self._current_subtree = getattr(next_element, self._children_prop, ())
        return next_element

    def prune(self):
        """Prune current subtree (do not descend any further into subtree)"""
        self._current_subtree = ()


def read_csl_bibliography(path: str) -> JSON:
    """
    Read CSL-style bibliography from file
    :param path: path to bibliography file
    :return: bibliography in JSON format
    """
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def sanitize_path(path: str) -> str:
    """
    Sanitize file paths to make sure they are within the current directory
    :param path: path to a file
    :return: sanitized path
    """
    return os.path.join('', os.path.relpath(os.path.join('/', path), '/'))


class Jinja2TemplateLoader:  # pylint: disable=too-few-public-methods
    """Load templates from fixtures directory using jinja2"""

    def __init__(self, templates_root: str = _DEFAULT_TEMPLATE_DIR):
        """
        :param templates_root: root directory of Jinja2 templates
        """
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_root),
            autoescape=jinja2.select_autoescape()
        )

    def get_template(self, name: str) -> Callable[..., str]:
        """
        Get template function
        :param name: name of template
        :return: function that takes in params and returns rendered document
        """
        filename = sanitize_path(f'{name}.j2')
        return self._env.get_template(filename).render


def separate_markdown_metadata(markdown: str) -> (str, str):
    """
    Separate the leading metadata block from the MarkDown document and return
    both
    :param markdown: MarkDown document text
    :return: tuple containing 1. metadata block, 2. rest of MarkDown document
    """
    match = _METADATA_BLOCK.match(markdown)
    if not match:
        return "", markdown

    return match.group("meta"), match.group("body")
