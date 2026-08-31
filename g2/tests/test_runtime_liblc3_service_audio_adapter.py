# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/shared/liblc3"
UPSTREAM = ROOT / "third_party/liblc3"
FIXTURE = ROOT / "tests/fixtures/runtime_liblc3_service_audio_adapter_host.c"
ADAPTER_C = COMPONENT / "runtime_liblc3_service_audio_adapter.c"
ADAPTER_H = COMPONENT / "runtime_liblc3_service_audio_adapter.h"
PROVIDER_C = COMPONENT / "runtime_liblc3_encoder_provider.c"
TARGET_COMPAT = COMPONENT / "target_compat"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
ENCODER_SOURCES = tuple(
    UPSTREAM_SRC / f"{name}.c"
    for name in (
        "attdet", "bits", "bwdet", "energy", "lc3", "ltpf", "mdct",
        "sns", "spec", "tables", "tns",
    )
)
TARGET_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffast-math",
    "-fshort-enums", "-ffreestanding", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
    "-Werror",
)
ADAPTER_ROOTS = (
    "open_cfw_liblc3_service_audio_state_init",
    "open_cfw_liblc3_service_audio_open",
    "open_cfw_liblc3_service_audio_encode",
    "open_cfw_liblc3_service_audio_close",
)
EXPECTED_RUNTIME_IMPORTS = {
    "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf", "fmaxf",
    "fminf", "memcpy", "memmove", "memset", "roundf", "sqrtf",
    "truncf",
}


