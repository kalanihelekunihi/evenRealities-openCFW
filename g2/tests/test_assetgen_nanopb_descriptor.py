#!/usr/bin/env python3
"""End-to-end gate for assetgen_nanopb_descriptor.py.

Requires the pinned `protoc` and `nanopb==0.4.9` external host tools (the
same version as the pinned `third-party/upstream/nanopb` submodule); skips cleanly if
either is absent rather than failing the whole suite, since this item's
tooling deliberately treats them as external dependencies (see module
docstring), not vendored inputs.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/assetgen_nanopb_descriptor.py"
NANOPB_RUNTIME = ROOT.parent / "third-party/upstream/nanopb"

PROTO = """\
syntax = "proto3";
message Example {
  uint32 id = 1;
  string label = 2;
  repeated uint32 values = 3;
}
"""


def load_tool():
    spec = importlib.util.spec_from_file_location("assetgen_nanopb_descriptor", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _nanopb_available(m) -> bool:
    try:
        m._require_protoc()
        m._require_nanopb_generator()
    except m.AssetGenError:
        return False
    return True


class AssetgenNanopbDescriptorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_tool()
        cls.tmp = tempfile.TemporaryDirectory(prefix="assetgen-nanopb-")
        cls.dir = Path(cls.tmp.name)
        cls.proto = cls.dir / "example.proto"
        cls.proto.write_text(PROTO)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_version_pin_matches_nanopb_submodule(self):
        import subprocess
        tree = subprocess.run(
            ["git", "-C", str(ROOT.parent), "ls-tree", "HEAD", "third-party/upstream/nanopb"],
            capture_output=True, text=True, check=True,
        ).stdout.split()
        self.assertEqual(tree[:3], ["160000", "commit", self.m.REQUIRED_NANOPB_COMMIT])

    def test_never_reads_stock_image(self):
        source_text = TOOL.read_text()
        self.assertNotIn("blobs/official", source_text)
        self.assertNotIn("ota_s200_firmware_ota", source_text)

    def test_missing_generator_fails_closed(self):
        with self.assertRaises(self.m.AssetGenError):
            self.m.generate(self.dir / "does-not-exist.proto", self.dir / "out")

    @unittest.skipUnless(shutil.which("protoc"), "protoc not available on this host")
    def test_end_to_end_generate_and_compile(self):
        m = self.m
        if not _nanopb_available(m):
            self.skipTest(f"nanopb=={m.REQUIRED_NANOPB_VERSION} python package not installed")
        out = self.dir / "out"
        report = m.generate(self.proto, out)
        header = Path(report["header"])
        source = Path(report["source"])
        self.assertTrue(header.is_file())
        self.assertTrue(source.is_file())
        self.assertIn(f"nanopb-{m.REQUIRED_NANOPB_VERSION}", header.read_text())

        result = subprocess.run(
            [
                "clang", "-c",
                "-I", str(NANOPB_RUNTIME), "-I", str(out),
                str(source), "-o", str(out / "example.pb.o"),
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        # Re-running against the same input is deterministic modulo the
        # generator's own path-comment lines; the field table itself repeats.
        out2 = self.dir / "out2"
        m.generate(self.proto, out2)
        self.assertEqual(source.read_bytes(), (out2 / "example.pb.c").read_bytes())


if __name__ == "__main__":
    unittest.main()
