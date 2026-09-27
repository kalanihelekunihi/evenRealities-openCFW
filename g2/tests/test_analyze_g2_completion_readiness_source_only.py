"""Unit tests for the ``--require-source-only`` fail-closed gate.

These exercise ``source_only_gate`` in isolation against synthetic
per-component rows so the test does not depend on the live, constantly
mutating repository state that ``analyze_g2_completion_readiness.analyze()``
composes from (several other agents rebuild those inputs concurrently; see
``tests.test_analyze_g2_completion_readiness`` for the live-data assertions).
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness  # noqa: E402

SIX_COMPONENTS = (
    "apollo_main", "apollo_bootloader", "ble_em9305",
    "codec", "touch", "case",
)


def _row(*, release_blocking_bytes: int, production_routed: bool) -> dict:
    return {
        "release_blocking_bytes": release_blocking_bytes,
        "production_routed": production_routed,
        "source_complete": release_blocking_bytes == 0,
    }


class SourceOnlyGateTests(unittest.TestCase):
    def test_ready_when_every_component_is_complete_and_routed(self) -> None:
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        result = readiness.source_only_gate(components)
        self.assertTrue(result["ready"])
        self.assertEqual(result["blocking_bytes_by_component"], {})
        self.assertEqual(result["not_production_routed_components"], [])
        self.assertEqual(result["global_blockers"], [])

    def test_retained_bytes_block_even_when_production_routed(self) -> None:
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        components["codec"] = _row(
            release_blocking_bytes=326_000, production_routed=True
        )
        result = readiness.source_only_gate(components)
        self.assertFalse(result["ready"])
        self.assertEqual(result["blocking_bytes_by_component"], {"codec": 326_000})
        self.assertEqual(result["not_production_routed_components"], [])
        self.assertEqual(result["global_blockers"], [])

    def test_unrouted_candidate_blocks_even_with_zero_blocking_bytes(self) -> None:
        """A source candidate that is not production-routed must not count
        as completion, even if its own byte ledger claims zero retained
        bytes -- this is the exact gap the completion goal calls out."""
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        components["touch"] = _row(release_blocking_bytes=0, production_routed=False)
        result = readiness.source_only_gate(components)
        self.assertFalse(result["ready"])
        self.assertIn("touch", result["blocking_bytes_by_component"])
        self.assertEqual(result["blocking_bytes_by_component"]["touch"], 0)
        self.assertEqual(result["not_production_routed_components"], ["touch"])
        self.assertEqual(result["global_blockers"], [])

    def test_every_component_missing_is_all_blocking(self) -> None:
        components = {
            name: _row(release_blocking_bytes=100, production_routed=False)
            for name in SIX_COMPONENTS
        }
        result = readiness.source_only_gate(components)
        self.assertFalse(result["ready"])
        self.assertEqual(
            set(result["blocking_bytes_by_component"]), set(SIX_COMPONENTS)
        )
        self.assertEqual(
            set(result["not_production_routed_components"]), set(SIX_COMPONENTS)
        )
        self.assertEqual(result["global_blockers"], [])

    def test_global_quality_debt_blocks_even_when_components_are_ready(self) -> None:
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        result = readiness.source_only_gate(
            components,
            source_ownership_quality_clean=False,
            project_license_policy_clean=True,
        )
        self.assertFalse(result["ready"])
        self.assertEqual(result["blocking_bytes_by_component"], {})
        self.assertEqual(result["not_production_routed_components"], [])
        self.assertEqual(result["global_blockers"], ["source_ownership_quality"])

    def test_project_license_policy_debt_blocks_even_when_components_are_ready(self) -> None:
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        result = readiness.source_only_gate(
            components,
            source_ownership_quality_clean=True,
            project_license_policy_clean=False,
        )
        self.assertFalse(result["ready"])
        self.assertEqual(result["blocking_bytes_by_component"], {})
        self.assertEqual(result["not_production_routed_components"], [])
        self.assertEqual(result["global_blockers"], ["project_license_policy"])

    def test_manifest_name_is_recorded(self) -> None:
        components = {
            name: _row(release_blocking_bytes=0, production_routed=True)
            for name in SIX_COMPONENTS
        }
        result = readiness.source_only_gate(components)
        self.assertEqual(
            result["manifest"], "manifests/g2-2.2.6.10-source-only.json"
        )


class RequireSourceOnlyCLITests(unittest.TestCase):
    """The gate must be wired into main() and always report per-component
    bytes on failure, whether or not --json was also passed."""

    def test_flag_is_registered_and_help_documents_it(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools/analyze_g2_completion_readiness.py"),
             "--help"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("--require-source-only", completed.stdout)

    @staticmethod
    def _fake_report(*, ready: bool) -> dict:
        components = {
            name: _row(release_blocking_bytes=0 if ready else 42,
                       production_routed=True)
            for name in SIX_COMPONENTS
        }
        gate = readiness.source_only_gate(components)
        return {
            "components": components,
            "aggregate": {"component_payload_bytes": 0,
                          "buckets": {"unclassified": 0},
                          "release_blocking_bytes": 0},
            "source_only": gate,
            "gates": {
                "classification_complete": True,
                "source_complete": True,
                "source_only_ready": gate["ready"],
                "source_ownership_quality_clean": True,
                "project_license_policy_clean": True,
                "release_authorized": True,
            },
            "source_ownership_quality": {
                "source_owned_bytes_currently_overstated": 0,
            },
            "project_license_policy": {
                "project_owned_gpl_records_pending_mit": 0,
            },
        }

    def test_main_returns_zero_when_source_only_is_ready(self) -> None:
        with mock.patch.object(readiness, "analyze",
                                return_value=self._fake_report(ready=True)), \
             mock.patch.object(sys, "argv",
                                ["analyze_g2_completion_readiness.py",
                                 "--require-source-only"]):
            self.assertEqual(readiness.main(), 0)

    def test_main_returns_six_and_reports_bytes_when_not_ready(self) -> None:
        report = self._fake_report(ready=False)
        with mock.patch.object(readiness, "analyze", return_value=report), \
             mock.patch.object(sys, "argv",
                                ["analyze_g2_completion_readiness.py",
                                 "--require-source-only"]):
            self.assertEqual(readiness.main(), 6)
        # Every blocking component's exact byte count must be discoverable
        # from the same report main() printed from.
        self.assertEqual(
            report["source_only"]["blocking_bytes_by_component"],
            {name: 42 for name in SIX_COMPONENTS},
        )

    def test_require_source_only_does_not_mask_other_gate_failures(self) -> None:
        """--require-source-only alone must not report success (0) when the
        underlying report says source-only is not ready."""
        report = self._fake_report(ready=False)
        with mock.patch.object(readiness, "analyze", return_value=report), \
             mock.patch.object(sys, "argv",
                                ["analyze_g2_completion_readiness.py",
                                 "--require-source-only", "--json"]):
            self.assertNotEqual(readiness.main(), 0)


if __name__ == "__main__":
    unittest.main()
