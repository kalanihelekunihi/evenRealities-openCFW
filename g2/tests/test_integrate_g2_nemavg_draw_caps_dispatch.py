#!/usr/bin/env python3
from __future__ import annotations

# SPDX-License-Identifier: MIT

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INTEGRATOR = ROOT / "tools/integrate_g2_nemavg_draw_caps_dispatch.py"


def load_integrator():
    name = "integrate_g2_nemavg_draw_caps_dispatch_under_test"
    spec = importlib.util.spec_from_file_location(name, INTEGRATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class NemaDrawCapsIntegratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.integrator = load_integrator()

    def _relocations(self, error_offset: int) -> list[dict[str, object]]:
        return [
            {
                "offset": 2,
                "symbol": "open_cfw_retained_nemavg_draw_start_cap",
                "symbol_type": "STT_NOTYPE",
                "target_address": 0x0051B8F0,
                "type": "R_ARM_THM_CALL",
            },
            {
                "offset": 8,
                "symbol": "open_cfw_retained_nemavg_draw_end_cap",
                "symbol_type": "STT_NOTYPE",
                "target_address": 0x0051BF7C,
                "type": "R_ARM_THM_CALL",
            },
            {
                "offset": error_offset,
                "symbol": "open_cfw_retained_nemavg_set_error",
                "symbol_type": "STT_NOTYPE",
                "target_address": 0x0051565C,
                "type": "R_ARM_THM_CALL",
            },
        ]

    def _observation(self, profile: str) -> dict[str, object]:
        apple = profile == "apple-clang"
        relocations = self._relocations(34 if apple else 30)
        pins = {
            "alignment": 4,
            "offset": 360580 if apple else 145316,
            "sha256": "a" * 64 if apple else "b" * 64,
            "size": 52 if apple else 48,
            "unrelocated_sha256": "c" * 64 if apple else "d" * 64,
            "relocations": relocations,
        }
        return {
            "core_stage": {
                "expected": {
                    "component_size": 100 if apple else 101,
                    "component_sha256": "e" * 64 if apple else "f" * 64,
                    "overlay_size": 90 if apple else 91,
                    "overlay_sha256": "1" * 64 if apple else "2" * 64,
                },
                "relocated_leaves": [
                    {
                        "extraction": {
                            "function": self.integrator.COORDINATOR,
                        },
                        "pins": pins,
                        "toolchain": {},
                    }
                ],
            },
            "liblc3_ltpf": {
                "payload_size": 20 if apple else 21,
                "payload_sha256": "3" * 64 if apple else "4" * 64,
                "component_size": 30 if apple else 31,
                "component_sha256": "5" * 64 if apple else "6" * 64,
            },
            "source_inputs": {
                "entries": [],
                "sha256": "7" * 64,
            },
        }

    def _config(self) -> dict[str, object]:
        return {
            "functions": [
                "unrelated_function",
                self.integrator.START_ENDPOINT,
                self.integrator.COORDINATOR,
                self.integrator.END_ENDPOINT,
                self.integrator.COORDINATOR,
            ],
            "patch_sites": [
                {
                    "name": "unrelated_patch",
                    "runtime_address": 0x00500000,
                    "target_function": "unrelated_function",
                },
                {
                    "name": "old_start",
                    "runtime_address": 0x0051B8F0,
                    "target_function": self.integrator.START_ENDPOINT,
                },
                {
                    "name": "old_end_alias",
                    "runtime_address": 0x00500004,
                    "target_function": self.integrator.END_ENDPOINT,
                },
                {
                    "name": "old_dispatch",
                    "runtime_address": 0x0051C5EC,
                    "target_function": self.integrator.COORDINATOR,
                },
            ],
            "relocated_leaves": [
                {"function": "unrelated_function", "keep": True},
                {"function": self.integrator.START_ENDPOINT},
                {"function": self.integrator.END_ENDPOINT},
                {"function": self.integrator.COORDINATOR},
            ],
            "core_stage_expected": {"stale": True},
            "toolchain_profiles": {
                "linux-clang": {"core_stage_expected": {"stale": True}},
            },
            "post_link_providers": {
                "liblc3_ltpf": {
                    "profiles": {
                        "apple-clang": {},
                        "linux-clang": {},
                    }
                }
            },
        }

    def test_restore_is_exactly_coordinator_only_and_removes_endpoint_routes(
        self,
    ) -> None:
        apple = self._observation("apple-clang")
        linux = self._observation("linux-clang")
        proposed = self.integrator._restore_semantics(
            self._config(), apple, linux
        )

        self.assertEqual(
            proposed["functions"],
            ["unrelated_function", self.integrator.COORDINATOR],
        )
        self.assertEqual(
            proposed["patch_sites"],
            [
                {
                    "name": "unrelated_patch",
                    "runtime_address": 0x00500000,
                    "target_function": "unrelated_function",
                },
                self.integrator.PATCH,
            ],
        )
        leaves = proposed["relocated_leaves"]
        self.assertEqual(
            [item["function"] for item in leaves],
            ["unrelated_function", self.integrator.COORDINATOR],
        )
        coordinator = leaves[-1]
        self.assertTrue(coordinator["strict_relocation_contract"])
        self.assertEqual(coordinator["source"], self.integrator.SOURCE_IDENTITY)
        self.assertEqual(
            coordinator["toolchain"]["flags"], self.integrator.FLAGS
        )
        self.assertEqual(
            coordinator["toolchain"]["reviewed_version_prefix"],
            "Apple clang version 21.0.0",
        )
        self.assertEqual(
            coordinator["toolchain_profiles"]["linux-clang"]
            ["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        for relocation in (
            coordinator["relocations"]
            + coordinator["toolchain_profiles"]["linux-clang"]["relocations"]
        ):
            self.assertIn("target_address", relocation)
            self.assertNotIn("target_function", relocation)
        self.assertEqual(
            [item["target_address"] for item in coordinator["relocations"]],
            [0x0051B8F0, 0x0051BF7C, 0x0051565C],
        )

        encoded = json.dumps(proposed, sort_keys=True)
        self.assertNotIn(self.integrator.START_ENDPOINT, encoded)
        self.assertNotIn(self.integrator.END_ENDPOINT, encoded)

    def test_restore_does_not_mutate_the_live_input_object(self) -> None:
        config = self._config()
        original = copy.deepcopy(config)
        self.integrator._restore_semantics(
            config,
            self._observation("apple-clang"),
            self._observation("linux-clang"),
        )
        self.assertEqual(config, original)

    def test_pins_reject_target_function_relocations(self) -> None:
        observation = self._observation("apple-clang")
        relocation = observation["core_stage"]["relocated_leaves"][0][
            "pins"
        ]["relocations"][0]
        relocation["target_function"] = self.integrator.START_ENDPOINT
        with self.assertRaisesRegex(
            self.integrator.admission.AdmissionError,
            "retains both endpoint providers",
        ):
            self.integrator._pins(observation, (2, 8, 34))

    def test_pins_reject_malformed_and_wrong_offset_relocations(self) -> None:
        malformed = self._observation("apple-clang")
        malformed["core_stage"]["relocated_leaves"][0]["pins"][
            "relocations"
        ][1] = "not-an-object"
        with self.assertRaisesRegex(
            self.integrator.admission.AdmissionError,
            "relocation receipt changed",
        ):
            self.integrator._pins(malformed, (2, 8, 34))

        wrong_offset = self._observation("apple-clang")
        wrong_offset["core_stage"]["relocated_leaves"][0]["pins"][
            "relocations"
        ][2]["offset"] = 30
        with self.assertRaisesRegex(
            self.integrator.admission.AdmissionError,
            "relocation receipt changed",
        ):
            self.integrator._pins(wrong_offset, (2, 8, 34))

    def test_review_snapshots_proposed_config_and_does_not_write_live_config(
        self,
    ) -> None:
        apple = self._observation("apple-clang")
        linux = self._observation("linux-clang")
        apple_receipt = {"observation": apple}
        linux_receipt = {"observation": linux}
        snapshot = [{"path": "proposed", "size": 1, "sha256": "8" * 64}]

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "overlay.json"
            original = (json.dumps(self._config(), indent=2) + "\n").encode()
            config_path.write_bytes(original)
            with (
                mock.patch.object(self.integrator, "CONFIG", config_path),
                mock.patch.object(
                    self.integrator.admission,
                    "admit_reproducible_pair",
                    side_effect=[
                        (apple_receipt, copy.deepcopy(apple_receipt)),
                        (linux_receipt, copy.deepcopy(linux_receipt)),
                    ],
                ),
                mock.patch.object(
                    self.integrator.admission,
                    "validate_observation_independence",
                ),
                mock.patch.object(
                    self.integrator.admission, "validate_generation"
                ),
                mock.patch.object(
                    self.integrator.builder,
                    "_canonical_input_snapshot",
                    return_value=snapshot,
                ) as take_snapshot,
                mock.patch.object(
                    self.integrator.builder,
                    "_canonical_input_report",
                    return_value={"sha256": "9" * 64},
                ),
                mock.patch.object(
                    self.integrator.admission, "validate_current_inputs"
                ) as validate_inputs,
                mock.patch.object(
                    self.integrator.admission,
                    "_require_reviewed_core_leaf_pins",
                ),
                mock.patch.object(
                    self.integrator.admission, "update_profile_pins"
                ),
            ):
                proposed, report = self.integrator.review(
                    [Path("apple-a"), Path("apple-b"),
                     Path("linux-a"), Path("linux-b")]
                )

            self.assertEqual(config_path.read_bytes(), original)
            snapshot_config = take_snapshot.call_args.args[2]
            self.assertEqual(snapshot_config, proposed)
            self.assertIsNot(snapshot_config, self._config())
            validate_inputs.assert_called_once_with(
                apple["source_inputs"], snapshot
            )
            self.assertEqual(
                report["source_inputs"],
                {"entries": 1, "sha256": "9" * 64},
            )
            self.assertEqual(
                report["endpoint_entries_unpatched"],
                ["0x0051B8F0", "0x0051BF7C"],
            )

    def test_main_writes_only_explicit_proposal_without_apply(self) -> None:
        proposed = {"proposal": True}
        report = {"status": "reviewed-coordinator-core-pin-proposal"}
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            proposal = Path(directory) / "coordinator-overlay.json"
            argv = [
                str(INTEGRATOR),
                "--review-observations",
                "apple-a", "apple-b", "linux-a", "linux-b",
                "--proposal", str(proposal),
            ]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    self.integrator,
                    "review",
                    return_value=(proposed, report),
                ),
                mock.patch.object(
                    self.integrator.admission, "atomic_write"
                ) as atomic_write,
                mock.patch("builtins.print"),
            ):
                self.assertEqual(self.integrator.main(), 0)
            atomic_write.assert_called_once()
            self.assertEqual(atomic_write.call_args.args[0], proposal)
            self.assertNotEqual(atomic_write.call_args.args[0], self.integrator.CONFIG)
            self.assertEqual(
                json.loads(atomic_write.call_args.args[1]), proposed
            )
            self.assertEqual(
                report["status"], "reviewed-coordinator-core-pin-proposal"
            )

    def test_main_rejects_live_config_and_symlink_alias_proposal_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            alias = Path(directory) / "overlay-alias.json"
            alias.symlink_to(self.integrator.CONFIG)
            for proposal in (self.integrator.CONFIG, alias):
                argv = [
                    str(INTEGRATOR),
                    "--review-observations",
                    "apple-a", "apple-b", "linux-a", "linux-b",
                    "--proposal", str(proposal),
                ]
                with (
                    self.subTest(proposal=proposal),
                    mock.patch.object(sys, "argv", argv),
                    mock.patch.object(self.integrator, "review") as review,
                    mock.patch.object(
                        self.integrator.admission, "atomic_write"
                    ) as atomic_write,
                ):
                    with self.assertRaisesRegex(
                        SystemExit, "proposal path must differ from live config"
                    ):
                        self.integrator.main()
                    review.assert_not_called()
                    atomic_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
