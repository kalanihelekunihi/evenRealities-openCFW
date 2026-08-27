from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_allocator_416e04.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_allocator_host.c"

STOCK = (
    (0x6E04, 0x6E26, "dbde042aa14dd9444549f1a9ac3909b0bd7d0265382c23c18454059ac7e26467"),
    (0x6E26, 0x6E48, "17d55fa5b63d3f6230df808bd452e2f2b2d9ce7de994bfe49a77ab5023fdf2d7"),
    (0x6E48, 0x6E60, "ed89378cfb216a894fcf4e19f7c2b26c55def623f6336f92c899033b0155dd0a"),
    (0x6E60, 0x6F20, "5808961f4a7ba0ee4cb7408763fe321723bb629b172d6da6cfe462ee0f9df9da"),
    (0x6F20, 0x6F62, "6f3f60e6089e04df3ad7148f81cec89ffa42c76b4a4a2f16c8814080e9c56c13"),
    (0x6F62, 0x6FC6, "32a2dcb7ea0d9bac0abc9b15204c4e03c5367dcae95781aecf37126eebc5a617"),
    (0x6FC6, 0x702A, "22c75168e5eb30ed5ec358e26446057f14ab8151fd553445b38b7565d57f33d1"),
    (0x702A, 0x707C, "83437d777169d547f542d6439a5bf5d3a76e962fdb0c13ecd03c949624766e5c"),
    (0x707C, 0x70DE, "cce455a859d6bfaae97a2a3d2a47a9cd091209bb5bde901c39dcd10593fd042b"),
    (0x70DE, 0x711C, "d1da704179fd80d4bf8d1638e244508c9610ab578a0f640b73708a72360097f1"),
)

CALLERS = (
    0x6FB4, 0x7018, 0x7076, 0x71DC, 0x72D4, 0x7054, 0x7060,
    0x6FBC, 0x7020, 0x72C4, 0x72CC, 0x710A, 0x727C, 0x7286,
)


class BootloaderTlsfAllocatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "tlsf_allocator.dylib" if sys.platform == "darwin" else "tlsf_allocator.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.cases = {}
        for name in (
            "insert_remove", "can_split", "split", "absorb",
            "merge_previous", "merge_next", "trim_locate_prepare",
            "assert_contract",
        ):
            function = getattr(cls.lib, f"open_cfw_test_tlsf_allocator_{name}")
            function.restype = ctypes.c_uint
            cls.cases[name] = function

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entries_callers_and_assertions(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
        for caller in CALLERS:
            self.assertEqual(image[caller:caller + 2], b"\xff\xf7")
        text = SOURCE.read_text()
        for address in (
            "0x00430CC8U", "0x004318CCU", "0x0043138CU",
            "0x00431D90U", "0x004328B8U", "0x004314F8U",
            "0x004328E4U", "0x00431DC8U", "0x004325C8U",
            "0x00433738U", "0x004320E0U", "0x00415735U",
        ):
            self.assertIn(address, text)

    def test_class_insert_remove_and_split_boundary(self):
        self.assertEqual(self.cases["insert_remove"](), 1)
        self.assertEqual(self.cases["can_split"](), 1)

    def test_split_and_absorb_preserve_sizes_flags_and_links(self):
        self.assertEqual(self.cases["split"](), 1)
        self.assertEqual(self.cases["absorb"](), 1)

    def test_bidirectional_coalescing_removes_neighbor_free_nodes(self):
        self.assertEqual(self.cases["merge_previous"](), 1)
        self.assertEqual(self.cases["merge_next"](), 1)

    def test_lookup_trim_and_used_preparation(self):
        self.assertEqual(self.cases["trim_locate_prepare"](), 1)

    def test_stock_assert_contract_and_freestanding_target_compile(self):
        self.assertEqual(self.cases["assert_contract"](), 1)
        output = Path(self.temporary.name) / "allocator.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
