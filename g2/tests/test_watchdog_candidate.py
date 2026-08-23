import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/watchdog.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_watchdog_enable",
    "open_cfw_watchdog_init",
}


class WatchdogCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"watchdog{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "watchdog_host.h"),
                str(SOURCE), str(FIXTURE / "watchdog_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def reset(self, selector: int) -> None:
        self.loaded.open_cfw_test_watchdog_reset(selector)

    def test_enable_uses_selector_zero_and_only_value_one_enables(self) -> None:
        for selector in (0, 2, 255):
            with self.subTest(selector=selector):
                self.reset(selector)
                self.loaded.open_cfw_watchdog_enable()
                self.assertEqual(self.uint("open_cfw_test_watchdog_selector_calls"), 1)
                self.assertEqual(self.uint("open_cfw_test_watchdog_selector_argument"), 0)
                self.assertEqual(self.uint("open_cfw_test_watchdog_provider_calls"), 0)

        self.reset(1)
        self.loaded.open_cfw_watchdog_enable()
        self.assertEqual(self.uint("open_cfw_test_watchdog_selector_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_watchdog_selector_argument"), 0)
        self.assertEqual(self.uint("open_cfw_test_watchdog_provider_calls"), 1)

    def test_init_delegates_once_to_the_complete_enable_policy(self) -> None:
        self.reset(1)
        self.loaded.open_cfw_watchdog_init()
        self.assertEqual(self.uint("open_cfw_test_watchdog_selector_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_watchdog_provider_calls"), 1)

    def test_thumb_compile_has_only_the_two_reviewed_text_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "watchdog.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
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

    def test_source_is_nonempty_and_stably_hashable(self) -> None:
        raw = SOURCE.read_bytes()
        self.assertGreater(len(raw), 900)
        self.assertEqual(len(hashlib.sha256(raw).hexdigest()), 64)


if __name__ == "__main__":
    unittest.main()
