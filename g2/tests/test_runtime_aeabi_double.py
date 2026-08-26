"""Validate source-owned Apollo510 ARM-EABI double helpers."""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components" / "shared" / "runtime" / "runtime_aeabi_double.c"


class RuntimeAeabiDoubleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("aeabi_double.dylib" if sys.platform == "darwin" else "aeabi_double.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(SOURCE)]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.target = temporary / "aeabi_double.o"
        subprocess.run(
            [
                clang, "--target=thumbv7em-none-eabi", "-mthumb", "-O2",
                "-ffreestanding", "-fno-builtin", "-fropi", "-Wall",
                "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(cls.target),
            ], check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_host_fallback_semantics(self) -> None:
        for name in ("__aeabi_dadd", "__aeabi_dmul", "__aeabi_ddiv"):
            fn = getattr(self.loaded, name)
            fn.argtypes = [ctypes.c_double, ctypes.c_double]
            fn.restype = ctypes.c_double
        self.assertEqual(getattr(self.loaded, "__aeabi_dadd")(1.25, 2.5), 3.75)
        self.assertEqual(getattr(self.loaded, "__aeabi_dmul")(-3.0, 0.5), -1.5)
        self.assertEqual(getattr(self.loaded, "__aeabi_ddiv")(7.0, 2.0), 3.5)
        convert = getattr(self.loaded, "__aeabi_ui2d")
        convert.argtypes = [ctypes.c_uint]
        convert.restype = ctypes.c_double
        narrow = getattr(self.loaded, "__aeabi_d2f")
        narrow.argtypes = [ctypes.c_double]
        narrow.restype = ctypes.c_float
        self.assertEqual(convert(4_000_000_000), 4_000_000_000.0)
        self.assertAlmostEqual(narrow(1.25), 1.25)

    def test_target_exports_have_no_runtime_dependencies(self) -> None:
        symbols = subprocess.run(["/usr/bin/nm", "-g", str(self.target)], check=True, capture_output=True, text=True).stdout
        for name in ("__aeabi_dadd", "__aeabi_dmul", "__aeabi_ddiv", "__aeabi_ui2d", "__aeabi_d2f"):
            self.assertIn(name, symbols)
        self.assertFalse(any(line.strip().startswith("U ") for line in symbols.splitlines()), symbols)
        disassembly = subprocess.run(["/usr/bin/objdump", "-d", str(self.target)], check=True, capture_output=True, text=True).stdout.lower()
        # Apple's objdump does not decode FPv5 for this object triple, so pin
        # the emitted opcode halfwords as well as the reviewed source text.
        for encoding in ("ee30 0b01", "ee20 0b01", "ee80 0b01", "eeb8 0b40", "eeb7 0bc0"):
            self.assertIn(encoding, disassembly)
        source = SOURCE.read_text()
        for mnemonic in ("vadd.f64", "vmul.f64", "vdiv.f64", "vcvt.f64.u32", "vcvt.f32.f64"):
            self.assertIn(mnemonic, source)


if __name__ == "__main__":
    unittest.main()
