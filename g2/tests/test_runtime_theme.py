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
SOURCE = COMPONENT_ROOT / "runtime_theme.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_theme_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTIONS = {
    "get_from_object": (0x00482F74, 0x00482F8A),
    "apply": (0x00482F8A, 0x00482FAA),
    "primary_color": (0x00482FAA, 0x00482FCE),
}
EVENT_CAPACITY = 16
EVENT_OBJECT_GET_DISPLAY = 1
EVENT_DISPLAY_GET_DEFAULT = 2
EVENT_DISPLAY_GET_THEME = 3
EVENT_OBJECT_REMOVE_STYLES = 4
EVENT_APPLY_RECURSION = 5
EVENT_COPY = 6
EVENT_PALETTE_MAIN = 7

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


class RuntimeThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_theme.dylib"
            if sys.platform == "darwin"
            else "runtime_theme.so"
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
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.set_primary = (
            cls.loaded.open_cfw_test_runtime_theme_set_primary_color
        )
        cls.set_primary.argtypes = [ctypes.c_uint32]
        cls.set_primary.restype = None
        cls.execute_get = cls.loaded.open_cfw_test_runtime_theme_execute_get
        cls.execute_get.argtypes = [ctypes.c_uint32]
        cls.execute_get.restype = ctypes.c_uint32
        cls.execute_apply = (
            cls.loaded.open_cfw_test_runtime_theme_execute_apply
        )
        cls.execute_apply.argtypes = [ctypes.c_uint32]
        cls.execute_apply.restype = None
        cls.execute_primary = (
            cls.loaded.open_cfw_test_runtime_theme_execute_primary
        )
        cls.execute_primary.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.execute_primary.restype = ctypes.c_uint32
        cls.event_kind = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_event_kind",
        )
        cls.event_first = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_event_first",
        )
        cls.event_second = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_event_second",
        )
        cls.event_third = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_theme_event_third",
        )

        target_object = Path(cls.temporary.name) / "theme.o"
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

    def events(self) -> list[tuple[int, int, int, int]]:
        count = self.uint("open_cfw_test_runtime_theme_event_count").value
        self.assertLessEqual(count, EVENT_CAPACITY)
        return [
            (
                self.event_kind[index],
                self.event_first[index],
                self.event_second[index],
                self.event_third[index],
            )
            for index in range(count)
        ]

    def test_theme_resolution_selects_object_or_default_display(self) -> None:
        object_pointer = 0x10203040
        object_display = 0x20001000
        default_display = 0x20002000
        theme = 0x280
        self.reset(object_display, default_display, theme, 0)
        self.assertEqual(self.execute_get(object_pointer), theme)
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_OBJECT_GET_DISPLAY,
                    object_pointer,
                    object_display,
                    0,
                ),
                (EVENT_DISPLAY_GET_THEME, object_display, theme, 0),
            ],
        )

        self.reset(object_display, default_display, theme, 0)
        self.assertEqual(self.execute_get(0), theme)
        self.assertEqual(
            self.events(),
            [
                (EVENT_DISPLAY_GET_DEFAULT, default_display, 0, 0),
                (EVENT_DISPLAY_GET_THEME, default_display, theme, 0),
            ],
        )

    def test_null_display_is_forwarded_without_validation(self) -> None:
        for object_pointer in (0, 0x12345678):
            self.reset(0, 0, 0x340, 0)
            self.assertEqual(self.execute_get(object_pointer), 0x340)
            with self.subTest(object_pointer=object_pointer):
                self.assertEqual(
                    self.events()[-1],
                    (EVENT_DISPLAY_GET_THEME, 0, 0x340, 0),
                )

    def test_apply_removes_styles_then_recurses_only_with_theme(self) -> None:
        object_pointer = 0x55667788
        display = 0x20003000
        theme = 0x240
        self.reset(display, 0, theme, 0)
        self.execute_apply(object_pointer)
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_OBJECT_GET_DISPLAY,
                    object_pointer,
                    display,
                    0,
                ),
                (EVENT_DISPLAY_GET_THEME, display, theme, 0),
                (EVENT_OBJECT_REMOVE_STYLES, object_pointer, 0, 0),
                (
                    EVENT_APPLY_RECURSION,
                    theme,
                    object_pointer,
                    0,
                ),
            ],
        )

        self.reset(display, 0, 0, 0)
        self.execute_apply(object_pointer)
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_OBJECT_GET_DISPLAY,
                    object_pointer,
                    display,
                    0,
                ),
                (EVENT_DISPLAY_GET_THEME, display, 0, 0),
            ],
        )

    def test_primary_color_copies_exact_three_byte_bgr_field(self) -> None:
        generator = random.Random(0x00482FAA)
        object_pointer = 0x12345678
        display = 0x20004000
        theme = 0x180
        for case in range(512):
            color = generator.getrandbits(24)
            carrier = generator.getrandbits(8) << 24
            self.reset(display, 0, theme, 0)
            self.set_primary(color)
            observed = self.execute_primary(object_pointer, carrier)
            with self.subTest(case=case):
                self.assertEqual(observed, carrier | color)
                self.assertEqual(
                    self.events(),
                    [
                        (
                            EVENT_OBJECT_GET_DISPLAY,
                            object_pointer,
                            display,
                            0,
                        ),
                        (EVENT_DISPLAY_GET_THEME, display, theme, 0),
                        (EVENT_COPY, theme + 0x10, 3, 0),
                    ],
                )

    def test_primary_color_fallback_uses_blue_grey_palette_17(self) -> None:
        object_pointer = 0xA0B0C0D0
        display = 0x20005000
        fallback = 0x00A1B2C3
        for carrier in (0, 0x5A000000, 0xFF000000):
            self.reset(display, 0, 0, fallback)
            observed = self.execute_primary(object_pointer, carrier)
            with self.subTest(carrier=hex(carrier)):
                self.assertEqual(observed, carrier | fallback)
                self.assertEqual(
                    self.events(),
                    [
                        (
                            EVENT_OBJECT_GET_DISPLAY,
                            object_pointer,
                            display,
                            0,
                        ),
                        (EVENT_DISPLAY_GET_THEME, display, 0, 0),
                        (EVENT_PALETTE_MAIN, 0x11, 0, 0),
                    ],
                )

    def test_stock_functions_and_adjacent_spans_are_exact(self) -> None:
        expected = {
            "get_from_object": (
                22,
                "a45dcd36a86fb1508668eeb3b0ecf11a"
                "b7505fa501bed7ebfa93f0d2cf008121",
            ),
            "apply": (
                32,
                "adcadcb716c018d786a76ab81df356c1"
                "857bdac6b505aba7d8c93bf98e729458",
            ),
            "primary_color": (
                36,
                "e0736b76b156e169dc6ccb048ac3f174"
                "ae428d9f2bf932a959daf3b08e47a680",
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            size, digest = expected[name]
            with self.subTest(name=name):
                self.assertEqual(len(body), size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        cluster = self.span(0x00482F74, 0x00482FCE)
        self.assertEqual(len(cluster), 90)
        self.assertEqual(
            hashlib.sha256(cluster).hexdigest(),
            "7e0a30860c051b990a19bd02045a981a"
            "ed535b61e6a500bfdaa932668ca13dbf",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482EF6, 0x00482F74)
            ).hexdigest(),
            "a7592268b38ddf26d83350adb19100ce"
            "d38a1416416097a2cd3f72f9ba4c3764",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482FCE, 0x00482FF2)
            ).hexdigest(),
            "2fef5af03427a5ec0dbe61a99b4296b"
            "0339d78a6ec60da85fa55ceab65b821d7",
        )

    def test_callers_dependencies_and_return_use_are_exact(self) -> None:
        expected_callers = {
            "get_from_object": [
                (0x00482F90, "fff7f0ff"),
                (0x00482FAC, "fff7e2ff"),
            ],
            "apply": [
                (0x0044D106, "35f040ff"),
                (0x0044FE78, "33f087f8"),
            ],
            "primary_color": [
                (0x005C3FE4, "bef6e1ff"),
                (0x005C4006, "bef6d0ff"),
                (0x005C404C, "bef6adff"),
                (0x005C9002, "b9f6d2ff"),
            ],
        }
        expected_digests = {
            "get_from_object":
                "d40e8e00cb417217e50cd86dee00b9af"
                "66c8f6db619b33a864aaf0f09fc6cf1e",
            "apply":
                "cda840185cd376aa1c841a008aa969dd"
                "4a0ea0d7b9f19cc002883dbdc9947c6f",
            "primary_color":
                "c573fd6a739dd91d8b7bc8504da2d15c"
                "7a88e79d52c4c7ef2a9cd0ccc2520aee",
        }
        expected_dependencies = {
            "get_from_object": [
                (0x00482F7A, 0x0044DC0A, "caf746fe"),
                (0x00482F80, 0x0044FA1A, "ccf74bfd"),
                (0x00482F84, 0x0044FE7E, "ccf77bff"),
            ],
            "apply": [
                (0x00482F90, 0x00482F74, "fff7f0ff"),
                (0x00482F9C, 0x0044BC3A, "c8f74dfe"),
                (0x00482FA4, 0x00482FF2, "00f025f8"),
            ],
            "primary_color": [
                (0x00482FAC, 0x00482F74, "fff7e2ff"),
                (0x00482FBC, 0x00439BE4, "b6f712fe"),
                (0x00482FC4, 0x00488290, "05f064f9"),
            ],
        }
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interior = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
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
                        interior[name].append((address, target, link))
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )
        for name in FUNCTIONS:
            with self.subTest(name=name):
                self.assertEqual(callers[name], expected_callers[name])
                self.assertEqual(
                    hashlib.sha256(
                        b"".join(
                            struct.pack("<I", address)
                            for address, _encoded in callers[name]
                        )
                    ).hexdigest(),
                    expected_digests[name],
                )
                self.assertEqual(jumps[name], [])
                self.assertEqual(interior[name], [])
                self.assertEqual(
                    dependencies[name],
                    expected_dependencies[name],
                )

        self.assertEqual(
            self.span(0x0044D106, 0x0044D10C).hex(),
            "35f040ff2900",
        )
        self.assertEqual(
            self.span(0x0044FE78, 0x0044FE7E).hex(),
            "33f087f831bd",
        )
        for address, _encoded in expected_callers["primary_color"]:
            self.assertEqual(
                self.span(address + 4, address + 6).hex(),
                "0090",
            )

    def test_primary_return_padding_is_nonsemantic_saved_stack_data(
        self,
    ) -> None:
        body = self.span(*FUNCTIONS["primary_color"])
        self.assertEqual(body[:2].hex(), "80b5")
        self.assertEqual(
            self.span(0x00482FB6, 0x00482FC0).hex(),
            "684610310322b6f712fe",
        )
        self.assertEqual(
            self.span(0x00482FC8, 0x00482FCE).hex(),
            "0090009802bd",
        )
        self.assertNotIn("8df803", body.hex())

    def test_no_narrow_or_stored_pointer_topology_exists(self) -> None:
        narrow_entry = {name: [] for name in FUNCTIONS}
        narrow_interior = {name: [] for name in FUNCTIONS}
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
            for name, (start, end) in FUNCTIONS.items():
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
        self.assertEqual(narrow_entry, {name: [] for name in FUNCTIONS})
        self.assertEqual(narrow_interior, {name: [] for name in FUNCTIONS})

        stored = {name: [] for name in FUNCTIONS}
        for name, (start, end) in FUNCTIONS.items():
            for target in range(start, end, 2):
                needle = struct.pack("<I", target | 1)
                position = self.application.find(needle)
                while position >= 0:
                    stored[name].append(
                        (APPLICATION_BASE + position, target)
                    )
                    position = self.application.find(
                        needle,
                        position + 1,
                    )
        self.assertEqual(stored, {name: [] for name in FUNCTIONS})

    def test_reviewed_target_clang_output_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_theme_get_from_object": {
                    "offset": 0,
                    "size": 40,
                },
                "open_cfw_runtime_theme_apply": {
                    "offset": 40,
                    "size": 46,
                },
                "open_cfw_runtime_theme_get_primary_color": {
                    "offset": 88,
                    "size": 62,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 150)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            2,
        )
        self.assertEqual(
            self.target_report["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 44,
                    "symbol":
                        "open_cfw_runtime_theme_get_from_object",
                    "type": 10,
                },
                {
                    "section": ".rel.text",
                    "site": 92,
                    "symbol":
                        "open_cfw_runtime_theme_get_from_object",
                    "type": 10,
                },
            ],
        )
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "6f6ea5547ce391fdaea0322fa5efaf51"
            "dc66edf3988b4a2b35b09fb24c43cfb0",
        )
        expected_hashes = {
            "open_cfw_runtime_theme_get_from_object":
                "f105630b3b99fdffe2f38ce7e963e6db"
                "88fcdf6c2a077ea221690421518365aa",
            "open_cfw_runtime_theme_apply":
                "17404ef1c3c3b50c6bd98ed6d795d772"
                "caa2cb870390d6c5dfff4d8fa0cf1351",
            "open_cfw_runtime_theme_get_primary_color":
                "03fee14bb95305dafd30732bbac3b3339"
                "4c359c15ec82795136543373239337b",
        }
        for name, expected in expected_hashes.items():
            info = self.target_functions[name]
            body = self.target_text[
                info["offset"]:info["offset"] + info["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_combined_translation_unit_compatibility(self) -> None:
        sources = [
            "runtime_color_mix.c",
            "runtime_color_math.c",
            "runtime_color_over32.c",
            "runtime_theme.c",
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

    def test_source_and_fixture_hashes_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "9a9b7580339ac10d4c663d2c318d415a"
            "e623549bfe996344cd38534ab1466df5",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "54c6c652dcec0071855c7ad530dafb503"
            "7dc0fafaf95587bf5d9238a9aae9e0b",
        )


if __name__ == "__main__":
    unittest.main()
