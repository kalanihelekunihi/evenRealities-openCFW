from __future__ import annotations

import os

import ctypes
import hashlib
import math
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_etoa.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_etoa_host.c"
OFFICIAL = (
    OPENCFW_ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
LANE_START = 0x00483612
CODE_START = 0x0048364C
CODE_END = 0x00483908
NEXT_FUNCTION = 0x00483960
ZERO_PAD = 1 << 0
LEFT = 1 << 1
PLUS = 1 << 2
UPPER = 1 << 5
PRECISION = 1 << 10
ADAPT = 1 << 11

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2",
    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror",
]


def _model(
    value: float,
    precision: int,
    width: int,
    flags: int,
) -> tuple[float, int, int, int, int]:
    negative = value < 0.0
    if negative:
        value = -value
    if not flags & PRECISION:
        precision = 6
    bits = struct.unpack("<Q", struct.pack("<d", value))[0]
    exponent_two = ((bits >> 52) & 0x7FF) - 1023
    bits = (bits & ((1 << 52) - 1)) | (1023 << 52)
    conversion = struct.unpack("<d", struct.pack("<Q", bits))[0]
    exponent_decimal = int(
        0.1760912590558
        + exponent_two * 0.301029995663981
        + (conversion - 1.5) * 0.289529654602168
    )
    exponent_two = int(exponent_decimal * 3.321928094887362 + 0.5)
    z = (
        exponent_decimal * 2.302585092994046
        - exponent_two * 0.6931471805599453
    )
    z_squared = z * z
    conversion = struct.unpack(
        "<d",
        struct.pack("<Q", ((exponent_two + 1023) & 0xFFF) << 52),
    )[0]
    conversion *= (
        1.0
        + 2.0 * z
        / (
            2.0 - z
            + z_squared / (6.0 + z_squared / (10.0 + z_squared / 14.0))
        )
    )
    if value < conversion:
        exponent_decimal -= 1
        conversion /= 10.0
    exponent_width = 4 if -100 < exponent_decimal < 100 else 5
    if flags & ADAPT:
        if 1e-4 <= value < 1e6:
            precision = (
                precision - exponent_decimal - 1
                if precision > exponent_decimal
                else 0
            )
            flags |= PRECISION
            exponent_width = 0
            exponent_decimal = 0
        elif precision > 0 and flags & PRECISION:
            precision -= 1
    floating_width = width - exponent_width if width > exponent_width else 0
    if flags & LEFT and exponent_width:
        floating_width = 0
    if exponent_decimal:
        value /= conversion
    return (
        -value if negative else value,
        precision,
        floating_width,
        flags & ~ADAPT,
        exponent_decimal,
    )


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeEtoaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_etoa.dylib" if sys.platform == "darwin"
            else "runtime_etoa.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), "-O2", "-Wall", "-Wextra", "-Werror",
            str(FIXTURE),
        ]
        command.extend(
            ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_etoa_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.execute = cls.loaded.open_cfw_test_runtime_etoa_execute
        cls.execute.argtypes = [
            ctypes.c_double, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.execute.restype = ctypes.c_uint32
        cls.characters = (ctypes.c_ubyte * 64).in_dll(
            cls.loaded, "open_cfw_test_runtime_etoa_output_character"
        )
        cls.indices = (ctypes.c_uint32 * 64).in_dll(
            cls.loaded, "open_cfw_test_runtime_etoa_output_index"
        )

        target = temporary / "runtime_etoa.o"
        subprocess.run(
            [os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target)],
            check=True, capture_output=True, text=True,
        )
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbols = apollo_overlay.section_named(sections, ".symtab")
        strings = sections[int(symbols["link"])]
        string_data = data[
            int(strings["offset"]):int(strings["offset"]) + int(strings["size"])
        ]
        parsed = []
        for i in range(int(symbols["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbols["offset"]) + i * 16
            )
            parsed.append((
                apollo_overlay.elf_string(string_data, fields[0], "symbol"),
                fields,
            ))
        cls.target_functions = {
            name: {"offset": fields[1] & ~1, "size": fields[2]}
            for name, fields in parsed
            if fields[3] & 15 == 2 and fields[5] == int(text["index"])
        }
        cls.target_relocations = []
        for section in sections:
            if int(section["type"]) != 9 or int(section["info"]) != int(text["index"]):
                continue
            for i in range(int(section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II", data, int(section["offset"]) + i * 8
                )
                cls.target_relocations.append({
                    "site": offset, "type": info & 255,
                    "symbol": parsed[info >> 8][0],
                })
        cls.rodata = [
            section for section in sections if apollo_overlay.is_rodata(section)
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def double(self, name: str) -> float:
        return ctypes.c_double.in_dll(self.loaded, name).value

    def test_normal_and_adaptive_modes_match_the_upstream_model(self) -> None:
        generator = random.Random(CODE_START)
        cases = [
            (0.0, 0, 0, 0), (-1.0, 2, 12, PRECISION),
            (1e-5, 4, 14, PRECISION | ADAPT),
            (1e-4, 4, 14, PRECISION | ADAPT),
            (999999.0, 5, 20, PRECISION | ADAPT),
            (1e6, 5, 20, PRECISION | ADAPT | UPPER),
            (1e100, 8, 30, PRECISION), (1e-100, 8, 30, PRECISION),
        ]
        cases.extend(
            (
                math.ldexp(generator.uniform(1.0, 2.0), generator.randrange(-900, 900)),
                generator.randrange(0, 12),
                generator.randrange(0, 40),
                generator.choice((0, PRECISION, PRECISION | ADAPT, PRECISION | LEFT)),
            )
            for _ in range(256)
        )
        for case, (value, precision, width, flags) in enumerate(cases):
            expected = _model(value, precision, width, flags)
            self.reset(100, 104)
            observed = self.execute(value, precision, width, flags, 7, 200)
            with self.subTest(case=case):
                self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_calls"), 1)
                self.assertTrue(math.isclose(
                    self.double("open_cfw_test_runtime_etoa_ftoa_value"),
                    expected[0], rel_tol=2e-12, abs_tol=1e-300,
                ))
                self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_precision"), expected[1])
                self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_width"), expected[2])
                self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_flags"), expected[3])
                exponent = expected[4]
                emits_exponent = not (
                    flags & ADAPT and 1e-4 <= abs(value) < 1e6
                )
                if emits_exponent:
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_calls"), 1)
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_value"), abs(exponent))
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_negative"), exponent < 0)
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_base"), 10)
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_width"), 3 if abs(exponent) < 100 else 4)
                    self.assertEqual(self.characters[0], ord("E" if flags & UPPER else "e"))
                    self.assertEqual(self.indices[0], 100)
                    self.assertGreaterEqual(observed, 104)
                else:
                    self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_calls"), 0)
                    self.assertEqual(observed, 100)

    def test_nan_and_infinities_tail_forward_directly_to_ftoa(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf")):
            self.reset(0x12345678, 0)
            observed = self.execute(value, 9, 17, 0xA5A5, 3, 55)
            self.assertEqual(observed, 0x12345678)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_calls"), 1)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_precision"), 9)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_width"), 17)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ftoa_flags"), 0xA5A5)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_ntoa_calls"), 0)
            self.assertEqual(self.uint("open_cfw_test_runtime_etoa_output_calls"), 0)

    def test_left_mode_pads_after_the_exponent(self) -> None:
        self.reset(20, 24)
        result = self.execute(1e20, 4, 30, PRECISION | LEFT, 5, 99)
        self.assertEqual(result, 35)
        self.assertEqual(self.characters[0], ord("e"))
        self.assertEqual(self.indices[0], 20)
        self.assertEqual(bytes(self.characters[1:12]), b" " * 11)
        self.assertEqual(list(self.indices[1:12]), list(range(24, 35)))

    def test_stock_boundaries_literals_and_feature_configuration(self) -> None:
        prefix = self.application[
            LANE_START - APPLICATION_BASE:CODE_START - APPLICATION_BASE
        ]
        code = self.application[
            CODE_START - APPLICATION_BASE:CODE_END - APPLICATION_BASE
        ]
        literals = self.application[
            CODE_END - APPLICATION_BASE:NEXT_FUNCTION - APPLICATION_BASE
        ]
        self.assertEqual((len(prefix), len(code), len(literals)), (58, 700, 88))
        self.assertEqual(hashlib.sha256(prefix).hexdigest(), "b931af2a102ca4c6d865d1a556408a26724ccef0881c9b8871f85d0deba1200c")
        self.assertEqual(hashlib.sha256(code).hexdigest(), "66c7415fa9587cb5f1022d48848abf4d54f1c1929c38a16d385ad7d6978e527e")
        self.assertEqual(hashlib.sha256(literals).hexdigest(), "de58f84b02774c29c6fcf6efea3b439c4b4ae6e249e9be05f8e3dd1af592445c")
        lane = self.application[
            LANE_START - APPLICATION_BASE:NEXT_FUNCTION - APPLICATION_BASE
        ]
        self.assertEqual(len(lane), 846)
        self.assertEqual(hashlib.sha256(lane).hexdigest(), "69771027648dd6aac925211a6478e5fea785630155436fdaf84d224993e6c477")
        source = SOURCE.read_text()
        for token in ("DEFAULT_PRECISION = 6U", "OPEN_CFW_RUNTIME_ETOA_ADAPT_EXP", "__DBL_MAX__", 'target("fp64")'):
            self.assertIn(token, source)

    def test_callers_dependencies_and_branch_topology_are_exact(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay
        callers, jumps, interior, dependencies = [], [], [], []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(address, encoded, link=link)
                except apollo_overlay.BuildError:
                    continue
                if target == CODE_START:
                    destination.append((address, encoded.hex()))
                if CODE_START < target < CODE_END and not CODE_START <= address < CODE_END:
                    interior.append((address, target, link))
                if link and CODE_START <= address < CODE_END:
                    dependencies.append((address, target, encoded.hex()))
        self.assertEqual(callers, [(0x483404, "00f022f9"), (0x483E8A, "fff7dffb")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [
            (0x483698, 0x483350, "fff75afe"),
            (0x483884, 0x483350, "fff764fd"),
            (0x4838DC, 0x48320A, "fff795fc"),
        ])
        self.assertEqual(hashlib.sha256(b"".join(struct.pack("<I", a) for a, _ in callers)).hexdigest(), "b3de1ffdae528535f8278347d0cacf28bd4bf61ce072a2ea60157537137ec31c")

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entry, narrow_interior = [], []

        def sign_extend(value: int, bits: int) -> int:
            sign = 1 << (bits - 1)
            return value - (1 << bits) if value & sign else value

        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address + 4
                    + sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address + 4
                    + sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                candidates.append(
                    address + 4
                    + (((halfword >> 9) & 1) << 6)
                    + (((halfword >> 3) & 0x1F) << 1)
                )
            if CODE_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    CODE_START < target < CODE_END
                    and not CODE_START <= address < CODE_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1 and CODE_START <= target < CODE_END:
                stored.append((APPLICATION_BASE + offset, target, value))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [
            (0x00480623, 0x004837D0, 0x004837D1),
            (0x00492B9D, 0x004837D4, 0x004837D5),
            (0x0049AF07, 0x004836D4, 0x004836D5),
            (0x0049B08B, 0x004836D4, 0x004836D5),
            (0x004A6561, 0x00483746, 0x00483747),
            (0x004AE945, 0x004837BC, 0x004837BD),
            (0x004AEB97, 0x004836D4, 0x004836D5),
            (0x004AED1B, 0x004836D4, 0x004836D5),
            (0x004C8E11, 0x004837D0, 0x004837D1),
            (0x004D5187, 0x004837D0, 0x004837D1),
            (0x005B4769, 0x00483846, 0x00483847),
        ])

    @_APPLE_ONLY
    def test_target_artifact_uses_fp64_and_only_source_dependencies(self) -> None:
        self.assertEqual(self.target_functions, {"open_cfw_runtime_etoa": {"offset": 0, "size": 712}})
        self.assertEqual(len(self.target_text), 712)
        self.assertEqual(hashlib.sha256(self.target_text).hexdigest(), "4be8badc0b6927b03f23e34865b34d6281d7a8ce28ec2b91448afc0d53914d5b")
        self.assertEqual(
            self.target_text[:24].hex(),
            "2de9f04f81b02ded028b88b00df1500999e88003b4ee400b",
        )
        self.assertEqual(self.target_text[0x14:0x18], b"\xb4\xee\x40\x0b")
        self.assertEqual(self.rodata, [])
        self.assertEqual(self.target_relocations, [
            {"site": 418, "type": 30, "symbol": "open_cfw_runtime_ftoa"},
            {"site": 518, "type": 10, "symbol": "open_cfw_runtime_ftoa"},
            {"site": 586, "type": 10, "symbol": "open_cfw_runtime_ntoa_long"},
        ])
        self.assertNotIn(b"__aeabi", self.target_text)

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn("#include <", source)
        for token in ("open_cfw_runtime_etoa(", "OPEN_CFW_RUNTIME_ETOA_FTOA(", "OPEN_CFW_RUNTIME_ETOA_NTOA_LONG(", "output("):
            self.assertIn(token, source)
        self.assertIn('pcs("aapcs-vfp")', source)
        self.assertIn("runtime_etoa.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
