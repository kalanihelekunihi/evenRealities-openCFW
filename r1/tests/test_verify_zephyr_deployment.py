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


def load(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deployment = load("prepare_zephyr_deployment")
verification = load("verify_zephyr_deployment")


class ZephyrDeploymentReadbackTests(unittest.TestCase):
    def prepare_fixture(self, root: Path):
        bundle = root / "bundle.zip"
        backup_path = root / "backup.bin"
        uicr_path = root / "uicr.bin"
        package = root / "deployment"
        bundle.write_bytes(b"verified-bundle-fixture")
        backup = bytearray(
            (index * 13 + 5) & 0xFF
            for index in range(deployment.FLASH_LIMIT))
        for index, tag in enumerate((
                deployment.FDS_DATA_TAG,
                deployment.FDS_DATA_TAG,
                deployment.FDS_SWAP_TAG)):
            address = deployment.SETTINGS_START + \
                index * deployment.FLASH_PAGE_SIZE
            backup[address:address + 4] = \
                deployment.FDS_PAGE_MAGIC.to_bytes(4, "little")
            backup[address + 4:address + 8] = tag.to_bytes(4, "little")
        backup_path.write_bytes(bytes(backup))
        uicr = bytes(
            (index * 19 + 11) & 0xFF
            for index in range(deployment.UICR_SIZE))
        uicr_path.write_bytes(uicr)
        install = {
            0: 0x11,
            7: 0x22,
            deployment.FLASH_PAGE_SIZE * 2 + 31: 0x33,
            deployment.SETTINGS_START - 1: 0x44,
        }
        members = {"openr1-full.hex": deployment.write_ihex(install)}
        with mock.patch.object(
                deployment, "verify_bundle", return_value=(members, {})):
            deployment.prepare(bundle, backup_path, uicr_path, package)
        expected = package / deployment.EXPECTED_FLASH_ARTIFACT
        readback = root / "readback.bin"
        readback.write_bytes(expected.read_bytes())
        uicr_readback = root / "uicr-readback.bin"
        uicr_readback.write_bytes(uicr)
        return bundle, package, readback, uicr_readback, members

    def test_accepts_exact_full_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            bundle, package, readback, uicr_readback, members = self.prepare_fixture(
                Path(temporary))
            with mock.patch.object(
                    verification, "verify_bundle",
                    return_value=(members, {})):
                plan = verification.verify_deployment(
                    bundle, package, readback, uicr_readback)
            self.assertEqual(plan["schema"], 3)
            self.assertEqual(
                plan["installation"]["readback_range"],
                [0, deployment.FLASH_LIMIT])

    def test_rejects_changed_erased_gap_and_preserved_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, package, readback, uicr_readback, members = \
                self.prepare_fixture(root)
            for address in (
                1,
                deployment.SETTINGS_START + 17,
                deployment.DATA_START + 17,
            ):
                changed = bytearray(readback.read_bytes())
                changed[address] ^= 0x01
                candidate = root / f"changed-{address}.bin"
                candidate.write_bytes(changed)
                with mock.patch.object(
                        verification, "verify_bundle",
                        return_value=(members, {})):
                    with self.assertRaisesRegex(
                            ValueError, f"0x{address:08x}"):
                        verification.verify_deployment(
                            bundle, package, candidate, uicr_readback)

    def test_rejects_tampered_expected_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, package, readback, uicr_readback, members = \
                self.prepare_fixture(root)
            expected_path = package / deployment.EXPECTED_FLASH_ARTIFACT
            expected = bytearray(expected_path.read_bytes())
            expected[2] ^= 1
            expected_path.write_bytes(expected)
            with mock.patch.object(
                    verification, "verify_bundle",
                    return_value=(members, {})):
                with self.assertRaisesRegex(
                        ValueError, "page-erase model"):
                    verification.verify_deployment(
                        bundle, package, readback, uicr_readback)

    def test_rejects_tampered_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, package, readback, uicr_readback, members = \
                self.prepare_fixture(root)
            plan_path = package / verification.PLAN_ARTIFACT
            plan = json.loads(plan_path.read_text())
            plan["installation"]["mass_erase_forbidden"] = False
            plan_path.write_text(json.dumps(plan))
            with mock.patch.object(
                    verification, "verify_bundle",
                    return_value=(members, {})):
                with self.assertRaisesRegex(
                        ValueError, "plan differs"):
                    verification.verify_deployment(
                        bundle, package, readback, uicr_readback)

    def test_rejects_changed_post_install_uicr(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, package, readback, uicr_readback, members = \
                self.prepare_fixture(root)
            changed = bytearray(uicr_readback.read_bytes())
            offset = 0x304
            changed[offset] ^= 0x01
            candidate = root / "changed-uicr.bin"
            candidate.write_bytes(changed)
            with mock.patch.object(
                    verification, "verify_bundle",
                    return_value=(members, {})):
                with self.assertRaisesRegex(
                        ValueError,
                        f"0x{deployment.UICR_START + offset:08x}"):
                    verification.verify_deployment(
                        bundle, package, readback, candidate)

    def test_accepts_exact_recovery_and_rejects_changed_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, package, _, uicr_readback, _ = self.prepare_fixture(root)
            backup = package / verification.BACKUP_ARTIFACT
            verification.verify_recovery_readback(
                package, backup, uicr_readback)
            changed = bytearray(backup.read_bytes())
            address = deployment.DATA_START + 91
            changed[address] ^= 0x80
            candidate = root / "changed-recovery.bin"
            candidate.write_bytes(changed)
            with self.assertRaisesRegex(
                    ValueError, f"0x{address:08x}"):
                verification.verify_recovery_readback(
                    package, candidate, uicr_readback)

            changed_uicr = bytearray(uicr_readback.read_bytes())
            uicr_offset = 0x20C
            changed_uicr[uicr_offset] ^= 0x40
            changed_uicr_path = root / "changed-recovery-uicr.bin"
            changed_uicr_path.write_bytes(changed_uicr)
            with self.assertRaisesRegex(
                    ValueError,
                    f"0x{deployment.UICR_START + uicr_offset:08x}"):
                verification.verify_recovery_readback(
                    package, backup, changed_uicr_path)


if __name__ == "__main__":
    unittest.main()
