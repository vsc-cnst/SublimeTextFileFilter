import sys
import sublime  # type: ignore
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

File_Filter = sys.modules["File Filter.file_filter"]
LOGGER = File_Filter.LOGGER
FileFilterCommand = File_Filter.FileFilterCommand
OptionsInputHandler = File_Filter.OptionsInputHandler
RegexInputHandler = File_Filter.RegexInputHandler
HistoryInputHandler = File_Filter.HistoryInputHandler
FavoritsInputHandler = File_Filter.FavoritsInputHandler
FileFilterListener = File_Filter.FileFilterListener

enums = sys.modules["File Filter.utils.enums"]
FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes

view_utils = sys.modules["File Filter.utils.view"]
VIEW_SETTINGS_CURRENT_FOLDING_TYPE = view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE
VIEW_SETTINGS_CURRENT_REGEX = view_utils.VIEW_SETTINGS_CURRENT_REGEX
VIEW_SETTINGS_IS_FILTER_ACTIVE = view_utils.VIEW_SETTINGS_IS_FILTER_ACTIVE
VIEW_SETTINGS_REGEX_HISTORY = view_utils.VIEW_SETTINGS_REGEX_HISTORY
get_folding_type = view_utils.get_folding_type
get_highlight_type = view_utils.get_highlight_type




class TestFileFilterOptionsInputHandler(unittest.TestCase):

	def setUp(self):
		self.window = sublime.active_window()
		self.view = self.window.new_file()
		self.window.focus_view(self.view)
		self.handler = OptionsInputHandler(self.view, MagicMock())

	def tearDown(self):
		self.view.set_scratch(True)
		self.window.focus_view(self.view)
		self.view.window().run_command("close_file")

	def test_file_filter_command_returns_options_handler(self):
		command = FileFilterCommand(self.view)

		self.assertIsInstance(command.input({}), OptionsInputHandler)

	def test_name_and_items(self):
		self.assertEqual(self.handler.name(), "option")
		self.assertEqual(
			self.handler.list_items(),
			[
				("New", "new"),
				("From Selected Text", "from_selection"),
				("History", "history"),
				("Favorites", "favorites"),
				("Clear", "clear"),
			],
		)

	def test_new_routes_to_regex_handler(self):
		self.view.settings().set(VIEW_SETTINGS_CURRENT_REGEX, "cached")

		next_handler = self.handler.next_input({"option": "new"})

		self.assertIsInstance(next_handler, RegexInputHandler)
		self.assertEqual(next_handler.initial_text(), "cached")

	def test_history_routes_to_history_handler(self):
		history_handler = self.handler.next_input({"option": "history"})
		self.assertIsInstance(history_handler, HistoryInputHandler)
		self.view.settings().set(VIEW_SETTINGS_REGEX_HISTORY, ["ERROR", "WARN"])
		self.assertEqual(history_handler.list_items(), ["ERROR", "WARN"])

	def test_favorites_routes_to_favorites_handler(self):
		favorites_handler = self.handler.next_input({"option": "favorites"})
		self.assertIsInstance(favorites_handler, FavoritsInputHandler)
		favorites_handler.settings.favorits = [
			{"name": "Errors", "pattern": "ERROR"},
			{"name": "Warnings", "pattern": "WARN"},
		]
		self.assertEqual(
			favorites_handler.list_items(),
			[("Errors", "ERROR"), ("Warnings", "WARN")],
		)

	@patch.object(view_utils, "filter")
	@patch.object(view_utils, "add_to_history")
	def test_history_confirmation_records_and_applies_regex(self, mock_add, mock_filter):
		history_handler = self.handler.next_input({"option": "history"})
		history_handler.confirm("ERROR")

		mock_add.assert_called_once_with(history_handler.logger, self.view, "ERROR")
		filter_args = mock_filter.call_args.args
		self.assertEqual(filter_args[:3], (history_handler.logger, self.view, "ERROR"))
		self.assertIsInstance(filter_args[3], FoldingTypes)
		self.assertIsInstance(filter_args[4], HighlightTypes)

	@patch.object(view_utils, "filter")
	@patch.object(view_utils, "add_to_history")
	def test_favorite_confirmation_records_and_applies_regex(self, mock_add, mock_filter):
		favorites_handler = self.handler.next_input({"option": "favorites"})
		favorites_handler.confirm("ERROR")

		mock_add.assert_called_once_with(favorites_handler.logger, self.view, "ERROR")
		filter_args = mock_filter.call_args.args
		self.assertEqual(filter_args[:3], (favorites_handler.logger, self.view, "ERROR"))
		self.assertIsInstance(filter_args[3], FoldingTypes)
		self.assertIsInstance(filter_args[4], HighlightTypes)

	def test_unknown_option_does_not_continue(self):
		self.assertIsNone(self.handler.next_input({"option": "unknown"}))

	@patch.object(view_utils, "clear")
	def test_clear_uses_configured_options(self, mock_clear):
		self.handler.settings.commands.clear = SimpleNamespace(
			unfold_regions=False,
			remove_highlights=True,
			center_viewport_on_carret=False,
		)

		result = self.handler.next_input({"option": "clear"})

		self.assertIsNone(result)
		mock_clear.assert_called_once_with(
			self.handler.logger,
			self.view,
			unfold_regions=False,
			remove_highlights=True,
			center_viewport_on_carret=False,
		)

	@patch.object(view_utils, "clear")
	def test_clear_context_clears_and_returns_active_state(self, mock_clear):
		self.view.settings().set(VIEW_SETTINGS_IS_FILTER_ACTIVE, True)

		result = FileFilterListener().on_query_context(
			self.view,
			"file_filter.keymaps_context.clear",
			0,
			None,
			False,
		)

		self.assertTrue(result)
		mock_clear.assert_called_once_with(LOGGER, self.view)

	@patch.object(view_utils, "clear")
	def test_unrelated_context_does_not_clear(self, mock_clear):
		result = FileFilterListener().on_query_context(
			self.view,
			"unrelated.context",
			0,
			None,
			False,
		)

		self.assertIsNone(result)
		mock_clear.assert_not_called()


