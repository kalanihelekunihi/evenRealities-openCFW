#!/usr/bin/env python3
"""Exercise the production-excluded G2 adapter around pristine TinyFrame."""

from __future__ import annotations

import ctypes
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "tinyframe"
ADAPTER_DIR = ROOT / "components" / "shared" / "tinyframe"
ADAPTER = ADAPTER_DIR / "runtime_tinyframe_g2_adapter_candidate.c"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_tinyframe_g2_adapter_candidate_host.c"


def crc16_arc(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ 0xA001 if value & 1 else value >> 1
    return value & 0xFFFF


def frame(frame_id: int, frame_type: int, payload: bytes) -> bytes:
    head = b"\x01" + struct.pack(">HHH", frame_id, len(payload), frame_type)
    result = head + struct.pack(">H", crc16_arc(head)) + payload
    if payload:
        result += struct.pack(">H", crc16_arc(payload))
    return result


class TinyFrameG2AdapterCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-g2-")
        temporary = Path(cls.temporary.name)
        objects = []
        common = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-fshort-enums",
            "-fPIC",
            "-I",
            str(SNAPSHOT / "g2-config"),
            "-I",
            str(SNAPSHOT),
            "-I",
            str(ADAPTER_DIR),
        ]
        sources = [
            (
                SNAPSHOT / "TinyFrame.c",
                [
                    "-DTF_Init=open_cfw_tinyframe_upstream_init",
                    "-DTF_InitStatic=open_cfw_tinyframe_upstream_init_static",
                    "-DTF_DeInit=open_cfw_tinyframe_upstream_deinit",
                ],
            ),
            (ADAPTER, []),
            (FIXTURE, []),
        ]
        for index, (source, extra) in enumerate(sources):
            target = temporary / f"part-{index}.o"
            subprocess.run(
                [*common, *extra, "-c", str(source), "-o", str(target)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            objects.append(target)
        library = temporary / (
            "tinyframe-g2.dylib" if sys.platform == "darwin" else "tinyframe-g2.so"
        )
        subprocess.run(
            [
                clang,
                *(str(path) for path in objects),
                *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared"] ),
                "-o",
                str(library),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.tinyframe_host_start.argtypes = [ctypes.c_uint]
        cls.lib.tinyframe_host_start.restype = ctypes.c_int
        cls.lib.tinyframe_host_send.argtypes = [
            ctypes.c_uint16,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint16,
        ]
        cls.lib.tinyframe_host_send.restype = ctypes.c_int
        cls.lib.tinyframe_host_add_listener.argtypes = [ctypes.c_uint16]
        cls.lib.tinyframe_host_add_listener.restype = ctypes.c_int
        cls.lib.tinyframe_host_accept.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32,
        ]
        cls.lib.tinyframe_host_query_timeout.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
        cls.lib.tinyframe_host_query_timeout.restype = ctypes.c_int
        for name in (
            "tinyframe_host_capture_length",
            "tinyframe_host_allocation_size",
            "tinyframe_host_expected_allocation_size",
            "tinyframe_host_core_delta",
            "tinyframe_host_expected_core_delta",
        ):
            getattr(cls.lib, name).restype = ctypes.c_size_t
        cls.lib.tinyframe_host_capture.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.tinyframe_host_last_log.restype = ctypes.c_char_p
        cls.lib.tinyframe_host_prefix.restype = ctypes.c_uint32
        cls.lib.tinyframe_host_suffix.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def tearDown(self) -> None:
        self.lib.tinyframe_host_stop()

    @staticmethod
    def _array(value: bytes):
        return (ctypes.c_uint8 * len(value)).from_buffer_copy(value)

    def _capture(self) -> bytes:
        length = self.lib.tinyframe_host_capture_length()
        return bytes(self.lib.tinyframe_host_capture()[:length])

    def test_bookended_allocation_is_separate_from_pristine_core(self) -> None:
        self.assertEqual(self.lib.tinyframe_host_start(0), 1)
        self.assertEqual(self.lib.tinyframe_host_prefix(), 0xA5A5A5A5)
        self.assertEqual(self.lib.tinyframe_host_suffix(), 0x5A5A5A5A)
        self.assertEqual(
            self.lib.tinyframe_host_core_delta(),
            self.lib.tinyframe_host_expected_core_delta(),
        )
        self.assertEqual(
            self.lib.tinyframe_host_allocation_size(),
            self.lib.tinyframe_host_expected_allocation_size(),
        )

    def test_transport_keeps_timeout_100_and_master_peer_bit(self) -> None:
        self.assertEqual(self.lib.tinyframe_host_start(1), 1)
        self.lib.tinyframe_host_reset_capture()
        payload = b"\x10\x20"
        data = self._array(payload)
        self.assertEqual(self.lib.tinyframe_host_send(0x1234, data, len(payload)), 1)
        self.assertEqual(
            self._capture(),
            bytes.fromhex("01800000021234b7a31020180c"),
        )
        self.assertEqual(self.lib.tinyframe_host_write_timeout(), 100)
        self.assertEqual(self.lib.tinyframe_host_write_calls(), 1)

    def test_receive_listener_observes_the_same_opaque_core_pointer(self) -> None:
        self.assertEqual(self.lib.tinyframe_host_start(0), 1)
        self.assertEqual(self.lib.tinyframe_host_add_listener(0x3344), 1)
        wire = frame(0x8123, 0x3344, b"callback")
        data = self._array(wire)
        self.lib.tinyframe_host_accept(data, len(wire))
        self.assertEqual(self.lib.tinyframe_host_listener_calls(), 1)
        self.assertEqual(self.lib.tinyframe_host_callback_pointer_matches(), 1)
        self.assertEqual(self.lib.tinyframe_host_prefix(), 0xA5A5A5A5)
        self.assertEqual(self.lib.tinyframe_host_suffix(), 0x5A5A5A5A)

    def test_timeout_callback_observes_the_same_pointer(self) -> None:
        self.assertEqual(self.lib.tinyframe_host_start(0), 1)
        self.lib.tinyframe_host_reset_capture()
        self.assertEqual(self.lib.tinyframe_host_query_timeout(0x4567, 1), 1)
        self.lib.tinyframe_host_tick()
        self.assertEqual(self.lib.tinyframe_host_timeout_calls(), 1)
        self.assertEqual(self.lib.tinyframe_host_callback_pointer_matches(), 1)
        self.assertIn(b"ID listener", self.lib.tinyframe_host_last_log())

    def test_invalid_head_checksum_reaches_isolated_logger_port(self) -> None:
        self.assertEqual(self.lib.tinyframe_host_start(0), 1)
        self.lib.tinyframe_host_reset_capture()
        wire = bytearray(frame(2, 3, b"bad"))
        wire[8] ^= 1
        data = self._array(bytes(wire))
        self.lib.tinyframe_host_accept(data, len(wire))
        self.assertGreater(self.lib.tinyframe_host_log_calls(), 0)
        self.assertIn(b"cksum mismatch", self.lib.tinyframe_host_last_log())

    def test_target_candidate_compiles_with_exact_g2_layout_assertions(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        assert clang is not None
        with tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-g2-target-") as raw:
            target = Path(raw) / "adapter.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-std=c11",
                    "-ffreestanding",
                    "-fshort-enums",
                    "-I",
                    str(SNAPSHOT / "g2-compat"),
                    "-I",
                    str(SNAPSHOT / "g2-config"),
                    "-I",
                    str(SNAPSHOT),
                    "-I",
                    str(ADAPTER_DIR),
                    "-c",
                    str(ADAPTER),
                    "-o",
                    str(target),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(target.read_bytes().startswith(b"\x7fELF"))


if __name__ == "__main__":
    unittest.main()
