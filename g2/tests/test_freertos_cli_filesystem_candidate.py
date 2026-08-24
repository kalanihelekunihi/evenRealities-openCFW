from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/freertos_cli_filesystem.c"
HOST = ROOT / "tests/fixtures/freertos_cli_filesystem_host.c"


class BlockStats(ctypes.Structure):
    _fields_ = [("free_bytes", ctypes.c_uint32), ("used_bytes", ctypes.c_uint32), ("blocks", ctypes.c_uint32), ("used_blocks", ctypes.c_uint32)]


class FilesystemCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "cli_fs.so"
        subprocess.run(["clang", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror", str(HOST), "-o", str(library)], check=True, cwd=ROOT)
        cls.lib = ctypes.CDLL(str(library))
        for name in ("ls", "cat", "rm", "cd", "mkdir", "touch", "pwd", "mv", "md5", "df"):
            function = getattr(cls.lib, f"open_cfw_cli_fs_{name}")
            function.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p]
            function.restype = ctypes.c_int32
        cls.lib.open_cfw_cli_fs_normalize_path.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls.lib.open_cfw_cli_fs_normalize_path.restype = ctypes.c_int32
        cls.lib.open_cfw_cli_fs_block_stats_accumulate.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(BlockStats)]
        for name in ("cwd", "printed", "last_path", "last_path2"):
            getattr(cls.lib, f"open_cfw_test_cli_fs_{name}").restype = ctypes.c_char_p
        cls.lib.open_cfw_test_cli_fs_last_mode.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_cli_fs_displayed.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        cls.lib.open_cfw_test_cli_fs_displayed.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.lib.open_cfw_test_cli_fs_reset()

    def text(self, name):
        return getattr(self.lib, f"open_cfw_test_cli_fs_{name}")().decode()

    def test_normalize_is_root_bounded_and_resolves_dot_segments(self):
        output = ctypes.create_string_buffer(256)
        self.assertEqual(self.lib.open_cfw_cli_fs_normalize_path(output, b"//work/./a/../sub"), 0)
        self.assertEqual(output.value, b"/work/sub")
        self.assertEqual(self.lib.open_cfw_cli_fs_normalize_path(output, b"../../.."), 0)
        self.assertEqual(output.value, b"/")

    def test_ls_skips_dot_entries_and_cat_streams_bytes(self):
        self.lib.open_cfw_cli_fs_ls(None, 0, b"ls")
        self.assertEqual(self.text("printed"), "a\r\nsub/\r\n")
        self.lib.open_cfw_test_cli_fs_reset()
        self.lib.open_cfw_cli_fs_cat(None, 0, b"cat a")
        output = (ctypes.c_uint8 * 16)()
        count = self.lib.open_cfw_test_cli_fs_displayed(output, len(output))
        self.assertEqual(bytes(output[:count]), b"abc")
        self.assertEqual((self.text("last_path"), self.lib.open_cfw_test_cli_fs_last_mode()), ("/work/a", 1))

    def test_rm_mkdir_touch_and_mount_gate(self):
        self.lib.open_cfw_cli_fs_rm(None, 0, b"rm a")
        self.assertEqual(self.text("last_path"), "/work/a")
        self.lib.open_cfw_cli_fs_mkdir(None, 0, b"mkdir sub")
        self.assertEqual(self.text("last_path"), "/work/sub")
        self.lib.open_cfw_cli_fs_touch(None, 0, b"touch new")
        self.assertEqual((self.text("last_path"), self.lib.open_cfw_test_cli_fs_last_mode()), ("/work/new", 0x102))
        self.lib.open_cfw_test_cli_fs_set_mounted(0)
        self.lib.open_cfw_cli_fs_rm(None, 0, b"rm ignored")
        self.assertEqual(self.text("last_path"), "/work/new")

    def test_cd_commits_only_a_valid_directory_and_pwd_reports_it(self):
        self.lib.open_cfw_cli_fs_cd(None, 0, b"cd ./sub")
        self.assertEqual(self.text("cwd"), "/work/sub")
        self.lib.open_cfw_cli_fs_pwd(None, 0, b"pwd")
        self.assertEqual(self.text("printed"), "/work/sub\r\n")
        self.lib.open_cfw_cli_fs_cd(None, 0, b"cd missing")
        self.assertEqual(self.text("cwd"), "/work/sub")
        self.assertIn("invaild path", self.text("printed"))

    def test_mv_normalizes_and_appends_basename_for_directory_target(self):
        self.lib.open_cfw_cli_fs_mv(None, 0, b"mv a /dest")
        self.assertEqual((self.text("last_path"), self.text("last_path2")), ("/work/a", "/dest/a"))
        self.lib.open_cfw_test_cli_fs_reset()
        self.lib.open_cfw_cli_fs_mv(None, 0, b"mv")
        self.assertIn("missing operand", self.text("printed"))

    def test_md5_and_df_are_streaming_and_overflow_safe(self):
        self.lib.open_cfw_cli_fs_md5(None, 0, b"md5 a")
        self.assertIn("MD5(/work/a) = 616263", self.text("printed"))
        self.lib.open_cfw_test_cli_fs_reset()
        self.lib.open_cfw_cli_fs_df(None, 0, b"df")
        report = self.text("printed")
        self.assertIn("littlefs", report)
        self.assertIn("64", report)
        self.assertIn("20", report)
        self.assertIn("31%", report)

    def test_block_stats_accumulator_separates_used_and_free(self):
        stats = BlockStats()
        self.lib.open_cfw_cli_fs_block_stats_accumulate(0x1000, 32, 0, ctypes.byref(stats))
        self.lib.open_cfw_cli_fs_block_stats_accumulate(0x1020, 48, 1, ctypes.byref(stats))
        self.assertEqual((stats.free_bytes, stats.used_bytes, stats.blocks, stats.used_blocks), (32, 48, 2, 1))

    def test_all_twelve_cortex_m55_selectors_compile_to_one_global_leaf(self):
        selectors = {
            "LS": "open_cfw_cli_fs_ls", "CAT": "open_cfw_cli_fs_cat", "RM": "open_cfw_cli_fs_rm",
            "NORMALIZE": "open_cfw_cli_fs_normalize_path", "CD": "open_cfw_cli_fs_cd", "MKDIR": "open_cfw_cli_fs_mkdir",
            "TOUCH": "open_cfw_cli_fs_touch", "PWD": "open_cfw_cli_fs_pwd", "MV": "open_cfw_cli_fs_mv",
            "MD5": "open_cfw_cli_fs_md5", "DF": "open_cfw_cli_fs_df", "BLOCK_STATS": "open_cfw_cli_fs_block_stats_accumulate",
        }
        flags = ["-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / f"{selector}.o"
                subprocess.run(["clang", *flags, f"-DOPEN_CFW_CLI_FS_{selector}_ONLY=1", "-c", str(SOURCE), "-o", str(obj)], check=True, cwd=ROOT)
                output = subprocess.run(["nm", str(obj)], check=True, capture_output=True, text=True).stdout
                entries = {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {symbol}, selector)


if __name__ == "__main__":
    unittest.main()
