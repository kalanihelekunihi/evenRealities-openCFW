"""Gate the Ghidra-to-source pipeline: harvest, database, codegen, placement.

These tests do not need Ghidra.  They authenticate the harvested corpus that
is checked in, and exercise the pure logic that turns it into source and then
into image bytes.  The stages that need the vendor payload skip when it is
absent, matching the rest of the G2 suite.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
HARVEST = ROOT / "research/corpus/apollo-main/ghidra/decomp"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

APOLLO_IMAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
APOLLO_IMAGE_BYTES = 3523396


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HarvestCorpusTests(unittest.TestCase):
    """The harvested decompilation must authenticate itself."""

    @classmethod
    def setUpClass(cls) -> None:
        summary_path = HARVEST / "HARVEST.json"
        if not summary_path.is_file():
            raise unittest.SkipTest("no harvested decompilation corpus present")
        cls.summary = json.loads(summary_path.read_text(encoding="utf-8"))

    def test_every_artifact_matches_its_recorded_digest(self) -> None:
        for name, digest in self.summary["artifacts"].items():
            with self.subTest(artifact=name):
                path = HARVEST / name
                self.assertTrue(path.is_file(), f"{name} is missing")
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(actual, digest)

    def test_harvest_targets_the_authenticated_apollo_payload(self) -> None:
        self.assertEqual(
            self.summary["census"]["executable_sha256"], APOLLO_IMAGE_SHA256
        )

    def test_every_function_decompiled(self) -> None:
        counts = self.summary["counts"]
        self.assertEqual(counts["not_decompiled"], 0)
        self.assertEqual(counts["decompiled"], counts["functions"])

    def test_records_and_bodies_agree(self) -> None:
        records = [
            json.loads(line)
            for line in (HARVEST / "functions.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        self.assertEqual(len(records), self.summary["counts"]["functions"])
        self.assertEqual(
            sum(record["body_bytes"] for record in records),
            self.summary["counts"]["function_body_bytes"],
        )
        entries = [int(record["entry"], 16) for record in records]
        self.assertEqual(entries, sorted(entries), "records must be address-ordered")
        self.assertEqual(len(set(entries)), len(entries), "entries must be unique")

    def test_body_ranges_account_for_every_body_byte(self) -> None:
        for line in (HARVEST / "functions.jsonl").read_text(
            encoding="utf-8"
        ).splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            spanned = sum(
                int(high, 16) - int(low, 16) + 1 for low, high in record["ranges"]
            )
            with self.subTest(entry=record["entry"]):
                self.assertEqual(spanned, record["body_bytes"])


class FunctionDatabaseTests(unittest.TestCase):
    """The region map must cover the image exactly once, with no holes."""

    @classmethod
    def setUpClass(cls) -> None:
        if not BLOB.is_file():
            raise unittest.SkipTest("official Apollo payload is not present")
        if not (HARVEST / "functions.jsonl").is_file():
            raise unittest.SkipTest("no harvested decompilation corpus present")
        cls.module = load("build_transparent_function_db")

    def test_region_cover_is_gapless_and_exact(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch)
            summary = self.module.build(HARVEST, output)
            regions = json.loads(
                (output / "region-map.json").read_text(encoding="utf-8")
            )["regions"]

        self.assertEqual(summary["image_bytes"], APOLLO_IMAGE_BYTES)
        self.assertEqual(summary["overlapping_functions_dropped"], 0)
        self.assertEqual(
            summary["code_bytes"] + summary["non_code_bytes"], APOLLO_IMAGE_BYTES
        )

        cursor = regions[0]["start"]
        for region in regions:
            self.assertEqual(region["start"], cursor, "region cover has a hole")
            self.assertGreater(region["size"], 0)
            cursor = region["end"]
        self.assertEqual(cursor - regions[0]["start"], APOLLO_IMAGE_BYTES)

    def test_tiers_are_ordered_weakest_first(self) -> None:
        self.assertEqual(self.module.TIER_ORDER[0], "unrecovered")
        self.assertEqual(self.module.TIER_ORDER[-1], "source")
        self.assertEqual(
            self.module.stronger("decompiled", "attributed"), "attributed"
        )
        self.assertEqual(
            self.module.stronger("attributed", "decompiled"), "attributed"
        )


class GeneratedSourceTests(unittest.TestCase):
    """Declaration inference must follow how a unit actually uses a symbol."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load("generate_transparent_source")

    def test_data_symbols_resolve_to_their_own_address(self) -> None:
        declaration = self.module.declaration_for(
            "DAT_004452c8", "  uVar1 = DAT_004452c8;", {}
        )
        self.assertEqual(declaration, "#define DAT_004452c8 (*(undefined4 *)0x004452C8u)")

    def test_called_data_symbol_becomes_a_function_pointer(self) -> None:
        declaration = self.module.declaration_for(
            "DAT_080000c4", "  (*DAT_080000c4)();", {}
        )
        self.assertEqual(declaration, "#define DAT_080000c4 (*(code **)0x080000C4u)")

    def test_indexed_data_symbol_becomes_an_array(self) -> None:
        declaration = self.module.declaration_for(
            "DAT_00470000", "  x = DAT_00470000[2];", {}
        )
        self.assertEqual(declaration, "#define DAT_00470000 ((undefined4 *)0x00470000u)")

    def test_callee_keeps_its_return_type_but_drops_its_arity(self) -> None:
        declaration = self.module.declaration_for(
            "FUN_0045fba2",
            "  iVar1 = FUN_0045fba2(1, 2, 3);",
            {"FUN_0045fba2": "undefined4 FUN_0045fba2(int param_1);"},
        )
        self.assertEqual(declaration, "undefined4 FUN_0045fba2();")

    def test_void_callee_is_widened_to_a_machine_word(self) -> None:
        # Ghidra analyzes callers independently of callees, so a callee it
        # recorded as returning nothing is still assigned from elsewhere.
        declaration = self.module.declaration_for(
            "FUN_00444444",
            "  iVar1 = FUN_00444444();",
            {"FUN_00444444": "void FUN_00444444(void);"},
        )
        self.assertEqual(declaration, "undefined4 FUN_00444444();")

    def test_unresolved_goto_is_detected(self) -> None:
        self.assertEqual(
            self.module.missing_labels("  goto LAB_00401000;"), {"LAB_00401000"}
        )
        self.assertEqual(
            self.module.missing_labels("LAB_00401000:\n  goto LAB_00401000;"), set()
        )

    def test_unrecovered_function_traps_instead_of_returning(self) -> None:
        record = {
            "entry": 0x00438504,
            "name": "FUN_00438504",
            "ghidra_name": "FUN_00438504",
            "tier": "unrecovered",
            "sources": ["unanchored-census"],
            "size": 256,
            "covered_bytes": 256,
        }
        text, disposition = self.module.render_unit(record, None, {})
        self.assertEqual(disposition, "trap-no-decompilation")
        self.assertIn("OPENG2_UNRECOVERED(0x00438504u)", text)
        self.assertNotIn("return", text)


