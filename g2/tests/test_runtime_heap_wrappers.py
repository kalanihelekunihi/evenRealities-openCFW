from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_heap_wrappers.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_heap_wrappers_host.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
ALLOCATE_START, ALLOCATE_END = 0x0044F718, 0x0044F730
FREE_START, FREE_END = 0x0044F758, 0x0044F76A
ALLOCATE_ADAPTER_START, ALLOCATE_ADAPTER_END = 0x0048431E, 0x0048432A
FREE_ADAPTER_START, FREE_ADAPTER_END = 0x00484338, 0x00484344
EMPTY_POINTER = 0x2006F5AC
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeHeapWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_heap_wrappers.dylib"
            if sys.platform == "darwin"
            else "runtime_heap_wrappers.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_heap_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.allocate = cls.loaded.open_cfw_runtime_heap_allocate
        cls.allocate.argtypes = [ctypes.c_uint32]
        cls.allocate.restype = ctypes.c_uint32
        cls.free = cls.loaded.open_cfw_runtime_heap_free
        cls.free.argtypes = [ctypes.c_uint32]
        cls.free.restype = None

        cls.target_object = temporary / "runtime_heap_wrappers.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields for name, fields in parsed_symbols if name
        }
        cls.relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_zero_size_returns_empty_pointer_without_adapter_call(
        self,
    ) -> None:
        for adapter_result in (0, 1, EMPTY_POINTER, 0xFFFFFFFF):
            self.reset(adapter_result)
            with self.subTest(adapter_result=f"{adapter_result:#010x}"):
                self.assertEqual(self.allocate(0), EMPTY_POINTER)
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_allocate_calls"),
                    0,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_allocate_size"),
                    0,
                )

    def test_nonzero_size_forwards_exact_adapter_result(self) -> None:
        cases = (
            (1, 0),
            (8, 0x20279670),
            (0x7FFFFFFF, EMPTY_POINTER),
            (0xFFFFFFFF, 0xFFFFFFFF),
        )
        for size, adapter_result in cases:
            self.reset(adapter_result)
            with self.subTest(
                size=f"{size:#010x}",
                adapter_result=f"{adapter_result:#010x}",
            ):
                self.assertEqual(self.allocate(size), adapter_result)
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_allocate_calls"),
                    1,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_allocate_size"),
                    size,
                )

    def test_null_and_empty_pointer_free_are_no_ops(self) -> None:
        for allocation in (0, EMPTY_POINTER):
            self.reset(0xAAAAAAAA)
            self.free(allocation)
            with self.subTest(allocation=f"{allocation:#010x}"):
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_free_calls"),
                    0,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_freed"),
                    0,
                )

    def test_other_free_values_reach_adapter_exactly_once(self) -> None:
        for allocation in (1, 0x20279670, 0xFFFFFFFF):
            self.reset(0xAAAAAAAA)
            self.free(allocation)
            with self.subTest(allocation=f"{allocation:#010x}"):
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_free_calls"),
                    1,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_runtime_heap_freed"),
                    allocation,
                )

    def test_stock_wrapper_spans_literals_and_hashes_are_exact(self) -> None:
        allocate = self.span(ALLOCATE_START, ALLOCATE_END)
        self.assertEqual(
            allocate.hex(),
            "80b5002801d1214805e034f0fcfd002801d10020ffe702bd",
        )
        self.assertEqual(
            hashlib.sha256(allocate).hexdigest(),
            "6f9d2c280a65a9ad8f6bd6c6d648bfe"
            "e419ffa3643ec7674109f263f67484472",
        )

        free = self.span(FREE_START, FREE_END)
        self.assertEqual(
            free.hex(),
            "80b51249884203d0002801d034f0e8fd01bd",
        )
        self.assertEqual(
            hashlib.sha256(free).hexdigest(),
            "f4c5f66b61c9e19b839c553e4f8173b"
            "0073543ac72c0ab57c199ff51c07f67d4",
        )
        self.assertEqual(
            struct.unpack("<I", self.span(0x0044F7A4, 0x0044F7A8))[0],
            EMPTY_POINTER,
        )
        literal_pool = self.span(0x0044F7A4, 0x0044F7B4)
        self.assertEqual(
            hashlib.sha256(literal_pool).hexdigest(),
            "d3c32e01d96f5e4185903c53e328757e"
            "944a561c4f8a88a1e5c5b2f94fec4bda",
        )

    def test_retained_adapter_bodies_and_dependencies_are_exact(self) -> None:
        allocate_adapter = self.span(
            ALLOCATE_ADAPTER_START,
            ALLOCATE_ADAPTER_END,
        )
        self.assertEqual(
            allocate_adapter.hex(),
            "80b501001248fff72cff02bd",
        )
        self.assertEqual(
            hashlib.sha256(allocate_adapter).hexdigest(),
            "219878e5a22fbec313dac05088cdabda3"
            "ca24f5f4b24e90f00eda4aad1062184",
        )
        free_adapter = self.span(
            FREE_ADAPTER_START,
            FREE_ADAPTER_END,
        )
        self.assertEqual(
            free_adapter.hex(),
            "80b501000b48fff7aeff01bd",
        )
        self.assertEqual(
            hashlib.sha256(free_adapter).hexdigest(),
            "faf392e39c380a7622fdf8194c285455"
            "f7e82e5705ae9eb8118e0c1b846521da",
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                0x00484324,
                self.span(0x00484324, 0x00484328),
                link=True,
            ),
            0x00484180,
        )
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                0x0048433E,
                self.span(0x0048433E, 0x00484342),
                link=True,
            ),
            0x0048429E,
        )
        self.assertEqual(
            struct.unpack("<I", self.span(0x0048436C, 0x00484370))[0],
            0x20000338,
        )

    def test_all_wide_callers_and_wrapper_dependencies_are_pinned(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = {ALLOCATE_START: [], FREE_START: []}
        jumps = {ALLOCATE_START: [], FREE_START: []}
        interior = {ALLOCATE_START: [], FREE_START: []}
        dependencies = {ALLOCATE_START: [], FREE_START: []}
        ends = {
            ALLOCATE_START: ALLOCATE_END,
            FREE_START: FREE_END,
        }
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                for start, end in ends.items():
                    if target == start:
                        (callers if link else jumps)[start].append(address)
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[start].append((address, target, link))
                    if link and start <= address < end:
                        dependencies[start].append(
                            (address, target, encoded.hex())
                        )

        expected = {
            ALLOCATE_START: (
                58,
                "802adeee76be97aec5568fcac9520871"
                "9544f152bc649a482a5f02ce07713ff0",
                [(0x0044F722, 0x0048431E, "34f0fcfd")],
            ),
            FREE_START: (
                122,
                "fed63006a21f2f806a155ea3aae0eed7"
                "31bb1169d7605b2a539f028e8cca3e1f",
                [(0x0044F764, 0x00484338, "34f0e8fd")],
            ),
        }
        for start, (count, digest, expected_dependencies) in expected.items():
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(len(callers[start]), count)
                self.assertEqual(
                    hashlib.sha256(
                        b"".join(
                            struct.pack("<I", address)
                            for address in callers[start]
                        )
                    ).hexdigest(),
                    digest,
                )
                self.assertEqual(jumps[start], [])
                self.assertEqual(interior[start], [])
                self.assertEqual(
                    dependencies[start],
                    expected_dependencies,
                )
        self.assertIn(0x0048401C, callers[ALLOCATE_START])
        self.assertIn(0x0048403C, callers[FREE_START])
        self.assertIn(0x00484096, callers[FREE_START])

    def test_no_external_narrow_or_stored_wrapper_entries(self) -> None:
        expected_internal = {
            (ALLOCATE_START, ALLOCATE_END): [
                (0x0044F71C, 0x0044F722, 0xD101),
                (0x0044F720, 0x0044F72E, 0xE005),
                (0x0044F728, 0x0044F72E, 0xD101),
                (0x0044F72C, 0x0044F72E, 0xE7FF),
            ],
            (FREE_START, FREE_END): [
                (0x0044F75E, 0x0044F768, 0xD003),
                (0x0044F762, 0x0044F768, 0xD001),
            ],
        }
        for (start, end), expected in expected_internal.items():
            narrow_entry = []
            narrow_interior = []
            internal = []
            for offset in range(0, len(self.application) - 1, 2):
                address = BASE + offset
                halfword = struct.unpack_from(
                    "<H",
                    self.application,
                    offset,
                )[0]
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
                if start in candidates:
                    narrow_entry.append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior.append(
                            (address, target, halfword)
                        )
                    if (
                        start <= address < end
                        and start <= target < end
                    ):
                        internal.append((address, target, halfword))

            stored = []
            for offset in range(0, len(self.application) - 3):
                value = struct.unpack_from(
                    "<I",
                    self.application,
                    offset,
                )[0]
                target = value & ~1
                if value & 1 and start <= target < end:
                    stored.append((BASE + offset, target))

            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(narrow_entry, [])
                self.assertEqual(narrow_interior, [])
                self.assertEqual(internal, expected)
                self.assertEqual(stored, [])

    def test_target_text_bodies_symbols_and_relocations_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.target), 44)
        self.assertEqual(
            hashlib.sha256(self.target).hexdigest(),
            "db948ed6c5e56466699df08ce4330897"
            "ff253dd2c3bb55dd0f88985bd034f753",
        )
        self.assertEqual(
            self.relocations,
            [
                (4, 30, "open_cfw_runtime_heap_allocate_adapter"),
                (40, 30, "open_cfw_runtime_heap_free_adapter"),
            ],
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [
                "open_cfw_runtime_heap_allocate_adapter",
                "open_cfw_runtime_heap_free_adapter",
            ],
        )

        allocate_symbol = self.symbols["open_cfw_runtime_heap_allocate"]
        allocate_offset = allocate_symbol[1] & ~1
        allocate_size = allocate_symbol[2]
        self.assertEqual((allocate_offset, allocate_size), (0, 18))
        allocate = self.target[
            allocate_offset:allocate_offset + allocate_size
        ]
        self.assertEqual(
            allocate.hex(),
            "002818bffff7febf4ff2ac50c2f206007047",
        )
        self.assertEqual(
            hashlib.sha256(allocate).hexdigest(),
            "97793f62221282babfdcaf845542cc77a"
            "fc22d0b1a549b3ed294790e60d0ad23",
        )

        free_symbol = self.symbols["open_cfw_runtime_heap_free"]
        free_offset = free_symbol[1] & ~1
        free_size = free_symbol[2]
        self.assertEqual((free_offset, free_size), (20, 24))
        self.assertEqual(self.target[18:20], b"\x00\xBF")
        free = self.target[free_offset:free_offset + free_size]
        self.assertEqual(
            free.hex(),
            "002808bf70474ff2ac51c2f206018842"
            "00d17047fff7febf",
        )
        self.assertEqual(
            hashlib.sha256(free).hexdigest(),
            "d65ffd473fcc149c74f4db5c9cfe980b"
            "d5f0b45ec7ecf591540c71c50fea81cd",
        )

    def test_source_is_bounded_to_public_heap_wrappers(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_heap_allocate(",
            "open_cfw_runtime_heap_free(",
            "open_cfw_runtime_heap_allocate_adapter(",
            "open_cfw_runtime_heap_free_adapter(",
            "OPEN_CFW_RUNTIME_HEAP_EMPTY_POINTER = 0x2006F5ACU",
            "if (size == 0U)",
            "allocation == 0U",
            "OPEN_CFW_RUNTIME_HEAP_ALLOCATE_ADAPTER(size)",
            "OPEN_CFW_RUNTIME_HEAP_FREE_ADAPTER(allocation)",
        ):
            self.assertIn(token, source)
        for excluded in (
            "#include <",
            "0x00441C44",
            "0x004417EE",
            "0x004D05E4",
            "0x004D0722",
            "0x004D0808",
            "0x20000338",
            "0x0048431FU",
            "0x00484339U",
            "printf",
            "malloc",
        ):
            self.assertNotIn(excluded, source)
        self.assertIn("runtime_heap_wrappers.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
