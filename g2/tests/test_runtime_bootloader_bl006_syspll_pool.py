#!/usr/bin/env python3
"""BL-006 cluster: System-PLL literal pool plus range-error/div-zero tails.

Pins the reviewed 60-byte literal pool at 0x00427588 (megahertz
scaling constants, VCO bounds, post-divider and PTS table
pointers, SYSPLL state/magic words, VRCTRL/PLL register
addresses), the reviewed 4-byte range-error cell word at
0x004275E4, the reconstructed 18-byte range-error setter at
0x004275D2 (in place, exact fill), and the reconstructed 2-byte
divide-by-zero return at 0x004275E8 (in place, byte-exact)
against the authenticated stock image.

Loader grades (see the audit for why): every pool/cell slot is
"stale" -- its spelling is named by at least one reviewed
consumer source, and every routed loader lives in a named
replaced span whose shipped replacement carries zero data
relocations (stale by construction) or in an explicitly listed
retained dead span (dead by survey containment) -- except the
range-error cell word at 0x004275E4, whose 0x004275CC loader now
sits in the byte-exact alternate-setter leaf while 0x004275DA
stays in the exact-fill range-error body (graded "mixed" below).
Any loader anywhere else fails the test. A whole-image linear
sweep misses 32-bit `ldr.w` loaders through desync, so every
span is decoded anchored at its own start.

The 14-byte setter prologue at 0x004275C4 was routed by BL-006
(see g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md):
it is now a byte-exact in-place leaf selecting 0x21 into the
shared publish body, and its caller at 0x00427D92 sits in the
byte-exact binary32 remainder leaf admitted in the same turn.
Both bodies stay unreachable (survey-graded), so no live traffic
is claimed; the "stays retained" pin below was re-derived into
`test_a_prologue_now_routed`.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-427588-syspll-pool-source-closure.md`.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000
CLANG = "/usr/bin/clang"

STATE_DIR = "components/bootloader/core_overlay"

POOL_PATH = "components/bootloader/core_overlay/runtime_bl006_syspll_pool_427588.c"
RANGE_PATH = "components/bootloader/core_overlay/runtime_double_range_error_4275d2.c"
DIVZERO_PATH = "components/bootloader/core_overlay/runtime_u64_divzero_4275e8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_double_range_error_4275d2_host.c"

POOL_SYMBOL = "open_cfw_bootloader_bl006_pool_427588"
POOL_SECTION = ".rodata.bl006_pool_427588"
POOL_ADDRESS = 0x00427588
POOL_SIZE = 60
POOL_SHA256 = "a04471dd596a285b55bfdf0d5afa4dd2ee599c1cb73c65bfd80ab6a09799c58b"

WORD_SYMBOL = "open_cfw_bootloader_bl006_word_4275e4"
WORD_SECTION = ".rodata.bl006_word_4275e4"
WORD_ADDRESS = 0x004275E4
WORD_SIZE = 4
WORD_SHA256 = "a4a4e7547897f9edc0c1af4fd1146b046b654682d6afefbe3ee69e6fb1555a62"

RANGE_FUNCTION = "open_cfw_bootloader_double_range_error_4275d2"
RANGE_ADDRESS = 0x004275D2
RANGE_STOCK_SIZE = 18
RANGE_STOCK_SHA256 = "5e134e4cc9fa43b1c5f87e5d050a934169bc3c0987612ce9b198d572298f8e38"
RANGE_BODY_SIZE = 18
RANGE_BODY_SHA256 = "f01e4b7395338750ee33d795cb12293094418adf6965d78e2aaa70e465c62373"

DIVZERO_FUNCTION = "open_cfw_bootloader_u64_divzero_4275e8"
DIVZERO_ADDRESS = 0x004275E8
DIVZERO_SIZE = 2
DIVZERO_SHA256 = "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"

# Replaced-span stock PCs loading pool slots. Each owning span's
# shipped replacement carries zero data relocations (stale by
# construction); the fill and dead hits are dead by containment.
# A whole-image linear sweep misses 32-bit `ldr.w` loaders through
# desync, so the pinned sets below were derived by decoding every
# routed span anchored at its own start.
MINFVCO_FUNCTION = "open_cfw_bootloader_syspll_min_fvco_427040"
POSTDIV_FUNCTION = "open_cfw_bootloader_syspll_postdiv_427160"
INIT_FUNCTION = "open_cfw_bootloader_row6_create_4272ac"
DEINIT_FUNCTION = "open_cfw_bootloader_row6_destroy_427310"
ENABLE_FUNCTION = "open_cfw_bootloader_row6_start_427360"
DISABLE_FUNCTION = "open_cfw_bootloader_row6_stop_4273dc"
CONFIGURE_FUNCTION = "open_cfw_bootloader_row6_configure_42740c"
LOCKWAIT_FUNCTION = "open_cfw_bootloader_row6_lock_wait_427522"
STALE_SPANS = {
    0x0042708A: MINFVCO_FUNCTION,
    0x0042711A: MINFVCO_FUNCTION,
    0x004270C8: MINFVCO_FUNCTION,
    0x00427120: MINFVCO_FUNCTION,
    0x00427172: POSTDIV_FUNCTION,
    0x0042718E: POSTDIV_FUNCTION,
    0x004271C8: POSTDIV_FUNCTION,
    0x004271E6: POSTDIV_FUNCTION,
    0x004271CC: POSTDIV_FUNCTION,
    0x004271FA: POSTDIV_FUNCTION,
    0x00427226: POSTDIV_FUNCTION,
    0x0042724C: POSTDIV_FUNCTION,
    0x004272C2: INIT_FUNCTION,
    0x004272EC: INIT_FUNCTION,
    0x0042731C: DEINIT_FUNCTION,
    0x0042736A: ENABLE_FUNCTION,
    0x004273E6: DISABLE_FUNCTION,
    0x00427418: CONFIGURE_FUNCTION,
    0x00427386: ENABLE_FUNCTION,
    0x004273C4: ENABLE_FUNCTION,
    0x004273F4: DISABLE_FUNCTION,
    0x0042747E: CONFIGURE_FUNCTION,
    0x004274AC: CONFIGURE_FUNCTION,
    0x004274C0: CONFIGURE_FUNCTION,
    0x0042752E: LOCKWAIT_FUNCTION,
    0x0042753A: LOCKWAIT_FUNCTION,
    0x00427544: LOCKWAIT_FUNCTION,
    0x00427580: LOCKWAIT_FUNCTION,
    0x004275DA: "open_cfw_bootloader_double_range_error_4275d2",
}

# Retained dead spans (survey-corroborated category-A tails, plus
# the replaced lock-wait tail fill) whose stock-decode hits are
# dead by containment. The range-error setter A prologue, the
# setter B body (routed earlier as the byte-exact range-error
# leaf), and the binary32 remainder-core tail (routed as a
# byte-exact in-place leaf by BL-006; see
# g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md)
# are no longer listed here; the routed bodies stay unreachable,
# pinned by their verifiers.
DEAD_SPANS: tuple[tuple[int, int, str], ...] = ()


WORDS = {
    0x00427588: {"stale": ("10000000U", ("runtime_syspll_min_fvco_427040.c",), (0x0042708A, 0x0042711A))},
    0x0042758C: {"stale": ("0x00431e70U", ("runtime_syspll_min_fvco_427040.c",), (0x004270C8,))},
    0x00427590: {"stale": ("1000000U", ("runtime_syspll_min_fvco_427040.c", "runtime_syspll_postdiv_427160.c"), (0x00427120, 0x004271CC, 0x004271FA, 0x00427226, 0x0042724C))},
    0x00427594: {"stale": ("60000000U", ("runtime_syspll_postdiv_427160.c",), (0x00427172,))},
    0x00427598: {"stale": ("240000000U", ("runtime_syspll_postdiv_427160.c",), (0x0042718E,))},
    0x0042759C: {"stale": ("0x00433cc8U", ("runtime_syspll_postdiv_427160.c",), (0x004271C8,))},
    0x004275A0: {"stale": ("0x00433cb8U", ("runtime_syspll_postdiv_427160.c",), (0x004271E6,))},
    0x004275A4: {"stale": ("0x20027010U", ("runtime_syspll_initialize_4272ac.c",), (0x004272C2,))},
    0x004275A8: {"stale": ("0x00504c30U", ("runtime_syspll_initialize_4272ac.c",), (0x004272EC,))},
    0x004275AC: {"stale": ("0x01504c30U", ("runtime_syspll_lock_wait_427522.c", "runtime_syspll_deinitialize_427310.c", "runtime_syspll_enable_427360.c", "runtime_syspll_disable_4273dc.c", "runtime_syspll_configure_42740c.c"), (0x0042752E, 0x0042731C, 0x0042736A, 0x004273E6, 0x00427418))},
    0x004275B0: {"stale": ("0x40020060U", ("runtime_syspll_enable_427360.c",), (0x00427386,))},
    0x004275B4: {"stale": ("0x400204d8U", ("runtime_syspll_lock_wait_427522.c", "runtime_syspll_configure_42740c.c", "runtime_syspll_enable_427360.c", "runtime_syspll_disable_4273dc.c"), (0x0042753A, 0x004273C4, 0x004273F4, 0x0042747E))},
    0x004275B8: {"stale": ("0x400204dcU", ("runtime_syspll_configure_42740c.c",), (0x004274AC,))},
    0x004275BC: {"stale": ("0x400204e0U", ("runtime_syspll_lock_wait_427522.c", "runtime_syspll_configure_42740c.c"), (0x00427544, 0x004274C0))},
    0x004275C0: {"stale": ("0x400204e4U", ("runtime_syspll_lock_wait_427522.c",), (0x00427580,))},
    0x004275E4: {"mixed": ("0x20027194U", ("runtime_double_range_error_4275d2.c",), (0x004275CC,), (0x004275DA,))},
}

DATA_FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]

RANGE_FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_syspll", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006SyspllPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(dir=ROOT / "build")
        library = Path(cls.temporary.name) / "range-error-4275d2.dylib"
        subprocess.run(
            [os.environ.get("CC", CLANG), "-std=c11", "-Wall", "-Wextra",
             "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.range_fixture = ctypes.CDLL(str(library)).open_cfw_bootloader_double_range_error_4275d2_fixture
        cls.range_fixture.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_data(self, symbol: str, section: str, address: int, size: int):
        source_bytes = (ROOT / POOL_PATH).read_bytes()
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            return self.module.compile_in_place_data_group(
                root=ROOT,
                clang=CLANG,
                group_config={
                    "symbol": symbol,
                    "section": section,
                    "source": {
                        "path": POOL_PATH,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi", "flags": DATA_FLAGS},
                    "expected": {"size": size, "sha256": "0" * 64, "alignment": 1},
                    "placements": [{
                        "name": symbol.split("bl006_", 1)[1],
                        "runtime_address": address,
                        "source_offset": 0,
                        "size": size,
                        "stock_sha256": "0" * 64,
                    }],
                },
                object_path=Path(directory) / "data.o",
                record=True,
            )

    def compile_leaf(self, path: str, symbol: str, flags) -> bytes:
        source = ROOT / path
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as directory:
            object_path = Path(directory) / "leaf.o"
            completed = subprocess.run(
                [CLANG, "--target=arm-none-eabi", *flags, "-c",
                 str(source), "-o", str(object_path)],
                capture_output=True, text=True,
                env=self.module.hermetic_compiler_environment(),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            elf, sections = self.module.parse_elf32(object_path)
            section = self.module.section_named(sections, f".text.{symbol}")
            start = int(section["offset"])
            return bytes(elf[start:start + int(section["size"])])

    def code_spans(self):
        # (start, end, label). Patch spans cover whole replaced
        # stock bodies (redirect plus NOP fill), so they carry the
        # target function label; overlapping decodes dedupe by PC.
        spans: list[tuple[int, int, str]] = []
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            stock = entry.get("stock", {})
            end = start + int(stock.get("size", entry["expected"]["size"]))
            spans.append((start, end, entry["function"]))
        for entry in self.overlay.get("cave_leaves", []):
            start = int(entry["runtime_address"])
            stock = entry.get("stock", {})
            if "size" in stock:
                spans.append((start, start + int(stock["size"]), entry["function"]))
        for entry in self.overlay.get("patch_sites", []):
            start = int(entry["runtime_address"])
            label = entry.get("target_function") or ("patch:" + entry["name"])
            spans.append((start, start + int(entry["expected_size"]), label))
        for start, end, label in DEAD_SPANS:
            spans.append((start, end, "dead:" + label))
        return spans

    def exact_functions(self) -> set[str]:
        exact = set()
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            size = int(entry["expected"]["size"])
            if hashlib.sha256(self.stock(start, size)).hexdigest() == entry["expected"]["sha256"]:
                exact.add(entry["function"])
        return exact

    def loaders_of(self, slot: int):
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        live: list[int] = []
        stale: list[int] = []
        dead: list[int] = []
        foreign: list[str] = []
        exact = self.exact_functions()
        window = (slot - 0x1000, slot + 0x1000)
        seen: set[int] = set()
        for start, end, name in sorted(self.code_spans()):
            if end <= window[0] or start >= window[1]:
                continue
            code = self.image[start - RUN_BASE:end - RUN_BASE]
            for insn in decoder.disasm(code, start):
                if insn.address in seen:
                    continue
                targets: list[int] = []
                for op in insn.operands:
                    if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                        targets.append(((insn.address + 4) & ~3) + op.mem.disp)
                if slot not in targets:
                    continue
                seen.add(insn.address)
                if name.startswith("dead:"):
                    dead.append(insn.address)
                elif name in exact:
                    live.append(insn.address)
                elif insn.address in STALE_SPANS and STALE_SPANS[insn.address] == name:
                    stale.append(insn.address)
                else:
                    foreign.append(f"{name}@{insn.address:#x}")
        return live, stale, dead, foreign

    def callers_of(self, target: int):
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        found: list[tuple[int, str]] = []
        seen: set[int] = set()
        for start, end, name in sorted(self.code_spans()):
            code = self.image[start - RUN_BASE:end - RUN_BASE]
            for insn in decoder.disasm(code, start):
                if insn.address in seen:
                    continue
                if not insn.mnemonic.startswith("b"):
                    continue
                if insn.mnemonic in ("bic", "bic.w", "bfc", "bfi", "bkpt"):
                    continue
                for op in insn.operands:
                    if op.type == ARM_OP_IMM and op.imm == target:
                        seen.add(insn.address)
                        found.append((insn.address, name))
        return found

    def test_stock_regions_unchanged(self) -> None:
        pins = [
            (POOL_ADDRESS, POOL_SIZE, POOL_SHA256),
            (WORD_ADDRESS, WORD_SIZE, WORD_SHA256),
            (RANGE_ADDRESS, RANGE_STOCK_SIZE, RANGE_STOCK_SHA256),
            (DIVZERO_ADDRESS, DIVZERO_SIZE, DIVZERO_SHA256),
        ]
        for address, size, sha in pins:
            with self.subTest(address=hex(address)):
                self.assertEqual(hashlib.sha256(self.stock(address, size)).hexdigest(), sha)

    def test_compiled_data_matches_stock(self) -> None:
        for symbol, section, address, size, sha in [
            (POOL_SYMBOL, POOL_SECTION, POOL_ADDRESS, POOL_SIZE, POOL_SHA256),
            (WORD_SYMBOL, WORD_SECTION, WORD_ADDRESS, WORD_SIZE, WORD_SHA256),
        ]:
            with self.subTest(symbol=symbol):
                payload, report = self.compile_data(symbol, section, address, size)
                self.assertEqual(payload, self.stock(address, size))
                self.assertEqual(hashlib.sha256(payload).hexdigest(), sha)
                self.assertEqual(report["extraction"]["relocation_count"], 0)

    def test_overlay_registers_data(self) -> None:
        registered = {item["symbol"]: item for item in self.overlay.get("in_place_data", [])}
        for symbol, section, address, size, sha in [
            (POOL_SYMBOL, POOL_SECTION, POOL_ADDRESS, POOL_SIZE, POOL_SHA256),
            (WORD_SYMBOL, WORD_SECTION, WORD_ADDRESS, WORD_SIZE, WORD_SHA256),
        ]:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, registered)
                entry = registered[symbol]
                self.assertEqual(entry["section"], section)
                self.assertEqual(entry["expected"]["size"], size)
                self.assertEqual(entry["expected"]["sha256"], sha)
                self.assertEqual(len(entry["placements"]), 1)
                placement = entry["placements"][0]
                self.assertEqual(placement["runtime_address"], address)
                self.assertEqual(placement["size"], size)
                self.assertEqual(placement["stock_sha256"], sha)
                self.assertEqual(entry["source"]["path"], POOL_PATH)
                self.assertEqual(entry["source"]["license"], "MIT")

    def test_slot_grades_and_spellings(self) -> None:
        for slot, contract in WORDS.items():
            with self.subTest(slot=hex(slot)):
                live, stale, dead, foreign = self.loaders_of(slot)
                self.assertEqual(foreign, [], f"{slot:#x} has a loader outside pinned spans")
                if "mixed" in contract:
                    # One byte-exact shipped loader (the BL-006
                    # alternate setter entry) plus remaining
                    # stale/dead loaders.
                    spelling, sources, live_want, rest_want = contract["mixed"]
                    self.assertEqual(sorted(live), sorted(live_want),
                                     f"{slot:#x} byte-exact loader set changed; re-derive")
                    self.assertEqual(sorted(stale + dead), sorted(rest_want),
                                     f"{slot:#x} stale/dead loader set changed; re-derive")
                else:
                    spelling, sources, want = contract["stale"]
                    self.assertEqual(live, [], f"{slot:#x} gained a byte-exact loader")
                    self.assertEqual(sorted(stale + dead), sorted(want),
                                     f"{slot:#x} loader set changed; re-derive")
                for source in sources:
                    text = (ROOT / STATE_DIR / source).read_text()
                    self.assertIn(spelling, text, f"{spelling} not named by {source}")

    def test_stale_spans_carry_no_data_relocations(self) -> None:
        leaves = {entry["function"]: entry
                  for entry in self.overlay.get("in_place_leaves", [])}
        leaves.update({entry["function"]: entry
                       for entry in self.overlay.get("cave_leaves", [])})
        for pc, function in STALE_SPANS.items():
            with self.subTest(function=function):
                self.assertIn(function, leaves)
                for reloc in leaves[function].get("relocations", []):
                    self.assertEqual(reloc["type"], "R_ARM_THM_CALL",
                                     f"{function} has a data relocation; stale claim at {pc:#x} void")

    def test_range_error_body_and_behavior(self) -> None:
        body = self.compile_leaf(RANGE_PATH, RANGE_FUNCTION, RANGE_FLAGS)
        self.assertEqual(len(body), RANGE_BODY_SIZE)
        self.assertEqual(hashlib.sha256(body).hexdigest(), RANGE_BODY_SHA256)
        self.assertEqual(self.range_fixture(), 0x22)
        registered = {item["function"]: item for item in self.overlay.get("in_place_leaves", [])}
        self.assertIn(RANGE_FUNCTION, registered)
        entry = registered[RANGE_FUNCTION]
        self.assertEqual(int(entry["runtime_address"]), RANGE_ADDRESS)
        self.assertEqual(entry["expected"]["size"], RANGE_BODY_SIZE)
        self.assertEqual(entry["expected"]["sha256"], RANGE_BODY_SHA256)
        self.assertEqual(entry["stock"]["size"], RANGE_STOCK_SIZE)
        self.assertEqual(entry["stock"]["sha256"], RANGE_STOCK_SHA256)
        self.assertEqual(entry["relocations"], [])
        callers = self.callers_of(RANGE_ADDRESS)
        live_callers = [(pc, name) for pc, name in callers if name in self.exact_functions()]
        self.assertEqual(sorted(pc for pc, _ in live_callers), [0x00422748])

    def test_divzero_body_and_caller(self) -> None:
        body = self.compile_leaf(DIVZERO_PATH, DIVZERO_FUNCTION, DATA_FLAGS)
        self.assertEqual(body, b"\x70\x47")
        self.assertEqual(hashlib.sha256(body).hexdigest(), DIVZERO_SHA256)
        registered = {item["function"]: item for item in self.overlay.get("in_place_leaves", [])}
        self.assertIn(DIVZERO_FUNCTION, registered)
        entry = registered[DIVZERO_FUNCTION]
        self.assertEqual(int(entry["runtime_address"]), DIVZERO_ADDRESS)
        self.assertEqual(entry["expected"]["sha256"], DIVZERO_SHA256)
        self.assertEqual(entry["stock"]["sha256"], DIVZERO_SHA256)
        callers = self.callers_of(DIVZERO_ADDRESS)
        live_callers = [(pc, name) for pc, name in callers if name in self.exact_functions()]
        self.assertEqual(sorted(pc for pc, _ in live_callers), [0x004228E0])

    def test_a_prologue_now_routed(self) -> None:
        # Re-derived by BL-006: the setter A prologue is now the
        # byte-exact in-place leaf
        # open_cfw_bootloader_syspll_alt_entry_4275c4 (see
        # g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md).
        # Nothing else may cover the span.
        covered: list[str] = []
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["stock"].get("size", entry["expected"]["size"]))
            if start < 0x004275D2 and end > 0x004275C4:
                covered.append(entry["function"])
        for entry in self.overlay.get("in_place_data", []):
            for placement in entry.get("placements", []):
                start = int(placement["runtime_address"])
                if start < 0x004275D2 and start + int(placement["size"]) > 0x004275C4:
                    covered.append(entry["symbol"])
        for site in self.overlay.get("patch_sites", []):
            start = int(site["runtime_address"])
            if start < 0x004275D2 and start + int(site["expected_size"]) > 0x004275C4:
                covered.append(site["name"])
        self.assertEqual(covered, ["open_cfw_bootloader_syspll_alt_entry_4275c4"])
        entry = {item["function"]: item
                 for item in self.overlay.get("in_place_leaves", [])}[
                     "open_cfw_bootloader_syspll_alt_entry_4275c4"]
        self.assertEqual(int(entry["runtime_address"]), 0x004275C4)
        self.assertEqual(entry["expected"]["size"], 14)
        self.assertEqual(entry["relocations"], [])
        callers = self.callers_of(0x004275C4)
        self.assertEqual(sorted(pc for pc, _ in callers), [0x00427D92])
        # The caller now sits in the byte-exact binary32 remainder
        # leaf admitted in the same turn -- still unreachable, but
        # shipped from source rather than retained dead fill.
        self.assertEqual([name for _, name in callers],
                         ["open_cfw_bootloader_binary32_rem_tail_427d84"])
        self.assertIn("open_cfw_bootloader_binary32_rem_tail_427d84",
                      self.exact_functions())


if __name__ == "__main__":
    unittest.main()
