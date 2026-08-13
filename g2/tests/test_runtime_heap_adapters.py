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
    / "runtime_heap_adapters.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_heap_adapters_host.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
DESCRIPTOR = 0x20000338
EMPTY_POINTER = 0x2006F5AC
FUNCTIONS = {
    "allocate": (0x0048431E, 0x0048432A),
    "reallocate": (0x0048432A, 0x00484338),
    "free": (0x00484338, 0x00484344),
}
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


class RuntimeHeapAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_heap_adapters.dylib"
            if sys.platform == "darwin"
            else "runtime_heap_adapters.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_heap_adapter_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.allocate = cls.loaded.open_cfw_runtime_heap_allocate_adapter
        cls.allocate.argtypes = [ctypes.c_uint32]
        cls.allocate.restype = ctypes.c_uint32
        cls.reallocate = (
            cls.loaded.open_cfw_runtime_heap_reallocate_adapter
        )
        cls.reallocate.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reallocate.restype = ctypes.c_uint32
        cls.free = cls.loaded.open_cfw_runtime_heap_free_adapter
        cls.free.argtypes = [ctypes.c_uint32]
        cls.free.restype = None

        cls.target_object = temporary / "runtime_heap_adapters.o"
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
        cls.parsed_symbols = []
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
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields for name, fields in cls.parsed_symbols if name
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
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_allocate_forwards_every_value_without_public_filtering(
        self,
    ) -> None:
        for size in (0, 1, EMPTY_POINTER, 0x7FFFFFFF, 0xFFFFFFFF):
            for result in (0, 1, EMPTY_POINTER, 0xFFFFFFFF):
                with self.subTest(size=f"{size:#x}", result=f"{result:#x}"):
                    self.reset(result, 0xAAAAAAAA)
                    self.assertEqual(self.allocate(size), result)
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_heap_adapter_"
                            "allocate_calls"
                        ),
                        1,
                    )
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_heap_adapter_"
                            "allocate_descriptor"
                        ),
                        DESCRIPTOR,
                    )
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_heap_adapter_"
                            "allocate_size"
                        ),
                        size,
                    )
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_heap_adapter_"
                            "reallocate_calls"
                        ),
                        0,
                    )
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_heap_adapter_free_calls"
                        ),
                        0,
                    )

    def test_reallocate_forwards_pointer_size_and_result_exactly(
        self,
    ) -> None:
        allocations = (0, 1, EMPTY_POINTER, 0x2027A2E4, 0xFFFFFFFF)
        sizes = (0, 1, EMPTY_POINTER, 0x7FFFFFFF, 0xFFFFFFFF)
        results = (0, 1, EMPTY_POINTER, 0xFFFFFFFF)
        for allocation in allocations:
            for size in sizes:
                for result in results:
                    with self.subTest(
                        allocation=f"{allocation:#x}",
                        size=f"{size:#x}",
                        result=f"{result:#x}",
                    ):
                        self.reset(0xAAAAAAAA, result)
                        self.assertEqual(
                            self.reallocate(allocation, size),
                            result,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "reallocate_calls"
                            ),
                            1,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "reallocate_descriptor"
                            ),
                            DESCRIPTOR,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "reallocate_allocation"
                            ),
                            allocation,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "reallocate_size"
                            ),
                            size,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "allocate_calls"
                            ),
                            0,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_heap_adapter_"
                                "free_calls"
                            ),
                            0,
                        )

    def test_free_forwards_null_sentinel_and_other_values_once(
        self,
    ) -> None:
        for allocation in (
            0,
            1,
            EMPTY_POINTER,
            0x2027A2E4,
            0xFFFFFFFF,
        ):
            with self.subTest(allocation=f"{allocation:#x}"):
                self.reset(0xAAAAAAAA, 0x55555555)
                self.free(allocation)
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_heap_adapter_free_calls"
                    ),
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_heap_adapter_"
                        "free_descriptor"
                    ),
                    DESCRIPTOR,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_heap_adapter_"
                        "free_allocation"
                    ),
                    allocation,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_heap_adapter_"
                        "allocate_calls"
                    ),
                    0,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_heap_adapter_"
                        "reallocate_calls"
                    ),
                    0,
                )

    def test_stock_spans_group_hashes_and_literal_are_exact(self) -> None:
        expected = {
            "allocate": (
                "80b501001248fff72cff02bd",
                "219878e5a22fbec313dac05088cdabda3"
                "ca24f5f4b24e90f00eda4aad1062184",
            ),
            "reallocate": (
                "80b50a0001000e48fff77fff02bd",
                "45fe398ca48d9f2b769d5ee758ec48e0"
                "dfcbe8923167bd3c3f3a187d0cbf2cc5",
            ),
            "free": (
                "80b501000b48fff7aeff01bd",
                "faf392e39c380a7622fdf8194c285455"
                "f7e82e5705ae9eb8118e0c1b846521da",
            ),
        }
        for name, (body_hex, digest) in expected.items():
            start, end = FUNCTIONS[name]
            body = self.span(start, end)
            with self.subTest(name=name):
                self.assertEqual(body.hex(), body_hex)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        group = self.span(0x0048431E, 0x00484344)
        self.assertEqual(len(group), 38)
        self.assertEqual(
            hashlib.sha256(group).hexdigest(),
            "bbd37dab814066c686a843f9141fad3b2"
            "31b7bbb12629c55a1f18196b8a838c0",
        )
        self.assertEqual(
            struct.unpack("<I", self.span(0x0048436C, 0x00484370))[0],
            DESCRIPTOR,
        )

    def test_wide_callers_dependencies_and_interiors_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interiors = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
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
                for name, (start, end) in FUNCTIONS.items():
                    if target == start:
                        (callers if link else jumps)[name].append(
                            (address, encoded.hex())
                        )
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interiors[name].append(
                            (address, target, link, encoded.hex())
                        )
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        expected_callers = {
            "allocate": [
                (0x0044F722, "34f0fcfd"),
                (0x0044F73E, "34f0eefd"),
            ],
            "reallocate": [(0x0044F786, "34f0d0fd")],
            "free": [(0x0044F764, "34f0e8fd")],
        }
        expected_digests = {
            "allocate": (
                "95eab79e500be7849d0a86bff65735ba"
                "a534db9eb77e83784995b045a9ca9361"
            ),
            "reallocate": (
                "3ea3d51365ad3027fde6b42fb42950fb"
                "91162bfb268eca40eb09a8f4bb8004b8"
            ),
            "free": (
                "b839fb25927b6ef07960f2ab3c83d1e5"
                "56e83fb331a1c2a875a142ef7c965b7e"
            ),
        }
        expected_dependencies = {
            "allocate": [(0x00484324, 0x00484180, "fff72cff")],
            "reallocate": [(0x00484332, 0x00484234, "fff77fff")],
            "free": [(0x0048433E, 0x0048429E, "fff7aeff")],
        }
        self.assertEqual(callers, expected_callers)
        self.assertEqual(jumps, {name: [] for name in FUNCTIONS})
        self.assertEqual(interiors, {name: [] for name in FUNCTIONS})
        self.assertEqual(dependencies, expected_dependencies)
        for name in FUNCTIONS:
            digest = hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers[name]
                )
            ).hexdigest()
            with self.subTest(name=name):
                self.assertEqual(digest, expected_digests[name])

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entries = {name: [] for name in FUNCTIONS}
        narrow_interiors = {name: [] for name in FUNCTIONS}
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
            for name, (start, end) in FUNCTIONS.items():
                if start in candidates:
                    narrow_entries[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interiors[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1:
                for name, (start, end) in FUNCTIONS.items():
                    if start <= target < end:
                        stored[name].append(
                            (BASE + offset, target, value)
                        )

        self.assertEqual(
            narrow_entries,
            {name: [] for name in FUNCTIONS},
        )
        self.assertEqual(
            narrow_interiors,
            {name: [] for name in FUNCTIONS},
        )
        self.assertEqual(
            stored,
            {
                "allocate": [],
                "reallocate": [
                    (0x0078AB55, 0x0048432E, 0x0048432F),
                ],
                "free": [],
            },
        )
        self.assertTrue(
            all(
                address & 1
                for values in stored.values()
                for address, _target, _value in values
            )
        )

    def test_retained_generic_layer_boundaries_hashes_and_calls(
        self,
    ) -> None:
        retained = {
            "allocate": (
                0x00484180,
                0x004841D8,
                "5c8eae7744e9bcd8bcfe6ed1ebaf678c"
                "faf80ebcb4b1d9a74178f991bf163084",
            ),
            "memalign": (
                0x004841D8,
                0x00484234,
                "a098f7aca0ad496ce3ccd16fa3a61aa90"
                "68e663ad265ab1a00aa14eb223713f6",
            ),
            "reallocate": (
                0x00484234,
                0x0048429E,
                "470c32d27721f6932431a553868f6e5e4"
                "34d56bb1c8a0818e42e42b45882828e",
            ),
            "free": (
                0x0048429E,
                0x004842E6,
                "26fffcabeaafc258cfa459b415b1eefe"
                "672cc859c9bc23a19bd5834c6072886e",
            ),
        }
        for name, (start, end, digest) in retained.items():
            with self.subTest(name=name):
                self.assertEqual(
                    hashlib.sha256(self.span(start, end)).hexdigest(),
                    digest,
                )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00484180, 0x004842E6)
            ).hexdigest(),
            "324439dce3c072be68b3634216fcae1f"
            "d62a57c38db8ef28720136c9fb8ebf59",
        )

    def test_target_text_symbols_and_relocations_are_exact(self) -> None:
        self.assertEqual(len(self.target), 46)
        self.assertEqual(
            self.target.hex(),
            "014640f23830c2f20000fff7febf"
            "00bf"
            "0a46014640f23830c2f20000fff7febf"
            "014640f23830c2f20000fff7febf",
        )
        self.assertEqual(
            hashlib.sha256(self.target).hexdigest(),
            "76eedf0490b7f854529d73837f9797ea"
            "113b6527f30566f814e21157a2b6f173",
        )
        self.assertEqual(
            self.relocations,
            [
                (
                    10,
                    30,
                    "open_cfw_runtime_heap_generic_allocate",
                ),
                (
                    28,
                    30,
                    "open_cfw_runtime_heap_generic_reallocate",
                ),
                (
                    42,
                    30,
                    "open_cfw_runtime_heap_generic_free",
                ),
            ],
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [
                "open_cfw_runtime_heap_generic_allocate",
                "open_cfw_runtime_heap_generic_free",
                "open_cfw_runtime_heap_generic_reallocate",
            ],
        )

        expected = {
            "open_cfw_runtime_heap_allocate_adapter": (
                0,
                14,
                "014640f23830c2f20000fff7febf",
                "45d83fd78bef53435a3cbd6eb94502e3"
                "d8d72f8f31d6315cb70173fdd9ef9ae9",
            ),
            "open_cfw_runtime_heap_reallocate_adapter": (
                16,
                16,
                "0a46014640f23830c2f20000fff7febf",
                "566eb5ce41f37ebfe24a3e0f2bead5db"
                "9ba9208a029b6aeb6617bb55b75ef082",
            ),
            "open_cfw_runtime_heap_free_adapter": (
                32,
                14,
                "014640f23830c2f20000fff7febf",
                "45d83fd78bef53435a3cbd6eb94502e3"
                "d8d72f8f31d6315cb70173fdd9ef9ae9",
            ),
        }
        for name, (
            expected_offset,
            expected_size,
            expected_hex,
            expected_digest,
        ) in expected.items():
            symbol = self.symbols[name]
            offset = symbol[1] & ~1
            size = symbol[2]
            body = self.target[offset:offset + size]
            with self.subTest(name=name):
                self.assertEqual((offset, size), (
                    expected_offset,
                    expected_size,
                ))
                self.assertEqual(body.hex(), expected_hex)
                self.assertEqual(
                    hashlib.sha256(body).hexdigest(),
                    expected_digest,
                )
        self.assertEqual(self.target[14:16], b"\x00\xBF")

    def test_source_scope_and_dependency_seams_are_explicit(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_heap_allocate_adapter(",
            "open_cfw_runtime_heap_reallocate_adapter(",
            "open_cfw_runtime_heap_free_adapter(",
            "OPEN_CFW_RUNTIME_HEAP_PRIMARY_DESCRIPTOR = 0x20000338U",
            "open_cfw_runtime_heap_generic_allocate(",
            "open_cfw_runtime_heap_generic_reallocate(",
            "open_cfw_runtime_heap_generic_free(",
            "OPEN_CFW_RUNTIME_HEAP_GENERIC_ALLOCATE(",
            "OPEN_CFW_RUNTIME_HEAP_GENERIC_REALLOCATE(",
            "OPEN_CFW_RUNTIME_HEAP_GENERIC_FREE(",
        ):
            self.assertIn(token, source)
        for excluded in (
            "0x00441C44",
            "0x004417EE",
            "0x004D05E4",
            "0x004D0722",
            "0x004D0808",
            "0x2006F5AC",
            "if (size ==",
            "if (allocation ==",
            "#include <",
            "malloc",
            "printf",
            "0x00484181U",
            "0x00484235U",
            "0x0048429FU",
        ):
            self.assertNotIn(excluded, source)
        self.assertIn("runtime_heap_adapters.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
