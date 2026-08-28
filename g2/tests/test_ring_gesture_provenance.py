# SPDX-License-Identifier: MIT
"""Fail-closed tests for the offline ring-gesture GPL provenance proof."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "apollo_main" / "ring_gesture"
VERIFIER = COMPONENT / "verify_provenance.py"
EVIDENCE_FILES = (
    "PROVENANCE.json",
    "DERIVATION.patch",
    "LICENSE",
    "NOTICE.md",
    "overlay.json",
    "ring_gesture.c",
    "upstream/gesture_fwd.c",
)


def load_verifier():
    spec = importlib.util.spec_from_file_location("ring_gesture_provenance", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RingGestureProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verifier = load_verifier()

    def copy_evidence(self, destination: Path) -> Path:
        component = destination / "ring_gesture"
        for name in EVIDENCE_FILES:
            source = COMPONENT / name
            target = component / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return component

    def test_exact_commit_tree_path_blob_and_license_chain_verifies(self) -> None:
        report = self.verifier.verify()
        self.assertEqual(
            report,
            {
                "commit": "6d5c58598e047ca5980065a9ee7570ce2d172ca7",
                "upstream_path": "patches/gesture_fwd.c",
                "upstream_blob": "4997b81d4afa1ede5bd15c79957509f65ec75828",
                "checked_in_sha256": "e7824afc0f4d3f567b6b6247df3c0198e2af18275644313da9b199fd3b33605f",
                "license_blob": "e72bfddabc15be5718a7cc061ac10e47741d8219",
                "network_used": False,
                "hardware_used": False,
            },
        )

    def test_verifier_has_no_network_or_git_process_dependency(self) -> None:
        source = VERIFIER.read_text(encoding="utf-8")
        for forbidden in (
            "import socket",
            "import subprocess",
            "import urllib",
            "import requests",
            "git clone",
            "git fetch",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_checked_in_source_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "ring_gesture.c"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "checked-in source size"):
                self.verifier.verify(component)

    def test_upstream_blob_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "upstream" / "gesture_fwd.c"
            data = bytearray(path.read_bytes())
            data[0] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "upstream source SHA-256"):
                self.verifier.verify(component)

    def test_commit_tree_path_evidence_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            entries = value["git_objects"]["patches_tree"]["entries"]
            next(entry for entry in entries if entry["name"] == "gesture_fwd.c")[
                "name"
            ] = "gesture_forward.c"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "patches tree proof"):
                self.verifier.verify(component)

    def test_license_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "LICENSE"
            data = bytearray(path.read_bytes())
            data[100] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "license SHA-256"):
                self.verifier.verify(component)

    def test_derivation_diff_must_match_both_exact_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "DERIVATION.patch"
            data = bytearray(path.read_bytes())
            data[-1] = ord(" ")
            path.write_bytes(data)
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "derivation diff SHA-256"):
                self.verifier.verify(component)

    def test_overlay_claim_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            component = self.copy_evidence(Path(temporary))
            path = component / "overlay.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["source"]["upstream_commit"] = "0" * 40
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(self.verifier.ProvenanceError, "overlay source provenance"):
                self.verifier.verify(component)


if __name__ == "__main__":
    unittest.main()
