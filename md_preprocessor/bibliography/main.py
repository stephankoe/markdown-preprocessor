#!/usr/bin/env python3
"""
Run Pandoc-style citation Markdown preprocessor to parse citations to HTML
"""
from argparse import ArgumentParser
import sys

from md_preprocessor.bibliography.citations import CitationReplacer
from md_preprocessor.bibliography.utils import read_csl_bibliography
from md_preprocessor.utils.replace import apply_replace_markdown


def get_args(parser: ArgumentParser | None = None):
    """
    Get arguments for citation preprocessor
    :param parser: parser
    """
    parser = parser or ArgumentParser()
    parser.add_argument('md_file',
                        help="Path to a Markdown file")
    parser.add_argument('--bibliography',
                        type=str,
                        default=None,
                        help="Path to CSL-JSON file containing bibliography")
    parser.add_argument('--bibliography-marker',
                        type=str,
                        default=r'{{bibliography}}',
                        help="Find this string in the parsed Markdown file and"
                             " replace it by the HTML bibliography")
    return parser.parse_args()


def main_cli():
    """Main entry point for the CLI program"""
    args = get_args()
    with open(args.md_file, 'r', encoding='utf-8') as fh:
        contents = fh.read()
    bibliography = read_csl_bibliography(args.bibliography)
    replacer = CitationReplacer(bibliography=bibliography)
    output = apply_replace_markdown(contents, replacer)
    output = output.replace(args.bibliography_marker,
                            replacer.render_bibliography())
    try:
        sys.stdout.write(output)
    except BrokenPipeError:
        pass


if __name__ == '__main__':
    main_cli()
