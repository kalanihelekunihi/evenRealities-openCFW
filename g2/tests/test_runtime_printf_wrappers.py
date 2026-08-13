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
COMPONENT = ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT / "runtime_printf_wrappers.c"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_printf_wrappers_host.c"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000
FUNCTIONS = {
    "snprintf": (0x483FD0, 0x483FEA),
    "vsnprintf": (0x483FEA, 0x483FFC),
}
CORE = (0x483960, 0x483FCC)
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror",
]


class RuntimePrintfWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / ("w.dylib" if sys.platform == "darwin" else "w.so")
        command = [os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_printf_reset
        cls.reset.argtypes = [ctypes.c_int32]
        cls.execute_snprintf = cls.loaded.open_cfw_test_runtime_printf_execute_snprintf
        cls.execute_snprintf.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        cls.execute_snprintf.restype = ctypes.c_int32
        cls.execute_vsnprintf = cls.loaded.open_cfw_test_runtime_printf_execute_vsnprintf
        cls.execute_vsnprintf.argtypes = [ctypes.c_uint32]
        cls.execute_vsnprintf.restype = ctypes.c_int32
        cls.buffer = (ctypes.c_ubyte * 32).in_dll(cls.loaded, "open_cfw_test_runtime_printf_buffer")
        cls.arguments = (ctypes.c_int32 * 3).in_dll(cls.loaded, "open_cfw_test_runtime_printf_argument")

        target = temporary / "w.o"
        subprocess.run([os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
        sym = apollo_overlay.section_named(sections, ".symtab")
        strings = sections[int(sym["link"])]
        sd = data[int(strings["offset"]):int(strings["offset"]) + int(strings["size"])]
        parsed = []
        cls.target_functions = {}
        for i in range(int(sym["size"]) // 16):
            fields = struct.unpack_from("<IIIBBH", data, int(sym["offset"]) + i * 16)
            name = apollo_overlay.elf_string(sd, fields[0], "symbol")
            parsed.append((name, fields))
            if fields[3] & 15 == 2 and fields[5] == int(text["index"]):
                cls.target_functions[name] = {"offset": fields[1] & ~1, "size": fields[2]}
        cls.relocations = []
        for section in sections:
            if int(section["type"]) == 9 and int(section["info"]) == int(text["index"]):
                for i in range(int(section["size"]) // 8):
                    off, info = struct.unpack_from("<II", data, int(section["offset"]) + i * 8)
                    cls.relocations.append((off, info & 255, parsed[info >> 8][0]))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def test_variadic_snprintf_forwards_argument_cursor_and_all_fields(self) -> None:
        for count in (0, 1, 31, 0xFFFFFFFF):
            self.reset(-12345)
            observed = self.execute_snprintf(count, -1, 0x12345678, 65)
            self.assertEqual(observed, -12345)
            self.assertEqual(self.uint("open_cfw_test_runtime_printf_calls"), 1)
            self.assertEqual(self.uint("open_cfw_test_runtime_printf_maximum_length"), count)
            self.assertEqual(list(self.arguments), [-1, 0x12345678, 65])
            self.assertEqual(
                ctypes.c_size_t.in_dll(self.loaded, "open_cfw_test_runtime_printf_observed_buffer").value,
                ctypes.addressof(self.buffer),
            )
            self.assertNotEqual(ctypes.c_size_t.in_dll(self.loaded, "open_cfw_test_runtime_printf_output").value, 0)

    def test_vsnprintf_wrapper_preserves_an_existing_va_list(self) -> None:
        self.reset(8765)
        observed = self.execute_vsnprintf(17, 11, -22, 33)
        self.assertEqual(observed, 8765)
        self.assertEqual(self.uint("open_cfw_test_runtime_printf_maximum_length"), 17)
        self.assertEqual(list(self.arguments), [11, -22, 33])

    def test_stock_spans_and_following_literal_boundary_are_exact(self) -> None:
        core = self.application[CORE[0] - BASE:CORE[1] - BASE]
        self.assertEqual(len(core), 1644)
        self.assertEqual(
            hashlib.sha256(core).hexdigest(),
            "69f04620a01aaca4a11601ea426644fa3e2bd47c972700c6ddc1676607e1435b",
        )
        self.assertEqual(
            self.application[CORE[1] - BASE:FUNCTIONS["snprintf"][0] - BASE],
            bytes.fromhex("7cdc7800"),
        )
        expected = {
            "snprintf": (26, "a7bbf413eb4e6661219f9fa0f0b2e90ec4ff1f6321af913ea5b0561c19700bbe"),
            "vsnprintf": (18, "efd2fb98268737ddd968133f20a0ae190b499fb11e24abeab8bfd69a239b388f"),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(len(body), expected[name][0])
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected[name][1])
        following = self.application[0x483FFC - BASE:0x484014 - BASE]
        self.assertEqual(len(following), 24)
        self.assertEqual(hashlib.sha256(following).hexdigest(), "c35cd51aba4e0bf1a9e40136ce2888eb8c607a5e4a88d3612c2d67bbbbc80518")
        self.assertEqual(struct.unpack_from("<I", following, 20)[0], 0x00483029)

    def test_wide_callers_dependencies_and_interior_topology_are_exact(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        expected_callers = {
            "snprintf": [0x44D302, 0x498738, 0x4C8FBA, 0x4C90C0, 0x4C9154, 0x5C3CD4, 0x5C3D1E, 0x5C3D5E, 0x5CA220, 0x5CC4EC],
            "vsnprintf": [0x44D2BA, 0x489AE0, 0x489B34],
        }
        expected_digests = {
            "snprintf": "54baa7981e895a0d0bbba40cb2ddb003093e3d70f32affda7e7f18337f259831",
            "vsnprintf": "5dad0226547894e3ebe50d2b6675807d304bee638b92f33fa541e3a2f9ac6145",
        }
        for name, (start, end) in FUNCTIONS.items():
            callers, jumps, interior, dependencies = [], [], [], []
            for offset in range(0, len(self.application) - 3, 2):
                address, encoded = BASE + offset, self.application[offset:offset + 4]
                for link, destination in ((True, callers), (False, jumps)):
                    try:
                        target = apollo_overlay.decode_thumb_branch(address, encoded, link=link)
                    except apollo_overlay.BuildError:
                        continue
                    if target == start:
                        destination.append(address)
                    if start < target < end and not start <= address < end:
                        interior.append((address, target, link))
                    if link and start <= address < end:
                        dependencies.append((address, target))
            self.assertEqual(callers, expected_callers[name])
            self.assertEqual(jumps, [])
            self.assertEqual(interior, [])
            self.assertEqual(dependencies, [((0x483FE0 if name == "snprintf" else 0x483FF6), 0x483960)])
            self.assertEqual(hashlib.sha256(b"".join(struct.pack("<I", a) for a in callers)).hexdigest(), expected_digests[name])

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entry = {name: [] for name in FUNCTIONS}
        narrow_interior = {name: [] for name in FUNCTIONS}

        def signed(value: int, bits: int) -> int:
            sign = 1 << (bits - 1)
            return value - (1 << bits) if value & sign else value

        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(address + 4 + signed((halfword & 0x7FF) << 1, 12))
            condition = (halfword >> 8) & 15
            if halfword & 0xF000 == 0xD000 and condition < 14:
                candidates.append(address + 4 + signed((halfword & 255) << 1, 9))
            if halfword & 0xF500 == 0xB100:
                candidates.append(address + 4 + (((halfword >> 9) & 1) << 6) + (((halfword >> 3) & 31) << 1))
            for name, (start, end) in FUNCTIONS.items():
                if start in candidates:
                    narrow_entry[name].append((address, halfword))
                narrow_interior[name].extend(
                    (address, target, halfword) for target in candidates
                    if start < target < end and not start <= address < end
                )
        stored = {name: [] for name in FUNCTIONS}
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in FUNCTIONS.items():
                if start <= target < end:
                    stored[name].append((BASE + offset, target, value))
        self.assertEqual(narrow_entry, {"snprintf": [], "vsnprintf": []})
        self.assertEqual(narrow_interior, {"snprintf": [], "vsnprintf": []})
        self.assertEqual(stored["snprintf"], [])
        self.assertEqual(stored["vsnprintf"], [(0x455625, 0x483FFA, 0x483FFB)])

    def test_raw_target_artifact_and_unresolved_dependencies_are_exact(self) -> None:
        self.assertEqual(self.target_functions, {
            "open_cfw_runtime_snprintf": {"offset": 0, "size": 52},
            "open_cfw_runtime_vsnprintf_wrapper": {"offset": 52, "size": 34},
        })
        self.assertEqual(len(self.target_text), 86)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "f3c7cd90a31d5b2eee30751c4fdb22e59cde6726cb78b970d86211335e752aa8",
        )
        self.assertEqual(self.relocations, [
            (22, 49, "open_cfw_runtime_bounded_byte_store"), (26, 50, "open_cfw_runtime_bounded_byte_store"),
            (38, 10, "open_cfw_runtime_vsnprintf"),
            (64, 49, "open_cfw_runtime_bounded_byte_store"), (68, 50, "open_cfw_runtime_bounded_byte_store"),
            (78, 10, "open_cfw_runtime_vsnprintf"),
        ])

    def test_both_target_bodies_and_source_core_calls_are_exact(self) -> None:
        expected = {
            "open_cfw_runtime_snprintf": {
                "digest": "dd20a88162e3b20ec8eaa857ba91cdb73a387f3a6914dfb0307dd573f7efb7af",
                "call_offset": 38,
            },
            "open_cfw_runtime_vsnprintf_wrapper": {
                "digest": "19432dc2d4333fa543489af922d071deecbfd111da6e2840088d033dc4a041a7",
                "call_offset": 78,
            },
        }

        for name, topology in expected.items():
            function = self.target_functions[name]
            start = function["offset"]
            body = self.target_text[start:start + function["size"]]
            self.assertEqual(hashlib.sha256(body).hexdigest(), topology["digest"])
            self.assertIn(
                (
                    topology["call_offset"],
                    10,
                    "open_cfw_runtime_vsnprintf",
                ),
                self.relocations,
            )

    def test_source_scope_is_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_snprintf(",
            "open_cfw_runtime_vsnprintf_wrapper(",
            'open_cfw_runtime_printf_vsnprintf(',
            '__asm__("open_cfw_runtime_vsnprintf")',
            "__builtin_va_start",
            "__builtin_va_end",
        ):
            self.assertIn(token, source)
        self.assertNotIn("int open_cfw_runtime_vsnprintf(", source)
        self.assertNotIn("0x00483961U", source)
        self.assertNotIn("#include <", source)
        fixture = FIXTURE.read_text()
        self.assertLess(
            fixture.index("#define OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF("),
            fixture.index('#include "../../components/apollo_main/core_overlay/runtime_printf_wrappers.c"'),
        )
        self.assertIn("__builtin_va_list", fixture)


if __name__ == "__main__":
    unittest.main()
