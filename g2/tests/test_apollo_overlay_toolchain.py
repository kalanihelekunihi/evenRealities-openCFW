from __future__ import annotations

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
from unittest import mock


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import apollo_overlay  # noqa: E402


class ApolloOverlayToolchainTests(unittest.TestCase):
    @staticmethod
    def _arm_clang() -> str:
        clang = shutil.which("clang")
        if clang is None:
            raise unittest.SkipTest("clang is unavailable")
        return clang

    @staticmethod
    def _isolated_flags() -> list[str]:
        return [
            "-mcpu=cortex-m55",
            "-mthumb",
            "-Oz",
            "-ffreestanding",
            "-fno-builtin",
            "-ffunction-sections",
            "-fdata-sections",
        ]

    def test_reviewed_apple_clang_release_accepts_shipping_patch_builds(self) -> None:
        toolchain = {"reviewed_version_prefix": "Apple clang version 21.0.0"}

        for version in (
            "Apple clang version 21.0.0 (clang-2100.1.1.101)",
            "Apple clang version 21.0.0 (clang-2100.3.27.1)",
        ):
            with self.subTest(version=version):
                apollo_overlay.validate_compiler_version(toolchain, version)

    def test_reviewed_apple_clang_release_rejects_other_families(self) -> None:
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "reviewed toolchain family",
        ):
            apollo_overlay.validate_compiler_version(
                {"reviewed_version_prefix": "Apple clang version 21.0.0"},
                "Apple clang version 20.1.0 (clang-2000.0.1)",
            )

    def test_toolchain_cannot_mix_exact_and_release_family_pins(self) -> None:
        with self.assertRaisesRegex(apollo_overlay.BuildError, "cannot set both"):
            apollo_overlay.validate_compiler_version(
                {
                    "reviewed_version": "Apple clang version 21.0.0",
                    "reviewed_version_prefix": "Apple clang version 21.0.0",
                },
                "Apple clang version 21.0.0",
            )

    def test_compiler_builtin_headers_are_the_only_system_include_root(self) -> None:
        clang = self._arm_clang()
        builtin = apollo_overlay.compiler_builtin_include_dir(clang)
        arguments = apollo_overlay.hermetic_compiler_arguments(builtin)
        self.assertEqual(
            arguments,
            ["--no-default-config", "-nostdinc", "-isystem", str(builtin)],
        )
        with tempfile.TemporaryDirectory() as directory:
            ambient = Path(directory)
            (ambient / "stdint.h").write_text(
                '#error "ambient header entered hermetic compile"\n',
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {
                    "CPATH": str(ambient),
                    "C_INCLUDE_PATH": str(ambient),
                    "SDKROOT": str(ambient),
                    "CCC_OVERRIDE_OPTIONS": "^--sysroot=/usr/local+",
                },
            ):
                environment = apollo_overlay.hermetic_compiler_environment()
                for key in apollo_overlay._COMPILER_INCLUDE_ENVIRONMENT:
                    self.assertNotIn(key, environment)
                completed = subprocess.run(
                    [
                        clang,
                        *arguments,
                        "--target=arm-none-eabi",
                        "-E",
                        "-v",
                        "-x",
                        "c",
                        "/dev/null",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
        search = completed.stderr.split("#include <...> search starts here:", 1)[1]
        search = search.split("End of search list.", 1)[0]
        self.assertIn(str(builtin), search)
        self.assertNotIn("/usr/local/include", search)

    def test_compile_overlay_passes_absolute_include_arguments_in_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            builtin = root / "builtin"
            builtin.mkdir()
            source = root / "probe.c"
            object_path = root / "probe.o"
            config = {
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": ["-mthumb", "-O2"],
                },
                "functions": ["open_cfw_probe"],
            }
            completed = mock.Mock(returncode=0, stderr="", stdout="")
            linked = (
                b"\x00\xbf",
                {"open_cfw_probe": {"offset": 0, "size": 2}},
                {
                    "text_size": 2,
                    "rodata_size": 0,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
            )

            with (
                mock.patch.object(
                    apollo_overlay,
                    "compiler_version",
                    return_value="test clang",
                ),
                mock.patch.object(
                    apollo_overlay.subprocess,
                    "run",
                    return_value=completed,
                ) as run,
                mock.patch.object(
                    apollo_overlay,
                    "extract_linked_overlay",
                    return_value=linked,
                ),
            ):
                apollo_overlay.compile_overlay(
                    clang="/toolchain/clang",
                    source_path=source,
                    object_path=object_path,
                    config=config,
                    include_dirs=[first, second],
                    builtin_include_dir=builtin,
                )

            self.assertEqual(
                run.call_args.args[0],
                [
                    "/toolchain/clang",
                    "--no-default-config",
                    "-nostdinc",
                    "-isystem",
                    str(builtin),
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-O2",
                    "-I",
                    str(first),
                    "-I",
                    str(second),
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
            )

    def test_build_resolves_include_dirs_independently_of_cwd_and_reports_them(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory).resolve()
            root = temporary / "openCFW"
            caller = temporary / "caller"
            headers = root / "headers"
            more_headers = root / "include" / "more"
            output = root / "build"
            caller.mkdir()
            headers.mkdir(parents=True)
            more_headers.mkdir(parents=True)
            source = root / "source.c"
            source.write_text("void open_cfw_probe(void) {}\n", encoding="utf-8")
            base = root / "base.bin"
            base.write_bytes(b"base")
            config_path = root / "overlay.json"
            config = {
                "schema_version": 1,
                "name": "include-probe",
                "firmware_version": "test",
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": ["-mthumb"],
                    "include_dirs": [
                        "headers/../headers",
                        "include/more",
                    ],
                },
                "sources": [{"path": "source.c"}],
                "base": {
                    "path": "base.bin",
                    "size": len(base.read_bytes()),
                    "sha256": hashlib.sha256(base.read_bytes()).hexdigest(),
                },
                "expected": {},
                "functions": ["open_cfw_probe"],
                "patch_sites": [],
                "preamble_bytes": 32,
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            compiled = (
                b"\x00\xbf",
                {"open_cfw_probe": {"offset": 0, "size": 2}},
                "test clang",
                {
                    "text_size": 2,
                    "rodata_size": 0,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
            )

            previous_cwd = Path.cwd()
            try:
                os.chdir(caller)
                with (
                    mock.patch.object(
                        apollo_overlay,
                        "compiler_builtin_include_dir",
                        return_value=headers,
                    ),
                    mock.patch.object(
                        apollo_overlay,
                        "compile_overlay",
                        return_value=compiled,
                    ) as compile_mock,
                    mock.patch.object(
                        apollo_overlay,
                        "patch_component",
                        return_value=(b"component", {"patched_sites": []}),
                    ),
                ):
                    report = apollo_overlay.build(
                        root=root,
                        config_path=config_path,
                        output_dir=output,
                        clang="/toolchain/clang",
                    )
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(
                compile_mock.call_args.kwargs["include_dirs"],
                [headers.resolve(), more_headers.resolve()],
            )
            self.assertEqual(
                report["toolchain"]["include_dirs"],
                ["headers", "include/more"],
            )
            persisted = json.loads(
                (output / "build-report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                persisted["toolchain"]["include_dirs"],
                ["headers", "include/more"],
            )

    def test_include_dirs_are_optional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            resolved, normalized = (
                apollo_overlay.resolve_toolchain_include_dirs(
                    Path(directory),
                    {},
                )
            )
        self.assertEqual(resolved, [])
        self.assertIsNone(normalized)

    def test_include_dirs_reject_invalid_types_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory).resolve()
            root = temporary / "openCFW"
            outside = temporary / "outside"
            headers = root / "headers"
            root.mkdir()
            outside.mkdir()
            headers.mkdir()
            (root / "file").write_text("not a directory", encoding="utf-8")

            cases = [
                ("not-list", {"include_dirs": "headers"}, "must be a list"),
                (
                    "empty",
                    {"include_dirs": [""]},
                    "entries must be nonempty strings",
                ),
                (
                    "whitespace",
                    {"include_dirs": ["   "]},
                    "entries must be nonempty strings",
                ),
                (
                    "non-string",
                    {"include_dirs": [1]},
                    "entries must be nonempty strings",
                ),
                (
                    "absolute",
                    {"include_dirs": [str(headers)]},
                    "must be openCFW-root-relative",
                ),
                (
                    "escape",
                    {"include_dirs": ["../outside"]},
                    "path escapes openCFW root",
                ),
                (
                    "missing",
                    {"include_dirs": ["missing"]},
                    "is not a directory",
                ),
                (
                    "file",
                    {"include_dirs": ["file"]},
                    "is not a directory",
                ),
            ]
            for name, toolchain, message in cases:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        apollo_overlay.resolve_toolchain_include_dirs(
                            root,
                            toolchain,
                        )

    def test_isolated_leaf_extracts_only_named_relocation_free_section(
        self,
    ) -> None:
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "upstream.c"
            object_path = temporary / "upstream.o"
            source.write_text(
                "#include <stdint.h>\n"
                "volatile uint32_t private_state;\n"
                "__attribute__((noinline)) uint32_t unrelated(uint32_t x) {\n"
                "    return private_state + x;\n"
                "}\n"
                "__attribute__((noinline)) uint32_t reviewed_leaf(uint32_t x) {\n"
                "    return x ^ 0x12345678u;\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    *self._isolated_flags(),
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            leaf, report = apollo_overlay.extract_isolated_function_section(
                object_path,
                "reviewed_leaf",
            )

        self.assertGreater(len(leaf), 0)
        self.assertEqual(report["size"], len(leaf))
        self.assertEqual(
            report["sha256"],
            hashlib.sha256(leaf).hexdigest(),
        )
        self.assertEqual(report["relocation_count"], 0)
        discarded_names = {
            section["name"] for section in report["discarded_alloc_sections"]
        }
        self.assertIn(".text.unrelated", discarded_names)
        self.assertIn(".bss.private_state", discarded_names)
        self.assertNotIn(".text.reviewed_leaf", discarded_names)

    def test_mini_linker_resolves_only_authenticated_prel_movwt_pairs(
        self,
    ) -> None:
        source_text = r"""
.syntax unified
.thumb
.section .text,"ax",%progbits
.p2align 2
.global open_cfw_prel_probe
.type open_cfw_prel_probe,%function
.thumb_func
open_cfw_prel_probe:
.Llow:
    .inst.w 0xf64f70f4
    .reloc .Llow, R_ARM_THM_MOVW_PREL_NC, probe_table
.Lhigh:
    .inst.w 0xf6cf70f8
    .reloc .Lhigh, R_ARM_THM_MOVT_PREL, probe_table
    bx lr
.size open_cfw_prel_probe, .-open_cfw_prel_probe

.section .rodata,"a",%progbits
.p2align 2
.type probe_table,%object
probe_table:
    .word 0x11223344
.size probe_table, .-probe_table
"""
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "prel-pair.S"
            object_path = temporary / "prel-pair.o"
            source.write_text(source_text, encoding="utf-8")
            subprocess.run(
                [
                    clang,
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            blob, functions, report = apollo_overlay.extract_linked_overlay(
                object_path
            )

            malformed_source = temporary / "prel-malformed.S"
            malformed_object = temporary / "prel-malformed.o"
            malformed_source.write_text(
                source_text.replace("0xf6cf70f8", "0xf6cf71f8"),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-c",
                    str(malformed_source),
                    "-o",
                    str(malformed_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "same destination register",
            ):
                apollo_overlay.extract_linked_overlay(malformed_object)

        self.assertEqual(
            functions,
            {"open_cfw_prel_probe": {"offset": 0, "size": 10}},
        )
        self.assertEqual(report["resolved_relocation_count"], 2)
        for relocation in report["resolved_relocations"]:
            self.assertEqual(relocation["low_addend"], -12)
            self.assertEqual(relocation["high_addend"], -8)
            self.assertEqual(relocation["low_result"], 0)
            self.assertEqual(relocation["high_result"], 0)
            self.assertEqual(relocation["register"], 0)
        low_first, low_second, high_first, high_second = struct.unpack_from(
            "<HHHH", blob
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(low_first, low_second),
            0,
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(high_first, high_second),
            0,
        )

    def test_build_places_configured_isolated_leaf_in_function_abi(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / "build"
            source = root / "source.c"
            source.write_text("void primary(void) {}\n", encoding="utf-8")
            base = root / "base.bin"
            base.write_bytes(b"base")
            config_path = root / "overlay.json"
            config = {
                "schema_version": 1,
                "name": "isolated-probe",
                "firmware_version": "test",
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": ["-mthumb"],
                },
                "sources": [{"path": "source.c"}],
                "isolated_leaves": [
                    {
                        "function": "reviewed_leaf",
                        "source": {"path": "upstream.c"},
                        "toolchain": {},
                        "expected": {},
                    }
                ],
                "base": {
                    "path": "base.bin",
                    "size": len(base.read_bytes()),
                    "sha256": hashlib.sha256(base.read_bytes()).hexdigest(),
                },
                "expected": {},
                "functions": ["primary", "reviewed_leaf"],
                "patch_sites": [],
                "preamble_bytes": 0,
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            compiled = (
                b"\x00\xbf\x00",
                {"primary": {"offset": 0, "size": 2}},
                "test clang",
                {
                    "text_size": 2,
                    "rodata_size": 1,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
            )
            isolated = (
                b"\x70\x47",
                {
                    "source": {"path": "upstream.c"},
                    "toolchain": {"target": "arm-none-eabi"},
                    "extraction": {
                        "function": "reviewed_leaf",
                        "section": ".text.reviewed_leaf",
                        "size": 2,
                        "sha256": hashlib.sha256(b"\x70\x47").hexdigest(),
                        "alignment": 4,
                        "relocation_count": 0,
                    },
                },
            )

            with (
                mock.patch.object(
                    apollo_overlay,
                    "compiler_builtin_include_dir",
                    return_value=root,
                ),
                mock.patch.object(
                    apollo_overlay,
                    "compile_overlay",
                    return_value=compiled,
                ) as compile_mock,
                mock.patch.object(
                    apollo_overlay,
                    "compile_isolated_leaf",
                    return_value=isolated,
                ) as isolated_mock,
                mock.patch.object(
                    apollo_overlay,
                    "patch_component",
                    return_value=(b"component", {"patched_sites": []}),
                ) as patch_mock,
            ):
                report = apollo_overlay.build(
                    root=root,
                    config_path=config_path,
                    output_dir=output,
                    clang="/toolchain/clang",
                )

        self.assertEqual(
            compile_mock.call_args.kwargs["expected_functions"],
            {"primary"},
        )
        self.assertEqual(
            isolated_mock.call_args.kwargs["leaf_config"],
            config["isolated_leaves"][0],
        )
        self.assertEqual(
            patch_mock.call_args.kwargs["overlay"],
            b"\x00\xbf\x00\x00\x70\x47",
        )
        self.assertEqual(
            patch_mock.call_args.kwargs["functions"]["reviewed_leaf"],
            {"offset": 4, "size": 2},
        )
        self.assertEqual(
            report["isolated_leaves"][0]["placement"],
            {
                "offset": 4,
                "size": 2,
                "alignment": 4,
                "padding_before": 1,
            },
        )

    def test_isolated_leaf_rejects_relocation_to_private_state(self) -> None:
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "upstream.c"
            object_path = temporary / "upstream.o"
            source.write_text(
                "#include <stdint.h>\n"
                "volatile uint32_t private_state;\n"
                "__attribute__((noinline)) uint32_t reviewed_leaf(uint32_t x) {\n"
                "    return private_state + x;\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    *self._isolated_flags(),
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "has relocations",
            ):
                apollo_overlay.extract_isolated_function_section(
                    object_path,
                    "reviewed_leaf",
                )

    def test_two_byte_in_place_leaf_can_use_reviewed_halfword_placement(self) -> None:
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "halfword.c"
            object_path = temporary / "halfword.o"
            source.write_text(
                "__attribute__((noinline, aligned(4))) "
                "void reviewed_halfword_leaf(void) {}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    *self._isolated_flags(),
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "violates section alignment 4",
            ):
                apollo_overlay.extract_in_place_function_section(
                    object_path,
                    "reviewed_halfword_leaf",
                    runtime_address=0x1002,
                    relocation_configs=[],
                )

            leaf, extraction = apollo_overlay.extract_in_place_function_section(
                object_path,
                "reviewed_halfword_leaf",
                runtime_address=0x1002,
                relocation_configs=[],
                allow_halfword_placement=True,
            )
            self.assertEqual(leaf, bytes.fromhex("7047"))
            self.assertEqual(extraction["alignment"], 4)
            self.assertEqual(extraction["runtime_address"], 0x1002)

    def test_halfword_placement_override_is_narrow(self) -> None:
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "allow_halfword_placement must be boolean",
        ):
            apollo_overlay.extract_in_place_function_section(
                Path("unused.o"),
                "reviewed_halfword_leaf",
                runtime_address=0x1002,
                relocation_configs=[],
                allow_halfword_placement="yes",  # type: ignore[arg-type]
            )

    def test_complete_thumb_leaf_can_use_reviewed_halfword_placement(self) -> None:
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "halfword-function.c"
            object_path = temporary / "halfword-function.o"
            source.write_text(
                "__attribute__((noinline, aligned(4))) "
                "unsigned reviewed_halfword_function(unsigned x) { "
                "return (x ^ 0x1234u) + 7u; }\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    *self._isolated_flags(),
                    "-c",
                    str(source),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            leaf, extraction = apollo_overlay.extract_in_place_function_section(
                object_path,
                "reviewed_halfword_function",
                runtime_address=0x1002,
                relocation_configs=[],
                allow_halfword_placement=True,
            )
            self.assertGreater(len(leaf), 2)
            self.assertEqual(extraction["runtime_address"], 0x1002)
            self.assertEqual(extraction["alignment"], 4)

    def test_authenticated_isolated_leaf_can_be_appended_without_other_tu_state(
        self,
    ) -> None:
        clang = self._arm_clang()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "upstream.c"
            probe_object = root / "probe.o"
            source.write_text(
                "#include <stdint.h>\n"
                "volatile uint32_t private_state;\n"
                "__attribute__((noinline)) uint32_t unrelated(uint32_t x) {\n"
                "    return private_state + x;\n"
                "}\n"
                "__attribute__((noinline)) uint32_t reviewed_leaf(uint32_t x) {\n"
                "    return x ^ 0x12345678u;\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    *self._isolated_flags(),
                    "-c",
                    str(source),
                    "-o",
                    str(probe_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            expected_leaf, _ = (
                apollo_overlay.extract_isolated_function_section(
                    probe_object,
                    "reviewed_leaf",
                )
            )
            leaf_config = {
                "function": "reviewed_leaf",
                "source": {
                    "path": "upstream.c",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "license": "test-only",
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": self._isolated_flags(),
                },
                "expected": {
                    "size": len(expected_leaf),
                    "sha256": hashlib.sha256(expected_leaf).hexdigest(),
                },
            }

            leaf, compile_report = apollo_overlay.compile_isolated_leaf(
                root=root,
                clang=clang,
                leaf_config=leaf_config,
                object_path=root / "reviewed.o",
            )
            (
                combined,
                functions,
                link_report,
                placement_reports,
            ) = apollo_overlay.append_isolated_leaves(
                overlay=b"\x00\xbf\x00",
                functions={"primary": {"offset": 0, "size": 2}},
                link_report={
                    "text_size": 2,
                    "rodata_size": 1,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
                leaves=[(leaf, compile_report)],
            )

        placement = placement_reports[0]["placement"]
        self.assertEqual(placement["offset"] % 4, 0)
        self.assertEqual(
            combined[
                placement["offset"]:placement["offset"] + placement["size"]
            ],
            expected_leaf,
        )
        self.assertEqual(set(functions), {"primary", "reviewed_leaf"})
        self.assertEqual(
            functions["reviewed_leaf"],
            {
                "offset": placement["offset"],
                "size": len(expected_leaf),
            },
        )
        self.assertEqual(link_report["isolated_text_size"], len(expected_leaf))
        discarded_names = {
            section["name"]
            for section in compile_report["extraction"][
                "discarded_alloc_sections"
            ]
        }
        self.assertIn(".text.unrelated", discarded_names)
        self.assertIn(".bss.private_state", discarded_names)


if __name__ == "__main__":
    unittest.main()
