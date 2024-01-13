# Markdown Preprocessor Toolkit

Preprocessor toolkit for Markdown-to-HTML converters to parse non-standard 
Markdown syntax. 
Currently, this toolkit supports the following preprocessors:

- Pandoc-style citation preprocessor: Parses `[@key]` and `@key` as BibTex 
  references and adds a bibliography

The preprocessors output Markdown documents in which the non-standard Markdown 
is replaced by the parsed HTML code.

## Installation

From within the project root, run the following command line:

```bash
pip install .
```

This installs the `md_preprocessor` package and the corresponding command-line 
tools.

## Usage

### Pandoc-style citation preprocessor

The citation preprocessor can be called from the command-line with 
`preprocess-citations`. The arguments are:

  - `md_file`: the file path to the Markdown file to be rendered (required)
  - `--bibliography`: path to CSL bibliography (optional) 
  - `--bibliography-marker`: marker of the location within `md_file` where the  
    bibliography should be inserted (optional, defaults to `{{bibliography}}`)
  - `-h`: show usage information

The parsed markdown file is printed to stdout.

```
usage: preprocess-citations [-h] [--bibliography BIBLIOGRAPHY] [--bibliography-marker BIBLIOGRAPHY_MARKER] md_file
```

For example:

```bash
preprocess-citations --bibliography /path/to/bibliography.json /path/to/document.md > /path/to/parsed-document.md
```
