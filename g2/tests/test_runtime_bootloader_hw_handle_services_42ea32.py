import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_services_42ea32.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FLAGS = ("-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
         "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
         "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
         "-Werror", "-fno-ident", "-mllvm", "-enable-machine-outliner=never")
PROFILES = {"apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
            "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang")}
FUNCTIONS = (
    ("open_cfw_bootloader_hw_handle_reset_42ea32", 0x0042EA32, 54,
     "33eeb24b6b211f5d9920815c5ccc30b5c985bb5f094890a5e543b85e194c19b4", 0x0055DAAE),
    ("open_cfw_bootloader_hw_handle_configure_42eb74", 0x0042EB74, 54,
     "d227983f298102fc851a91454e4e48ffcaf57a43f050190e690a7cd6629f7fbb", 0x0055DBF0),
    ("open_cfw_bootloader_hw_handle_enable_42ebaa", 0x0042EBAA, 56,
     "052085424ed967f77d8f36303a119e299f4428fde2a6482b8a08f4686de151cd", 0x0055DC26),
    ("open_cfw_bootloader_hw_handle_disable_42ebe2", 0x0042EBE2, 42,
     "ebd287ea1a933ce89fb082d850d121c22baa5a0a765804e468539386133187d0", 0x0055DC5E),
)


class Handle(ctypes.Structure):
    _fields_ = [("word0", ctypes.c_uint32), ("word1", ctypes.c_uint32)]


class Config(ctypes.Structure):
    _fields_ = [("byte0", ctypes.c_uint8), ("byte1", ctypes.c_uint8),
                ("padding", ctypes.c_uint8 * 2), ("word4", ctypes.c_uint32)]


class Registers(ctypes.Structure):
    _fields_ = [("status", ctypes.c_uint32), ("command", ctypes.c_uint32),
                ("configuration", ctypes.c_uint32)]


class BootloaderHardwareHandleServices42ea32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "hw_handle.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run([compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True, text=True)
        dll = ctypes.CDLL(str(library))
        cls.reset = dll.open_cfw_bootloader_hw_handle_reset_42ea32_portable
        cls.configure = dll.open_cfw_bootloader_hw_handle_configure_42eb74_portable
        cls.enable = dll.open_cfw_bootloader_hw_handle_enable_42ebaa_portable
        cls.disable = dll.open_cfw_bootloader_hw_handle_disable_42ebe2_portable
        cls.reset.argtypes = [ctypes.POINTER(Handle)]; cls.reset.restype = ctypes.c_uint32
        cls.configure.argtypes = [ctypes.POINTER(Handle), ctypes.POINTER(Config),
                                  ctypes.POINTER(Registers)]
        cls.configure.restype = ctypes.c_uint32
        cls.enable.argtypes = cls.disable.argtypes = [ctypes.POINTER(Handle),
                                                       ctypes.POINTER(Registers)]
        cls.enable.restype = cls.disable.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls): cls.temporary.cleanup()

    def test_portable_handle_and_register_semantics(self):
        invalid = Handle(0, 9); regs = Registers()
        self.assertEqual(self.reset(ctypes.byref(invalid)), 2)
        self.assertEqual(self.enable(ctypes.byref(invalid), ctypes.byref(regs)), 2)
        handle = Handle(0x01AFAFAF, 0xFFFFFFFF)
        config = Config(byte1=0xFF, word4=0xFFFFFFFF)
        self.assertEqual(self.configure(ctypes.byref(handle), ctypes.byref(config),
                                        ctypes.byref(regs)), 0)
        self.assertEqual(regs.configuration, 0x000703FF)
        self.assertEqual(self.enable(ctypes.byref(handle), ctypes.byref(regs)), 7)
        regs.status = 1
        self.assertEqual(self.enable(ctypes.byref(handle), ctypes.byref(regs)), 0)
        self.assertEqual(regs.command, 0x80000000)
        self.assertEqual(self.disable(ctypes.byref(handle), ctypes.byref(regs)), 0)
        self.assertEqual(regs.command, 0)
        handle.word0 |= 0x01000000
        self.assertEqual(self.reset(ctypes.byref(handle)), 0)
        self.assertEqual((handle.word0, handle.word1), (0, 0))

    def test_dual_toolchain_and_main_bodies_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE), "-o",
                                str(output)], check=True, capture_output=True, text=True)
                for function, start, size, digest, main_start in FUNCTIONS:
                    stock = boot[start - BOOT_BASE:start - BOOT_BASE + size]
                    analogue = main[main_start - MAIN_BASE:main_start - MAIN_BASE + size]
                    self.assertEqual(hashlib.sha256(stock).hexdigest(), digest)
                    self.assertEqual(stock, analogue)
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, function, runtime_address=start, relocation_configs=[],
                        strict_relocation_contract=True, allow_discarded_alloc_sections=True)
                    self.assertEqual(linked, stock, (profile, function))
                    self.assertEqual(report["relocation_count"], 0)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        for function, *_rest in FUNCTIONS: self.assertIn(function, body)
        for token in (".byte", ".short", ".word", ".inst"): self.assertNotIn(token, body)


if __name__ == "__main__": unittest.main()
