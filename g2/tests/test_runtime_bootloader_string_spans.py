from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "components/bootloader/core_overlay/runtime_strcspn.c",
    ROOT / "components/bootloader/core_overlay/runtime_strspn.c",
)
HEADER = ROOT / "components/bootloader/core_overlay/runtime_string_spans.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_string_spans_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderStringSpanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "string-spans.dylib"
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        for name in ("open_cfw_bootloader_strcspn_fixture", "open_cfw_bootloader_strspn_fixture"):
            function = getattr(cls.lib, name)
            function.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            function.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_strcspn_semantics(self) -> None:
        cases = ((b"", b"abc", 0), (b"abcdef", b"", 6), (b"abcdef", b"xdy", 3), (b"abcdef", b"a", 0), (b"aaaa", b"z", 4))
        for string, reject, expected in cases:
            with self.subTest(string=string, reject=reject):
                self.assertEqual(self.lib.open_cfw_bootloader_strcspn_fixture(string, reject), expected)

    def test_strspn_semantics(self) -> None:
        cases = ((b"", b"abc", 0), (b"abcdef", b"", 0), (b"abcdef", b"cba", 3), (b"aaaa", b"a", 4), (b"abcdef", b"xyz", 0))
        for string, accept, expected in cases:
            with self.subTest(string=string, accept=accept):
                self.assertEqual(self.lib.open_cfw_bootloader_strspn_fixture(string, accept), expected)

    def test_authenticated_stock_spans(self) -> None:
        blob = OFFICIAL.read_bytes()
        expected = {
            (0x57F8, 0x581A): "f37ecd01540d7e9eb35cce13ef72d20c729e84932a0cbf296f3ff8d8ac58c5cb",
            (0x581A, 0x583C): "9abdb501517f35c72df7dd947891eb902da69f5598591ba36103bf450bdeb7fa",
        }
        for (start, end), digest in expected.items():
            body = blob[start:end]
            self.assertEqual(len(body), 34)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_freestanding_target_compiles(self) -> None:
        for source in SOURCES:
            output = Path(self.temporary.name) / f"{source.stem}-arm.o"
            subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(output)], check=True, capture_output=True, text=True)
            self.assertGreater(output.stat().st_size, 0)
        text = HEADER.read_text(encoding="utf-8")
        self.assertIn("open_cfw_bootloader_strcspn", text)
        self.assertIn("open_cfw_bootloader_strspn", text)


if __name__ == "__main__":
    unittest.main()
