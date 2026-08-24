from __future__ import annotations

import importlib.util
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "qualify_hardware_candidate", ROOT / "tools" / "qualify_hardware_candidate.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture() -> tuple[bytes, dict]:
    payload = bytearray(b"\x00" * 512)
    struct.pack_into("<II", payload, 32, 0x2007FB00, 0x005E4233)
    payload[320:330] = b"2.2.6.10\0\0"
    payload[400:410] = b"2.2.6.10\0\0"
    package = b"prefix" + bytes(payload) + b"suffix"
    report = {
        "apollo_main": {
            "payload_offset": 6,
            "payload_size": len(payload),
            "runtime_version_fields": {
                "settings": {"payload_offset": 320},
                "product_test_0x24": {"payload_offset": 400},
            },
        }
    }
    return package, report


class HardwareQualificationTests(unittest.TestCase):
    def test_repository_minimal_rung_is_one_noncritical_hook(self) -> None:
        config = json.loads(
            (ROOT / "hardware" / "qualification" / "advertised-name-overlay.json")
            .read_text(encoding="utf-8")
        )
        metrics = MODULE._overlay_metrics(
            config,
            {
                "apollo_main": {
                    "source_sha256": config["expected"]["component_sha256"]
                }
            },
        )
        self.assertEqual(metrics["patch_site_count"], 1)
        self.assertEqual(metrics["critical_runtime_patch_count"], 0)
        self.assertEqual(
            config["functions"], ["open_cfw_copy_advertised_name_pair_suffix"]
        )
        self.assertEqual(config["in_place_data"], [])
        self.assertEqual(config["in_place_leaves"], [])

    def test_repository_minimal_manifest_pins_the_component(self) -> None:
        pairs = (
            (
                "g2-2.2.6.10-minimal-name-hook.json",
                "advertised-name-overlay.json",
            ),
            (
                "g2-2.2.6.10-name-memcpy-hook.json",
                "name-memcpy-overlay.json",
            ),
        )
        for manifest_name, config_name in pairs:
            with self.subTest(manifest=manifest_name):
                manifest = json.loads(
                    (ROOT / "manifests" / manifest_name).read_text(
                        encoding="utf-8"
                    )
                )
                provider = manifest["component_overrides"]["apollo_main"][
                    "provider"
                ]
                expected = json.loads(
                    (ROOT / "hardware" / "qualification" / config_name).read_text(
                        encoding="utf-8"
                    )
                )["expected"]
                self.assertEqual(provider["size"], expected["component_size"])
                self.assertEqual(provider["sha256"], expected["component_sha256"])

    def test_memcpy_rung_adds_only_the_earliest_critical_hook(self) -> None:
        config = json.loads(
            (ROOT / "hardware" / "qualification" / "name-memcpy-overlay.json")
            .read_text(encoding="utf-8")
        )
        metrics = MODULE._overlay_metrics(
            config,
            {
                "apollo_main": {
                    "source_sha256": config["expected"]["component_sha256"]
                }
            },
        )
        self.assertEqual(metrics["patch_site_count"], 2)
        self.assertEqual(metrics["critical_runtime_patch_count"], 1)
        self.assertEqual(
            metrics["critical_runtime_patches"][0]["name"],
            "replace_iar_memcpy_public",
        )

    def test_stock_control_allows_only_crc_and_version_fields(self) -> None:
        stock_package, report = fixture()
        candidate = bytearray(stock_package)
        candidate[6 + 4 : 6 + 8] = b"CRC!"
        candidate[6 + 320 : 6 + 330] = b"2.2.6.0\0\0\0"
        candidate[6 + 400 : 6 + 410] = b"2.2.6.0\0\0\0"
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=bytes(candidate),
            stock_report=report,
            candidate_report=report,
            overlay_config=None,
            stage="stock-control",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertTrue(result["eligible_for_next_hardware_test"])
        self.assertTrue(result["vectors_equal"])
        self.assertEqual(result["candidate_apollo"]["reset_handler"], "0x005E4233")

    def test_stock_control_rejects_one_code_byte(self) -> None:
        stock_package, report = fixture()
        candidate = bytearray(stock_package)
        candidate[6 + 120] ^= 1
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=bytes(candidate),
            stock_report=report,
            candidate_report=report,
            overlay_config=None,
            stage="stock-control",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])
        self.assertIn("non-version/code bytes", " ".join(result["blocking_reasons"]))

    def test_minimal_hook_rejects_freertos_patch(self) -> None:
        package, report = fixture()
        config = {
            "expected": {"component_sha256": "candidate"},
            "patch_sites": [
                {
                    "name": "replace_freertos_task_start_scheduler",
                    "runtime_address": 0x454CEC,
                    "target_function": "open_cfw_freertos_task_start_scheduler",
                }
            ]
        }
        result = MODULE.qualify(
            stock_package=package,
            candidate_package=package,
            stock_report=report,
            candidate_report={
                **report,
                "apollo_main": {
                    **report["apollo_main"],
                    "source_sha256": "candidate",
                },
            },
            overlay_config=config,
            stage="minimal-hook",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])
        self.assertEqual(result["overlay"]["critical_runtime_patch_count"], 1)

    def test_rejects_overlay_metadata_from_a_different_build(self) -> None:
        package, report = fixture()
        result = MODULE.qualify(
            stock_package=package,
            candidate_package=package,
            stock_report=report,
            candidate_report={
                **report,
                "apollo_main": {
                    **report["apollo_main"],
                    "source_sha256": "candidate-build",
                },
            },
            overlay_config={
                "expected": {"component_sha256": "later-build"},
                "patch_sites": [
                    {
                        "name": "rewrite_g2_advertised_name_suffix",
                        "runtime_address": 0x46DF68,
                        "target_function": (
                            "open_cfw_copy_advertised_name_pair_suffix"
                        ),
                    }
                ],
            },
            stage="minimal-hook",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])
        self.assertFalse(result["overlay"]["metadata_bound_to_candidate"])
        self.assertIn("not hash-bound", " ".join(result["blocking_reasons"]))

    def test_full_source_is_never_a_first_stage_candidate(self) -> None:
        package, report = fixture()
        result = MODULE.qualify(
            stock_package=package,
            candidate_package=package,
            stock_report=report,
            candidate_report=report,
            overlay_config={
                "expected": {"component_sha256": "candidate"},
                "patch_sites": [],
            },
            stage="full-source",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])


if __name__ == "__main__":
    unittest.main()
