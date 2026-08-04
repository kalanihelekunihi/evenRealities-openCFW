from __future__ import annotations

import copy
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import apollo_overlay  # noqa: E402


class ApolloOverlayRelocatedLeafTests(unittest.TestCase):
    RUN_BASE = 0x00438000
    OVERLAY_RUNTIME_ADDRESS = 0x0043A000
    PRIMARY_OVERLAY = b"\x70\x47\xa5"
    PRIMARY_FUNCTIONS = {"primary": {"offset": 0, "size": 2}}

    @staticmethod
    def _clang() -> str:
        clang = shutil.which("clang")
        if clang is None:
            raise unittest.SkipTest("clang is unavailable")
        return clang

    @staticmethod
    def _flags() -> list[str]:
        return [
            "-mcpu=cortex-m55",
            "-mthumb",
            "-Oz",
            "-ffreestanding",
            "-fno-builtin",
            "-ffunction-sections",
            "-fdata-sections",
        ]

    @staticmethod
    def _digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def _base(cls, payload_size: int = 0x40) -> bytes:
        image = bytearray(32 + payload_size)
        struct.pack_into("<I", image, 0, len(image))
        struct.pack_into("<I", image, 0x10, 0xCB)
        struct.pack_into("<I", image, 0x14, cls.RUN_BASE)
        struct.pack_into("<I", image, 4, zlib.crc32(image[8:]) & 0xFFFFFFFF)
        return bytes(image)

    def _write_and_compile(
        self,
        root: Path,
        *,
        filename: str,
        source_text: str,
    ) -> tuple[Path, Path]:
        source = root / filename
        object_path = root / f"{Path(filename).stem}.o"
        source.write_text(source_text, encoding="utf-8")
        subprocess.run(
            [
                self._clang(),
                "--target=arm-none-eabi",
                *self._flags(),
                "-c",
                str(source),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return source, object_path

    @staticmethod
    def _section_for_function(
        object_path: Path,
        function_name: str,
    ) -> tuple[bytes, list[dict[str, int | str]], dict[str, int | str]]:
        data, sections = apollo_overlay.parse_elf32(object_path)
        section = apollo_overlay.section_named(
            sections,
            f".text.{function_name}",
        )
        return data, sections, section

    def _observed_relocations(
        self,
        object_path: Path,
        function_name: str,
    ) -> list[dict[str, object]]:
        data, sections, function_section = self._section_for_function(
            object_path,
            function_name,
        )
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        names = {
            value: name
            for name, value in apollo_overlay.IN_PLACE_RELOCATION_TYPES.items()
        }
        records: list[dict[str, object]] = []
        for section in sections:
            if (
                int(section["type"]) not in (
                    apollo_overlay.SHT_REL,
                    apollo_overlay.SHT_RELA,
                )
                or int(section["info"]) != int(function_section["index"])
                or not int(section["size"])
            ):
                continue
            self.assertEqual(
                int(section["type"]),
                apollo_overlay.SHT_REL,
                "the synthetic compiler unexpectedly emitted RELA",
            )
            self.assertEqual(int(section["entry_size"]), 8)
            for index in range(
                int(section["size"]) // int(section["entry_size"])
            ):
                entry = (
                    int(section["offset"])
                    + index * int(section["entry_size"])
                )
                offset, info = struct.unpack_from("<II", data, entry)
                relocation_type = info & 0xFF
                symbol_index = info >> 8
                records.append(
                    {
                        "offset": offset,
                        "type": names.get(
                            relocation_type,
                            f"UNKNOWN_{relocation_type}",
                        ),
                        "symbol": str(symbols[symbol_index]["name"]),
                    }
                )
        return records

    def _call_source(
        self,
        *,
        function_name: str = "relocated_leaf",
        target_name: str = "primary",
        tail_call: bool = False,
        define_target: bool = False,
        include_unrelated_state: bool = True,
    ) -> str:
        declarations = (
            (
                "__attribute__((noinline))\n"
                f"unsigned {target_name}(unsigned value) {{\n"
                "    return value ^ 0x13579bdfu;\n"
                "}\n"
            )
            if define_target
            else f"extern unsigned {target_name}(unsigned value);\n"
        )
        unrelated = (
            "volatile unsigned unrelated_state;\n"
            "__attribute__((noinline))\n"
            "unsigned unrelated_state_user(unsigned value) {\n"
            "    return unrelated_state + value;\n"
            "}\n"
            if include_unrelated_state
            else ""
        )
        result = (
            f"{target_name}(value)"
            if tail_call
            else f"{target_name}(value) + 1u"
        )
        return (
            declarations
            + unrelated
            + "__attribute__((noinline))\n"
            + f"unsigned {function_name}(unsigned value) {{\n"
            + f"    return {result};\n"
            + "}\n"
        )

    def _prepared_leaf(
        self,
        root: Path,
        *,
        overlay: bytes | None = None,
        functions: dict[str, dict[str, int]] | None = None,
        overlay_runtime_address: int | None = None,
        filename: str = "relocated.c",
        function_name: str = "relocated_leaf",
        target_name: str = "primary",
        tail_call: bool = False,
        source_text: str | None = None,
    ) -> tuple[dict[str, object], bytes, Path, Path, int]:
        overlay = self.PRIMARY_OVERLAY if overlay is None else overlay
        functions = self.PRIMARY_FUNCTIONS if functions is None else functions
        overlay_runtime_address = (
            self.OVERLAY_RUNTIME_ADDRESS
            if overlay_runtime_address is None
            else overlay_runtime_address
        )
        if source_text is None:
            source_text = self._call_source(
                function_name=function_name,
                target_name=target_name,
                tail_call=tail_call,
            )
        source, object_path = self._write_and_compile(
            root,
            filename=filename,
            source_text=source_text,
        )
        relocations = self._observed_relocations(
            object_path,
            function_name,
        )
        self.assertEqual(len(relocations), 1)
        self.assertEqual(relocations[0]["symbol"], target_name)
        _data, _sections, function_section = self._section_for_function(
            object_path,
            function_name,
        )
        alignment = int(function_section["alignment"])
        offset = apollo_overlay.align_up(len(overlay), alignment)
        runtime_address = overlay_runtime_address + offset
        target_address = (
            overlay_runtime_address + int(functions[target_name]["offset"])
        )
        resolved_relocations = [
            {
                "offset": relocation["offset"],
                "type": relocation["type"],
                "symbol": relocation["symbol"],
                "target_address": target_address,
            }
            for relocation in relocations
        ]
        final_leaf, extraction_report = (
            apollo_overlay.extract_in_place_function_section(
                object_path,
                function_name,
                runtime_address=runtime_address,
                relocation_configs=resolved_relocations,
            )
        )
        leaf_config: dict[str, object] = {
            "function": function_name,
            "source": {
                "path": source.name,
                "size": len(source.read_bytes()),
                "sha256": self._digest(source.read_bytes()),
                "license": "test-only",
            },
            "toolchain": {
                "target": "arm-none-eabi",
                "flags": self._flags(),
            },
            "expected": {
                "size": len(final_leaf),
                "sha256": self._digest(final_leaf),
                "alignment": alignment,
                "offset": offset,
                "unrelocated_sha256": extraction_report[
                    "unrelocated_sha256"
                ],
            },
            "relocations": [
                {
                    **relocation,
                    "target_function": target_name,
                }
                for relocation in relocations
            ],
        }
        return leaf_config, final_leaf, source, object_path, offset

    def _prepared_defined_sibling_pair(
        self,
        root: Path,
        *,
        tail_call: bool,
    ) -> tuple[
        list[dict[str, object]],
        bytes,
        dict[str, dict[str, int]],
        Path,
        list[dict[str, object]],
    ]:
        target_name = "selected_sibling_target"
        caller_name = "selected_sibling_caller"
        source, object_path = self._write_and_compile(
            root,
            filename=(
                "defined-sibling-tail.c"
                if tail_call
                else "defined-sibling-call.c"
            ),
            source_text=self._call_source(
                function_name=caller_name,
                target_name=target_name,
                tail_call=tail_call,
                define_target=True,
                include_unrelated_state=False,
            ),
        )
        source_record = {
            "path": source.name,
            "size": len(source.read_bytes()),
            "sha256": self._digest(source.read_bytes()),
            "license": "test-only",
        }
        toolchain = {
            "target": "arm-none-eabi",
            "flags": self._flags(),
        }

        _data, _sections, target_section = self._section_for_function(
            object_path,
            target_name,
        )
        target_alignment = int(target_section["alignment"])
        target_offset = apollo_overlay.align_up(
            len(self.PRIMARY_OVERLAY),
            target_alignment,
        )
        target_runtime = self.OVERLAY_RUNTIME_ADDRESS + target_offset
        target_bytes, target_report = (
            apollo_overlay.extract_in_place_function_section(
                object_path,
                target_name,
                runtime_address=target_runtime,
                relocation_configs=[],
            )
        )
        target_config = {
            "function": target_name,
            "source": source_record,
            "toolchain": toolchain,
            "expected": {
                "size": len(target_bytes),
                "sha256": self._digest(target_bytes),
                "alignment": target_alignment,
                "offset": target_offset,
                "unrelocated_sha256": target_report[
                    "unrelocated_sha256"
                ],
            },
            "relocations": [],
        }
        overlay_after_target = (
            self.PRIMARY_OVERLAY
            + b"\0" * (target_offset - len(self.PRIMARY_OVERLAY))
            + target_bytes
        )
        functions_after_target = {
            **self.PRIMARY_FUNCTIONS,
            target_name: {
                "offset": target_offset,
                "size": len(target_bytes),
            },
        }

        observed = self._observed_relocations(
            object_path,
            caller_name,
        )
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["symbol"], target_name)
        _data, _sections, caller_section = self._section_for_function(
            object_path,
            caller_name,
        )
        caller_alignment = int(caller_section["alignment"])
        caller_offset = apollo_overlay.align_up(
            len(overlay_after_target),
            caller_alignment,
        )
        caller_runtime = self.OVERLAY_RUNTIME_ADDRESS + caller_offset
        resolved = [
            {
                **observed[0],
                "target_address": target_runtime,
            }
        ]
        caller_bytes, caller_report = (
            apollo_overlay.extract_in_place_function_section(
                object_path,
                caller_name,
                runtime_address=caller_runtime,
                relocation_configs=resolved,
                allowed_defined_relocation_targets=frozenset(
                    {target_name}
                ),
            )
        )
        caller_config = {
            "function": caller_name,
            "source": source_record,
            "toolchain": toolchain,
            "expected": {
                "size": len(caller_bytes),
                "sha256": self._digest(caller_bytes),
                "alignment": caller_alignment,
                "offset": caller_offset,
                "unrelocated_sha256": caller_report[
                    "unrelocated_sha256"
                ],
            },
            "relocations": [
                {
                    **observed[0],
                    "target_function": target_name,
                }
            ],
        }
        return (
            [target_config, caller_config],
            overlay_after_target,
            functions_after_target,
            object_path,
            resolved,
        )

    @staticmethod
    def _link_report() -> dict[str, object]:
        return {
            "text_size": 2,
            "rodata_size": 1,
            "rodata_sections": [],
            "resolved_relocation_count": 0,
            "resolved_relocations": [],
        }

    def _append(
        self,
        root: Path,
        *,
        leaf_configs: list[dict[str, object]],
        overlay: bytes | None = None,
        functions: dict[str, dict[str, int]] | None = None,
        overlay_runtime_address: int | None = None,
    ):
        return apollo_overlay.append_relocated_leaves(
            root=root,
            clang=self._clang(),
            overlay=self.PRIMARY_OVERLAY if overlay is None else overlay,
            overlay_runtime_address=(
                self.OVERLAY_RUNTIME_ADDRESS
                if overlay_runtime_address is None
                else overlay_runtime_address
            ),
            functions=(
                self.PRIMARY_FUNCTIONS if functions is None else functions
            ),
            link_report=self._link_report(),
            leaf_configs=leaf_configs,
            object_root=root,
        )

    def _minimal_config(
        self,
        root: Path,
        relocated_leaves,
        *,
        functions: list[str] | None = None,
        isolated_leaves: list[dict[str, object]] | None = None,
        in_place_leaves: list[dict[str, object]] | None = None,
        sources: list[dict[str, object]] | None = None,
    ) -> tuple[dict[str, object], Path]:
        primary = root / "primary.c"
        primary.write_text("void primary(void) {}\n", encoding="utf-8")
        base = root / "base.bin"
        base_bytes = self._base()
        base.write_bytes(base_bytes)
        config: dict[str, object] = {
            "schema_version": 1,
            "name": "relocated-test",
            "firmware_version": "test",
            "toolchain": {
                "target": "arm-none-eabi",
                "flags": ["-mthumb"],
            },
            "sources": (
                [{"path": primary.name}]
                if sources is None
                else sources
            ),
            "base": {
                "path": base.name,
                "size": len(base_bytes),
                "sha256": self._digest(base_bytes),
            },
            "expected": {},
            "functions": (
                ["primary", "relocated_leaf"]
                if functions is None
                else functions
            ),
            "relocated_leaves": relocated_leaves,
            "patch_sites": [],
            "run_base": self.RUN_BASE,
            "preamble_bytes": 32,
            "alignment": 4,
        }
        if isolated_leaves is not None:
            config["isolated_leaves"] = isolated_leaves
        if in_place_leaves is not None:
            config["in_place_leaves"] = in_place_leaves
        config_path = root / "overlay.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return config, config_path

    def test_build_appends_relocated_leaf_after_isolated_tail_without_abi_drift(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            base = self._base()
            overlay_runtime_address = (
                self.RUN_BASE
                + apollo_overlay.align_up(len(base), 4)
                - 32
            )
            isolated_leaf = b"\x00\xbf\x70\x47"
            isolated_report = {
                "source": {"path": "isolated.c"},
                "toolchain": {"target": "arm-none-eabi"},
                "extraction": {
                    "function": "isolated_tail",
                    "section": ".text.isolated_tail",
                    "size": len(isolated_leaf),
                    "sha256": self._digest(isolated_leaf),
                    "alignment": 4,
                    "relocation_count": 0,
                    "discarded_alloc_section_count": 0,
                    "discarded_alloc_section_bytes": 0,
                    "discarded_alloc_sections": [],
                },
            }
            isolated_offset = apollo_overlay.align_up(
                len(self.PRIMARY_OVERLAY),
                4,
            )
            before_relocated = (
                self.PRIMARY_OVERLAY
                + b"\0" * (isolated_offset - len(self.PRIMARY_OVERLAY))
                + isolated_leaf
            )
            functions_before_relocated = {
                **self.PRIMARY_FUNCTIONS,
                "isolated_tail": {
                    "offset": isolated_offset,
                    "size": len(isolated_leaf),
                },
            }
            leaf_config, final_leaf, _source, _object, leaf_offset = (
                self._prepared_leaf(
                    root,
                    overlay=before_relocated,
                    functions=functions_before_relocated,
                    overlay_runtime_address=overlay_runtime_address,
                )
            )
            config, config_path = self._minimal_config(
                root,
                [leaf_config],
                functions=["primary", "isolated_tail", "relocated_leaf"],
                isolated_leaves=[{"function": "isolated_tail"}],
            )
            primary = root / "primary.c"
            config["sources"] = [{"path": primary.name}]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            compiled = (
                self.PRIMARY_OVERLAY,
                copy.deepcopy(self.PRIMARY_FUNCTIONS),
                "test clang",
                self._link_report(),
            )

            with (
                mock.patch.object(
                    apollo_overlay,
                    "compile_overlay",
                    return_value=compiled,
                ) as compile_mock,
                mock.patch.object(
                    apollo_overlay,
                    "compile_isolated_leaf",
                    return_value=(isolated_leaf, isolated_report),
                ),
            ):
                report = apollo_overlay.build(
                    root=root,
                    config_path=config_path,
                    output_dir=root / "build",
                    clang=self._clang(),
                )

            overlay = (root / "build" / "relocated-test.text.bin").read_bytes()

        self.assertEqual(
            compile_mock.call_args.kwargs["expected_functions"],
            {"primary"},
        )
        self.assertEqual(
            compile_mock.call_args.kwargs["source_path"],
            primary,
        )
        self.assertEqual(
            overlay[:len(before_relocated)],
            before_relocated,
        )
        self.assertEqual(
            overlay[leaf_offset:leaf_offset + len(final_leaf)],
            final_leaf,
        )
        self.assertEqual(
            report["overlay"]["functions"]["primary"],
            self.PRIMARY_FUNCTIONS["primary"],
        )
        self.assertEqual(
            report["overlay"]["functions"]["isolated_tail"],
            functions_before_relocated["isolated_tail"],
        )
        self.assertEqual(
            report["overlay"]["functions"]["relocated_leaf"],
            {"offset": leaf_offset, "size": len(final_leaf)},
        )
        relocated = report["relocated_leaves"][0]
        self.assertEqual(relocated["placement"]["offset"], leaf_offset)
        self.assertEqual(
            relocated["placement"]["runtime_address"],
            overlay_runtime_address + leaf_offset,
        )
        self.assertEqual(
            relocated["extraction"]["relocations"][0]["target_function"],
            "primary",
        )
        relocation_offset = int(
            relocated["extraction"]["relocations"][0]["offset"]
        )
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                overlay_runtime_address + leaf_offset + relocation_offset,
                final_leaf[relocation_offset:relocation_offset + 4],
                link=True,
            ),
            overlay_runtime_address,
        )
        discarded = {
            item["name"]
            for item in relocated["extraction"]["discarded_alloc_sections"]
        }
        self.assertIn(".text.unrelated_state_user", discarded)
        self.assertIn(".bss.unrelated_state", discarded)
        self.assertEqual(
            report["overlay"]["link"]["relocated_text_size"],
            len(final_leaf),
        )
        self.assertEqual(
            report["overlay"]["link"]["relocated_padding_size"],
            leaf_offset - len(before_relocated),
        )
        self.assertEqual(
            report["overlay"]["link"]["relocated_functions"],
            [
                {
                    "function": "relocated_leaf",
                    **relocated["placement"],
                }
            ],
        )
        self.assertEqual(
            report["component"]["source_owned_bytes"],
            len(overlay),
        )
        self.assertEqual(
            report["component"]["opaque_base_bytes"],
            len(base) - 32,
        )

    def test_relocated_call_and_tail_jump_use_canonical_rel_placeholders(
        self,
    ) -> None:
        for tail_call, expected_type, link in (
            (False, "R_ARM_THM_CALL", True),
            (True, "R_ARM_THM_JUMP24", False),
        ):
            with self.subTest(type=expected_type):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    config, expected_leaf, _source, _object, offset = (
                        self._prepared_leaf(
                            root,
                            tail_call=tail_call,
                        )
                    )
                    self.assertEqual(
                        config["relocations"][0]["type"],
                        expected_type,
                    )
                    overlay, functions, link_report, reports = self._append(
                        root,
                        leaf_configs=[config],
                    )

                self.assertEqual(
                    overlay[offset:offset + len(expected_leaf)],
                    expected_leaf,
                )
                self.assertEqual(
                    functions["relocated_leaf"],
                    {"offset": offset, "size": len(expected_leaf)},
                )
                relocation = reports[0]["extraction"]["relocations"][0]
                relocation_offset = int(relocation["offset"])
                self.assertEqual(
                    apollo_overlay.decode_thumb_branch(
                        self.OVERLAY_RUNTIME_ADDRESS
                        + offset
                        + relocation_offset,
                        expected_leaf[
                            relocation_offset:relocation_offset + 4
                        ],
                        link=link,
                    ),
                    self.OVERLAY_RUNTIME_ADDRESS,
                )
                self.assertEqual(link_report["relocated_text_size"], len(expected_leaf))

    def test_appends_call_free_leaf_with_explicit_empty_relocations(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            function_name = "call_free_leaf"
            source, object_path = self._write_and_compile(
                root,
                filename="call-free.c",
                source_text=(
                    "__attribute__((noinline))\n"
                    f"unsigned {function_name}(unsigned value) {{\n"
                    "    value ^= value >> 3;\n"
                    "    return value + 7u;\n"
                    "}\n"
                ),
            )
            self.assertEqual(
                self._observed_relocations(object_path, function_name),
                [],
            )
            _data, _sections, section = self._section_for_function(
                object_path,
                function_name,
            )
            alignment = int(section["alignment"])
            offset = apollo_overlay.align_up(
                len(self.PRIMARY_OVERLAY),
                alignment,
            )
            runtime_address = self.OVERLAY_RUNTIME_ADDRESS + offset
            expected_leaf, extraction = (
                apollo_overlay.extract_in_place_function_section(
                    object_path,
                    function_name,
                    runtime_address=runtime_address,
                    relocation_configs=[],
                )
            )
            config = {
                "function": function_name,
                "source": {
                    "path": source.name,
                    "size": len(source.read_bytes()),
                    "sha256": self._digest(source.read_bytes()),
                    "license": "test-only",
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": self._flags(),
                },
                "expected": {
                    "size": len(expected_leaf),
                    "sha256": self._digest(expected_leaf),
                    "alignment": alignment,
                    "offset": offset,
                    "unrelocated_sha256": extraction[
                        "unrelocated_sha256"
                    ],
                },
                "relocations": [],
            }
            overlay, functions, link_report, reports = self._append(
                root,
                leaf_configs=[config],
            )

        self.assertEqual(
            overlay[offset:offset + len(expected_leaf)],
            expected_leaf,
        )
        self.assertEqual(
            functions[function_name],
            {"offset": offset, "size": len(expected_leaf)},
        )
        self.assertEqual(reports[0]["extraction"]["relocation_count"], 0)
        self.assertEqual(reports[0]["extraction"]["relocations"], [])
        self.assertEqual(
            reports[0]["extraction"]["unrelocated_sha256"],
            reports[0]["extraction"]["sha256"],
        )
        self.assertEqual(
            link_report["relocated_text_size"],
            len(expected_leaf),
        )

    def test_allows_only_existing_or_prior_overlay_function_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first, first_bytes, _source, _object, first_offset = (
                self._prepared_leaf(
                    root,
                    filename="first.c",
                    function_name="leaf_one",
                )
            )
            overlay_after_first = (
                self.PRIMARY_OVERLAY
                + b"\0" * (first_offset - len(self.PRIMARY_OVERLAY))
                + first_bytes
            )
            functions_after_first = {
                **self.PRIMARY_FUNCTIONS,
                "leaf_one": {
                    "offset": first_offset,
                    "size": len(first_bytes),
                },
            }
            second, second_bytes, _source, _object, second_offset = (
                self._prepared_leaf(
                    root,
                    overlay=overlay_after_first,
                    functions=functions_after_first,
                    filename="second.c",
                    function_name="leaf_two",
                    target_name="leaf_one",
                )
            )
            overlay, functions, _link, reports = self._append(
                root,
                leaf_configs=[first, second],
            )
            self.assertEqual(
                overlay[second_offset:second_offset + len(second_bytes)],
                second_bytes,
            )
            self.assertEqual(
                reports[1]["extraction"]["relocations"][0][
                    "target_function"
                ],
                "leaf_one",
            )
            self.assertEqual(functions["leaf_one"]["offset"], first_offset)

            unknown = copy.deepcopy(first)
            unknown["relocations"][0]["symbol"] = "not_in_overlay"
            unknown["relocations"][0]["target_function"] = "not_in_overlay"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unavailable prior overlay function",
            ):
                self._append(root, leaf_configs=[unknown])

            future_first = copy.deepcopy(first)
            future_first["relocations"][0]["symbol"] = "leaf_two"
            future_first["relocations"][0]["target_function"] = "leaf_two"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unavailable prior overlay function",
            ):
                self._append(
                    root,
                    leaf_configs=[future_first, second],
                )

    def test_schema_rejects_missing_duplicate_and_ambiguous_registrations(
        self,
    ) -> None:
        placeholder = {
            "function": "relocated_leaf",
            "source": {},
            "toolchain": {},
            "expected": {},
            "relocations": [],
        }
        cases = [
            (
                "not-list",
                {"relocated_leaves": {}},
                "relocated_leaves must be a list",
            ),
            (
                "missing-name",
                {"relocated_leaves": [{}]},
                "relocated leaf requires a function",
            ),
            (
                "duplicate",
                {"relocated_leaves": [placeholder, placeholder]},
                "function names must be unique",
            ),
            (
                "absent-abi",
                {
                    "relocated_leaves": [placeholder],
                    "functions": ["primary"],
                },
                "absent from the overlay function ABI",
            ),
            (
                "also-isolated",
                {
                    "relocated_leaves": [placeholder],
                    "isolated_leaves": [
                        {"function": "relocated_leaf"}
                    ],
                },
                "both isolated and relocated",
            ),
            (
                "also-in-place",
                {
                    "relocated_leaves": [placeholder],
                    "in_place_leaves": [
                        {"function": "relocated_leaf"}
                    ],
                },
                "in-place leaves cannot be registered",
            ),
        ]
        for name, overrides, message in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    relocated_leaves = overrides.get(
                        "relocated_leaves",
                        [placeholder],
                    )
                    _config, config_path = self._minimal_config(
                        root,
                        relocated_leaves,
                        functions=overrides.get("functions"),
                        isolated_leaves=overrides.get("isolated_leaves"),
                        in_place_leaves=overrides.get("in_place_leaves"),
                    )
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        apollo_overlay.build(
                            root=root,
                            config_path=config_path,
                            output_dir=root / "build",
                            clang=self._clang(),
                        )

    def test_relocated_source_cannot_enter_primary_combined_translation_unit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf, _bytes, source, _object, _offset = self._prepared_leaf(root)
            primary = root / "primary.c"
            primary.write_text("void primary(void) {}\n", encoding="utf-8")
            for path_spelling in (source.name, f"./{source.name}"):
                with self.subTest(path=path_spelling):
                    sources = [
                        {"path": primary.name},
                        {
                            "path": path_spelling,
                            "sha256": self._digest(source.read_bytes()),
                        },
                    ]
                    _config, config_path = self._minimal_config(
                        root,
                        [leaf],
                        sources=sources,
                    )
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "relocated leaf source.*primary",
                    ):
                        apollo_overlay.build(
                            root=root,
                            config_path=config_path,
                            output_dir=root / "build",
                            clang=self._clang(),
                        )

    def test_rejects_exact_relocation_identity_and_order_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf, _bytes, _source, _object, _offset = self._prepared_leaf(root)

            missing = copy.deepcopy(leaf)
            missing["relocations"] = []
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "relocation list differs",
            ):
                self._append(root, leaf_configs=[missing])

            wrong_type = copy.deepcopy(leaf)
            wrong_type["relocations"][0]["type"] = "R_ARM_THM_JUMP24"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "relocation list differs",
            ):
                self._append(root, leaf_configs=[wrong_type])

            unsupported_appended_type = copy.deepcopy(leaf)
            unsupported_appended_type["relocations"][0][
                "type"
            ] = "R_ARM_THM_PC8"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unsupported appended-leaf type",
            ):
                self._append(
                    root,
                    leaf_configs=[unsupported_appended_type],
                )

            wrong_offset = copy.deepcopy(leaf)
            wrong_offset["relocations"][0]["offset"] += 2
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "relocation list differs",
            ):
                self._append(root, leaf_configs=[wrong_offset])

            mismatched_binding = copy.deepcopy(leaf)
            mismatched_binding["relocations"][0][
                "target_function"
            ] = "other"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "exact symbol.*target_function",
            ):
                self._append(
                    root,
                    leaf_configs=[mismatched_binding],
                    functions={
                        **self.PRIMARY_FUNCTIONS,
                        "other": {"offset": 2, "size": 1},
                    },
                )

            unexpected_field = copy.deepcopy(leaf)
            unexpected_field["relocations"][0]["target_address"] = 0
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "exactly one of target_function or target_address",
            ):
                self._append(root, leaf_configs=[unexpected_field])

            two_call_source = (
                "extern unsigned primary(unsigned value);\n"
                "extern unsigned other(unsigned value);\n"
                "__attribute__((noinline))\n"
                "unsigned two_calls(unsigned value) {\n"
                "    return primary(value) + other(value);\n"
                "}\n"
            )
            source, object_path = self._write_and_compile(
                root,
                filename="two_calls.c",
                source_text=two_call_source,
            )
            relocations = self._observed_relocations(
                object_path,
                "two_calls",
            )
            self.assertEqual(len(relocations), 2)
            functions = {
                "primary": {"offset": 0, "size": 2},
                "other": {"offset": 2, "size": 2},
            }
            _data, _sections, section = self._section_for_function(
                object_path,
                "two_calls",
            )
            alignment = int(section["alignment"])
            offset = apollo_overlay.align_up(
                len(self.PRIMARY_OVERLAY),
                alignment,
            )
            runtime_address = self.OVERLAY_RUNTIME_ADDRESS + offset
            resolved = [
                {
                    **relocation,
                    "target_address": (
                        self.OVERLAY_RUNTIME_ADDRESS
                        + functions[str(relocation["symbol"])]["offset"]
                    ),
                }
                for relocation in relocations
            ]
            final, _report = apollo_overlay.extract_in_place_function_section(
                object_path,
                "two_calls",
                runtime_address=runtime_address,
                relocation_configs=resolved,
            )
            ordered_config = {
                "function": "two_calls",
                "source": {
                    "path": source.name,
                    "size": len(source.read_bytes()),
                    "sha256": self._digest(source.read_bytes()),
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": self._flags(),
                },
                "expected": {
                    "size": len(final),
                    "sha256": self._digest(final),
                    "alignment": alignment,
                },
                "relocations": [
                    {
                        **relocation,
                        "target_function": relocation["symbol"],
                    }
                    for relocation in relocations
                ],
            }
            reversed_config = copy.deepcopy(ordered_config)
            reversed_config["relocations"].reverse()
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "ordered by offset",
            ):
                self._append(
                    root,
                    leaf_configs=[reversed_config],
                    functions=functions,
                )

    def test_rejects_rela_unsupported_types_and_noncanonical_placeholders(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf, _bytes, _source, object_path, _offset = (
                self._prepared_leaf(root)
            )
            data, sections, function_section = self._section_for_function(
                object_path,
                "relocated_leaf",
            )
            relocation_section = next(
                section
                for section in sections
                if int(section["type"]) == apollo_overlay.SHT_REL
                and int(section["info"]) == int(function_section["index"])
            )

            rela_object = root / "rela.o"
            rela_data = bytearray(data)
            section_table = struct.unpack_from("<I", rela_data, 0x20)[0]
            section_entry_size = struct.unpack_from("<H", rela_data, 0x2E)[0]
            relocation_header = (
                section_table
                + int(relocation_section["index"]) * section_entry_size
            )
            struct.pack_into(
                "<I",
                rela_data,
                relocation_header + 4,
                apollo_overlay.SHT_RELA,
            )
            rela_object.write_bytes(rela_data)
            resolved = [
                {
                    "offset": leaf["relocations"][0]["offset"],
                    "type": leaf["relocations"][0]["type"],
                    "symbol": "primary",
                    "target_address": self.OVERLAY_RUNTIME_ADDRESS,
                }
            ]
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unsupported RELA",
            ):
                apollo_overlay.extract_in_place_function_section(
                    rela_object,
                    "relocated_leaf",
                    runtime_address=(
                        self.OVERLAY_RUNTIME_ADDRESS
                        + int(leaf["expected"]["alignment"])
                    ),
                    relocation_configs=resolved,
                )

            unsupported_object = root / "unsupported.o"
            unsupported_data = bytearray(data)
            relocation_entry = int(relocation_section["offset"])
            info = struct.unpack_from(
                "<I",
                unsupported_data,
                relocation_entry + 4,
            )[0]
            struct.pack_into(
                "<I",
                unsupported_data,
                relocation_entry + 4,
                (info & ~0xFF) | apollo_overlay.R_ARM_REL32,
            )
            unsupported_object.write_bytes(unsupported_data)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unsupported relocation type 3",
            ):
                apollo_overlay.extract_in_place_function_section(
                    unsupported_object,
                    "relocated_leaf",
                    runtime_address=(
                        self.OVERLAY_RUNTIME_ADDRESS
                        + int(leaf["expected"]["alignment"])
                    ),
                    relocation_configs=resolved,
                )

            placeholder_object = root / "placeholder.o"
            placeholder_data = bytearray(data)
            relocation_offset = int(leaf["relocations"][0]["offset"])
            function_bytes = int(function_section["offset"])
            placeholder_data[function_bytes + relocation_offset] ^= 1
            placeholder_object.write_bytes(placeholder_data)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "canonical zero-symbol REL placeholder",
            ):
                apollo_overlay.extract_in_place_function_section(
                    placeholder_object,
                    "relocated_leaf",
                    runtime_address=(
                        self.OVERLAY_RUNTIME_ADDRESS
                        + int(leaf["expected"]["alignment"])
                    ),
                    relocation_configs=resolved,
                )

    def test_requires_relocation_symbol_to_be_global_and_undefined(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source, object_path = self._write_and_compile(
                root,
                filename="defined.c",
                source_text=self._call_source(
                    define_target=True,
                    include_unrelated_state=False,
                ),
            )
            self.assertTrue(source.exists())
            relocations = self._observed_relocations(
                object_path,
                "relocated_leaf",
            )
            self.assertEqual(len(relocations), 1)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "global undefined symbol or an explicitly selected whole "
                "global sibling function",
            ):
                apollo_overlay.extract_in_place_function_section(
                    object_path,
                    "relocated_leaf",
                    runtime_address=self.OVERLAY_RUNTIME_ADDRESS,
                    relocation_configs=[
                        {
                            **relocations[0],
                            "target_address": self.OVERLAY_RUNTIME_ADDRESS,
                        }
                    ],
                )

    def test_selected_defined_sibling_call_and_jump_are_relocated(self) -> None:
        for tail_call, expected_type, link in (
            (False, "R_ARM_THM_CALL", True),
            (True, "R_ARM_THM_JUMP24", False),
        ):
            with self.subTest(type=expected_type):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    configs, _before_caller, _functions, _object, _resolved = (
                        self._prepared_defined_sibling_pair(
                            root,
                            tail_call=tail_call,
                        )
                    )
                    overlay, functions, _link_report, reports = self._append(
                        root,
                        leaf_configs=configs,
                    )

                target = reports[0]
                caller = reports[1]
                relocation = caller["extraction"]["relocations"][0]
                self.assertEqual(relocation["type"], expected_type)
                self.assertEqual(
                    relocation["target_function"],
                    "selected_sibling_target",
                )
                self.assertEqual(
                    relocation["target_address"],
                    target["placement"]["runtime_address"],
                )
                caller_offset = int(caller["placement"]["offset"])
                relocation_offset = int(relocation["offset"])
                self.assertEqual(
                    apollo_overlay.decode_thumb_branch(
                        self.OVERLAY_RUNTIME_ADDRESS
                        + caller_offset
                        + relocation_offset,
                        overlay[
                            caller_offset + relocation_offset:
                            caller_offset + relocation_offset + 4
                        ],
                        link=link,
                    ),
                    target["placement"]["runtime_address"],
                )
                self.assertEqual(
                    functions["selected_sibling_target"]["offset"],
                    target["placement"]["offset"],
                )

    def test_defined_sibling_requires_selected_whole_global_function(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            configs, overlay_after_target, functions_after_target, object_path, resolved = (
                self._prepared_defined_sibling_pair(
                    root,
                    tail_call=False,
                )
            )
            caller = configs[1]
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "explicitly selected whole global sibling function",
            ):
                self._append(
                    root,
                    leaf_configs=[caller],
                    overlay=overlay_after_target,
                    functions=functions_after_target,
                )

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unavailable prior overlay function",
            ):
                self._append(
                    root,
                    leaf_configs=[caller, configs[0]],
                    overlay=overlay_after_target,
                    functions=self.PRIMARY_FUNCTIONS,
                )

            unlisted = copy.deepcopy(caller)
            unlisted["relocations"] = []
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "explicitly selected whole global sibling function",
            ):
                self._append(
                    root,
                    leaf_configs=[configs[0], unlisted],
                )

            data, sections = apollo_overlay.parse_elf32(object_path)
            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            symbol_table = apollo_overlay.section_named(sections, ".symtab")
            target_index = next(
                index
                for index, symbol in enumerate(symbols)
                if symbol["name"] == "selected_sibling_target"
            )
            target_entry = int(symbol_table["offset"]) + target_index * 16
            caller_section = apollo_overlay.section_named(
                sections,
                ".text.selected_sibling_caller",
            )
            original_fields = list(
                struct.unpack_from("<IIIBBH", data, target_entry)
            )

            cases = []
            defined_data = original_fields.copy()
            defined_data[3] = (
                apollo_overlay.STB_GLOBAL << 4
            ) | apollo_overlay.STT_OBJECT
            cases.append(("defined-data", defined_data))
            local_function = original_fields.copy()
            local_function[3] = (
                apollo_overlay.STB_LOCAL << 4
            ) | apollo_overlay.STT_FUNC
            cases.append(("local", local_function))
            weak_function = original_fields.copy()
            weak_function[3] = (2 << 4) | apollo_overlay.STT_FUNC
            cases.append(("weak", weak_function))
            same_section = original_fields.copy()
            same_section[5] = int(caller_section["index"])
            same_section[1] = 1
            same_section[2] = int(caller_section["size"])
            cases.append(("same-section", same_section))
            interior = original_fields.copy()
            interior[1] = 3
            interior[2] = int(interior[2]) - 2
            cases.append(("interior", interior))

            caller_runtime = (
                self.OVERLAY_RUNTIME_ADDRESS
                + int(caller["expected"]["offset"])
            )
            for name, fields in cases:
                with self.subTest(name=name):
                    mutated = bytearray(data)
                    struct.pack_into(
                        "<IIIBBH",
                        mutated,
                        target_entry,
                        *fields,
                    )
                    mutated_object = root / f"defined-sibling-{name}.o"
                    mutated_object.write_bytes(mutated)
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "explicitly selected whole global sibling function",
                    ):
                        apollo_overlay.extract_in_place_function_section(
                            mutated_object,
                            "selected_sibling_caller",
                            runtime_address=caller_runtime,
                            relocation_configs=resolved,
                            allowed_defined_relocation_targets=frozenset(
                                {"selected_sibling_target"}
                            ),
                        )

    def test_authenticates_source_toolchain_final_bytes_and_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf, _bytes, _source, _object, _offset = self._prepared_leaf(root)
            cases: list[tuple[str, dict[str, object], str]] = []

            bad_source_sha = copy.deepcopy(leaf)
            bad_source_sha["source"]["sha256"] = "0" * 64
            cases.append(
                ("source-sha", bad_source_sha, "source SHA-256 differs")
            )

            bad_source_size = copy.deepcopy(leaf)
            bad_source_size["source"]["size"] += 1
            cases.append(
                ("source-size", bad_source_size, "source size differs")
            )

            bad_toolchain = copy.deepcopy(leaf)
            bad_toolchain["toolchain"]["flags"].remove("-fdata-sections")
            cases.append(
                ("toolchain", bad_toolchain, "requires -fdata-sections")
            )

            bad_size = copy.deepcopy(leaf)
            bad_size["expected"]["size"] += 2
            cases.append(
                ("final-size", bad_size, "output differs from reviewed pins")
            )

            bad_sha = copy.deepcopy(leaf)
            bad_sha["expected"]["sha256"] = "0" * 64
            cases.append(
                ("final-sha", bad_sha, "output differs from reviewed pins")
            )

            bad_offset = copy.deepcopy(leaf)
            bad_offset["expected"]["offset"] += 2
            cases.append(
                ("offset", bad_offset, "offset differs from reviewed")
            )

            bad_unrelocated = copy.deepcopy(leaf)
            bad_unrelocated["expected"]["unrelocated_sha256"] = "0" * 64
            cases.append(
                (
                    "unrelocated-sha",
                    bad_unrelocated,
                    "unrelocated SHA-256 differs",
                )
            )

            actual_alignment = int(leaf["expected"]["alignment"])
            bad_alignment = copy.deepcopy(leaf)
            bad_alignment["expected"]["alignment"] = actual_alignment * 2
            cases.append(
                ("alignment", bad_alignment, "alignment differs")
            )

            invalid_alignment = copy.deepcopy(leaf)
            invalid_alignment["expected"]["alignment"] = 3
            cases.append(
                (
                    "invalid-alignment",
                    invalid_alignment,
                    "power-of-two alignment",
                )
            )

            for name, config, message in cases:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        self._append(root, leaf_configs=[config])

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "output differs from reviewed pins",
            ):
                placement_sensitive = copy.deepcopy(leaf)
                placement_sensitive["expected"].pop("offset")
                self._append(
                    root,
                    leaf_configs=[placement_sensitive],
                    overlay=self.PRIMARY_OVERLAY + b"\x00\xbf",
                )

    def test_rejects_alignment_and_branch_range_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf, _bytes, _source, object_path, offset = (
                self._prepared_leaf(root)
            )
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "halfword-aligned overlay runtime address",
            ):
                self._append(
                    root,
                    leaf_configs=[leaf],
                    overlay_runtime_address=(
                        self.OVERLAY_RUNTIME_ADDRESS + 1
                    ),
                )

            resolved = [
                {
                    "offset": leaf["relocations"][0]["offset"],
                    "type": leaf["relocations"][0]["type"],
                    "symbol": "primary",
                    "target_address": 0x02000000,
                }
            ]
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "outside the \\+/-16 MiB range",
            ):
                apollo_overlay.extract_in_place_function_section(
                    object_path,
                    "relocated_leaf",
                    runtime_address=self.OVERLAY_RUNTIME_ADDRESS + offset,
                    relocation_configs=resolved,
                )

            odd_target = copy.deepcopy(leaf)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "Thumb target must be halfword aligned",
            ):
                self._append(
                    root,
                    leaf_configs=[odd_target],
                    functions={"primary": {"offset": 1, "size": 2}},
                )


if __name__ == "__main__":
    unittest.main()
