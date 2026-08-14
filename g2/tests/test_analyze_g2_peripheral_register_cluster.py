#!/usr/bin/env python3
"""Guard the Apollo peripheral-register cluster attribution audit."""

from __future__ import annotations

import importlib.util
import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_peripheral_register_cluster.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
CENSUS_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
MANIFESTS = ROOT / "tools/manifests"
AMBIQSUITE = ROOT / "third_party/ambiqsuite-apollo510"

EXPECTED_FAMILY_TOTALS = {
    # family: (functions, envelope_bytes, official_opaque_bytes)
    "ambiqsuite-hal": (6, 7478, 6604),
    "g2-board-support": (3, 1044, 976),
    "investigation-required": (13, 12454, 12414),
}

EXPECTED_RECONCILIATION = {
    "census_register_hint_functions": 22,
    "census_sram_only_functions": 8,
    "census_hardware_hint_functions": 30,
    "validated_register_functions": 9,
    "validated_register_references": 69,
    "sram_indirect_candidates": 1,
    "call_topology_members": 2,
    "hint_collision_functions": 10,
}


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_peripheral_register_cluster", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _register_map(analyzer):
    return analyzer.build_register_map(
        (AMBIQSUITE / "CMSIS/AmbiqMicro/Include/apollo510.h").read_text(encoding="utf-8"),
        (AMBIQSUITE / "mcu/apollo510/regs/am_reg_base_addresses.h").read_text(encoding="utf-8"),
        (AMBIQSUITE / "mcu/apollo510/hal/am_hal_sysctrl.h").read_text(encoding="utf-8"),
    )


