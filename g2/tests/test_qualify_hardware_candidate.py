from __future__ import annotations

import importlib.util
import hashlib
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import open_cfw  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "qualify_hardware_candidate", ROOT / "tools" / "qualify_hardware_candidate.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def source_payload() -> bytes:
    payload = bytearray(b"\x00" * 512)
    struct.pack_into("<II", payload, 32, 0x2007FB00, 0x005E4233)
    for offset in MODULE.RUNTIME_VERSION_FIELDS.values():
        payload[offset:offset + len(MODULE.SOURCE_RUNTIME_FIELD)] = (
            MODULE.SOURCE_RUNTIME_FIELD
        )
    struct.pack_into("<I", payload, 4, zlib.crc32(payload[8:]) & 0xFFFFFFFF)
    return bytes(payload)


def release_payload(source: bytes) -> bytes:
    payload = bytearray(source)
    for offset in MODULE.RUNTIME_VERSION_FIELDS.values():
        payload[offset:offset + len(MODULE.RELEASE_RUNTIME_FIELD)] = (
            MODULE.RELEASE_RUNTIME_FIELD
        )
    struct.pack_into("<I", payload, 4, zlib.crc32(payload[8:]) & 0xFFFFFFFF)
    return bytes(payload)


def package_for(payload: bytes, version: str) -> bytes:
    payloads = {
        "codec": b"codec",
        "ble_em9305": b"em9305",
        "touch": b"touch",
        "case": b"case",
        "apollo_bootloader": b"bootloader",
        "apollo_main": payload,
    }
    manifest = {
        "package": {
            "build_date": "2026-08-23",
            "build_time": "16:00:00",
            "version": version,
        },
        "components": [
            {
                "name": name,
                "entry_id": entry_id,
                "type_id": type_id,
                "storage_type": storage_type,
                "package_filename": filename,
            }
            for name, (entry_id, type_id, storage_type, filename) in zip(
                payloads,
                MODULE.CANONICAL_ENTRY_IDENTITIES,
            )
        ],
    }
    package, _ = open_cfw.assemble_evenota(manifest, payloads)
    return package


def apollo_payload(package: bytes) -> tuple[bytes, int]:
    offset, size = MODULE._independent_apollo_range(package)
    return package[offset:offset + size], offset


def report_for(source_package: bytes, released_package: bytes) -> dict:
    source, offset = apollo_payload(source_package)
    released, released_offset = apollo_payload(released_package)
    assert offset == released_offset and len(source) == len(released)
    return {
        "schema_version": 1,
        "source": {
            "version": MODULE.SOURCE_PACKAGE_VERSION,
            "size": len(source_package),
            "sha256": hashlib.sha256(source_package).hexdigest(),
        },
        "release": {
            "version": MODULE.RELEASE_PACKAGE_VERSION,
            "runtime_version": "2.2.6.0",
            "size": len(released_package),
            "sha256": hashlib.sha256(released_package).hexdigest(),
        },
        "apollo_main": {
            "payload_offset": offset,
            "payload_size": len(source),
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "release_sha256": hashlib.sha256(released).hexdigest(),
            "runtime_version_fields": {
                name: {
                    "payload_offset": relative,
                    "package_offset": offset + relative,
                }
                for name, relative in MODULE.RUNTIME_VERSION_FIELDS.items()
            },
        }
    }


def fixture(*, change_code: bool = False) -> tuple[bytes, dict, bytes, dict]:
    stock_source = source_payload()
    stock_source_package = package_for(stock_source, MODULE.SOURCE_PACKAGE_VERSION)
    stock_release_package = package_for(
        release_payload(stock_source), MODULE.RELEASE_PACKAGE_VERSION
    )
    stock_report = report_for(stock_source_package, stock_release_package)
    candidate_source = bytearray(stock_source)
    if change_code:
        candidate_source[300] ^= 1
        struct.pack_into(
            "<I", candidate_source, 4, zlib.crc32(candidate_source[8:]) & 0xFFFFFFFF
        )
    candidate_source_package = package_for(
        bytes(candidate_source), MODULE.SOURCE_PACKAGE_VERSION
    )
    candidate_release_package = package_for(
        release_payload(bytes(candidate_source)), MODULE.RELEASE_PACKAGE_VERSION
    )
    candidate_report = report_for(candidate_source_package, candidate_release_package)
    return stock_source_package, stock_report, candidate_release_package, candidate_report


class HardwareQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime_fields = mock.patch.object(
            MODULE,
            "RUNTIME_VERSION_FIELDS",
            {"settings": 320, "product_test_0x24": 400},
        )
        self.runtime_fields.start()

    def tearDown(self) -> None:
        self.runtime_fields.stop()

    def test_repository_minimal_rung_is_one_noncritical_hook(self) -> None:
        config = json.loads(
            (ROOT / "hardware" / "qualification" / "advertised-name-overlay.json")
            .read_text(encoding="utf-8")
        )
        metrics = MODULE._overlay_metrics(
            config,
            config["expected"]["component_sha256"],
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
            config["expected"]["component_sha256"],
        )
        self.assertEqual(metrics["patch_site_count"], 2)
        self.assertEqual(metrics["critical_runtime_patch_count"], 1)
        self.assertEqual(
            metrics["critical_runtime_patches"][0]["name"],
            "replace_iar_memcpy_public",
        )

    def test_stock_control_allows_only_crc_and_version_fields(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture()
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=candidate,
            stock_report=stock_report,
            candidate_report=candidate_report,
            overlay_config=None,
            stage="stock-control",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertTrue(result["eligible_for_next_hardware_test"])
        self.assertTrue(result["vectors_equal"])
        self.assertEqual(result["candidate_apollo"]["reset_handler"], "0x005E4233")

    def test_stock_control_rejects_one_code_byte(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture(
            change_code=True
        )
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=candidate,
            stock_report=stock_report,
            candidate_report=candidate_report,
            overlay_config=None,
            stage="stock-control",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])
        self.assertIn("non-version/code bytes", " ".join(result["blocking_reasons"]))

    def test_minimal_hook_rejects_freertos_patch(self) -> None:
        stock_package, stock_report, package, report = fixture(change_code=True)
        candidate_source_sha = report["apollo_main"]["source_sha256"]
        config = {
            "expected": {"component_sha256": candidate_source_sha},
            "patch_sites": [
                {
                    "name": "replace_freertos_task_start_scheduler",
                    "runtime_address": 0x454CEC,
                    "target_function": "open_cfw_freertos_task_start_scheduler",
                }
            ]
        }
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=package,
            stock_report=stock_report,
            candidate_report=report,
            overlay_config=config,
            stage="minimal-hook",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])
        self.assertEqual(result["overlay"]["critical_runtime_patch_count"], 1)

    def test_rejects_overlay_metadata_from_a_different_build(self) -> None:
        stock_package, stock_report, package, report = fixture(change_code=True)
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=package,
            stock_report=stock_report,
            candidate_report=report,
            overlay_config={
                "expected": {"component_sha256": "0" * 64},
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

    def test_rejects_forged_whole_package_identity(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture()
        candidate_report = json.loads(json.dumps(candidate_report))
        candidate_report["release"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            MODULE.QualificationError,
            "does not match exactly one release-report role",
        ):
            MODULE.qualify(
                stock_package=stock_package,
                candidate_package=candidate,
                stock_report=stock_report,
                candidate_report=candidate_report,
                overlay_config=None,
                stage="stock-control",
                max_patch_sites=8,
                max_critical_runtime_patches=0,
            )

    def test_rejects_forged_apollo_range(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture()
        candidate_report = json.loads(json.dumps(candidate_report))
        candidate_report["apollo_main"]["payload_offset"] += 4
        with self.assertRaisesRegex(
            MODULE.QualificationError,
            "range differs from independently parsed package",
        ):
            MODULE.qualify(
                stock_package=stock_package,
                candidate_package=candidate,
                stock_report=stock_report,
                candidate_report=candidate_report,
                overlay_config=None,
                stage="stock-control",
                max_patch_sites=8,
                max_critical_runtime_patches=0,
            )

    def test_rejects_forged_source_payload_hash_for_release(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture()
        candidate_report = json.loads(json.dumps(candidate_report))
        candidate_report["apollo_main"]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            MODULE.QualificationError,
            "source Apollo hash is not reconstructibly bound",
        ):
            MODULE.qualify(
                stock_package=stock_package,
                candidate_package=candidate,
                stock_report=stock_report,
                candidate_report=candidate_report,
                overlay_config={
                    "expected": {"component_sha256": "0" * 64},
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

    def test_rejects_noncanonical_or_duplicate_entry_identity(self) -> None:
        package = bytearray(
            package_for(source_payload(), MODULE.SOURCE_PACKAGE_VERSION)
        )
        struct.pack_into("<I", package, 8, 1)
        with self.assertRaisesRegex(
            MODULE.QualificationError, "canonical six entries"
        ):
            MODULE._independent_apollo_range(bytes(package))

        package = bytearray(
            package_for(source_payload(), MODULE.SOURCE_PACKAGE_VERSION)
        )
        second_toc = MODULE.EVENOTA_TOC_OFFSET + MODULE.EVENOTA_TOC_ENTRY_SIZE
        struct.pack_into("<I", package, second_toc, 1)
        with self.assertRaisesRegex(MODULE.QualificationError, "metadata"):
            MODULE._independent_apollo_range(bytes(package))

    def test_rejects_outer_component_crc_corruption(self) -> None:
        package = bytearray(
            package_for(source_payload(), MODULE.SOURCE_PACKAGE_VERSION)
        )
        package[-1] ^= 1
        with self.assertRaisesRegex(MODULE.QualificationError, "CRC-32C"):
            MODULE._independent_apollo_range(bytes(package))

    def test_rejects_runtime_field_range_and_package_offset_forgery(self) -> None:
        stock_package, stock_report, candidate, candidate_report = fixture()
        for key, value in (("payload_offset", -1), ("package_offset", 0)):
            with self.subTest(key=key):
                forged = json.loads(json.dumps(candidate_report))
                forged["apollo_main"]["runtime_version_fields"]["settings"][
                    key
                ] = value
                with self.assertRaisesRegex(
                    MODULE.QualificationError, "range or identity changed"
                ):
                    MODULE.qualify(
                        stock_package=stock_package,
                        candidate_package=candidate,
                        stock_report=stock_report,
                        candidate_report=forged,
                        overlay_config=None,
                        stage="stock-control",
                        max_patch_sites=8,
                        max_critical_runtime_patches=0,
                    )

    def test_rejects_stale_source_release_role_confusion(self) -> None:
        stock_package, stock_report, _, _ = fixture()
        with self.assertRaisesRegex(
            MODULE.QualificationError,
            "source stock package and release candidate",
        ):
            MODULE.qualify(
                stock_package=stock_package,
                candidate_package=stock_package,
                stock_report=stock_report,
                candidate_report=stock_report,
                overlay_config=None,
                stage="stock-control",
                max_patch_sites=8,
                max_critical_runtime_patches=0,
            )

    def test_rejects_nested_apollo_crc_even_with_valid_outer_crc(self) -> None:
        broken_source = bytearray(source_payload())
        struct.pack_into("<I", broken_source, 4, 0)
        source_package = package_for(
            bytes(broken_source), MODULE.SOURCE_PACKAGE_VERSION
        )
        released_package = package_for(
            release_payload(bytes(broken_source)), MODULE.RELEASE_PACKAGE_VERSION
        )
        report = report_for(source_package, released_package)
        with self.assertRaisesRegex(MODULE.QualificationError, "nested CRC-32"):
            MODULE.qualify(
                stock_package=source_package,
                candidate_package=released_package,
                stock_report=report,
                candidate_report=report,
                overlay_config=None,
                stage="stock-control",
                max_patch_sites=8,
                max_critical_runtime_patches=0,
            )

    def test_atomic_output_replaces_symlink_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-qualification-") as temporary:
            root = Path(temporary)
            protected = root / "protected.json"
            output = root / "qualification.json"
            protected.write_text("preserve", encoding="utf-8")
            output.symlink_to(protected.name)
            MODULE._atomic_write(output, b"{}\n")
            self.assertEqual(protected.read_text(encoding="utf-8"), "preserve")
            self.assertFalse(output.is_symlink())
            self.assertEqual(output.read_bytes(), b"{}\n")

    def test_full_source_is_never_a_first_stage_candidate(self) -> None:
        stock_package, stock_report, package, report = fixture(change_code=True)
        result = MODULE.qualify(
            stock_package=stock_package,
            candidate_package=package,
            stock_report=stock_report,
            candidate_report=report,
            overlay_config={
                "expected": {
                    "component_sha256": report["apollo_main"]["source_sha256"]
                },
                "patch_sites": [],
            },
            stage="full-source",
            max_patch_sites=8,
            max_critical_runtime_patches=0,
        )
        self.assertFalse(result["eligible_for_next_hardware_test"])


if __name__ == "__main__":
    unittest.main()