class TestRegexInputHandler(unittest.TestCase):

	def setUp(self):
		self.window = sublime.active_window()
		self.view = self.window.new_file()
		self.window.focus_view(self.view)
		self.handler = RegexInputHandler(self.view, MagicMock())

	def tearDown(self):
		self.view.set_scratch(True)
		self.window.focus_view(self.view)
		self.view.window().run_command("close_file")

	def test_prompt_contract(self):
		self.assertEqual(self.handler.name(), "regex")
		self.assertEqual(self.handler.initial_text(), "")
		self.assertIsNone(self.handler.initial_selection())
		self.assertIsNone(self.handler.placeholder())
		self.assertFalse(self.handler.validate(""))
		self.assertTrue(self.handler.validate("ERROR"))

	def test_initial_text_uses_current_regex(self):
		self.view.settings().set(VIEW_SETTINGS_CURRENT_REGEX, "ERROR")
		handler = RegexInputHandler(self.view, MagicMock())

		self.assertEqual(handler.initial_text(), "ERROR")

	@patch.object(view_utils, "filter")
	@patch.object(File_Filter.mini_html, "create_preview", return_value="preview")
	def test_preview_filters_on_change_when_enabled(self, mock_preview, mock_filter):
		self.handler.settings.commands.new.filter_on_change = True
		self.handler.settings.commands.new.show_total_matches = False

		result = self.handler.preview("ERROR")

		self.assertEqual(result, "preview")
		mock_filter.assert_called_once()
		rows = mock_preview.call_args.args[1]
		self.assertIn(("Filter on change", "on"), rows)

	@patch.object(view_utils, "filter")
	@patch.object(File_Filter.mini_html, "create_preview", return_value="preview")
	def test_preview_skips_filter_when_filter_on_change_is_disabled(self, mock_preview, mock_filter):
		self.handler.settings.commands.new.filter_on_change = False
		self.handler.settings.commands.new.show_total_matches = True
		self.view.run_command("insert", {"characters": "ERROR"})

		result = self.handler.preview("ERROR")

		self.assertEqual(result, "preview")
		mock_filter.assert_not_called()
		self.assertEqual(mock_preview.call_args.args[0], ("Total matches", 1))
		self.assertIn(("Filter on change", "off"), mock_preview.call_args.args[1])

	@patch.object(view_utils, "filter")
	@patch.object(view_utils, "add_to_history")
	def test_confirm_records_and_applies_regex(self, mock_add_to_history, mock_filter):
		self.handler.confirm("ERROR")

		mock_add_to_history.assert_called_once_with(
			self.handler.logger,
			self.view,
			"ERROR",
		)
		mock_filter.assert_called_once_with(
			self.handler.logger,
			self.view,
			"ERROR",
			get_folding_type(self.handler.logger, self.view, self.handler.settings),
			get_highlight_type(self.handler.logger, self.view, self.handler.settings),
		)
