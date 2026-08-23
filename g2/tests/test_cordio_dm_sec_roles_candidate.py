from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_dm_sec_roles.c"
FIXTURE = ROOT / "tests/fixtures"


class Ccb(ctypes.Structure):
    _fields_ = [
        ("reserved0", ctypes.c_ubyte * 12),
        ("handle", ctypes.c_ushort),
        ("reserved14", ctypes.c_ubyte * 2),
        ("connection_id", ctypes.c_ubyte),
        ("reserved17", ctypes.c_ubyte),
        ("using_ltk", ctypes.c_ubyte),
        ("reserved19", ctypes.c_ubyte * 5),
        ("temporary_security_level", ctypes.c_ubyte),
    ]


class CordioDmSecRolesCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / ("dm_sec_roles" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-Wall", "-Wextra", "-Werror",
                "-include", str(FIXTURE / "cordio_dm_sec_roles_host.h"),
                str(SOURCE), str(FIXTURE / "cordio_dm_sec_roles_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.pair_rsp = cls.loaded.open_cfw_cordio_dm_sec_slave_pair_response
        cls.pair_rsp.argtypes = [ctypes.c_ubyte] * 5
        cls.slave_req = cls.loaded.open_cfw_cordio_dm_sec_slave_request
        cls.slave_req.argtypes = [ctypes.c_ubyte] * 2
        cls.ltk_rsp = cls.loaded.open_cfw_cordio_dm_sec_slave_ltk_response
        cls.ltk_rsp.argtypes = [
            ctypes.c_ubyte, ctypes.c_uint, ctypes.c_ubyte, ctypes.c_void_p
        ]
        cls.smp_encrypt = (
            cls.loaded.open_cfw_cordio_dm_sec_master_smp_encrypt_request
        )
        cls.smp_encrypt.argtypes = [
            ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_void_p
        ]
        cls.pair_req = cls.loaded.open_cfw_cordio_dm_sec_master_pair_request
        cls.pair_req.argtypes = [ctypes.c_ubyte] * 5
        cls.encrypt_req = (
            cls.loaded.open_cfw_cordio_dm_sec_master_encrypt_request
        )
        cls.encrypt_req.argtypes = [
            ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_void_p
        ]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def reset(self, allocation=1):
        self.loaded.open_cfw_test_dm_sec_roles_reset(allocation)

    def word(self, name):
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def byte(self, name):
        return ctypes.c_ubyte.in_dll(self.loaded, name).value

    def message(self):
        return (ctypes.c_ubyte * 32).in_dll(
            self.loaded, "open_cfw_test_dm_sec_roles_message"
        )

    def test_slave_pair_and_security_requests(self):
        self.reset()
        self.pair_rsp(0x34, 1, 0x25, 0xFF, 0xA6)
        message = self.message()
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_alloc_size"), 8)
        self.assertEqual(
            (message[0], message[1], message[2], message[3]),
            (0x34, 0, 2, 0xA5),
        )
        self.assertEqual(tuple(message[4:8]), (1, 0x25, 7, 6))
        self.assertEqual(
            self.word("open_cfw_test_dm_sec_roles_smp_send_calls"), 1
        )

        self.reset()
        self.slave_req(7, 0x19)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_alloc_size"), 6)
        self.assertEqual(
            (message[0], message[2], message[3], message[4], message[5]),
            (7, 5, 0xA5, 0x19, 0xA5),
        )

    def test_slave_ltk_response_found_missing_and_allocation_failure(self):
        key = (ctypes.c_ubyte * 16)(*range(16))
        self.reset()
        self.ltk_rsp(9, 1, 4, key)
        message = self.message()
        self.assertEqual((message[0], message[2], message[20], message[21]),
                         (9, 0x29, 1, 4))
        self.assertEqual(bytes(message[4:20]), bytes(key))
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_copy_calls"), 1)
        self.assertEqual(self.byte("open_cfw_test_dm_sec_roles_send_handler"),
                         0x5A)

        self.reset()
        self.ltk_rsp(2, 0, 3, None)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_copy_calls"), 0)
        self.assertEqual(bytes(message[4:20]), b"\xA5" * 16)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_wsf_send_calls"),
                         1)

        self.reset(allocation=0)
        self.ltk_rsp(1, 1, 1, key)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_wsf_send_calls"),
                         0)

    def test_master_smp_encrypt_request_and_missing_connection(self):
        key = (ctypes.c_ubyte * 16)(*(0xF0 + index for index in range(16)))
        self.reset()
        ccb = Ccb.in_dll(self.loaded, "open_cfw_test_dm_sec_roles_ccb")
        ccb.handle = 0x3456
        ccb.using_ltk = 1
        self.smp_encrypt(3, 6, key)
        self.assertEqual(ccb.temporary_security_level, 6)
        self.assertEqual(ccb.using_ltk, 0)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_start_calls"), 1)
        self.assertEqual(
            ctypes.c_ushort.in_dll(
                self.loaded, "open_cfw_test_dm_sec_roles_start_handle"
            ).value,
            0x3456,
        )
        random = (ctypes.c_ubyte * 8).in_dll(
            self.loaded, "open_cfw_test_dm_sec_roles_start_random"
        )
        recorded_key = (ctypes.c_ubyte * 16).in_dll(
            self.loaded, "open_cfw_test_dm_sec_roles_start_key"
        )
        self.assertEqual(bytes(random), b"\0" * 8)
        self.assertEqual(bytes(recorded_key), bytes(key))

        ctypes.c_uint.in_dll(
            self.loaded, "open_cfw_test_dm_sec_roles_ccb_available"
        ).value = 0
        self.smp_encrypt(3, 2, key)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_start_calls"), 1)

    def test_master_pair_and_encrypt_requests(self):
        self.reset()
        self.pair_req(5, 0, 0x11, 0x89, 0xFE)
        message = self.message()
        self.assertEqual((message[0], message[2]), (5, 1))
        self.assertEqual(tuple(message[4:8]), (0, 0x11, 1, 6))

        ltk = (ctypes.c_ubyte * 26)(*(index ^ 0x5A for index in range(26)))
        self.reset()
        self.encrypt_req(8, 7, ltk)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_alloc_size"), 32)
        self.assertEqual((message[0], message[2], message[3]), (8, 0x28, 0xA5))
        self.assertEqual(bytes(message[4:30]), bytes(ltk))
        self.assertEqual((message[30], message[31]), (7, 0xA5))
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_copy_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_sec_roles_wsf_send_calls"),
                         1)

    def test_thumb_object_exposes_exactly_six_text_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "dm_sec_roles.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            text_symbols = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(
                text_symbols,
                {
                    "open_cfw_cordio_dm_sec_slave_pair_response",
                    "open_cfw_cordio_dm_sec_slave_request",
                    "open_cfw_cordio_dm_sec_slave_ltk_response",
                    "open_cfw_cordio_dm_sec_master_smp_encrypt_request",
                    "open_cfw_cordio_dm_sec_master_pair_request",
                    "open_cfw_cordio_dm_sec_master_encrypt_request",
                },
            )


if __name__ == "__main__":
    unittest.main()
