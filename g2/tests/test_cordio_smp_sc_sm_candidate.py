#!/usr/bin/env python3
"""Host behavior and source-data tests for Cordio SC role state machines."""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/cordio_smp_sc_sm_host.c"
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_sc_sm.c"
SOURCE_SIZE = 16284
SOURCE_SHA256 = "6bc75e8320b1ceabff762f64ba655b12f5a18c8539a5258a5c8d61f08d2a8739"
DISPATCH_SIZE = 1495
DISPATCH_SHA256 = "9438c7c72904056d2d0f6e9a4ce322cb1e52198738aef88558b35d5281bda801"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CordioSmpScSmCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "libcordio_smp_sc_sm.dylib"
        subprocess.run(
            [
                "/usr/bin/clang",
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-dynamiclib",
                str(FIXTURE),
                "-o",
                str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_smpi_sc_state_string.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_cordio_smpi_sc_state_string.restype = ctypes.c_char_p
        cls.lib.open_cfw_cordio_smpr_sc_state_string.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_cordio_smpr_sc_state_string.restype = ctypes.c_char_p
        cls.lib.open_cfw_smp_sc_sm_host_master.restype = ctypes.c_size_t
        cls.lib.open_cfw_smp_sc_sm_host_slave.restype = ctypes.c_size_t
        cls.lib.open_cfw_smp_sc_sm_host_init_calls.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_smp_sc_sm_host_reset()

    def test_source_and_compiled_dispatch_are_pinned(self) -> None:
        source = SOURCE.read_bytes()
        self.assertEqual((len(source), sha256(source)), (SOURCE_SIZE, SOURCE_SHA256))
        array_type = ctypes.c_uint8 * DISPATCH_SIZE
        dispatch = bytes(array_type.in_dll(self.lib, "open_cfw_cordio_smp_sc_dispatch"))
        self.assertEqual(sha256(dispatch), DISPATCH_SHA256)

    def test_dispatch_matches_all_authenticated_stock_tables(self) -> None:
        path = ROOT / "tools/analyze_g2_cordio_smp_sc_sm.py"
        spec = importlib.util.spec_from_file_location("cordio_smp_sc_sm_audit", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        blob = module.IMAGE.read_bytes()
        expected = bytearray()
        import struct

        for config in module.ROLES.values():
            interface = config["interface"]
            state_root, action_root, common_root = struct.unpack(
                "<III", module.image_slice(blob, interface, interface + 12)
            )
            expected += module.image_slice(blob, interface, interface + 12)
            expected += module.image_slice(
                blob, action_root, action_root + config["action_count"] * 4
            )
            pointers = module.image_slice(
                blob, state_root, state_root + config["state_count"] * 4
            )
            expected += pointers
            expected += module.read_state_table(blob, common_root)
            for address in struct.unpack(f"<{config['state_count']}I", pointers):
                expected += module.read_state_table(blob, address)
        array_type = ctypes.c_uint8 * DISPATCH_SIZE
        observed = bytes(array_type.in_dll(self.lib, "open_cfw_cordio_smp_sc_dispatch"))
        self.assertEqual(observed, bytes(expected))

    def test_initializers_bind_both_interfaces_and_run_common_init(self) -> None:
        self.lib.open_cfw_cordio_smpi_sc_initialize()
        self.assertEqual(self.lib.open_cfw_smp_sc_sm_host_master(), 0x0078C320)
        self.assertEqual(self.lib.open_cfw_smp_sc_sm_host_slave(), 0)
        self.lib.open_cfw_cordio_smpr_sc_initialize()
        self.assertEqual(self.lib.open_cfw_smp_sc_sm_host_slave(), 0x0078C470)
        self.assertEqual(self.lib.open_cfw_smp_sc_sm_host_init_calls(), 2)

    def test_state_name_ranges_and_unknown_fallbacks(self) -> None:
        self.assertEqual(self.lib.open_cfw_cordio_smpi_sc_state_string(0), b"I_IDLE")
        self.assertEqual(self.lib.open_cfw_cordio_smpi_sc_state_string(37), b"I_RSP_TO")
        self.assertEqual(self.lib.open_cfw_cordio_smpi_sc_state_string(38), b"I_Unknown")
        self.assertEqual(self.lib.open_cfw_cordio_smpi_sc_state_string(255), b"I_Unknown")
        self.assertEqual(self.lib.open_cfw_cordio_smpr_sc_state_string(0), b"R_IDLE")
        self.assertEqual(self.lib.open_cfw_cordio_smpr_sc_state_string(39), b"R_RSP_TO")
        self.assertEqual(self.lib.open_cfw_cordio_smpr_sc_state_string(40), b"R_Unknown")
        self.assertEqual(self.lib.open_cfw_cordio_smpr_sc_state_string(255), b"R_Unknown")


if __name__ == "__main__":
    unittest.main()
