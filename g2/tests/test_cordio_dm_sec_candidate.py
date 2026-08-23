from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_dm_sec.c"
FIXTURE = ROOT / "tests/fixtures"


class Ccb(ctypes.Structure):
    _fields_ = [
        ("reserved0", ctypes.c_ubyte * 12),
        ("handle", ctypes.c_ushort),
        ("reserved14", ctypes.c_ubyte * 2),
        ("connection_id", ctypes.c_ubyte),
        ("reserved17", ctypes.c_ubyte),
        ("using_ltk", ctypes.c_ubyte),
        ("reserved19", ctypes.c_ubyte * 4),
        ("security_level", ctypes.c_ubyte),
        ("temporary_security_level", ctypes.c_ubyte),
    ]


class CordioDmSecCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / ("dm_sec" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-Wall", "-Wextra", "-Werror",
                "-include", str(FIXTURE / "cordio_dm_sec_host.h"),
                str(SOURCE), str(FIXTURE / "cordio_dm_sec_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.hci = cls.loaded.open_cfw_cordio_dm_sec_hci_handler
        cls.hci.argtypes = [ctypes.c_void_p]
        cls.message = cls.loaded.open_cfw_cordio_dm_sec_message_handler
        cls.message.argtypes = [ctypes.c_void_p]
        cls.callback = cls.loaded.open_cfw_cordio_dm_sec_smp_callback_execute
        cls.callback.argtypes = [ctypes.c_void_p]
        cls.auth = cls.loaded.open_cfw_cordio_dm_sec_auth_response
        cls.auth.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_void_p]
        cls.init = cls.loaded.open_cfw_cordio_dm_sec_init
        cls.get_csrk = cls.loaded.open_cfw_cordio_dm_sec_get_local_csrk
        cls.get_csrk.restype = ctypes.c_void_p
        cls.get_irk = cls.loaded.open_cfw_cordio_dm_sec_get_local_irk
        cls.get_irk.restype = ctypes.c_void_p
        cls.reset_fn = cls.loaded.open_cfw_cordio_dm_sec_reset
        cls.loaded.open_cfw_test_dm_sec_set_stk.argtypes = [
            ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_uint
        ]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def reset(self, allocation=1):
        self.loaded.open_cfw_test_dm_sec_reset(allocation)

    def word(self, name):
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def byte(self, name):
        return ctypes.c_ubyte.in_dll(self.loaded, name).value

    def ccb(self):
        return Ccb.in_dll(self.loaded, "open_cfw_test_dm_sec_ccb")

    def record(self, name, size=32):
        return (ctypes.c_ubyte * size).in_dll(self.loaded, name)

    def test_hci_ltk_paths_and_secure_connections_rejection(self):
        self.reset()
        event = (ctypes.c_ubyte * 16)()
        event[0:2] = (0x56, 0x34)
        event[2] = 0x10
        key = (ctypes.c_ubyte * 16)(*range(16))
        self.loaded.open_cfw_test_dm_sec_set_stk(key, 5, 0)
        self.hci(event)
        self.assertEqual(self.word("open_cfw_test_dm_sec_reply_calls"), 1)
        self.assertEqual(
            bytes(self.record("open_cfw_test_dm_sec_reply_key", 16)), bytes(key)
        )
        self.assertEqual(self.ccb().temporary_security_level, 5)
        self.assertEqual(self.ccb().using_ltk, 0)

        self.reset()
        event[0:2] = (0x56, 0x34)
        event[2] = 0x10
        event[14:16] = (1, 0)
        self.loaded.open_cfw_test_dm_sec_set_stk(None, 0, 1)
        self.hci(event)
        self.assertEqual(
            self.word("open_cfw_test_dm_sec_negative_reply_calls"), 1
        )
        self.assertEqual(
            ctypes.c_ushort.in_dll(
                self.loaded, "open_cfw_test_dm_sec_negative_handle"
            ).value,
            0x3456,
        )

        self.reset()
        event[:] = b"\0" * 16
        event[0:2] = (0x56, 0x34)
        event[2] = 0x10
        self.hci(event)
        self.assertEqual(event[0:3], [3, 0, 0x30])
        self.assertEqual(self.word("open_cfw_test_dm_sec_dm_callback_calls"), 1)
        self.assertEqual(self.byte("open_cfw_test_dm_sec_idle_value"), 1)
        self.assertEqual(self.ccb().using_ltk, 1)

    def test_hci_encryption_completion_orders_callbacks_and_smp(self):
        self.reset()
        ccb = self.ccb()
        ccb.temporary_security_level = 4
        ccb.using_ltk = 1
        event = (ctypes.c_ubyte * 16)()
        event[0:2] = (0x56, 0x34)
        event[2] = 0x0F
        self.hci(event)
        self.assertEqual(self.byte("open_cfw_test_dm_sec_idle_value"), 0)
        self.assertEqual(self.ccb().security_level, 4)
        self.assertEqual(self.word("open_cfw_test_dm_sec_att_callback_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_sec_dm_callback_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_sec_encrypt_calls"), 1)
        record = self.record("open_cfw_test_dm_sec_encrypt_record")
        self.assertEqual((record[0], record[2], record[3], record[4]), (3, 0x2C, 0, 1))

        self.reset()
        event[2] = 0x0E
        event[3] = 7
        self.hci(event)
        self.assertEqual(self.word("open_cfw_test_dm_sec_att_callback_calls"), 0)
        self.assertEqual(self.word("open_cfw_test_dm_sec_dm_callback_calls"), 1)
        record = self.record("open_cfw_test_dm_sec_encrypt_record")
        self.assertEqual((record[2], record[3]), (0x2D, 7))

    def test_message_handler_encrypt_and_ltk_response_paths(self):
        self.reset()
        message = (ctypes.c_ubyte * 32)()
        message[0] = 3
        message[2] = 0x28
        message[4:20] = range(16)
        message[20:28] = range(20, 28)
        message[28:30] = (0x34, 0x12)
        message[30] = 6
        self.message(message)
        self.assertEqual(self.word("open_cfw_test_dm_sec_start_calls"), 1)
        self.assertEqual(self.ccb().temporary_security_level, 6)
        self.assertEqual(self.ccb().using_ltk, 1)
        self.assertEqual(
            ctypes.c_ushort.in_dll(
                self.loaded, "open_cfw_test_dm_sec_start_diversifier"
            ).value,
            0x1234,
        )

        self.reset()
        message[:] = b"\0" * 32
        message[0] = 3
        message[2] = 0x29
        message[4:20] = range(16, 32)
        message[20] = 1
        message[21] = 7
        self.message(message)
        self.assertEqual(self.word("open_cfw_test_dm_sec_reply_calls"), 1)
        self.assertEqual(self.ccb().temporary_security_level, 7)

        self.reset()
        message[20] = 0
        self.message(message)
        self.assertEqual(
            self.word("open_cfw_test_dm_sec_negative_reply_calls"), 1
        )
        self.assertEqual(self.byte("open_cfw_test_dm_sec_idle_value"), 0)

    def test_callback_auth_init_accessors_and_reset(self):
        self.reset()
        event = (ctypes.c_ubyte * 8)()
        event[2] = 0x2A
        self.callback(event)
        self.assertEqual(self.word("open_cfw_test_dm_sec_att_callback_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_sec_dm_callback_calls"), 1)

        auth = (ctypes.c_ubyte * 16)(*(0xF0 + index for index in range(16)))
        self.auth(9, 16, auth)
        message = self.record("open_cfw_test_dm_sec_allocated_message")
        self.assertEqual((message[0], message[2], message[20]), (9, 4, 16))
        self.assertEqual(bytes(message[4:20]), bytes(auth))
        self.assertEqual(self.word("open_cfw_test_dm_sec_send_calls"), 1)

        self.init()
        zero = self.record("open_cfw_test_dm_sec_zero_key", 16)
        self.assertEqual(self.get_irk(), ctypes.addressof(zero))
        self.assertEqual(self.get_csrk(), ctypes.addressof(zero))
        self.assertEqual(
            ctypes.c_void_p.in_dll(
                self.loaded, "open_cfw_test_dm_sec_interface"
            ).value,
            0x78A898,
        )
        self.reset_fn()
        self.assertEqual(self.word("open_cfw_test_dm_sec_db_init_calls"), 1)

        self.reset(allocation=0)
        self.auth(1, 0, None)
        self.assertEqual(self.word("open_cfw_test_dm_sec_alloc_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_sec_send_calls"), 0)

    def test_thumb_object_exposes_exactly_eight_text_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "dm_sec.o"
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
                    "open_cfw_cordio_dm_sec_hci_handler",
                    "open_cfw_cordio_dm_sec_message_handler",
                    "open_cfw_cordio_dm_sec_smp_callback_execute",
                    "open_cfw_cordio_dm_sec_auth_response",
                    "open_cfw_cordio_dm_sec_init",
                    "open_cfw_cordio_dm_sec_get_local_csrk",
                    "open_cfw_cordio_dm_sec_get_local_irk",
                    "open_cfw_cordio_dm_sec_reset",
                },
            )


if __name__ == "__main__":
    unittest.main()
