import ctypes
import hashlib
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAF = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_state_dispatch_42d6c0.c")
POOL = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_dispatch_pool_42d834.c")
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
START = 0x0042D6C0
SIZE = 222
SHA = "39812d745910a1fa17f8df9bcbc3e4633f99d79d8a4722a50d80fa241f37325b"
ANALOGUE = 0x005A08E4
NAME = "open_cfw_bootloader_state_flag_dispatch_42d6c0"

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

POOL_SYMBOL = "open_cfw_bootloader_bl009_dispatch_pool_42d834"
POOL_SECTION = ".rodata." + POOL_SYMBOL
POOL_CELLS = (
    (0x0042D834, 0x4002000C),
    (0x0042D840, 0x3FE00000),
)
POOL_SHA = hashlib.sha256(
    b"\x0c\x00\x02\x40\x00\x00\xe0\x3f").hexdigest()

# Original literal-load sites in the stock dispatcher that consume each
# routed cell (16-bit Thumb `ldr [pc, #imm]`; PC = (site + 4) & ~3).
# The register cell is loaded once into r2 at 0x0042D6C2 and read
# indirectly (`ldr r1, [r2]`) at 0x0042D6E4/0x0042D6F6/0x0042D708/
# 0x0042D728/0x0042D73A; those indirect readers are not literal
# referents and are asserted separately below.
POOL_REFERENTS = {
    0x0042D834: (0x0042D6C2,),
    0x0042D840: (0x0042D750,),
}
POOL_INDIRECT_READERS = (
    0x0042D6E4, 0x0042D6F6, 0x0042D708, 0x0042D728, 0x0042D73A,
)


def _load_portable():
    temporary = tempfile.TemporaryDirectory()
    library = Path(temporary.name) / "dispatch.so"
    compiler = shutil.which("cc") or shutil.which("clang")
    subprocess.run(
        [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(LEAF),
         "-o", str(library)], check=True, capture_output=True, text=True,
    )
    return temporary, ctypes.CDLL(str(library))


def _expect(mode_reg, state, status):
    """Independent expectation transcribed from the stock branch structure."""
    mode = mode_reg & 0xFF
    first = 1 if (mode == 0x21 and state == 2) else 0
    second = 1 if ((mode == 0x21 and state in (2, 3)) or
                   (mode == 0x22 and state == 0)) else 0
    if mode == 0x22 and state == 1:
        third = 1
    elif mode == 0x23 and state == 0:
        masked = status & 0x3FE00000
        low_clear = (status & 0xFFFF) == 0
        mid_hit = (masked == 0x31800000 and
                   ((status >> 16) & 0x1F) >= 0x14 and low_clear)
        high_hit = (((status >> 25) & 0x1F) >= 0x19 and low_clear)
        third = 0 if (mid_hit or high_hit) else 1
    else:
        third = 0
    return first, second, third


class DispatchBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary, cls.lib = _load_portable()
        fn = cls.lib.open_cfw_bootloader_state_flag_dispatch_42d6c0_portable
        fn.argtypes = [ctypes.c_uint32] * 3 + [
            ctypes.POINTER(ctypes.c_uint8)] * 3
        fn.restype = ctypes.c_uint32
        cls.fn = fn

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def _run(self, mode_reg, state, status):
        first = ctypes.c_uint8(0xA5)
        second = ctypes.c_uint8(0xA5)
        third = ctypes.c_uint8(0xA5)
        ret = self.fn(mode_reg, state, status, ctypes.byref(first),
                      ctypes.byref(second), ctypes.byref(third))
        self.assertEqual(ret, 0)
        return first.value, second.value, third.value

    def test_first_flag_gate(self):
        for mode, state, want in (
                (0x21, 2, 1), (0x21, 3, 0), (0x21, 1, 0), (0x22, 2, 0),
                (0x20, 2, 0), (0x121, 2, 1)):
            got = self._run(0x40020000 | mode, state, 0)
            self.assertEqual(got[0], want, hex(mode))
        # Only the low byte selects: high bytes are ignored.
        self.assertEqual(self._run(0xFF002100, 2, 0)[0], 0)
        self.assertEqual(self._run(0xAB002100 & 0xFFFFFFFF, 2, 0)[0], 0)

    def test_second_flag_routes(self):
        for mode, state, want in (
                (0x21, 2, 1), (0x21, 3, 1), (0x21, 4, 0), (0x21, 0, 0),
                (0x22, 0, 1), (0x22, 1, 0), (0x23, 0, 0), (0x00, 0, 0)):
            self.assertEqual(self._run(mode, state, 0)[1], want, hex(mode))

    def test_third_flag_direct_and_guarded_routes(self):
        self.assertEqual(self._run(0x22, 1, 0xFFFFFFFF)[2], 1)
        self.assertEqual(self._run(0x22, 1, 0)[2], 1)
        self.assertEqual(self._run(0x22, 0, 0)[2], 0)
        # Guarded route with a status word that hits neither predicate.
        self.assertEqual(self._run(0x23, 0, 0x00000000)[2], 1)
        self.assertEqual(self._run(0x23, 0, 0x12345678)[2], 1)
        # Mid predicate: masked match, bits 20:16 >= 0x14, low half clear.
        self.assertEqual(self._run(0x23, 0, 0x31940000)[2], 0)
        # Mask mismatch clears the mid hit even with the field set
        # (0x30140000 also keeps bits 29:25 below the high floor).
        self.assertEqual(self._run(0x23, 0, 0x30140000)[2], 1)
        # Mid field one below the floor keeps the flag set.
        self.assertEqual(self._run(0x23, 0, 0x31930000)[2], 1)
        # Nonzero low halfword clears the mid hit.
        self.assertEqual(self._run(0x23, 0, 0x31940001)[2], 1)
        # High predicate: bits 29:25 >= 0x19, low half clear.
        self.assertEqual(self._run(0x23, 0, 0x32000000)[2], 0)
        self.assertEqual(self._run(0x23, 0, 0x30000000)[2], 1)
        # Nonzero low halfword clears the high hit too.
        self.assertEqual(self._run(0x23, 0, 0x32000001)[2], 1)
        # Wrong state or mode never sets the guarded flag.
        self.assertEqual(self._run(0x23, 1, 0x31940000)[2], 0)
        self.assertEqual(self._run(0x24, 0, 0)[2], 0)

    def test_randomized_against_independent_model(self):
        rng = random.Random(0x42D6C0)
        for _ in range(2000):
            mode_reg = rng.getrandbits(32)
            state = rng.getrandbits(32)
            status = rng.getrandbits(32)
            self.assertEqual(self._run(mode_reg, state, status),
                             _expect(mode_reg, state, status),
                             (hex(mode_reg), hex(state), hex(status)))