class ImagePlacementTests(unittest.TestCase):
    """Branch encoding and trap stubs decide whether placed code is sound."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load("build_transparent_image")

    def test_thumb_branch_round_trips(self) -> None:
        for site, target in (
            (0x00438000, 0x00438100),
            (0x00500000, 0x004FF000),
            (0x00438004, 0x00438004),
            (0x00440000, 0x00C3FFFE),
        ):
            with self.subTest(site=site, target=target):
                encoded = self.module.encode_thumb_branch(site, target, link=True)
                addend = self.module.decode_thumb_branch_addend(encoded)
                self.assertEqual(site + 4 + addend, target)

    def test_thumb_bit_belongs_in_pointers_not_branch_offsets(self) -> None:
        # Function symbols carry bit 0 set so a function pointer is callable,
        # but a BL displacement is measured to the even instruction address.
        # Feeding the odd address straight in makes every call to a Thumb
        # function an unaligned displacement, which refuses to encode.
        with self.assertRaises(self.module.ImageError):
            self.module.encode_thumb_branch(0x00438000, 0x00438101, link=True)
        encoded = self.module.encode_thumb_branch(
            0x00438000, 0x00438101 & ~1, link=True
        )
        self.assertEqual(
            0x00438000 + 4 + self.module.decode_thumb_branch_addend(encoded),
            0x00438100,
        )

    def test_branch_out_of_range_is_refused(self) -> None:
        with self.assertRaises(self.module.ImageError):
            self.module.encode_thumb_branch(0x00438000, 0x0F438000, link=True)

    def test_link_bit_distinguishes_bl_from_b(self) -> None:
        call = self.module.encode_thumb_branch(0x00438000, 0x00438100, link=True)
        jump = self.module.encode_thumb_branch(0x00438000, 0x00438100, link=False)
        self.assertNotEqual(call, jump)
        self.assertEqual(call[3] & 0xD0, 0xD0)

    def test_movw_movt_immediates_round_trip(self) -> None:
        # MOVW r0, #0 and MOVT r0, #0 as clang leaves them for the linker.
        for name, instruction, value in (
            ("movw", bytes.fromhex("40f20000"), 0x1234),
            ("movt", bytes.fromhex("c0f20000"), 0xABCD),
            ("movw", bytes.fromhex("40f20000"), 0xFFFF),
            ("movt", bytes.fromhex("c0f20000"), 0x0000),
        ):
            with self.subTest(instruction=name, value=value):
                patched = self.module.encode_thumb_movw_movt(instruction, value)
                self.assertEqual(
                    self.module.decode_thumb_movw_movt_addend(patched), value
                )

    def test_movw_movt_patching_preserves_opcode_and_register(self) -> None:
        instruction = bytes.fromhex("41f2ff71")  # MOVW r1, #0x1fff
        patched = self.module.encode_thumb_movw_movt(instruction, 0x2222)
        self.assertEqual(patched[1] & 0xFB, instruction[1] & 0xFB)
        self.assertEqual(patched[3] & 0x0F, instruction[3] & 0x0F)

    def test_envelope_overflow_is_bucketed_not_enumerated(self) -> None:
        self.assertEqual(self.module.bucket_overflow(1), "<= 2 bytes over")
        self.assertEqual(self.module.bucket_overflow(2), "<= 2 bytes over")
        self.assertEqual(self.module.bucket_overflow(3), "<= 4 bytes over")
        self.assertEqual(self.module.bucket_overflow(1000), "> 256 bytes over")

    def test_trap_stub_never_falls_through(self) -> None:
        for size in (2, 4, 16, 256):
            with self.subTest(size=size):
                stub = self.module.trap_bytes(size)
                self.assertEqual(len(stub), size)
                self.assertEqual(stub[:2], self.module.THUMB_BREAKPOINT)

    def test_unsupported_relocations_are_not_silently_accepted(self) -> None:
        self.assertNotIn(0, self.module.SUPPORTED_RELOCATIONS)
        self.assertNotIn(self.module.R_ARM_PREL31, self.module.SUPPORTED_RELOCATIONS)


class RelocationArenaTests(unittest.TestCase):
    """A function that outgrows its stock envelope gets relocated, not trapped.

    These exercise the same `place_unit` primitive the per-envelope placement
    path uses, with the optional shared literal-pool cache the relocation
    arena passes it.  No full image build is needed: the placement contract
    is pure and address-independent given a symbol table.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load("build_transparent_image")
        cls.clang = shutil.which("clang")

    def test_align_up_rounds_to_the_next_multiple(self) -> None:
        align_up = self.module.align_up
        self.assertEqual(align_up(0, 4), 0)
        self.assertEqual(align_up(1, 4), 4)
        self.assertEqual(align_up(4, 4), 4)
        self.assertEqual(align_up(5, 8), 8)

    def test_redirect_stub_is_exactly_one_thumb_branch(self) -> None:
        # `REDIRECT_STUB_BYTES` sizes every redirect write; it must match what
        # encode_thumb_branch actually produces or padding math goes wrong.
        stub = self.module.encode_thumb_branch(0x00438000, 0x00794400, link=False)
        self.assertEqual(len(stub), self.module.REDIRECT_STUB_BYTES)

    def _compile(self, tmp: Path, name: str, body: str) -> "object":
        if self.clang is None:
            self.skipTest("clang unavailable")
        header = ROOT / "tools/transparent"
        source = tmp / f"{name}.c"
        source.write_text(body, encoding="utf-8")
        obj = tmp / f"{name}.o"
        completed = subprocess.run(
            [
                self.clang, "--target=armv8.1m.main-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-mfloat-abi=soft", "-std=gnu11", "-Oz", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-I", str(header), "-c", str(source), "-o", str(obj),
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return self.module.Elf32(obj.read_bytes(), obj.name)

    def test_shared_pool_deduplicates_identical_rodata_across_units(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            tmp = Path(scratch)
            elf_a = self._compile(
                tmp, "unit_a",
                '#include "openg2_decompiled_runtime.h"\n'
                "const unsigned char pool_a[8] = {1,2,3,4,5,6,7,8};\n"
                "unsigned int fn_a(void) { return pool_a[3]; }\n",
            )
            elf_b = self._compile(
                tmp, "unit_b",
                '#include "openg2_decompiled_runtime.h"\n'
                "const unsigned char pool_b[8] = {1,2,3,4,5,6,7,8};\n"
                "unsigned int fn_b(void) { return pool_b[5]; }\n",
            )

            shared_pool: dict[bytes, int] = {}
            base = 0x00794324
            payload_a, report_a = self.module.place_unit(
                elf_a, base, 1 << 16, {}, shared_pool=shared_pool
            )
            second_base = base + len(payload_a)
            payload_b, report_b = self.module.place_unit(
                elf_b, second_base, 1 << 16, {}, shared_pool=shared_pool
            )

            # The identical 8-byte pool is only ever placed once: unit B's
            # placement omits it, and both units' relocations resolve inside
            # unit A's buffer for that content.
            self.assertEqual(len(shared_pool), 1)
            pool_address = next(iter(shared_pool.values()))
            self.assertGreaterEqual(pool_address, base)
            self.assertLess(pool_address, base + len(payload_a))
            pool_bytes = bytes([1, 2, 3, 4, 5, 6, 7, 8])
            self.assertIn(pool_bytes, bytes(payload_a))
            self.assertNotIn(pool_bytes, bytes(payload_b))
            # Placing the same content through a *fresh* dict (no sharing)
            # costs strictly more bytes than sharing did.
            unshared_b, _ = self.module.place_unit(elf_b, second_base, 1 << 16, {})
            self.assertGreater(len(unshared_b), len(payload_b))

    def test_shared_pool_never_reuses_code_sections(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            tmp = Path(scratch)
            # Two trivially identical leaf functions: same machine code, but
            # code must never alias even when byte-identical, since a future
            # edit to one must not silently move the other.
            elf_a = self._compile(
                tmp, "leaf_a",
                '#include "openg2_decompiled_runtime.h"\n'
                "unsigned int leaf_a(unsigned int x) { return x + 1; }\n",
            )
            elf_b = self._compile(
                tmp, "leaf_b",
                '#include "openg2_decompiled_runtime.h"\n'
                "unsigned int leaf_b(unsigned int x) { return x + 1; }\n",
            )
            shared_pool: dict[bytes, int] = {}
            base = 0x00794324
            payload_a, _ = self.module.place_unit(
                elf_a, base, 1 << 16, {}, shared_pool=shared_pool
            )
            payload_b, _ = self.module.place_unit(
                elf_b, base + len(payload_a), 1 << 16, {}, shared_pool=shared_pool
            )
            self.assertGreater(len(payload_b), 0)
            # .text is never registered in the pool at all.
            self.assertNotIn(bytes(payload_a), shared_pool)


if __name__ == "__main__":
    unittest.main()
