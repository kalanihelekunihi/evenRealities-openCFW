#!/usr/bin/env python3
"""Guard the authenticated parallel EM9305 SDK archive runner."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/run_em9305_sdk_archive_batch.py"
MANIFEST = ROOT / "tools/manifests/em9305-sdk-discovery.tsv"


def load_tool():
    spec = importlib.util.spec_from_file_location("run_em9305_sdk_archive_batch", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305SdkArchiveBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_checked_in_manifest_has_safe_unique_archives(self) -> None:
        rows = self.tool.read_manifest(MANIFEST)
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({row["label"] for row in rows}), 16)
        self.assertTrue(all(row["source_path"].endswith(".a") for row in rows))
        self.assertTrue(all(len(row["git_blob"]) == 40 for row in rows))
        self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))

    def test_manifest_rejects_traversal_and_duplicate_labels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.tsv"
            path.write_text(
                f"same\tlibs/a.a\t{'a' * 40}\t{'b' * 64}\t1\n"
                f"same\t../b.a\t{'c' * 40}\t{'d' * 64}\t1\n"
            )
            with self.assertRaises(self.tool.BatchError):
                self.tool.read_manifest(path)

    def test_output_directory_must_be_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "output"
            self.tool.require_empty_output(path)
            (path / "occupied").write_text("x")
            with self.assertRaises(self.tool.BatchError):
                self.tool.require_empty_output(path)


if __name__ == "__main__":
    unittest.main()
