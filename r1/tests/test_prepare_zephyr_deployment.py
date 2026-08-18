from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "prepare_zephyr_deployment.py"
SPEC = importlib.util.spec_from_file_location("prepare_zephyr_deployment", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
deployment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deployment)


class ZephyrDeploymentPreparationTests(unittest.TestCase):
    @staticmethod
    def retail_fds_backup(seed: bytes | bytearray) -> bytes:
        backup = bytearray(seed)
        tags = (
            deployment.FDS_DATA_TAG,
            deployment.FDS_DATA_TAG,
            deployment.FDS_SWAP_TAG,
        )
        for index, tag in enumerate(tags):
            address = deployment.SETTINGS_START + \
                index * deployment.FLASH_PAGE_SIZE
            backup[address:address + 4] = \
                deployment.FDS_PAGE_MAGIC.to_bytes(4, "little")
            backup[address + 4:address + 8] = tag.to_bytes(4, "little")
        return bytes(backup)

    @staticmethod
    def backup_provenance(backup: bytes, uicr: bytes) -> dict[str, object]:
        pages = []
        for address in range(0x27000, 0xFF000,
                             deployment.FLASH_PAGE_SIZE):
            pages.append({
                "range": [address, address + deployment.FLASH_PAGE_SIZE],
                "sha256": deployment.digest(
                    backup[address:address + deployment.FLASH_PAGE_SIZE]),
            })
        return {
            "schema": 1,
            "format": "r1-ace-recovery-basis",
            "provenance": [
                {
                    "range": [0, 0xFF8],
                    "kind": "pinned-official-reconstruction",
                },
                {
                    "range": [0xFF8, 0x1000],
                    "kind": "source-proven-mbr-config",
                    "sha256": deployment.digest(backup[0xFF8:0x1000]),
                },
                {
                    "range": [0x1000, 0x27000],
                    "kind": "pinned-official-reconstruction",
                },
                {
                    "range": [0x27000, 0xFF000],
                    "kind": "live-ace-page-readback",
                    "pages": len(pages),
                    "page_bytes": deployment.FLASH_PAGE_SIZE,
                },
                {
                    "range": [0xFF000, deployment.FLASH_LIMIT],
                    "kind": "source-proven-settings-mirror",
                    "live_backup_range": [0xFE000, 0xFF000],
                    "live_backup_sha256": deployment.digest(
                        backup[0xFE000:0xFF000]),
                },
            ],
            "protected_extent_sha256": deployment.digest(backup[:0x27000]),
            "official_matches": {
                "application": {"byte_exact": True},
                "bootloader": {"byte_exact": True},
            },
            "uicr": {
                "range": [deployment.UICR_START, deployment.UICR_LIMIT],
                "bytes": deployment.UICR_SIZE,
                "sha256": deployment.digest(uicr),
            },
            "live_pages": pages,
            "output": {
                "bytes": deployment.FLASH_LIMIT,
                "sha256": deployment.digest(backup),
            },
        }

    def test_ranges_and_full_flash_preservation_plan(self) -> None:
        install = {
            0: 0x11,
            1: 0x22,
            4: 0x33,
            deployment.SETTINGS_START - 1: 0x44,
        }
        backup = self.retail_fds_backup(bytes(
            (index * 29 + 7) & 0xFF
            for index in range(deployment.FLASH_LIMIT)
        ))
        self.assertEqual(
            deployment.contiguous_ranges(install),
            [[0, 2], [4, 5],
             [deployment.SETTINGS_START - 1, deployment.SETTINGS_START]],
        )
        plan = deployment.build_deployment_plan(
            "ab" * 32, install, backup,
            bytes([0xA5]) * deployment.UICR_SIZE,
            b":recovery\n", b":uicr-recovery\n",
            deployment.build_expected_internal_flash(install, backup))
        self.assertEqual(plan["schema"], 3)
        self.assertEqual(plan["bundle_sha256"], "ab" * 32)
        self.assertEqual(
            plan["installation"]["write_ranges"],
            deployment.contiguous_ranges(install),
        )
        self.assertTrue(plan["installation"]["mass_erase_forbidden"])
        self.assertTrue(plan["installation"]["readback_required"])
        self.assertEqual(
            plan["installation"]["erase_ranges"],
            [[0, deployment.DATA_START],
             [deployment.DATA_LIMIT, deployment.FLASH_LIMIT]],
        )
        self.assertTrue(
            plan["installation"][
                "unaddressed_install_bytes_must_be_erased"])
        self.assertEqual(
            plan["installation"]["expected_readback_artifact"],
            deployment.EXPECTED_FLASH_ARTIFACT)
        self.assertEqual(
            plan["backup"]["sha256"], deployment.digest(backup))
        self.assertEqual(len(plan["product_partitions"]), 7)
        self.assertEqual(
            plan["product_partitions"][0]["range"],
            [deployment.DATA_START, deployment.DATA_START + 0x2000],
        )
        self.assertFalse(plan["recovery"]["includes_uicr"])
        self.assertFalse(plan["recovery"]["on_device_rollback_available"])
        self.assertEqual(
            plan["uicr_backup"]["range"],
            [deployment.UICR_START, deployment.UICR_LIMIT])
        self.assertTrue(
            plan["uicr_backup"]["post_install_readback_required"])
        self.assertTrue(plan["recovery"]["uicr_readback_required"])

        expected = deployment.build_expected_internal_flash(install, backup)
        self.assertEqual(len(expected), deployment.FLASH_LIMIT)
        self.assertEqual(expected[0], 0x11)
        self.assertEqual(expected[1], 0x22)
        self.assertEqual(expected[2], 0xFF)
        self.assertEqual(expected[4], 0x33)
        self.assertEqual(
            expected[deployment.FLASH_PAGE_SIZE],
            0xFF)
        self.assertEqual(expected[deployment.SETTINGS_START], 0xFF)
        self.assertEqual(expected[deployment.DATA_START],
                         backup[deployment.DATA_START])
        self.assertEqual(expected[deployment.DATA_LIMIT], 0xFF)
        self.assertEqual(
            plan["settings_transition"]["layout"],
            "retail-nordic-fds")
        self.assertTrue(
            plan["settings_transition"]["owner_repairing_required"])
        self.assertFalse(
            plan["settings_transition"]["retail_credentials_imported"])
        self.assertTrue(
            plan["installation"]["reset_held_until_readback_verified"])
        self.assertEqual(
            plan["expected_readback"]["sha256"],
            deployment.digest(expected))

    def test_rejects_incomplete_backup_and_preserved_range_overlap(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly"):
            deployment.validate_deployment_inputs({0: 0}, b"short")
        backup = self.retail_fds_backup(bytes(deployment.FLASH_LIMIT))
        with self.assertRaisesRegex(ValueError, "overlaps"):
            deployment.validate_deployment_inputs(
                {deployment.SETTINGS_START: 0}, backup)
        with self.assertRaisesRegex(ValueError, "empty"):
            deployment.validate_deployment_inputs({}, backup)
        with self.assertRaisesRegex(ValueError, "UICR backup must be exactly"):
            deployment.build_deployment_plan(
                "ab" * 32, {0: 0x11}, backup, b"short",
                b":recovery\n", b":uicr-recovery\n",
                b"expected")

    def test_classifies_only_exact_retail_fds_or_erased_settings(self) -> None:
        retail = self.retail_fds_backup(
            bytes([0xA5]) * deployment.FLASH_LIMIT)
        classification = deployment.classify_first_install_settings(retail)
        self.assertEqual(classification["layout"], "retail-nordic-fds")
        self.assertEqual(
            [page["kind"] for page in classification["pages"]],
            ["fds-data", "fds-data", "fds-swap"])

        erased = bytearray(retail)
        erased[deployment.SETTINGS_START:deployment.DATA_START] = \
            b"\xff" * (deployment.DATA_START - deployment.SETTINGS_START)
        classification = deployment.classify_first_install_settings(
            bytes(erased))
        self.assertEqual(classification["layout"], "erased")
        self.assertFalse(classification["owner_repairing_required"])

        unknown = bytearray(retail)
        unknown[deployment.SETTINGS_START] ^= 1
        with self.assertRaisesRegex(ValueError, "unknown or torn"):
            deployment.classify_first_install_settings(bytes(unknown))

        interrupted = bytearray(retail)
        interrupted[deployment.SETTINGS_START:
                    deployment.SETTINGS_START + deployment.FLASH_PAGE_SIZE] = \
            b"\xff" * deployment.FLASH_PAGE_SIZE
        with self.assertRaisesRegex(ValueError, "interrupted retail FDS"):
            deployment.classify_first_install_settings(bytes(interrupted))

    def test_validates_and_records_mixed_backup_provenance(self) -> None:
        backup_buffer = bytearray(
            (index * 11 + 5) & 0xFF
            for index in range(deployment.FLASH_LIMIT))
        backup_buffer[0xFF000:deployment.FLASH_LIMIT] = \
            backup_buffer[0xFE000:0xFF000]
        backup = self.retail_fds_backup(backup_buffer)
        uicr = bytes([0xA5]) * deployment.UICR_SIZE
        provenance = self.backup_provenance(backup, uicr)
        deployment.validate_backup_provenance(provenance, backup, uicr)
        plan = deployment.build_deployment_plan(
            "ab" * 32, {0: 0x11}, backup, uicr,
            b":recovery\n", b":uicr-recovery\n",
            deployment.build_expected_internal_flash({0: 0x11}, backup),
            provenance)
        self.assertEqual(
            plan["backup"]["protected_extent_source"],
            "pinned-official-reconstruction")
        self.assertEqual(
            plan["backup"]["live_readback_range"],
            [0x27000, deployment.FLASH_LIMIT])
        provenance["live_pages"][0]["sha256"] = "00" * 32
        with self.assertRaisesRegex(
                ValueError, "live ACE page provenance differs"):
            deployment.validate_backup_provenance(provenance, backup, uicr)

    def test_rejects_output_path_that_is_not_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle.zip"
            backup = root / "backup.bin"
            uicr = root / "uicr.bin"
            output = root / "output"
            bundle.write_bytes(b"bundle")
            backup.write_bytes(self.retail_fds_backup(
                bytes(deployment.FLASH_LIMIT)))
            uicr.write_bytes(bytes(deployment.UICR_SIZE))
            output.write_bytes(b"occupied")
            members = {"openr1-full.hex": deployment.write_ihex({0: 0x11})}
            with mock.patch.object(
                    deployment, "verify_bundle", return_value=(members, {})):
                with self.assertRaisesRegex(ValueError, "not a directory"):
                    deployment.prepare(bundle, backup, uicr, output)

    def test_prepare_emits_exact_expected_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle.zip"
            backup = root / "backup.bin"
            uicr = root / "uicr.bin"
            output = root / "output"
            bundle.write_bytes(b"bundle")
            original = self.retail_fds_backup(bytes(
                (index * 17 + 3) & 0xFF
                for index in range(deployment.FLASH_LIMIT))
            )
            backup.write_bytes(original)
            uicr_bytes = bytes(
                (index * 7 + 1) & 0xFF
                for index in range(deployment.UICR_SIZE))
            uicr.write_bytes(uicr_bytes)
            install = {
                0: 0x11,
                deployment.FLASH_PAGE_SIZE + 9: 0x22,
            }
            members = {"openr1-full.hex": deployment.write_ihex(install)}
            with mock.patch.object(
                    deployment, "verify_bundle", return_value=(members, {})):
                plan_path = deployment.prepare(
                    bundle, backup, uicr, output)
            plan = json.loads(plan_path.read_text())
            expected = (
                output / deployment.EXPECTED_FLASH_ARTIFACT).read_bytes()
            self.assertEqual(
                expected,
                deployment.build_expected_internal_flash(install, original))
            self.assertEqual(
                plan["expected_readback"]["sha256"],
                deployment.digest(expected))
            self.assertEqual(
                (output / deployment.UICR_BACKUP_ARTIFACT).read_bytes(),
                uicr_bytes)
            self.assertEqual(
                (output / deployment.UICR_RECOVERY_ARTIFACT).read_bytes(),
                deployment.write_ihex({
                    deployment.UICR_START + offset: value
                    for offset, value in enumerate(uicr_bytes)
                }))


if __name__ == "__main__":
    unittest.main()
