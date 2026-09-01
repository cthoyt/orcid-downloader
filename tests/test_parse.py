"""Test parsing XML."""

import unittest
from pathlib import Path

import ssslm

from orcid_downloader.api import Record, _process_file
from orcid_downloader.client import _get
from orcid_downloader.name_utils import clean_name

HERE = Path(__file__).parent.resolve()
EXAMPLE_DIRECTORY = HERE.joinpath("examples")


def ensure_example(orcid: str) -> Path:
    """Ensure an example file exists."""
    path = EXAMPLE_DIRECTORY.joinpath(orcid).with_suffix(".xml")
    if path.is_file():
        return path
    data = _get(orcid, format="xml")
    path.write_text(data.text)
    return path


def parse(orcid: str) -> Record:
    """Parse an example."""
    grounder = ssslm.EmptyGrounder()
    orcid_to_wikimedia_commons: dict[str, str] = {}
    orcid_to_wikidata: dict[str, str] = {}
    with ensure_example(orcid).open("rb") as file:
        res = _process_file(file, grounder, orcid_to_wikidata, orcid_to_wikimedia_commons)
    if res is None:
        raise ValueError
    return res


class TestParse(unittest.TestCase):
    """Test parsing an XML file."""

    def test_parse_works(self) -> None:
        """Test parsing works."""
        res = parse("0000-0003-4423-4370")
        self.assertTrue(
            any(
                work.pubmed == "36151740"
                and work.title
                == "A review of biomedical datasets relating to drug discovery: "
                "a knowledge graph perspective"
                for work in res.works or []
            ),
            msg=f"works:\n\n{res.works}",
        )

    def test_linkedin_params_garbage(self) -> None:
        """Test parsing garbage."""
        # before linkedin:amir-arsalan-ghahari-101019364?trk=contact-info
        res = parse("0009-0005-6476-5998")
        self.assertEqual("amir-arsalan-ghahari-101019364", res.linkedin)

        res2 = parse("0009-0006-5701-3998")
        self.assertEqual("websitegamebai", res2.linkedin)

        # weird example with minus first
        res3 = parse("0000-0003-3589-9995")
        self.assertEqual("-1VJ-3oAAAAJ", res3.google)

    def test_clean_names(self) -> None:
        """Test cleaning names."""
        self.assertEqual("Francess Dufie Azumah", clean_name("Francess Dufie Azumah (DR.)"))
        self.assertEqual("Girjesh Shukla", clean_name("(Dr.) Girjesh Shukla"))

    def test_empty_name_thrown(self) -> None:
        """Test the primary credit name, which is just an abbreviation, gets thrown out."""
        res = parse("0000-0003-1605-4778")
        self.assertEqual("Nita Shah", res.name)

    def test_duplicate_name(self) -> None:
        """Test duplicate names get filtered out."""
        res = parse("0000-0002-7596-343X")
        self.assertEqual("Hussain Arif", res.name)
        self.assertNotIn("Hussain Arif", res.aliases or [])
