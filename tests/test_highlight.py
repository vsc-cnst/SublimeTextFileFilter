import sys
import sublime
import unittest
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes


class TestHighlight(unittest.TestCase):

    def test_filter_passes_highlight_flags_to_sublime(self):
        for highlight_type in HighlightTypes:
            with self.subTest(highlight_type=highlight_type.name):
                view = MagicMock()
                match = sublime.Region(1, 4)
                view.size.return_value = 5
                view.find_all.return_value = [match]

                view_utils.filter(
                    MagicMock(),
                    view,
                    "err",
                    FoldingTypes.highlight_only,
                    highlight_type,
                )

                if highlight_type is HighlightTypes.none:
                    view.add_regions.assert_not_called()
                else:
                    view.add_regions.assert_called_once_with(
                        key=view_utils.VIEW_SETTINGS_HIGHLIGHTED_REGIONS,
                        regions=[match],
                        scope="highlight",
                        icon="",
                        flags=highlight_type.value,
                        annotations=[],
                        annotation_color="#32a852",
                    )