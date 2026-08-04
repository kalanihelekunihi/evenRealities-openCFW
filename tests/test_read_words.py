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
SOURCE = COMPONENT_ROOT / "read_words.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "read_words_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x0048086A
STOCK_END = 0x00480872


class ReadWordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "read_words.dylib"
            if sys.platform == "darwin"
            else "read_words.so"
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
        cls.reset = cls.loaded.open_cfw_test_read_words_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.copy = cls.loaded.open_cfw_read_words
        cls.copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_uint,
        ]
        cls.copy.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_read_words_{name}",
        )

    @classmethod
    def array(cls, name: str, size: int) -> ctypes.Array:
        return (ctypes.c_uint * size).in_dll(
            cls.loaded,
            f"open_cfw_test_read_words_{name}",
        )

    @staticmethod
    def pointer(
        values: ctypes.Array,
        offset: int = 0,
    ) -> ctypes.POINTER(ctypes.c_uint):
        return ctypes.cast(
            ctypes.byref(values, offset * ctypes.sizeof(ctypes.c_uint)),
            ctypes.POINTER(ctypes.c_uint),
        )

    def events(self) -> list[tuple[int, int]]:
        count = self.word("event_count").value
        return list(
            zip(
                self.array("event_kind", 1024)[:count],
                self.array("event_value", 1024)[:count],
            )
        )

    def test_single_word_reads_before_writing(self) -> None:
        source = (ctypes.c_uint * 1)(0xA5A55A5A)
        destination = (ctypes.c_uint * 1)(0)
        self.reset()

        self.copy(source, destination, 1)

        self.assertEqual(destination[0], 0xA5A55A5A)
        self.assertEqual(
            self.events(),
            [(1, 0xA5A55A5A), (2, 0xA5A55A5A)],
        )

    def test_multiple_words_copy_in_forward_order(self) -> None:
        source_values = (0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF)
        source = (ctypes.c_uint * len(source_values))(*source_values)
        destination = (ctypes.c_uint * len(source_values))(
            *([0xCCCCCCCC] * len(source_values))
        )
        self.reset()

        self.copy(source, destination, len(source_values))

        self.assertEqual(tuple(destination), source_values)
        self.assertEqual(
            self.events(),
            [
                event
                for value in source_values
                for event in ((1, value), (2, value))
            ],
        )

    def test_source_and_destination_may_be_identical(self) -> None:
        values = (ctypes.c_uint * 4)(1, 2, 3, 4)
        self.reset()
        self.copy(values, values, 4)
        self.assertEqual(tuple(values), (1, 2, 3, 4))
        self.assertEqual(self.word("event_count").value, 8)

    def test_overlap_preserves_stock_forward_copy_semantics(self) -> None:
        values = (ctypes.c_uint * 6)(1, 2, 3, 4, 5, 6)
        self.reset()

        self.copy(self.pointer(values), self.pointer(values, 1), 5)

        self.assertEqual(tuple(values), (1, 1, 1, 1, 1, 1))
        self.assertEqual(
            self.events(),
            [(1, 1), (2, 1)] * 5,
        )

    def test_randomized_nonzero_counts_match_forward_model(self) -> None:
        rng = random.Random(0x48086A)
        for count in range(1, 65):
            with self.subTest(count=count):
                source_values = [rng.getrandbits(32) for _ in range(count)]
                source = (ctypes.c_uint * count)(*source_values)
                destination = (ctypes.c_uint * count)(
                    *[rng.getrandbits(32) for _ in range(count)]
                )
                self.reset()
                self.copy(source, destination, count)
                self.assertEqual(tuple(destination), tuple(source_values))
                self.assertEqual(self.word("event_count").value, count * 2)

    def test_stock_wrapper_padding_and_next_boundary_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        wrapper = application[
            STOCK_START - APPLICATION_BASE:
            STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(wrapper), 8)
        self.assertEqual(
            hashlib.sha256(wrapper).hexdigest(),
            "28fbddc5962a26c875030d4bb760e1ab"
            "3a1c002294b2e957a125e35ecff3d1bd",
        )
        padding = application[
            STOCK_END - APPLICATION_BASE:
            0x00480874 - APPLICATION_BASE
        ]
        self.assertEqual(padding, b"\0\0")
        self.assertEqual(
            hashlib.sha256(padding).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )
        next_function = application[
            0x00480874 - APPLICATION_BASE:
            0x004809C4 - APPLICATION_BASE
        ]
        self.assertEqual(len(next_function), 336)
        self.assertEqual(
            hashlib.sha256(next_function).hexdigest(),
            "fc0ab63e464dbd21244bbfe1df929801"
            "f9857a6ca6cdaa1b90e04d09f1928da5",
        )

    def test_stock_topology_and_itcm_dependency_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        calls = []
        jumps = []
        external_interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append(address)
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    external_interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target))
        self.assertEqual(calls, [0x004D3F32])
        self.assertEqual(jumps, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(dependencies, [(0x0048086C, 0x00000048)])

        internal_calls = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            try:
                target = apollo_overlay.decode_thumb_branch(
                    address,
                    application[offset:offset + 4],
                    link=True,
                )
            except apollo_overlay.BuildError:
                continue
            if target == 0x00000048:
                internal_calls.append(address)
        self.assertEqual(internal_calls, [0x0048086C])

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_zero_count_contract_is_explicit_in_source(self) -> None:
        source_text = SOURCE.read_text()
        self.assertIn("do {", source_text)
        self.assertIn("} while (--word_count != 0U);", source_text)
        self.assertIn(
            "a zero count underflows and is not treated as a no-op",
            source_text,
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "497afbcf322f1e84281e1d23e9e71c57e479cc0ee6256e5454c2a1143e79a370",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6faaddf37687e42dc30ff99bacfbf5f691b3b89db95464ba3e9b96af6b614105",
        )


if __name__ == "__main__":
    unittest.main()
