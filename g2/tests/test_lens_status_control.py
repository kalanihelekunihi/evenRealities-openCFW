from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "lens_status_control.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "lens_status_control_host.c"
)


class LensStatusControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "lens_status_control.dylib"
            if sys.platform == "darwin"
            else "lens_status_control.so"
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
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.publish = cls.loaded.open_cfw_lens_status_publish
        cls.publish.argtypes = []
        cls.publish.restype = None
        cls.template4 = cls.loaded.open_cfw_status_packet_template4
        cls.template4.argtypes = [ctypes.c_uint]
        cls.template4.restype = ctypes.c_uint
        cls.accessors = [
            cls.loaded.open_cfw_lens_status_bit0,
            cls.loaded.open_cfw_lens_status_bit1,
            cls.loaded.open_cfw_lens_status_pair23,
            cls.loaded.open_cfw_lens_status_bit4,
            cls.loaded.open_cfw_lens_status_bit5,
        ]
        for function in cls.accessors:
            function.argtypes = []
            function.restype = ctypes.c_uint
        cls.available_accessor = (
            cls.loaded.open_cfw_lens_status_available
        )
        cls.available_accessor.argtypes = []
        cls.available_accessor.restype = ctypes.c_uint
        cls.selected_accessor = cls.loaded.open_cfw_lens_status_selected
        cls.selected_accessor.argtypes = []
        cls.selected_accessor.restype = ctypes.c_uint

        cls.state = cls.uint8("open_cfw_test_lens_status_state")
        cls.available = cls.uint("open_cfw_test_lens_status_available")
        cls.selector = cls.uint("open_cfw_test_lens_status_selector")
        cls.log_levels = (ctypes.c_uint * 4).in_dll(
            cls.loaded,
            "open_cfw_test_lens_status_log_levels",
        )
        cls.log_level_calls = cls.uint(
            "open_cfw_test_lens_status_log_level_calls"
        )
        cls.log_calls = cls.uint("open_cfw_test_lens_status_log_calls")
        cls.trace_calls = cls.uint("open_cfw_test_lens_status_trace_calls")
        cls.template6_calls = cls.uint(
            "open_cfw_test_lens_status_template6_calls"
        )
        cls.template5_calls = cls.uint(
            "open_cfw_test_lens_status_template5_calls"
        )
        cls.lens_values = (ctypes.c_uint * 2).in_dll(
            cls.loaded,
            "open_cfw_test_lens_status_lens_values",
        )
        cls.lens_calls = cls.uint("open_cfw_test_lens_status_lens_calls")
        cls.send_calls = cls.uint("open_cfw_test_lens_status_send_calls")
        cls.send_command = cls.uint(
            "open_cfw_test_lens_status_send_command"
        )
        cls.send_size = cls.uint("open_cfw_test_lens_status_send_size")
        cls.send_option = cls.uint("open_cfw_test_lens_status_send_option")
        cls.send_payload = (ctypes.c_ubyte * 8).in_dll(
            cls.loaded,
            "open_cfw_test_lens_status_send_payload",
        )

        cls.log_severity = cls.uint(
            "open_cfw_test_lens_status_log_severity"
        )
        cls.log_module = cls.ulong("open_cfw_test_lens_status_log_module")
        cls.log_file = cls.ulong("open_cfw_test_lens_status_log_file")
        cls.log_function = cls.ulong(
            "open_cfw_test_lens_status_log_function"
        )
        cls.log_line = cls.uint("open_cfw_test_lens_status_log_line")
        cls.log_identity = cls.ulong(
            "open_cfw_test_lens_status_log_identity"
        )
        cls.trace_event = cls.uint(
            "open_cfw_test_lens_status_trace_event"
        )
        cls.trace_identity = cls.ulong(
            "open_cfw_test_lens_status_trace_identity"
        )

    @classmethod
    def uint(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    @classmethod
    def uint8(cls, name: str) -> ctypes.c_ubyte:
        return ctypes.c_ubyte.in_dll(cls.loaded, name)

    @classmethod
    def ulong(cls, name: str) -> ctypes.c_ulong:
        return ctypes.c_ulong.in_dll(cls.loaded, name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self) -> None:
        self.state.value = 0
        self.available.value = 0
        self.selector.value = 0
        self.log_levels[:] = [0, 0, 0, 0]
        self.log_level_calls.value = 0
        self.log_calls.value = 0
        self.trace_calls.value = 0
        self.template6_calls.value = 0
        self.template5_calls.value = 0
        self.lens_values[:] = [0, 0]
        self.lens_calls.value = 0
        self.send_calls.value = 0

    def test_state_accessors_match_all_byte_values(self) -> None:
        for state in range(256):
            self.state.value = state
            self.assertEqual(
                [function() for function in self.accessors],
                [
                    state & 1,
                    (state >> 1) & 1,
                    1 if state & 0x0C == 0x0C else 0,
                    (state >> 4) & 1,
                    (state >> 5) & 1,
                ],
            )

    def test_template4_matches_stock_packet_model(self) -> None:
        generator = random.Random(0x0047D870)
        for _ in range(300):
            self.reset()
            first_side = generator.getrandbits(32)
            second_side = generator.getrandbits(32)
            enabled = generator.getrandbits(32)
            self.lens_values[:] = [first_side, second_side]

            self.assertEqual(self.template4(enabled), 0x00010004)
            self.assertEqual(self.lens_calls.value, 2)
            self.assertEqual(self.send_calls.value, 1)
            self.assertEqual(self.send_command.value, 0x103)
            self.assertEqual(self.send_size.value, 8)
            self.assertEqual(self.send_option.value, 0)
            self.assertEqual(
                bytes(self.send_payload),
                bytes(
                    [
                        4,
                        0,
                        1,
                        0,
                        first_side & 0xFF,
                        2 if second_side == 1 else 1,
                        1 if enabled != 0 else 0,
                        0,
                    ]
                ),
            )

    def test_available_accessor_preserves_query_result(self) -> None:
        for value in (0, 1, 2, 0x7FFFFFFF, 0xFFFFFFFF):
            self.available.value = value
            self.assertEqual(self.available_accessor(), value)

    def test_selected_accessor_uses_side_specific_state_bit(self) -> None:
        for state in range(256):
            self.state.value = state
            self.selector.value = 0
            self.assertEqual(self.selected_accessor(), (state >> 5) & 1)
            self.selector.value = 1
            self.assertEqual(self.selected_accessor(), (state >> 4) & 1)
            self.selector.value = 0xFFFFFFFF
            self.assertEqual(self.selected_accessor(), (state >> 4) & 1)

    def test_publish_selects_template_without_diagnostics(self) -> None:
        for selector, expected6, expected5 in (
            (0, 0, 1),
            (1, 1, 0),
            (0xFFFFFFFF, 1, 0),
        ):
            self.reset()
            self.available.value = 1
            self.selector.value = selector
            self.publish()
            self.assertEqual(self.template6_calls.value, expected6)
            self.assertEqual(self.template5_calls.value, expected5)
            self.assertEqual(self.log_level_calls.value, 0)
            self.assertEqual(self.log_calls.value, 0)
            self.assertEqual(self.trace_calls.value, 0)

    def test_unavailable_structured_and_primary_trace_metadata(self) -> None:
        self.reset()
        self.log_levels[:] = [3, 1, 0, 0]
        self.publish()

        self.assertEqual(self.template6_calls.value, 0)
        self.assertEqual(self.template5_calls.value, 0)
        self.assertEqual(self.log_level_calls.value, 2)
        self.assertEqual(self.log_calls.value, 1)
        self.assertEqual(self.trace_calls.value, 1)
        self.assertEqual(self.log_severity.value, 4)
        self.assertEqual(self.log_module.value, 0x0078C908)
        self.assertEqual(self.log_file.value, 0x0070874C)
        self.assertEqual(self.log_function.value, 0x00774774)
        self.assertEqual(self.log_line.value, 0xFD)
        self.assertEqual(self.log_identity.value, 0x00730CFC)
        self.assertEqual(self.trace_event.value, 0x10000000)
        self.assertEqual(self.trace_identity.value, 0x00711C64)

    def test_unavailable_trace_fallback_rereads_level(self) -> None:
        self.reset()
        self.log_levels[:] = [0, 0, 4, 0]
        self.publish()
        self.assertEqual(self.log_level_calls.value, 3)
        self.assertEqual(self.log_calls.value, 0)
        self.assertEqual(self.trace_calls.value, 1)

        self.reset()
        self.log_levels[:] = [0, 0, 0, 0]
        self.publish()
        self.assertEqual(self.log_level_calls.value, 3)
        self.assertEqual(self.trace_calls.value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ce094bbbc618e2c43f27fc4b7516edd3f148f6c25bcfb4c21dd68f3b115eb4f2",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "15aa606cd63333dee60dfe55fdd820dd07721d95ce09a085958c58491352e90b",
        )


if __name__ == "__main__":
    unittest.main()