class ProviderConfig(ctypes.Structure):
    _fields_ = [
        ("frame_us", ctypes.c_uint32),
        ("sample_rate_hz", ctypes.c_uint32),
        ("pcm_sample_rate_hz", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
        ("pcm_format", ctypes.c_uint32),
        ("pcm_stride", ctypes.c_uint32),
    ]


class ProviderPlan(ctypes.Structure):
    _fields_ = [
        ("encoded_samples_per_frame", ctypes.c_uint32),
        ("pcm_samples_per_frame", ctypes.c_uint32),
        ("frame_bytes", ctypes.c_uint32),
        ("encoder_bytes", ctypes.c_uint32),
        ("pcm_frame_bytes", ctypes.c_uint32),
        ("pcm_sample_bytes", ctypes.c_uint32),
        ("storage_alignment", ctypes.c_uint32),
    ]


class Provider(ctypes.Structure):
    _fields_ = [
        ("initialized_seal", ctypes.c_uint32),
        ("encoder", ctypes.c_void_p),
        ("storage_size", ctypes.c_uint32),
        ("config", ProviderConfig),
        ("plan", ProviderPlan),
    ]


class ServiceConfig(ctypes.Structure):
    _fields_ = [
        ("pcm_format", ctypes.c_uint32),
        ("frame_us", ctypes.c_uint32),
        ("sample_rate_hz", ctypes.c_uint32),
        ("channels", ctypes.c_uint32),
        ("channel_offset", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
    ]


class ServicePlan(ctypes.Structure):
    _fields_ = [
        ("pcm_samples_per_frame", ctypes.c_uint32),
        ("frame_bytes", ctypes.c_uint32),
        ("pcm_sample_bytes", ctypes.c_uint32),
        ("interleaved_input_frame_bytes", ctypes.c_uint32),
        ("encoder_storage_bytes", ctypes.c_uint32),
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


class RuntimeLiblc3ServiceAudioAdapterTests(unittest.TestCase):
    OK = 0
    INVALID = -1
    CORRUPT = -2
    NOT_OPEN = -3
    WRONG_OWNER = -4
    ALREADY_OPEN = -5
    BUSY = -6
    UNSUPPORTED = -7
    INPUT_GEOMETRY = -8
    OUTPUT_TOO_SMALL = -9
    PROVIDER_ERROR = -10
    OVERLAP = -12
    OWNER = 0x13579BDF

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        cls.nm = (shutil.which("llvm-nm") or
                  "/opt/homebrew/opt/llvm@22/bin/llvm-nm")
        cls.lld = shutil.which("ld.lld")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required")
        cls.tmp = tempfile.TemporaryDirectory(
            prefix="opencfw-liblc3-service-audio-")
        library = Path(cls.tmp.name) / (
            "service-audio.dylib" if sys.platform == "darwin"
            else "service-audio.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(UPSTREAM_INCLUDE), "-I", str(COMPONENT), str(FIXTURE),
        ]
        command += (["-dynamiclib", "-o", str(library)]
                    if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))

        cls.state_init = cls.lib.open_cfw_liblc3_service_audio_state_init
        cls.state_init.argtypes = [ctypes.POINTER(ServiceState)]
        cls.state_init.restype = ctypes.c_int
        cls.open = cls.lib.open_cfw_liblc3_service_audio_open
        cls.open.argtypes = [ctypes.POINTER(ServiceState), ctypes.c_uint32,
                             ctypes.POINTER(ServiceConfig),
                             ctypes.POINTER(ServicePlan)]
        cls.open.restype = ctypes.c_int
        cls.query_plan = cls.lib.open_cfw_liblc3_service_audio_query_plan
        cls.query_plan.argtypes = [ctypes.POINTER(ServiceState),
                                   ctypes.c_uint32,
                                   ctypes.POINTER(ServicePlan)]
        cls.query_plan.restype = ctypes.c_int
        cls.snapshot = cls.lib.open_cfw_liblc3_service_audio_snapshot
        cls.snapshot.argtypes = [ctypes.POINTER(ServiceState), ctypes.c_uint32,
                                 ctypes.POINTER(ServiceConfig),
                                 ctypes.POINTER(ServicePlan)]
        cls.snapshot.restype = ctypes.c_int
        cls.encode = cls.lib.open_cfw_liblc3_service_audio_encode
        cls.encode.argtypes = [ctypes.POINTER(ServiceState), ctypes.c_uint32,
                               ctypes.c_void_p, ctypes.c_size_t,
                               ctypes.c_void_p, ctypes.c_size_t,
                               ctypes.POINTER(ctypes.c_size_t)]
        cls.encode.restype = ctypes.c_int
        cls.close = cls.lib.open_cfw_liblc3_service_audio_close
        cls.close.argtypes = [ctypes.POINTER(ServiceState), ctypes.c_uint32]
        cls.close.restype = ctypes.c_int

        cls.reset = cls.lib.fixture_service_audio_reset
        cls.fail_call = cls.lib.fixture_service_audio_fail_call
        cls.fail_call.argtypes = [ctypes.c_uint32]
        cls.set_encoder_bytes = cls.lib.fixture_service_audio_set_encoder_bytes
        cls.set_encoder_bytes.argtypes = [ctypes.c_uint32]
        cls.set_setup_status = cls.lib.fixture_service_audio_set_setup_status
        cls.set_setup_status.argtypes = [ctypes.c_int]
        cls.call_count = cls.lib.fixture_service_audio_call_count
        cls.call_count.restype = ctypes.c_uint32
        cls.setup_storage = cls.lib.fixture_service_audio_setup_storage
        cls.setup_storage.restype = ctypes.c_size_t
        cls.setup_storage_size = cls.lib.fixture_service_audio_setup_storage_size
        cls.setup_storage_size.restype = ctypes.c_size_t
        for name in ("pcm", "output"):
            call = getattr(cls.lib, f"fixture_service_audio_call_{name}")
            call.argtypes = [ctypes.c_uint32]
            call.restype = ctypes.c_size_t
        for name in ("pcm_bytes", "output_size"):
            call = getattr(cls.lib, f"fixture_service_audio_call_{name}")
            call.argtypes = [ctypes.c_uint32]
            call.restype = ctypes.c_size_t
        cls.lib.fixture_service_audio_call_stride.argtypes = [ctypes.c_uint32]
        cls.lib.fixture_service_audio_call_stride.restype = ctypes.c_uint32
        for name in ("state_size", "state_alignment", "config_word_offset",
                     "owner_offset", "storage_offset"):
            call = getattr(cls.lib, f"fixture_service_audio_{name}")
            call.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.reset()

    @staticmethod
    def config(**overrides: int) -> ServiceConfig:
        values = {
            "pcm_format": 0,
            "frame_us": 10_000,
            "sample_rate_hz": 16_000,
            "channels": 2,
            "channel_offset": 1,
            "bitrate_bps": 32_000,
        }
        values.update(overrides)
        return ServiceConfig(**values)

    @staticmethod
    def new_state(phase_mod8: int = 4) -> ServiceState:
        if phase_mod8 not in (0, 4):
            raise ValueError("stock-slot phase must be zero or four mod eight")
        backing = (ctypes.c_uint8 * (ctypes.sizeof(ServiceState) + 8))()
        offset = (phase_mod8 - (ctypes.addressof(backing) & 7)) & 7
        state = ServiceState.from_buffer(backing, offset)
        state._stock_slot_backing = backing
        if ctypes.addressof(state) & 7 != phase_mod8:
            raise AssertionError("stock-slot state phase is incorrect")
        return state

    def opened(self, config: ServiceConfig | None = None
               ) -> tuple[ServiceState, ServicePlan]:
        state = self.new_state()
        plan = ServicePlan()
        actual = config or self.config()
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                                   ctypes.byref(actual), ctypes.byref(plan)),
                         self.OK)
        return state, plan

    def test_exact_host_abi_and_arm32_geometry_contract(self) -> None:
        self.assertEqual(ctypes.sizeof(ServiceConfig), 24)
        self.assertEqual(ctypes.sizeof(ServicePlan), 20)
        self.assertEqual(ctypes.sizeof(Provider), 72)
        self.assertEqual(self.lib.fixture_service_audio_state_size(),
                         ctypes.sizeof(ServiceState))
        self.assertEqual(self.lib.fixture_service_audio_state_alignment(), 4)
        self.assertEqual(self.lib.fixture_service_audio_owner_offset(), 4)
        self.assertEqual(self.lib.fixture_service_audio_config_word_offset(), 12)
        self.assertEqual(self.lib.fixture_service_audio_storage_offset(), 28)
        self.assertEqual(ctypes.sizeof(ServiceState), 2628)
        source = ADAPTER_C.read_text(encoding="utf-8")
        self.assertIn("storage) == 28U", source)
        self.assertIn("state) == 2628U", source)

    def test_lifetime_requires_pristine_control_and_cannot_reset_owner(self) -> None:
        raw = (ctypes.c_uint8 * (ctypes.sizeof(ServiceState) + 8))()
        misaligned = ctypes.cast(ctypes.addressof(raw) + 1,
                                 ctypes.POINTER(ServiceState))
        self.assertEqual(self.state_init(misaligned), self.INVALID)
        dirty = self.new_state()
        dirty.owner_token = 1
        self.assertEqual(self.state_init(ctypes.byref(dirty)), self.CORRUPT)

        state = self.new_state()
        state.storage[2599] = 0xA5
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
        self.assertEqual(state.storage[2599], 0xA5)
        generation = state.generation
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
        self.assertEqual(state.generation, generation)
        config = self.config()
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                                   ctypes.byref(config), None), self.OK)
        self.assertEqual(self.state_init(ctypes.byref(state)),
                         self.ALREADY_OPEN)
        self.assertEqual(state.owner_token, self.OWNER)
        self.assertEqual(self.close(ctypes.byref(state), self.OWNER), self.OK)
        self.assertEqual(state.storage[2599], 0xA5)
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)

    def test_open_publishes_exact_stock_geometry_and_ownership(self) -> None:
        state = self.new_state()
        config = self.config()
        plan = ServicePlan()
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                                   ctypes.byref(config), ctypes.byref(plan)),
                         self.CORRUPT)
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
        self.assertEqual(self.open(ctypes.byref(state), 0,
                                   ctypes.byref(config), ctypes.byref(plan)),
                         self.INVALID)
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                                   ctypes.byref(config), ctypes.byref(plan)),
                         self.OK)
        self.assertEqual((plan.pcm_samples_per_frame, plan.frame_bytes,
                          plan.pcm_sample_bytes,
                          plan.interleaved_input_frame_bytes,
                          plan.encoder_storage_bytes),
                         (160, 40, 2, 640, 1200))
        self.assertEqual(state.config_word, 0x4C33001C)
        self.assertEqual((state.channels, state.channel_offset,
                          state.bitrate_bps), (2, 1, 32_000))
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                                   ctypes.byref(config), None),
                         self.ALREADY_OPEN)
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER ^ 1,
                                   ctypes.byref(config), None),
                         self.WRONG_OWNER)
        self.assertEqual(self.close(ctypes.byref(state), self.OWNER ^ 1),
                         self.WRONG_OWNER)
        self.assertEqual(self.close(ctypes.byref(state), self.OWNER), self.OK)
        self.assertEqual(self.close(ctypes.byref(state), self.OWNER),
                         self.NOT_OPEN)

    def test_two_interleaved_frames_select_channel_and_advance_exactly(self) -> None:
        state, plan = self.opened()
        pcm = (ctypes.c_uint8 * (2 * plan.interleaved_input_frame_bytes))()
        output = (ctypes.c_uint8 * (2 * plan.frame_bytes))()
        output_bytes = ctypes.c_size_t(0xFFFFFFFF)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(output_bytes)), self.OK)
        self.assertEqual(output_bytes.value, 80)
        self.assertEqual(self.call_count(), 2)
        for index in range(2):
            self.assertEqual(self.lib.fixture_service_audio_call_pcm(index),
                ctypes.addressof(pcm) + 2 + index * 640)
            self.assertEqual(
                self.lib.fixture_service_audio_call_pcm_bytes(index), 638)
            self.assertEqual(self.lib.fixture_service_audio_call_output(index),
                ctypes.addressof(output) + index * 40)
            self.assertEqual(
                self.lib.fixture_service_audio_call_output_size(index), 40)
            self.assertEqual(
                self.lib.fixture_service_audio_call_stride(index), 2)
        self.assertNotEqual(bytes(output), bytes(ctypes.sizeof(output)))

    def test_all_four_stock_pcm_widths_and_mono_stride(self) -> None:
        for pcm_format, width in enumerate((2, 4, 3, 4)):
            with self.subTest(pcm_format=pcm_format):
                self.reset()
                config = self.config(pcm_format=pcm_format, channels=1,
                                     channel_offset=0)
                state, plan = self.opened(config)
                self.assertEqual(plan.pcm_sample_bytes, width)
                self.assertEqual(plan.interleaved_input_frame_bytes,
                                 160 * width)
                pcm = (ctypes.c_uint8 * plan.interleaved_input_frame_bytes)()
                output = (ctypes.c_uint8 * plan.frame_bytes)()
                output_bytes = ctypes.c_size_t()
                self.assertEqual(self.encode(ctypes.byref(state), self.OWNER,
                    pcm, ctypes.sizeof(pcm), output, ctypes.sizeof(output),
                    ctypes.byref(output_bytes)), self.OK)
                self.assertEqual(
                    self.lib.fixture_service_audio_call_stride(0), 1)
                self.assertEqual(self.lib.fixture_service_audio_call_pcm(0),
                                 ctypes.addressof(pcm))

    def test_complete_admitted_configuration_codes_round_trip(self) -> None:
        observed_words = set()
        for duration in (2500, 5000, 7500, 10000):
            for rate in (8000, 16000, 24000, 32000, 48000):
                for pcm_format in range(4):
                    with self.subTest(duration=duration, rate=rate,
                                      pcm_format=pcm_format):
                        self.reset()
                        config = self.config(
                            frame_us=duration, sample_rate_hz=rate,
                            pcm_format=pcm_format, channels=3,
                            channel_offset=2, bitrate_bps=64_000)
                        state = self.new_state()
                        plan = ServicePlan()
                        self.assertEqual(
                            self.state_init(ctypes.byref(state)), self.OK)
                        status = self.open(
                            ctypes.byref(state), self.OWNER,
                            ctypes.byref(config), ctypes.byref(plan))
                        if status == self.OK:
                            observed_words.add(state.config_word)
                            pcm = (ctypes.c_uint8 *
                                   plan.interleaved_input_frame_bytes)()
                            output = (ctypes.c_uint8 * plan.frame_bytes)()
                            produced = ctypes.c_size_t()
                            self.assertEqual(self.encode(
                                ctypes.byref(state), self.OWNER, pcm,
                                ctypes.sizeof(pcm), output,
                                ctypes.sizeof(output), ctypes.byref(produced)),
                                self.OK)
                            self.assertEqual(produced.value, plan.frame_bytes)
                            self.assertEqual(
                                self.lib.fixture_service_audio_call_stride(0),
                                3)
                        else:
                            self.assertEqual(status, self.UNSUPPORTED)
        self.assertEqual(len(observed_words), 80)

    def test_both_authenticated_address_phases_align_encoder_storage(self
            ) -> None:
        for phase, prefix, capacity in ((4, 0, 2600), (0, 4, 2596)):
            with self.subTest(phase=phase):
                self.reset()
                self.set_encoder_bytes(2596)
                state = self.new_state(phase)
                config = self.config()
                self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
                self.assertEqual(self.open(
                    ctypes.byref(state), self.OWNER,
                    ctypes.byref(config), None), self.OK)
                self.assertEqual(self.setup_storage() & 7, 0)
                self.assertEqual(
                    self.setup_storage(),
                    ctypes.addressof(state) + ServiceState.storage.offset +
                    prefix)
                self.assertEqual(self.setup_storage_size(), capacity)

    def test_real_provider_transient_view_preserves_encoder_lifetime(self
            ) -> None:
        library = Path(self.tmp.name) / (
            "service-audio-real.dylib" if sys.platform == "darwin"
            else "service-audio-real.so")
        command = [
            self.clang, "-std=c11", "-O2", "-ffast-math", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror",
            "-I", str(UPSTREAM_INCLUDE), "-I", str(UPSTREAM_SRC),
            "-I", str(COMPONENT), str(ADAPTER_C), str(PROVIDER_C),
            *(str(source) for source in ENCODER_SOURCES),
            str(UPSTREAM_SRC / "plc.c"),
        ]
        command += (["-dynamiclib", "-o", str(library)]
                    if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-lm", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        real = ctypes.CDLL(str(library))
        state_init = real.open_cfw_liblc3_service_audio_state_init
        state_init.argtypes = [ctypes.POINTER(ServiceState)]
        state_init.restype = ctypes.c_int
        open_call = real.open_cfw_liblc3_service_audio_open
        open_call.argtypes = [ctypes.POINTER(ServiceState), ctypes.c_uint32,
                              ctypes.POINTER(ServiceConfig),
                              ctypes.POINTER(ServicePlan)]
        open_call.restype = ctypes.c_int
        encode_call = real.open_cfw_liblc3_service_audio_encode
        encode_call.argtypes = [
            ctypes.POINTER(ServiceState), ctypes.c_uint32, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t)]
        encode_call.restype = ctypes.c_int

        outputs = []
        for phase in (4, 0):
            state = self.new_state(phase)
            config = self.config(channels=1, channel_offset=0)
            plan = ServicePlan()
            self.assertEqual(state_init(ctypes.byref(state)), self.OK)
            self.assertEqual(open_call(
                ctypes.byref(state), self.OWNER,
                ctypes.byref(config), ctypes.byref(plan)), self.OK)
            self.assertEqual(plan.encoder_storage_bytes, 2596)
            pcm = (ctypes.c_int16 * plan.pcm_samples_per_frame)(
                *(index * 97 - 7000
                  for index in range(plan.pcm_samples_per_frame)))
            output = (ctypes.c_uint8 * plan.frame_bytes)()
            produced = ctypes.c_size_t()
            self.assertEqual(encode_call(
                ctypes.byref(state), self.OWNER, pcm, ctypes.sizeof(pcm),
                output, ctypes.sizeof(output), ctypes.byref(produced)), self.OK)
            self.assertEqual(produced.value, plan.frame_bytes)
            outputs.append(bytes(output))
        self.assertEqual(outputs[0], outputs[1])
        self.assertNotEqual(outputs[0], bytes(len(outputs[0])))

        supported_encoder_sizes = []
        for duration in (2500, 5000, 7500, 10000):
            for rate in (8000, 16000, 24000, 32000, 48000):
                statuses = []
                sizes = []
                for phase in (4, 0):
                    state = self.new_state(phase)
                    config = self.config(
                        frame_us=duration, sample_rate_hz=rate,
                        channels=1, channel_offset=0, bitrate_bps=64_000)
                    plan = ServicePlan()
                    self.assertEqual(state_init(ctypes.byref(state)), self.OK)
                    statuses.append(open_call(
                        ctypes.byref(state), self.OWNER,
                        ctypes.byref(config), ctypes.byref(plan)))
                    sizes.append(plan.encoder_storage_bytes)
                with self.subTest(duration=duration, rate=rate):
                    self.assertEqual(statuses[0], statuses[1])
                    self.assertIn(statuses[0], (self.OK, self.UNSUPPORTED))
                    if statuses[0] == self.OK:
                        self.assertEqual(sizes[0], sizes[1])
                        supported_encoder_sizes.append(sizes[0])
        self.assertTrue(supported_encoder_sizes)
        self.assertEqual(max(supported_encoder_sizes), 2596)

    def test_open_rejects_unsupported_geometry_and_setup_failure(self) -> None:
        unsupported = (
            self.config(channels=0),
            self.config(channel_offset=2),
            self.config(pcm_format=4),
            self.config(frame_us=6_000),
            self.config(bitrate_bps=8_000),  # 10-byte stock frame floor.
        )
        for config in unsupported:
            values = tuple(getattr(config, name)
                           for name, _ in ServiceConfig._fields_)
            with self.subTest(config=values):
                state = self.new_state()
                self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
                self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
                    ctypes.byref(config), None), self.UNSUPPORTED)
                self.assertEqual(state.owner_token, 0)
        state = self.new_state()
        self.assertEqual(self.state_init(ctypes.byref(state)), self.OK)
        config = self.config()
        self.set_encoder_bytes(2601)
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
            ctypes.byref(config), None), self.UNSUPPORTED)
        self.set_encoder_bytes(1200)
        self.set_setup_status(-7)
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
            ctypes.byref(config), None), self.PROVIDER_ERROR)
        self.assertEqual((state.state_seal, state.owner_token),
                         (0x5341334C, 0))

    def test_input_output_bounds_are_transactional(self) -> None:
        state, plan = self.opened()
        pcm = (ctypes.c_uint8 * plan.interleaved_input_frame_bytes)()
        output = (ctypes.c_uint8 * plan.frame_bytes)()
        produced = ctypes.c_size_t(123)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm) - 1, output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.INPUT_GEOMETRY)
        self.assertEqual(produced.value, 0)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output) - 1,
            ctypes.byref(produced)), self.OUTPUT_TOO_SMALL)
        self.assertEqual(self.call_count(), 0)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm, 0,
            output, 0, ctypes.byref(produced)), self.OK)
        self.assertEqual((produced.value, self.call_count()), (0, 0))

    def test_plan_query_rederives_geometry_without_reinitializing(self) -> None:
        state, opened_plan = self.opened()
        generation = state.generation
        setup_storage = self.setup_storage()
        queried = ServicePlan()
        self.assertEqual(self.query_plan(
            ctypes.byref(state), self.OWNER, ctypes.byref(queried)), self.OK)
        self.assertEqual(bytes(queried), bytes(opened_plan))
        config = ServiceConfig()
        snapshot_plan = ServicePlan()
        self.assertEqual(self.snapshot(
            ctypes.byref(state), self.OWNER, ctypes.byref(config),
            ctypes.byref(snapshot_plan)), self.OK)
        self.assertEqual(bytes(config), bytes(self.config()))
        self.assertEqual(bytes(snapshot_plan), bytes(opened_plan))
        self.assertEqual(state.generation, generation)
        self.assertEqual(self.setup_storage(), setup_storage)
        self.assertEqual(self.query_plan(
            ctypes.byref(state), self.OWNER ^ 1, ctypes.byref(queried)),
            self.WRONG_OWNER)
        alias = ctypes.cast(
            ctypes.byref(state, ServiceState.storage.offset),
            ctypes.POINTER(ServicePlan))
        self.assertEqual(self.query_plan(
            ctypes.byref(state), self.OWNER, alias), self.OVERLAP)

    def test_provider_failure_reports_prefix_and_invalidates_lifetime(self) -> None:
        state, plan = self.opened()
        pcm = (ctypes.c_uint8 * (2 * plan.interleaved_input_frame_bytes))()
        output = (ctypes.c_uint8 * (2 * plan.frame_bytes))()
        produced = ctypes.c_size_t()
        generation = state.generation
        self.fail_call(2)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.PROVIDER_ERROR)
        self.assertEqual((produced.value, self.call_count()), (40, 2))
        self.assertEqual((state.state_seal, state.owner_token),
                         (0x5341334C, 0))
        self.assertGreater(state.generation, generation)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.NOT_OPEN)
        self.fail_call(0)
        config = self.config()
        self.assertEqual(self.open(ctypes.byref(state), self.OWNER,
            ctypes.byref(config), None), self.OK)

    def test_busy_wrong_owner_and_tampered_state_fail_before_provider(self) -> None:
        state, plan = self.opened()
        pcm = (ctypes.c_uint8 * plan.interleaved_input_frame_bytes)()
        output = (ctypes.c_uint8 * plan.frame_bytes)()
        produced = ctypes.c_size_t(1)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER ^ 1, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.WRONG_OWNER)
        state.state_seal |= 0x80000000
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.BUSY)
        self.assertEqual(self.close(ctypes.byref(state), self.OWNER), self.BUSY)
        state.state_seal &= 0x7FFFFFFF
        state.config_word ^= 1 << 2
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output),
            ctypes.byref(produced)), self.CORRUPT)
        self.assertEqual(self.call_count(), 0)

        state2, plan2 = self.opened()
        pcm2 = (ctypes.c_uint8 * plan2.interleaved_input_frame_bytes)()
        output2 = (ctypes.c_uint8 * plan2.frame_bytes)()
        state2.bitrate_bps += 1
        self.assertEqual(self.encode(ctypes.byref(state2), self.OWNER, pcm2,
            ctypes.sizeof(pcm2), output2, ctypes.sizeof(output2),
            ctypes.byref(produced)), self.CORRUPT)
        self.assertEqual(self.call_count(), 0)

    def test_all_boundary_aliases_fail_without_mutating_owned_state(self) -> None:
        state, plan = self.opened()
        pcm = (ctypes.c_uint8 * plan.interleaved_input_frame_bytes)()
        output = (ctypes.c_uint8 * plan.frame_bytes)()
        produced = ctypes.c_size_t(77)
        seal = state.state_seal

        state_size_out = ctypes.cast(ctypes.byref(state),
                                     ctypes.POINTER(ctypes.c_size_t))
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output), state_size_out),
            self.OVERLAP)
        self.assertEqual(state.state_seal, seal)
        pcm_size_out = ctypes.cast(pcm, ctypes.POINTER(ctypes.c_size_t))
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output), pcm_size_out),
            self.OVERLAP)
        output_size_out = ctypes.cast(output, ctypes.POINTER(ctypes.c_size_t))
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), output, ctypes.sizeof(output), output_size_out),
            self.OVERLAP)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER,
            ctypes.byref(state), ctypes.sizeof(pcm), output,
            ctypes.sizeof(output), ctypes.byref(produced)), self.OVERLAP)
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, pcm,
            ctypes.sizeof(pcm), ctypes.byref(state), ctypes.sizeof(output),
            ctypes.byref(produced)), self.OVERLAP)
        shared = (ctypes.c_uint8 * plan.interleaved_input_frame_bytes)()
        self.assertEqual(self.encode(ctypes.byref(state), self.OWNER, shared,
            ctypes.sizeof(shared), shared, plan.frame_bytes,
            ctypes.byref(produced)), self.OVERLAP)
        self.assertEqual(self.call_count(), 0)

        closed = self.new_state()
        self.assertEqual(self.state_init(ctypes.byref(closed)), self.OK)
        alias_config = ctypes.cast(
            ctypes.byref(closed, ServiceState.config_word.offset),
            ctypes.POINTER(ServiceConfig))
        self.assertEqual(self.open(ctypes.byref(closed), self.OWNER,
            alias_config, None), self.OVERLAP)
        config = self.config()
        alias_plan = ctypes.cast(
            ctypes.byref(closed, ServiceState.storage.offset),
            ctypes.POINTER(ServicePlan))
        self.assertEqual(self.open(ctypes.byref(closed), self.OWNER,
            ctypes.byref(config), alias_plan), self.OVERLAP)
        self.assertEqual(closed.owner_token, 0)

    def test_cortex_m55_full_encoder_link_and_deterministic_adapter_object(self
            ) -> None:
        profiles = [Path("/usr/bin/clang"),
                    Path("/opt/homebrew/opt/llvm@22/bin/clang")]
        profiles = [path for path in profiles if path.is_file()]
        if not profiles or self.lld is None or not Path(self.nm).is_file():
            self.skipTest("reviewed Cortex-M55 compilers, llvm-nm, and lld required")
        for compiler in profiles:
            with self.subTest(compiler=str(compiler)):
                profile_dir = Path(self.tmp.name) / compiler.name
                if profile_dir.exists():
                    profile_dir = Path(self.tmp.name) / f"{compiler.name}-22"
                profile_dir.mkdir()
                objects: list[Path] = []
                sources = (ADAPTER_C, PROVIDER_C, *ENCODER_SOURCES)
                for index, source in enumerate(sources):
                    output = profile_dir / f"{index:02d}-{source.stem}.o"
                    subprocess.run([
                        str(compiler), *TARGET_FLAGS,
                        "-I", str(TARGET_COMPAT),
                        "-I", str(UPSTREAM_INCLUDE),
                        "-I", str(UPSTREAM_SRC),
                        "-I", str(COMPONENT),
                        "-c", str(source), "-o", str(output),
                    ], check=True, capture_output=True, text=True)
                    objects.append(output)
                repeat = profile_dir / "adapter-repeat.o"
                subprocess.run([
                    str(compiler), *TARGET_FLAGS,
                    "-I", str(TARGET_COMPAT),
                    "-I", str(UPSTREAM_INCLUDE),
                    "-I", str(UPSTREAM_SRC),
                    "-I", str(COMPONENT),
                    "-c", str(ADAPTER_C), "-o", str(repeat),
                ], check=True, capture_output=True, text=True)
                self.assertEqual(objects[0].read_bytes(), repeat.read_bytes())
                self.assertLess(objects[0].stat().st_size, 8_000)
                self.assertEqual(len(hashlib.sha256(
                    objects[0].read_bytes()).hexdigest()), 64)

                linked = profile_dir / "service-audio-retained.o"
                subprocess.run([
                    self.lld, "-m", "armelf", "-r", "--gc-sections",
                    f"--entry={ADAPTER_ROOTS[0]}",
                    *(f"--undefined={root}" for root in ADAPTER_ROOTS),
                    "-o", str(linked), *(str(obj) for obj in objects),
                ], check=True, capture_output=True, text=True)
                symbols = subprocess.run(
                    [self.nm, str(linked)], check=True, capture_output=True,
                    text=True).stdout
                undefined = set(re.findall(r"^\s+U\s+(\S+)$", symbols, re.M))
                self.assertEqual(undefined, EXPECTED_RUNTIME_IMPORTS)
                for root in ADAPTER_ROOTS:
                    self.assertIsNotNone(
                        re.search(rf"\b{root}$", symbols, re.M))
                self.assertLess(linked.stat().st_size, 200_000)

    def test_boundary_scope_and_license_are_explicit(self) -> None:
        source = ADAPTER_C.read_text(encoding="utf-8")
        header = ADAPTER_H.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", source)
        self.assertIn("SPDX-License-Identifier: MIT", header)
        self.assertIn("single-executor", header)
        self.assertIn("storage itself need not be cleared", header)
        self.assertNotIn("overlay", source + header)
        self.assertNotIn("hardware", source + header)


if __name__ == "__main__":
    unittest.main()
