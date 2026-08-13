#!/usr/bin/env python3
"""Guard modified EM9305 SDK comparison helpers and identities."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_em9305_modified_sdk_functions.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "compare_em9305_modified_sdk_functions", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class Em9305ModifiedSdkFunctionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_longest_equal_run_respects_masks_and_mismatches(self) -> None:
        self.assertEqual(
            self.tool.longest_equal_run(b"abcdefghi", b"abcxefghi", {5}),
            3,
        )
        self.assertEqual(
            self.tool.longest_equal_run(b"abcdefgh", b"abcdefgh", {3}),
            4,
        )

    def test_selected_modified_membership_is_pinned(self) -> None:
        self.assertEqual(len(self.tool.EXPECTED_MODIFIED), 9)
        self.assertEqual(
            self.tool.EXPECTED_MODIFIED["lctrSendChanMapUpdateInd"], 0x00325A68
        )
        self.assertEqual(len(self.tool.ARCHIVE_GIT_BLOB), 40)
        self.assertEqual(len(self.tool.ARCHIVE_SHA256), 64)


if __name__ == "__main__":
    unittest.main()
