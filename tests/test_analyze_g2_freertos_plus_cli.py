#!/usr/bin/env python3
"""Guard the fail-closed G2 FreeRTOS-Plus-CLI recovery audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_freertos_plus_cli.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_freertos_plus_cli", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSPlusCLIAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer.MAIN.read_bytes()
        cls.report = cls.analyzer.audit_image(cls.data)

    def test_result_fails_closed_as_source_plus_patch(self) -> None:
        self.assertEqual(
            self.report["status"],
            "official MIT V1.0.4-compatible source base plus one proven Even patch",
        )
        self.assertIsNone(self.report["exact_historical_upstream_commit"])
        self.assertIsNone(self.report["exact_historical_component_version"])
        self.assertFalse(self.report["local_patch"]["present_in_official_history"])
        self.assertEqual(
            self.report["local_patch"]["behavior"],
            "do not emit unknown-command text for exactly CR or empty input",
        )

    def test_function_ranges_and_hashes_are_exact(self) -> None:
        self.assertEqual(
            self.report["code"]["FreeRTOS_CLIProcessCommand"]["range"],
            [0x005847FE, 0x005848FC],
        )
        self.assertEqual(
            self.report["code"]["FreeRTOS_CLIRegisterCommand"]["size"], 82
        )
        self.assertEqual(
            self.report["local_patch"]["range"], [0x005848CA, 0x005848F4]
        )

    def test_descriptor_and_callback_abi_are_recovered(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["descriptor_size"], 16)
        self.assertEqual(
            abi["descriptor_fields"],
            {
                "pcCommand": 0,
                "pcHelpString": 4,
                "pxCommandInterpreter": 8,
                "cExpectedNumberOfParameters": 12,
            },
        )
        self.assertEqual(abi["variable_parameter_sentinel"], -1)
        self.assertTrue(abi["negative_expected_counts_bypass_validation"])
        self.assertEqual(abi["list_node_size"], 8)
        self.assertEqual(abi["size_t_bytes"], 4)

    def test_buffers_and_limits_are_recovered_without_inventing_macro(self) -> None:
        buffers = self.report["buffers"]
        self.assertEqual(
            buffers["effective_output"], {"address": 0x20071B48, "bytes": 128}
        )
        self.assertEqual(buffers["input"]["address"], 0x20071BC8)
        self.assertEqual(buffers["input"]["safe_nul_terminated_payload_max"], 127)
        self.assertIn("not recoverable", buffers["configCOMMAND_INT_MAX_OUTPUT_SIZE"])
        parameters = self.report["parameters"]
        self.assertEqual(parameters["vendor_descriptor_range"], [-1, 3])
        self.assertEqual(parameters["highest_parameter_index_requested_by_retained_handlers"], 11)
        self.assertIsNone(parameters["FreeRTOS_CLIGetParameter_internal_limit"])

    def test_dynamic_allocation_policy_is_pinned(self) -> None:
        allocation = self.report["allocation"]
        self.assertEqual(allocation["observed_registration_api"], "dynamic")
        self.assertEqual(allocation["vendor_dynamic_nodes"], 76)
        self.assertEqual(allocation["minimum_payload_bytes_allocated"], 608)
        self.assertFalse(allocation["free_path"])
        self.assertFalse(allocation["static_registration_observed"])
        self.assertEqual(
            allocation["static_registration_body_identity"], "not established"
        )
        self.assertIn("not statically proven", allocation["configSUPPORT_STATIC_ALLOCATION"])

    def test_vendor_descriptor_census_is_complete(self) -> None:
        glue = self.report["vendor_glue"]
        commands = glue["commands"]
        self.assertEqual(len(commands), 76)
        self.assertEqual([item["command"] for item in commands], list(self.analyzer.VENDOR_COMMAND_NAMES))
        self.assertEqual(commands[0]["command"], "reset")
        self.assertEqual(commands[-1]["command"], "get")
        self.assertEqual(self.report["parameters"]["vendor_distribution"], {"-1": 15, "0": 19, "1": 27, "2": 12, "3": 3})

    def test_upstream_commit_tree_blob_and_license_pins_are_complete(self) -> None:
        upstream = self.analyzer.UPSTREAM
        self.assertEqual(upstream["license"], "MIT")
        self.assertEqual(
            upstream["selected"]["commit"],
            "43defa566cc440251dbd6b48d1fcca27f88cfcdd",
        )
        self.assertEqual(
            upstream["historical_semantic_floor"]["commit"],
            "747a0e15faf033e9b80cfec0c31b68a29b304f92",
        )
        self.assertEqual(
            upstream["identical_file_pair_ceiling"]["commit"],
            "1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2",
        )
        self.assertEqual(len(upstream["files"]), 4)
        for identity in upstream["files"].values():
            self.assertEqual(len(identity["git_blob"]), 40)
            self.assertEqual(len(identity["sha256"]), 64)

    def test_mutated_and_truncated_images_are_rejected(self) -> None:
        mutated = bytearray(self.data)
        mutated[0x005848CA - self.analyzer.LOAD_BASE] ^= 1
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
        self.assertEqual(report["vendor_glue"]["registered_descriptor_count"], 76)
        self.assertIsNone(report["exact_historical_upstream_commit"])


if __name__ == "__main__":
    unittest.main()
