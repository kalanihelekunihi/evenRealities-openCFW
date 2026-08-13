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
SOURCE = COMPONENT_ROOT / "runtime_color_math.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_color_math_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
MIX_START = 0x00482E4C
MIX_END = 0x00482ED4
BRIGHTNESS_START = 0x00482ED4
BRIGHTNESS_END = 0x00482EF6


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def pack_color(blue: int, green: int, red: int, alpha: int) -> int:
    return (
        blue
        | (green << 8)
        | (red << 16)
        | (alpha << 24)
    )


def expected_mix(source: int, destination: int) -> int:
    alpha = source >> 24
    if alpha >= 253:
        return (source & 0x00FFFFFF) | (destination & 0xFF000000)
    if alpha < 3:
        return destination
    inverse = 255 - alpha
    result = destination & 0xFF000000
    for shift in (0, 8, 16):
        source_lane = (source >> shift) & 0xFF
        destination_lane = (destination >> shift) & 0xFF
        result |= (
            (
                alpha * source_lane
                + inverse * destination_lane
            ) >> 8
        ) << shift
    return result


def expected_brightness(color: int) -> int:
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    return (blue * 4 + green + red * 3) >> 3


class RuntimeColorMathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_color_math.dylib"
            if sys.platform == "darwin"
            else "runtime_color_math.so"
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
        cls.mix = cls.loaded.open_cfw_test_runtime_color_mix_alpha
        cls.mix.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.mix.restype = ctypes.c_uint32
        cls.brightness = cls.loaded.open_cfw_test_runtime_color_brightness
        cls.brightness.argtypes = [ctypes.c_uint32]
        cls.brightness.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_mix_matches_oracle_for_every_alpha_and_randomized_words(
        self,
    ) -> None:
        generator = random.Random(MIX_START)
        for alpha in range(256):
            for sample in range(32):
                source = generator.getrandbits(24) | (alpha << 24)
                destination = generator.getrandbits(32)
                with self.subTest(alpha=alpha, sample=sample):
                    self.assertEqual(
                        self.mix(source, destination),
                        expected_mix(source, destination),
                    )

    def test_mix_thresholds_and_divide_by_256_darkening_are_exact(
        self,
    ) -> None:
        destination = pack_color(0x11, 0x80, 0xFF, 0xA5)
        source_rgb = pack_color(0xE2, 0x31, 0x77, 0)
        for alpha in (0, 1, 2):
            self.assertEqual(
                self.mix(source_rgb | (alpha << 24), destination),
                destination,
            )
        for alpha in (253, 254, 255):
            self.assertEqual(
                self.mix(source_rgb | (alpha << 24), destination),
                (source_rgb & 0x00FFFFFF) | 0xA5000000,
            )

        identical_rgb = pack_color(1, 128, 255, 0)
        destination = identical_rgb | 0x5A000000
        for alpha in (3, 64, 128, 192, 252):
            observed = self.mix(
                identical_rgb | (alpha << 24),
                destination,
            )
            with self.subTest(alpha=alpha):
                self.assertEqual(
                    observed,
                    pack_color(0, 127, 254, 0x5A),
                )

    def test_mix_always_retains_destination_alpha(self) -> None:
        source_rgb = 0x00123456
        destination_rgb = 0x00FEDCBA
        for source_alpha in range(256):
            for destination_alpha in range(256):
                source = source_rgb | (source_alpha << 24)
                destination = (
                    destination_rgb | (destination_alpha << 24)
                )
                observed = self.mix(source, destination)
                with self.subTest(
                    source_alpha=source_alpha,
                    destination_alpha=destination_alpha,
                ):
                    self.assertEqual(
                        observed >> 24,
                        destination_alpha,
                    )

    def test_brightness_lane_weights_alpha_independence_and_oracle(
        self,
    ) -> None:
        self.assertEqual(self.brightness(pack_color(255, 0, 0, 0)), 127)
        self.assertEqual(self.brightness(pack_color(0, 255, 0, 0)), 31)
        self.assertEqual(self.brightness(pack_color(0, 0, 255, 0)), 95)
        self.assertEqual(
            self.brightness(pack_color(255, 255, 255, 0)),
            255,
        )

        generator = random.Random(BRIGHTNESS_START)
        for sample in range(8192):
            blue = generator.randrange(256)
            green = generator.randrange(256)
            red = generator.randrange(256)
            expected = (blue * 4 + green + red * 3) >> 3
            for alpha in (0, 1, 0x7F, 0xFF):
                color = pack_color(blue, green, red, alpha)
                with self.subTest(sample=sample, alpha=alpha):
                    self.assertEqual(self.brightness(color), expected)
                    self.assertEqual(
                        self.brightness(color),
                        expected_brightness(color),
                    )

    def test_reviewed_target_text_functions_rodata_and_relocations(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = Path(directory) / "runtime_color_math.o"
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
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
                "-c",
                str(SOURCE),
                "-o",
                str(object_path),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
            import apollo_overlay

            data, sections = apollo_overlay.parse_elf32(object_path)
            text_section = apollo_overlay.section_named(sections, ".text")
            start = int(text_section["offset"])
            end = start + int(text_section["size"])
            text = data[start:end]
            overlay, functions, report = (
                apollo_overlay.extract_linked_overlay(object_path)
            )

        self.assertEqual(len(text), 132)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "e585d2bbf099c0f445e79ede60685c34"
            "75552c3429e10c050aefa3aeca1a8ca0",
        )
        self.assertEqual(overlay, text)
        self.assertEqual(
            functions,
            {
                "open_cfw_runtime_color_mix_alpha": {
                    "offset": 0,
                    "size": 106,
                },
                "open_cfw_runtime_color_brightness": {
                    "offset": 108,
                    "size": 24,
                },
            },
        )
        self.assertEqual(report["rodata_size"], 0)
        self.assertEqual(report["rodata_sections"], [])
        self.assertEqual(report["resolved_relocation_count"], 0)
        self.assertNotIn(
            ".rel.text",
            {str(section["name"]) for section in sections},
        )

    def test_combined_translation_unit_with_rgb888_mix_compiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = Path(directory) / "runtime_color_combined.o"
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
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
                "-include",
                str(COMPONENT_ROOT / "runtime_color_mix.c"),
                "-include",
                str(SOURCE),
                "-x",
                "c",
                "-c",
                "/dev/null",
                "-o",
                str(object_path),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

    def test_stock_boundaries_callers_dependencies_and_topology(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        spans = {
            (0x00482DD8, MIX_START):
                "7f812480f5849e8396429428554c8f73"
                "c5511d9f3d476e945af364e85ced0017",
            (MIX_START, MIX_END):
                "bdf9e6d76b887d4096e5a9c75a5d730"
                "20728346c1d5fa6c47d66342312e0b7af",
            (BRIGHTNESS_START, BRIGHTNESS_END):
                "c5270e432425b4468cd1a1bb07624d8f"
                "a951cd0a23e1a17774b39a0b58922a45",
            (BRIGHTNESS_END, 0x00482F72):
                "a0691979a4d03f0a8e2d014a67c327d0"
                "48bf3ab277bca115e77b2f8010e19118",
        }
        expected_sizes = [116, 136, 34, 124]
        for ((start, end), expected), size in zip(
            spans.items(),
            expected_sizes,
        ):
            body = span(start, end)
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(len(body), size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        expected_callers = {
            "mix": [
                (0x00482F28, "fff790ff"),
                (0x00482F64, "fff772ff"),
            ],
            "brightness": [
                (0x005C907C, "b9f62aff"),
                (0x005C90B0, "b9f610ff"),
                (0x005C90EE, "b9f6f1fe"),
                (0x005C912E, "b9f6d1fe"),
                (0x005C916E, "b9f6b1fe"),
                (0x005C91AE, "b9f691fe"),
            ],
        }
        caller_digests = {
            "mix":
                "3a105ffba24f640a8a40295d35f547f3"
                "5d428282c5fcf602a269b5bbcb3100af",
            "brightness":
                "f099e95e0fad06fb9d143e1ab71861ee"
                "19989da26741c1b027bb50453e51b6c0",
        }
        functions = {
            "mix": (MIX_START, MIX_END),
            "brightness": (BRIGHTNESS_START, BRIGHTNESS_END),
        }
        for name, (function_start, function_end) in functions.items():
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
                    if target == function_start:
                        observed.append((address, encoded.hex()))
                    if (
                        function_start < target < function_end
                        and not function_start <= address < function_end
                    ):
                        interior.append((address, target, link))
                    if (
                        link
                        and function_start <= address < function_end
                    ):
                        dependencies.append(
                            (address, target, encoded.hex())
                        )
            digest = hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
            ).hexdigest()
            with self.subTest(function=name):
                self.assertEqual(callers, expected_callers[name])
                self.assertEqual(digest, caller_digests[name])
                self.assertEqual(jumps, [])
                self.assertEqual(interior, [])
                self.assertEqual(dependencies, [])

    def test_narrow_and_stored_pointer_topology_is_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        functions = {
            "mix": (MIX_START, MIX_END),
            "brightness": (BRIGHTNESS_START, BRIGHTNESS_END),
        }
        narrow_entry = {name: [] for name in functions}
        narrow_interior = {name: [] for name in functions}
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
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in functions.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target, value)
                    )

        self.assertEqual(narrow_entry, {"mix": [], "brightness": []})
        self.assertEqual(narrow_interior, {"mix": [], "brightness": []})
        self.assertEqual(
            stored["mix"],
            [
                (0x0046DFD9, 0x00482ED0, 0x00482ED1),
                (0x004C8E37, 0x00482ED0, 0x00482ED1),
                (0x0055E169, 0x00482E60, 0x00482E61),
            ],
        )
        self.assertEqual(stored["brightness"], [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_color_mix_alpha(",
            "open_cfw_runtime_color_brightness(",
            "if (alpha >= 253U)",
            "if (alpha < 3U)",
            "(destination & 0xFF000000U)",
            "alpha * source",
            "+ (255U - alpha) * destination",
            ") >> 8U;",
            "open_cfw_runtime_color_lane(color, 0U) * 4U",
            "open_cfw_runtime_color_lane(color, 16U) * 3U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_color_math.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
