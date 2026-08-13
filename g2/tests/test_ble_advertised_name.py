from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "ble_advertised_name.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "ble_advertised_name_host.c"
CONFIG = COMPONENT_ROOT / "overlay.json"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
PREAMBLE_BYTES = 32
PATCH_SITE = 0x0046DDA8
STOCK_MEMCPY = 0x00439BE4
PATCH_BYTES = bytes.fromhex("cbf71cff")


def serial_record(serial: bytes, *, terminator: int = 0) -> bytes:
    if len(serial) != 14:
        raise ValueError("test serial must be 14 bytes")
    return b"\x02" + serial + bytes([terminator])


class G2AdvertisedNamePatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "ble_advertised_name.dylib"
            if sys.platform == "darwin"
            else "ble_advertised_name.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)

        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_adv_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.set_serial_record = cls.loaded.open_cfw_test_adv_set_serial_record
        cls.set_serial_record.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.set_serial_record.restype = None
        cls.execute = cls.loaded.open_cfw_test_adv_execute
        cls.execute.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
        ]
        cls.execute.restype = None
        cls.recorded = (ctypes.c_ubyte * 32).in_dll(
            cls.loaded,
            "open_cfw_test_adv_recorded",
        )
        cls.recorded_length = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_adv_recorded_length",
        )
        cls.call_count = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_adv_call_count",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.keepalive: list[ctypes.Array[ctypes.c_ubyte]] = []

    def buffer(self, body: bytes) -> ctypes.Array[ctypes.c_ubyte]:
        value = (ctypes.c_ubyte * len(body))(*body)
        self.keepalive.append(value)
        return value

    def install_serial(self, body: bytes) -> None:
        self.set_serial_record(self.buffer(body))

    def run_hook(self, stock_suffix: bytes) -> bytes:
        self.execute(self.buffer(stock_suffix), len(stock_suffix))
        self.assertEqual(self.call_count.value, 1)
        self.assertEqual(self.recorded_length.value, len(stock_suffix))
        return bytes(self.recorded[: len(stock_suffix)])

    def test_cold_start_final_copy_uses_pair_serial_suffix(self) -> None:
        self.install_serial(serial_record(b"S211GCBC300403"))

        self.assertEqual(self.run_hook(b"1CEF4C"), b"300403")

    def test_both_temples_converge_on_the_same_pair_suffix(self) -> None:
        self.install_serial(serial_record(b"S211GCBC300403"))
        self.assertEqual(self.run_hook(b"1CEF4C"), b"300403")

        self.reset()
        self.keepalive = []
        self.install_serial(serial_record(b"S211GCBC300403"))
        self.assertEqual(self.run_hook(b"9C97C0"), b"300403")

    def test_missing_or_invalid_serial_fails_open_to_stock_mac_suffix(self) -> None:
        self.assertEqual(self.run_hook(b"1CEF4C"), b"1CEF4C")

        for record in (
            serial_record(b"S211GCBC30-403"),
            serial_record(b"S211GCBC300403", terminator=ord("X")),
        ):
            with self.subTest(record=record):
                self.reset()
                self.keepalive = []
                self.install_serial(record)
                self.assertEqual(self.run_hook(b"1CEF4C"), b"1CEF4C")

    def test_non_suffix_copy_length_remains_stock(self) -> None:
        self.install_serial(serial_record(b"S211GCBC300403"))

        self.assertEqual(self.run_hook(b"NOT-A-SUFFIX"), b"NOT-A-SUFFIX")

    def test_lowercase_alphanumeric_serial_is_supported(self) -> None:
        self.install_serial(serial_record(b"s211gcbcabcdef"))

        self.assertEqual(self.run_hook(b"1CEF4C"), b"abcdef")

    def test_overlay_registration_and_final_copy_callsite_pin_are_exact(self) -> None:
        config = json.loads(CONFIG.read_text())
        leaf = next(
            item
            for item in config["relocated_leaves"]
            if item["function"]
            == "open_cfw_copy_advertised_name_pair_suffix"
        )
        source = leaf["source"]
        self.assertEqual(source["license"], "GPL-3.0-only")
        self.assertEqual(
            source["sha256"],
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        )
        self.assertEqual(leaf["relocations"], [])
        self.assertIn(
            "open_cfw_copy_advertised_name_pair_suffix",
            config["functions"],
        )
        patch = next(
            item
            for item in config["patch_sites"]
            if item["name"] == "rewrite_g2_advertised_name_suffix"
        )
        self.assertEqual(patch["runtime_address"], PATCH_SITE)
        self.assertEqual(bytes.fromhex(patch["expected_hex"]), PATCH_BYTES)
        self.assertEqual(patch["branch"], "bl")
        self.assertEqual(
            patch["target_function"],
            "open_cfw_copy_advertised_name_pair_suffix",
        )
        offset = PREAMBLE_BYTES + PATCH_SITE - APPLICATION_BASE
        self.assertEqual(OFFICIAL.read_bytes()[offset : offset + 4], PATCH_BYTES)

    def test_source_calls_public_memcpy_entry_and_uses_serial_record(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("0x00439BE5U", source)
        self.assertIn("0x2000383CU", source)
        config = json.loads(CONFIG.read_text())
        replacements = [
            item
            for item in config["patch_sites"]
            if item["runtime_address"] == STOCK_MEMCPY
        ]
        self.assertEqual(len(replacements), 1)
        self.assertEqual(
            replacements[0]["target_function"],
            "open_cfw_iar_memcpy_void",
        )


if __name__ == "__main__":
    unittest.main()
