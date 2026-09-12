import ctypes
import hashlib
import json
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAF = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_hwstate_leaves_42bd8c.c")
TAIL = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_zero_tail_42d848.c")
CELL = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_hwstate_cell_42bde4.c")
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


LEAF_FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
POOL_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
)
PROFILES = {
    "apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}

# (symbol, boot entry, size, stock sha, main twin or None,
#  16-bit literal-ldr offsets inside the body)
LEAVES = (
    ("open_cfw_bootloader_hwstate_field_publish_42bd8c",
     0x0042BD8C, 16,
     "be4eee4794c9782d543005a82ac0e4e56dfe436069af6c275ce44403ed968e49",
     0x005A1BBC, (0,)),
    ("open_cfw_bootloader_trim_gate_publish_42bda0",
     0x0042BDA0, 28,
     "5b778e55e31d125b0010a2f28e87be6a4a7c8a424afcce5f2651318f33959762",
     0x005A1BCC, (0, 4, 10)),
    ("open_cfw_bootloader_trim_gate_fields_set_42bdbc",
     0x0042BDBC, 40,
     "052fa599a17346e2f42d30db543e5c1c5ddf7036e6e2fddd254e21ce41963c9d",
     0x005A1BEC, (0, 4, 10, 24)),
)
TAIL_NAME = "open_cfw_bootloader_zero_tail_42d848"
TAIL_ADDR = 0x0042D848
TAIL_SIZE = 4
TAIL_SHA = "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"

CELL_SYMBOL = "open_cfw_bootloader_bl009_hwstate_cell_42bde4"
CELL_SECTION = ".rodata." + CELL_SYMBOL
CELL_ADDR = 0x0042BDE4
CELL_VALUE = 0x4002034C
CELL_SITE = 0x0042BD8C
CELL_SHA = hashlib.sha256(struct.pack("<I", CELL_VALUE)).hexdigest()

# Dispatch-vector slots (0x0041D150, one word per entry) that store the
# Thumb entries of the routed bodies.
VECTOR_BASE = 0x0041D150
VECTOR_SLOTS = {
    8: 0x0042BD8D,
    9: 0x0042BDA1,
    10: 0x0042BDBD,
    14: 0x0042D849,
}

GATE_EXPECT = 0x1F01600D
FIELD_MASK = 0x3E000000
FIELD_VALUE = 6 << 25


def _load_portable():
    temporary = tempfile.TemporaryDirectory()
    library = Path(temporary.name) / "hwstate.so"
    compiler = shutil.which("cc") or shutil.which("clang")
    subprocess.run(
        [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(LEAF),
         str(TAIL), "-o", str(library)],
        check=True, capture_output=True, text=True,
    )
    return temporary, ctypes.CDLL(str(library))


def _ldr_target(body, base, off):
    half = int.from_bytes(body[off:off + 2], "little")
    assert half & 0xF800 == 0x4800, hex(base + off)
    return ((base + off + 4) & ~3) + (half & 0xFF) * 4


def _expect_field(reg):
    return (reg & ~FIELD_MASK) | FIELD_VALUE


def _expect_gate_publish(gate, src, ldo):
    if gate == GATE_EXPECT:
        return (ldo & ~0x3FF) | ((src >> 7) & 0x3FF)
    return ldo & 0xFFFFFFFF


def _expect_gate_fields(gate, src, first, second):
    if gate == GATE_EXPECT:
        first = (first & ~0x3F) | ((src >> 2) & 0x3F)
        second = (second & ~(3 << 15)) | ((src & 3) << 15)
    return first & 0xFFFFFFFF, second & 0xFFFFFFFF


class HwstateBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary, cls.lib = _load_portable()
        fn = cls.lib.open_cfw_bootloader_hwstate_field_publish_42bd8c_portable
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        cls.field = fn
        fn = cls.lib.open_cfw_bootloader_trim_gate_publish_42bda0_portable
        fn.argtypes = [ctypes.c_uint32] * 2 + [
            ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        cls.publish = fn
        fn = cls.lib.open_cfw_bootloader_trim_gate_fields_set_42bdbc_portable
        fn.argtypes = [ctypes.c_uint32] * 2 + [
            ctypes.POINTER(ctypes.c_uint32)] * 2
        fn.restype = ctypes.c_uint32
        cls.fields = fn
        fn = cls.lib.open_cfw_bootloader_zero_tail_42d848_portable
        fn.argtypes = []
        fn.restype = ctypes.c_uint32
        cls.tail = fn

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_field_publish_sets_bits_29_to_25(self):
        for reg, in ((0x00000000,), (0xFFFFFFFF,), (0x4002034C,),
                     (0x3E000000,), (0x12345678,)):
            cell = ctypes.c_uint32(reg)
            self.assertEqual(self.field(ctypes.byref(cell)), 0)
            self.assertEqual(cell.value, _expect_field(reg), hex(reg))

    def test_field_publish_randomized(self):
        rng = random.Random(0x42BD8C)
        for _ in range(500):
            reg = rng.getrandbits(32)
            cell = ctypes.c_uint32(reg)
            self.assertEqual(self.field(ctypes.byref(cell)), 0)
            self.assertEqual(cell.value, _expect_field(reg), hex(reg))

    def test_gate_publish_match_and_mismatch(self):
        ldo = ctypes.c_uint32(0xFFFFFFFF)
        self.assertEqual(
            self.publish(GATE_EXPECT, 0x00001000, ctypes.byref(ldo)), 0)
        self.assertEqual(ldo.value, 0xFFFFFC20)
        ldo = ctypes.c_uint32(0x12345678)
        self.assertEqual(
            self.publish(GATE_EXPECT ^ 1, 0x00001000, ctypes.byref(ldo)), 0)
        self.assertEqual(ldo.value, 0x12345678)

    def test_gate_publish_randomized(self):
        rng = random.Random(0x42BDA0)
        for _ in range(1000):
            gate = rng.getrandbits(32)
            src = rng.getrandbits(32)
            ldo = rng.getrandbits(32)
            cell = ctypes.c_uint32(ldo)
            self.assertEqual(
                self.publish(gate, src, ctypes.byref(cell)), 0)
            self.assertEqual(cell.value, _expect_gate_publish(gate, src, ldo),
                             (hex(gate), hex(src), hex(ldo)))

    def test_gate_fields_match_and_mismatch(self):
        first = ctypes.c_uint32(0xFFFFFFFF)
        second = ctypes.c_uint32(0xFFFFFFFF)
        self.assertEqual(self.fields(GATE_EXPECT, 0x000001E4,
                                     ctypes.byref(first),
                                     ctypes.byref(second)), 0)
        self.assertEqual(first.value, 0xFFFFFFF9)
        self.assertEqual(second.value, 0xFFFE7FFF)
        first = ctypes.c_uint32(0x12345678)
        second = ctypes.c_uint32(0x9ABCDEF0)
        self.assertEqual(self.fields(0, 0xFFFFFFFF, ctypes.byref(first),
                                     ctypes.byref(second)), 0)
        self.assertEqual(first.value, 0x12345678)
        self.assertEqual(second.value, 0x9ABCDEF0)

    def test_gate_fields_randomized(self):
        rng = random.Random(0x42BDBC)
        for _ in range(1000):
            gate = rng.getrandbits(32)
            src = rng.getrandbits(32)
            first = rng.getrandbits(32)
            second = rng.getrandbits(32)
            c_first = ctypes.c_uint32(first)
            c_second = ctypes.c_uint32(second)
            self.assertEqual(self.fields(gate, src, ctypes.byref(c_first),
                                         ctypes.byref(c_second)), 0)
            want_first, want_second = _expect_gate_fields(
                gate, src, first, second)
            self.assertEqual((c_first.value, c_second.value),
                             (want_first, want_second),
                             (hex(gate), hex(src)))

    def test_zero_tail_returns_zero(self):
        self.assertEqual(self.tail(), 0)


class HwstateExactTests(unittest.TestCase):
    def test_dual_toolchain_bodies_match_stock(self):
        boot = BOOT.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                for name, addr, size, sha, _, _ in LEAVES:
                    stock = boot[addr - BOOT_BASE:addr - BOOT_BASE + size]
                    self.assertEqual(hashlib.sha256(stock).hexdigest(), sha)
                    output = Path(temporary) / f"{profile}-{name}.o"
                    subprocess.run(
                        [str(compiler), *LEAF_FLAGS, "-c", str(LEAF),
                         "-o", str(output)],
                        check=True, capture_output=True, text=True,
                    )
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, name, runtime_address=addr,
                        relocation_configs=[],
                        strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(bytes(linked), stock, (profile, name))
                    self.assertEqual(report["relocation_count"], 0)
                stock = boot[TAIL_ADDR - BOOT_BASE:
                             TAIL_ADDR - BOOT_BASE + TAIL_SIZE]
                self.assertEqual(hashlib.sha256(stock).hexdigest(), TAIL_SHA)
                output = Path(temporary) / f"{profile}-tail.o"
                subprocess.run(
                    [str(compiler), *LEAF_FLAGS, "-c", str(TAIL),
                     "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, TAIL_NAME, runtime_address=TAIL_ADDR,
                    relocation_configs=[],
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(bytes(linked), stock, profile)
                self.assertEqual(report["relocation_count"], 0)

    def test_main_twins_share_layout_independent_bytes(self):
        boot = BOOT.read_bytes()
        main = MAIN.read_bytes()
        for _, addr, size, _, twin, ldr_offs in LEAVES:
            stock = boot[addr - BOOT_BASE:addr - BOOT_BASE + size]
            twin_bytes = main[twin - MAIN_BASE:twin - MAIN_BASE + size]
            mask = bytearray(b"\xff" * size)
            for off in ldr_offs:
                mask[off:off + 2] = b"\x00\x00"
                for body, base in ((stock, addr), (twin_bytes, twin)):
                    half = int.from_bytes(body[off:off + 2], "little")
                    self.assertEqual(half & 0xF800, 0x4800,
                                     (hex(base), off))
            self.assertEqual(
                bytes(b & m for b, m in zip(stock, mask)),
                bytes(b & m for b, m in zip(twin_bytes, mask)),
                hex(addr))

    def test_pool_targets_carry_shared_semantics(self):
        boot = BOOT.read_bytes()
        main = MAIN.read_bytes()
        # Boot literal targets and their stocked values.
        boot_targets = {
            (0x0042BD8C, 0): (CELL_ADDR, CELL_VALUE),
            (0x0042BDA0, 0): (0x0042BFCC, 0x20026BA0),
            (0x0042BDA0, 4): (0x0042BFD0, GATE_EXPECT),
            (0x0042BDA0, 10): (0x0042C020, 0x40020080),
            (0x0042BDBC, 0): (0x0042BFCC, 0x20026BA0),
            (0x0042BDBC, 4): (0x0042BFD0, GATE_EXPECT),
            (0x0042BDBC, 10): (0x0042C024, 0x40020088),
            (0x0042BDBC, 24): (0x0042C028, 0x400201B0),
        }
        for (base, off), (addr, value) in boot_targets.items():
            body = boot[base - BOOT_BASE:base - BOOT_BASE + 64]
            target = _ldr_target(body, base, off)
            self.assertEqual(target, addr, hex(base + off))
            raw = boot[target - BOOT_BASE:target - BOOT_BASE + 4]
            self.assertEqual(int.from_bytes(raw, "little"), value, hex(addr))
        # Main twins read the same semantic values; only the SRAM gate
        # pointer differs by layout (asserted as an SRAM address).
        main_targets = {
            (0x005A1BBC, 0): CELL_VALUE,
            (0x005A1BCC, 4): GATE_EXPECT,
            (0x005A1BCC, 10): 0x40020080,
            (0x005A1BEC, 10): 0x40020088,
            (0x005A1BEC, 24): 0x400201B0,
        }
        for (base, off), value in main_targets.items():
            body = main[base - MAIN_BASE:base - MAIN_BASE + 64]
            target = _ldr_target(body, base, off)
            raw = main[target - MAIN_BASE:target - MAIN_BASE + 4]
            self.assertEqual(int.from_bytes(raw, "little"), value,
                             hex(base + off))
        for base, off in ((0x005A1BCC, 0), (0x005A1BEC, 0)):
            body = main[base - MAIN_BASE:base - MAIN_BASE + 64]
            target = _ldr_target(body, base, off)
            raw = main[target - MAIN_BASE:target - MAIN_BASE + 4]
            gate = int.from_bytes(raw, "little")
            self.assertEqual(gate & 0xFF000000, 0x20000000, hex(base + off))

    def test_dispatch_vector_holds_stored_entries(self):
        boot = BOOT.read_bytes()
        for index, entry in VECTOR_SLOTS.items():
            raw = boot[VECTOR_BASE - BOOT_BASE + index * 4:
                       VECTOR_BASE - BOOT_BASE + index * 4 + 4]
            self.assertEqual(int.from_bytes(raw, "little"), entry, index)
        # The main vector (located through the single stored referent of
        # the 0x005A08E4 dispatcher twin) carries twins at the same
        # indices for the three leaves but diverges at index 14, so the
        # zero tail has no main analogue.
        main = MAIN.read_bytes()
        words = struct.unpack("<%dI" % (len(main) // 4), main[:len(main) // 4 * 4])
        hits = [i for i, w in enumerate(words) if w == 0x005A08E5]
        self.assertEqual(len(hits), 1)
        base = hits[0] * 4 - 12 * 4
        for index, entry in ((8, 0x5A1BBD), (9, 0x5A1BCD), (10, 0x5A1BED)):
            raw = main[base + index * 4:base + index * 4 + 4]
            self.assertEqual(int.from_bytes(raw, "little"), entry, index)
        raw = main[base + 14 * 4:base + 14 * 4 + 4]
        self.assertNotEqual(int.from_bytes(raw, "little"), 0x5A07F0 & 0xFFFFFF)

    def test_cell_payload_and_referent(self):
        boot = BOOT.read_bytes()
        raw = boot[CELL_ADDR - BOOT_BASE:CELL_ADDR - BOOT_BASE + 4]
        self.assertEqual(int.from_bytes(raw, "little"), CELL_VALUE)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), CELL_SHA)
        body = boot[CELL_SITE - BOOT_BASE:CELL_SITE - BOOT_BASE + 16]
        self.assertEqual(_ldr_target(body, CELL_SITE, 0), CELL_ADDR)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}-cell.o"
                subprocess.run(
                    [str(compiler), *POOL_FLAGS, "-c", str(CELL),
                     "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                data, sections = apollo_overlay.parse_elf32(output)
                section = [s for s in sections
                           if s.get("name") == CELL_SECTION]
                self.assertEqual(len(section), 1, profile)
                payload = data[section[0]["offset"]:
                               section[0]["offset"] + section[0]["size"]]
                self.assertEqual(bytes(payload), raw, profile)

    def test_overlay_registers_matching_pins(self):
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {entry["function"]: entry
                  for entry in config["in_place_leaves"]}
        for name, addr, size, sha, _, _ in LEAVES:
            entry = leaves[name]
            self.assertEqual(entry["runtime_address"], addr)
            self.assertEqual(entry["expected"]["size"], size)
            self.assertEqual(entry["expected"]["sha256"], sha)
            self.assertEqual(entry["stock"]["sha256"], sha)
            self.assertEqual(entry["relocations"], [])
            source = entry["source"]
            raw = (ROOT / source["path"]).read_bytes()
            self.assertEqual(source["size"], len(raw))
            self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(source["license"], "MIT")
        entry = leaves[TAIL_NAME]
        self.assertEqual(entry["runtime_address"], TAIL_ADDR)
        self.assertEqual(entry["expected"]["size"], TAIL_SIZE)
        self.assertEqual(entry["expected"]["sha256"], TAIL_SHA)
        self.assertEqual(entry["stock"]["sha256"], TAIL_SHA)
        self.assertEqual(entry["relocations"], [])
        data = {entry["symbol"]: entry for entry in config["in_place_data"]}
        cell = data[CELL_SYMBOL]
        self.assertEqual(cell["section"], CELL_SECTION)
        self.assertEqual(cell["expected"]["size"], 4)
        self.assertEqual(cell["expected"]["sha256"], CELL_SHA)
        self.assertEqual(len(cell["placements"]), 1)
        placement = cell["placements"][0]
        self.assertEqual(placement["runtime_address"], CELL_ADDR)
        self.assertEqual(placement["source_offset"], 0)
        self.assertEqual(placement["size"], 4)
        stock = BOOT.read_bytes()[CELL_ADDR - BOOT_BASE:CELL_ADDR - BOOT_BASE + 4]
        self.assertEqual(placement["stock_sha256"],
                         hashlib.sha256(stock).hexdigest())

    def test_sources_are_reviewable_mit_c_without_raw_encodings(self):
        for path in (LEAF, TAIL, CELL):
            body = path.read_text(encoding="utf-8")
            self.assertIn("SPDX-License-Identifier: MIT", body)
            for token in (".byte", ".short", ".word", ".inst"):
                self.assertNotIn(token, body)
        body = LEAF.read_text(encoding="utf-8")
        for name, _, _, _, _, _ in LEAVES:
            self.assertIn(name, body)
            self.assertIn(name + "_portable", body)
        tail_body = TAIL.read_text(encoding="utf-8")
        self.assertIn(TAIL_NAME, tail_body)
        self.assertIn(TAIL_NAME + "_portable", tail_body)


if __name__ == "__main__":
    unittest.main()
