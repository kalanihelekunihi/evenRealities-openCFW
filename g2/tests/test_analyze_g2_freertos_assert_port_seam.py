#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_freertos_assert_port_seam.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freertos_assert_port_seam",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load FreeRTOS assertion-seam analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSAssertPortSeamAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_exact_boundary_semantics_and_upstream_identity(self) -> None:
        result = self.analyzer.run_audit()

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["read_only"])
        function = result["function"]
        self.assertEqual(function["start"], 0x005FA0A4)
        self.assertEqual(function["end_exclusive"], 0x005FA0BA)
        self.assertEqual(function["size"], 22)
        self.assertEqual(
            function["sha256"],
            "f6bd0708e653c8e8880e33e298f9dc8"
            "ede1305c9386ea4ca5ff554d4022dc323",
        )
        self.assertEqual(
            function["abi"]["configMAX_SYSCALL_INTERRUPT_PRIORITY"],
            0x30,
        )
        self.assertEqual(function["abi"]["outgoing_calls"], [])
        self.assertEqual(function["abi"]["relocations_or_literals"], [])
        self.assertEqual(
            result["upstream"]["portable_layer"],
            "IAR/ARM_CM55_NTZ/non_secure",
        )
        self.assertEqual(result["upstream"]["license"], "MIT")

    def test_complete_reference_topology_is_pinned(self) -> None:
        references = self.analyzer.run_audit()["references"]
        self.assertEqual(references["direct_bl_count"], 181)
        self.assertEqual(
            references["direct_bl_callsite_sha256"],
            "f0187e62c4c399694d4fdd8e64a2e238"
            "724f6fb0ec89a6520c3020156eb9c106",
        )
        self.assertEqual(
            references["direct_bl_addresses"][0],
            0x0043C7EA,
        )
        self.assertEqual(
            references["direct_bl_addresses"][-1],
            0x005847D0,
        )
        for address in (
            0x004415D4,
            0x0044208C,
            0x00454F26,
            0x004561A2,
            0x0047E6C8,
            0x005847D0,
        ):
            self.assertIn(address, references["direct_bl_addresses"])
        self.assertEqual(references["direct_bw"], [])
        self.assertEqual(references["external_interior_wide"], [])
        self.assertEqual(
            references["external_entry_or_interior_narrow"],
            [],
        )
        self.assertEqual(references["stored_entry_or_interior"], [])

    def test_json_cli_is_read_only_and_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["read_only"])
        self.assertTrue(
            result["ownership_assessment"]["unequivocal_public_source"]
        )
        self.assertTrue(result["ownership_assessment"]["source_ownable"])
        self.assertTrue(
            result["ownership_assessment"][
                "fixed_seam_safe_while_official_provider_is_retained"
            ]
        )

    def test_authentication_rejects_a_mutated_package(self) -> None:
        package = bytearray(self.analyzer.DEFAULT_IMAGE.read_bytes())
        offset = (
            self.analyzer.PACKAGE_PREAMBLE_SIZE
            + self.analyzer.FUNCTION_START
            - self.analyzer.APPLICATION_BASE
        )
        package[offset] ^= 0x01
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "mutated.bin"
            mutated.write_bytes(package)
            with self.assertRaisesRegex(
                self.analyzer.AuditError,
                "package SHA-256 drift",
            ):
                self.analyzer.run_audit(mutated)


if __name__ == "__main__":
    unittest.main()
