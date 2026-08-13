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
SOURCE = COMPONENT_ROOT / "runtime_color_mix.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_color_mix_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482DD8
STOCK_END = 0x00482E4C

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


def _channel(first: int, second: int, opacity: int) -> int:
    mix = opacity & 0xFF
    weighted = first * mix + second * (255 - mix)
    return (weighted * 0x8081) >> 23


def _mix(first: int, second: int, opacity: int) -> int:
    return sum(
        _channel(
            (first >> shift) & 0xFF,
            (second >> shift) & 0xFF,
            opacity,
        )
        << shift
        for shift in (0, 8, 16)
    )


class RuntimeColorMixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_color_mix.dylib"
            if sys.platform == "darwin"
            else "runtime_color_mix.so"
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
        cls.execute = cls.loaded.open_cfw_test_runtime_color_mix_execute
        cls.execute.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.execute.restype = ctypes.c_uint32
        for name in ("size", "blue_offset", "green_offset", "red_offset"):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_runtime_color_mix_{name}",
            )
            function.argtypes = []
            function.restype = ctypes.c_uint32

        target_object = Path(cls.temporary.name) / "color_mix.o"
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
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
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

    def test_layout_channel_order_and_padding_carrier_are_explicit(
        self,
    ) -> None:
        self.assertEqual(
            [
                self.loaded.open_cfw_test_runtime_color_mix_size(),
                self.loaded.open_cfw_test_runtime_color_mix_blue_offset(),
                self.loaded.open_cfw_test_runtime_color_mix_green_offset(),
                self.loaded.open_cfw_test_runtime_color_mix_red_offset(),
            ],
            [3, 0, 1, 2],
        )
        first = 0x00112233
        second = 0x00D4E5F6
        for opacity in (0, 1, 63, 127, 128, 254, 255):
            for carrier in (0, 0x5A000000, 0xFF000000):
                observed = self.execute(
                    first,
                    second,
                    opacity,
                    carrier,
                )
                with self.subTest(opacity=opacity, carrier=hex(carrier)):
                    self.assertEqual(observed & 0xFFFFFF, _mix(
                        first,
                        second,
                        opacity,
                    ))
                    self.assertEqual(
                        observed & 0xFF000000,
                        carrier,
                    )

    def test_magic_divider_is_exact_for_the_complete_weighted_range(
        self,
    ) -> None:
        for weighted in range(65026):
            self.assertEqual(
                (weighted * 0x8081) >> 23,
                weighted // 255,
            )

    def test_all_opacities_and_deterministic_color_grid_match_oracle(
        self,
    ) -> None:
        channel_values = [
            0,
            1,
            2,
            15,
            31,
            63,
            127,
            128,
            192,
            224,
            253,
            254,
            255,
        ]
        for opacity in range(256):
            for index, first_channel in enumerate(channel_values):
                second_channel = channel_values[-1 - index]
                first = (
                    first_channel
                    | channel_values[(index + 3) % len(channel_values)] << 8
                    | channel_values[(index + 7) % len(channel_values)] << 16
                )
                second = (
                    second_channel
                    | channel_values[(index + 5) % len(channel_values)] << 8
                    | channel_values[(index + 9) % len(channel_values)] << 16
                )
                observed = self.execute(first, second, opacity, 0)
                with self.subTest(opacity=opacity, index=index):
                    self.assertEqual(observed, _mix(
                        first,
                        second,
                        opacity,
                    ))

    def test_opacity_uses_only_low_byte_for_full_word_arguments(self) -> None:
        generator = random.Random(STOCK_START)
        for case in range(4096):
            first = generator.getrandbits(24)
            second = generator.getrandbits(24)
            low = generator.getrandbits(8)
            opacity = low | (generator.getrandbits(24) << 8)
            carrier = generator.getrandbits(8) << 24
            observed = self.execute(first, second, opacity, carrier)
            with self.subTest(case=case):
                self.assertEqual(
                    observed,
                    carrier | _mix(first, second, low),
                )

    def test_endpoints_identity_and_rounding_policy_are_exact(self) -> None:
        generator = random.Random(0x8081)
        for case in range(2048):
            first = generator.getrandbits(24)
            second = generator.getrandbits(24)
            with self.subTest(case=case):
                self.assertEqual(
                    self.execute(first, second, 0, 0),
                    second,
                )
                self.assertEqual(
                    self.execute(first, second, 255, 0),
                    first,
                )
        self.assertEqual(_channel(0, 1, 127), 0)
        self.assertEqual(_channel(1, 0, 128), 0)
        self.assertEqual(_channel(255, 0, 127), 127)
        self.assertEqual(_channel(255, 0, 128), 128)

    def test_stock_body_padding_writes_and_adjacent_boundaries_are_pinned(
        self,
    ) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(len(body), 116)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "7f812480f5849e8396429428554c8f73"
            "c5511d9f3d476e945af364e85ced0017",
        )
        self.assertEqual(
            body.hex(),
            "33b481b048f281009df806101300dbb29df80a401500edb2"
            "d5f1ff056c4303fb01414143c90d8df802109df805101300"
            "dbb29df809401500edb2d5f1ff056c4303fb01414143c90d"
            "8df801109df804101300dbb29df80840d2b2d2f1ff0202fb"
            "04f203fb01224243d20d8df8002000983ebc7047",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482DAE, STOCK_START)
            ).hexdigest(),
            "3565b5bf9a474304896e0a7acdcab630"
            "e492df488323a00845064736babb0463",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(STOCK_END, 0x00482ED2)
            ).hexdigest(),
            "fb761e3d9b88eaa77c208bb062b5e6f7"
            "b601051cdf466cf8dc9f0f4637603561",
        )

        stores = [
            (0x00482DFE, "8df80210", 2),
            (0x00482E20, "8df80110", 1),
            (0x00482E42, "8df80020", 0),
        ]
        for address, encoded, stack_offset in stores:
            self.assertEqual(
                self.span(address, address + 4).hex(),
                encoded,
            )
            self.assertIn(stack_offset, (0, 1, 2))
        self.assertEqual(
            self.span(0x00482E46, 0x00482E4A).hex(),
            "00983ebc",
        )
        self.assertNotIn("8df803", body.hex())

    def test_callers_and_three_byte_consumers_are_complete(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        raw_dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
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
                    raw_dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x0044CBEA, "36f0f5f8"),
                (0x00452E5E, "2ff0bbff"),
                (0x005C909C, "b9f69cfe"),
                (0x005C90D0, "b9f682fe"),
                (0x005C910E, "b9f663fe"),
                (0x005C914E, "b9f643fe"),
                (0x005C918E, "b9f623fe"),
                (0x005C91CE, "b9f603fe"),
                (0x005C91FA, "b9f6edfd"),
                (0x005C9218, "b9f6defd"),
                (0x005C9242, "b9f6c9fd"),
                (0x005C926E, "b9f6b3fd"),
                (0x005C929A, "b9f69dfd"),
                (0x005C92C6, "b9f687fd"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
            ).hexdigest(),
            "205d15dd4ad3ca2cef7d248205eab58f"
            "f56352467de5db4a2b4472ad263320ab",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            raw_dependencies,
            [(0x00482E38, 0x00687442, "04f203fb")],
        )
        self.assertEqual(
            self.span(0x00482E36, 0x00482E3A).hex(),
            "02fb04f2",
        )

        next_stores = {
            0x0044CBEA: "0290",
            **{
                address: "0090"
                for address, _encoded in callers[1:]
            },
        }
        for address, expected in next_stores.items():
            self.assertEqual(
                self.span(address + 4, address + 6).hex(),
                expected,
            )

        contexts = {
            (0x0044CBDE, 0x0044CC0E):
                "f851a305b820a539a5583b1c22939d24"
                "c69b3115d058c529a3d3293d7d3c8de9",
            (0x00452E52, 0x00452E68):
                "521802c98eea21604eb3476626409d2b"
                "34e42eda83ebe3dfc915d26f310b4f8a",
        }
        for (start, end), expected in contexts.items():
            self.assertEqual(
                hashlib.sha256(self.span(start, end)).hexdigest(),
                expected,
            )

    def test_no_narrow_or_stored_pointer_entry_topology_exists(
        self,
    ) -> None:
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
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
        for target in range(STOCK_START, STOCK_END, 2):
            needle = struct.pack("<I", target | 1)
            position = self.application.find(needle)
            while position >= 0:
                stored.append((APPLICATION_BASE + position, target))
                position = self.application.find(needle, position + 1)
        self.assertEqual(stored, [])

    def test_reviewed_target_clang_abi_text_and_relocations_are_exact(
        self,
    ) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_color_mix": {
                    "offset": 0,
                    "size": 94,
                }
            },
        )
        self.assertEqual(self.target_report["text_size"], 94)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            0,
        )
        self.assertEqual(self.target_report["resolved_relocations"], [])
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "89261a71e0f935349309615ab71404568"
            "e66cf340b5ce71e4e67e6ec195b27df",
        )
        self.assertEqual(
            self.target_text[:4].hex(),
            "b0b5d2b2",
        )
        self.assertEqual(
            self.target_text[-14:].hex(),
            "02ead4321144c0f3c7500844b0bd",
        )

    def test_combined_translation_unit_compatibility(self) -> None:
        sources = [
            "runtime_linked_list_pointer_setters.c",
            "runtime_color_mix.c",
            "runtime_style_default_value.c",
        ]
        translation_unit = "\n".join(
            f'#include "{COMPONENT_ROOT / source}"'
            for source in sources
        ) + "\n"
        combined_object = Path(self.temporary.name) / "combined.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-x",
                "c",
                "-c",
                "-",
                "-o",
                str(combined_object),
            ],
            input=translation_unit,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(combined_object.stat().st_size, 0)

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_color_mix(",
            "unsigned char blue;",
            "unsigned char green;",
            "unsigned char red;",
            "255U - mix",
            "weighted * 0x8081U",
            ">> 23U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_color_mix.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
