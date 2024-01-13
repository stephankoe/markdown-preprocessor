import os.path
import unittest

from md_preprocessor.utils.replace import apply_replace, apply_replace_markdown
from tests.utils import MapReplacer

_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURES_PATH = os.path.join(_ROOT_PATH, 'fixtures')
_EXAMPLES_PATH = os.path.join(_FIXTURES_PATH, 'examples')


def load_example(name: str, root: str = _EXAMPLES_PATH) -> (str, str | None):
    example_path = os.path.join(root, f'{name}.md')
    expected_path = os.path.join(root, f'{name}_expected.md')
    with open(example_path, 'r') as fh:
        text = fh.read()

    if not os.path.isfile(expected_path):
        return text, None

    with open(expected_path, 'r') as fh:
        expected = fh.read()

    return text, expected


class TestApplyReplace(unittest.TestCase):
    """Test the apply_replace function"""

    def setUp(self):
        self.replacer = MapReplacer({
            'understand': 'comprehend',
        })

    def test_apply_replace__empty(self):
        text = ""
        result = apply_replace(text, self.replacer)
        expected = ""
        self.assertEqual(expected, result)

    def test_apply_replace_markdown(self):
        text = ("Any fool can write code that a computer can understand. "
                "Good programmers write code that humans can understand.")
        result = apply_replace(text, self.replacer)
        expected = ("Any fool can write code that a computer can comprehend. "
                    "Good programmers write code that humans can comprehend.")
        self.assertEqual(expected, result)


class TestApplyReplaceMarkdown(unittest.TestCase):
    """Test the apply_replace_markdown function"""

    def setUp(self):
        self.replacer = MapReplacer({
            '@kingmaAdamMethodStochastic2017': 'Kingma, 2017',
            '@bottouOptimizationMethodsLargeScale2018': 'Bottou, 2018',
            '@ningqianMomentumTermGradient1999': 'Ning, 1999',
            '@liMemoryEfficientOptimizers2023': 'Li, 2023',
            '@grosseKroneckerfactoredApproximateFisher2016': 'Grosse, 2016',
            '@bengioAdvancesOptimizingRecurrent2012': 'Bengio, 2012',
        })

    def test_apply_replace_markdown__empty(self):
        text, expected = [""] * 2
        result = apply_replace_markdown(text, self.replacer)
        self.assertEqual(expected, result)

    def test_apply_replace_markdown(self):
        text, expected = load_example("citation_document1")
        result = apply_replace_markdown(text, self.replacer)
        self.assertEqual(expected, result)