class DispatchExactTests(unittest.TestCase):
    def test_dual_toolchain_body_matches_stock_and_main(self):
        boot = BOOT.read_bytes()
        main = MAIN.read_bytes()
        stock = boot[START - BOOT_BASE:START - BOOT_BASE + SIZE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(), SHA)
        twin = main[ANALOGUE - MAIN_BASE:ANALOGUE - MAIN_BASE + SIZE]
        self.assertEqual(stock, twin)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}-dispatch.o"
                subprocess.run(
                    [str(compiler), *LEAF_FLAGS, "-c", str(LEAF),
                     "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, NAME, runtime_address=START,
                    relocation_configs=[],
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(bytes(linked), stock, profile)
                self.assertEqual(report["relocation_count"], 0)

    def test_pool_payload_and_referents(self):
        boot = BOOT.read_bytes()
        want = b"".join(
            boot[addr - BOOT_BASE:addr - BOOT_BASE + 4] for addr, _ in POOL_CELLS
        )
        self.assertEqual(hashlib.sha256(want).hexdigest(), POOL_SHA)
        for addr, value in POOL_CELLS:
            raw = boot[addr - BOOT_BASE:addr - BOOT_BASE + 4]
            self.assertEqual(int.from_bytes(raw, "little"), value, hex(addr))
        # Every routed cell is consumed by at least one original Thumb
        # literal load inside the dispatched body.
        body = boot[START - BOOT_BASE:START - BOOT_BASE + SIZE]
        for addr, sites in POOL_REFERENTS.items():
            self.assertTrue(sites, hex(addr))
            for site in sites:
                off = site - START
                half = int.from_bytes(body[off:off + 2], "little")
                self.assertEqual(half & 0xF800, 0x4800, hex(site))
                imm = (half & 0xFF) * 4
                pc = ((site + 4) & ~3) + imm
                self.assertEqual(pc, addr, hex(site))
        # The register cell's remaining readers are indirect word loads
        # through the r2 captured above (`ldr r1, [r2]` = 0x6811).
        for site in POOL_INDIRECT_READERS:
            off = site - START
            half = int.from_bytes(body[off:off + 2], "little")
            self.assertEqual(half, 0x6811, hex(site))
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}-pool.o"
                subprocess.run(
                    [str(compiler), *POOL_FLAGS, "-c", str(POOL),
                     "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                data, sections = apollo_overlay.parse_elf32(output)
                section = [s for s in sections if s.get("name") == POOL_SECTION]
                self.assertEqual(len(section), 1, profile)
                payload = data[section[0]["offset"]:
                               section[0]["offset"] + section[0]["size"]]
                self.assertEqual(bytes(payload), want, profile)

    def test_overlay_registers_matching_pins(self):
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {entry["function"]: entry
                  for entry in config["in_place_leaves"]}
        entry = leaves[NAME]
        self.assertEqual(entry["runtime_address"], START)
        self.assertEqual(entry["expected"]["size"], SIZE)
        self.assertEqual(entry["expected"]["sha256"], SHA)
        self.assertEqual(entry["stock"]["size"], SIZE)
        self.assertEqual(entry["stock"]["sha256"], SHA)
        self.assertEqual(entry["relocations"], [])
        source = entry["source"]
        raw = (ROOT / source["path"]).read_bytes()
        self.assertEqual(source["size"], len(raw))
        self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(source["license"], "MIT")
        data = {entry["symbol"]: entry for entry in config["in_place_data"]}
        pool = data[POOL_SYMBOL]
        self.assertEqual(pool["section"], POOL_SECTION)
        self.assertEqual(pool["expected"]["size"], 8)
        self.assertEqual(pool["expected"]["sha256"], POOL_SHA)
        self.assertEqual(len(pool["placements"]), len(POOL_CELLS))
        offset = 0
        for placement, (addr, _) in zip(pool["placements"], POOL_CELLS):
            self.assertEqual(placement["runtime_address"], addr)
            self.assertEqual(placement["source_offset"], offset)
            self.assertEqual(placement["size"], 4)
            stock = BOOT.read_bytes()[addr - BOOT_BASE:addr - BOOT_BASE + 4]
            self.assertEqual(placement["stock_sha256"],
                             hashlib.sha256(stock).hexdigest())
            offset += 4

    def test_sources_are_reviewable_mit_c_without_raw_encodings(self):
        for path in (LEAF, POOL):
            body = path.read_text(encoding="utf-8")
            self.assertIn("SPDX-License-Identifier: MIT", body)
            for token in (".byte", ".short", ".word", ".inst"):
                self.assertNotIn(token, body)
        body = LEAF.read_text(encoding="utf-8")
        self.assertIn(NAME, body)
        self.assertIn(NAME + "_portable", body)


if __name__ == "__main__":
    unittest.main()
