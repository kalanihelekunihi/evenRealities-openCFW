from __future__ import annotations

import os

import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_pc_task_get_name.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_pc_task_get_name_host.c"
)
UPSTREAM = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
PRODUCTION_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

APPLICATION_BASE = 0x0043_8000
STOCK_START = 0x0045_4F16
STOCK_END = 0x0045_4F38
STOCK_BYTES = bytes.fromhex(
    "80b5002802d1a1480068ffe7002806d1"
    "a5f1bdf800205ff0ff310860fee7343002bd"
)
STOCK_SHA256 = (
    "a25ace28ece3ca37f11da7e73945acb2"
    "8f1f99d906203613e9856d2070c07817"
)
CALLER = (0x0044_AAEE, "0af012fa")
CALLER_SHA256 = (
    "6b6b656546449e21e970d725927d278f"
    "881d1c0bf448fd732bf3759f73366ee4"
)
CURRENT_TCB_WORD = 0x2007_4A20
CURRENT_TCB_LITERAL = 0x0045_51A4
NAME_OFFSET = 0x34
STACK_DEPTH_OFFSET = 0x54
MASK_FUNCTION = 0x005F_A0A4
NAME_WRITER_START = 0x0045_4976
NAME_WRITER_END = 0x0045_499E
NAME_WRITER_SHA256 = (
    "f59595f8a0b62d16cbeedde20fca564d"
    "9d2687162a2a2bd9208197c382960c10"
)

TARGET_FUNCTION = "open_cfw_freertos_pc_task_get_name"
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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGET_BYTES = bytes.fromhex(
    "28b944f62020c2f20700006808b13430704780b5fff7feff"
    "4ff0ff3000210160bde88040fee7"
)
TARGET_SHA256 = (
    "b680e949844cca19a586fbe865837f81"
    "80e592434ac1517b29ceb1482c9dd3b6"
)
SOURCE_SHA256 = (
    "d46408b0bdce9622ac1fa8c694ccc790"
    "c76169b681d0c413a4ada35fbe29d21a"
)
UPSTREAM_SHA256 = (
    "14020d617b96dd2814e1211f6e3b645b"
    "cf5e2bd3179c23fe7dd16bc666fe9463"
)
UPSTREAM_FUNCTION_SHA256 = (
    "27c5eefcb2b560e54f113eb0db7062bb"
    "4c0d43181467f956076ad7906a9b5ec2"
)

