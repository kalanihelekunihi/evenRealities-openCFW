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
SOURCE = COMPONENT_ROOT / "runtime_color_over32.c"
MIX_SOURCE = COMPONENT_ROOT / "runtime_color_math.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_color_over32_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x00482EF6
FUNCTION_END = 0x00482F72
MIX_START = 0x00482E4C
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


def _packed(blue: int, green: int, red: int, alpha: int) -> int:
    return blue | green << 8 | red << 16 | alpha << 24


def _mix32(foreground: int, background: int) -> int:
    alpha = foreground >> 24
    if alpha >= 253:
        return (foreground & 0x00FFFFFF) | (background & 0xFF000000)
    if alpha < 3:
        return background

    result = background & 0xFF000000
    for shift in (0, 8, 16):
        source = foreground >> shift & 0xFF
        destination = background >> shift & 0xFF
        lane = (
            source * alpha
            + destination * (255 - alpha)
        ) >> 8
        result |= lane << shift
    return result


def _over32(foreground: int, background: int) -> int:
    foreground_alpha = foreground >> 24
    background_alpha = background >> 24
    if foreground_alpha >= 253 or background_alpha < 3:
        return foreground
    if foreground_alpha < 3:
        return background
    if background_alpha == 255:
        return _mix32(foreground, background)

    composite_alpha = 255 - (
        (255 - foreground_alpha) * (255 - background_alpha) >> 8
    )
    ratio = foreground_alpha * 255 // composite_alpha
    adjusted = (foreground & 0x00FFFFFF) | ratio << 24
    result = _mix32(adjusted, background)
    return (result & 0x00FFFFFF) | composite_alpha << 24


