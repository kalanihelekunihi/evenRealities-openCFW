#!/usr/bin/env python3
"""Round-trip and compile gates for assetgen_string_pool.py."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/assetgen_string_pool.py"

SPEC = {
    "pool_name": "sample_strings",
    "entries": [
        {"name": "greeting", "text": "Hello"},
        {"name": "farewell", "text": "Goodbye, world"},
        {"name": "empty", "text": ""},
        {"name": "unicode", "text": "café"},
    ],
}


def load_tool():
    spec = importlib.util.spec_from_file_location("assetgen_string_pool", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AssetgenStringPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_tool()
        cls.tmp = tempfile.TemporaryDirectory(prefix="assetgen-string-pool-")
        cls.dir = Path(cls.tmp.name)
        cls.spec_path = cls.dir / "spec.json"
        cls.spec_path.write_text(json.dumps(SPEC))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_round_trip(self):
        text, meta = self.m.build(self.spec_path, layout="both")
        self.assertEqual(meta["entries"], 4)
        blob, offsets, names = self.m.pack(SPEC)
        self.assertEqual(self.m.decode(blob, offsets), [e["text"] for e in SPEC["entries"]])
        self.assertIn("sample_strings_bytes", text)
        self.assertIn("sample_strings_offsets", text)
        self.assertIn("sample_strings_ptrs", text)
        self.assertIn("SAMPLE_STRINGS_GREETING = 0", text)

    def test_deterministic(self):
        text1, _ = self.m.build(self.spec_path, layout="offsets")
        text2, _ = self.m.build(self.spec_path, layout="offsets")
        self.assertEqual(text1, text2)

    def test_duplicate_names_rejected(self):
        bad = dict(SPEC, entries=[{"name": "x", "text": "a"}, {"name": "x", "text": "b"}])
        path = self.dir / "bad.json"
        path.write_text(json.dumps(bad))
        with self.assertRaises(self.m.StringPoolError):
            self.m.build(path)

    @unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
    def test_generated_source_compiles(self):
        text, _ = self.m.build(self.spec_path, layout="both")
        out = self.dir / "gen.c"
        out.write_text(text)
        result = subprocess.run(
            ["clang", "-c", "-Wall", "-Wextra", "-Werror", str(out), "-o", str(self.dir / "gen.o")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
    def test_generated_strings_readable_at_runtime(self):
        text, _ = self.m.build(self.spec_path, layout="pointers")
        harness = self.dir / "harness.c"
        harness.write_text(
            text + "\n"
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "int main(void){\n"
            "    if (strcmp(sample_strings_ptrs[0], \"Hello\") != 0) return 1;\n"
            "    if (strcmp(sample_strings_ptrs[1], \"Goodbye, world\") != 0) return 2;\n"
            "    if (strcmp(sample_strings_ptrs[2], \"\") != 0) return 3;\n"
            "    return 0;\n"
            "}\n"
        )
        binary = self.dir / "harness"
        subprocess.run(["clang", str(harness), "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)])
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
