import ctypes
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/service_codec_host.c"
FIXTURE = ROOT / "tests/fixtures/service_codec_host_host.c"
HEADER = ROOT / "tests/fixtures/service_codec_host_host.h"


class CodecMessage(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("command", ctypes.c_uint16),
        ("sequence", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("encoded_body_length", ctypes.c_uint16),
        ("header_crc", ctypes.c_uint32),
        ("body", ctypes.POINTER(ctypes.c_uint8)),
        ("body_length", ctypes.c_uint16),
        ("body_crc", ctypes.c_uint32),
        ("wire_length", ctypes.c_uint16),
    ]


class ServiceCodecHostCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.libs = {}
        for selector in range(1, 27):
            output = Path(cls.temp.name) / f"codec-host-{selector}.so"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                f"-DOPEN_CFW_SELECTOR={selector}", str(SOURCE), str(FIXTURE),
                "-o", str(output),
            ], check=True)
            cls.libs[selector] = ctypes.CDLL(str(output))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def u8(lib, name):
        return ctypes.c_uint8.in_dll(lib, name)

    @staticmethod
    def u16(lib, name):
        return ctypes.c_uint16.in_dll(lib, name)

    @staticmethod
    def u32(lib, name):
        return ctypes.c_uint32.in_dll(lib, name)

    @staticmethod
    def i32(lib, name):
        return ctypes.c_int32.in_dll(lib, name)

    @staticmethod
    def array(lib, name, size):
        return (ctypes.c_uint8 * size).in_dll(lib, name)

    def set_response(self, lib, body):
        target = self.array(lib, "host_response_body", 16)
        for index, value in enumerate(body):
            target[index] = value
        self.u16(lib, "host_response_body_length").value = len(body)

    def test_host_init_and_cleanup_preserve_porting_status(self):
        init = self.libs[1]
        init.open_cfw_codec_host_init.restype = ctypes.c_int32
        self.i32(init, "host_init_result").value = 0
        self.assertEqual(init.open_cfw_codec_host_init(), 0)
        self.assertEqual(self.u32(init, "host_baud").value, 115200)
        self.i32(init, "host_init_result").value = -4
        self.u32(init, "host_baud").value = 0
        self.assertEqual(init.open_cfw_codec_host_init(), -4)
        self.assertEqual(self.u32(init, "host_baud").value, 0)

        close = self.libs[2]
        close.open_cfw_codec_host_cleanup.restype = ctypes.c_int32
        self.i32(close, "host_close_result").value = -7
        self.assertEqual(close.open_cfw_codec_host_cleanup(), -7)

    def test_magic_pack_crc_and_bounds(self):
        magic = self.libs[3]
        magic.open_cfw_codec_host_magic_matches.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        magic.open_cfw_codec_host_magic_matches.restype = ctypes.c_int32
        good = (ctypes.c_uint8 * 4)(*b"BUXX")
        bad = (ctypes.c_uint8 * 4)(*b"BAXX")
        self.assertEqual(magic.open_cfw_codec_host_magic_matches(good), 0)
        self.assertNotEqual(magic.open_cfw_codec_host_magic_matches(bad), 0)

        lib = self.libs[4]
        fn = lib.open_cfw_codec_host_pack_message
        fn.argtypes = [ctypes.c_uint16, ctypes.c_uint16,
                       ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16,
                       ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8),
                       ctypes.POINTER(ctypes.c_uint16)]
        fn.restype = ctypes.c_int32
        body = (ctypes.c_uint8 * 3)(1, 2, 3)
        wire = (ctypes.c_uint8 * 30)()
        length = ctypes.c_uint16()
        self.u8(lib, "host_codec_sequence").value = 0xFE
        self.assertEqual(fn(0x000B, 0x0100, body, 3, 1, wire,
                            ctypes.byref(length)), 0)
        raw = bytes(wire[:length.value])
        self.assertEqual(raw[:10], b"BUXX\x0b\x01\xfe\x01\x07\x00")
        self.assertEqual(raw[14:17], b"\x01\x02\x03")
        self.assertEqual(struct.unpack_from("<I", raw, 10)[0],
                         zlib.crc32(raw[:10]) & 0xFFFFFFFF)
        self.assertEqual(struct.unpack_from("<I", raw, 17)[0],
                         zlib.crc32(b"\x01\x02\x03") & 0xFFFFFFFF)
        self.assertEqual(self.u8(lib, "host_codec_sequence").value, 0xFF)
        oversized = (ctypes.c_uint8 * 13)(*range(13))
        self.assertEqual(fn(1, 0x100, oversized, 13, 1, wire,
                            ctypes.byref(length)), -2)
        self.assertEqual(fn(1, 0x100, None, 1, 0, wire,
                            ctypes.byref(length)), -1)

    def test_unpack_validates_magic_lengths_and_both_crcs(self):
        lib = self.libs[5]
        fn = lib.open_cfw_codec_host_unpack_message
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16,
                       ctypes.POINTER(CodecMessage), ctypes.c_void_p]
        fn.restype = ctypes.c_int32

        body = b"abc"
        header = bytearray(b"BUXX\x02\x02\x09\x01\x07\x00\x00\x00\x00\x00")
        struct.pack_into("<I", header, 10, zlib.crc32(header[:10]) & 0xFFFFFFFF)
        raw = bytes(header) + body + struct.pack("<I", zlib.crc32(body) & 0xFFFFFFFF)
        wire = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
        message = CodecMessage()
        self.assertEqual(fn(wire, len(raw), ctypes.byref(message), None), 0)
        self.assertEqual((message.command, message.sequence, message.body_length,
                          message.wire_length), (0x0202, 9, 3, 21))
        self.assertEqual(ctypes.string_at(message.body, 3), body)
        lib.host_codec_free(message.body)

        corrupt = bytearray(raw)
        corrupt[-1] ^= 1
        bad_wire = (ctypes.c_uint8 * len(corrupt)).from_buffer_copy(corrupt)
        before = self.u32(lib, "host_free_calls").value
        self.assertEqual(fn(bad_wire, len(corrupt), ctypes.byref(message), None), -7)
        self.assertEqual(self.u32(lib, "host_free_calls").value, before + 1)
        self.assertFalse(bool(message.body))
        corrupt = bytearray(raw)
        corrupt[0] = ord("Q")
        self.assertEqual(fn((ctypes.c_uint8 * len(corrupt)).from_buffer_copy(corrupt),
                            len(corrupt), ctypes.byref(message), None), -2)
        self.assertEqual(fn(wire, 13, ctypes.byref(message), None), -1)

    def test_send_read_and_request_cleanup_paths(self):
        send = self.libs[6]
        send.open_cfw_codec_host_send_message.restype = ctypes.c_int32
        self.i32(send, "host_pack_result").value = 0
        self.i32(send, "host_write_result").value = -5
        self.assertEqual(send.open_cfw_codec_host_send_message(7, 0x100,
                                                               None, 0, 0), -5)
        self.assertEqual(self.array(send, "host_uart_output", 64)[0], 0xAA)

        read = self.libs[7]
        fn = read.open_cfw_codec_host_uart_read_blocking
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16,
                       ctypes.c_uint32, ctypes.c_void_p]
        fn.restype = ctypes.c_int32
        payload = bytearray(b"BUXX\x02\x02\x00\x00\x03\x00\x00\x00\x00\x00abc")
        source = self.array(read, "host_uart_input", 64)
        source[:len(payload)] = payload
        self.u16(read, "host_uart_input_length").value = len(payload)
        self.u16(read, "host_uart_input_position").value = 0
        destination = (ctypes.c_uint8 * 30)()
        self.assertEqual(fn(destination, 30, 20, None), len(payload))
        self.assertEqual(bytes(destination[:len(payload)]), bytes(payload))
        self.u16(read, "host_uart_input_length").value = 0
        self.u16(read, "host_uart_input_position").value = 0
        ctypes.c_uint64.in_dll(read, "host_now_ms").value = 0
        self.assertEqual(fn(destination, 30, 2, None), -1)
        self.assertGreaterEqual(self.u32(read, "host_delay_calls").value, 2)

        wrapper = self.libs[8]
        wrapper.open_cfw_codec_host_read_uart_data.restype = ctypes.c_int32
        self.i32(wrapper, "host_read_result").value = 18
        length = ctypes.c_uint16()
        self.assertEqual(wrapper.open_cfw_codec_host_read_uart_data(
            self.array(wrapper, "host_codec_rx_buffer", 30), 30,
            ctypes.byref(length), 50), 0)
        self.assertEqual(length.value, 18)

        request = self.libs[9]
        request.open_cfw_codec_host_send_and_wait_response.restype = ctypes.c_int32
        response = CodecMessage()
        self.i32(request, "host_send_result").value = 0
        self.i32(request, "host_read_result").value = 0
        self.i32(request, "host_unpack_result").value = 0
        self.u16(request, "host_uart_input_length").value = 14
        self.set_response(request, b"ok")
        self.assertEqual(request.open_cfw_codec_host_send_and_wait_response(
            2, 0x100, None, 0, 0, ctypes.byref(response), 200), 0)
        self.assertEqual((self.u32(request, "host_init_calls").value,
                          self.u32(request, "host_close_calls").value), (1, 1))
        self.i32(request, "host_send_result").value = -8
        self.assertEqual(request.open_cfw_codec_host_send_and_wait_response(
            2, 0x100, None, 0, 0, ctypes.byref(response), 200), -8)
        self.assertEqual(self.u32(request, "host_close_calls").value, 2)

    def test_free_message_owns_only_allocated_body(self):
        lib = self.libs[10]
        lib.open_cfw_codec_host_free_message.argtypes = [ctypes.POINTER(CodecMessage)]
        lib.host_codec_allocate.argtypes = [ctypes.c_uint32]
        lib.host_codec_allocate.restype = ctypes.c_void_p
        allocation = lib.host_codec_allocate(4)
        message = CodecMessage(body=ctypes.cast(allocation,
                                                ctypes.POINTER(ctypes.c_uint8)),
                               body_length=4)
        before = self.u32(lib, "host_free_calls").value
        lib.open_cfw_codec_host_free_message(ctypes.byref(message))
        self.assertEqual(self.u32(lib, "host_free_calls").value, before + 1)
        self.assertFalse(bool(message.body))
        self.assertEqual(message.body_length, 0)

    def test_command_helpers_retry_and_decode_exact_contracts(self):
        cases = [
            (11, "open_cfw_codec_read_version", 0x02, b"\x01\x02\x03\x04", 4),
            (12, "open_cfw_codec_switch_bf_mode", 0x07, b"\x01", 1),
            (13, "open_cfw_codec_switch_wakeup_mode", 0x08, b"\x00", 1),
            (14, "open_cfw_codec_query_mic_state", 0x70, b"\x34\x12", 2),
        ]
        for selector, name, command, body, width in cases:
            lib = self.libs[selector]
            self.set_response(lib, body)
            self.u32(lib, "host_send_wait_failures").value = 1
            output = (ctypes.c_uint8 * 4)()
            fn = getattr(lib, name)
            fn.restype = ctypes.c_int32
            self.assertEqual(fn(output, 77), 0)
            self.assertEqual(self.u32(lib, "host_send_wait_calls").value, 2)
            self.assertEqual(self.u16(lib, "host_last_command_low").value, command)
            self.assertEqual(bytes(output[:width]), body[:width])

        gain = self.libs[15]
        self.set_response(gain, b"\x01\x00")
        status16 = ctypes.c_uint16()
        gain.open_cfw_codec_set_mic_gain.restype = ctypes.c_int32
        self.assertEqual(gain.open_cfw_codec_set_mic_gain(
            9, ctypes.byref(status16), 88), 0)
        self.assertEqual((self.u16(gain, "host_last_command_low").value,
                          self.u16(gain, "host_last_body_length").value,
                          self.array(gain, "host_last_body", 16)[0],
                          status16.value), (0x0B, 1, 9, 1))

        dmic = self.libs[16]
        self.set_response(dmic, b"\x01\x00")
        dmic.open_cfw_codec_dmic_control.restype = ctypes.c_int32
        self.assertEqual(dmic.open_cfw_codec_dmic_control(
            1, ctypes.byref(status16), 99), 0)
        self.assertEqual(self.u16(dmic, "host_last_command_low").value, 0x0C)
        self.assertEqual(dmic.open_cfw_codec_dmic_control(
            0, ctypes.byref(status16), 99), 0)
        self.assertEqual(self.u16(dmic, "host_last_command_low").value, 0x0D)

        i2s = self.libs[17]
        self.set_response(i2s, b"\x01")
        status8 = ctypes.c_uint8()
        i2s.open_cfw_codec_i2s_output_control.restype = ctypes.c_int32
        self.assertEqual(i2s.open_cfw_codec_i2s_output_control(
            7, ctypes.byref(status8), 101), 0)
        self.assertEqual((self.u16(i2s, "host_last_command_low").value,
                          self.array(i2s, "host_last_body", 16)[0],
                          status8.value), (0x0F, 1, 1))

    def test_fixed_delay_request_and_public_status_wrappers(self):
        delay = self.libs[18]
        self.set_response(delay, b"\x01")
        self.u16(delay, "host_uart_input_length").value = 15
        status = ctypes.c_uint8()
        delay.open_cfw_codec_mic_delay_1bit.restype = ctypes.c_int32
        self.assertEqual(delay.open_cfw_codec_mic_delay_1bit(
            ctypes.byref(status), 200), 0)
        self.assertEqual(bytes(self.array(delay, "host_uart_output", 64)[:14]),
                         bytes.fromhex("425558580e0101000000d4db2f68"))
        self.assertEqual(status.value, 1)

        wrapper_cases = [
            (19, "open_cfw_svc_switch_bf_mode", 1, None),
            (20, "open_cfw_svc_switch_wakeup_mode", 0, None),
            (21, "open_cfw_svc_set_mic_gain", 1, 8),
            (22, "open_cfw_svc_codec_dmic_open", 1, None),
            (23, "open_cfw_svc_codec_dmic_close", 1, None),
            (24, "open_cfw_svc_codec_mic_delay_1bit", 1, None),
            (25, "open_cfw_svc_i2s_output_control", 1, 1),
        ]
        for selector, name, expected_status, argument in wrapper_cases:
            lib = self.libs[selector]
            self.i32(lib, "host_low_level_result").value = 0
            self.u16(lib, "host_low_level_status16").value = expected_status
            self.u8(lib, "host_low_level_status8").value = expected_status
            fn = getattr(lib, name)
            fn.restype = ctypes.c_int32
            result = fn() if argument is None else fn(argument)
            self.assertEqual(result, 0, name)
            self.assertEqual(self.u32(lib, "host_last_timeout").value, 200)
        self.assertEqual(self.u8(self.libs[21], "host_last_gain").value, 8)
        self.assertEqual(self.u8(self.libs[22], "host_last_enable").value, 1)
        self.assertEqual(self.u8(self.libs[23], "host_last_enable").value, 0)

    def test_voice_event_requires_three_body_bytes(self):
        lib = self.libs[26]
        self.set_response(lib, b"\x07\x34\x12")
        self.u16(lib, "host_uart_input_length").value = 17
        output = (ctypes.c_uint8 * 4)()
        lib.open_cfw_codec_get_voice_event.restype = ctypes.c_int32
        self.assertEqual(lib.open_cfw_codec_get_voice_event(output), 0)
        self.assertEqual(bytes(output), b"\x07\x00\x34\x12")
        self.set_response(lib, b"\x07\x34")
        self.assertEqual(lib.open_cfw_codec_get_voice_event(output), -1)

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 27):
            output = Path(self.temp.name) / f"codec-host-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-target", "arm-none-eabi", "-mthumb",
                "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                "-fno-builtin", "-fropi", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_SELECTOR={selector}", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
