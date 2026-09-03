# SPDX-License-Identifier: MIT
"""Focused v3 canonical-admission checks for the FreeType CFF stage."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
import zlib
from hashlib import sha256
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


ADMISSION = load(
    G2 / "tools/apply_g2_canonical_observations.py",
    "open_cfw_canonical_cff_test",
)


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


class CanonicalCFFAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        run_base = 0x1000
        preamble = 8
        pt_component = bytearray(b"\xa5" * 256)
        patch_runtime = 0x1050
        patch_offset = preamble + patch_runtime - run_base
        pt_component[patch_offset:patch_offset + 4] = (
            ADMISSION.CFF_STOCK_CLASS_BYTES
        )
        section_specs = (
            (".cff_stock_rodata", 0x1020, b"RODA", 4),
            (".cff_stock_text", 0x1030, b"TEXT", 8),
            (".cff_tail_text", 0x1110, b"TAILTEXT", 8),
            (".cff_tail_exidx", 0x1118, b"EXID", 4),
        )
        final_end = 0x111C
        final_size = preamble + final_end - run_base
        output = bytearray(pt_component)
        output.extend(b"\xff" * (final_size - len(output)))
        sections = []
        artifacts = {}
        artifact_records = {}
        for name, start, body, alignment in section_specs:
            offset = preamble + start - run_base
            output[offset:offset + len(body)] = body
            sections.append({
                "name": name,
                "start": start,
                "end_exclusive": start + len(body),
                "size": len(body),
                "alignment": alignment,
                "sha256": digest(body),
            })
            artifacts[name] = body
            artifact_records[name] = {
                "artifact": f"{name.removeprefix('.')}.bin",
                "size": len(body),
                "sha256": digest(body),
            }
        output[patch_offset:patch_offset + 4] = (
            ADMISSION.CFF_REPLACEMENT_CLASS_BYTES
        )
        output[0:4] = (0x04000000 | len(output)).to_bytes(4, "little")
        output[4:8] = b"\x00" * 4
        nested_crc = zlib.crc32(output[8:]) & 0xFFFFFFFF
        output[4:8] = nested_crc.to_bytes(4, "little")
        final_component = bytes(output)
        manifest_body = b"scatter-manifest"
        elf_body = b"final-elf"
        cff = {
            "license": ADMISSION.CFF_LICENSE,
            "component": {
                "size": len(final_component),
                "sha256": digest(final_component),
                "runtime_start": run_base,
                "runtime_end_exclusive": final_end,
                "growth_bytes": len(final_component) - len(pt_component),
                "nested_crc32": f"0x{nested_crc:08X}",
            },
            "placement": {
                "base_runtime_end_exclusive": "0x000010F8",
                "runtime_end_exclusive": f"0x{final_end:08X}",
                "erased_gap_start": "0x000010F8",
                "erased_gap_end_exclusive": "0x00001110",
                "erased_gap_size": 0x18,
                "erased_gap_byte": 0xFF,
                "nested_crc32": nested_crc,
                "sections": sections,
                "unused_scattered_table_pool_bytes": 360,
                "unused_scattered_table_pool_consumed": 0,
            },
            "module_class_patch": {
                "runtime_address": f"0x{patch_runtime:08X}",
                "expected_hex": ADMISSION.CFF_STOCK_CLASS_BYTES.hex(),
                "replacement_hex": ADMISSION.CFF_REPLACEMENT_CLASS_BYTES.hex(),
                "compare_before_write": True,
                "applied_after_all_preflight_checks": True,
            },
            "scatter_manifest": {
                "size": len(manifest_body),
                "sha256": digest(manifest_body),
                "profile_final_elf": {
                    "bytes": len(elf_body),
                    "sha256": digest(elf_body),
                },
                "undefined_symbols": [],
                "relocations": {
                    "total": 0,
                    "internal": 0,
                    "external": 0,
                    "by_type": {},
                    "external_by_symbol": {},
                    "records_sha256": digest(b"[]"),
                },
            },
            "receipt_sha256": digest(b"receipt"),
            "hardware": copy.deepcopy(ADMISSION.DEFERRED_HARDWARE_POLICY),
            "section_artifacts": artifact_records,
        }
        self.observation = {
            "image_mapping": {
                "base_size": len(pt_component),
                "run_base": run_base,
                "preamble_bytes": preamble,
            },
            "final": {
                "overlay_size": 1,
                "overlay_sha256": digest(b"x"),
                "component_size": len(final_component),
                "component_sha256": digest(final_component),
            },
            "freetype_cff": cff,
        }
        self.pt_component = bytes(pt_component)
        self.final_component = final_component
        self.artifacts = artifacts

    def test_v3_schema_and_exact_mutation_replay_are_accepted(self) -> None:
        ADMISSION._validate_freetype_cff_schema(
            self.observation["freetype_cff"]
        )
        ADMISSION._validate_freetype_cff_contract(
            self.observation,
            self.pt_component,
            self.final_component,
            self.artifacts,
        )

    def test_v3_replay_rejects_each_unaccounted_byte_class(self) -> None:
        mutations = []
        changed = bytearray(self.pt_component)
        changed[0x58] ^= 1
        mutations.append((bytes(changed), self.final_component, self.artifacts))
        changed = bytearray(self.final_component)
        changed[0x108] = 0
        mutations.append((self.pt_component, bytes(changed), self.artifacts))
        changed_artifacts = dict(self.artifacts)
        changed_artifacts[".cff_stock_text"] = b"FAIL"
        mutations.append((self.pt_component, self.final_component, changed_artifacts))
        for index, (pt_component, final_component, artifacts) in enumerate(
            mutations
        ):
            with self.subTest(index=index):
                with self.assertRaises(ADMISSION.AdmissionError):
                    ADMISSION._validate_freetype_cff_contract(
                        self.observation,
                        pt_component,
                        final_component,
                        artifacts,
                    )

    def test_v3_schema_rejects_open_relocations_and_hardware_claims(self) -> None:
        for mutate in (
            lambda value: value["scatter_manifest"]["relocations"].update(
                {"total": 1}
            ),
            lambda value: value["hardware"].update(
                {"qualification_complete": True}
            ),
            lambda value: value["placement"].update(
                {"unused_scattered_table_pool_consumed": 1}
            ),
        ):
            changed = copy.deepcopy(self.observation["freetype_cff"])
            mutate(changed)
            with self.assertRaises(ADMISSION.AdmissionError):
                ADMISSION._validate_freetype_cff_schema(changed)

    def test_linux_profile_rows_rebuild_stock_and_pointer_intervals(self) -> None:
        config = {
            "run_base": 0x1000,
            "preamble_bytes": 8,
            "base": {"size": 256},
            "post_link_providers": {
                "freetype_cff": {
                    "placement": {
                        "stock_start": 0x1020,
                        "stock_end_exclusive": 0x1040,
                        "tail_start": 0x1100,
                        "tail_end_exclusive": 0x111C,
                        "module_class_pointer": 0x1050,
                    }
                }
            },
        }
        regions = [
            {"file_offset": 0x28, "size": 4},
            {"file_offset": 0x2C, "size": 12},
            {"file_offset": 0x38, "size": 4},
            {"file_offset": 0x3C, "size": 20},
            {"file_offset": 0x58, "size": 4},
        ]
        replacements = ADMISSION._linux_cff_profile_replacements(
            regions,
            config,
            self.observation,
            self.pt_component,
            self.final_component,
        )
        self.assertEqual(len(replacements), 2)
        stock, pointer = replacements
        self.assertEqual((stock["start"], stock["end_exclusive"]), (0x28, 0x50))
        self.assertEqual(
            sum(row["size"] for row in stock["regions"]), 0x28
        )
        self.assertEqual(
            [
                row["size"] for row in stock["regions"]
                if row["address_status"] == "source_compiled"
            ],
            [4, 4],
        )
        self.assertEqual(
            (pointer["start"], pointer["end_exclusive"]), (0x58, 0x5C)
        )
        changed = bytearray(self.final_component)
        changed[0x40] ^= 1
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION._linux_cff_profile_replacements(
                regions,
                config,
                self.observation,
                self.pt_component,
                bytes(changed),
            )

    def test_v3_independence_covers_pt_and_all_four_sections(self) -> None:
        keys = {
            "overlay", "component", "core_stage_overlay",
            "core_stage_component", "liblc3_payload", "liblc3_component",
            "pt_component", *ADMISSION.CFF_SECTION_NAMES,
        }

        def receipt(seed: int):
            return {
                "observation": {
                    "schema_version": 3,
                    "freetype_cff": {
                        "section_artifacts": {
                            key: {} for key in ADMISSION.CFF_SECTION_NAMES
                        },
                    },
                },
                "report_identity": (1, seed, 0),
                "artifact_identities": {
                    key: (1, seed + index + 1, 0)
                    for index, key in enumerate(sorted(keys))
                },
            }

        first = receipt(10)
        second = receipt(100)
        ADMISSION.validate_observation_independence((first, second))
        incomplete = copy.deepcopy(second)
        incomplete["artifact_identities"].pop("pt_component")
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.validate_observation_independence((first, incomplete))
        reused = copy.deepcopy(second)
        reused["artifact_identities"]["pt_component"] = first[
            "artifact_identities"
        ][".cff_tail_text"]
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.validate_observation_independence((first, reused))


if __name__ == "__main__":
    unittest.main()
