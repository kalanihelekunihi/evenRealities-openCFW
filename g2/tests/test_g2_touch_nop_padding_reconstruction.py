# SPDX-License-Identifier: MIT
"""Tests for the G2 Touch residual NOP-padding reconstruction verifier."""

import importlib.util
import shutil
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/verify_g2_touch_nop_padding_reconstruction.py"
S = importlib.util.spec_from_file_location("g2_touch_nop_padding_reconstruction", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)

CLANG_AVAILABLE = Path("/opt/homebrew/opt/llvm/bin/clang").is_file() or shutil.which("clang")


@unittest.skipUnless(CLANG_AVAILABLE, "ARMv6-M clang toolchain unavailable")
class TouchNopPaddingReconstructionTests(unittest.TestCase):
    def test_pinned_buckets_are_loadable(self):
        pinned = M.load_pinned_buckets()
        self.assertIn("typed_code_residual_arch_nop_padding", pinned)
        self.assertIn("typed_code_residual_legacy_nop_padding", pinned)
        self.assertEqual(pinned["typed_code_residual_arch_nop_padding"]["bytes"], "8")
        self.assertEqual(pinned["typed_code_residual_legacy_nop_padding"]["bytes"], "126")

    def test_reconstruction_matches_pinned_stock_content(self):
        report = M.reconstruct()
        self.assertEqual(report["reconstructed_bytes"], 134)
        self.assertFalse(report["production_routed"])
        by_bucket = {entry["bucket"]: entry for entry in report["categories"]}
        arch = by_bucket["typed_code_residual_arch_nop_padding"]
        self.assertEqual(arch["bytes"], 8)
        self.assertEqual(arch["compiled_encoding"], "00bf")
        self.assertEqual(
            arch["content_sha256"],
            "0fbf3781a949ae1c40a167e8b22998fc9b6135f6d0135f97da55de21d94f0b01",
        )
        legacy = by_bucket["typed_code_residual_legacy_nop_padding"]
        self.assertEqual(legacy["bytes"], 126)
        self.assertEqual(legacy["compiled_encoding"], "c046")
        self.assertEqual(
            legacy["content_sha256"],
            "ce9feda3cee7af78db19513116d9f98419f1fc6d421c618e5b56fecb26e16c0e",
        )

    def test_wrong_pinned_digest_is_rejected(self):
        original_loader = M.load_pinned_buckets
        pinned = original_loader()
        pinned["typed_code_residual_arch_nop_padding"]["content_sha256"] = "0" * 64
        try:
            M.load_pinned_buckets = lambda: pinned
            with self.assertRaises(M.ReconstructionError):
                M.reconstruct()
        finally:
            M.load_pinned_buckets = original_loader


if __name__ == "__main__":
    unittest.main()
