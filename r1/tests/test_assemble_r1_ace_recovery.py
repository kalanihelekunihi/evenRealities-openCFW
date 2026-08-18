from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from contextlib import ExitStack
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "assemble_r1_ace_recovery.py"
SPEC = importlib.util.spec_from_file_location("assemble_r1_ace_recovery", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)
from package_zephyr_bundle import write_ihex


class R1AceRecoveryAssemblyTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> dict[str, Path]:
        softdevice = root / "s140.hex"
        softdevice.write_bytes(write_ihex({
            0: 0x00,
            1: 0x20,
            recovery.SOFTDEVICE_LIMIT - 1: 0x7A,
        }))

        application_body = bytes(
            (index * 13 + 9) & 0xFF for index in range(0x2200))
        application = root / "application.zip"
        with zipfile.ZipFile(application, "w") as archive:
            archive.writestr("application.bin", application_body)
            archive.writestr("application.dat", b"test-init")
            archive.writestr("manifest.json", b"{}")

        bootloader_body = bytearray(
            (index * 7 + 3) & 0xFF
            for index in range(
                recovery.BOOTLOADER_LIMIT - recovery.BOOTLOADER_START))
        bootloader_body[0x3D98:0x3D9A] = b"\x00\xbf"
        bootloader = root / "bootloader.zip"
        with zipfile.ZipFile(bootloader, "w") as archive:
            archive.writestr("bootloader.bin", bootloader_body)
            archive.writestr("bootloader.dat", b"test-init")
            archive.writestr("manifest.json", b"{}")

        pages = root / "pages"
        pages.mkdir()
        live = bytearray(b"\xff" * recovery.FLASH_SIZE)
        live[
            recovery.APPLICATION_START:
            recovery.APPLICATION_START + len(application_body)
        ] = application_body
        live[
            recovery.BOOTLOADER_START:recovery.BOOTLOADER_LIMIT
        ] = bootloader_body
        settings = bytearray(b"\xff" * recovery.PAGE_SIZE)
        settings[4:0x5C] = bytes(range(0x58))
        struct.pack_into("<I", settings, 0, zlib.crc32(settings[4:0x5C]))
        live[
            recovery.SETTINGS_BACKUP_START:recovery.SETTINGS_PRIMARY_START
        ] = settings
        for address in range(
                recovery.APPLICATION_START,
                recovery.SETTINGS_PRIMARY_START,
                recovery.PAGE_SIZE):
            (pages / f"{address:05x}.bin").write_bytes(
                live[address:address + recovery.PAGE_SIZE])

        uicr = bytearray(b"\xff" * recovery.UICR_SIZE)
        struct.pack_into("<II", uicr, 0x14, 0xF8000, 0xFE000)
        uicr_path = root / "uicr.bin"
        uicr_path.write_bytes(uicr)
        settings_source = root / "nrf_dfu_settings.c"
        settings_source.write_bytes(b"synthetic pinned settings source\n")
        prior_backup = root / "prior-backup.bin"
        prior_backup.write_bytes(settings)
        prior_primary = root / "prior-primary.partial.bin"
        prior_primary.write_bytes(settings[:0xA7C])
        return {
            "softdevice": softdevice,
            "application": application,
            "bootloader": bootloader,
            "pages": pages,
            "uicr": uicr_path,
            "settings_source": settings_source,
            "prior_backup": prior_backup,
            "prior_primary": prior_primary,
        }

    def patched_pins(self, fixture: dict[str, Path]) -> ExitStack:
        with zipfile.ZipFile(fixture["application"]) as archive:
            application_body = archive.read("application.bin")
        with zipfile.ZipFile(fixture["bootloader"]) as archive:
            bootloader_body = archive.read("bootloader.bin")
        stack = ExitStack()
        for name, value in (
            ("S140_HEX_SHA256", recovery.digest(
                fixture["softdevice"].read_bytes())),
            ("APPLICATION_ARCHIVE_SHA256", recovery.digest(
                fixture["application"].read_bytes())),
            ("APPLICATION_IMAGE_SHA256", recovery.digest(application_body)),
            ("BOOTLOADER_ARCHIVE_SHA256", recovery.digest(
                fixture["bootloader"].read_bytes())),
            ("BOOTLOADER_IMAGE_SHA256", recovery.digest(bootloader_body)),
            ("OWNER_KEY_SHA256", recovery.digest(
                bootloader_body[0x5868:0x5868 + 64])),
            ("SETTINGS_SOURCE_SHA256", recovery.digest(
                fixture["settings_source"].read_bytes())),
        ):
            stack.enter_context(mock.patch.object(recovery, name, value))
        return stack

    def test_assembles_mixed_provenance_recovery_basis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = self.make_fixture(root)
            output = root / "recovery.bin"
            evidence_path = root / "evidence.json"
            with self.patched_pins(fixture):
                evidence = recovery.assemble(
                    fixture["softdevice"], fixture["application"],
                    fixture["bootloader"], fixture["pages"], fixture["uicr"],
                    fixture["settings_source"], fixture["prior_primary"],
                    fixture["prior_backup"],
                    output, evidence_path)

            self.assertEqual(len(output.read_bytes()), recovery.FLASH_SIZE)
            self.assertEqual(evidence["output"]["sha256"], recovery.digest(
                output.read_bytes()))
            self.assertEqual(
                evidence["provenance"][0]["kind"],
                "pinned-official-reconstruction")
            self.assertEqual(
                evidence["provenance"][1]["kind"],
                "source-proven-mbr-config")
            self.assertEqual(
                evidence["provenance"][3]["kind"],
                "live-ace-page-readback")
            self.assertEqual(
                evidence["provenance"][3]["pages"],
                (recovery.SETTINGS_PRIMARY_START - recovery.APPLICATION_START) //
                recovery.PAGE_SIZE)
            self.assertEqual(
                evidence["provenance"][4]["kind"],
                "source-proven-settings-mirror")
            self.assertEqual(
                output.read_bytes()[recovery.SETTINGS_PRIMARY_START:],
                output.read_bytes()[
                    recovery.SETTINGS_BACKUP_START:
                    recovery.SETTINGS_PRIMARY_START])
            self.assertTrue(
                evidence["official_matches"]["application"]["byte_exact"])
            self.assertEqual(
                json.loads(evidence_path.read_text())["uicr"]["bytes"],
                recovery.UICR_SIZE)

    def test_rejects_missing_live_page_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = self.make_fixture(root)
            missing = fixture["pages"] / "27000.bin"
            missing.unlink()
            output = root / "recovery.bin"
            evidence_path = root / "evidence.json"
            with self.patched_pins(fixture):
                with self.assertRaisesRegex(ValueError, "missing live page"):
                    recovery.assemble(
                        fixture["softdevice"], fixture["application"],
                        fixture["bootloader"], fixture["pages"],
                        fixture["uicr"],
                        fixture["settings_source"], fixture["prior_primary"],
                        fixture["prior_backup"],
                        output, evidence_path)
            self.assertFalse(output.exists())
            self.assertFalse(evidence_path.exists())


if __name__ == "__main__":
    unittest.main()
