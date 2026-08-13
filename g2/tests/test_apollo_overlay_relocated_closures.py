from __future__ import annotations

import copy
import hashlib
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import apollo_overlay  # noqa: E402


class ApolloOverlayRelocatedClosureTests(unittest.TestCase):
    RUNTIME_ADDRESS = 0x007B0000
    COPY_ADDRESS = 0x00439BE4
    MOVE_ADDRESS = 0x00439710

    @staticmethod
    def _clang() -> str:
        clang = shutil.which("clang")
        if clang is None:
            raise unittest.SkipTest("clang is unavailable")
        return clang

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _flags() -> list[str]:
        return [
            "-mthumb",
            "-mcpu=cortex-m55",
            "-O2",
            "-ffreestanding",
            "-fno-builtin",
            "-fropi",
            "-ffunction-sections",
            "-fdata-sections",
        ]

    def _compile(self, root: Path, name: str, source: str) -> tuple[Path, Path]:
        source_path = root / name
        object_path = root / f"{Path(name).stem}.o"
        source_path.write_text(source, encoding="utf-8")
        subprocess.run(
            [
                self._clang(),
                "--target=thumbv7em-none-eabi",
                *self._flags(),
                "-c",
                str(source_path),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return source_path, object_path

    @staticmethod
    def _relocations(
        object_path: Path,
        text_section_name: str,
    ) -> list[dict[str, object]]:
        data, sections = apollo_overlay.parse_elf32(object_path)
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        text = apollo_overlay.section_named(sections, text_section_name)
        names = {
            apollo_overlay.R_ARM_REL32: "R_ARM_REL32",
            apollo_overlay.R_ARM_THM_CALL: "R_ARM_THM_CALL",
            apollo_overlay.R_ARM_THM_JUMP24: "R_ARM_THM_JUMP24",
            apollo_overlay.R_ARM_THM_MOVW_ABS_NC: (
                "R_ARM_THM_MOVW_ABS_NC"
            ),
            apollo_overlay.R_ARM_THM_MOVT_ABS: "R_ARM_THM_MOVT_ABS",
            apollo_overlay.R_ARM_THM_MOVW_PREL_NC: (
                "R_ARM_THM_MOVW_PREL_NC"
            ),
            apollo_overlay.R_ARM_THM_MOVT_PREL: "R_ARM_THM_MOVT_PREL",
        }
        result = []
        for section in sections:
            if (
                int(section["type"]) != apollo_overlay.SHT_REL
                or int(section["info"]) != int(text["index"])
            ):
                continue
            for index in range(int(section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II", data, int(section["offset"]) + index * 8
                )
                result.append(
                    {
                        "offset": offset,
                        "type": names[info & 0xFF],
                        "symbol": str(symbols[info >> 8]["name"]),
                    }
                )
        return sorted(result, key=lambda item: int(item["offset"]))

    @staticmethod
    def _closure_config(
        object_path: Path,
        *,
        text_section_name: str,
        rodata_section_name: str,
    ) -> dict[str, object]:
        data, sections = apollo_overlay.parse_elf32(object_path)
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        rodata = apollo_overlay.section_named(sections, rodata_section_name)
        start = int(rodata["offset"])
        payload = data[start:start + int(rodata["size"])]
        retained = [
            {
                "name": str(symbol["name"]),
                "offset": int(symbol["value"]),
                "size": int(symbol["size"]),
            }
            for symbol in symbols
            if int(symbol["section_index"]) == int(rodata["index"])
            and int(symbol["type"]) == apollo_overlay.STT_OBJECT
            and symbol["name"]
        ]
        retained.sort(key=lambda item: item["offset"])
        return {
            "text_section": text_section_name,
            "rodata": {
                "section": rodata_section_name,
                "size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "alignment": int(rodata["alignment"]),
                "symbols": retained,
            },
        }

    def _fixed_relocations(
        self,
        object_path: Path,
        text_section_name: str,
    ) -> list[dict[str, object]]:
        result = self._relocations(object_path, text_section_name)
        targets = {
            "__aeabi_memcpy": self.COPY_ADDRESS,
            "__aeabi_memmove": self.MOVE_ADDRESS,
            "external_copy": self.COPY_ADDRESS,
            "external_move": self.MOVE_ADDRESS,
        }
        for item in result:
            if item["type"] in ("R_ARM_THM_CALL", "R_ARM_THM_JUMP24"):
                item["target_address"] = targets[str(item["symbol"])]
        return result

    @staticmethod
    def _assembly_movwt_source() -> str:
        return r"""
.syntax unified
.thumb
.section .text.closure_leaf,"ax",%progbits
.p2align 2
.global closure_leaf
.type closure_leaf,%function
.thumb_func
closure_leaf:
    bl external_copy
    bl external_move
.Linc_movw:
    .inst.w 0xf2400000
    .reloc .Linc_movw, R_ARM_THM_MOVW_PREL_NC, inc32table
.Linc_movt:
    .inst.w 0xf2c00004
    .reloc .Linc_movt, R_ARM_THM_MOVT_PREL, inc32table
.Ldec_movw:
    .inst.w 0xf2400000
    .reloc .Ldec_movw, R_ARM_THM_MOVW_PREL_NC, dec64table
.Ldec_movt:
    .inst.w 0xf2c00004
    .reloc .Ldec_movt, R_ARM_THM_MOVT_PREL, dec64table
    bx lr
.size closure_leaf, .-closure_leaf

.section .rodata.tables,"a",%progbits
.p2align 2
.type inc32table,%object
inc32table:
    .byte 0, 1, 2, 1, 0, 4, 4, 4
.size inc32table, .-inc32table
.type dec64table,%object
dec64table:
    .byte 0, 0, 0, 1, 0, 4, 4, 4
.size dec64table, .-dec64table
"""

    @staticmethod
    def _assembly_prel_oracle_source() -> str:
        return r"""
.syntax unified
.thumb
.section .text.closure_leaf,"ax",%progbits
.p2align 2
.global closure_leaf
.type closure_leaf,%function
.thumb_func
closure_leaf:
.Lstr_movw:
    .inst.w 0xf64f70ec
    .reloc .Lstr_movw, R_ARM_THM_MOVW_PREL_NC, oracle_string
.Lstr_movt:
    .inst.w 0xf6cf70f0
    .reloc .Lstr_movt, R_ARM_THM_MOVT_PREL, oracle_string
.Lzero_movw:
    .inst.w 0xf2400100
    .reloc .Lzero_movw, R_ARM_THM_MOVW_PREL_NC, oracle_string
.Lzero_movt:
    .inst.w 0xf2c00100
    .reloc .Lzero_movt, R_ARM_THM_MOVT_PREL, oracle_string
    bx lr
.size closure_leaf, .-closure_leaf

.section .rodata.tables,"a",%progbits
.p2align 2
.type oracle_string,%object
oracle_string:
    .asciz "oracle"
.size oracle_string, .-oracle_string
"""

    @staticmethod
    def _assembly_rel32_source() -> str:
        return r"""
.syntax unified
.thumb
.section .text.closure_leaf,"ax",%progbits
.p2align 2
.global closure_leaf
.type closure_leaf,%function
.thumb_func
closure_leaf:
    bl external_copy
    bl external_move
    bx lr
.Linc_rel32:
    .word 0
    .reloc .Linc_rel32, R_ARM_REL32, inc32table
.Ldec_rel32:
    .word 0
    .reloc .Ldec_rel32, R_ARM_REL32, dec64table
.size closure_leaf, .-closure_leaf

.section .rodata.tables,"a",%progbits
.p2align 2
.type inc32table,%object
inc32table:
    .byte 0, 1, 2, 1, 0, 4, 4, 4
.size inc32table, .-inc32table
.type dec64table,%object
dec64table:
    .byte 0, 0, 0, 1, 0, 4, 4, 4
.size dec64table, .-dec64table
"""

    @staticmethod
    def _assembly_easylogger_closure_source() -> str:
        return r"""
.syntax unified
.thumb
.section .text.closure_leaf,"ax",%progbits
.p2align 2
.global closure_leaf
.type closure_leaf,%function
.thumb_func
closure_leaf:
    bl closure_leaf
    b.w external_jump
.Ldata_movw:
    .inst.w 0xf2400000
    .reloc .Ldata_movw, R_ARM_THM_MOVW_ABS_NC, external_data
.Ldata_movt:
    .inst.w 0xf2c00000
    .reloc .Ldata_movt, R_ARM_THM_MOVT_ABS, external_data
.Lstr_movw:
    .inst.w 0xf2400000
    .reloc .Lstr_movw, R_ARM_THM_MOVW_PREL_NC, .L.str
.Lstr_movt:
    .inst.w 0xf2c00004
    .reloc .Lstr_movt, R_ARM_THM_MOVT_PREL, .L.str
    bx lr
.size closure_leaf, .-closure_leaf

.section .rodata.strings,"a",%progbits
.type .L.str,%object
.L.str:
    .asciz "easylogger"
.size .L.str, .-.L.str
"""

    @staticmethod
    def _assembly_no_rodata_leaf_source() -> str:
        return r"""
.syntax unified
.thumb
.section .text.submit_leaf,"ax",%progbits
.p2align 2
.global submit_leaf
.type submit_leaf,%function
.thumb_func
submit_leaf:
    bl prior
.Lhandle_movw:
    .inst.w 0xf2400000
    .reloc .Lhandle_movw, R_ARM_THM_MOVW_ABS_NC, event_handle
.Lhandle_movt:
    .inst.w 0xf2c00000
    .reloc .Lhandle_movt, R_ARM_THM_MOVT_ABS, event_handle
    b.w external_jump
    bx lr
.size submit_leaf, .-submit_leaf
"""

    def test_rel32_closure_is_pinned_relocated_and_appended(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source, object_path = self._compile(
                root, "closure.S", self._assembly_rel32_source()
            )
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.tables",
            )
            relocations = self._fixed_relocations(
                object_path, ".text.closure_leaf"
            )
            self.assertEqual(
                {item["type"] for item in relocations},
                {"R_ARM_THM_CALL", "R_ARM_REL32"},
            )
            blob, extraction = apollo_overlay.extract_relocated_function_closure(
                object_path,
                "closure_leaf",
                runtime_address=self.RUNTIME_ADDRESS,
                closure_config=closure,
                relocation_configs=relocations,
            )
            leaf_config = {
                "function": "closure_leaf",
                "source": {
                    "path": source.name,
                    "size": len(source.read_bytes()),
                    "sha256": self._sha256(source.read_bytes()),
                },
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": self._flags(),
                },
                "expected": {
                    "size": extraction["size"],
                    "sha256": extraction["sha256"],
                    "alignment": extraction["alignment"],
                    "offset": 0,
                    "unrelocated_sha256": extraction["unrelocated_sha256"],
                    "closure_size": extraction["closure_size"],
                    "closure_sha256": extraction["closure_sha256"],
                    "rodata_offset": extraction["rodata"]["offset"],
                },
                "closure": closure,
                "relocations": relocations,
            }
            overlay, functions, link, reports = (
                apollo_overlay.append_relocated_leaves(
                    root=root,
                    clang=self._clang(),
                    overlay=b"",
                    overlay_runtime_address=self.RUNTIME_ADDRESS,
                    functions={},
                    link_report={},
                    leaf_configs=[leaf_config],
                    object_root=root,
                )
            )

        self.assertEqual(overlay, blob)
        self.assertEqual(
            functions["closure_leaf"],
            {"offset": 0, "size": extraction["size"]},
        )
        self.assertEqual(link["relocated_text_size"], extraction["size"])
        self.assertEqual(
            link["relocated_rodata_size"], extraction["rodata"]["size"]
        )
        self.assertEqual(
            reports[0]["placement"]["size"], extraction["closure_size"]
        )
        self.assertEqual(
            reports[0]["pins"]["closure_sha256"],
            extraction["closure_sha256"],
        )
        for relocation in extraction["relocations"]:
            if relocation["type"] == "R_ARM_THM_CALL":
                offset = int(relocation["offset"])
                self.assertEqual(
                    apollo_overlay.decode_thumb_branch(
                        self.RUNTIME_ADDRESS + offset,
                        blob[offset:offset + 4],
                        link=True,
                    ),
                    relocation["target_address"],
                )
            elif relocation["type"] == "R_ARM_REL32":
                offset = int(relocation["offset"])
                relative = struct.unpack_from("<i", blob, offset)[0]
                self.assertEqual(offset + relative, relocation["target_offset"])

    def test_movw_movt_prel_closure_resolves_local_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            _source, object_path = self._compile(
                root, "closure.S", self._assembly_movwt_source()
            )
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.tables",
            )
            relocations = self._fixed_relocations(
                object_path, ".text.closure_leaf"
            )
            self.assertEqual(
                [item["type"] for item in relocations],
                [
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_MOVW_PREL_NC",
                    "R_ARM_THM_MOVT_PREL",
                    "R_ARM_THM_MOVW_PREL_NC",
                    "R_ARM_THM_MOVT_PREL",
                ],
            )
            blob, report = apollo_overlay.extract_relocated_function_closure(
                object_path,
                "closure_leaf",
                runtime_address=self.RUNTIME_ADDRESS,
                closure_config=closure,
                relocation_configs=relocations,
            )
            record_closure = copy.deepcopy(closure)
            record_closure["text_section"] = ".text.canonical_other_profile"
            record_relocations = [
                copy.deepcopy(relocations[0]),
                copy.deepcopy(relocations[1]),
                {
                    "offset": 0x64,
                    "type": "R_ARM_REL32",
                    "symbol": "inc32table",
                },
                {
                    "offset": 0x68,
                    "type": "R_ARM_REL32",
                    "symbol": "dec64table",
                },
            ]
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "relocation sequence differs under this toolchain",
            ):
                apollo_overlay.extract_relocated_function_closure(
                    object_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=record_closure,
                    relocation_configs=record_relocations,
                    record=True,
                )
            recorded_blob, recorded = (
                apollo_overlay.extract_relocated_function_closure(
                    object_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=record_closure,
                    relocation_configs=relocations,
                    record=True,
                )
            )

            nonzero_source = (
                self._assembly_movwt_source()
                .replace("0xf2400000", "0xf64f70ec", 1)
                .replace("0xf2c00004", "0xf6cf70f0", 1)
            )
            _nonzero_source, nonzero_object = self._compile(
                root,
                "prel-signed-nonzero.S",
                nonzero_source,
            )
            nonzero_closure = self._closure_config(
                nonzero_object,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.tables",
            )
            nonzero_blob, nonzero_report = (
                apollo_overlay.extract_relocated_function_closure(
                    nonzero_object,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=nonzero_closure,
                    relocation_configs=self._fixed_relocations(
                        nonzero_object,
                        ".text.closure_leaf",
                    ),
                )
            )

            missing_prel_movt = copy.deepcopy(relocations)
            missing_prel_movt.pop(3)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "adjacent same-symbol pair",
            ):
                apollo_overlay.extract_relocated_function_closure(
                    object_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=closure,
                    relocation_configs=missing_prel_movt,
                )

            for filename, replacement, message in (
                (
                    "prel-wrong-opcode.S",
                    ("0xf2400000", "0x00000000"),
                    "canonical Thumb MOVW instruction",
                ),
                (
                    "prel-inconsistent-addends.S",
                    ("0xf2c00004", "0xf2c80000"),
                    "same upper 16-bit relocation result",
                ),
                (
                    "prel-register-mismatch.S",
                    ("0xf2c00004", "0xf2c00104"),
                    "same destination register",
                ),
            ):
                with self.subTest(prel=filename):
                    _variant_source, variant_object = self._compile(
                        root,
                        filename,
                        self._assembly_movwt_source().replace(
                            replacement[0],
                            replacement[1],
                            1,
                        ),
                    )
                    variant_closure = self._closure_config(
                        variant_object,
                        text_section_name=".text.closure_leaf",
                        rodata_section_name=".rodata.tables",
                    )
                    with self.assertRaisesRegex(apollo_overlay.BuildError, message):
                        apollo_overlay.extract_relocated_function_closure(
                            variant_object,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=variant_closure,
                            relocation_configs=self._fixed_relocations(
                                variant_object,
                                ".text.closure_leaf",
                            ),
                        )

        self.assertEqual(report["relocation_count"], 6)
        self.assertEqual(recorded_blob, blob)
        self.assertEqual(recorded["section"], ".text.closure_leaf")
        self.assertEqual(recorded["relocations"], report["relocations"])
        nonzero_pair = nonzero_report["relocations"][2]
        self.assertEqual(nonzero_pair["prel_low_addend"], -20)
        self.assertEqual(nonzero_pair["prel_high_addend"], -16)
        self.assertEqual(nonzero_pair["prel_register"], 0)
        self.assertEqual(
            nonzero_pair["prel_result"],
            (
                int(nonzero_pair["target_offset"])
                - 20
                - int(nonzero_pair["offset"])
            ) & 0xFFFFFFFF,
        )
        first, second = struct.unpack_from(
            "<HH", nonzero_blob, int(nonzero_pair["offset"])
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(first, second),
            nonzero_pair["prel_result"] & 0xFFFF,
        )
        for relocation in report["relocations"][2:]:
            offset = int(relocation["offset"])
            first, second = struct.unpack_from("<HH", blob, offset)
            immediate = apollo_overlay.thumb_movwt_immediate(first, second)
            relative = int(relocation["prel_result"])
            expected = (
                relative >> 16
                if relocation["type"] == "R_ARM_THM_MOVT_PREL"
                else relative
            ) & 0xFFFF
            self.assertEqual(immediate, expected)

    def test_prel_movwt_pair_wraps_only_after_signed_pair_validation(self) -> None:
        blob = bytearray(8)
        low = apollo_overlay.thumb_movwt_with_immediate(
            0xF240,
            0x0000,
            0x8000,
        )
        high = apollo_overlay.thumb_movwt_with_immediate(
            0xF2C0,
            0x0000,
            0x8004,
        )
        struct.pack_into("<HHHH", blob, 0, *low, *high)

        details = apollo_overlay.resolve_prel_movwt_pair(blob, 0, 0)

        self.assertEqual(details["low_addend"], -32768)
        self.assertEqual(details["high_addend"], -32764)
        self.assertEqual(details["result"], 0xFFFF8000)
        low_first, low_second, high_first, high_second = struct.unpack(
            "<HHHH", blob
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(low_first, low_second),
            0x8000,
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(high_first, high_second),
            0xFFFF,
        )

    def test_prel_movwt_pair_accepts_zero_rel_addends_without_hiding_carry(
        self,
    ) -> None:
        blob = bytearray(8)
        struct.pack_into("<HHHH", blob, 0, 0xF240, 0, 0xF2C0, 0)

        details = apollo_overlay.resolve_prel_movwt_pair(blob, 0, 0x1234)

        self.assertEqual(details["low_addend"], 0)
        self.assertEqual(details["high_addend"], 0)
        self.assertEqual(details["low_result"], 0x1234)
        self.assertEqual(details["high_result"], 0x1230)
        self.assertEqual(details["result"], 0x1234)
        low_first, low_second, high_first, high_second = struct.unpack(
            "<HHHH", blob
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(low_first, low_second),
            0x1234,
        )
        self.assertEqual(
            apollo_overlay.thumb_movwt_immediate(high_first, high_second),
            0,
        )

        boundary = bytearray(8)
        struct.pack_into("<HHHH", boundary, 0, 0xF240, 0, 0xF2C0, 0)
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "same upper 16-bit relocation result",
        ):
            apollo_overlay.resolve_prel_movwt_pair(
                boundary,
                0,
                0x10000,
            )

    def test_prel_movwt_pair_matches_lld_rel_oracle(self) -> None:
        pinned_linker = (
            OPENCFW_ROOT
            / "build"
            / "toolchains"
            / "lld-22.1.8"
            / "bin"
            / "ld.lld"
        )
        linker = shutil.which("ld.lld")
        if linker is None and pinned_linker.is_file():
            linker = str(pinned_linker)
        if linker is None:
            self.skipTest("ld.lld is unavailable")
        try:
            subprocess.run(
                [linker, "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("the discovered ld.lld cannot execute on this host")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            _source, object_path = self._compile(
                root,
                "prel-oracle.S",
                self._assembly_prel_oracle_source(),
            )
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.tables",
            )
            local_blob, report = (
                apollo_overlay.extract_relocated_function_closure(
                    object_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=closure,
                    relocation_configs=self._relocations(
                        object_path,
                        ".text.closure_leaf",
                    ),
                )
            )
            script = root / "prel-oracle.ld"
            script.write_text(
                "SECTIONS {\n"
                f"  . = 0x{self.RUNTIME_ADDRESS:08X};\n"
                "  .text : { *(.text.closure_leaf) }\n"
                "  .rodata ALIGN(4) : { *(.rodata.tables) }\n"
                "}\n",
                encoding="utf-8",
            )
            linked = root / "prel-oracle.elf"
            subprocess.run(
                [linker, "-T", str(script), str(object_path), "-o", str(linked)],
                check=True,
                capture_output=True,
                text=True,
            )
            linked_data, linked_sections = apollo_overlay.parse_elf32(linked)
            linked_text = apollo_overlay.section_named(
                linked_sections,
                ".text",
            )
            linked_code = linked_data[
                int(linked_text["offset"]):
                int(linked_text["offset"]) + int(linked_text["size"])
            ]

        self.assertEqual(
            local_blob[:report["size"]],
            linked_code[:report["size"]],
        )
        self.assertEqual(report["relocations"][0]["prel_low_addend"], -20)
        self.assertEqual(report["relocations"][0]["prel_high_addend"], -16)
        self.assertEqual(report["relocations"][2]["prel_low_addend"], 0)
        self.assertEqual(report["relocations"][2]["prel_high_addend"], 0)
        self.assertEqual(
            report["relocations"][2]["prel_result"],
            report["relocations"][2]["prel_low_addend"]
            + int(report["relocations"][2]["target_offset"])
            - int(report["relocations"][2]["offset"]),
        )

    def test_rejects_every_unlisted_or_unpinned_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            _source, object_path = self._compile(
                root, "closure.S", self._assembly_movwt_source()
            )
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.tables",
            )
            relocations = self._fixed_relocations(
                object_path, ".text.closure_leaf"
            )

            cases = []
            missing_relocation = copy.deepcopy(relocations)
            missing_relocation.pop()
            cases.append((closure, missing_relocation, "unpaired PREL MOVW"))

            wrong_hash = copy.deepcopy(closure)
            wrong_hash["rodata"]["sha256"] = "0" * 64
            cases.append((wrong_hash, relocations, "rodata differs"))

            extra_section_field = copy.deepcopy(closure)
            extra_section_field["other_section"] = ".rodata.other"
            cases.append((extra_section_field, relocations, "unknown fields"))

            incomplete_symbols = copy.deepcopy(closure)
            incomplete_symbols["rodata"]["symbols"].pop()
            cases.append((incomplete_symbols, relocations, "exactly cover"))

            unlisted_symbol = copy.deepcopy(relocations)
            unlisted_symbol[2]["symbol"] = "other_table"
            cases.append((closure, unlisted_symbol, "unlisted local symbol"))

            missing_target = copy.deepcopy(relocations)
            missing_target[0].pop("target_address")
            cases.append((closure, missing_target, "fixed halfword-aligned"))

            unexpected_target = copy.deepcopy(relocations)
            unexpected_target[2]["target_address"] = self.COPY_ADDRESS
            cases.append((closure, unexpected_target, "derived, not configurable"))

            for candidate_closure, candidate_relocations, message in cases:
                with self.subTest(message=message):
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError, message
                    ):
                        apollo_overlay.extract_relocated_function_closure(
                            object_path,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=candidate_closure,
                            relocation_configs=candidate_relocations,
                        )

    def test_easylogger_closure_accepts_only_typed_authenticated_extensions(
        self,
    ) -> None:
        jump_address = 0x004495E4
        data_address = 0x20074570
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source, object_path = self._compile(
                root,
                "easylogger-closure.S",
                self._assembly_easylogger_closure_source(),
            )
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.strings",
            )
            relocations = self._relocations(
                object_path,
                ".text.closure_leaf",
            )
            for relocation in relocations:
                if relocation["symbol"] == "closure_leaf":
                    relocation["target_address"] = self.RUNTIME_ADDRESS
                    relocation["symbol_type"] = "STT_FUNC"
                elif relocation["symbol"] == "external_jump":
                    relocation["target_address"] = jump_address
                    relocation["symbol_type"] = "STT_NOTYPE"
                elif relocation["symbol"] == "external_data":
                    relocation["target_address"] = data_address
                    relocation["symbol_type"] = "STT_NOTYPE"

            blob, extraction = apollo_overlay.extract_relocated_function_closure(
                object_path,
                "closure_leaf",
                runtime_address=self.RUNTIME_ADDRESS,
                closure_config=closure,
                relocation_configs=relocations,
                strict_relocation_contract=True,
            )
            profile_relocations = copy.deepcopy(relocations)
            for relocation in profile_relocations:
                if relocation["symbol"] == "closure_leaf":
                    relocation.pop("target_address")
                    relocation["target_function"] = "closure_leaf"
            leaf_config = {
                "function": "closure_leaf",
                "source": {
                    "path": source.name,
                    "size": len(source.read_bytes()),
                    "sha256": self._sha256(source.read_bytes()),
                },
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": self._flags(),
                },
                "expected": {
                    "size": extraction["size"],
                    "sha256": extraction["sha256"],
                    "alignment": extraction["alignment"],
                    "offset": 0,
                    "unrelocated_sha256": extraction["unrelocated_sha256"],
                    "closure_size": extraction["closure_size"],
                    "closure_sha256": extraction["closure_sha256"],
                    "rodata_offset": extraction["rodata"]["offset"],
                },
                "closure": closure,
                "relocations": relocations,
                "strict_relocation_contract": True,
                "toolchain_profiles": {
                    "focused": {"relocations": profile_relocations}
                },
            }
            appended, _functions, _link, reports = (
                apollo_overlay.append_relocated_leaves(
                    root=root,
                    clang=self._clang(),
                    overlay=b"",
                    overlay_runtime_address=self.RUNTIME_ADDRESS,
                    functions={},
                    link_report={},
                    leaf_configs=[leaf_config],
                    object_root=root,
                    toolchain_profile="focused",
                )
            )

            malformed_cases = []
            missing_movt = copy.deepcopy(relocations)
            missing_movt.pop(3)
            malformed_cases.append((closure, missing_movt, "adjacent same-symbol"))
            mismatched_pair = copy.deepcopy(relocations)
            mismatched_pair[3]["target_address"] += 4
            malformed_cases.append((closure, mismatched_pair, "same-target pair"))
            wrong_self_target = copy.deepcopy(relocations)
            wrong_self_target[0]["target_address"] += 2
            malformed_cases.append(
                (closure, wrong_self_target, "exact selected-function self-call")
            )
            missing_external_type = copy.deepcopy(relocations)
            missing_external_type[1].pop("symbol_type")
            malformed_cases.append(
                (closure, missing_external_type, "exact symbol_type")
            )
            broad_local_name = copy.deepcopy(closure)
            broad_local_name["rodata"]["symbols"][0]["name"] = ".L.evil"
            malformed_cases.append(
                (broad_local_name, relocations, "C identifier or Clang")
            )
            for candidate_closure, candidate_relocations, message in malformed_cases:
                with self.subTest(message=message):
                    with self.assertRaisesRegex(apollo_overlay.BuildError, message):
                        apollo_overlay.extract_relocated_function_closure(
                            object_path,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=candidate_closure,
                            relocation_configs=candidate_relocations,
                            strict_relocation_contract=True,
                        )

            _bad_source, bad_object = self._compile(
                root,
                "bad-absolute-placeholder.S",
                self._assembly_easylogger_closure_source().replace(
                    "0xf2400000",
                    "0x00000000",
                    1,
                ),
            )
            bad_closure = self._closure_config(
                bad_object,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.strings",
            )
            bad_relocations = self._relocations(
                bad_object,
                ".text.closure_leaf",
            )
            for relocation in bad_relocations:
                if relocation["symbol"] == "closure_leaf":
                    relocation["target_address"] = self.RUNTIME_ADDRESS
                    relocation["symbol_type"] = "STT_FUNC"
                elif relocation["symbol"] == "external_jump":
                    relocation["target_address"] = jump_address
                    relocation["symbol_type"] = "STT_NOTYPE"
                elif relocation["symbol"] == "external_data":
                    relocation["target_address"] = data_address
                    relocation["symbol_type"] = "STT_NOTYPE"
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "canonical zero-addend Thumb instruction",
            ):
                apollo_overlay.extract_relocated_function_closure(
                    bad_object,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=bad_closure,
                    relocation_configs=bad_relocations,
                    strict_relocation_contract=True,
                )

        self.assertEqual(appended, blob)
        self.assertEqual(
            reports[0]["extraction"]["relocations"][0]["target_function"],
            "closure_leaf",
        )
        self.assertEqual(closure["rodata"]["symbols"][0]["name"], ".L.str")
        jump = extraction["relocations"][1]
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                self.RUNTIME_ADDRESS + int(jump["offset"]),
                blob[int(jump["offset"]):int(jump["offset"]) + 4],
                link=False,
            ),
            jump_address,
        )
        absolute = extraction["relocations"][2:4]
        low = apollo_overlay.thumb_movwt_immediate(
            *struct.unpack_from("<HH", blob, int(absolute[0]["offset"]))
        )
        high = apollo_overlay.thumb_movwt_immediate(
            *struct.unpack_from("<HH", blob, int(absolute[1]["offset"]))
        )
        self.assertEqual(low | (high << 16), data_address)

    def test_no_rodata_relocated_leaf_supports_submit_style_relocations(
        self,
    ) -> None:
        overlay = b"\x70\x47"
        prior_address = self.RUNTIME_ADDRESS
        data_address = 0x20074570
        jump_address = 0x004495E4
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source, object_path = self._compile(
                root,
                "submit.S",
                self._assembly_no_rodata_leaf_source(),
            )
            raw = self._relocations(object_path, ".text.submit_leaf")
            expected_offset = 4
            runtime_address = self.RUNTIME_ADDRESS + expected_offset
            resolved = copy.deepcopy(raw)
            for relocation in resolved:
                relocation["target_address"] = {
                    "prior": prior_address,
                    "event_handle": data_address,
                    "external_jump": jump_address,
                }[str(relocation["symbol"])]
                relocation["symbol_type"] = "STT_NOTYPE"
            expected_blob, extraction = (
                apollo_overlay.extract_in_place_function_section(
                    object_path,
                    "submit_leaf",
                    runtime_address=runtime_address,
                    relocation_configs=resolved,
                    strict_relocation_contract=True,
                )
            )
            configured = copy.deepcopy(raw)
            for relocation in configured:
                relocation["symbol_type"] = "STT_NOTYPE"
                if relocation["symbol"] == "prior":
                    relocation["target_function"] = "prior"
                else:
                    relocation["target_address"] = {
                        "event_handle": data_address,
                        "external_jump": jump_address,
                    }[str(relocation["symbol"])]
            leaf_config = {
                "function": "submit_leaf",
                "source": {
                    "path": source.name,
                    "size": len(source.read_bytes()),
                    "sha256": self._sha256(source.read_bytes()),
                },
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "flags": self._flags(),
                },
                "expected": {
                    "size": extraction["size"],
                    "sha256": extraction["sha256"],
                    "alignment": extraction["alignment"],
                    "offset": expected_offset,
                    "unrelocated_sha256": extraction["unrelocated_sha256"],
                },
                "relocations": configured,
                "strict_relocation_contract": True,
            }
            appended, _functions, _link, reports = (
                apollo_overlay.append_relocated_leaves(
                    root=root,
                    clang=self._clang(),
                    overlay=overlay,
                    overlay_runtime_address=self.RUNTIME_ADDRESS,
                    functions={"prior": {"offset": 0, "size": len(overlay)}},
                    link_report={},
                    leaf_configs=[leaf_config],
                    object_root=root,
                )
            )

            mismatched_pair = copy.deepcopy(configured)
            mismatched_pair[2]["target_address"] += 4
            bad_config = {**leaf_config, "relocations": mismatched_pair}
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "same-target pair",
            ):
                apollo_overlay.append_relocated_leaves(
                    root=root,
                    clang=self._clang(),
                    overlay=overlay,
                    overlay_runtime_address=self.RUNTIME_ADDRESS,
                    functions={"prior": {"offset": 0, "size": len(overlay)}},
                    link_report={},
                    leaf_configs=[bad_config],
                    object_root=root,
                )
            missing_external_type = copy.deepcopy(configured)
            missing_external_type[0].pop("symbol_type")
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "exact symbol_type",
            ):
                apollo_overlay.append_relocated_leaves(
                    root=root,
                    clang=self._clang(),
                    overlay=overlay,
                    overlay_runtime_address=self.RUNTIME_ADDRESS,
                    functions={"prior": {"offset": 0, "size": len(overlay)}},
                    link_report={},
                    leaf_configs=[
                        {**leaf_config, "relocations": missing_external_type}
                    ],
                    object_root=root,
                )

        self.assertEqual(appended[expected_offset:], expected_blob)
        self.assertEqual(
            reports[0]["extraction"]["relocations"][0]["target_function"],
            "prior",
        )
        self.assertNotIn("rodata", reports[0]["extraction"])

    def test_strict_contract_rejects_alloc_and_external_symbol_metadata(
        self,
    ) -> None:
        jump_address = 0x004495E4
        data_address = 0x20074570

        def closure_relocations(object_path: Path) -> list[dict[str, object]]:
            result = self._relocations(object_path, ".text.closure_leaf")
            for relocation in result:
                if relocation["symbol"] == "closure_leaf":
                    relocation["target_address"] = self.RUNTIME_ADDRESS
                    relocation["symbol_type"] = "STT_FUNC"
                elif relocation["symbol"] == "external_jump":
                    relocation["target_address"] = jump_address
                    relocation["symbol_type"] = "STT_NOTYPE"
                elif relocation["symbol"] == "external_data":
                    relocation["target_address"] = data_address
                    relocation["symbol_type"] = "STT_NOTYPE"
            return result

        def submit_relocations(object_path: Path) -> list[dict[str, object]]:
            result = self._relocations(object_path, ".text.submit_leaf")
            for relocation in result:
                relocation["target_address"] = {
                    "prior": self.RUNTIME_ADDRESS,
                    "event_handle": data_address,
                    "external_jump": jump_address,
                }[str(relocation["symbol"])]
                relocation["symbol_type"] = "STT_NOTYPE"
            return result

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            closure_source = self._assembly_easylogger_closure_source()
            for section_source, section_name in (
                (
                    '\n.section .rodata.unexpected,"a",%progbits\n.byte 1\n',
                    ".rodata.unexpected",
                ),
                (
                    '\n.section .bss.unexpected,"aw",%nobits\n.space 4\n',
                    ".bss.unexpected",
                ),
            ):
                with self.subTest(closure_alloc=section_name):
                    _source, object_path = self._compile(
                        root,
                        f"closure-{section_name[1:]}.S",
                        closure_source + section_source,
                    )
                    closure = self._closure_config(
                        object_path,
                        text_section_name=".text.closure_leaf",
                        rodata_section_name=".rodata.strings",
                    )
                    relocations = closure_relocations(object_path)
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "strict relocation contract rejects unexpected "
                        "allocated sections",
                    ):
                        apollo_overlay.extract_relocated_function_closure(
                            object_path,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=closure,
                            relocation_configs=relocations,
                            strict_relocation_contract=True,
                        )
                    legacy_relocations = copy.deepcopy(relocations)
                    for relocation in legacy_relocations:
                        relocation.pop("symbol_type", None)
                    _blob, legacy = (
                        apollo_overlay.extract_relocated_function_closure(
                            object_path,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=closure,
                            relocation_configs=legacy_relocations,
                        )
                    )
                    self.assertIn(
                        section_name,
                        {
                            item["name"]
                            for item in legacy["discarded_alloc_sections"]
                        },
                    )

            for directive, message in (
                (".type external_jump,%object", "strict external symbol metadata"),
                (".hidden external_jump", "global undefined symbol"),
                (".weak external_jump", "global undefined symbol"),
            ):
                with self.subTest(closure_symbol=directive):
                    variant = closure_source.replace(
                        ".thumb\n",
                        f".thumb\n{directive}\n",
                        1,
                    )
                    _source, object_path = self._compile(
                        root,
                        "closure-symbol.S",
                        variant,
                    )
                    closure = self._closure_config(
                        object_path,
                        text_section_name=".text.closure_leaf",
                        rodata_section_name=".rodata.strings",
                    )
                    with self.assertRaisesRegex(apollo_overlay.BuildError, message):
                        apollo_overlay.extract_relocated_function_closure(
                            object_path,
                            "closure_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            closure_config=closure,
                            relocation_configs=closure_relocations(object_path),
                            strict_relocation_contract=True,
                        )

            submit_source = self._assembly_no_rodata_leaf_source()
            for section_source in (
                '\n.section .rodata.unexpected,"a",%progbits\n.byte 1\n',
                '\n.section .bss.unexpected,"aw",%nobits\n.space 4\n',
            ):
                with self.subTest(submit_alloc=section_source.split()[1]):
                    _source, object_path = self._compile(
                        root,
                        "submit-alloc.S",
                        submit_source + section_source,
                    )
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "strict relocation contract rejects unexpected "
                        "allocated sections",
                    ):
                        apollo_overlay.extract_in_place_function_section(
                            object_path,
                            "submit_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            relocation_configs=submit_relocations(object_path),
                            strict_relocation_contract=True,
                        )

            for directive, message in (
                (".type external_jump,%object", "strict external symbol metadata"),
                (".hidden external_jump", "strict external symbol metadata"),
                (".weak external_jump", "global undefined symbol"),
            ):
                with self.subTest(submit_symbol=directive):
                    variant = submit_source.replace(
                        ".thumb\n",
                        f".thumb\n{directive}\n",
                        1,
                    )
                    _source, object_path = self._compile(
                        root,
                        "submit-symbol.S",
                        variant,
                    )
                    with self.assertRaisesRegex(apollo_overlay.BuildError, message):
                        apollo_overlay.extract_in_place_function_section(
                            object_path,
                            "submit_leaf",
                            runtime_address=self.RUNTIME_ADDRESS,
                            relocation_configs=submit_relocations(object_path),
                            strict_relocation_contract=True,
                        )

    def test_strict_contract_authenticates_then_discards_only_cantunwind(
        self,
    ) -> None:
        source = r"""
static const char closure_text[] = "cantunwind";

__attribute__((used, noinline))
const char *closure_leaf(void)
{
    return closure_text;
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            _source, object_path = self._compile(root, "cantunwind.c", source)
            closure = self._closure_config(
                object_path,
                text_section_name=".text.closure_leaf",
                rodata_section_name=".rodata.closure_text",
            )
            relocations = self._relocations(
                object_path,
                ".text.closure_leaf",
            )
            _blob, extraction = (
                apollo_overlay.extract_relocated_function_closure(
                    object_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=closure,
                    relocation_configs=relocations,
                    strict_relocation_contract=True,
                )
            )
            self.assertEqual(
                extraction["authenticated_cantunwind_discard_count"],
                1,
            )
            authenticated = extraction[
                "authenticated_cantunwind_discards"
            ][0]
            self.assertEqual(authenticated["size"], 8)
            self.assertIn("deliberately discarded", authenticated["policy"])
            self.assertIn(
                authenticated["name"],
                {
                    item["name"]
                    for item in extraction["discarded_alloc_sections"]
                },
            )

            data, sections = apollo_overlay.parse_elf32(object_path)
            companion = apollo_overlay.section_named(
                sections,
                ".ARM.exidx.text.closure_leaf",
            )
            malformed = bytearray(data)
            struct.pack_into(
                "<I",
                malformed,
                int(companion["offset"]) + 4,
                0x8000_0000,
            )
            malformed_path = root / "personality-data.o"
            malformed_path.write_bytes(malformed)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "differs from the reviewed canonical row",
            ):
                apollo_overlay.extract_relocated_function_closure(
                    malformed_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=closure,
                    relocation_configs=relocations,
                    strict_relocation_contract=True,
                )

            cross_source = source + r"""
