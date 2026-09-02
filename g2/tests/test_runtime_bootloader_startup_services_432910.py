import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_services_432910.c"
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
    ("open_cfw_bootloader_vector_table_relocate_432910", 0x00432910, 10,
     "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c",
     0x005E4228, ()),
    ("open_cfw_bootloader_stack_limits_init_43291a", 0x0043291A, 16,
     "320ede47e52c2388957bf2ba938af992c2fb0cfa01e63bf1b6d6fea1f56b5980",
     0x005E4232, ((0x0A, "open_cfw_bootloader_process_stack_provider_43293c", 0x0043293C),)),
    ("open_cfw_bootloader_process_stack_init_43293c", 0x0043293C, 24,
     "83b3b48d97503ec64f1922ffc3774a94e510616f7621abca62508fe9aa65d21a",
     0x005E4254, ((0x10, "open_cfw_bootloader_fpu_provider_432958", 0x00432958),
                  (0x14, "open_cfw_bootloader_runtime_start_43297c", 0x0043297C))),
    ("open_cfw_bootloader_fpu_enable_432958", 0x00432958, 34,
     "0a4d65c423e1840131ae14f4b432a592b8928d1dffeb7624edd12b5e483dd00a",
     0x005E4270, ()),
)


class State(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "vector_table", "main_stack_limit", "process_stack_limit",
        "process_stack", "coprocessor_access", "floating_point_status",
        "process_stack_initialized", "runtime_started",
    )]


class BootloaderStartupServices432910Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "startup_services.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.dll = ctypes.CDLL(str(library))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_portable_startup_state_transitions(self):
        state = State()
        vector = self.dll.open_cfw_bootloader_vector_table_relocate_432910_portable
        vector.argtypes = [ctypes.POINTER(State)]; vector.restype = ctypes.c_uint32
        limits = self.dll.open_cfw_bootloader_stack_limits_init_43291a_portable
        limits.argtypes = [ctypes.POINTER(State), ctypes.c_uint32]
        process = self.dll.open_cfw_bootloader_process_stack_init_43293c_portable
        process.argtypes = [ctypes.POINTER(State), ctypes.c_uint32]
        fpu = self.dll.open_cfw_bootloader_fpu_enable_432958_portable
        fpu.argtypes = [ctypes.POINTER(State)]
        self.assertEqual(vector(ctypes.byref(state)), 1)
        limits(ctypes.byref(state), 0x2007D000)
        process(ctypes.byref(state), 0xFEF5EDA5)
        fpu(ctypes.byref(state))
        self.assertEqual(state.vector_table, 0x00410000)
        self.assertEqual((state.main_stack_limit, state.process_stack_limit),
                         (0x2007D000, 0x2007D000))
        self.assertEqual(state.process_stack, 0xFEF5ED9D)
        self.assertEqual(state.process_stack_initialized, 1)
        self.assertEqual(state.runtime_started, 1)
        self.assertEqual(state.coprocessor_access, 0x00F00000)
        self.assertEqual(state.floating_point_status, 0x02040000)

    def test_dual_toolchain_bodies_and_main_analogues_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                for function, address, size, digest, main_address, edges in FUNCTIONS:
                    relocations = [{"offset": offset, "type": "R_ARM_THM_CALL",
                                    "symbol": symbol, "symbol_type": "STT_NOTYPE",
                                    "target_address": target}
                                   for offset, symbol, target in edges]
                    stock = boot[address - BOOT_BASE:address - BOOT_BASE + size]
                    analogue = main[main_address - MAIN_BASE:main_address - MAIN_BASE + size]
                    self.assertEqual(hashlib.sha256(stock).hexdigest(), digest)
                    self.assertEqual(stock, analogue)
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
        for token in (".byte", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
