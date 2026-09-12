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
LEAVES = ROOT / ("components/bootloader/core_overlay/"
                 "runtime_bl009_trim_state_leaves_42d5c2.c")
POOL = ROOT / ("components/bootloader/core_overlay/"
               "runtime_bl009_trim_pool_42d7e0.c")
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

LEAVES_CASES = (
    ("open_cfw_bootloader_state_flag_raise_42d5c2", 0x0042D5C2, 10,
     "25ecf9ae2286c9e2a088491125d73344390d883b7e889f4e480429ed557eaea5",
     0x005A07E6),
    ("open_cfw_bootloader_trim_field_publish_42d5f8", 0x0042D5F8, 38,
     "6d2402dae2b925c74e6376ac9e7d783aacfe6d823f8299d026202df3e30f509d",
     0x005A081C),
    ("open_cfw_bootloader_trim_fields_set_42d61e", 0x0042D61E, 28,
     "8ba3e01b253aa983f4b8ccf3e8c0831be516bf2045fda2cf65a63161ffd88937",
     0x005A0842),
    ("open_cfw_bootloader_trim_block_program_42d63a", 0x0042D63A, 88,
     "f2b1e6d2bdacbeb3917a740b15665d1c67356b5bf257bd1be8329f822d0c2acb",
     0x005A085E),
    ("open_cfw_bootloader_trim_bits_raise_42d692", 0x0042D692, 20,
     "3b333cb5bf6987caae18a3c3e272c286410f2799228a448ebff2604aa4d39035",
     0x005A08B6),
    ("open_cfw_bootloader_trim_bits_clear_42d6a6", 0x0042D6A6, 26,
     "91ded6f9e1cf5752f96528944986774aa26f111293f66fc7fe31ac405e739f43",
     0x005A08CA),
)

POOL_SYMBOL = "open_cfw_bootloader_bl009_trim_pool_42d7e0"
POOL_SECTION = ".rodata." + POOL_SYMBOL
POOL_CELLS = (
    (0x0042D7E0, 0x40020080),
    (0x0042D7E8, 0x40020088),
    (0x0042D7FC, 0x400201B0),
    (0x0042D818, 0x400211A0),
    (0x0042D81C, 0x400211A8),
    (0x0042D820, 0x400211A4),
    (0x0042D824, 0x400211AC),
    (0x0042D828, 0x400211B4),
    (0x0042D82C, 0x400211BC),
)
POOL_SHA = "e5982a522495e4c06836c87281ace081cb498afa3cffd64f1c82b1adbf042b4e"


def _load_portables():
    temporary = tempfile.TemporaryDirectory()
    library = Path(temporary.name) / "trim_leaves.so"
    compiler = shutil.which("cc") or shutil.which("clang")
    subprocess.run(
        [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(LEAVES),
         "-o", str(library)], check=True, capture_output=True, text=True,
    )
    return temporary, ctypes.CDLL(str(library))


class TrimLeafBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary, cls.lib = _load_portables()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_flag_raise(self):
        fn = self.lib.open_cfw_bootloader_state_flag_raise_42d5c2_portable
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        fn.restype = ctypes.c_uint32
        for start in (0, 1, 0xFF):
            flag = ctypes.c_uint8(start)
            self.assertEqual(fn(ctypes.byref(flag)), 0)
            self.assertEqual(flag.value, 1)

    def test_trim_field_publish(self):
        fn = self.lib.open_cfw_bootloader_trim_field_publish_42d5f8_portable
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8),
                       ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        rng = random.Random(0x42D5F8)
        gate = ctypes.c_uint8(0)
        level = ctypes.c_uint32(0xDEADBEEF)
        reg = ctypes.c_uint32(0xA5A5A5A5)
        self.assertEqual(fn(ctypes.byref(gate), ctypes.byref(level),
                            ctypes.byref(reg)), 0)
        self.assertEqual(reg.value, 0xA5A5A5A5)
        for _ in range(300):
            raw = rng.getrandbits(32)
            before = rng.getrandbits(32)
            gate = ctypes.c_uint8(1)
            level = ctypes.c_uint32(raw)
            reg = ctypes.c_uint32(before)
            self.assertEqual(fn(ctypes.byref(gate), ctypes.byref(level),
                                ctypes.byref(reg)), 0)
            field = (raw - 7) & 0xFFFFFFFF if raw >= 8 else 0
            self.assertEqual(reg.value,
                             (before & ~0x3FF) | (field & 0x3FF))
        for raw, want in ((0, 0), (7, 0), (8, 1), (9, 2), (1007, 1000),
                          (0xFFFFFFFF, (0xFFFFFFFF - 7) & 0x3FF)):
            gate = ctypes.c_uint8(7)
            level = ctypes.c_uint32(raw)
            reg = ctypes.c_uint32(0xFFFFFC00)
            fn(ctypes.byref(gate), ctypes.byref(level), ctypes.byref(reg))
            self.assertEqual(reg.value, 0xFFFFFC00 | want)

    def test_trim_fields_set(self):
        fn = self.lib.open_cfw_bootloader_trim_fields_set_42d61e_portable
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 2
        fn.restype = ctypes.c_uint32
        rng = random.Random(0x42D61E)
        for _ in range(300):
            a = rng.getrandbits(32)
            b = rng.getrandbits(32)
            first = ctypes.c_uint32(a)
            second = ctypes.c_uint32(b)
            self.assertEqual(fn(ctypes.byref(first), ctypes.byref(second)), 0)
            self.assertEqual(first.value, (a & ~0x3F) | 1)
            self.assertEqual(second.value, (b & ~(3 << 15)) | (2 << 15))

    def test_trim_block_program(self):
        fn = self.lib.open_cfw_bootloader_trim_block_program_42d63a_portable
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 6
        fn.restype = ctypes.c_uint32
        rng = random.Random(0x42D63A)
        for _ in range(300):
            words = [rng.getrandbits(32) for _ in range(6)]
            cells = [ctypes.c_uint32(w) for w in words]
            refs = [ctypes.byref(c) for c in cells]
            self.assertEqual(fn(*refs), 0)
            head = ((words[0] & ~0x1F00) & 0xFFFF) | (0x3E8 << 16)
            head &= ~3
            self.assertEqual(cells[0].value, head)
            self.assertEqual([c.value for c in cells[1:]],
                             [0, 0x320, 0x1C2, 0x258, 0xFA])

    def test_trim_bits_raise_and_clear_round_trip(self):
        ra = self.lib.open_cfw_bootloader_trim_bits_raise_42d692_portable
        ra.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(ctypes.c_uint8)]
        ra.restype = ctypes.c_uint32
        cl = self.lib.open_cfw_bootloader_trim_bits_clear_42d6a6_portable
        cl.argtypes = [ctypes.POINTER(ctypes.c_uint8),
                       ctypes.POINTER(ctypes.c_uint32)]
        cl.restype = ctypes.c_uint32
        rng = random.Random(0x42D692)
        for _ in range(300):
            head = ctypes.c_uint32(rng.getrandbits(32))
            before = head.value
            flag = ctypes.c_uint8(0)
            self.assertEqual(ra(ctypes.byref(head), ctypes.byref(flag)), 0)
            self.assertEqual(head.value, before | 3)
            self.assertEqual(flag.value, 1)
            self.assertEqual(cl(ctypes.byref(flag), ctypes.byref(head)), 0)
            self.assertEqual(head.value, (before | 3) & ~3)
            self.assertEqual(flag.value, 0)
        head = ctypes.c_uint32(0xFFFFFFFF)
        flag = ctypes.c_uint8(0)
        self.assertEqual(cl(ctypes.byref(flag), ctypes.byref(head)), 0)
        self.assertEqual(head.value, 0xFFFFFFFF)
        flag = ctypes.c_uint8(0x80)
        head = ctypes.c_uint32(0x12345678)
        self.assertEqual(cl(ctypes.byref(flag), ctypes.byref(head)), 0)
        self.assertEqual(head.value, 0x12345678 & ~3)
        self.assertEqual(flag.value, 0)


