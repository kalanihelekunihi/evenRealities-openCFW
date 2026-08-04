from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
ADAPTER = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "evenhub_lz4_upstream_adapter.c"
)
LEGACY_DECODER = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "evenhub_lz4.c"
)
LEGACY_MODE2 = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "evenhub_decompression.c"
)
UPSTREAM = ROOT / "third_party" / "lz4" / "lz4.c"
CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"

ADAPTER_SHA256 = "83e49a1aeda2d8737db7adfcdce86237602946ea2f883506771468d59ab7151f"
SAFE_SHA256 = "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f"
MODE2_SHA256 = "d2a627965efb0521d9d82b99c176462388495b7e199696bf1a3eafceb619a450"

PROFILE_PINS = {
    "apple-clang": {
        "overlay": (
            123454,
            "9e5004af49fb14a22e7e7ed7357e4c10f87dc8da3a7fb4d7b97fcffcde804c43",
        ),
        "component": (
            3646850,
            "8722e5565bf54dade66fb751155c11ebd128d7a12853e3e4b8671c3c97807827",
        ),
        "legacy": {
            "open_cfw_evenhub_mode2_decompress_legacy": {
                "offset": 12484,
                "size": 30,
            },
            "open_cfw_lz4_decompress_safe_legacy": {
                "offset": 12516,
                "size": 696,
            },
        },
        "active": {
            "LZ4_decompress_safe": {"offset": 116224, "size": 1660},
            "open_cfw_lz4_decompress_safe": {"offset": 117948, "size": 4},
            "open_cfw_evenhub_mode2_decompress": {
                "offset": 117952,
                "size": 30,
            },
        },
        "accounting": (121900, 84654, 84836, 3438528),
    },
    "linux-clang": {
        "overlay": (
            125278,
            "a0a520069e497613b397af1d7327752201ced44c876d6925a7561ae45c91fa7c",
        ),
        "component": (
            3648674,
            "8c477d28a9f58feaf722bd1e00b9767a8ca745ba618515d46339271cd0288c1a",
        ),
        "legacy": {
            "open_cfw_evenhub_mode2_decompress_legacy": {
                "offset": 12488,
                "size": 30,
            },
            "open_cfw_lz4_decompress_safe_legacy": {
                "offset": 12520,
                "size": 650,
            },
        },
        "active": {
            "LZ4_decompress_safe": {"offset": 118052, "size": 1690},
            "open_cfw_lz4_decompress_safe": {"offset": 119808, "size": 4},
            "open_cfw_evenhub_mode2_decompress": {
                "offset": 119812,
                "size": 30,
            },
        },
        "accounting": (123752, 84654, 84836, 3438528),
    },
}

