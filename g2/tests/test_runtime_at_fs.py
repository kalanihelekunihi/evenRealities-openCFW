from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/at_fs.c"
FIXTURES = ROOT / "tests/fixtures"


class RuntimeAtFsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library_path = Path(cls.temporary.name) / f"at_fs{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURES / "at_fs_host.h"),
            str(SOURCE), str(FIXTURES / "at_fs_host.c"),
            "-o", str(cls.library_path),
        ], check=True, cwd=ROOT)
        cls.library = ctypes.CDLL(str(cls.library_path))
        for name in ("remove", "list_recursive", "list", "mkdir"):
            function = getattr(cls.library, f"open_cfw_at_fs_{name}")
            function.argtypes = [ctypes.c_char_p]
            function.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.library.open_cfw_test_at_fs_reset()

    def integer(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.library, name).value

    def outputs(self) -> list[str]:
        count = self.integer("open_cfw_test_at_fs_output_count")
        rows = ((ctypes.c_char * 160) * 16).in_dll(
            self.library, "open_cfw_test_at_fs_outputs"
        )
        return [bytes(rows[index]).split(b"\0", 1)[0].decode() for index in range(count)]

    def test_ready_gate_is_fail_closed(self) -> None:
        ctypes.c_uint32.in_dll(self.library, "open_cfw_test_at_fs_ready").value = 0
        self.assertEqual(self.library.open_cfw_at_fs_remove(b"x"), 0)
        self.assertEqual(self.library.open_cfw_at_fs_list_recursive(b"root"), 0)
        self.assertEqual(self.library.open_cfw_at_fs_mkdir(b"x"), 0)
        self.assertEqual(self.outputs(), [])

    def test_remove_reports_success_and_provider_failure(self) -> None:
        self.assertEqual(self.library.open_cfw_at_fs_remove(b"old"), 1)
        self.assertEqual(self.outputs(), ["RM+OK"])
        self.library.open_cfw_test_at_fs_reset()
        ctypes.c_int.in_dll(
            self.library, "open_cfw_test_at_fs_remove_result"
        ).value = -7
        self.assertEqual(self.library.open_cfw_at_fs_remove(b"old"), 0)
        self.assertEqual(self.outputs(), ["RMERR old -7"])

    def test_recursive_listing_skips_dots_and_reports_sizes(self) -> None:
        self.assertEqual(self.library.open_cfw_at_fs_list(b"root"), 1)
        self.assertEqual(self.outputs(), [
            "D root/sub",
            "F root/sub/nested 1023 0",
            "F root/file 2050 2",
            "LS+OK",
        ])
        self.assertEqual(self.integer("open_cfw_test_at_fs_delay_count"), 4)
        self.assertEqual(self.integer("open_cfw_test_at_fs_close_count"), 2)
        self.assertEqual(self.integer("open_cfw_test_at_fs_closedir_count"), 2)

    def test_list_open_failure_is_reported_by_wrapper(self) -> None:
        self.assertEqual(self.library.open_cfw_at_fs_list(b"missing"), 1)
        self.assertEqual(self.outputs(), ["OPENERR missing", "LS+ERR"])
        self.assertEqual(self.integer("open_cfw_test_at_fs_delay_count"), 1)

    def test_mkdir_reports_result_but_returns_handled(self) -> None:
        self.assertEqual(self.library.open_cfw_at_fs_mkdir(b"new"), 1)
        self.assertEqual(self.outputs(), ["MKDIR+OK"])
        self.library.open_cfw_test_at_fs_reset()
        ctypes.c_int.in_dll(
            self.library, "open_cfw_test_at_fs_mkdir_result"
        ).value = -1
        self.assertEqual(self.library.open_cfw_at_fs_mkdir(b"new"), 1)
        self.assertEqual(self.outputs(), ["MKDIRERR new"])

    def test_target_compiles_with_four_global_text_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "at_fs.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(target),
            ], check=True, cwd=ROOT)
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, {
                "open_cfw_at_fs_remove",
                "open_cfw_at_fs_list_recursive",
                "open_cfw_at_fs_list",
                "open_cfw_at_fs_mkdir",
            })


if __name__ == "__main__":
    unittest.main()