class TrimLeafExactTests(unittest.TestCase):
    def test_dual_toolchain_bodies_match_stock_and_main(self):
        boot = BOOT.read_bytes()
        main = MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for name, start, size, sha, analogue in LEAVES_CASES:
                stock = boot[start - BOOT_BASE:start - BOOT_BASE + size]
                self.assertEqual(hashlib.sha256(stock).hexdigest(), sha, name)
                twin = main[analogue - MAIN_BASE:analogue - MAIN_BASE + size]
                self.assertEqual(stock, twin, name)
                for profile, compiler in PROFILES.items():
                    output = Path(temporary) / f"{profile}-{name}.o"
                    subprocess.run(
                        [str(compiler), *LEAF_FLAGS, "-c", str(LEAVES),
                         "-o", str(output)],
                        check=True, capture_output=True, text=True,
                    )
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, name, runtime_address=start,
                        relocation_configs=[],
                        strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(bytes(linked), stock,
                                     f"{name}/{profile}")
                    self.assertEqual(report["relocation_count"], 0)

    def test_pool_payload_matches_stock_cells(self):
        boot = BOOT.read_bytes()
        want = b"".join(
            boot[addr - BOOT_BASE:addr - BOOT_BASE + 4] for addr, _ in POOL_CELLS
        )
        self.assertEqual(hashlib.sha256(want).hexdigest(), POOL_SHA)
        for addr, value in POOL_CELLS:
            self.assertEqual(
                int.from_bytes(boot[addr - BOOT_BASE:addr - BOOT_BASE + 4],
                               "little"), value, hex(addr))
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
        for name, start, size, sha, _ in LEAVES_CASES:
            entry = leaves[name]
            self.assertEqual(entry["runtime_address"], start)
            self.assertEqual(entry["expected"]["size"], size)
            self.assertEqual(entry["expected"]["sha256"], sha)
            self.assertEqual(entry["stock"]["size"], size)
            self.assertEqual(entry["stock"]["sha256"], sha)
            self.assertEqual(entry["relocations"], [])
            source = entry["source"]
            path = ROOT / source["path"]
            raw = path.read_bytes()
            self.assertEqual(source["size"], len(raw))
            self.assertEqual(source["sha256"],
                             hashlib.sha256(raw).hexdigest())
            self.assertEqual(source["license"], "MIT")
        data = {entry["symbol"]: entry for entry in config["in_place_data"]}
        entry = data[POOL_SYMBOL]
        self.assertEqual(entry["section"], POOL_SECTION)
        self.assertEqual(entry["expected"]["size"], 36)
        self.assertEqual(entry["expected"]["sha256"], POOL_SHA)
        self.assertEqual(len(entry["placements"]), len(POOL_CELLS))
        offset = 0
        for placement, (addr, _) in zip(entry["placements"], POOL_CELLS):
            self.assertEqual(placement["runtime_address"], addr)
            self.assertEqual(placement["source_offset"], offset)
            self.assertEqual(placement["size"], 4)
            stock = BOOT.read_bytes()[addr - BOOT_BASE:addr - BOOT_BASE + 4]
            self.assertEqual(placement["stock_sha256"],
                             hashlib.sha256(stock).hexdigest())
            offset += 4

    def test_sources_are_reviewable_mit_c_without_raw_encodings(self):
        for path in (LEAVES, POOL):
            body = path.read_text(encoding="utf-8")
            self.assertIn("SPDX-License-Identifier: MIT", body)
            for token in (".byte", ".short", ".word", ".inst"):
                self.assertNotIn(token, body)
        body = LEAVES.read_text(encoding="utf-8")
        for name, _, _, _, _ in LEAVES_CASES:
            self.assertIn(name, body)
            self.assertIn(name + "_portable", body)


if __name__ == "__main__":
    unittest.main()
