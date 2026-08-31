#!/usr/bin/env python3
"""Hostile qualification for specialized liblc3 immutable-table finalization."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
CONFIG = COMPONENT / "specialization_experiment.json"
BUILDER_PATH = COMPONENT / "build_specialization_experiment.py"
XIP_PATH = COMPONENT / "specialized_xip.py"
OBJCOPY = "/opt/homebrew/opt/llvm@22/bin/llvm-objcopy"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloLiblc3SpecializedXipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or "/usr/bin/clang"
        cls.lld = os.environ.get("OPENCFW_LLD") or "/opt/homebrew/bin/ld.lld"
        if not all(Path(path).is_file()
                   for path in (cls.clang, cls.lld, OBJCOPY)):
            raise unittest.SkipTest("reviewed Apple Clang/LLVM tools unavailable")
        cls.builder = load(BUILDER_PATH, "liblc3_specialized_builder_test")
        cls.xip = load(XIP_PATH, "liblc3_specialized_xip_test")
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="opencfw-lc3-specialized-xip-test-")
        cls.output = Path(cls.temporary.name)
        cls.report = cls.builder.build(
            config_path=CONFIG, output_dir=cls.output,
            clang=cls.clang, lld=cls.lld, objcopy=OBJCOPY)
        cls.variant = cls.report["variants"]["non_hr_only"]
        cls.relocatable = (
            cls.output / "non_hr_only/liblc3_encoder.relocatable.o")

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def relocation_records(self):
        payload, sections = self.builder.B.parse_elf32(self.relocatable)
        symbols = self.builder.B.parse_elf32_symbols(payload, sections)
        return self.xip.relocation_records(payload, sections, symbols)

    def test_builder_converts_before_emitting_relocated_xip(self) -> None:
        policy = self.variant["immutable_table_policy"]
        self.assertEqual(policy["pre_policy_allocated_writable_sections"],
                         [".lc3_table_rodata"])
        self.assertEqual(policy["post_policy_allocated_writable_sections"], [])
        self.assertEqual(policy["runtime_copy_bytes"], 0)
        self.assertEqual(policy["runtime_writable_bytes"], 0)
        self.assertEqual(policy["relocations"]["table_initializers"]["count"],
                         78)
        self.assertEqual(policy["relocations"]["table_code_references"]["count"],
                         12)
        final = self.variant["qualification_finalization"]
        self.assertEqual(final["relocation_application"]["output_relocations"],
                         0)
        raw = (self.output / "non_hr_only/"
               "liblc3_encoder.table_rodata.relocatable.bin").read_bytes()
        relocated = (self.output / "non_hr_only/qualification-final/"
                     "liblc3_encoder.table_rodata.qualification-xip.bin").read_bytes()
        self.assertNotEqual(raw, relocated)
        self.assertEqual(len(raw), len(relocated))
        self.assertEqual(len(raw), 404)
        self.assertFalse(final["production_placement"])
        self.assertFalse(final["runtime_bindings_authenticated_for_stock"])

    def test_hostile_relocation_closure_mutations_fail_closed(self) -> None:
        records = self.relocation_records()
        imports = set(self.variant["receipt"]["retained_imports"])
        self.assertEqual(
            self.xip.validate_relocation_closure(records, imports)["total"],
            484)
        table_index = next(index for index, row in enumerate(records)
                           if row["section"] == ".lc3_table_rodata")
        code_index = next(index for index, row in enumerate(records)
                          if row["section"] == ".text" and
                          row["symbol_section"] == ".lc3_table_rodata")
        external_index = next(index for index, row in enumerate(records)
                              if row["external"])
        mutations = []
        missing = copy.deepcopy(records)
        missing.pop(table_index)
        mutations.append(missing)
        wrong_kind = copy.deepcopy(records)
        wrong_kind[table_index]["type"] = "R_ARM_THM_JUMP24"
        mutations.append(wrong_kind)
        wrong_target = copy.deepcopy(records)
        wrong_target[table_index]["symbol_section"] = ".text"
        mutations.append(wrong_target)
        lost_reference = copy.deepcopy(records)
        lost_reference[code_index]["symbol_section"] = ".rodata"
        mutations.append(lost_reference)
        ingress = copy.deepcopy(records)
        ingress[external_index]["symbol"] = "unadmitted_runtime"
        mutations.append(ingress)
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                with self.assertRaises(self.xip.SpecializedXipError):
                    self.xip.validate_relocation_closure(mutation, imports)

    def test_runtime_binding_map_rejects_missing_even_overlap_far_and_aliases(
            self) -> None:
        final = self.variant["qualification_finalization"]
        layout = final["layout"]
        imports = set(self.variant["receipt"]["retained_imports"])
        bindings = final["runtime_bindings"]
        self.xip.validate_runtime_bindings(
            bindings, allowed_imports=imports, layout=layout)
        first = sorted(bindings)[0]
        second = sorted(bindings)[1]
        mutations = []
        missing = dict(bindings)
        missing.pop(first)
        mutations.append(missing)
        even = dict(bindings)
        even[first] &= ~1
        mutations.append(even)
        overlap = dict(bindings)
        overlap[first] = layout["text"]["start"] | 1
        mutations.append(overlap)
        far = dict(bindings)
        far[first] = 0x03000001
        mutations.append(far)
        alias = dict(bindings)
        alias[first] = alias[second]
        mutations.append(alias)
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                with self.assertRaises(self.xip.SpecializedXipError):
                    self.xip.validate_runtime_bindings(
                        mutation, allowed_imports=imports, layout=layout)

    def test_finalizer_rejects_noncanonical_layout_before_link(self) -> None:
        final = self.variant["qualification_finalization"]
        imports = set(self.variant["receipt"]["retained_imports"])
        mutations = []
        overlap = copy.deepcopy(final["layout"])
        overlap["rodata"]["start"] -= 16
        mutations.append(overlap)
        shifted_table = copy.deepcopy(final["layout"])
        shifted_table["table_rodata"]["start"] += 8
        mutations.append(shifted_table)
        wrong_size = copy.deepcopy(final["layout"])
        wrong_size["table_rodata"]["size"] = 400
        mutations.append(wrong_size)
        for index, layout in enumerate(mutations):
            with self.subTest(case=index), tempfile.TemporaryDirectory(
                    prefix="opencfw-lc3-finalizer-hostile-") as output:
                with self.assertRaises(self.xip.SpecializedXipError):
                    self.xip.finalize_xip(
                        self.relocatable, Path(output), builder=self.builder.B,
                        roots=list(self.variant["receipt"]["roots"]),
                        allowed_imports=imports, lld=self.lld, layout=layout,
                        runtime_bindings=final["runtime_bindings"])

    def test_post_policy_flag_and_final_pointer_tampering_fail_closed(self) -> None:
        payload, sections = self.builder.B.parse_elf32(self.relocatable)
        table = next(section for section in sections
                     if section["name"] == ".lc3_table_rodata")
        tampered = bytearray(payload)
        section_header_offset = (
            struct.unpack_from("<I", tampered, 32)[0] +
            int(table["index"]) * struct.unpack_from("<H", tampered, 46)[0])
        struct.pack_into("<I", tampered, section_header_offset + 8,
                         int(table["flags"]) | self.xip.SHF_WRITE)
        with tempfile.TemporaryDirectory(
                prefix="opencfw-lc3-table-flags-") as output:
            path = Path(output) / "writable.o"
            path.write_bytes(tampered)
            with self.assertRaises(self.xip.SpecializedXipError):
                self.xip.validate_policy_object(
                    path, builder=self.builder.B,
                    roots=list(self.variant["receipt"]["roots"]),
                    allowed_imports=set(
                        self.variant["receipt"]["retained_imports"]),
                    table_readonly=True)

        raw = (self.output / "non_hr_only/"
               "liblc3_encoder.table_rodata.relocatable.bin").read_bytes()
        final_path = (self.output / "non_hr_only/qualification-final/"
                      "liblc3_encoder.table_rodata.qualification-xip.bin")
        final_table = bytearray(final_path.read_bytes())
        final_table[0] ^= 4
        records = [row for row in self.relocation_records()
                   if row["section"] == ".lc3_table_rodata"]
        layout = self.variant["qualification_finalization"]["layout"]
        with self.assertRaises(self.xip.SpecializedXipError):
            self.xip._validate_final_table(
                template=raw, final_table=bytes(final_table),
                table_relocations=records,
                rodata_start=layout["rodata"]["start"],
                rodata_size=layout["rodata"]["size"])


if __name__ == "__main__":
    unittest.main()
