import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_onboarding_config.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_onboarding_config_get",
    "open_cfw_kvdb_onboarding_config_persist",
    "open_cfw_kvdb_onboarding_config_pointer",
    "open_cfw_kvdb_onboarding_config_read",
    "open_cfw_kvdb_onboarding_config_set_indexed",
    "open_cfw_kvdb_onboarding_config_update_and_persist",
}
SOURCE_SHA256 = "42c5d8032ee0c0bb8a723496d4dd5555f49d624f99196de565f17a00664db653"


class KvdbOnboardingConfigCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_onboarding_config{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_onboarding_config_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_onboarding_config_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_onboarding_config_set_indexed.argtypes = [
            ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte),
        ]
        cls.loaded.open_cfw_kvdb_onboarding_config_update_and_persist.argtypes = [
            ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte),
        ]
        cls.loaded.open_cfw_kvdb_onboarding_config_get.restype = ctypes.c_ubyte
        cls.loaded.open_cfw_kvdb_onboarding_config_pointer.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_kvdb_onboarding_config_pointer.restype = ctypes.c_void_p
        cls.loaded.open_cfw_kvdb_onboarding_config_read.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_kvdb_onboarding_config_read.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_onboarding_config_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def record(self) -> ctypes.Array:
        return (ctypes.c_ubyte * 1).in_dll(
            self.loaded, "open_cfw_test_kvdb_onboarding_config_record"
        )

    def test_indexed_setter_preserves_stock_null_and_unknown_index_rules(self) -> None:
        record = self.record()
        record[0] = 7
        self.assertEqual(
            self.loaded.open_cfw_kvdb_onboarding_config_set_indexed(0, None), 0
        )
        self.assertEqual(record[0], 7)
        value = ctypes.c_ubyte(9)
        self.assertEqual(
            self.loaded.open_cfw_kvdb_onboarding_config_set_indexed(
                0, ctypes.byref(value)
            ),
            0,
        )
        self.assertEqual(record[0], 9)
        self.assertEqual(
            self.loaded.open_cfw_kvdb_onboarding_config_set_indexed(
                1, ctypes.byref(value)
            ),
            -1,
        )
        self.assertEqual(record[0], 9)
        self.assertEqual(self.uint("open_cfw_test_kvdb_onboarding_config_unknown_count"), 1)

    def test_update_and_persist_propagates_backend_result(self) -> None:
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_kvdb_onboarding_config_write_result"
        ).value = -4
        value = ctypes.c_ubyte(0xA5)
        self.assertEqual(
            self.loaded.open_cfw_kvdb_onboarding_config_update_and_persist(
                0, ctypes.byref(value)
            ),
            -4,
        )
        self.assertEqual(self.record()[0], 0xA5)
        self.assertEqual(
            ctypes.c_ubyte.in_dll(
                self.loaded, "open_cfw_test_kvdb_onboarding_config_written"
            ).value,
            0xA5,
        )
        self.assertEqual(self.uint("open_cfw_test_kvdb_onboarding_config_write_count"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_kvdb_onboarding_config_write_failure_count"), 1
        )

    def test_invalid_update_does_not_persist(self) -> None:
        value = ctypes.c_ubyte(3)
        self.assertEqual(
            self.loaded.open_cfw_kvdb_onboarding_config_update_and_persist(
                2, ctypes.byref(value)
            ),
            -1,
        )
        self.assertEqual(self.uint("open_cfw_test_kvdb_onboarding_config_write_count"), 0)

    def test_scalar_and_pointer_getters_share_the_record_for_every_index(self) -> None:
        record = self.record()
        record[0] = 0x5C
        self.assertEqual(self.loaded.open_cfw_kvdb_onboarding_config_get(), 0x5C)
        address = ctypes.addressof(record)
        self.assertEqual(self.loaded.open_cfw_kvdb_onboarding_config_pointer(0), address)
        self.assertEqual(self.loaded.open_cfw_kvdb_onboarding_config_pointer(255), address)

    def test_read_overwrites_live_byte_and_only_zero_reports_failure(self) -> None:
        read_value = ctypes.c_ubyte.in_dll(
            self.loaded, "open_cfw_test_kvdb_onboarding_config_read_value"
        )
        result = ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_kvdb_onboarding_config_read_result"
        )
        read_value.value = 0x33
        result.value = 1
        address = self.loaded.open_cfw_kvdb_onboarding_config_read(99)
        self.assertEqual(address, ctypes.addressof(self.record()))
        self.assertEqual(self.record()[0], 0x33)
        self.assertEqual(self.uint("open_cfw_test_kvdb_onboarding_config_read_failure_count"), 0)
        read_value.value = 0x44
        result.value = 0
        self.loaded.open_cfw_kvdb_onboarding_config_read(0)
        self.assertEqual(self.record()[0], 0x44)
        self.assertEqual(self.uint("open_cfw_test_kvdb_onboarding_config_read_failure_count"), 1)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_onboarding_config.o"
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
