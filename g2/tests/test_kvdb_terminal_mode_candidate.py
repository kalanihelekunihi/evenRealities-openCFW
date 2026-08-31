import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_terminal_mode.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_terminal_mode_default_initialize",
    "open_cfw_kvdb_terminal_mode_load_and_migrate",
    "open_cfw_kvdb_write_terminal_mode",
}
SOURCE_SHA256 = "816832d6cb61ad41520b612ea580e9fe5dd9a9fdde829d673dec93f184757f94"


class KvdbTerminalModeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_terminal_mode{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_terminal_mode_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_terminal_mode_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_terminal_mode.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_test_kvdb_terminal_mode_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_terminal_mode_reset()

    def record(self) -> bytes:
        return bytes((ctypes.c_ubyte * 4).in_dll(
            self.loaded, "open_cfw_test_kvdb_terminal_mode_record"
        ))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_read(self, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * 4).from_buffer_copy(value)
        self.loaded.open_cfw_test_kvdb_terminal_mode_set_read(raw, result)

    def test_default_crc(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_terminal_mode_default_initialize(), 0)
        self.assertEqual(self.record(), bytes.fromhex("01003e2e"))

    def test_writer_replaces_record_and_forces_version_crc(self) -> None:
        raw = (ctypes.c_ubyte * 4).from_buffer_copy(bytes.fromhex("097faabb"))
        self.assertEqual(self.loaded.open_cfw_kvdb_write_terminal_mode(raw), 0)
        self.assertEqual(self.record(), bytes.fromhex("017f46a1"))
        written = bytes((ctypes.c_ubyte * 4).in_dll(
            self.loaded, "open_cfw_test_kvdb_terminal_mode_written"
        ))
        self.assertEqual(written, self.record())
        self.assertEqual(self.uint("open_cfw_test_kvdb_terminal_mode_write_count"), 1)

    def test_migration_never_imports_stored_record(self) -> None:
        for stored, read_result, expected_writes in (
            (bytes.fromhex("00ff3412"), 0, 1),
            (bytes.fromhex("00ff3412"), 1, 1),
            (bytes.fromhex("01ff3412"), 1, 0),
        ):
            self.loaded.open_cfw_test_kvdb_terminal_mode_reset()
            self.loaded.open_cfw_kvdb_terminal_mode_default_initialize()
            current = self.record()
            self.set_read(stored, read_result)
            self.loaded.open_cfw_kvdb_terminal_mode_load_and_migrate()
            self.assertEqual(self.record(), current)
            self.assertEqual(
                self.uint("open_cfw_test_kvdb_terminal_mode_write_count"),
                expected_writes,
            )

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_terminal_mode.o"
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
