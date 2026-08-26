import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/service_touch_dfu.c"
FIXTURE = ROOT / "tests/fixtures/service_touch_dfu_host.c"
HEADER = ROOT / "tests/fixtures/service_touch_dfu_host.h"
NAMES = (
    "open_cfw_touch_frame_read_u16", "open_cfw_touch_frame_write_u16",
    "open_cfw_touch_frame_payload", "open_cfw_touch_frame_terminator",
    "open_cfw_touch_frame_command", "open_cfw_touch_frame_payload_length",
    "open_cfw_touch_frame_checksum", "open_cfw_touch_frame_has_terminator",
    "open_cfw_touch_frame_init", "open_cfw_touch_frame_set_command",
    "open_cfw_touch_frame_set_payload_length", "open_cfw_touch_frame_set_checksum",
    "open_cfw_touch_frame_set_terminator", "open_cfw_touch_frame_checksum16",
    "open_cfw_touch_validate_reply", "open_cfw_touch_receive_reply_retry",
    "open_cfw_touch_crc32c", "open_cfw_touch_build_and_send_frame",
    "open_cfw_touch_enter_dfu", "open_cfw_touch_set_app_meta",
    "open_cfw_touch_send_one_packet", "open_cfw_touch_program_data",
    "open_cfw_touch_verify_app", "open_cfw_touch_exit_dfu",
    "open_cfw_touch_send_app_file", "open_cfw_touch_free_firmware_memory",
    "open_cfw_touch_get_package_version", "open_cfw_touch_load_package",
    "open_cfw_touch_format_version", "open_cfw_touch_is_upgrade_needed",
    "open_cfw_touch_log_current_version", "open_cfw_touch_update_firmware_check",
)


class TouchDfuCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / ("touch.dylib" if os.uname().sysname == "Darwin" else "touch.so")
        command = [os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), "-O2",
                   "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                   str(SOURCE), str(FIXTURE), "-I", str(HEADER.parent)]
        command += (["-dynamiclib", "-o", str(library)] if os.uname().sysname == "Darwin"
                    else ["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_crc32c.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.open_cfw_touch_crc32c.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_build_and_send_frame.argtypes = [ctypes.c_void_p,
            ctypes.c_uint8, ctypes.c_void_p, ctypes.c_uint16]
        cls.lib.host_touch_copy_tx.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.host_touch_copy_tx.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.lib.host_touch_reset()

    def tx(self):
        output = (ctypes.c_ubyte * 32768)()
        size = self.lib.host_touch_copy_tx(output, len(output))
        return bytes(output[:size])

    def test_all_target_selectors_compile_strictly(self):
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-mcpu=cortex-m55",
                 "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                 "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                 "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                 "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
                 "-enable-machine-outliner=never"]
        for selector, name in enumerate(NAMES, 1):
            output = Path(self.tmp.name) / f"{selector}.o"
            subprocess.run([os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), *flags,
                f"-DOPEN_CFW_TOUCH_DFU_SELECTOR={selector}", "-c", str(SOURCE),
                "-o", str(output)], check=True, capture_output=True)
            self.assertGreater(output.stat().st_size, 0, name)

    def test_crc32c_and_frame_contract(self):
        sample = ctypes.create_string_buffer(b"123456789")
        self.assertEqual(self.lib.open_cfw_touch_crc32c(sample, 9), 0xE3069283)
        payload = (ctypes.c_ubyte * 4)(4, 3, 2, 1)
        ops = (ctypes.c_void_p * 4).in_dll(self.lib, "touch_dfu_ops_words")
        self.assertEqual(self.lib.open_cfw_touch_build_and_send_frame(
            ctypes.byref(ops), 0x38, payload, 4), 0)
        self.assertEqual(self.tx(), b"\x01\x38\x04\x00\x04\x03\x02\x01\xb9\xff\x17")

    def test_reply_validation_accepts_only_complete_checksum_frame(self):
        frame = (ctypes.c_ubyte * 15)()
        frame[0], frame[1], frame[6] = 1, 0x38, 0x17
        frame[4], frame[5] = 0xC7, 0xFF
        valid = ctypes.c_bool()
        self.lib.open_cfw_touch_validate_reply.argtypes = [ctypes.c_uint16,
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        self.assertEqual(self.lib.open_cfw_touch_validate_reply(15, frame,
            ctypes.byref(valid)), 0x38)
        self.assertTrue(valid.value)
        frame[6] = 0
        self.assertEqual(self.lib.open_cfw_touch_validate_reply(15, frame,
            ctypes.byref(valid)), 4)
        self.assertFalse(valid.value)

    def test_package_load_validates_crc_and_excludes_trailing_word(self):
        self.lib.host_touch_make_package(0, 0)
        self.assertEqual(self.lib.open_cfw_touch_load_package(), 0)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib,
            "touch_dfu_firmware_size").value, 128)
        self.lib.open_cfw_touch_free_firmware_memory()
        self.lib.host_touch_make_package(1, 0)
        self.assertEqual(self.lib.open_cfw_touch_load_package(), -1)
        self.lib.host_touch_make_package(0, 1)
        self.assertEqual(self.lib.open_cfw_touch_load_package(), -1)

    def test_recovered_command_sequence_and_program_granularity(self):
        data = (ctypes.c_ubyte * 129)(*range(129))
        self.assertEqual(self.lib.open_cfw_touch_send_app_file(data, 129), 0)
        transmitted = self.tx()
        commands = []
        offset = 0
        while offset < len(transmitted):
            self.assertEqual(transmitted[offset], 1)
            size = int.from_bytes(transmitted[offset + 2:offset + 4], "little")
            commands.append(transmitted[offset + 1])
            offset += size + 7
        self.assertEqual(commands, [0x37] * 4 + [0x49] + [0x37] * 4 + [0x49])
        self.assertEqual(offset, len(transmitted))

    def test_skip_force_upgrade_and_cleanup(self):
        self.lib.host_touch_make_package(0, 0)
        self.assertEqual(self.lib.open_cfw_touch_update_firmware_check(False), 1)
        self.assertEqual(self.lib.host_touch_switch_count(), 0)
        self.lib.host_touch_make_package(0, 0)
        self.assertEqual(self.lib.open_cfw_touch_update_firmware_check(True), 0)
        self.assertEqual(self.lib.host_touch_switch_count(), 1)
        self.assertEqual(self.lib.host_touch_reset_count(), 3)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib,
            "touch_dfu_firmware_size").value, 0)
        transmitted = self.tx()
        self.assertEqual(transmitted[1], 0x38)
        self.assertEqual(transmitted[-6], 0x3B)

    def test_transport_failure_is_bounded_and_cleans_memory(self):
        self.lib.host_touch_make_package(0, 0)
        self.lib.host_touch_set_auto_reply(0)
        self.assertEqual(self.lib.open_cfw_touch_update_firmware_check(True), -1)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib,
            "touch_dfu_firmware_size").value, 0)
        self.assertGreaterEqual(self.lib.host_touch_delay_total(), 150)


if __name__ == "__main__":
    unittest.main()
