# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/shared/liblc3"
UPSTREAM_INCLUDE = ROOT / "third_party/liblc3/include"
FIXTURE = ROOT / "tests/fixtures/runtime_liblc3_service_audio_stock_shim_host.c"


class ServiceConfig(ctypes.Structure):
    _fields_ = [
        ("pcm_format", ctypes.c_uint32),
        ("frame_us", ctypes.c_uint32),
        ("sample_rate_hz", ctypes.c_uint32),
        ("channels", ctypes.c_uint32),
        ("channel_offset", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
    ]


class ServiceState(ctypes.Structure):
    _fields_ = [
        ("state_seal", ctypes.c_uint32),
        ("owner_token", ctypes.c_uint32),
        ("generation", ctypes.c_uint32),
        ("config_word", ctypes.c_uint32),
        ("channels", ctypes.c_uint32),
        ("channel_offset", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
        ("storage", ctypes.c_uint8 * 2600),
    ]


class StockServiceAudioShimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            raise unittest.SkipTest("Clang is required")
        cls.tmp = tempfile.TemporaryDirectory(prefix="opencfw-lc3-stock-shim-")
        library = Path(cls.tmp.name) / (
            "stock-shim.dylib" if sys.platform == "darwin" else "stock-shim.so")
        command = [
            clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(UPSTREAM_INCLUDE), "-I", str(COMPONENT), str(FIXTURE),
        ]
        command += (["-dynamiclib", "-o", str(library)] if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.reset = cls.lib.fixture_stock_reset
        cls.context_address = cls.lib.fixture_stock_context_address
        cls.context_address.argtypes = [ctypes.c_uint32]
        cls.context_address.restype = ctypes.c_size_t
        cls.configure = cls.lib.fixture_stock_configure
        cls.configure.argtypes = [ctypes.c_uint32, ctypes.POINTER(ServiceConfig)]
        cls.copy_header = cls.lib.fixture_stock_copy_header
        cls.copy_header.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.setup = cls.lib.open_cfw_liblc3_service_audio_stock_setup
        cls.setup.argtypes = [ctypes.c_void_p]
        cls.encode = cls.lib.open_cfw_liblc3_service_audio_stock_encode
        cls.encode.argtypes = [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int32), ctypes.c_void_p,
        ]
        cls.encode.restype = ctypes.c_int32
        cls.call_count = cls.lib.fixture_service_audio_call_count
        cls.call_count.restype = ctypes.c_uint32
        cls.setup_storage_size = cls.lib.fixture_service_audio_setup_storage_size
        cls.setup_storage_size.restype = ctypes.c_size_t
        cls.setup_call_count = cls.lib.fixture_service_audio_setup_call_count
        cls.setup_call_count.restype = ctypes.c_uint32
        cls.fail_call = cls.lib.fixture_service_audio_fail_call
        cls.fail_call.argtypes = [ctypes.c_uint32]
        cls.set_setup_status = cls.lib.fixture_service_audio_set_setup_status
        cls.set_setup_status.argtypes = [ctypes.c_int]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.reset()

    @staticmethod
    def config(**overrides: int) -> ServiceConfig:
        values = dict(pcm_format=0, frame_us=10_000, sample_rate_hz=16_000,
                      channels=2, channel_offset=1, bitrate_bps=32_000)
        values.update(overrides)
        return ServiceConfig(**values)

    def context(self, index: int) -> int:
        return self.context_address(index)

    def configure_context(self, index: int, config: ServiceConfig | None = None
                          ) -> ServiceConfig:
        actual = config or self.config()
        self.configure(index, ctypes.byref(actual))
        return actual

    def state(self, index: int) -> ServiceState:
        return ServiceState.from_address(self.context(index))

    def header(self, index: int) -> bytes:
        result = (ctypes.c_uint8 * 28)()
        self.copy_header(index, result)
        return bytes(result)

    def test_all_four_exact_slots_transition_and_explicit_setup_resets(self) -> None:
        for index, capacity in enumerate((2600, 2596, 2600, 2596)):
            with self.subTest(index=index):
                self.reset()
                self.configure_context(index)
                context = self.context(index)
                self.setup(context)
                state = self.state(index)
                self.assertEqual(state.owner_token, 0x4C430001 + index)
                self.assertNotEqual(state.state_seal, 0)
                self.assertEqual(self.setup_storage_size(), capacity)
                generation = state.generation
                self.setup(context)
                self.assertGreater(state.generation, generation)
                self.assertEqual(self.setup_storage_size(), capacity)
                self.assertEqual(self.setup_call_count(), 2)

    def test_lazy_transition_and_stock_encode_result_geometry(self) -> None:
        self.configure_context(2)
        pcm = (ctypes.c_uint8 * 1280)()
        output = (ctypes.c_uint8 * 80)()
        produced = ctypes.c_int32(-77)
        self.assertEqual(self.encode(
            pcm, len(pcm), output, ctypes.byref(produced), self.context(2)), 0)
        self.assertEqual(produced.value, 80)
        self.assertEqual(self.call_count(), 2)
        self.assertEqual(self.setup_call_count(), 1)
        self.assertEqual(self.state(2).owner_token, 0x4C430003)

    def test_zero_frames_succeed_and_invalid_geometry_preserves_count(self) -> None:
        self.configure_context(0)
        pcm = (ctypes.c_uint8 * 640)()
        output = (ctypes.c_uint8 * 40)()
        produced = ctypes.c_int32(123)
        self.assertEqual(self.encode(
            pcm, 639, output, ctypes.byref(produced), self.context(0)), -1)
        self.assertEqual(produced.value, 123)
        self.assertEqual(self.encode(
            pcm, 0, output, ctypes.byref(produced), self.context(0)), 0)
        self.assertEqual(produced.value, 0)

    def test_unsupported_or_setup_failure_restores_stock_header_for_retry(self
            ) -> None:
        invalid = self.configure_context(1, self.config(frame_us=6000))
        expected = bytes(invalid) + bytes(4)
        self.setup(self.context(1))
        self.assertEqual(self.header(1), expected)

        self.reset()
        valid = self.configure_context(1)
        expected = bytes(valid) + bytes(4)
        self.set_setup_status(-7)
        self.setup(self.context(1))
        self.assertEqual(self.header(1), expected)
        self.set_setup_status(0)
        self.setup(self.context(1))
        self.assertEqual(self.state(1).owner_token, 0x4C430002)

    def test_unknown_context_nulls_and_aliases_fail_closed(self) -> None:
        self.configure_context(0)
        pcm = (ctypes.c_uint8 * 640)()
        output = (ctypes.c_uint8 * 40)()
        produced = ctypes.c_int32(71)
        unknown = ctypes.addressof(pcm)
        self.setup(unknown)
        self.assertEqual(self.encode(
            pcm, len(pcm), output, ctypes.byref(produced), unknown), -1)
        self.assertEqual(produced.value, 71)
        self.assertEqual(self.encode(
            None, len(pcm), output, ctypes.byref(produced), self.context(0)), -1)
        alias_count = ctypes.cast(self.context(0), ctypes.POINTER(ctypes.c_int32))
        self.assertEqual(self.encode(
            pcm, len(pcm), output, alias_count, self.context(0)), -1)
        shared = (ctypes.c_uint8 * 640)()
        self.assertEqual(self.encode(
            shared, len(shared), shared, ctypes.byref(produced), self.context(0)), -1)

    def test_tampered_compact_state_is_not_reclassified_as_stock_header(self
            ) -> None:
        self.configure_context(3)
        self.setup(self.context(3))
        state = self.state(3)
        generation = state.generation
        state.state_seal ^= 0x40
        produced = ctypes.c_int32(55)
        pcm = (ctypes.c_uint8 * 640)()
        output = (ctypes.c_uint8 * 40)()
        self.assertEqual(self.encode(
            pcm, len(pcm), output, ctypes.byref(produced), self.context(3)), -1)
        self.assertEqual(produced.value, 55)
        self.assertEqual(state.generation, generation)

    def test_provider_failure_returns_completed_prefix_then_invalidates(self
            ) -> None:
        self.configure_context(0)
        pcm = (ctypes.c_uint8 * 1280)()
        output = (ctypes.c_uint8 * 80)()
        produced = ctypes.c_int32(-1)
        self.fail_call(2)
        self.assertEqual(self.encode(
            pcm, len(pcm), output, ctypes.byref(produced), self.context(0)), -1)
        self.assertEqual(produced.value, 40)
        self.fail_call(0)
        self.assertEqual(self.encode(
            pcm, len(pcm), output, ctypes.byref(produced), self.context(0)), -1)
        self.assertEqual(produced.value, 40)


if __name__ == "__main__":
    unittest.main()
