# Markdown Preprocessor Toolkit

Preprocessor toolkit for Markdown-to-HTML converters to parse non-standard Markdown syntax. 
Currently, this toolkit supports the following preprocessors:

- Pandoc-style citation preprocessor: Parses `[@key]` and `@key` as BibTex references and adds a bibliography

The preprocessors output Markdown documents in which the non-standard Markdown is replaced by the parsed HTML code.

## Installation

From within the project root, run the following command line:

```commandline
pip install .
```

This installs the `md_preprocessor` package and the corresponding command-line tools.

## Usage

### Pandoc-style citation preprocessor

```commandline
preprocess-citations 
```
