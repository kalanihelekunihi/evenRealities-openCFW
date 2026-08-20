import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/at_nus.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_at_nus_handler",
}
SOURCE_SHA256 = "b80576c1aea40353475d331686bb5ec2b5915bc1acf911b73e6fee4a12cc87ae"


class AtNusCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"at_nus{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "at_nus_host.h"),
                str(SOURCE), str(FIXTURE / "at_nus_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_at_nus_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def response_address(self) -> int:
        return ctypes.addressof(
            (ctypes.c_char * 9).in_dll(
                self.loaded, "open_cfw_test_at_nus_response"
            )
        )

    def test_response_fixture_is_the_retained_stock_response(self) -> None:
        self.assertEqual(
            ctypes.string_at(self.response_address()), b"NUS+OK\r\n"
        )

    def test_handler_emits_response_once_and_returns_one(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_nus_handler(), 1)
        self.assertEqual(self.uint("open_cfw_test_at_nus_output_count"), 1)
        written = ctypes.c_void_p.in_dll(
            self.loaded, "open_cfw_test_at_nus_written"
        )
        self.assertEqual(written.value, self.response_address())
        self.assertEqual(ctypes.string_at(written.value), b"NUS+OK\r\n")

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "at_nus.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
                    "-Werror", "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, EXPECTED_SYMBOLS)

    def test_source_hash(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
