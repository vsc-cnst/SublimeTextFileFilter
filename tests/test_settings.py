import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

settings_manager_module = sys.modules["File Filter.utils.settings_manager"]
SettingsManager = settings_manager_module.SettingsManager
SettingsClient = settings_manager_module.SettingsClient
ApplicationSettings = settings_manager_module.ApplicationSettings
SettingsSnapshot = settings_manager_module.SettingsSnapshot

class TestSettingsManager(unittest.TestCase):

    def test_initialization_loads_settings_and_registers_reload(self):
        manager_type = type(ApplicationSettings)
        original_instance = manager_type._SettingsManager__instance
        original_initialized = manager_type._SettingsManager__initialized
        sublime_settings = MagicMock()
        sublime_settings.get.side_effect = lambda key, default=None: default

        try:
            manager_type._SettingsManager__instance = None
            manager_type._SettingsManager__initialized = False
            with patch.object(settings_manager_module.sublime, 'load_settings', return_value=sublime_settings) as load_settings:
                manager = SettingsManager()

            self.assertIsInstance(manager.settings_snapshot, SettingsSnapshot)
            self.assertIs(SettingsManager(), manager)
            load_settings.assert_called_once_with('file_filter.sublime-settings')
            sublime_settings.add_on_change.assert_called_once_with('Settings', manager.reload_settings)
        finally:
            manager_type._SettingsManager__instance = original_instance
            manager_type._SettingsManager__initialized = original_initialized

    def test_reload_settings_rebuilds_snapshot_and_logs(self):
        original_snapshot = ApplicationSettings.settings_snapshot
        original_logger = ApplicationSettings.logger
        sublime_settings = MagicMock()
        sublime_settings.get.side_effect = lambda key, default=None: default
        mock_logger = MagicMock()

        try:
            ApplicationSettings.settings_sublime = sublime_settings
            ApplicationSettings.logger = mock_logger

            ApplicationSettings.reload_settings()

            self.assertIsInstance(ApplicationSettings.settings_snapshot, SettingsSnapshot)
            self.assertIsNot(ApplicationSettings.settings_snapshot, original_snapshot)
            self.assertEqual(mock_logger.info.call_count, 2)
        finally:
            ApplicationSettings.settings_snapshot = original_snapshot
            ApplicationSettings.logger = original_logger

    def test_settings_client_subscribes_and_cleans_up(self):
        original_settings = ApplicationSettings.settings_sublime
        original_snapshot = ApplicationSettings.settings_snapshot
        sublime_settings = MagicMock()
        snapshot = object()

        class Client(SettingsClient):
            def reload_settings(self):
                self.reloaded = True

        try:
            ApplicationSettings.settings_sublime = sublime_settings
            ApplicationSettings.settings_snapshot = snapshot
            client = Client()

            self.assertIs(client.settings, snapshot)
            sublime_settings.add_on_change.assert_called_once_with(client.settings_key, client.reload_settings)
            sublime_settings.add_on_change.call_args.args[1]()
            self.assertTrue(client.reloaded)

            client.__del__()
            sublime_settings.clear_on_change.assert_called_once_with(client.settings_key)
            client.settings_key = None
        finally:
            ApplicationSettings.settings_sublime = original_settings
            ApplicationSettings.settings_snapshot = original_snapshot

    def test_snapshot_defaults(self):
        settings = MagicMock()
        settings.get.side_effect = lambda key, default=None: default

        snapshot = SettingsSnapshot(settings)

        self.assertEqual(snapshot.global_settings.log_level, logging.ERROR)
        self.assertEqual(snapshot.global_settings.global_regex_flags, 'gi')
        self.assertEqual(snapshot.defaults.folding.type, 'line')
        self.assertEqual(snapshot.defaults.highlight.type, 'solid')
        self.assertEqual(snapshot.defaults.highlight.color, 'white')
        self.assertFalse(snapshot.commands.new.filter_on_change)
        self.assertFalse(snapshot.commands.new.show_total_matches)
        self.assertFalse(snapshot.commands.from_selection.escape_selection)
        self.assertFalse(snapshot.commands.clear.center_viewport_on_carret)
        self.assertTrue(snapshot.commands.clear.unfold_regions)
        self.assertFalse(snapshot.commands.clear.remove_highlights)
        self.assertEqual(snapshot.favorits, [])
        self.assertEqual(snapshot.expressions, [])
        self.assertIn('expressions=[]', repr(snapshot))

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
            'favorits': [{
                'code': 'errors',
                'name': 'Errors',
                'pattern': 'ERROR',
                'type': 'or',
                'color': 'red',
                'escape': True,
            }],
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
        self.assertTrue(snapshot.commands.new.show_total_matches)
        self.assertTrue(snapshot.commands.from_selection.escape_selection)
        self.assertTrue(snapshot.commands.clear.center_viewport_on_carret)
        self.assertTrue(snapshot.commands.clear.remove_highlights)
        self.assertFalse(snapshot.commands.clear.unfold_regions)
        self.assertEqual(len(snapshot.favorits), 1)
        favorit = snapshot.favorits[0]
        self.assertEqual(favorit.code, 'errors')
        self.assertEqual(favorit.name, 'Errors')
        self.assertEqual(favorit.pattern, 'ERROR')
        self.assertEqual(favorit.type, 'or')
        self.assertEqual(favorit.color, 'red')
        self.assertTrue(favorit.escape)

    def test_snapshot_skips_malformed_favorites(self):
        values = {
            'favorits': [
                'not a dictionary',
                {'code': 'missing-pattern'},
                {'pattern': 'missing-code'},
                {'code': 'valid', 'pattern': 'VALID'},
            ],
        }
        settings = MagicMock()
        settings.get.side_effect = lambda key, default=None: values.get(key, default)
        logger = MagicMock()

        snapshot = SettingsSnapshot(settings, logger=logger)

        self.assertEqual(len(snapshot.favorits), 1)
        self.assertEqual(snapshot.favorits[0].code, 'valid')
        self.assertEqual(logger.error.call_count, 3)
