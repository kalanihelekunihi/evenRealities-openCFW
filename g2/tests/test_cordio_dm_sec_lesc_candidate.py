from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_dm_sec_lesc.c"
FIXTURE = ROOT / "tests/fixtures"


class CordioDmSecLescCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / ("dm_sec_lesc" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "cordio_dm_sec_lesc_host.h"),
                str(SOURCE),
                str(FIXTURE / "cordio_dm_sec_lesc_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.handler = cls.loaded.open_cfw_cordio_dm_sec_lesc_message_handler
        cls.handler.argtypes = [ctypes.c_void_p]
        cls.generate = cls.loaded.open_cfw_cordio_dm_sec_generate_ecc_key_request
        cls.set_key = cls.loaded.open_cfw_cordio_dm_sec_set_ecc_key
        cls.set_key.argtypes = [ctypes.c_void_p]
        cls.get_key = cls.loaded.open_cfw_cordio_dm_sec_get_ecc_key
        cls.get_key.restype = ctypes.c_void_p
        cls.compare = cls.loaded.open_cfw_cordio_dm_sec_compare_response
        cls.compare.argtypes = [ctypes.c_ubyte, ctypes.c_uint]
        cls.value = cls.loaded.open_cfw_cordio_dm_sec_get_compare_value
        cls.value.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.value.restype = ctypes.c_uint
        cls.init = cls.loaded.open_cfw_cordio_dm_sec_lesc_init

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def word(self, name):
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def byte(self, name):
        return ctypes.c_ubyte.in_dll(self.loaded, name).value

    def reset(self, allocation=1):
        self.loaded.open_cfw_test_dm_reset(allocation)

    def test_message_handler_forwards_ecc_and_rebuilds_oob_event(self):
        self.reset()
        message = (ctypes.c_ubyte * 16)()
        message[2] = 0x41
        self.handler(message)
        self.assertEqual(message[2], 0x34)
        self.assertEqual(self.word("open_cfw_test_dm_callback_calls"), 1)
        record = (ctypes.c_ubyte * 36).in_dll(
            self.loaded, "open_cfw_test_dm_callback_record"
        )
        self.assertEqual(record[2], 0x34)

        self.reset()
        confirm = (ctypes.c_ubyte * 16)(*range(16))
        random = (ctypes.c_ubyte * 16)(*(range(16, 32)))
        plaintext = (ctypes.c_ubyte * 3)(1, 2, 3)
        message[2] = 0x40
        ctypes.c_void_p.in_dll(
            self.loaded, "open_cfw_test_dm_oob_random"
        ).value = ctypes.addressof(random)
        self.loaded.open_cfw_test_dm_set_message_fields(
            message, confirm, plaintext
        )
        self.handler(message)
        self.assertEqual(self.word("open_cfw_test_dm_free_calls"), 2)
        self.assertEqual(self.word("open_cfw_test_dm_copy_calls"), 2)
        self.assertEqual(bytes(record[4:20]), bytes(confirm))
        self.assertEqual(bytes(record[20:36]), bytes(random))
        self.assertEqual((record[2], record[3]), (0x33, 0))

    def test_key_generation_set_get_and_init(self):
        self.reset()
        self.generate()
        self.assertEqual(self.word("open_cfw_test_dm_ecc_calls"), 1)
        self.assertEqual(self.byte("open_cfw_test_dm_ecc_handler"), 0x5A)
        self.assertEqual(self.byte("open_cfw_test_dm_ecc_event"), 0x41)

        key = (ctypes.c_ubyte * 96)(*(index ^ 0xA5 for index in range(96)))
        self.set_key(key)
        local = (ctypes.c_ubyte * 96).in_dll(
            self.loaded, "open_cfw_test_dm_local_key"
        )
        self.assertEqual(bytes(local), bytes(key))
        self.assertEqual(self.get_key(), ctypes.addressof(local))

        self.init()
        self.assertEqual(
            ctypes.c_void_p.in_dll(
                self.loaded, "open_cfw_test_dm_interface"
            ).value,
            0x78A8A4,
        )

    def test_compare_response_preserves_allocation_and_cancel_policy(self):
        self.reset()
        self.compare(7, 1)
        message = (ctypes.c_ubyte * 22).in_dll(
            self.loaded, "open_cfw_test_dm_message"
        )
        self.assertEqual(bytes(message[:3]), b"\x07\x00\x16")
        self.assertEqual(self.word("open_cfw_test_dm_send_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_cancel_calls"), 0)

        self.reset()
        self.compare(9, 0)
        self.assertEqual(self.word("open_cfw_test_dm_cancel_calls"), 1)
        self.assertEqual(self.byte("open_cfw_test_dm_cancel_connection"), 9)
        self.assertEqual(self.byte("open_cfw_test_dm_cancel_reason"), 0x0C)
        self.assertEqual(self.word("open_cfw_test_dm_send_calls"), 1)

        self.reset(allocation=0)
        self.compare(1, 1)
        self.assertEqual(self.word("open_cfw_test_dm_alloc_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_dm_send_calls"), 0)

    def test_compare_value_uses_big_endian_tail_and_six_digits(self):
        confirm = (ctypes.c_ubyte * 16)()
        confirm[12:16] = (0x12, 0x34, 0x56, 0x78)
        self.assertEqual(self.value(confirm), 0x12345678 % 1000000)

    def test_thumb_object_exposes_exactly_seven_text_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "dm_sec_lesc.o"
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
                    "open_cfw_cordio_dm_sec_lesc_message_handler",
                    "open_cfw_cordio_dm_sec_generate_ecc_key_request",
                    "open_cfw_cordio_dm_sec_set_ecc_key",
                    "open_cfw_cordio_dm_sec_get_ecc_key",
                    "open_cfw_cordio_dm_sec_compare_response",
                    "open_cfw_cordio_dm_sec_get_compare_value",
                    "open_cfw_cordio_dm_sec_lesc_init",
                },
            )


if __name__ == "__main__":
    unittest.main()
