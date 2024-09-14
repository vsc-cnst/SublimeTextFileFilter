import sys

import sublime # type: ignore
import sublime_plugin # type: ignore

import gc

import unittest
from unittest.mock import MagicMock, patch

SettingsManager = sys.modules["File Filter.utils.settings"].SettingsManager

class TestSettingsManager(unittest.TestCase):

    @patch('sublime.load_settings')
    def test_initialization(self, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        manager = SettingsManager('Test.sublime-settings')
        self.assertEqual(manager.settings_file, 'Test.sublime-settings')
        self.assertIsInstance(manager.settings, MagicMock)
        mock_load_settings.assert_called_with('Test.sublime-settings')

    @patch('sublime.load_settings')
    @patch('sublime.Settings.add_on_change')
    def test_reload_settings(self, mock_add_on_change, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        mock_logger = MagicMock()
        manager = SettingsManager('Test.sublime-settings', logger=mock_logger)
        
        # Simulate a settings change
        manager.reload_settings()
        mock_load_settings.assert_called_with('Test.sublime-settings')
        mock_logger.info.assert_called_with(f"Settings reloaded for {manager.settings_key}")

    @unittest.skip("__del__ parece estar a ser chamado, mas não em ambiente de testes")
    @patch('sublime.load_settings')
    @patch('sublime.Settings.clear_on_change')
    def test_cleanup(self, mock_clear_on_change, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        mock_logger = MagicMock()
        manager = SettingsManager('Test.sublime-settings', logger=mock_logger)
        
        settings_key = manager.settings_key

        # Simulate cleanup
        del manager
        gc.collect()  # Force garbage collection to ensure __del__ is called
        
        mock_clear_on_change.assert_called_with(settings_key)
        mock_logger.info.assert_called_with(f"Cleaning up resources for {settings_key}")

    @patch('sublime.load_settings')
    def test_no_logger(self, mock_load_settings):
        mock_load_settings.return_value = MagicMock()
        manager = SettingsManager('Test.sublime-settings')
        
        # Simulate a settings change
        manager.reload_settings()
        # Ensure no logging occurs if logger is not provided
        self.assertEqual(manager.logger, None)
