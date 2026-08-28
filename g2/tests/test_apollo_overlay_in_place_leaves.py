from __future__ import annotations

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


class ApolloOverlayInPlaceLeafTests(unittest.TestCase):
    RUN_BASE = 0x1000
    LEAF_ADDRESS = 0x1040
    LITERAL_ADDRESS = 0x1080
    CALL_TARGET = 0x1100
    JUMP_TARGET = 0x1120
    LITERAL_BYTES = bytes.fromhex("204a0720")

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
            "-ffreestanding",
            "-fno-builtin",
            "-ffunction-sections",
            "-fdata-sections",
        ]

    @staticmethod
    def _source(
        *,
        pc8_instruction: str = "0x4800",
        call_instruction: str = "bl callTarget",
        literal_symbol: str = "literalWord",
        declarations: str = (
            ".extern literalWord\n"
            ".extern callTarget\n"
            ".extern jumpTarget\n"
        ),
    ) -> str:
        return (
            ".syntax unified\n"
            ".cpu cortex-m55\n"
            ".thumb\n"
            f"{declarations}"
            '.section .text.fixed_leaf, "ax", %progbits\n'
            ".p2align 1\n"
            ".global fixed_leaf\n"
            ".type fixed_leaf, %function\n"
            ".thumb_func\n"
            "fixed_leaf:\n"
            ".Lliteral:\n"
            f"  .inst.n {pc8_instruction}\n"
            f"  .reloc .Lliteral, R_ARM_THM_PC8, {literal_symbol}\n"
            ".Lcall:\n"
            f"  {call_instruction}\n"
            "  b.w jumpTarget\n"
            "  bx lr\n"
            ".size fixed_leaf, . - fixed_leaf\n"
            '.section .note.GNU-stack, "", %progbits\n'
        )

    def _compile(self, source: Path, object_path: Path) -> None:
        subprocess.run(
            [
                self._clang(),
                "--target=arm-none-eabi",
                *self._flags(),
                "-x",
                "assembler",
                "-c",
                str(source),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def _relocations(
        self,
        *,
        literal_address: int | None = None,
        call_target: int | None = None,
        jump_target: int | None = None,
    ) -> list[dict[str, object]]:
        return [
            {
                "offset": 0,
                "type": "R_ARM_THM_PC8",
                "symbol": "literalWord",
                "target_address": (
                    self.LITERAL_ADDRESS
                    if literal_address is None
                    else literal_address
                ),
                "target_expected_hex": self.LITERAL_BYTES.hex(),
            },
            {
                "offset": 2,
                "type": "R_ARM_THM_CALL",
                "symbol": "callTarget",
                "target_address": (
                    self.CALL_TARGET if call_target is None else call_target
                ),
            },
            {
                "offset": 6,
                "type": "R_ARM_THM_JUMP24",
                "symbol": "jumpTarget",
                "target_address": (
                    self.JUMP_TARGET if jump_target is None else jump_target
                ),
            },
        ]

    def _extract(
        self,
        object_path: Path,
        *,
        runtime_address: int | None = None,
        relocations: list[dict[str, object]] | None = None,
    ) -> tuple[bytes, dict[str, object]]:
        return apollo_overlay.extract_in_place_function_section(
            object_path,
            "fixed_leaf",
            runtime_address=(
                self.LEAF_ADDRESS
                if runtime_address is None
                else runtime_address
            ),
            relocation_configs=(
                self._relocations() if relocations is None else relocations
            ),
        )

    @classmethod
    def _base(
        cls,
        writes: dict[int, bytes],
        *,
        payload_size: int = 0x200,
    ) -> bytes:
        image = bytearray(32 + payload_size)
        for address, data in writes.items():
            offset = 32 + address - cls.RUN_BASE
            if offset < 32 or offset + len(data) > len(image):
                raise AssertionError("test write exceeds synthetic payload")
            image[offset:offset + len(data)] = data
        struct.pack_into("<I", image, 0, len(image))
        struct.pack_into("<I", image, 0x10, 0xCB)
        struct.pack_into("<I", image, 0x14, cls.RUN_BASE)
        struct.pack_into("<I", image, 4, zlib.crc32(image[8:]) & 0xFFFFFFFF)
        return bytes(image)

    @classmethod
    def _patch_config(
        cls,
        patch_sites: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return {
            "run_base": cls.RUN_BASE,
            "preamble_bytes": 32,
            "alignment": 4,
            "patch_sites": [] if patch_sites is None else patch_sites,
        }

    @staticmethod
    def _leaf_report(
        *,
        function: str,
        runtime_address: int,
        leaf: bytes,
        stock_sha256: str | None = None,
        relocations: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return {
            "stock": {
                "size": len(leaf),
                "sha256": (
                    hashlib.sha256(leaf).hexdigest()
                    if stock_sha256 is None
                    else stock_sha256
                ),
            },
            "extraction": {
                "function": function,
                "runtime_address": runtime_address,
                "relocations": [] if relocations is None else relocations,
            },
        }

    def test_exact_allowlisted_relocations_resolve_at_stock_address(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "fixed.S"
            object_path = temporary / "fixed.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, object_path)

            leaf, report = self._extract(object_path)

        pc_base = (self.LEAF_ADDRESS + 4) & ~3
        expected = (
            struct.pack(
                "<H",
                0x4800 | ((self.LITERAL_ADDRESS - pc_base) >> 2),
            )
            + apollo_overlay.encode_thumb_bl(
                self.LEAF_ADDRESS + 2,
                self.CALL_TARGET,
            )
            + apollo_overlay.encode_thumb_b_w(
                self.LEAF_ADDRESS + 6,
                self.JUMP_TARGET,
            )
            + b"\x70\x47"
        )
        self.assertEqual(leaf, expected)
        self.assertEqual(report["runtime_address"], self.LEAF_ADDRESS)
        self.assertEqual(report["relocation_count"], 3)
        self.assertEqual(
            [
                (item["offset"], item["type"], item["symbol"])
                for item in report["relocations"]
            ],
            [
                (0, "R_ARM_THM_PC8", "literalWord"),
                (2, "R_ARM_THM_CALL", "callTarget"),
                (6, "R_ARM_THM_JUMP24", "jumpTarget"),
            ],
        )

    def test_build_keeps_in_place_leaf_out_of_overlay_abi_and_reports_it(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / "build"
            primary = root / "primary.c"
            primary.write_text("void primary(void) {}\n", encoding="utf-8")
            source = root / "fixed.S"
            object_path = root / "probe.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, object_path)
            leaf, _report = self._extract(object_path)

            base_bytes = self._base(
                {
                    self.LEAF_ADDRESS: leaf,
                    self.LITERAL_ADDRESS: self.LITERAL_BYTES,
                }
            )
            base = root / "base.bin"
            base.write_bytes(base_bytes)
            config = {
                "schema_version": 1,
                "name": "in-place-probe",
                "firmware_version": "test",
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": ["-mthumb"],
                },
                "sources": [{"path": "primary.c"}],
                "base": {
                    "path": "base.bin",
                    "size": len(base_bytes),
                    "sha256": hashlib.sha256(base_bytes).hexdigest(),
                },
                "expected": {},
                "functions": ["primary"],
                "in_place_leaves": [
                    {
                        "function": "fixed_leaf",
                        "runtime_address": self.LEAF_ADDRESS,
                        "source": {
                            "path": "fixed.S",
                            "sha256": hashlib.sha256(
                                source.read_bytes()
                            ).hexdigest(),
                            "license": "test-only",
                        },
                        "toolchain": {
                            "target": "arm-none-eabi",
                            "flags": self._flags(),
                        },
                        "stock": {
                            "size": len(leaf),
                            "sha256": hashlib.sha256(leaf).hexdigest(),
                        },
                        "expected": {
                            "size": len(leaf),
                            "sha256": hashlib.sha256(leaf).hexdigest(),
                        },
                        "relocations": self._relocations(),
                    }
                ],
                "patch_sites": [],
                "run_base": self.RUN_BASE,
                "preamble_bytes": 32,
                "alignment": 4,
            }
            config_path = root / "overlay.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            compiled = (
                b"\x70\x47",
                {"primary": {"offset": 0, "size": 2}},
                "test clang",
                {
                    "text_size": 2,
                    "rodata_size": 0,
                    "rodata_sections": [],
                    "resolved_relocation_count": 0,
                    "resolved_relocations": [],
                },
            )

            with mock.patch.object(
                apollo_overlay,
                "compile_overlay",
                return_value=compiled,
            ):
                report = apollo_overlay.build(
                    root=root,
                    config_path=config_path,
                    output_dir=output,
                    clang=self._clang(),
                )

            component = (output / "ota_s200_firmware_ota.bin").read_bytes()

        payload_offset = 32 + self.LEAF_ADDRESS - self.RUN_BASE
        self.assertEqual(
            component[payload_offset:payload_offset + len(leaf)],
            leaf,
        )
        self.assertEqual(report["overlay"]["size"], 2)
        self.assertEqual(set(report["overlay"]["functions"]), {"primary"})
        self.assertNotIn("fixed_leaf", report["overlay"]["functions"])
        self.assertEqual(
            report["component"]["source_owned_in_place_bytes"],
            len(leaf),
        )
        self.assertEqual(
            report["component"]["source_owned_bytes"],
            2 + len(leaf),
        )
        self.assertEqual(len(report["in_place_leaves"]), 1)
        placement = report["in_place_leaves"][0]["placement"]
        self.assertEqual(placement["runtime_address"], self.LEAF_ADDRESS)
        self.assertEqual(
            placement["literal_dependencies"][0]["expected_hex"],
            self.LITERAL_BYTES.hex(),
        )

    def test_rejects_rela_unsupported_and_inexact_relocation_lists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "fixed.S"
            object_path = temporary / "fixed.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, object_path)

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "relocation list differs",
            ):
                self._extract(
                    object_path,
                    relocations=self._relocations()[:-1],
                )

            duplicate = self._relocations()
            duplicate.insert(1, dict(duplicate[0]))
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "duplicate relocation offsets",
            ):
                self._extract(object_path, relocations=duplicate)

            rela_object = temporary / "rela.o"
            raw = bytearray(object_path.read_bytes())
            _data, sections = apollo_overlay.parse_elf32(object_path)
            relocation_section = next(
                item
                for item in sections
                if item["name"] == ".rel.text.fixed_leaf"
            )
            section_table = struct.unpack_from("<I", raw, 0x20)[0]
            section_entry_size = struct.unpack_from("<H", raw, 0x2E)[0]
            section_header = (
                section_table
                + int(relocation_section["index"]) * section_entry_size
            )
            struct.pack_into(
                "<I",
                raw,
                section_header + 4,
                apollo_overlay.SHT_RELA,
            )
            rela_object.write_bytes(raw)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unsupported RELA",
            ):
                self._extract(rela_object)

            unsupported_source = temporary / "unsupported.S"
            unsupported_object = temporary / "unsupported.o"
            unsupported_source.write_text(
                ".syntax unified\n"
                ".cpu cortex-m55\n"
                ".thumb\n"
                ".extern literalWord\n"
                '.section .text.fixed_leaf, "ax", %progbits\n'
                ".global fixed_leaf\n"
                ".type fixed_leaf, %function\n"
                ".thumb_func\n"
                "fixed_leaf:\n"
                "  ldr r0, literalWord\n"
                "  bx lr\n"
                ".size fixed_leaf, . - fixed_leaf\n",
                encoding="utf-8",
            )
            self._compile(unsupported_source, unsupported_object)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "unsupported relocation type 54",
            ):
                self._extract(unsupported_object, relocations=[])

    def test_requires_global_undefined_relocation_symbols(self) -> None:
        cases = {
            "defined": (
                ".global literalWord\n"
                ".type literalWord, %object\n"
                ".section .rodata.literalWord, \"a\", %progbits\n"
                "literalWord:\n"
                "  .word 0x20074a20\n"
                ".size literalWord, . - literalWord\n"
                ".extern callTarget\n"
                ".extern jumpTarget\n"
            ),
            "weak": (
                ".weak literalWord\n"
                ".extern callTarget\n"
                ".extern jumpTarget\n"
            ),
        }
        for name, declarations in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    temporary = Path(directory)
                    source = temporary / "fixed.S"
                    object_path = temporary / "fixed.o"
                    source.write_text(
                        self._source(declarations=declarations),
                        encoding="utf-8",
                    )
                    self._compile(source, object_path)
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "global undefined symbol",
                    ):
                        self._extract(object_path)

    def test_rejects_noncanonical_pc8_and_branch_placeholders(self) -> None:
        cases = {
            "pc8": (
                self._source(pc8_instruction="0x4801"),
                "canonical narrow LDR literal",
            ),
            "branch": (
                self._source(
                    call_instruction=(
                        ".inst.w 0xf000f800\n"
                        "  .reloc .Lcall, R_ARM_THM_CALL, callTarget"
                    )
                ),
                "canonical zero-symbol REL placeholder",
            ),
        }
        for name, (source_text, message) in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    temporary = Path(directory)
                    source = temporary / "fixed.S"
                    object_path = temporary / "fixed.o"
                    source.write_text(source_text, encoding="utf-8")
                    self._compile(source, object_path)
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        self._extract(object_path)

    def test_rejects_relocation_alignment_and_range_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "fixed.S"
            object_path = temporary / "fixed.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, object_path)

            cases = [
                (
                    "runtime",
                    {"runtime_address": self.LEAF_ADDRESS + 1},
                    "runtime_address must be",
                ),
                (
                    "pc8 alignment",
                    {
                        "relocations": self._relocations(
                            literal_address=self.LITERAL_ADDRESS + 2
                        )
                    },
                    "PC8 target must be word aligned",
                ),
                (
                    "pc8 range",
                    {
                        "relocations": self._relocations(
                            literal_address=self.LEAF_ADDRESS + 0x800
                        )
                    },
                    "outside its aligned",
                ),
                (
                    "branch alignment",
                    {
                        "relocations": self._relocations(
                            call_target=self.CALL_TARGET + 1
                        )
                    },
                    "Thumb target must be halfword aligned",
                ),
                (
                    "branch range",
                    {
                        "relocations": self._relocations(
                            jump_target=0x02000000
                        )
                    },
                    "outside the \\+/-16 MiB range",
                ),
            ]
            for name, kwargs, message in cases:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        message,
                    ):
                        self._extract(object_path, **kwargs)

    def test_compile_authenticates_source_toolchain_stock_and_final_pins(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "fixed.S"
            probe = root / "probe.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, probe)
            leaf, _report = self._extract(probe)
            leaf_config = {
                "function": "fixed_leaf",
                "runtime_address": self.LEAF_ADDRESS,
                "source": {
                    "path": "fixed.S",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                },
                "toolchain": {
                    "target": "arm-none-eabi",
                    "flags": self._flags(),
                },
                "stock": {
                    "size": len(leaf),
                    "sha256": hashlib.sha256(leaf).hexdigest(),
                },
                "expected": {
                    "size": len(leaf),
                    "sha256": hashlib.sha256(leaf).hexdigest(),
                },
                "relocations": self._relocations(),
            }

            bad_source = json.loads(json.dumps(leaf_config))
            bad_source["source"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "source SHA-256 differs",
            ):
                apollo_overlay.compile_in_place_leaf(
                    root=root,
                    clang=self._clang(),
                    leaf_config=bad_source,
                    object_path=root / "bad-source.o",
                )

            bad_toolchain = json.loads(json.dumps(leaf_config))
            bad_toolchain["toolchain"]["flags"].remove("-fdata-sections")
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "requires -fdata-sections",
            ):
                apollo_overlay.compile_in_place_leaf(
                    root=root,
                    clang=self._clang(),
                    leaf_config=bad_toolchain,
                    object_path=root / "bad-toolchain.o",
                )

            bad_final = json.loads(json.dumps(leaf_config))
            bad_final["expected"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "output differs from reviewed pins",
            ):
                apollo_overlay.compile_in_place_leaf(
                    root=root,
                    clang=self._clang(),
                    leaf_config=bad_final,
                    object_path=root / "bad-final.o",
                )

            bad_stock = json.loads(json.dumps(leaf_config))
            bad_stock["stock"]["size"] += 2
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "expected and stock spans must have the same size",
            ):
                apollo_overlay.compile_in_place_leaf(
                    root=root,
                    clang=self._clang(),
                    leaf_config=bad_stock,
                    object_path=root / "bad-stock.o",
                )

    def test_patch_authenticates_stock_and_literal_bytes(self) -> None:
        leaf = b"\x00\xbf\x70\x47"
        base = self._base(
            {
                self.LEAF_ADDRESS: leaf,
                self.LITERAL_ADDRESS: self.LITERAL_BYTES,
            }
        )
        literal_relocation = [
            {
                "target_address": self.LITERAL_ADDRESS,
                "target_expected_hex": self.LITERAL_BYTES.hex(),
            }
        ]
        report = self._leaf_report(
            function="fixed",
            runtime_address=self.LEAF_ADDRESS,
            leaf=leaf,
            relocations=literal_relocation,
        )

        bad_stock = dict(report)
        bad_stock["stock"] = {
            "size": len(leaf),
            "sha256": "0" * 64,
        }
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "stock SHA-256 differs",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config(),
                in_place_leaves=[(leaf, bad_stock)],
            )

        bad_literal = self._leaf_report(
            function="fixed",
            runtime_address=self.LEAF_ADDRESS,
            leaf=leaf,
            relocations=[
                {
                    "target_address": self.LITERAL_ADDRESS,
                    "target_expected_hex": "00000000",
                }
            ],
        )
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "literal target.*expected",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config(),
                in_place_leaves=[(leaf, bad_literal)],
            )

    def test_literal_guard_accepts_size_and_sha256_without_stock_bytes(self) -> None:
        digest = hashlib.sha256(self.LITERAL_BYTES).hexdigest()
        relocations = self._relocations()
        relocations[0].pop("target_expected_hex")
        relocations[0]["target_expected_size"] = len(self.LITERAL_BYTES)
        relocations[0]["target_expected_sha256"] = digest
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            source = temporary / "fixed.S"
            object_path = temporary / "fixed.o"
            source.write_text(self._source(), encoding="utf-8")
            self._compile(source, object_path)
            _leaf, extraction = self._extract(
                object_path,
                relocations=relocations,
            )
        reviewed = extraction["relocations"][0]
        self.assertNotIn("target_expected_hex", reviewed)
        self.assertEqual(reviewed["target_expected_size"], len(self.LITERAL_BYTES))
        self.assertEqual(reviewed["target_expected_sha256"], digest)

        leaf = b"\x00\xbf\x70\x47"
        base = self._base(
            {
                self.LEAF_ADDRESS: leaf,
                self.LITERAL_ADDRESS: self.LITERAL_BYTES,
            }
        )
        report = self._leaf_report(
            function="fixed",
            runtime_address=self.LEAF_ADDRESS,
            leaf=leaf,
            relocations=[
                {
                    "target_address": self.LITERAL_ADDRESS,
                    "target_expected_size": len(self.LITERAL_BYTES),
                    "target_expected_sha256": digest,
                }
            ],
        )
        _patched, details = apollo_overlay.patch_component(
            base=base,
            overlay=b"\x70\x47",
            functions={"primary": {"offset": 0, "size": 2}},
            config=self._patch_config(),
            in_place_leaves=[(leaf, report)],
        )
        literal = details["patched_in_place_leaves"][0][
            "literal_dependencies"
        ][0]
        self.assertNotIn("expected_hex", literal)
        self.assertEqual(literal["expected_size"], len(self.LITERAL_BYTES))
        self.assertEqual(literal["expected_sha256"], digest)

        report["extraction"]["relocations"][0]["target_expected_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "literal target.*expected SHA-256",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config(),
                in_place_leaves=[(leaf, report)],
            )

    def test_patch_rejects_leaf_patch_and_literal_overlaps(self) -> None:
        first = b"\x00\xbf\x70\x47"
        second = b"\x70\x47\x00\xbf"
        base = self._base(
            {
                self.LEAF_ADDRESS: first + second,
                self.LITERAL_ADDRESS: self.LITERAL_BYTES,
            }
        )
        first_report = self._leaf_report(
            function="first",
            runtime_address=self.LEAF_ADDRESS,
            leaf=first,
        )
        overlap_report = self._leaf_report(
            function="second",
            runtime_address=self.LEAF_ADDRESS + 2,
            leaf=second,
            stock_sha256=hashlib.sha256(
                base[
                    32 + self.LEAF_ADDRESS + 2 - self.RUN_BASE:
                    32 + self.LEAF_ADDRESS + 6 - self.RUN_BASE
                ]
            ).hexdigest(),
        )
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "overlaps in-place leaf",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config(),
                in_place_leaves=[
                    (first, first_report),
                    (second, overlap_report),
                ],
            )

        patch_site = {
            "name": "overlap-leaf",
            "runtime_address": self.LEAF_ADDRESS,
            "expected_hex": first.hex(),
            "branch": "b_w",
            "target_function": "primary",
        }
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "patch span overlaps in-place leaf",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config([patch_site]),
                in_place_leaves=[(first, first_report)],
            )

        literal_report = self._leaf_report(
            function="literal-user",
            runtime_address=self.LEAF_ADDRESS,
            leaf=first,
            relocations=[
                {
                    "target_address": self.LITERAL_ADDRESS,
                    "target_expected_hex": self.LITERAL_BYTES.hex(),
                }
            ],
        )
        literal_patch = {
            "name": "overlap-literal",
            "runtime_address": self.LITERAL_ADDRESS,
            "expected_hex": self.LITERAL_BYTES.hex(),
            "branch": "b_w",
            "target_function": "primary",
        }
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "overlaps protected literal",
        ):
            apollo_overlay.patch_component(
                base=base,
                overlay=b"\x70\x47",
                functions={"primary": {"offset": 0, "size": 2}},
                config=self._patch_config([literal_patch]),
                in_place_leaves=[(first, literal_report)],
            )

    def test_build_rejects_ambiguous_in_place_registration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "primary.c"
            source.write_text("void fixed_leaf(void) {}\n", encoding="utf-8")
            base = root / "base.bin"
            base.write_bytes(b"base")
            config = {
                "schema_version": 1,
                "name": "ambiguous",
                "firmware_version": "test",
                "toolchain": {"target": "arm-none-eabi", "flags": ["-mthumb"]},
                "sources": [{"path": "primary.c"}],
                "base": {
                    "path": "base.bin",
                    "size": 4,
                    "sha256": hashlib.sha256(b"base").hexdigest(),
                },
                "expected": {},
                "functions": ["fixed_leaf"],
                "in_place_leaves": [{"function": "fixed_leaf"}],
                "patch_sites": [],
                "preamble_bytes": 32,
            }
            config_path = root / "overlay.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "cannot be registered in the overlay function ABI",
            ):
                apollo_overlay.build(
                    root=root,
                    config_path=config_path,
                    output_dir=root / "build",
                    clang=self._clang(),
                )

            config["functions"] = ["primary"]
            config["in_place_leaves"] = [{"function": "fixed_leaf"}]
            config["patch_sites"] = [
                {
                    "target_function": "fixed_leaf",
                }
            ]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                "patch sites cannot target fixed-address in-place leaves",
            ):
                apollo_overlay.build(
                    root=root,
                    config_path=config_path,
                    output_dir=root / "build",
                    clang=self._clang(),
                )


if __name__ == "__main__":
    unittest.main()
