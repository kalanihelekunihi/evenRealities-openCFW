import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_runtime_43297c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = {
    "apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}
FUNCTIONS = (
    ("open_cfw_bootloader_runtime_start_43297c", 0x0043297C, 30,
     "0f697df14e7a3026cd502d19b3c2bbdd540389796647c301283e815b47a6be2d",
     0x005E4294, 27,
     ((0x00, "open_cfw_bootloader_vector_table_provider_432910", 0x00432910),
      (0x08, "open_cfw_bootloader_init_array_provider_43299c", 0x0043299C),
      (0x16, "open_cfw_bootloader_platform_init_provider_41b862", 0x0041B862),
      (0x1A, "open_cfw_bootloader_terminal_loop_provider_4329c4", 0x004329C4))),
    ("open_cfw_bootloader_init_array_run_43299c", 0x0043299C, 32,
     "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd",
     0x005E42B4, 32, ()),
    ("open_cfw_bootloader_terminal_loop_4329c4", 0x004329C4, 14,
     "bea26157ebbe31038bcf52f8a3233885515b034fd35636d6349e9b21370f26a2",
     0x005E42DC, 11,
     ((0x08, "open_cfw_bootloader_terminal_service_provider_41b298", 0x0041B298),)),
)


class State(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "vector_table_ready", "init_calls", "platform_init_calls",
        "terminal_status",
    )]


CALLBACK = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
TERMINAL = ctypes.CFUNCTYPE(None, ctypes.c_uint32, ctypes.c_void_p)


class BootloaderStartupRuntime43297cTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "startup_runtime.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.dll = ctypes.CDLL(str(library))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_portable_dispatch_init_array_and_terminal_semantics(self):
        calls = []

        @CALLBACK
        def first(_context):
            calls.append(1); return 11

        @CALLBACK
        def second(_context):
            calls.append(2); return 22

        @TERMINAL
        def terminal(status, _context):
            calls.append(100 + status)

        state = State(vector_table_ready=1)
        runtime = self.dll.open_cfw_bootloader_runtime_start_43297c_portable
        runtime.argtypes = [ctypes.POINTER(State), CALLBACK, ctypes.c_void_p]
        runtime(ctypes.byref(state), first, None)
        self.assertEqual((state.init_calls, state.platform_init_calls,
                          state.terminal_status), (1, 1, 0))

        init_array = self.dll.open_cfw_bootloader_init_array_run_43299c_portable
        init_array.argtypes = [ctypes.POINTER(CALLBACK), ctypes.POINTER(CALLBACK),
                               ctypes.c_void_p]
        init_array.restype = ctypes.c_uint32
        array = (CALLBACK * 2)(first, second)
        end = ctypes.cast(ctypes.byref(array, ctypes.sizeof(array)),
                          ctypes.POINTER(CALLBACK))
        self.assertEqual(init_array(array, end, None), 2)

        loop = self.dll.open_cfw_bootloader_terminal_loop_4329c4_portable
        loop.argtypes = [ctypes.POINTER(State), ctypes.c_uint32, TERMINAL,
                         ctypes.c_void_p, ctypes.c_uint32]
        loop(ctypes.byref(state), 7, terminal, None, 3)
        self.assertEqual(state.terminal_status, 7)
        self.assertEqual(calls, [1, 1, 2, 107, 107, 107])

        state.vector_table_ready = 0
        runtime(ctypes.byref(state), first, None)
        self.assertEqual(state.init_calls, 1)
        self.assertEqual(state.platform_init_calls, 2)

    def test_dual_toolchain_bodies_and_main_analogues(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                for function, address, size, digest, main_address, identical, edges in FUNCTIONS:
                    relocations = [{"offset": offset, "type": "R_ARM_THM_CALL",
                                    "symbol": symbol, "symbol_type": "STT_NOTYPE",
                                    "target_address": target}
                                   for offset, symbol, target in edges]
                    stock = boot[address - BOOT_BASE:address - BOOT_BASE + size]
                    analogue = main[main_address - MAIN_BASE:
                                    main_address - MAIN_BASE + size]
                    self.assertEqual(hashlib.sha256(stock).hexdigest(), digest)
                    self.assertEqual(sum(a == b for a, b in zip(stock, analogue)),
                                     identical)
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, function, runtime_address=address,
                        relocation_configs=relocations,
                        strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(linked, stock, (profile, function))
                    self.assertEqual(report["relocation_count"], len(edges))

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        for function, *_rest in FUNCTIONS:
            self.assertIn(function, body)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