class RuntimeColorOver32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_color_over32.dylib"
            if sys.platform == "darwin"
            else "runtime_color_over32.so"
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
        cls.over = cls.loaded.open_cfw_runtime_color_over32
        cls.reset = cls.loaded.open_cfw_test_runtime_color_over32_reset
        cls.over.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.over.restype = ctypes.c_uint32
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.mix_calls = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_color_over32_mix_calls",
        )
        cls.mix_foreground = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_color_over32_mix_foreground",
        )
        cls.mix_background = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_color_over32_mix_background",
        )
        cls.mix_result = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_color_over32_mix_result",
        )

        target_object = temporary / "runtime_color_over32.o"
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

        combined_source = temporary / "runtime_color_combined.c"
        combined_source.write_text(
            f'#include "{MIX_SOURCE.as_posix()}"\n'
            "#define OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA("
            "foreground, background) \\\n"
            "    open_cfw_runtime_color_mix_alpha("
            "(foreground), (background))\n"
            f'#include "{SOURCE.as_posix()}"\n'
        )
        combined_object = temporary / "runtime_color_combined.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(combined_source),
                "-o",
                str(combined_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        (
            cls.combined_text,
            cls.combined_functions,
            cls.combined_report,
        ) = extract_linked_overlay(combined_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def setUp(self) -> None:
        self.reset()

    def test_packed_bgra_word_abi_and_threshold_precedence(self) -> None:
        foreground = _packed(0x11, 0x22, 0x33, 0x80)
        background = _packed(0x44, 0x55, 0x66, 0x90)
        self.assertEqual(foreground, 0x80332211)
        self.assertEqual(background, 0x90665544)

        for foreground_alpha in (253, 254, 255):
            foreground = _packed(0x11, 0x22, 0x33, foreground_alpha)
            for background_alpha in (0, 2, 3, 255):
                background = _packed(0x44, 0x55, 0x66, background_alpha)
                with self.subTest(
                    foreground_alpha=foreground_alpha,
                    background_alpha=background_alpha,
                ):
                    self.assertEqual(self.over(foreground, background), foreground)
                    self.assertEqual(self.mix_calls.value, 0)

        for background_alpha in (0, 1, 2):
            for foreground_alpha in (0, 1, 2, 3, 252):
                self.reset()
                foreground = _packed(
                    0x11,
                    0x22,
                    0x33,
                    foreground_alpha,
                )
                background = _packed(
                    0x44,
                    0x55,
                    0x66,
                    background_alpha,
                )
                with self.subTest(
                    foreground_alpha=foreground_alpha,
                    background_alpha=background_alpha,
                ):
                    self.assertEqual(self.over(foreground, background), foreground)
                    self.assertEqual(self.mix_calls.value, 0)

        for foreground_alpha in (0, 1, 2):
            for background_alpha in (3, 128, 254, 255):
                self.reset()
                foreground = _packed(
                    0x11,
                    0x22,
                    0x33,
                    foreground_alpha,
                )
                background = _packed(
                    0x44,
                    0x55,
                    0x66,
                    background_alpha,
                )
                with self.subTest(
                    foreground_alpha=foreground_alpha,
                    background_alpha=background_alpha,
                ):
                    self.assertEqual(self.over(foreground, background), background)
                    self.assertEqual(self.mix_calls.value, 0)

    def test_opaque_background_calls_mix_with_unmodified_foreground(self) -> None:
        foreground = _packed(0x12, 0x45, 0x89, 100)
        background = _packed(0xAB, 0x67, 0x23, 255)

        result = self.over(foreground, background)

        self.assertEqual(result, _mix32(foreground, background))
        self.assertEqual(self.mix_calls.value, 1)
        self.assertEqual(self.mix_foreground.value, foreground)
        self.assertEqual(self.mix_background.value, background)
        self.assertEqual(self.mix_result.value, result)

    def test_general_path_computes_alpha_then_ratio_then_overwrites_return(
        self,
    ) -> None:
        foreground = _packed(0x12, 0x45, 0x89, 100)
        background = _packed(0xAB, 0x67, 0x23, 128)
        composite_alpha = 255 - ((155 * 127) >> 8)
        ratio = 100 * 255 // composite_alpha
        adjusted = (foreground & 0x00FFFFFF) | ratio << 24

        result = self.over(foreground, background)

        self.assertEqual(composite_alpha, 179)
        self.assertEqual(ratio, 142)
        self.assertEqual(self.mix_calls.value, 1)
        self.assertEqual(self.mix_foreground.value, adjusted)
        self.assertEqual(self.mix_background.value, background)
        self.assertEqual(
            self.mix_result.value >> 24,
            background >> 24,
        )
        self.assertEqual(result >> 24, composite_alpha)
        self.assertEqual(result, _over32(foreground, background))

    def test_host_result_matches_exhaustive_alpha_oracle(self) -> None:
        foreground_rgb = _packed(0x19, 0x73, 0xD1, 0)
        background_rgb = _packed(0xE2, 0x4B, 0x26, 0)
        for foreground_alpha in range(256):
            foreground = foreground_rgb | foreground_alpha << 24
            for background_alpha in range(256):
                background = background_rgb | background_alpha << 24
                actual = self.over(foreground, background)
                expected = _over32(foreground, background)
                if actual != expected:
                    self.fail(
                        "oracle mismatch for alphas "
                        f"{foreground_alpha}, {background_alpha}: "
                        f"{actual:#010x} != {expected:#010x}"
                    )

    def test_stock_body_dependency_cluster_and_return_padding_are_exact(
        self,
    ) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(len(body), 124)
        self.assertEqual(
            body.hex(),
            "11b581b09df80700fd2804da00919df80300032801da01982fe0"
            "9df80700032801da009829e09df80300ff2806d100990198fff7"
            "90ff009000981ee09df80700d0f1ff009df80340d4f1ff0404fb"
            "00f42412d4f1ff049df80710ff2041432000c0b2b1fbf0f08df8"
            "070000990198fff772ff00908df80340009816bd",
        )
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "a0691979a4d03f0a8e2d014a67c327d"
            "048bf3ab277bca115e77b2f8010e19118",
        )
        dependency_cluster = self.span(MIX_START, FUNCTION_START)
        self.assertEqual(len(dependency_cluster), 170)
        self.assertEqual(
            hashlib.sha256(dependency_cluster).hexdigest(),
            "f5b8586d3d4467ed9de8c40b1a53543"
            "f212156eaf39fb34ba0ac5c69b007c271",
        )
        padding = self.span(FUNCTION_END, 0x00482F74)
        self.assertEqual(padding, b"\x00\x00")
        self.assertEqual(
            hashlib.sha256(padding).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )
        following = self.span(0x00482F74, 0x00482F8A)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "a45dcd36a86fb1508668eeb3b0ecf11a"
            "b7505fa501bed7ebfa93f0d2cf008121",
        )

    def test_callers_and_instruction_aligned_dependencies_are_exact(
        self,
    ) -> None:
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = []
        jumps = []
        interior = []
        raw_dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except BuildError:
                    continue
                if target == FUNCTION_START:
                    (callers if link else jumps).append(
                        (address, encoded.hex())
                    )
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, link))
                if link and FUNCTION_START <= address < FUNCTION_END:
                    raw_dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x0044C578, "36f0bdfc"),
                (0x00452EAC, "30f023f8"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
            ).hexdigest(),
            "b3f1d517474c23b2d5301a8bf62074ae"
            "181bc975d7ca9d323f7cab24156b8aa5",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            raw_dependencies,
            [
                (0x00482F28, MIX_START, "fff790ff"),
                (0x00482F5A, 0x00573078, "f0f08df8"),
                (0x00482F64, MIX_START, "fff772ff"),
            ],
        )
        self.assertEqual(
            self.span(0x00482F58, 0x00482F60).hex(),
            "b1fbf0f08df80700",
        )
        self.assertEqual(
            [
                (0x00482F28, self.span(0x00482F28, 0x00482F2C).hex()),
                (0x00482F64, self.span(0x00482F64, 0x00482F68).hex()),
            ],
            [
                (0x00482F28, "fff790ff"),
                (0x00482F64, "fff772ff"),
            ],
        )

    def test_no_narrow_topology_and_stored_candidates_are_false(
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
            if FUNCTION_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value & 1:
                target = value & ~1
                if FUNCTION_START <= target < FUNCTION_END:
                    stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            stored,
            [
                (0x004D4C05, 0x00482F20),
                (0x0051418D, 0x00482F46),
            ],
        )
        contexts = {
            (0x004D4C00, 0x004D4C10): (
                "08bc220018212f4800f064f8c5f83801",
                "fe6c84865d2ea4393e7adf6ef7f50109"
                "e42083fcd39943f574403c9aa57e4903",
            ),
            (0x00514188, 0x00514198): (
                "3049086070472f480068704731484069",
                "8fc735f3115ad5ac4d658a95fa1cf876"
                "364d86ea82831a3941d278c1b0dc9910",
            ),
        }
        for (start, end), (body_hex, digest) in contexts.items():
            context = self.span(start, end)
            self.assertEqual(context.hex(), body_hex)
            self.assertEqual(hashlib.sha256(context).hexdigest(), digest)

    def test_reviewed_target_clang_artifact_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_color_over32": {
                    "offset": 0,
                    "size": 90,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 90)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            0,
        )
        self.assertEqual(self.target_report["resolved_relocations"], [])
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "ab8cf6eb2c17de57ae8940f556ee1965"
            "d9e1792b126486255ff716c2d664e5b2",
        )

    def test_combined_translation_unit_links_source_mix_dependency(
        self,
    ) -> None:
        self.assertEqual(
            set(self.combined_functions),
            {
                "open_cfw_runtime_color_mix_alpha",
                "open_cfw_runtime_color_brightness",
                "open_cfw_runtime_color_over32",
            },
        )
        self.assertEqual(self.combined_report["rodata_size"], 0)
        self.assertEqual(
            self.combined_report["resolved_relocation_count"],
            2,
        )
        self.assertEqual(
            self.combined_report["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 164,
                    "type": 30,
                    "symbol": "open_cfw_runtime_color_mix_alpha",
                },
                {
                    "section": ".rel.text",
                    "site": 200,
                    "type": 10,
                    "symbol": "open_cfw_runtime_color_mix_alpha",
                },
            ],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_color_over32(",
            "0x00482E4DU",
            "foreground_alpha >= 253U",
            "background_alpha < 3U",
            "foreground_alpha < 3U",
            "background_alpha == 255U",
            "foreground_alpha * 255U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_color_over32.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
