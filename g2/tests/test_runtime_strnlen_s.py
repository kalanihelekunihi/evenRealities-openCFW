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
SOURCE = COMPONENT_ROOT / "runtime_strnlen_s.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_strnlen_s_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x00454770
FUNCTION_END = 0x00454778
DEPENDENCY_START = 0x0048D4E8
DEPENDENCY_END = 0x0048D53E
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


def _oracle(data: bytes, maximum_length: int) -> int:
    limit = min(len(data), maximum_length)
    for index in range(limit):
        if data[index] == 0:
            return index
    return limit


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeStrnlenSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_strnlen_s.dylib"
            if sys.platform == "darwin"
            else "runtime_strnlen_s.so"
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
        cls.execute = cls.loaded.open_cfw_test_runtime_strnlen_s_execute
        cls.execute.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
        ]
        cls.execute.restype = ctypes.c_uint32
        cls.execute_null = cls.loaded.open_cfw_test_runtime_strnlen_s_null
        cls.execute_null.argtypes = [ctypes.c_uint32]
        cls.execute_null.restype = ctypes.c_uint32
        cls.execute_invalid_zero = (
            cls.loaded.open_cfw_test_runtime_strnlen_s_zero_maximum_no_load
        )
        cls.execute_invalid_zero.argtypes = []
        cls.execute_invalid_zero.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_strnlen_s.o"
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
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        cls.target_data, cls.target_sections = apollo_overlay.parse_elf32(
            cls.target_object
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def run_data(self, data: bytes, maximum_length: int) -> int:
        storage = (ctypes.c_ubyte * len(data))(*data)
        return self.execute(storage, maximum_length)

    def test_null_and_zero_maximum_stock_edges(self) -> None:
        for maximum_length in (0, 1, 0xFFFFFFFF):
            self.assertEqual(self.execute_null(maximum_length), 0)
        self.assertEqual(self.execute_invalid_zero(), 0)

    def test_terminator_and_bound_grid_matches_oracle(self) -> None:
        cases = (
            b"\0",
            b"a\0",
            b"hello\0",
            b"hello\0ignored",
            b"\xff\xfe\xfd\0",
            bytes(range(1, 33)) + b"\0",
        )
        for data in cases:
            for maximum_length in range(0, len(data) + 3):
                self.assertEqual(
                    self.run_data(data, maximum_length),
                    _oracle(data, maximum_length),
                )

    def test_nonterminated_storage_stops_exactly_at_bound(self) -> None:
        for length in (1, 2, 3, 4, 7, 16, 31, 64):
            data = bytes([0xA5]) * length
            for maximum_length in range(length + 1):
                self.assertEqual(
                    self.run_data(data, maximum_length),
                    maximum_length,
                )

    def test_deterministic_randomized_bytes(self) -> None:
        generator = random.Random(0x454770)
        for _ in range(512):
            length = generator.randrange(1, 129)
            data = bytes(generator.randrange(256) for _ in range(length))
            maximum_length = generator.randrange(length + 1)
            self.assertEqual(
                self.run_data(data, maximum_length),
                _oracle(data, maximum_length),
            )

    def test_stock_entry_and_adjacent_boundaries_are_exact(self) -> None:
        preceding = self.span(0x00454768, FUNCTION_START)
        body = self.span(FUNCTION_START, FUNCTION_END)
        following = self.span(FUNCTION_END, 0x004547AE)
        self.assertEqual(body, bytes.fromhex("80b538f0b9fe02bd"))
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "d8a76b3ba496ca5db1dbc63f04c266c4"
            "155d94f7f2a7b5d2074f054c437f0d9c",
        )
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "e67dfe443678fe75c1f738939488a9b7"
            "026332e58c351426bdd112557e4fb291",
        )
        self.assertEqual(len(following), 54)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "d4f95bb268b5061dfd8296a6a3158aa"
            "addea4527a3267e69679cad965ced3fd5",
        )
        self.assertEqual(
            following[:4],
            bytes.fromhex("2de9f041"),
        )
        self.assertEqual(
            self.span(0x004547AE, 0x004547B0),
            bytes.fromhex("80b5"),
        )

    def test_stock_dependency_body_and_edge_contract_are_exact(self) -> None:
        dependency = self.span(DEPENDENCY_START, DEPENDENCY_END)
        self.assertEqual(len(dependency), 86)
        self.assertEqual(
            hashlib.sha256(dependency).hexdigest(),
            "6ae6688c0181b75443a608e2e2de6682"
            "98e9fbe5a81eea0d1db7c3789c7da786",
        )
        self.assertEqual(dependency[:4], bytes.fromhex("030027d0"))
        self.assertEqual(
            self.span(DEPENDENCY_END, 0x0048D540),
            b"\0\0",
        )
        self.assertIn(bytes.fromhex("491e26bf10f8012b"), dependency)
        self.assertIn(bytes.fromhex("491e28bf10f8012b"), dependency)

    def test_wide_callers_dependency_and_literal_topology_are_exact(
        self,
    ) -> None:
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        dependency_callers = []
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
                if target == FUNCTION_START:
                    destination.append((address, encoded.hex()))
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, link))
                if link and FUNCTION_START <= address < FUNCTION_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )
                if link and target == DEPENDENCY_START:
                    dependency_callers.append(
                        (address, encoded.hex())
                    )
        self.assertEqual(
            callers,
            [
                (0x004547F8, "fff7baff"),
                (0x00483F04, "d0f734fc"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x00454772, 0x0048D4E8, "38f0b9fe")],
        )
        self.assertEqual(dependency_callers, [(0x00454772, "38f0b9fe")])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
            ).hexdigest(),
            "e75d721a23737a718ee1be31570b53b03"
            "05e51262821fc57691d14ff9601c72b",
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _target, _encoded in dependencies
                )
            ).hexdigest(),
            "8a68c6110a9cfd6c00adf00e8541d24"
            "b3542dab55c33a7473b4cb44564309d93",
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<II", address, target)
                    for address, target, _encoded in dependencies
                )
            ).hexdigest(),
            "9068c588f738beff5cb08d1110a69cbf"
            "d9af5ad6a6afb0ae191ccdd0dbbd8e80",
        )
        self.assertNotIn(bytes.fromhex("dff8"), self.span(
            FUNCTION_START,
            FUNCTION_END,
        ))

    def test_narrow_and_stored_pointer_topology_is_negative(self) -> None:
        narrow_entry = []
        narrow_interior = []
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
                candidates.append(
                    address
                    + 4
                    + (((halfword >> 9) & 1) << 6)
                    + (((halfword >> 3) & 0x1F) << 1)
                )
            if FUNCTION_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    narrow_interior.append(
                        (address, target, halfword)
                    )
        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if (
                value & 1
                and FUNCTION_START <= target < FUNCTION_END
            ):
                stored.append(
                    (APPLICATION_BASE + offset, target, value)
                )
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    @_APPLE_ONLY
    def test_target_body_rodata_and_relocations_are_exact(self) -> None:
        import apollo_overlay

        text = apollo_overlay.section_named(self.target_sections, ".text")
        target = self.target_data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual(len(target), 4)
        self.assertEqual(
            hashlib.sha256(target).hexdigest(),
            "90a54a1f68a806a1795bd04485690823"
            "5426b3c0f67be605fb94d3d5344a747f",
        )
        self.assertEqual(target, bytes.fromhex("fff7febf"))
        section_names = {section["name"] for section in self.target_sections}
        self.assertNotIn(".rodata", section_names)
        self.assertNotIn(".rodata.str1.1", section_names)
        relocations = subprocess.run(
            ["/usr/bin/objdump", "-r", str(self.target_object)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("R_ARM_THM_JUMP24", relocations)
        self.assertIn(
            "open_cfw_runtime_bounded_string_length",
            relocations,
        )
        self.assertNotIn("__aeabi", relocations)
        self.assertIn("R_ARM_PREL31", relocations)

    def test_source_scope_and_upstream_provenance_are_bounded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e",
            source,
        )
        self.assertIn("open_cfw_runtime_strnlen_s(", source)
        self.assertIn("open_cfw_runtime_bounded_string_length(", source)
        self.assertIn("minsize", source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_strnlen_s.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
