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
ANALYZER = (
    ROOT / "tools" / "analyze_g2_freertos_queue_wrapper_tranche.py"
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freertos_queue_wrapper_tranche",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load queue-wrapper analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSQueueWrapperTrancheAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.result = cls.analyzer.run_audit()

    def test_exact_boundaries_hashes_and_released_source_are_pinned(
        self,
    ) -> None:
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["read_only"])
        expected = {
            "xQueueCreateMutexStatic": (
                0x004416F0,
                0x00441710,
                32,
                "2977000da7aab5b87abce1270dca651"
                "8785de04a1e72d08082802713d478fd28",
            ),
            "xQueueCreateCountingSemaphoreStatic": (
                0x00441790,
                0x004417C2,
                50,
                "a46100f23dd51b8276a4c2ebafa1ba96"
                "c6813114810ae0f5297764c20368eb62",
            ),
            "xQueueCreateCountingSemaphore": (
                0x004417C2,
                0x004417EE,
                44,
                "ed30ebca04b655b1ec31e60296d977382"
                "d0712057db88f99b205a555b374120f",
            ),
        }
        for name, values in expected.items():
            function = self.result["functions"][name]
            self.assertEqual(
                (
                    function["start"],
                    function["end_exclusive"],
                    function["size"],
                    function["sha256"],
                ),
                values,
            )
        self.assertEqual(
            self.result["ordered_tranche"],
            {
                "functions": [
                    "xQueueCreateMutexStatic",
                    "xQueueCreateCountingSemaphoreStatic",
                    "xQueueCreateCountingSemaphore",
                ],
                "total_size": 126,
                "sha256": (
                    "1d305cd5e6313c35b3489f26b310b416"
                    "1252543b882bc6c62e9c55d567523460"
                ),
            },
        )
        self.assertEqual(
            self.result["upstream"]["commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(self.result["upstream"]["license"], "MIT")
        self.assertEqual(
            set(self.result["upstream"]["function_blocks"]),
            set(expected),
        )

    def test_complete_reference_topology_is_pinned(self) -> None:
        expected_callers = {
            "xQueueCreateMutexStatic": [
                0x0043C7DE,
                0x00449778,
                0x00449784,
            ],
            "xQueueCreateCountingSemaphoreStatic": [
                0x00449938,
                0x00449CCA,
            ],
            "xQueueCreateCountingSemaphore": [0x00449944],
        }
        for name, callers in expected_callers.items():
            references = self.result["functions"][name]["references"]
            self.assertEqual(
                [item["address"] for item in references["direct_bl"]],
                callers,
            )
            self.assertEqual(references["direct_bl_count"], len(callers))
            self.assertEqual(references["direct_bw"], [])
            self.assertEqual(references["external_interior_wide"], [])
            self.assertEqual(
                references["external_entry_or_interior_narrow"],
                [],
            )
            self.assertEqual(references["stored_entry_or_interior"], [])

    def test_outgoing_queue_dependencies_are_currently_source_owned(
        self,
    ) -> None:
        closure = self.result["dependency_closure"]
        self.assertTrue(closure["all_queue_dependencies_source_owned"])
        self.assertEqual(
            {
                item["official_entry"]
                for item in closure["queue_dependencies"]
            },
            {0x004415CA, 0x00441636, 0x004416B8},
        )
        self.assertEqual(
            closure["remaining_non_queue_dependency"]["entry"],
            0x005FA0A4,
        )

        outgoing = {
            name: [
                (item["address"], item["target"])
                for item in function["outgoing_calls"]
            ]
            for name, function in self.result["functions"].items()
        }
        self.assertEqual(
            outgoing["xQueueCreateMutexStatic"],
            [
                (0x00441700, 0x004415CA),
                (0x00441708, 0x004416B8),
            ],
        )
        self.assertEqual(
            outgoing["xQueueCreateCountingSemaphoreStatic"],
            [
                (0x004417A8, 0x004415CA),
                (0x004417B4, 0x005FA0A4),
            ],
        )
        self.assertEqual(
            outgoing["xQueueCreateCountingSemaphore"],
            [
                (0x004417D4, 0x00441636),
                (0x004417E0, 0x005FA0A4),
            ],
        )

    def test_recovered_configuration_and_abi_are_explicit(self) -> None:
        configuration = self.result["configuration"]
        self.assertEqual(configuration["configUSE_MUTEXES"], 1)
        self.assertEqual(configuration["configUSE_COUNTING_SEMAPHORES"], 1)
        self.assertEqual(
            configuration["configSUPPORT_STATIC_ALLOCATION"],
            1,
        )
        self.assertEqual(
            configuration["configSUPPORT_DYNAMIC_ALLOCATION"],
            1,
        )
        self.assertEqual(
            configuration["queueSEMAPHORE_QUEUE_ITEM_LENGTH"],
            0,
        )
        self.assertEqual(
            configuration["queueQUEUE_TYPE_COUNTING_SEMAPHORE"],
            2,
        )
        self.assertEqual(
            configuration["Queue_t.messages_waiting_offset"],
            0x38,
        )
        self.assertEqual(configuration["StaticQueue_t_size"], 0x50)
        self.assertEqual(configuration["UBaseType_t_bits"], 32)

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
        self.assertEqual(
            result["ownership_assessment"]["remaining_port_seam"],
            0x005FA0A4,
        )

    def test_authentication_rejects_a_mutated_package(self) -> None:
        package = bytearray(self.analyzer.DEFAULT_IMAGE.read_bytes())
        offset = (
            self.analyzer.PACKAGE_PREAMBLE_SIZE
            + self.analyzer.FUNCTIONS["xQueueCreateMutexStatic"]["start"]
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
