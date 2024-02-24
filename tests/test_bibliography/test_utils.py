import unittest

from md_preprocessor.bibliography.utils import separate_markdown_metadata


class TestSeparateMarkdownMetadata(unittest.TestCase):

    def test_separate_markdown_metadata__no_metadata(self):
        document = ("# Hello world\n"
                    "\n"
                    "This is a test document\n")
        output_metadata, output_body = separate_markdown_metadata(document)
        self.assertEqual("", output_metadata)
        self.assertEqual(document, output_body)

    def test_separate_markdown_metadata__toml(self):
        line_endings = "\n"
        metadata = ["+++",
                    'title = "A test document"',
                    "+++",
                    ]
        document = ["# Hello world",
                    "",
                    "this is a test document",
                    ]
        expected_document = line_endings.join(document)
        expected_metadata = line_endings.join(metadata) + line_endings
        input_doc = line_endings.join(metadata + document)
        output_metadata, output_body = separate_markdown_metadata(input_doc)
        self.assertEqual(expected_metadata, output_metadata)
        self.assertEqual(expected_document, output_body)

    def test_separate_markdown_metadata__yaml(self):
        line_endings = "\n"
        metadata = ["---",
                    'title: "A test document"',
                    "---",
                    ]
        document = ["# Hello world",
                    "",
                    "this is a test document",
                    ]
        expected_document = line_endings.join(document)
        expected_metadata = line_endings.join(metadata) + line_endings
        input_doc = line_endings.join(metadata + document)
        output_metadata, output_body = separate_markdown_metadata(input_doc)
        self.assertEqual(expected_metadata, output_metadata)
        self.assertEqual(expected_document, output_body)

    def test_separate_markdown_metadata__whitespace_before(self):
        line_endings = "\n"
        metadata = ["---",
                    'title: "A test document"',
                    "---",
                    ]
        document = ["# Hello world",
                    "",
                    "this is a test document",
                    ]
        expected_document = line_endings.join(document)
        expected_metadata = (line_endings + line_endings.join(metadata)
                             + line_endings)
        input_doc = line_endings.join(["   "] + metadata + document)
        output_metadata, output_body = separate_markdown_metadata(input_doc)
        self.assertEqual(expected_metadata, output_metadata)
        self.assertEqual(expected_document, output_body)

    def test_separate_markdown_metadata__chars_before(self):
        line_endings = "\n"
        metadata = []
        document = ["abc",
                    "---",
                    'title: "A test document"',
                    "---",
                    "# Hello world",
                    "",
                    "this is a test document",
                    ]
        expected_document = line_endings.join(document)
        expected_metadata = line_endings.join(metadata)
        input_doc = line_endings.join(metadata + document)
        output_metadata, output_body = separate_markdown_metadata(input_doc)
        self.assertEqual(expected_metadata, output_metadata)
        self.assertEqual(expected_document, output_body)

    def test_separate_markdown_metadata__windows(self):
        line_endings = "\r\n"
        metadata = ["---",
                    'title: "A test document"',
                    "---",
                    ]
        document = ["# Hello world",
                    "",
                    "this is a test document",
                    ]
        expected_document = line_endings.join(document)
        expected_metadata = line_endings.join(metadata) + line_endings
        input_doc = line_endings.join(metadata + document)
        output_metadata, output_body = separate_markdown_metadata(input_doc)
        self.assertEqual(expected_metadata, output_metadata)
        self.assertEqual(expected_document, output_body)

    def test_separate_markdown_metadata__invalid_sequence(self):
        line_endings = "\n"
        document = line_endings.join(("----",
                                      'title: "A test document"',
                                      "---",
                                      "# Hello world",
                                      "",
                                      "this is a test document"))
        output_metadata, output_body = separate_markdown_metadata(document)
        self.assertEqual("", output_metadata)
        self.assertEqual(document, output_body)

    def test_separate_markdown_metadata__missing_return(self):
        line_endings = "\n"
        document = line_endings.join(("---"
                                      'title: "A test document"',
                                      "---",
                                      "# Hello world",
                                      "",
                                      "this is a test document"))
        output_metadata, output_body = separate_markdown_metadata(document)
        self.assertEqual("", output_metadata)
        self.assertEqual(document, output_body)
