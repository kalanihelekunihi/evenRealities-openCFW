from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import os
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
CONFIG_PATH = COMPONENT / "overlay.json"
BUILDER_PATH = COMPONENT / "build_component.py"
AMBIQ_SOURCE = (
    ROOT
    / "third_party"
    / "ambiqsuite-apollo510"
    / "mcu"
    / "apollo510"
    / "hal"
    / "mcu"
    / "am_hal_mspi.c"
)
AMBIQ_SOURCE_SHA256 = (
    "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"
)
AMBIQ_LEAF_SHA256 = (
    "87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b"
)
MLIST_ISOPEN_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_littlefs_mlist_isopen.c"
)
MLIST_ISOPEN_SOURCE_SHA256 = (
    "7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c"
)
MLIST_ISOPEN_LEAF_SHA256 = (
    "9b7caac591f8aea5d0eff0dc2b5ff7ff15ba85ab156ba5f95d47b1e4181db489"
)
LITTLEFS_UTIL_ENDIAN_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_littlefs_util_endian.c"
)
LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256 = (
    "830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac"
)
LITTLEFS_UTIL_IDENTITY_LEAF_SHA256 = (
    "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"
)
LITTLEFS_UTIL_SWAP_LEAF_SHA256 = (
    "7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11"
)
BOOT_OVERLAY_SHA256 = (
    "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314"
)

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_bootloader_isolated_leaf_builder",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bootloader core-overlay builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact Apple-clang assertion; Linux byte reproduction is covered by "
    "tests/test_toolchain_profiles.py",
)


class BootloaderIsolatedLeafTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.builder = load_builder()

    @staticmethod
    def isolated_flags() -> list[str]:
        return [
            "-mcpu=cortex-m55",
            "-mthumb",
            "-Oz",
            "-ffreestanding",
            "-fno-builtin",
            "-ffunction-sections",
            "-fdata-sections",
        ]

    def test_synthetic_boot_config_appends_authenticated_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "primary.c"
            source.write_text("void primary(void) {}\n", encoding="utf-8")
            upstream = root / "upstream.c"
            upstream.write_text(
                "__attribute__((noinline))\n"
                "unsigned reviewed_leaf(unsigned value) {\n"
                "    return value ^ 0x12345678u;\n"
                "}\n",
                encoding="utf-8",
            )
            headers = root / "headers"
            headers.mkdir()

            probe_object = root / "probe.o"
            subprocess.run(
                [
                    self.clang,
                    "--target=arm-none-eabi",
                    *self.isolated_flags(),
                    "-c",
                    str(upstream),
                    "-o",
                    str(probe_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            leaf, extraction = (
                apollo_overlay.extract_isolated_function_section(
                    probe_object,
                    "reviewed_leaf",
                )
            )

            primary_overlay = b"\x00\xbf\x00"
            primary_functions = {"primary": {"offset": 0, "size": 2}}
            leaf_report = {
                "source": {"path": "upstream.c"},
                "toolchain": {"target": "arm-none-eabi"},
                "extraction": extraction,
            }
            (
                expected_overlay,
                expected_functions,
                _link_report,
                _placement_reports,
            ) = apollo_overlay.append_isolated_leaves(
                overlay=primary_overlay,
                functions=primary_functions,
                link_report={
                    "text_size": 2,
                    "rodata_size": 1,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
                leaves=[(leaf, leaf_report)],
            )

            run_base = 0x00410000
            base = struct.pack("<II", 0x20000100, run_base + 5)
            base_path = root / "base.bin"
            base_path.write_bytes(base)
            expected_provider = base + expected_overlay
            leaf_config = {
                "function": "reviewed_leaf",
                "source": {
                    "path": "upstream.c",
                    "sha256": digest(upstream.read_bytes()),
                    "license": "test-only",
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": self.isolated_flags(),
                },
                "expected": {
                    "size": len(leaf),
                    "sha256": digest(leaf),
                },
            }
            config = {
                "schema_version": 1,
                "target": "apollo_bootloader",
                "name": "boot-isolated-probe",
                "firmware_version": "test",
                "preamble_bytes": 0,
                "run_base": run_base,
                "partition_end_exclusive": run_base + 0x100,
                "alignment": 4,
                "padding_byte": 0,
                "placement": {
                    "strategy": "fixed_aligned_after_authenticated_stock_eof",
                    "runtime_address": run_base + len(base),
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": ["-mthumb"],
                    "include_dirs": ["headers"],
                },
                "sources": [
                    {
                        "path": "primary.c",
                        "sha256": digest(source.read_bytes()),
                    }
                ],
                "isolated_leaves": [leaf_config],
                "base": {
                    "path": "base.bin",
                    "size": len(base),
                    "sha256": digest(base),
                },
                "functions": {
                    name: {
                        "expected_offset": details["offset"],
                        "expected_size": details["size"],
                    }
                    for name, details in expected_functions.items()
                },
                "patch_sites": [],
                "expected": {
                    "overlay_size": len(expected_overlay),
                    "overlay_sha256": digest(expected_overlay),
                    "component_size": len(expected_provider),
                    "component_sha256": digest(expected_provider),
                },
                "overlay_artifact": "overlay.bin",
                "provider_artifact": "provider.bin",
                "transport_contract": {},
            }
            config_path = root / "overlay.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            output = root / "build"
            compiled = (
                primary_overlay,
                primary_functions,
                "test clang",
                {
                    "text_size": 2,
                    "rodata_size": 1,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
            )

            with mock.patch.object(
                self.builder,
                "compile_overlay",
                return_value=compiled,
            ) as compile_mock:
                report = self.builder.build(
                    root=root,
                    config_path=config_path,
                    output_dir=output,
                    clang=self.clang,
                )

            self.assertEqual(
                compile_mock.call_args.kwargs["expected_functions"],
                {"primary"},
            )
            self.assertEqual(
                compile_mock.call_args.kwargs["include_dirs"],
                [headers],
            )
            self.assertEqual((output / "overlay.bin").read_bytes(), expected_overlay)
            self.assertEqual(
                (output / "provider.bin").read_bytes(),
                expected_provider,
            )
            self.assertEqual(
                report["overlay"]["functions"]["reviewed_leaf"],
                expected_functions["reviewed_leaf"],
            )
            self.assertEqual(
                report["isolated_leaves"][0]["placement"]["offset"],
                expected_functions["reviewed_leaf"]["offset"],
            )
            self.assertEqual(report["toolchain"]["include_dirs"], ["headers"])

    @_APPLE_ONLY
    def test_real_vendored_ambiq_leaf_builds_through_boot_schema(self) -> None:
        self.assertEqual(digest(AMBIQ_SOURCE.read_bytes()), AMBIQ_SOURCE_SHA256)
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(config["isolated_leaves"]), 6)
        leaf_configs = {
            leaf["function"]: leaf
            for leaf in config["isolated_leaves"]
        }
        leaf_config = leaf_configs["am_hal_mspi_interrupt_clear"]
        self.assertEqual(
            leaf_config["function"],
            "am_hal_mspi_interrupt_clear",
        )
        self.assertEqual(
            leaf_config["source"]["path"],
            AMBIQ_SOURCE.relative_to(ROOT).as_posix(),
        )
        self.assertEqual(
            leaf_config["source"]["sha256"],
            AMBIQ_SOURCE_SHA256,
        )
        self.assertEqual(
            leaf_config["source"]["upstream_commit"],
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        )
        self.assertEqual(
            leaf_config["expected"],
            {
                "size": 48,
                "sha256": AMBIQ_LEAF_SHA256,
            },
        )
        self.assertEqual(
            config["functions"]["am_hal_mspi_interrupt_clear"],
            {
                "expected_offset": 204,
                "expected_size": 48,
            },
        )
        mlist_config = leaf_configs["open_cfw_littlefs_mlist_isopen"]
        self.assertEqual(
            digest(MLIST_ISOPEN_SOURCE.read_bytes()),
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            mlist_config["source"]["path"],
            MLIST_ISOPEN_SOURCE.relative_to(ROOT).as_posix(),
        )
        self.assertEqual(
            mlist_config["source"]["sha256"],
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            mlist_config["expected"],
            {
                "size": 18,
                "sha256": MLIST_ISOPEN_LEAF_SHA256,
            },
        )
        self.assertEqual(
            config["functions"]["open_cfw_littlefs_mlist_isopen"],
            {
                "expected_offset": 252,
                "expected_size": 18,
            },
        )
        self.assertEqual(
            digest(LITTLEFS_UTIL_ENDIAN_SOURCE.read_bytes()),
            LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256,
        )
        endian_expectations = {
            "open_cfw_littlefs_util_fromle32": (
                270,
                2,
                LITTLEFS_UTIL_IDENTITY_LEAF_SHA256,
            ),
            "open_cfw_littlefs_util_tole32": (
                272,
                2,
                LITTLEFS_UTIL_IDENTITY_LEAF_SHA256,
            ),
            "open_cfw_littlefs_util_frombe32": (
                274,
                4,
                LITTLEFS_UTIL_SWAP_LEAF_SHA256,
            ),
            "open_cfw_littlefs_util_tobe32": (
                278,
                4,
                LITTLEFS_UTIL_SWAP_LEAF_SHA256,
            ),
        }
        for function_name, (
            expected_offset,
            expected_size,
            expected_sha256,
        ) in endian_expectations.items():
            with self.subTest(configured_endian_leaf=function_name):
                endian_config = leaf_configs[function_name]
                self.assertEqual(
                    endian_config["source"]["path"],
                    LITTLEFS_UTIL_ENDIAN_SOURCE.relative_to(ROOT).as_posix(),
                )
                self.assertEqual(
                    endian_config["source"]["sha256"],
                    LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256,
                )
                self.assertEqual(
                    endian_config["expected"],
                    {
                        "size": expected_size,
                        "sha256": expected_sha256,
                    },
                )
                self.assertEqual(
                    config["functions"][function_name],
                    {
                        "expected_offset": expected_offset,
                        "expected_size": expected_size,
                    },
                )
        self.assertEqual(
            {
                name: config["functions"][name]
                for name in (
                    "open_cfw_littlefs_util_max",
                    "open_cfw_littlefs_util_min",
                    "open_cfw_littlefs_util_aligndown",
                    "open_cfw_littlefs_util_alignup",
                )
            },
            {
                "open_cfw_littlefs_util_max": {
                    "expected_offset": 58,
                    "expected_size": 8,
                },
                "open_cfw_littlefs_util_min": {
                    "expected_offset": 66,
                    "expected_size": 8,
                },
                "open_cfw_littlefs_util_aligndown": {
                    "expected_offset": 74,
                    "expected_size": 8,
                },
                "open_cfw_littlefs_util_alignup": {
                    "expected_offset": 82,
                    "expected_size": 8,
                },
            },
        )
        self.assertEqual(
            leaf_config["toolchain"]["target"],
            "arm-none-eabi",
        )
        self.assertEqual(
            leaf_config["toolchain"]["reviewed_version_prefix"],
            "Apple clang version 21.0.0",
        )
        self.assertEqual(
            leaf_config["toolchain"]["flags"],
            [
                *self.isolated_flags(),
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-Wno-unused-function",
                "-Wno-sign-compare",
                "-Wno-unused-parameter",
            ],
        )
        self.assertEqual(
            leaf_config["toolchain"]["include_dirs"],
            [
                "third_party/ambiqsuite-apollo510/mcu/apollo510",
                "third_party/ambiqsuite-apollo510/mcu/apollo510/hal",
                (
                    "third_party/ambiqsuite-apollo510/"
                    "CMSIS/AmbiqMicro/Include"
                ),
                "third_party/cmsis-core/CMSIS/Core/Include",
            ],
        )

        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "ambiq"
            report = self.builder.build(
                root=ROOT,
                config_path=CONFIG_PATH,
                output_dir=output,
                clang=self.clang,
            )
            built_overlay = (
                output / "bootloader_core_overlay.bin"
            ).read_bytes()
            self.assertEqual(len(built_overlay), 15240)
            self.assertEqual(digest(built_overlay), BOOT_OVERLAY_SHA256)
            self.assertEqual(len(report["isolated_leaves"]), 6)
            leaf_reports = {
                leaf["extraction"]["function"]: leaf
                for leaf in report["isolated_leaves"]
            }
            leaf_report = leaf_reports["am_hal_mspi_interrupt_clear"]
            placement = leaf_report["placement"]
            self.assertEqual(
                placement,
                {
                    "offset": 204,
                    "size": 48,
                    "alignment": 4,
                    "padding_before": 0,
                },
            )
            leaf = built_overlay[placement["offset"]:placement["offset"] + 48]
            self.assertEqual(digest(leaf), AMBIQ_LEAF_SHA256)
            self.assertEqual(
                leaf_report["source"]["sha256"],
                AMBIQ_SOURCE_SHA256,
            )
            self.assertEqual(
                leaf_report["toolchain"]["flags"],
                leaf_config["toolchain"]["flags"],
            )
            self.assertEqual(
                leaf_report["toolchain"]["include_dirs"],
                leaf_config["toolchain"]["include_dirs"],
            )
            extraction = leaf_report["extraction"]
            self.assertEqual(
                {
                    key: extraction[key]
                    for key in (
                        "function",
                        "section",
                        "size",
                        "sha256",
                        "alignment",
                        "relocation_count",
                        "discarded_alloc_section_count",
                        "discarded_alloc_section_bytes",
                    )
                },
                {
                    "function": "am_hal_mspi_interrupt_clear",
                    "section": ".text.am_hal_mspi_interrupt_clear",
                    "size": 48,
                    "sha256": AMBIQ_LEAF_SHA256,
                    "alignment": 4,
                    "relocation_count": 0,
                    "discarded_alloc_section_count": 100,
                    "discarded_alloc_section_bytes": 18460,
                },
            )
            for function_name, (
                expected_offset,
                expected_size,
                expected_sha256,
            ) in endian_expectations.items():
                with self.subTest(built_endian_leaf=function_name):
                    endian_report = leaf_reports[function_name]
                    self.assertEqual(
                        endian_report["source"]["sha256"],
                        LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256,
                    )
                    self.assertEqual(
                        endian_report["placement"],
                        {
                            "offset": expected_offset,
                            "size": expected_size,
                            "alignment": 2,
                            "padding_before": 0,
                        },
                    )
                    self.assertEqual(
                        endian_report["extraction"]["sha256"],
                        expected_sha256,
                    )
                    self.assertEqual(
                        endian_report["extraction"]["relocation_count"],
                        0,
                    )
                    self.assertEqual(
                        digest(
                            built_overlay[
                                expected_offset:
                                expected_offset + expected_size
                            ]
                        ),
                        expected_sha256,
                    )
            discarded = {
                section["name"]
                for section in extraction["discarded_alloc_sections"]
            }
            self.assertIn(".bss.g_MSPIState", discarded)
            self.assertIn(
                ".ARM.exidx.text.am_hal_mspi_interrupt_clear",
                discarded,
            )
            mlist_report = leaf_reports[
                "open_cfw_littlefs_mlist_isopen"
            ]
            self.assertEqual(
                mlist_report["placement"],
                {
                    "offset": 252,
                    "size": 18,
                    "alignment": 2,
                    "padding_before": 0,
                },
            )
            self.assertEqual(
                digest(built_overlay[252:270]),
                MLIST_ISOPEN_LEAF_SHA256,
            )
            self.assertEqual(
                mlist_report["source"]["sha256"],
                MLIST_ISOPEN_SOURCE_SHA256,
            )
            self.assertEqual(
                {
                    key: mlist_report["extraction"][key]
                    for key in (
                        "function",
                        "section",
                        "size",
                        "sha256",
                        "alignment",
                        "relocation_count",
                        "discarded_alloc_section_count",
                        "discarded_alloc_section_bytes",
                    )
                },
                {
                    "function": "open_cfw_littlefs_mlist_isopen",
                    "section": ".text.open_cfw_littlefs_mlist_isopen",
                    "size": 18,
                    "sha256": MLIST_ISOPEN_LEAF_SHA256,
                    "alignment": 2,
                    "relocation_count": 0,
                    "discarded_alloc_section_count": 1,
                    "discarded_alloc_section_bytes": 8,
                },
            )

    def test_isolated_leaf_schema_rejects_ambiguous_abi(self) -> None:
        base_config = {
            "schema_version": 1,
            "target": "apollo_bootloader",
            "preamble_bytes": 0,
            "toolchain": {
                "target": "arm-none-eabi",
                "flags": ["-mthumb"],
            },
            "sources": [],
        }
        cases = (
            (
                {"functions": {}, "isolated_leaves": {}},
                "isolated_leaves must be a list",
            ),
            (
                {
                    "functions": {"primary": {}, "leaf": {}},
                    "isolated_leaves": [
                        {"function": "leaf"},
                        {"function": "leaf"},
                    ],
                },
                "function names must be unique",
            ),
            (
                {
                    "functions": {"primary": {}},
                    "isolated_leaves": [{"function": "leaf"}],
                },
                "absent from the bootloader function ABI",
            ),
            (
                {
                    "functions": {"leaf": {}},
                    "isolated_leaves": [{"function": "leaf"}],
                },
                "at least one primary source function",
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for index, (changes, message) in enumerate(cases):
                with self.subTest(case=index):
                    config = {**base_config, **changes}
                    config_path = root / f"case-{index}.json"
                    config_path.write_text(
                        json.dumps(config),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        self.builder.build(
                            root=root,
                            config_path=config_path,
                            output_dir=root / f"out-{index}",
                            clang=self.clang,
                        )


if __name__ == "__main__":
    unittest.main()