__attribute__((used, noinline))
int other_leaf(int value)
{
    return value + 1;
}
"""
            _source, cross_path = self._compile(
                root,
                "cantunwind-cross.c",
                cross_source,
            )
            cross_data, cross_sections = apollo_overlay.parse_elf32(cross_path)
            cross_symbols = apollo_overlay.parse_elf32_symbols(
                cross_data,
                cross_sections,
            )
            other_text = apollo_overlay.section_named(
                cross_sections,
                ".text.other_leaf",
            )
            other_section_symbol = next(
                index
                for index, symbol in enumerate(cross_symbols)
                if int(symbol["type"]) == apollo_overlay.STT_SECTION
                and int(symbol["section_index"]) == int(other_text["index"])
            )
            cross_companion = apollo_overlay.section_named(
                cross_sections,
                ".ARM.exidx.text.closure_leaf",
            )
            cross_relocation = next(
                section
                for section in cross_sections
                if int(section["type"]) == apollo_overlay.SHT_REL
                and int(section["info"]) == int(cross_companion["index"])
            )
            cross_mutated = bytearray(cross_data)
            offset, _information = struct.unpack_from(
                "<II",
                cross_mutated,
                int(cross_relocation["offset"]),
            )
            struct.pack_into(
                "<II",
                cross_mutated,
                int(cross_relocation["offset"]),
                offset,
                (other_section_symbol << 8) | apollo_overlay.R_ARM_PREL31,
            )
            cross_mutated_path = root / "cross-function-exidx.o"
            cross_mutated_path.write_bytes(cross_mutated)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "does not bind canonically to the selected text section",
            ):
                apollo_overlay.extract_relocated_function_closure(
                    cross_mutated_path,
                    "closure_leaf",
                    runtime_address=self.RUNTIME_ADDRESS,
                    closure_config=closure,
                    relocation_configs=relocations,
                    strict_relocation_contract=True,
                )

if __name__ == "__main__":
    unittest.main()
