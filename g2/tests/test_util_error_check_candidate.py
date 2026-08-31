import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/util_error_check.c"
FIXTURES = ROOT / "tests/fixtures"


class ErrorValue(ctypes.Union):
    _fields_ = [
        ("error_code", ctypes.c_uint16),
        ("expression", ctypes.c_char_p),
    ]


class ErrorInfo(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("error_type", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
        ("value", ErrorValue),
        ("file", ctypes.c_char_p),
        ("function", ctypes.c_char_p),
        ("line", ctypes.c_uint32),
    ]


class UtilErrorCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"util_error{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURES / "util_error_check_host.h"),
            str(SOURCE), str(FIXTURES / "util_error_check_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_app_error_fault_handler.argtypes = [
            ctypes.POINTER(ErrorInfo)
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_error_reset()

    def text(self, name: str) -> str:
        return bytes((ctypes.c_char * 768).in_dll(self.loaded, name)).split(
            b"\0", 1
        )[0].decode()

    def set_filter(self, value: int) -> None:
        ctypes.c_uint32.in_dll(
            self.loaded, "open_cfw_test_error_filter"
        ).value = value

    def test_known_api_error_uses_exact_table_message(self) -> None:
        self.set_filter(3)
        info = ErrorInfo(error_type=0, value=ErrorValue(error_code=1),
                         file=b"caller.c", function=b"run", line=27)
        self.loaded.open_cfw_app_error_fault_handler(ctypes.byref(info))
        self.assertEqual(
            self.text("open_cfw_test_sync"),
            "caller.c, run 27, Error code 0x0001: Invalid parameter.",
        )
        self.assertEqual(
            self.text("open_cfw_test_async"),
            "[assert]caller.c, run 27, Error code 0x0001: Invalid parameter.",
        )

    def test_unknown_api_error_is_bounded_and_fail_safe(self) -> None:
        self.set_filter(2)
        info = ErrorInfo(error_type=0, value=ErrorValue(error_code=0x9999),
                         file=b"caller.c", function=b"run", line=9)
        self.loaded.open_cfw_app_error_fault_handler(ctypes.byref(info))
        self.assertIn("0x9999: Application error.", self.text("open_cfw_test_sync"))
        self.assertEqual(
            ctypes.c_uint32.in_dll(
                self.loaded, "open_cfw_test_async_count"
            ).value,
            0,
        )

    def test_boolean_assertion_and_async_filter(self) -> None:
        self.set_filter(4)
        info = ErrorInfo(error_type=1, value=ErrorValue(expression=b"ready"),
                         file=b"state.c", function=b"step", line=41)
        self.loaded.open_cfw_app_error_fault_handler(ctypes.byref(info))
        self.assertEqual(
            ctypes.c_uint32.in_dll(
                self.loaded, "open_cfw_test_sync_count"
            ).value,
            0,
        )
        self.assertIn("(ready) is not established.", self.text("open_cfw_test_async"))
        self.assertEqual(
            ctypes.c_uint32.in_dll(self.loaded, "open_cfw_test_packed").value,
            0x05000000,
        )

    def test_target_object_has_one_global_text_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "util_error.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                "-std=c11", "-O2", "-ffreestanding", "-fno-jump-tables",
                "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-fropi", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                "-o", str(target),
            ], check=True, cwd=ROOT)
            symbols = subprocess.run(
                ["nm", "-g", str(target)], check=True,
                capture_output=True, text=True,
            ).stdout
            self.assertIn(" T open_cfw_app_error_fault_handler", symbols)
            self.assertEqual(symbols.count(" T "), 1)

    def test_source_is_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1c3bc2b8f21bf3a24d1fe9bee568bd46c6902a508b12a4ff66968d570d94cb48",
        )


if __name__ == "__main__":
    unittest.main()
