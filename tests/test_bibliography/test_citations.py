import itertools
import json
from operator import itemgetter
import os.path
from typing import Any, Iterable
import unittest
import xml.etree.ElementTree as ET

from md_preprocessor.bibliography.citations import CitationMatch, CitationReplacer
from md_preprocessor.bibliography.utils import Jinja2TemplateLoader

_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURES_PATH = os.path.join(_ROOT_PATH, 'fixtures')
_BIBLIOGRAPHY_PATH = os.path.join(_FIXTURES_PATH, 'bibliography.json')
_TEMPLATES_PATH = os.path.join(_FIXTURES_PATH, 'templates')


def load_bibliography(path: str = _BIBLIOGRAPHY_PATH) -> dict[str, Any]:
    with open(path, 'r') as fh:
        return json.load(fh)


class TestCitationReplacer(unittest.TestCase):
    """Test the CitationReplacer class"""

    def setUp(self):
        bibliography = load_bibliography()
        template_loader = Jinja2TemplateLoader(_TEMPLATES_PATH)
        self.replacer = CitationReplacer(bibliography,
                                         style_name='harvard1',
                                         template_loader=template_loader)

    def test_render_bibliography(self):
        citations = (
            ['kingmaAdamMethodStochastic2017'],
            ['bengioAdvancesOptimizingRecurrent2012',
             'ningqianMomentumTermGradient1999'],
            ['ningqianMomentumTermGradient1999',],
            ['suttonProblemsWithBackpropagation1986',
             'zeilerADADELTAAdaptiveLearning2012',
             'dettmers8bitOptimizersBlockwise2022'],
            ['xyz', 'shazeerAdafactorAdaptiveLearning2018'],
        )
        self._check_bibliography(citations, exclude=['xyz'])

    def test_pattern__bracket_key__start_end(self):
        text = "[@liMemoryEfficientOptimizers2023]"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=False), 0, len(text)),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__start_end(self):
        text = "@liMemoryEfficientOptimizers2023"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=True), 0, len(text)),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__bracket_key__in_text(self):
        text = "Lorem ipsum [@liMemoryEfficientOptimizers2023] dolor sit amet"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=False), 12, 46),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__in_text(self):
        text = "Lorem ipsum @liMemoryEfficientOptimizers2023 dolor sit amet"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=True), 12, 44),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__multiple(self):
        text = "@liMemoryEfficientOptimizers2023 and @hi-world"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=True), 0, 32),
            (CitationMatch(ref_ids=["hi-world"], is_running_text=True), 37, 46),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__comma_right(self):
        text = "@liMemoryEfficientOptimizers2023,"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=True), 0, 32),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__comma_left(self):
        text = ",@liMemoryEfficientOptimizers2023"
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__dot_right(self):
        text = "@liMemoryEfficientOptimizers2023."
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimizers2023"], is_running_text=True), 0, 32),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__double_punctuation(self):
        text = "@liMemoryEfficientOptimi--zers2023"
        expected = (
            (CitationMatch(ref_ids=["liMemoryEfficientOptimi"], is_running_text=True), 0, 24),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__email(self):
        text = "My email is test@example.com."
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__single_at(self):
        text = "The @ symbol"
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__multiple_citations(self):
        text = "Blah blah [@doe99; @smith2000; @smith2004]."
        expected = (
            (CitationMatch(ref_ids=["doe99", "smith2000", "smith2004"], is_running_text=False), 10, 42),
        )
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__escaped_at_backslash(self):
        text = r"Lorem ipsum \@liMemoryEfficientOptimizers2023 dolor sit amet"
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__text_key__escaped_at_at(self):
        text = r"Lorem ipsum @@liMemoryEfficientOptimizers2023 dolor sit amet"
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_pattern__bracket_key__escaped_bracket(self):
        text = r"Lorem ipsum \[@liMemoryEfficientOptimizers2023] dolor sit amet"
        expected = ()
        output = tuple(self.replacer.find(text))
        self.assertEqual(expected, output)

    def test_replace__no_key(self):
        self._check_citation(text='@xyz',
                             expected_keys=["xyz"],
                             expected_bodies=["xyz?"],
                             expected_before="(",
                             expected_after=")",
                             )

    def test_replace__text_key(self):
        self._check_citation(text='@bengioAdvancesOptimizingRecurrent2012',
                             expected_keys=["bengioadvancesoptimizingrecurrent2012"],
                             expected_bodies=["Bengio et al. 2012"],
                             expected_before="(",
                             expected_after=")",
                             )

    def test_replace__bracket_key(self):
        self._check_citation(text='[@bengioadvancesoptimizingrecurrent2012]',
                             expected_keys=["bengioadvancesoptimizingrecurrent2012"],
                             expected_bodies=["Bengio et al. 2012"],
                             expected_before="(",
                             expected_after=")",
                             )

    def test_replace__bracket_key__multiple(self):
        text = ('Lorem ipsum [@bengioAdvancesOptimizingRecurrent2012; '
                '@zeilerADADELTAAdaptiveLearning2012; @ningqianMomentumTermGradient1999] '
                'dolor sit amet')
        expected_keys = [
            "bengioadvancesoptimizingrecurrent2012",
            "zeileradadeltaadaptivelearning2012",
            "ningqianmomentumtermgradient1999",
        ]
        expected_bodies = [
            "Bengio et al. 2012",
            "Zeiler 2012",
            "Ning Qian 1999",
        ]
        self._check_citation(text, expected_keys, expected_bodies,
                             expected_before="(",
                             expected_after=")",
                             )

    def _check_bibliography(self,
                            citations: Iterable[Iterable[str]],
                            exclude: Iterable[str] | None,
                            ) -> None:
        exclude = set(exclude or ())
        for ref_ids in citations:
            self.replacer.replace(CitationMatch(ref_ids=list(ref_ids), is_running_text=True))

        output = self.replacer.render_bibliography()
        output_xml = ET.fromstring(output)

        actual_keys = sorted([child_xml.attrib['ref-id'].strip() for child_xml in output_xml])
        expected_keys = sorted({ref_id.lower() for ref_ids in citations for ref_id in ref_ids if ref_id not in exclude})
        self.assertEqual(expected_keys, actual_keys)

        for i, child_xml in enumerate(output_xml):
            ref_id = child_xml.attrib['ref-id']
            text = child_xml.text
            self.assertTrue(text, msg=f"{i}th bibliography entry with ref ID {ref_id} is empty!")

    def _check_citation(self,
                        text: str,
                        expected_keys: Iterable[str],
                        expected_bodies: Iterable[str],
                        expected_before: str | None = None,
                        expected_after: str | None = None,
                        ) -> None:
        match, = self._get_matches(text, n=1)
        output = self.replacer.replace(match)
        output_xml = ET.fromstring(output)

        actual_keys = [child_xml.attrib['ref-id'].strip() for child_xml in output_xml]
        actual_bodies = [child_xml.text.strip() for child_xml in output_xml]
        actual_before = output_xml.attrib['before']
        actual_after = output_xml.attrib['after']

        self.assertEqual(expected_keys, actual_keys)
        self.assertEqual(expected_bodies, actual_bodies)
        if expected_before is not None:
            self.assertEqual(expected_before, actual_before)
        if expected_after is not None:
            self.assertEqual(expected_after, actual_after)

    def _get_matches(self, text: str, n: int | None = None) -> list[CitationMatch]:
        matches = self.replacer.find(text)
        return list(itertools.islice(map(itemgetter(0), matches), n))
