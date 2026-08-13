#!/usr/bin/env python3
"""Guard the fail-closed G2 nanopb point-release audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_nanopb_point_release.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_nanopb_point_release", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NanopbPointReleaseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer.MAIN.read_bytes()

    def test_identity_and_fail_closed_result_are_pinned(self) -> None:
        report = self.analyzer.audit_image(self.data)
        self.assertEqual(report["status"], "point release unresolved")
        self.assertIsNone(report["exact_point_release"])
        self.assertEqual(
            report["candidate_releases_if_pristine_upstream"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        self.assertEqual(
            report["excluded_pristine_upstream_releases"],
            ["0.4.4", "0.4.5", "0.4.6"],
        )
        self.assertIn("backport", report["qualification"])
        self.assertEqual(report["embedded_candidate_version_strings"], [])
        self.assertEqual(
            report["firmware_build_timestamp"]["value"],
            "2025-04-28T13:29:15Z",
        )
        self.assertFalse(report["nanopb_0_4_9_1"]["changed_function_retained"])

    def test_discriminating_instruction_shapes_are_pinned(self) -> None:
        report = self.analyzer.audit_image(self.data)
        evidence = report["discriminators"]
        self.assertEqual(
            evidence["pb_read_saturating_clamp"],
            {
                "address": 0x0048F43C,
                "introduced": "0.4.7",
                "meaning": "clamp bytes_left to zero if callback consumed more than count",
            },
        )
        self.assertEqual(
            evidence["pb_decode_varint_63bit_guard"]["address"], 0x0048F5D4
        )
        self.assertEqual(
            evidence["pb_decode_varint_63bit_guard"]["introduced"], "0.4.6"
        )
        self.assertTrue(report["runtime_collision"]["reference_build_result"])

    def test_code_ranges_and_hashes_are_pinned(self) -> None:
        report = self.analyzer.audit_image(self.data)
        self.assertEqual(report["code"]["pb_read"], [0x0048F3BE, 0x0048F454])
        self.assertEqual(
            report["code"]["pb_decode_varint"], [0x0048F5B8, 0x0048F628]
        )
        self.assertEqual(
            report["code"]["sha256"], self.analyzer.PINNED_REGION_SHA256
        )

    def test_upstream_source_and_license_identities_are_complete(self) -> None:
        releases = self.analyzer.UPSTREAM_RELEASES
        self.assertEqual(
            list(releases),
            ["0.4.4", "0.4.5", "0.4.6", "0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        commits = {release["commit"] for release in releases.values()}
        trees = {release["tree"] for release in releases.values()}
        self.assertEqual(len(commits), 7)
        self.assertEqual(len(trees), 7)
        for release in releases.values():
            self.assertEqual(set(release["files"]), set(self.analyzer.UPSTREAM_FILES))
            self.assertEqual(
                release["files"]["LICENSE.txt"],
                self.analyzer.UPSTREAM_LICENSE_SHA256,
            )
        self.assertEqual(self.analyzer.UPSTREAM_LICENSE, "Zlib")

    def test_reference_hashes_prove_three_way_collision(self) -> None:
        objects = self.analyzer.REFERENCE_APPLE_CLANG_OBJECTS
        self.assertEqual(objects["0.4.7"], objects["0.4.8"])
        self.assertEqual(objects["0.4.8"], objects["0.4.9"])
        self.assertEqual(objects["0.4.9"][0], objects["0.4.9.1"][0])
        self.assertNotEqual(objects["0.4.9"][1], objects["0.4.9.1"][1])
        self.assertEqual(objects["0.4.9"][2], objects["0.4.9.1"][2])
        self.assertNotEqual(objects["0.4.6"][1], objects["0.4.7"][1])

    def test_mutated_or_truncated_image_is_rejected(self) -> None:
        mutated = bytearray(self.data)
        mutated[
            self.analyzer.PB_READ_SATURATING_CLAMP_ADDRESS - self.analyzer.LOAD_BASE
        ] ^= 1
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit_image(bytes(mutated))
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit_image(self.data[:-1])

    def test_cli_json_is_machine_readable(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        report = json.loads(completed.stdout)
        self.assertIsNone(report["exact_point_release"])
        self.assertEqual(
            report["candidate_releases_if_pristine_upstream"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )


if __name__ == "__main__":
    unittest.main()
