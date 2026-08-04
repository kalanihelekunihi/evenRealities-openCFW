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


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_theme_traversal.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_theme_traversal_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
CHAIN_START = 0x00482FCE
CHAIN_END = 0x00482FF2
RECURSION_START = CHAIN_END
RECURSION_END = 0x00483028
RECORD_CAPACITY = 4096

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


class RuntimeThemeTraversalObject(ctypes.Structure):
    _fields_ = [("class_pointer", ctypes.c_uint32)]


class RuntimeThemeTraversalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_theme_traversal.dylib"
            if sys.platform == "darwin"
            else "runtime_theme_traversal.so"
        )
        native_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            native_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            native_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            native_command,
            check=True,
            capture_output=True,
            text=True,
        )

        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_theme_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.theme_at = cls.loaded.open_cfw_test_runtime_theme_at
        cls.theme_at.argtypes = [ctypes.c_uint32]
        cls.theme_at.restype = ctypes.c_uint32
        cls.class_at = cls.loaded.open_cfw_test_runtime_class_at
        cls.class_at.argtypes = [ctypes.c_uint32]
        cls.class_at.restype = ctypes.c_uint32
        cls.set_callback = (
            cls.loaded.open_cfw_test_runtime_theme_set_callback
        )
        cls.set_callback.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_callback.restype = None
        cls.set_parent = cls.loaded.open_cfw_test_runtime_theme_set_parent
        cls.set_parent.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_parent.restype = None
        cls.set_base = cls.loaded.open_cfw_test_runtime_class_set_base
        cls.set_base.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_base.restype = None
        cls.set_flags = cls.loaded.open_cfw_test_runtime_class_set_flags
        cls.set_flags.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_flags.restype = None
        cls.set_mutation = (
            cls.loaded.open_cfw_test_runtime_theme_set_mutation
        )
        cls.set_mutation.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_mutation.restype = None
        cls.execute_chain = (
            cls.loaded.open_cfw_test_runtime_theme_execute_chain
        )
        cls.execute_chain.argtypes = [ctypes.c_uint32]
        cls.execute_chain.restype = None
        cls.execute_recursion = (
            cls.loaded.open_cfw_test_runtime_theme_execute_recursion
        )
        cls.execute_recursion.argtypes = [ctypes.c_uint32]
        cls.execute_recursion.restype = None
        cls.object = RuntimeThemeTraversalObject.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_object",
        )
        cls.record_callback = (ctypes.c_uint32 * RECORD_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_record_callback",
        )
        cls.record_callback_r2 = (
            ctypes.c_uint32 * RECORD_CAPACITY
        ).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_record_callback_r2",
        )
        cls.record_theme = (ctypes.c_uint32 * RECORD_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_record_theme",
        )
        cls.record_class = (ctypes.c_uint32 * RECORD_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_record_class",
        )

        target_object = Path(cls.temporary.name) / "theme_traversal.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        from apollo_overlay import extract_linked_overlay

        (
            cls.target_text,
            cls.target_functions,
            cls.target_report,
        ) = extract_linked_overlay(target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def records(self) -> list[tuple[int, int, int, int]]:
        count = self.uint(
            "open_cfw_test_runtime_theme_record_count"
        ).value
        self.assertLessEqual(count, RECORD_CAPACITY)
        return [
            (
                self.record_callback[index],
                self.record_callback_r2[index],
                self.record_theme[index],
                self.record_class[index],
            )
            for index in range(count)
        ]

    def test_theme_chain_is_parent_first_and_preserves_callback_abi(
        self,
    ) -> None:
        for count in (1, 2, 3, 17, 64):
            self.reset(count, 1)
            self.execute_chain(self.theme_at(count - 1))
            expected_class = self.class_at(0)
            with self.subTest(count=count):
                self.assertEqual(
                    self.records(),
                    [
                        (
                            index + 1,
                            index + 1,
                            self.theme_at(index),
                            expected_class,
                        )
                        for index in range(count)
                    ],
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_theme_theme_resolutions"
                    ).value,
                    count,
                )

    def test_null_callbacks_are_skipped_without_cutting_the_chain(
        self,
    ) -> None:
        self.reset(5, 1)
        self.set_callback(0, 0)
        self.set_callback(2, 0)
        self.set_callback(4, 0xA5A5)
        self.execute_chain(self.theme_at(4))
        self.assertEqual(
            [record[0] for record in self.records()],
            [2, 4, 0xA5A5],
        )
        self.assertEqual(
            [record[2] for record in self.records()],
            [self.theme_at(1), self.theme_at(3), self.theme_at(4)],
        )

    def test_class_recursion_forms_the_base_first_cross_product(
        self,
    ) -> None:
        self.reset(3, 4)
        self.execute_recursion(self.theme_at(2))
        self.assertEqual(
            self.records(),
            [
                (
                    theme_index + 1,
                    theme_index + 1,
                    self.theme_at(theme_index),
                    self.class_at(class_index),
                )
                for class_index in range(4)
                for theme_index in range(3)
            ],
        )
        self.assertEqual(self.object.class_pointer, self.class_at(3))
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_theme_class_resolutions"
            ).value,
            4,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_theme_theme_resolutions"
            ).value,
            12,
        )

    def test_inheritance_flag_and_base_pointer_gate_each_descent(
        self,
    ) -> None:
        scenarios = (
            (3, 0, [3]),
            (2, 0, [2, 3]),
            (3, (1 << 20) | 0x80000001, [0, 1, 2, 3]),
        )
        for changed_class, flags, expected_classes in scenarios:
            self.reset(1, 4)
            self.set_flags(changed_class, flags)
            self.execute_recursion(self.theme_at(0))
            with self.subTest(changed_class=changed_class, flags=flags):
                self.assertEqual(
                    [record[3] for record in self.records()],
                    [self.class_at(index) for index in expected_classes],
                )

        self.reset(1, 4)
        self.set_base(3, 0)
        self.execute_recursion(self.theme_at(0))
        self.assertEqual(
            [record[3] for record in self.records()],
            [self.class_at(3)],
        )

    def test_callback_class_mutation_is_restored_between_class_levels(
        self,
    ) -> None:
        self.reset(2, 3)
        poison_class = self.class_at(10)
        self.set_mutation(1, poison_class)
        self.execute_recursion(self.theme_at(1))
        self.assertEqual(
            self.records(),
            [
                (1, 1, self.theme_at(0), self.class_at(0)),
                (2, 2, self.theme_at(1), poison_class),
                (1, 1, self.theme_at(0), self.class_at(1)),
                (2, 2, self.theme_at(1), poison_class),
                (1, 1, self.theme_at(0), self.class_at(2)),
                (2, 2, self.theme_at(1), poison_class),
            ],
        )
        self.assertEqual(self.object.class_pointer, poison_class)

    def test_bounded_deep_cross_product_exhausts_fixture_capacity(
        self,
    ) -> None:
        self.reset(64, 64)
        self.execute_recursion(self.theme_at(63))
        records = self.records()
        self.assertEqual(len(records), RECORD_CAPACITY)
        self.assertEqual(
            records[0],
            (1, 1, self.theme_at(0), self.class_at(0)),
        )
        self.assertEqual(
            records[-1],
            (64, 64, self.theme_at(63), self.class_at(63)),
        )

    def test_stock_spans_and_adjacent_boundaries_are_exact(self) -> None:
        preceding = self.span(0x00482F74, CHAIN_START)
        self.assertEqual(len(preceding), 90)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "7e0a30860c051b990a19bd02045a981a"
            "ed535b61e6a500bfdaa932668ca13dbf",
        )

        chain = self.span(CHAIN_START, CHAIN_END)
        self.assertEqual(len(chain), 36)
        self.assertEqual(
            chain.hex(),
            "38b504000d006068002803d029006068fff7f6ff2068002803"
            "d0290020002268904731bd",
        )
        self.assertEqual(
            hashlib.sha256(chain).hexdigest(),
            "2fef5af03427a5ec0dbe61a99b4296b"
            "0339d78a6ec60da85fa55ceab65b821d7",
        )

        recursion = self.span(RECURSION_START, RECURSION_END)
        self.assertEqual(len(recursion), 54)
        self.assertEqual(
            recursion.hex(),
            "70b504000d002e682868006800280cd02868006ac0f300500028"
            "06d028680068286029002000fff7ebff2e6029002000fff7d4ff70bd",
        )
        self.assertEqual(
            hashlib.sha256(recursion).hexdigest(),
            "0970ae7ad16daca2c2a09a109e31ac6"
            "bf6cfd46add334e4737889e54cc0ea2c7",
        )

        following = self.span(RECURSION_END, 0x00483080)
        self.assertEqual(len(following), 88)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "422217cc3c3dc1573d449613dbab5c67"
            "e37a29af1f301521bc8aa2ba1020e312",
        )

    def test_wide_callers_dependencies_and_interior_topology_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        functions = {
            "chain": (CHAIN_START, CHAIN_END),
            "recursion": (RECURSION_START, RECURSION_END),
        }
        callers = {name: [] for name in functions}
        jumps = {name: [] for name in functions}
        interior = {name: [] for name in functions}
        dependencies = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                for name, (start, end) in functions.items():
                    if target == start:
                        destination[name].append(
                            (address, encoded.hex())
                        )
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[name].append(
                            (address, target, link)
                        )
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        self.assertEqual(
            callers,
            {
                "chain": [
                    (0x00482FDE, "fff7f6ff"),
                    (0x00483022, "fff7d4ff"),
                ],
                "recursion": [
                    (0x00482FA4, "00f025f8"),
                    (0x00483018, "fff7ebff"),
                ],
            },
        )
        self.assertEqual(jumps, {"chain": [], "recursion": []})
        self.assertEqual(interior, {"chain": [], "recursion": []})
        self.assertEqual(
            dependencies,
            {
                "chain": [
                    (0x00482FDE, CHAIN_START, "fff7f6ff"),
                ],
                "recursion": [
                    (0x00483018, RECURSION_START, "fff7ebff"),
                    (0x00483022, CHAIN_START, "fff7d4ff"),
                ],
            },
        )

    def test_narrow_and_stored_pointer_topology_is_reviewed(self) -> None:
        functions = {
            "chain": (CHAIN_START, CHAIN_END),
            "recursion": (RECURSION_START, RECURSION_END),
        }
        narrow_entry = {name: [] for name in functions}
        narrow_interior = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
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
            for name, (start, end) in functions.items():
                if start in candidates:
                    narrow_entry[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in functions.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target, value)
                    )

        self.assertEqual(narrow_entry, {"chain": [], "recursion": []})
        self.assertEqual(narrow_interior, {"chain": [], "recursion": []})
        self.assertEqual(
            stored,
            {
                "chain": [
                    (0x005354D7, 0x00482FD4, 0x00482FD5),
                ],
                "recursion": [
                    (0x004AA08F, 0x00483020, 0x00483021),
                ],
            },
        )

    def test_reviewed_target_clang_output_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_theme_apply_chain": {
                    "offset": 0,
                    "size": 34,
                },
                "open_cfw_runtime_theme_apply_recursion": {
                    "offset": 36,
                    "size": 42,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 78)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 12,
                    "symbol": "open_cfw_runtime_theme_apply_chain",
                    "type": 10,
                },
                {
                    "section": ".rel.text",
                    "site": 60,
                    "symbol": "open_cfw_runtime_theme_apply_recursion",
                    "type": 10,
                },
                {
                    "section": ".rel.text",
                    "site": 74,
                    "symbol": "open_cfw_runtime_theme_apply_chain",
                    "type": 30,
                },
            ],
        )
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            3,
        )
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "1a7ea20f24b15be4a746ba1a8aeae605"
            "5d2ffd0676c401c024b6a725993d3102",
        )
        self.assertEqual(self.target_text[34:36], b"\x00\xbf")

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_theme_apply_chain(",
            "open_cfw_runtime_theme_apply_recursion(",
            "theme->parent",
            "theme->apply_callback",
            "object_class->base_class",
            "object_class->flags_20",
            "OPEN_CFW_RUNTIME_THEME_INHERITABLE",
            "object->class_pointer = original_class;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_theme_traversal.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
