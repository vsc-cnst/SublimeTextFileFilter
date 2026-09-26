import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

settings_manager_module = sys.modules["File Filter.utils.settings_manager"]
SettingsManager = settings_manager_module.SettingsManager
SettingsSnapshot = settings_manager_module.SettingsSnapshot

class TestSettingsManager(unittest.TestCase):

    @patch('sublime.load_settings')
    def test_initialization(self, mock_load_settings):
        manager = SettingsManager()

        self.assertEqual(manager.settings_file, 'file_filter.sublime-settings')
        self.assertIsInstance(manager.settings, SettingsSnapshot)
        mock_load_settings.assert_called_once_with('file_filter.sublime-settings')
        manager.settings_sublime.add_on_change.assert_called_once_with(
            manager.settings_key,
            manager.reload_settings,
        )

    @patch('sublime.load_settings')
    def test_reload_settings_rebuilds_snapshot(self, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        mock_logger = MagicMock()
        manager = SettingsManager(logger=mock_logger)
        original_snapshot = manager.settings
        
        manager.reload_settings()
        self.assertIsNot(manager.settings, original_snapshot)
        mock_load_settings.assert_called_once_with('file_filter.sublime-settings')
        mock_logger.info.assert_called_with(f"Settings reloaded for {manager.settings_key}")

    @patch('sublime.load_settings')
    def test_no_logger(self, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        manager = SettingsManager()

        self.assertIsNone(manager.logger)
        manager.reload_settings()

    def test_snapshot_defaults(self):
        settings = MagicMock()
        settings.get.return_value = {}

        snapshot = SettingsSnapshot(settings)

        self.assertEqual(snapshot.global_settings.log_level, logging.ERROR)
        self.assertEqual(snapshot.global_settings.global_regex_flags, 'gi')
        self.assertEqual(snapshot.defaults.folding.type, 'line')
        self.assertEqual(snapshot.defaults.highlight.type, 'solid')
        self.assertEqual(snapshot.defaults.highlight.color, 'white')
        self.assertFalse(snapshot.commands.new.filter_on_change)
        self.assertFalse(snapshot.commands.from_selection.escape_selection)
        self.assertTrue(snapshot.commands.clear.unfold_regions)
        self.assertFalse(snapshot.commands.clear.remove_highlights)
        #self.assertEqual(snapshot.favorits, [])
        #self.assertEqual(snapshot.expressions, [])

    def test_snapshot_nested_overrides(self):
        values = {
            'global': {'log_level': logging.DEBUG, 'global_regex_flags': 'i'},
            'defaults': {
                'folding': {'type': 'match_only'},
                'highlight': {'type': 'underline_squiggly', 'color': 'red'},
            },
            'commands': {
                'new': {'filter_on_change': True, 'show_total_matches': True},
                'from_selection': {'escape_selection': True},
                'clear': {
                    'center_viewport_on_carret': True,
                    'remove_highlights': True,
                    'unfold_regions': False,
                },
            },
            'favorits': [{'name': 'errors', 'pattern': 'ERROR'}],
            'expressions': [{'name': 'combined', 'pattern': ['ERROR', 'WARN']}],
        }
        settings = MagicMock()
        settings.get.side_effect = lambda key, default=None: values.get(key, default)

        snapshot = SettingsSnapshot(settings)

        self.assertEqual(snapshot.global_settings.log_level, logging.DEBUG)
        self.assertEqual(snapshot.global_settings.global_regex_flags, 'i')
        self.assertEqual(snapshot.defaults.folding.type, 'match_only')
        self.assertEqual(snapshot.defaults.highlight.type, 'underline_squiggly')
        self.assertEqual(snapshot.defaults.highlight.color, 'red')
        self.assertTrue(snapshot.commands.new.filter_on_change)
        self.assertTrue(snapshot.commands.from_selection.escape_selection)
        self.assertFalse(snapshot.commands.clear.unfold_regions)
        self.assertEqual(snapshot.favorits, values['favorits'])
        self.assertEqual(snapshot.expressions, values['expressions'])