PRODUCTION_OFFSET = 113_932
PRODUCTION_ADDRESS = 0x007B_0030
PRODUCTION_BYTES_SHA256 = (
    "88edbdea558812d213013a8d319a09c6"
    "3dafa86ec91a7640f427c72c77552da1"
)
PRODUCTION_OVERLAY_SIZE = 167_426
PRODUCTION_OVERLAY_SHA256 = (
    "800245ad7f4ba1044f01888fc0141f9f3304bc531773847ba9c0c29e62245491"
)
PRODUCTION_COMPONENT_SIZE = 3_690_822
PRODUCTION_COMPONENT_SHA256 = (
    "9ed3e77e10dd911ae34e9ba17f691f6988c592723b52a9676b8d414554a21459"
)
PACKAGE_SIZE = 4_469_316
PACKAGE_SHA256 = (
    "d4c7f82a3e0cfbfc4476f8ca72c1bfd6a3aba5b13d32c6b924686cbc4d78c10d"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_upstream_function(source: str) -> bytes:
    marker = "char * pcTaskGetName( TaskHandle_t xTaskToQuery )"
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1].encode()
    raise AssertionError("unterminated upstream pcTaskGetName")


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFreeRTOSTaskGetNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_pc_task_get_name.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_pc_task_get_name.so"
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
        cls.host_compile = subprocess.run(
            host_command,
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.host_compile.returncode:
            raise AssertionError(
                cls.host_compile.stderr or cls.host_compile.stdout
            )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_pc_task_get_name_reset
        cls.reset.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls.reset.restype = None
        cls.explicit = cls.loaded.open_cfw_test_pc_task_get_name_explicit
        cls.explicit.restype = ctypes.c_char_p
        cls.current = cls.loaded.open_cfw_test_pc_task_get_name_current
        cls.current.restype = ctypes.c_char_p
        cls.delta = cls.loaded.open_cfw_test_pc_task_get_name_explicit_delta
        cls.delta.restype = ctypes.c_size_t
        cls.mask_calls = (
            cls.loaded.open_cfw_test_pc_task_get_name_mask_calls
        )
        cls.mask_calls.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_pc_task_get_name.o"
        cls.target_compile = subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.target_compile.returncode:
            raise AssertionError(
                cls.target_compile.stderr or cls.target_compile.stdout
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw
        cls.elf, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.symbols = apollo_overlay.parse_elf32_symbols(
            cls.elf,
            cls.sections,
        )
        cls.sections_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        text = cls.sections_by_name[f".text.{TARGET_FUNCTION}"]
        cls.target_text = cls.elf[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]

        production_output = temporary / "production"
        cls.production_report = apollo_overlay.build(
            root=ROOT,
            config_path=PRODUCTION_CONFIG,
            output_dir=production_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.production_overlay = (
            production_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.production_component = (
            production_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_upstream_and_source_are_exact(self) -> None:
        self.assertEqual(UPSTREAM.stat().st_size, 223_695)
        self.assertEqual(sha256(UPSTREAM.read_bytes()), UPSTREAM_SHA256)
        block = extract_upstream_function(UPSTREAM.read_text())
        self.assertEqual(len(block), 375)
        self.assertEqual(sha256(block), UPSTREAM_FUNCTION_SHA256)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

        source = SOURCE.read_text()
        self.assertEqual(SOURCE.stat().st_size, 3_489)
        self.assertEqual(sha256(source.encode()), SOURCE_SHA256)
        for marker in (
            "SPDX-License-Identifier: MIT",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "task_name[32]",
            "task_name",
            "0x34U",
            "0x54U",
            "0x20074A20U",
            "ulSetInterruptMask",
            "0xFFFFFFFFU",
        ):
            self.assertIn(marker, source)

    def test_stock_boundary_layout_writer_and_assert_dependency(self) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(body, STOCK_BYTES)
        self.assertEqual(len(body), 34)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(self.span(STOCK_START - 6, STOCK_START).hex(),
                         "a34800687047")
        self.assertEqual(self.span(STOCK_END, STOCK_END + 12).hex(),
                         "2de9f0410700884615000026")
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(CURRENT_TCB_LITERAL, CURRENT_TCB_LITERAL + 4),
            )[0],
            CURRENT_TCB_WORD,
        )
        writer = self.span(NAME_WRITER_START, NAME_WRITER_END)
        self.assertEqual(len(writer), 40)
        self.assertEqual(sha256(writer), NAME_WRITER_SHA256)
        self.assertEqual(NAME_OFFSET, 0x34)
        self.assertEqual(STACK_DEPTH_OFFSET, 0x54)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                0x0045_4F26,
                self.span(0x0045_4F26, 0x0045_4F2A),
                link=True,
            ),
            MASK_FUNCTION,
        )

    def test_stock_reference_topology_is_closed(self) -> None:
        calls = []
        jumps = []
        interiors = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in ((True, calls), (False, jumps)):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target == STOCK_START and not (
                    STOCK_START <= address < STOCK_END
                ):
                    destination.append((address, encoded.hex()))
                if STOCK_START < target < STOCK_END and not (
                    STOCK_START <= address < STOCK_END
                ):
                    interiors.append((address, target, link))
        self.assertEqual(calls, [CALLER])
        self.assertEqual(jumps, [])
        self.assertEqual(interiors, [])
        self.assertEqual(
            sha256(struct.pack("<I", CALLER[0])),
            CALLER_SHA256,
        )

        byte_windows = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1 if value & 1 else value
            if STOCK_START <= canonical < STOCK_END:
                byte_windows.append((APPLICATION_BASE + offset, canonical))
        self.assertEqual(byte_windows, [(0x004A_56B7, 0x0045_4F20)])
        self.assertEqual(
            self.span(0x004A_56B4, 0x004A_56BC).hex(),
            "4e4500204f450020",
        )

    def test_host_behavior_uses_explicit_or_current_tcb_name(self) -> None:
        self.assertEqual(self.host_compile.stderr, "")
        self.reset(b"explicit-task", b"current-task")
        self.assertEqual(self.explicit(), b"explicit-task")
        self.assertEqual(self.current(), b"current-task")
        self.assertEqual(self.delta(), NAME_OFFSET)
        self.assertEqual(self.mask_calls(), 0)

        self.reset(b"x" * 40, b"y" * 40)
        self.assertEqual(self.explicit(), b"x" * 31)
        self.assertEqual(self.current(), b"y" * 31)
        self.assertEqual(self.mask_calls(), 0)

    def test_target_section_and_direct_relocation_are_exact(self) -> None:
        self.assertEqual(self.target_compile.stderr, "")
        self.assertEqual(self.target_text, TARGET_BYTES)
        self.assertEqual(len(self.target_text), 38)
        self.assertEqual(sha256(self.target_text), TARGET_SHA256)
        text = self.sections_by_name[f".text.{TARGET_FUNCTION}"]
        self.assertEqual(int(text["alignment"]), 4)
        self.assertEqual(int(text["flags"]) & 7, 6)

        symbols_by_name = {
            str(symbol["name"]): symbol for symbol in self.symbols
        }
        function = symbols_by_name[TARGET_FUNCTION]
        self.assertEqual(int(function["binding"]), 1)
        self.assertEqual(int(function["type"]), 2)
        self.assertEqual(int(function["size"]), 38)
        self.assertEqual(int(function["section_index"]), int(text["index"]))
        relocation_section = self.sections_by_name[
            f".rel.text.{TARGET_FUNCTION}"
        ]
        relocations = []
        for entry in range(
            int(relocation_section["offset"]),
            int(relocation_section["offset"]) +
            int(relocation_section["size"]),
            8,
        ):
            offset, information = struct.unpack_from(
                "<II",
                self.elf,
                entry,
            )
            relocations.append(
                (
                    offset,
                    information & 0xFF,
                    str(self.symbols[information >> 8]["name"]),
                )
            )
        self.assertEqual(
            relocations,
            [(0x14, 10, "ulSetInterruptMask")],
        )
        self.assertEqual(
            int(symbols_by_name["ulSetInterruptMask"]["section_index"]),
            0,
        )

    @_APPLE_ONLY
    def test_production_redirect_relocation_and_accounting_are_exact(
        self,
    ) -> None:
        report = self.production_report
        self.assertEqual(
            (
                len(self.production_overlay),
                sha256(self.production_overlay),
            ),
            (PRODUCTION_OVERLAY_SIZE, PRODUCTION_OVERLAY_SHA256),
        )
        self.assertEqual(
            (
                len(self.production_component),
                sha256(self.production_component),
            ),
            (PRODUCTION_COMPONENT_SIZE, PRODUCTION_COMPONENT_SHA256),
        )
        leaf = next(
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == TARGET_FUNCTION
        )
        self.assertEqual(
            leaf["placement"],
            {
                "offset": PRODUCTION_OFFSET,
                "size": 38,
                "alignment": 4,
                "padding_before": 0,
                "runtime_address": PRODUCTION_ADDRESS,
                "runtime_address_hex": "0x007B0030",
            },
        )
        extraction = leaf["extraction"]
        self.assertEqual(extraction["sha256"], PRODUCTION_BYTES_SHA256)
        self.assertEqual(extraction["unrelocated_sha256"], TARGET_SHA256)
        self.assertEqual(extraction["relocation_count"], 1)
        relocation = extraction["relocations"][0]
        self.assertEqual(
            (
                relocation["offset"],
                relocation["symbol"],
                relocation["runtime_address"],
                relocation["target_address"],
            ),
            (0x14, "ulSetInterruptMask", 0x007B_0044, 0x007A_FF08),
        )
        body = self.production_overlay[
            PRODUCTION_OFFSET:PRODUCTION_OFFSET + 38
        ]
        self.assertEqual(sha256(body), PRODUCTION_BYTES_SHA256)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                PRODUCTION_ADDRESS + 0x14,
                body[0x14:0x18],
                link=True,
            ),
            0x007A_FF08,
        )

        patch = next(
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_freertos_pc_task_get_name"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(len(replacement), 34)
        self.assertEqual(
            sha256(replacement),
            "5fdaf5ca8faaca2855e409fde59b9e094"
            "57464aecca303cff240b58a5e018649",
        )
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                replacement[:4],
                link=False,
            ),
            PRODUCTION_ADDRESS,
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 15)
        self.assertEqual(
            {
                key: report["component"][key]
                for key in (
                    "generated_patch_site_bytes",
                    "opaque_base_bytes",
                    "replaced_stock_function_bytes",
                    "source_owned_bytes",
                )
            },
            {
                "generated_patch_site_bytes": 121_634,
                "opaque_base_bytes": 3_401_548,
                "replaced_stock_function_bytes": 121_812,
                "source_owned_bytes": 165_622,
            },
        )

    @_APPLE_ONLY
    def test_manifest_regions_and_package_identity_are_reversible(
        self,
    ) -> None:
        manifest, _root, payloads = self.open_cfw.verify_manifest(
            SOURCE_MANIFEST
        )
        image, _entries = self.open_cfw.assemble_evenota(
            manifest,
            payloads,
        )
        self.assertEqual(len(image), PACKAGE_SIZE)
        self.assertEqual(sha256(image), PACKAGE_SHA256)
        main = next(
            item
            for item in manifest["components"]
            if item["name"] == "apollo_main"
        )
        regions = {
            region["name"]: region
            for region in main["regions"]
            if "pc_task_get_name" in region["name"]
        }
        self.assertEqual(
            {
                name: (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                )
                for name, region in regions.items()
            },
            {
                "freertos_pc_task_get_name_source_replacement": (
                    118_582,
                    34,
                    STOCK_START,
                    "generated_source_entry_replacement",
                ),
                "opaque_between_freertos_pc_task_get_name_and_task_increment_tick": (
                    118_616,
                    276,
                    STOCK_END,
                    "official_blob",
                ),
                "apollo_freertos_pc_task_get_name_source_leaf": (
                    3_637_328,
                    38,
                    PRODUCTION_ADDRESS,
                    "source_compiled",
                ),
            },
        )
        component = payloads["apollo_main"]
        official = OFFICIAL.read_bytes()
        reconstructed = bytearray(component)
        reconstructed[118_582:118_616] = official[118_582:118_616]
        self.assertEqual(
            reconstructed[118_582:118_616],
            official[118_582:118_616],
        )
        self.assertEqual(
            component[3_637_328:3_637_366],
            self.production_overlay[PRODUCTION_OFFSET:PRODUCTION_OFFSET + 38],
        )

        historical_overlay = self.production_overlay[:113_970]
        self.assertEqual(
            sha256(historical_overlay),
            "dba3b91264a8437ea5f44d872b41a712"
            "3d6dd70e7816bdab7d6bff82d2c93ca9",
        )
        historical_component = bytearray(component)
        # Undo the newest FreeRTOS reset/unordered-event production pair
        # before applying the older historical inverses below.
        historical_component[38_198:38_378] = official[38_198:38_378]
        historical_component[119_964:120_182] = official[119_964:120_182]
        historical_component[71_484:71_638] = official[71_484:71_638]
        # The production image now also redirects both watchdog entries.
        # This historical checkpoint predates that milestone, so restore the
        # exact stock bodies before truncating the appended source tail.
        historical_component[1_012_480:1_012_544] = official[
            1_012_480:1_012_544
        ]
        historical_component[1_012_544:1_012_620] = official[
            1_012_544:1_012_620
        ]
        for offset, size in (
            # Scheduler-start core admitted after this historical milestone.
            (41_474, 46),
            (118_028, 144),
            (119_252, 206),
            (21_908, 1_026),
            (68_974, 132),
            (76_448, 24),
            (41_180, 20),
            (41_200, 24),
            (41_224, 44),
            (40_036, 354),
            (22_940, 106),
            (23_056, 26),
            (23_082, 26),
            (123_184, 256),
            (123_440, 112),
            (123_552, 90),
            (123_642, 94),
            (40_642, 34),
            (71_866, 180),
            (79_496, 162),
            (118_172, 12),
            (118_252, 306),
            (118_558, 8),
            (118_566, 10),
            (118_892, 338),
            (39_522, 200),
            (119_696, 246),
            (120_182, 16),
            (120_198, 128),
            (120_326, 10),
            (120_896, 22),
            (120_982, 38),
            (121_578, 22),
            (121_600, 22),
            # Charger-common eleven-body production cluster.
            (479_132, 240),
            (479_372, 94),
            (479_466, 464),
            (479_930, 450),
            (480_380, 226),
            (480_606, 276),
            (480_882, 372),
            (481_276, 142),
            (481_440, 122),
            (481_562, 6),
            (481_568, 8),
            # Goodix-derived application-error handler admitted later.
            (858_984, 178),
        ):
            historical_component[offset:offset + size] = official[
                offset:offset + size
            ]
        for offset, replacement_hex in (
            (
                691_244,
                "b6f2ecbb00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            ),
            (
                1_143_640,
                "48f266b800bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf",
            ),
        ):
            replacement = bytes.fromhex(replacement_hex)
            historical_component[offset:offset + len(replacement)] = (
                replacement
            )
        del historical_component[3_637_366:]
        first_word = struct.unpack_from("<I", historical_component, 0)[0]
        struct.pack_into(
            "<I",
            historical_component,
            0,
            (first_word & 0xFF000000) | len(historical_component),
        )
        struct.pack_into(
            "<I",
            historical_component,
            4,
            zlib.crc32(historical_component[8:]) & 0xFFFFFFFF,
        )
        self.assertEqual(
            sha256(bytes(historical_component)),
            "340120823caa5d95dc9c75199edb8f9915849d8ccc3ffe58e5474bc2d3324cd6",
        )
        historical_payloads = dict(payloads)
        historical_payloads["apollo_main"] = bytes(historical_component)
        historical_image, _entries = self.open_cfw.assemble_evenota(
            manifest,
            historical_payloads,
        )
        self.assertEqual(len(historical_image), 4_415_860)
        self.assertEqual(
            sha256(historical_image),
            "798f8d74b0b7062997d7c4949a6fe0254e82f96db3f3102cf9cb6d116dcdc1de",
        )


if __name__ == "__main__":
    unittest.main()