COMMON_TARGET_FLAGS = [
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Lz4UpstreamProductionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.temp = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.target_objects: dict[str, tuple[Path, Path]] = {}
        for repetition in ("a", "b"):
            safe = cls.temp / f"safe-{repetition}.o"
            mode2 = cls.temp / f"mode2-{repetition}.o"
            cls.compile_target(
                safe,
                "OPEN_CFW_LZ4_BUILD_SAFE_ADAPTER",
                cortex_m55=True,
            )
            cls.compile_target(
                mode2,
                "OPEN_CFW_LZ4_BUILD_MODE2_ADAPTER",
                cortex_m55=False,
            )
            cls.target_objects[repetition] = (safe, mode2)
        cls.host = cls.compile_host_library()
        cls.safe = cls.bind_safe(cls.host, "open_cfw_lz4_decompress_safe")
        cls.mode2 = cls.host.open_cfw_evenhub_mode2_decompress
        cls.mode2.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
        ]
        cls.mode2.restype = ctypes.c_uint
        cls.compress = cls.host.LZ4_compress_default
        cls.compress.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_int,
            ctypes.c_int,
        ]
        cls.compress.restype = ctypes.c_int
        cls.compress_bound = cls.host.LZ4_compressBound
        cls.compress_bound.argtypes = [ctypes.c_int]
        cls.compress_bound.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def compile_target(
        cls,
        output: Path,
        macro: str,
        *,
        cortex_m55: bool,
    ) -> None:
        flags = list(COMMON_TARGET_FLAGS)
        if cortex_m55:
            flags.extend(
                ["-mcpu=cortex-m55", "-mllvm", "-enable-machine-outliner=never"]
            )
        subprocess.run(
            [
                cls.clang,
                *flags,
                f"-D{macro}",
                "-c",
                str(ADAPTER),
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def compile_host_library(cls) -> ctypes.CDLL:
        objects = []
        for name, source, defines in (
            ("upstream", UPSTREAM, []),
            ("safe", ADAPTER, ["-DOPEN_CFW_LZ4_BUILD_SAFE_ADAPTER"]),
            ("mode2", ADAPTER, ["-DOPEN_CFW_LZ4_BUILD_MODE2_ADAPTER"]),
        ):
            output = cls.temp / f"host-{name}.o"
            subprocess.run(
                [
                    cls.clang,
                    "-O2",
                    "-fPIC",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    *defines,
                    "-c",
                    str(source),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            objects.append(output)
        library = cls.temp / ("lz4-active.dylib" if sys.platform == "darwin" else "lz4-active.so")
        command = [cls.clang, *(str(item) for item in objects)]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(library))

    @staticmethod
    def bind_safe(library: ctypes.CDLL, name: str) -> Any:
        function = getattr(library, name)
        function.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_int,
            ctypes.c_int,
        ]
        function.restype = ctypes.c_int
        return function

    def extract_target(
        self,
        object_path: Path,
        function_name: str,
    ) -> tuple[bytes, list[tuple[int, int, str]]]:
        module = self.apollo_overlay
        data, sections = module.parse_elf32(object_path)
        symbols = module.parse_elf32_symbols(data, sections)
        section = module.section_named(sections, f".text.{function_name}")
        start = int(section["offset"])
        code = data[start : start + int(section["size"])]
        relocations = []
        for relocation_section in sections:
            if (
                int(relocation_section["type"])
                not in (module.SHT_REL, module.SHT_RELA)
                or int(relocation_section["info"]) != int(section["index"])
            ):
                continue
            self.assertEqual(int(relocation_section["entry_size"]), 8)
            for index in range(
                int(relocation_section["size"])
                // int(relocation_section["entry_size"])
            ):
                offset, info = struct.unpack_from(
                    "<II",
                    data,
                    int(relocation_section["offset"]) + index * 8,
                )
                relocations.append((offset, info & 0xFF, symbols[info >> 8]["name"]))
        return code, sorted(relocations)

    def test_source_and_legacy_boundary_names_are_pinned(self) -> None:
        self.assertEqual(sha256(ADAPTER.read_bytes()), ADAPTER_SHA256)
        decoder_text = LEGACY_DECODER.read_text(encoding="utf-8")
        mode2_text = LEGACY_MODE2.read_text(encoding="utf-8")
        self.assertIn("open_cfw_lz4_decompress_safe_legacy", decoder_text)
        self.assertNotIn("int open_cfw_lz4_decompress_safe(\n", decoder_text)
        self.assertIn("open_cfw_lz4_decompress_safe_legacy", mode2_text)

    def test_target_adapter_leaves_are_deterministic_and_bounded(self) -> None:
        self.assertEqual(
            self.target_objects["a"][0].read_bytes(),
            self.target_objects["b"][0].read_bytes(),
        )
        self.assertEqual(
            self.target_objects["a"][1].read_bytes(),
            self.target_objects["b"][1].read_bytes(),
        )
        safe, safe_relocations = self.extract_target(
            self.target_objects["a"][0],
            "open_cfw_lz4_decompress_safe",
        )
        mode2, mode2_relocations = self.extract_target(
            self.target_objects["a"][1],
            "open_cfw_evenhub_mode2_decompress",
        )
        self.assertEqual((len(safe), sha256(safe)), (4, SAFE_SHA256))
        self.assertEqual((len(mode2), sha256(mode2)), (30, MODE2_SHA256))
        self.assertEqual(
            safe_relocations,
            [(0, self.apollo_overlay.R_ARM_THM_JUMP24, "LZ4_decompress_safe")],
        )
        self.assertEqual(
            mode2_relocations,
            [(16, self.apollo_overlay.R_ARM_THM_CALL, "open_cfw_lz4_decompress_safe")],
        )

    def test_production_config_pins_active_three_leaf_topology(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        names = [
            "LZ4_decompress_safe",
            "open_cfw_lz4_decompress_safe",
            "open_cfw_evenhub_mode2_decompress",
        ]
        leaves_by_name = {
            leaf["function"]: leaf for leaf in config["relocated_leaves"]
        }
        leaves = [leaves_by_name[name] for name in names]
        self.assertEqual([leaf["function"] for leaf in leaves], names)
        legacy_index = config["functions"].index(
            "open_cfw_evenhub_mode2_decompress_legacy"
        )
        self.assertEqual(config["functions"][legacy_index:legacy_index + 5], [
            "open_cfw_evenhub_mode2_decompress_legacy",
            "open_cfw_lz4_decompress_safe_legacy",
            *names,
        ])

        decoder, safe, mode2 = leaves
        self.assertEqual(
            decoder["closure"],
            {
                "text_section": ".text.unlikely.LZ4_decompress_safe",
                "rodata": {
                    "section": ".rodata.cst32",
                    "size": 64,
                    "sha256": (
                        "361b3c2a85717050294fd9e3c6440690de35c0a9455d50e487e"
                        "a8f0881c40f03"
                    ),
                    "alignment": 4,
                    "symbols": [
                        {"name": "inc32table", "offset": 0, "size": 32},
                        {"name": "dec64table", "offset": 32, "size": 32},
                    ],
                },
            },
        )
        self.assertEqual(
            (
                decoder["expected"]["size"],
                decoder["expected"]["closure_size"],
                decoder["expected"]["rodata_offset"],
            ),
            (1660, 1724, 1660),
        )
        linux_decoder = decoder["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux_decoder["closure"]["text_section"],
            ".text.LZ4_decompress_safe",
        )
        self.assertEqual(
            (
                linux_decoder["expected"]["size"],
                linux_decoder["expected"]["closure_size"],
                linux_decoder["expected"]["rodata_offset"],
            ),
            (1690, 1756, 1692),
        )
        self.assertEqual(
            [
                (item["type"], item["symbol"], item.get("target_address"))
                for item in decoder["relocations"]
            ],
            [
                ("R_ARM_THM_CALL", "__aeabi_memcpy", 0x00439BE4),
                ("R_ARM_THM_CALL", "__aeabi_memmove", 0x00439710),
                ("R_ARM_REL32", "inc32table", None),
                ("R_ARM_REL32", "dec64table", None),
            ],
        )
        self.assertEqual(
            [item["type"] for item in linux_decoder["relocations"]],
            [
                "R_ARM_THM_CALL",
                "R_ARM_THM_MOVW_PREL_NC",
                "R_ARM_THM_MOVT_PREL",
                "R_ARM_THM_MOVW_PREL_NC",
                "R_ARM_THM_MOVT_PREL",
                "R_ARM_THM_CALL",
            ],
        )
        self.assertEqual(
            safe["relocations"],
            [
                {
                    "offset": 0,
                    "type": "R_ARM_THM_JUMP24",
                    "symbol": "LZ4_decompress_safe",
                    "target_function": "LZ4_decompress_safe",
                }
            ],
        )
        self.assertEqual(
            mode2["relocations"],
            [
                {
                    "offset": 16,
                    "type": "R_ARM_THM_CALL",
                    "symbol": "open_cfw_lz4_decompress_safe",
                    "target_function": "open_cfw_lz4_decompress_safe",
                }
            ],
        )

        patches = {site["name"]: site for site in config["patch_sites"]}
        self.assertEqual(
            (
                patches["replace_evenhub_mode2_decompress"]["runtime_address"],
                patches["replace_evenhub_mode2_decompress"]["target_function"],
                len(bytes.fromhex(
                    patches["replace_evenhub_mode2_decompress"]["expected_hex"]
                )),
                sha256(bytes.fromhex(
                    patches["replace_evenhub_mode2_decompress"]["expected_hex"]
                )),
            ),
            (
                0x004E0C0C,
                "open_cfw_evenhub_mode2_decompress",
                40,
                "c97a5644f2451934f190a189006304f2a01f8b732fa5dd08711a2cc8272e5fc2",
            ),
        )
        self.assertEqual(
            (
                patches["replace_lz4_decompress_safe"]["runtime_address"],
                patches["replace_lz4_decompress_safe"]["target_function"],
                len(bytes.fromhex(
                    patches["replace_lz4_decompress_safe"]["expected_hex"]
                )),
                sha256(bytes.fromhex(
                    patches["replace_lz4_decompress_safe"]["expected_hex"]
                )),
            ),
            (
                0x0054F338,
                "open_cfw_lz4_decompress_safe",
                30,
                "d824bb067efb6bac662409f00f466631da69272c25c9bea6134c658e713eaef1",
            ),
        )

    def test_reviewed_profile_build_pins_topology_accounting_and_branches(
        self,
    ) -> None:
        version = self.apollo_overlay.compiler_version(self.clang)
        if version.startswith("Apple clang version 21.0.0"):
            profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            profile = "linux-clang"
        else:
            raise unittest.SkipTest(
                "available clang is not a reviewed production profile"
            )
        pins = PROFILE_PINS[profile]
        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        directory = Path(
            tempfile.mkdtemp(dir=build_root, prefix="_test-lz4-production-")
        )
        try:
            report = self.apollo_overlay.build(
                root=ROOT,
                config_path=CONFIG,
                output_dir=directory,
                clang=self.clang,
                toolchain_profile=profile,
            )
            component = (ROOT / report["component"]["artifact"]).read_bytes()
        finally:
            shutil.rmtree(directory, ignore_errors=True)

        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            pins["component"],
        )
        functions = report["overlay"]["functions"]
        for function, expected in {**pins["legacy"], **pins["active"]}.items():
            self.assertEqual(functions[function], expected)
        self.assertEqual(
            (
                report["component"]["source_owned_bytes"],
                report["component"]["generated_patch_site_bytes"],
                report["component"]["replaced_stock_function_bytes"],
                report["component"]["opaque_base_bytes"],
            ),
            pins["accounting"],
        )

        leaves = {
            item["extraction"]["function"]: item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] in pins["active"]
        }
        decoder = leaves["LZ4_decompress_safe"]
        decoder_expected = (
            1724,
            0,
            64,
            "46475de79c8b201f60a15a1e47e0f62a4191002d0bd1fc9fca65ed67916be2f2",
        ) if profile == "apple-clang" else (
            1756,
            2,
            64,
            "7d11b4e84417eb55c625f1ef064f19a07ed81bbf283ebbe87541a4159263f7d2",
        )
        self.assertEqual(
            (
                decoder["extraction"]["closure_size"],
                decoder["extraction"]["internal_padding_size"],
                decoder["extraction"]["rodata"]["size"],
                decoder["extraction"]["closure_sha256"],
            ),
            decoder_expected,
        )
        self.assertEqual(
            report["overlay"]["link"]["relocated_rodata_size"], 282
        )

        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        overlay_runtime = (
            config["run_base"]
            + self.apollo_overlay.align_up(
                config["base"]["size"], config["alignment"]
            )
            - config["preamble_bytes"]
        )
        overlay_payload_offset = self.apollo_overlay.align_up(
            config["base"]["size"], config["alignment"]
        )
        safe_address = (
            overlay_runtime + functions["open_cfw_lz4_decompress_safe"]["offset"]
        )
        safe_offset = (
            overlay_payload_offset
            + functions["open_cfw_lz4_decompress_safe"]["offset"]
        )
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                safe_address,
                component[safe_offset:safe_offset + 4],
                link=False,
            ),
            overlay_runtime + functions["LZ4_decompress_safe"]["offset"],
        )
        mode2_address = (
            overlay_runtime
            + functions["open_cfw_evenhub_mode2_decompress"]["offset"]
        )
        mode2_offset = (
            overlay_payload_offset
            + functions["open_cfw_evenhub_mode2_decompress"]["offset"]
        )
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                mode2_address + 16,
                component[mode2_offset + 16:mode2_offset + 20],
                link=True,
            ),
            safe_address,
        )
        for site_name, target_name in (
            ("replace_evenhub_mode2_decompress", "open_cfw_evenhub_mode2_decompress"),
            ("replace_lz4_decompress_safe", "open_cfw_lz4_decompress_safe"),
        ):
            site = next(
                item for item in config["patch_sites"] if item["name"] == site_name
            )
            component_offset = (
                config["preamble_bytes"]
                + site["runtime_address"]
                - config["run_base"]
            )
            target = self.apollo_overlay.decode_thumb_branch(
                site["runtime_address"],
                component[component_offset:component_offset + 4],
                link=False,
            )
            self.assertEqual(
                target,
                overlay_runtime + functions[target_name]["offset"],
            )
            self.assertEqual(
                component[
                    component_offset + 4:
                    component_offset + len(bytes.fromhex(site["expected_hex"]))
                ],
                b"\x00\xbf" * ((len(bytes.fromhex(site["expected_hex"])) - 4) // 2),
            )

    def test_active_mode2_path_round_trips_and_maps_failures(self) -> None:
        source = (b"Even Realities G2 upstream LZ4 production path\0" * 32)
        source_buffer = (ctypes.c_ubyte * len(source)).from_buffer_copy(source)
        compressed_capacity = int(self.compress_bound(len(source)))
        compressed_buffer = (ctypes.c_ubyte * compressed_capacity)()
        compressed_size = int(
            self.compress(
                source_buffer,
                compressed_buffer,
                len(source),
                compressed_capacity,
            )
        )
        self.assertGreater(compressed_size, 0)
        output = (ctypes.c_ubyte * len(source))()
        self.assertEqual(
            int(self.mode2(compressed_buffer, compressed_size, output, len(source))),
            len(source),
        )
        self.assertEqual(bytes(output), source)

        close_match = bytes.fromhex("10410100505a5a5a5a5a")
        close_input = (ctypes.c_ubyte * len(close_match)).from_buffer_copy(close_match)
        close_output = (ctypes.c_ubyte * 10)()
        self.assertLess(int(self.safe(close_input, close_output, len(close_match), 10)), 0)
        self.assertEqual(int(self.mode2(close_input, len(close_match), close_output, 10)), 0)

        zero_offset = bytes.fromhex("10410000505a5a5a5a5a")
        zero_input = (ctypes.c_ubyte * len(zero_offset)).from_buffer_copy(zero_offset)
        zero_output = (ctypes.c_ubyte * 16)()
        self.assertEqual(int(self.safe(zero_input, zero_output, len(zero_offset), 16)), 10)
        self.assertEqual(int(self.mode2(zero_input, len(zero_offset), zero_output, 16)), 10)
        self.assertEqual(int(self.mode2(None, len(zero_offset), zero_output, 16)), 0)
        self.assertEqual(int(self.mode2(zero_input, 0, zero_output, 16)), 0)
        self.assertEqual(int(self.mode2(zero_input, len(zero_offset), None, 16)), 0)
        self.assertEqual(int(self.mode2(zero_input, len(zero_offset), zero_output, 0)), 0)


if __name__ == "__main__":
    unittest.main()
