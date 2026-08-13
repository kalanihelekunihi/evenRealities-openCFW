from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_emit_span.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_emit_span_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482684
STOCK_END = 0x004826B2


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeEmitContext(ctypes.Structure):
    _fields_ = [
        ("reserved_00", ctypes.c_uint32),
        ("reserved_04", ctypes.c_uint32),
        ("output_state", ctypes.c_uint32),
        ("reserved_0c", ctypes.c_uint32),
        ("reserved_10", ctypes.c_uint32),
        ("reserved_14", ctypes.c_uint32),
        ("reserved_18", ctypes.c_uint32),
        ("reserved_1c", ctypes.c_uint32),
        ("reserved_20", ctypes.c_uint32),
        ("reserved_24", ctypes.c_uint32),
        ("reserved_28", ctypes.c_uint32),
        ("emitted_count", ctypes.c_uint32),
    ]


class RuntimeEmitSpanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_emit_span.dylib"
            if sys.platform == "darwin"
            else "runtime_emit_span.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)

        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_emit_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_emit_execute
        cls.execute.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
        ]
        cls.execute.restype = ctypes.c_int
        cls.context = RuntimeEmitContext.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_context",
        )
        cls.calls = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_calls",
        )
        cls.states = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_states",
        )
        cls.values = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_values",
        )
        cls.results = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_results",
        )
        cls.result_count = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_emit_result_count",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(
        self,
        *,
        source: bytes,
        initial_state: int,
        initial_count: int,
        results: list[int],
    ) -> tuple[int, list[int], list[int]]:
        self.reset(initial_state, initial_count)
        self.assertLessEqual(len(results), 256)
        for index, result in enumerate(results):
            self.results[index] = result
        self.result_count.value = len(results)

        buffer = (ctypes.c_ubyte * len(source)).from_buffer_copy(source)
        status = self.execute(buffer, len(source))
        calls = self.calls.value
        return (
            status,
            list(self.states[:calls]),
            list(self.values[:calls]),
        )

    def assert_reserved_fields_unchanged(self) -> None:
        self.assertEqual(self.context.reserved_00, 0x00000000)
        self.assertEqual(self.context.reserved_04, 0x04040404)
        self.assertEqual(self.context.reserved_0c, 0x0C0C0C0C)
        self.assertEqual(self.context.reserved_10, 0x10101010)
        self.assertEqual(self.context.reserved_14, 0x14141414)
        self.assertEqual(self.context.reserved_18, 0x18181818)
        self.assertEqual(self.context.reserved_1c, 0x1C1C1C1C)
        self.assertEqual(self.context.reserved_20, 0x20202020)
        self.assertEqual(self.context.reserved_24, 0x24242424)
        self.assertEqual(self.context.reserved_28, 0x28282828)

    def test_zero_length_is_an_exact_no_callback_identity(self) -> None:
        self.reset(0x12345678, 0x89ABCDEF)
        status = self.execute(None, 0)
        self.assertEqual(status, 0)
        self.assertEqual(self.calls.value, 0)
        self.assertEqual(self.context.output_state, 0x12345678)
        self.assertEqual(self.context.emitted_count, 0x89ABCDEF)
        self.assert_reserved_fields_unchanged()

    def test_every_byte_is_zero_extended_and_state_is_threaded(self) -> None:
        source = bytes((0x00, 0x7F, 0x80, 0xFF, 0x41))
        results = [0x80000000, 0xFFFFFFFF, 1, 0x12345678, 9]
        status, states, values = self.run_case(
            source=source,
            initial_state=0xDEADBEEF,
            initial_count=7,
            results=results,
        )
        self.assertEqual(status, 0)
        self.assertEqual(
            states,
            [0xDEADBEEF, 0x80000000, 0xFFFFFFFF, 1, 0x12345678],
        )
        self.assertEqual(values, list(source))
        self.assertEqual(self.context.output_state, 9)
        self.assertEqual(self.context.emitted_count, 12)
        self.assert_reserved_fields_unchanged()

    def test_first_callback_failure_stores_zero_without_counting(self) -> None:
        status, states, values = self.run_case(
            source=b"abc",
            initial_state=0x10203040,
            initial_count=11,
            results=[0],
        )
        self.assertEqual(status, -1)
        self.assertEqual(states, [0x10203040])
        self.assertEqual(values, [ord("a")])
        self.assertEqual(self.context.output_state, 0)
        self.assertEqual(self.context.emitted_count, 11)
        self.assert_reserved_fields_unchanged()

    def test_later_callback_failure_stops_before_remaining_bytes(self) -> None:
        status, states, values = self.run_case(
            source=b"abcdef",
            initial_state=3,
            initial_count=0xFFFFFFFE,
            results=[4, 5, 0, 7, 8, 9],
        )
        self.assertEqual(status, -1)
        self.assertEqual(states, [3, 4, 5])
        self.assertEqual(values, [ord("a"), ord("b"), ord("c")])
        self.assertEqual(self.context.output_state, 0)
        self.assertEqual(self.context.emitted_count, 0)
        self.assert_reserved_fields_unchanged()

    def test_deterministic_spans_match_independent_oracle(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            length = generator.randrange(0, 33)
            source = bytes(generator.randrange(0, 256) for _ in range(length))
            initial_state = generator.randrange(1, 1 << 32)
            initial_count = generator.getrandbits(32)
            results = [
                generator.randrange(1, 1 << 32) for _ in range(length)
            ]
            failure = None
            if length != 0 and generator.randrange(0, 4) == 0:
                failure = generator.randrange(0, length)
                results[failure] = 0

            status, states, values = self.run_case(
                source=source,
                initial_state=initial_state,
                initial_count=initial_count,
                results=results,
            )
            observed_count = length if failure is None else failure + 1
            expected_states = (
                []
                if observed_count == 0
                else [initial_state] + results[:observed_count - 1]
            )
            accepted = length if failure is None else failure
            expected_count = (initial_count + accepted) & 0xFFFFFFFF
            expected_state = (
                initial_state if length == 0 else results[observed_count - 1]
            )

            with self.subTest(index=index, length=length, failure=failure):
                self.assertEqual(status, 0 if failure is None else -1)
                self.assertEqual(states, expected_states)
                self.assertEqual(values, list(source[:observed_count]))
                self.assertEqual(self.context.output_state, expected_state)
                self.assertEqual(self.context.emitted_count, expected_count)
                self.assert_reserved_fields_unchanged()

    def test_stock_span_callers_indirect_dependency_and_adjacency(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 46)
        self.assertEqual(
            stock.hex(),
            "f8b505460e4617461c4600205cb117f8011bb068a847b060"
            "30b1f06a401cf0620020641ef3d1f2bd4ff0ff30f2bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "584f21e8f8b4cc13f7994f623e309f95"
            "22edb33e3b5d9fa5036650fb429532dc",
        )
        self.assertEqual(span(0x00482698, 0x0048269A).hex(), "a847")

        self.assertEqual(
            hashlib.sha256(span(0x00481A5C, 0x00481B86)).hexdigest(),
            "c7adfa039151d55e6da3707602889a77"
            "6ce0b8db7b20727c85dc4a9bcf0b4205",
        )
        call_contexts = [
            (0x00481A5C, 0x00481A68, "01236a4602a9304600f00efe"),
            (0x00481AA6, 0x00481AB2, "01236a4602a9304600f0e9fd"),
            (0x00481AF0, 0x00481AFC, "01236a4602a9304600f0c4fd"),
            (0x00481B3E, 0x00481B4A, "01236a4602a9304600f09dfd"),
            (0x00481B6E, 0x00481B7A, "01236a4602a9204600f085fd"),
        ]
        for start, end, encoded in call_contexts:
            self.assertEqual(span(start, end).hex(), encoded)

        preceding_pool = span(0x00482672, STOCK_START)
        self.assertEqual(
            hashlib.sha256(preceding_pool).hexdigest(),
            "193dc16eaca2246df95bb7dd28baae42"
            "55adaac92a75550c82d285373443fe7a",
        )
        retained_data = span(STOCK_END, 0x004826FC)
        self.assertEqual(len(retained_data), 74)
        self.assertEqual(
            hashlib.sha256(retained_data).hexdigest(),
            "c6c3d975e48a8c70ee95aff430c79357"
            "728201a4e219b4f4095e1d5089c37090",
        )
        self.assertEqual(
            retained_data,
            (
                b"\0\0printf_s: %n disallowed\0"
                b"printf: bad %n argument\0"
                b"\0\0\0\0nan\0NAN\0inf\0INF\0" + b"0\0\0\0"
            ),
        )
        next_function = span(0x004826FC, 0x00482708)
        self.assertEqual(
            hashlib.sha256(next_function).hexdigest(),
            "8ff986fa07383109f287b71ed376307b4"
            "e35fc4f7a01d5ab1ffdcc35daaff80b",
        )

        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target, encoded.hex()))

        self.assertEqual(
            callers,
            [
                (0x00481A64, "00f00efe"),
                (0x00481AAE, "00f0e9fd"),
                (0x00481AF8, "00f0c4fd"),
                (0x00481B46, "00f09dfd"),
                (0x00481B76, "00f085fd"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

    def test_no_narrow_entry_interior_or_stored_pointer_exists(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            if STOCK_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target, halfword))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "struct open_cfw_runtime_emit_context",
            "int open_cfw_runtime_emit_span(",
            "callback(context->output_state",
            "context->output_state = output_state;",
            "context->emitted_count += 1U;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_emit_span.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