class RegisterMapUnitTests(unittest.TestCase):
    """Corpus-independent checks of the CMSIS map, classifier, and decoders."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.register_map = _register_map(cls.analyzer)
        # staticmethod avoids binding the classifier closure as a method
        cls.classify = staticmethod(cls.analyzer.make_classifier(cls.register_map))

    def test_cmsis_map_is_pinned(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(self.register_map["bases"]), analyzer.EXPECTED_CMSIS_BASES)
        self.assertEqual(len(self.register_map["structs"]), analyzer.EXPECTED_CMSIS_STRUCTS)
        mspi = self.register_map["structs"]["MSPI0"][0]
        self.assertEqual(mspi["INTSTAT"], 0x204)
        self.assertEqual(mspi["INTCLR"], 0x208)
        self.assertEqual(self.register_map["bases"]["MSPI0"], 0x40060000)
        self.assertEqual(self.register_map["bases"]["GPIO"], 0x40010000)

    def test_classifier_accepts_real_registers(self) -> None:
        classify = self.classify
        self.assertEqual(classify(0x40060204), ("MSPI0", 0x204, "INTSTAT"))
        self.assertEqual(classify(0x40061204), ("MSPI1", 0x204, "INTSTAT"))
        self.assertEqual(classify(0x400C2000), ("OTP_INFOC", 0, None))
        self.assertEqual(classify(0x47FF0000), ("SYNC_READ", 0, None))
        self.assertEqual(classify(0x400B2000), ("USB", 0x2000, "CLKCTRL"))

    def test_classifier_rejects_constant_collisions(self) -> None:
        classify = self.classify
        # float constants, magic bitmasks, and misaligned junk must not map
        for junk in (0x40000001, 0x41C80000, 0x41200000, 0x55555555,
                     0x5AF00000, 0x4000FFFF, 0x4A24EE74, 0x40800000):
            self.assertIsNone(classify(junk), hex(junk))
        # 0x40000000 is the RSTGEN base itself; only offset 0 maps
        self.assertEqual(classify(0x40000000), ("RSTGEN", 0, "CFG"))

    def test_register_map_fails_closed_on_header_mutation(self) -> None:
        analyzer = self.analyzer
        cmsis = (AMBIQSUITE / "CMSIS/AmbiqMicro/Include/apollo510.h").read_text(encoding="utf-8")
        reg_base = (AMBIQSUITE / "mcu/apollo510/regs/am_reg_base_addresses.h").read_text(encoding="utf-8")
        sysctrl = (AMBIQSUITE / "mcu/apollo510/hal/am_hal_sysctrl.h").read_text(encoding="utf-8")
        mutated = cmsis.replace("#define MSPI0_BASE                  0x40060000UL",
                                "#define MSPI0_BASE                  0x40061000UL", 1)
        self.assertNotEqual(mutated, cmsis)
        with self.assertRaises(analyzer.ClusterError):
            analyzer.build_register_map(mutated, reg_base, sysctrl)
        mutated_sysctrl = sysctrl.replace("0x47FF0000", "0x47FF0004", 1)
        with self.assertRaises(analyzer.ClusterError):
            analyzer.build_register_map(cmsis, reg_base, mutated_sysctrl)
        mutated_reg = reg_base.replace("#define AM_REG_INFO1_BASEADDR           0x42002000\n", "", 1)
        with self.assertRaises(analyzer.ClusterError):
            analyzer.build_register_map(cmsis, mutated_reg, sysctrl)

    def test_struct_parser_rejects_non_32bit_members(self) -> None:
        analyzer = self.analyzer
        self.assertIsNone(analyzer.parse_cmsis_struct("__IOM uint64_t WIDE;"))
        parsed = analyzer.parse_cmsis_struct(
            "__IOM uint32_t CTRL;\nuint32_t RESERVED[2];\nunion { __IOM uint32_t STAT; struct { __IOM uint32_t EN : 1; } STAT_b; } ;"
        )
        self.assertIsNotNone(parsed)
        registers, size = parsed
        self.assertEqual((registers["CTRL"], registers["STAT"], size), (0, 0xC, 0x10))

    def test_ldr_literal_decoder_recovers_pool_constants(self) -> None:
        analyzer = self.analyzer
        load_base = 0x1000
        blob = bytearray(0x100)
        # 16-bit LDR r0, [PC, #4] at 0x1000 -> target 0x1008
        struct.pack_into("<H", blob, 0x000, 0x4801)
        struct.pack_into("<I", blob, 0x008, 0x40060000)
        # 32-bit LDR.W r1, [PC, #8] at 0x1002: hw1 0xF8DF, hw2 0x1008
        struct.pack_into("<H", blob, 0x002, 0xF8DF)
        struct.pack_into("<H", blob, 0x004, 0x1008)
        struct.pack_into("<I", blob, 0x00C, 0x40021000)
        constants = analyzer.scan_code_constants(bytes(blob), load_base, 0x1000, 0x1010)
        self.assertIn(0x40060000, constants)
        self.assertIn("ldr16", constants[0x40060000])
        self.assertIn(0x40021000, constants)
        self.assertIn("ldr32", constants[0x40021000])

    def test_movwt_pair_decoder(self) -> None:
        analyzer = self.analyzer
        load_base = 0x1000
        blob = bytearray(0x40)
        # MOVW r3, #0x0000 (hw1 0xF240, hw2 imm fields 0, rd=3) then
        # MOVT r3, #0x4006 -> 0x40060000
        def mov(hw1_base, imm16, rd):
            i_bit = (imm16 >> 11) & 1
            imm4 = (imm16 >> 12) & 0xF
            imm3 = (imm16 >> 8) & 0x7
            imm8 = imm16 & 0xFF
            hw1 = hw1_base | (i_bit << 10) | imm4
            hw2 = (imm3 << 12) | (rd << 8) | imm8
            return hw1, hw2
        hw1, hw2 = mov(0xF240, 0x0000, 3)
        struct.pack_into("<H", blob, 0x00, hw1)
        struct.pack_into("<H", blob, 0x02, hw2)
        hw1, hw2 = mov(0xF2C0, 0x4006, 3)
        struct.pack_into("<H", blob, 0x04, hw1)
        struct.pack_into("<H", blob, 0x06, hw2)
        constants = analyzer.scan_code_constants(bytes(blob), load_base, 0x1000, 0x1008)
        self.assertIn(0x40060000, constants)
        self.assertIn("movwt", constants[0x40060000])

    def test_text_scanner_finds_deref_and_cells(self) -> None:
        analyzer = self.analyzer
        lines = [
            "  puVar6 = (uint *)(DAT_004c1c50 + uVar9 * 0x1000 + 0x30);",
            "  *param_2 = *(undefined4 *)(param_1 + 0x400c2000);",
            "  param_6[1] = 0x40000000;",
        ]
        candidates, cell_offsets = analyzer.scan_text_constants(lines)
        self.assertIn(0x004C1C50, candidates)
        self.assertIn("dat-cell", candidates[0x004C1C50])
        self.assertIn(0x400C2000, candidates)
        self.assertIn("deref-const", candidates[0x400C2000])
        # plain assignments are not dereference evidence
        self.assertNotIn(0x40000000, candidates)
        self.assertIn((0x004C1C50, 0x30), cell_offsets)

    def test_attribution_pins_cover_exactly_the_register_hint_set(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            tuple(sorted(analyzer.EXPECTED_ATTRIBUTION)),
            analyzer.EXPECTED_REGISTER_HINT_ENTRIES,
        )
        for family, evidence, confidence in analyzer.EXPECTED_ATTRIBUTION.values():
            self.assertIn(family, analyzer.FAMILIES)
            self.assertIn(evidence, analyzer.EVIDENCE_CLASSES)
            self.assertIn(confidence, analyzer.CONFIDENCE_ORDER)
        reference_entries = {
            entry
            for entry, (_family, evidence, _confidence) in analyzer.EXPECTED_ATTRIBUTION.items()
            if evidence in ("machine-code-register-access", "decompiled-register-access")
        }
        self.assertEqual(reference_entries, set(analyzer.EXPECTED_REFERENCE_SUMMARY))

    def test_census_loader_fails_closed_on_hint_mutation(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "census.tsv"
            target_row = "\t".join(
                (
                    "0x004C3750", "0x004C3750", "0x004C377A", "42", "42",
                    "investigation-required-no-evidence", "none", "none",
                    "references peripheral registers",
                )
            )
            replacement_row = "\t".join(
                (
                    "0x004C3750", "0x004C3750", "0x004C377A", "42", "42",
                    "investigation-required-no-evidence", "none", "none",
                    "no closed-world evidence",
                )
            )
            text = CENSUS_TSV.read_text(encoding="utf-8")
            self.assertIn(target_row, text)
            mutated.write_text(text.replace(target_row, replacement_row, 1), encoding="utf-8")
            with self.assertRaises(analyzer.ClusterError):
                analyzer.load_census_rows(mutated)

    def test_census_loader_fails_closed_on_row_drop(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "census.tsv"
            lines = CENSUS_TSV.read_text(encoding="utf-8").splitlines()
            lines = [line for line in lines if not line.startswith("0x005FA13C")]
            mutated.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(analyzer.ClusterError):
                analyzer.load_census_rows(mutated)


@unittest.skipUnless(
    CORPUS.is_dir() and CENSUS_TSV.is_file(),
    "authenticated corpus/census manifest unavailable",
)
class RegisterClusterAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)
        cls.classify = staticmethod(
            cls.analyzer.make_classifier(_register_map(cls.analyzer))
        )

    def test_reconciliation_is_pinned(self) -> None:
        self.assertEqual(self.report["reconciliation"], EXPECTED_RECONCILIATION)

    def test_family_totals_are_pinned(self) -> None:
        actual = {
            family: (
                bucket["functions"],
                bucket["envelope_bytes"],
                bucket["official_opaque_bytes"],
            )
            for family, bucket in self.report["families"].items()
        }
        self.assertEqual(actual, EXPECTED_FAMILY_TOTALS)
        functions = sum(bucket[0] for bucket in actual.values())
        self.assertEqual(functions, 22)

    def test_per_function_attribution_matches_pins(self) -> None:
        actual = {
            record["entry"]: (record["family"], record["evidence"], record["confidence"])
            for record in self.report["functions"]
        }
        self.assertEqual(actual, self.analyzer.EXPECTED_ATTRIBUTION)

    def test_mspi_cluster_register_evidence(self) -> None:
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        control = by_entry[0x004C0F78]
        registers = control["references"]
        # handle-magic control function: MSPI device config/XIP/DMA/CQ registers
        for address in (0x40060000, 0x40060030, 0x40060090, 0x400602B4):
            self.assertIn(f"0x{address:08X}", registers)
        self.assertEqual(self.classify(0x40060030), ("MSPI0", 0x30, "MSPICFG"))
        self.assertEqual(self.classify(0x400602B4), ("MSPI0", 0x2B4, "CQSETCLEAR"))
        # callers are the anchored first-party MSPI consumers
        labels = set(control["caller_labels"].values())
        self.assertTrue(any("drv_mx25u25643g.c" in label for label in labels))
        self.assertTrue(any("drv_mspi_uled_common.c" in label for label in labels))

    def test_power_sequencer_register_evidence(self) -> None:
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        record = by_entry[0x0047FAE8]
        self.assertEqual(record["family"], "ambiqsuite-hal")
        self.assertEqual(record["confidence"], "medium")
        self.assertEqual(len(record["references"]), 23)
        names = {
            self.classify(int(address, 16))[2] for address in record["references"]
        }
        self.assertTrue({"SIMOBUCK2", "LDOREG1", "VREFGEN2", "PWRSW0"} <= names)

    def test_hint_collision_functions_have_no_references(self) -> None:
        for record in self.report["functions"]:
            if record["evidence"] == "no-register-evidence":
                self.assertEqual(record["references"], {})
                self.assertEqual(record["blocks"], [])
                self.assertEqual(record["family"], "investigation-required")

    def test_sram_only_listing_is_complete(self) -> None:
        rows = self.report["sram_only_functions"]
        self.assertEqual(
            tuple(record["entry"] for record in rows),
            self.analyzer.EXPECTED_SRAM_ONLY_ENTRIES,
        )
        for record in rows:
            self.assertEqual(record["evidence"], "sram-globals-only-listing")
            self.assertEqual(record["sram_references"], [])

    def test_checked_in_manifests_match_regeneration(self) -> None:
        self.assertEqual(
            self.analyzer.map_tsv(self.report, self.classify).encode(),
            (MANIFESTS / "g2-peripheral-register-cluster-map.tsv").read_bytes(),
        )
        self.assertEqual(
            self.analyzer.summary_json(self.report).encode(),
            (MANIFESTS / "g2-peripheral-register-cluster-summary.json").read_bytes(),
        )

    def test_documented_mspi_cells_are_revalidated(self) -> None:
        documented = self.report["documented_mspi_leaf"]
        self.assertEqual(documented["entry"], "0x004C23DE")
        self.assertEqual(documented["end_exclusive"], "0x004C240E")
        self.assertTrue(documented["source"].startswith("docs/research/"))

    def test_attribution_pin_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_ATTRIBUTION
        mutated = dict(original)
        family, _evidence, _confidence = mutated[0x004C0F78]
        mutated[0x004C0F78] = ("g2-board-support", _evidence, _confidence)
        analyzer.EXPECTED_ATTRIBUTION = mutated
        try:
            with self.assertRaises(analyzer.ClusterError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_ATTRIBUTION = original


if __name__ == "__main__":
    unittest.main()
