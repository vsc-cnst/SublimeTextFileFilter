import sys
import sublime # type: ignore
import unittest
from unittest.mock import MagicMock

File_Filter = sys.modules["File Filter.file_filter"]
enums = sys.modules["File Filter.utils.enums"]

FoldingTypes = enums.FoldingTypes

SetFoldingTypeCommand = File_Filter.SetFoldingTypeCommand
FoldingTypesInputHandler = File_Filter.FoldingTypesInputHandler
