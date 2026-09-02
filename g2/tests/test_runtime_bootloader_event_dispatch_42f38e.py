import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_dispatch_42f38e.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
FUNCTION = "open_cfw_bootloader_event_dispatch_42f38e"
START = 0x0042F38E
BODY_SHA = "21de4d3df3c7a071b8ced878b814af7bdadfd59d5d1986104abb50bede8fb90a"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FLAGS = ("-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
         "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
         "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
         "-Wextra", "-Werror", "-fno-ident", "-mllvm", "-enable-machine-outliner=never")
PROFILES = {"apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
            "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang")}
ZERO = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
VALUE = ctypes.CFUNCTYPE(None, ctypes.c_uint32, ctypes.c_void_p)


class State(ctypes.Structure):
    _fields_ = [("value", ctypes.c_uint8), ("padding", ctypes.c_uint8 * 3),
                ("first_word", ctypes.c_uint32), ("second_word", ctypes.c_uint32)]


class BootloaderEventDispatch42f38eTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "event_dispatch.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run([compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True,
                       capture_output=True, text=True)
        cls.dispatch = ctypes.CDLL(str(library)).open_cfw_bootloader_event_dispatch_42f38e_portable
        cls.dispatch.argtypes = [ctypes.c_uint32, ctypes.POINTER(State), ZERO, VALUE,
                                 ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
        cls.dispatch.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_all_event_routes_and_eight_bit_abi(self):
        calls = []

        @ZERO
        def zero(_context): calls.append(("zero", 0))

        @VALUE
        def value(item, _context): calls.append(("value", item))

        for event in range(256):
            state = State(value=0)
            self.assertEqual(self.dispatch(event, ctypes.byref(state), zero, value,
                                           None, 0x11223344, 0x55667788), 0)
            if event == 2:
                self.assertEqual((state.first_word, state.second_word),
                                 (0x11223344, 0x55667788))
            else:
                self.assertEqual((state.first_word, state.second_word), (0, 0))
        self.assertEqual(calls, [("zero", 0)])
        state = State(value=9)
        self.dispatch(0x101, ctypes.byref(state), zero, value, None, 1, 2)
        self.assertEqual(calls[-1], ("value", 9))

    def test_dual_toolchain_body_and_main_analogue_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        stock = boot[START - BOOT_BASE:START - BOOT_BASE + 76]
        analogue = main[0x0059FD36 - MAIN_BASE:0x0059FD36 - MAIN_BASE + 76]
        self.assertEqual(hashlib.sha256(stock).hexdigest(), BODY_SHA)
        self.assertEqual(stock, analogue)
        relocations = [
            {"offset": 0x2A, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_event_zero_provider_42f2fa",
             "symbol_type": "STT_NOTYPE", "target_address": 0x0042F2FA},
            {"offset": 0x32, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_event_value_provider_42f204",
             "symbol_type": "STT_NOTYPE", "target_address": 0x0042F204},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE), "-o",
                                str(output)], check=True, capture_output=True, text=True)
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=START,
                    relocation_configs=relocations, strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True)
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 2)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        self.assertIn(FUNCTION, body)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
