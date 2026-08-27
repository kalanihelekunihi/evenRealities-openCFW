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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_public_41711c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_public_host.c"

STOCK = (
    (0x711C, 0x714C, "fe8b87ca377d49c0c78ca4d30f04a9ba0fcfafa76757f8044ab4689959e454df"),
    (0x714C, 0x715C, "8ea52cdcde592f400149ede6ffa0612f5bb5a40315e2de4765603da69f99d0b5"),
    (0x715C, 0x7208, "251d9fcb87ce68fc547462058f4c07d85e91b8cc77bfbba679fdc48f1ebd105a"),
    (0x7208, 0x7240, "97815f0b67c4959b3d84618b093d115b73735a64d717c8e03a9c0d6f1d3c4704"),
    (0x7240, 0x726A, "3299fcb5966228ccc504f99d7fc74f3721e2b6a8eb294ec921df8a7a6c54fba3"),
    (0x726A, 0x7290, "b9a5b652f6bc5af40e06cd4a35f232b93cd6c394df429f0529a731ef8da3e79d"),
    (0x7290, 0x72DA, "10971e48ce46d2904569c0e093ed8a824eff74e25dd994d8e51f566e3cd7989b"),
)

CALLERS = (
    (0x7222, 0x711C, "fff77bff"),
    (0x7164, 0x714C, "fff7f2ff"),
    (0x7262, 0x715C, "fff77bff"),
    (0x7248, 0x7208, "fff7deff"),
    (0x5548, 0x726A, "01f08ffe"),
    (0x5572, 0x7290, "01f08dfe"),
)


class BootloaderTlsfPublicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "tlsf_public.dylib" if sys.platform == "darwin" else "tlsf_public.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.cases = {}
        for name in (
            "construct", "create_and_errors", "add_pool",
            "create_with_pool", "malloc", "free",
        ):
            function = getattr(cls.lib, f"open_cfw_test_tlsf_public_{name}")
            function.restype = ctypes.c_uint
            cls.cases[name] = function

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entries_and_direct_callers(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
        for caller, _target, instruction in CALLERS:
            self.assertEqual(image[caller:caller + 4], bytes.fromhex(instruction))

    def test_control_construction_and_pool_overhead(self):
        self.assertEqual(self.cases["construct"](), 1)

    def test_create_and_pool_error_contracts(self):
        self.assertEqual(self.cases["create_and_errors"](), 1)

    def test_pool_creation_links_free_block_and_sentinel(self):
        self.assertEqual(self.cases["add_pool"](), 1)
        self.assertEqual(self.cases["create_with_pool"](), 1)

    def test_malloc_and_free_delegate_complete_block_lifecycle(self):
        self.assertEqual(self.cases["malloc"](), 1)
        self.assertEqual(self.cases["free"](), 1)

    def test_stock_string_assert_contract_and_freestanding_target_compile(self):
        text = SOURCE.read_text()
        for address in (
            "0x004320E0U", "0x0043190CU", "0x00432114U",
            "0x00431E00U", "0x00431A04U", "0x00415735U",
            "0x00415FAFU",
        ):
            self.assertIn(address, text)
        self.assertIn("1188U", text)

        output = Path(self.temporary.name) / "tlsf_public.o"
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
