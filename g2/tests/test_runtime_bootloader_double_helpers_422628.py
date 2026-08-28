from __future__ import annotations

import ctypes
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
APOLLO = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_double_helpers_422628.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_double_helpers_host.c"

RANGES = (
    (0x00422628, 0x00422634, "3d9cd383328c9154f7f4458c8c7804a4953b75099aeb35a83083af7f0e397219"),
    (0x00422634, 0x00422698, "26cb6c3e8b0b82a1a5439a66af6c5b9cd3819aa36381e828fecfb2a53ecb34e0"),
    (0x00422698, 0x004226CC, "46a7b282661331eea999926ca210c62fe20fe7a7edb16b5b0678ea0823dfdf06"),
    (0x004226CC, 0x00422700, "f477d157e5470add8ec143ce6102542cd5c77ef7e185f09bbd80f3113d6b813d"),
    (0x00422700, 0x00422712, "768cb4742e8c3d9fde188518def7c0256f34609227dd14d0eb1beedb33060929"),
    (0x00422714, 0x00422804, "3690749b6e1f89f9f3c7ba0863de59546221db9a90d57e4e734607296c965f1a"),
    (0x00422804, 0x00422812, "daf9ec9c6b365a60c5c647bdb311426a1f4847c759b8ab957aadc4a80991bfe3"),
    (0x00422812, 0x00422820, "c9579fcb2a7fb1705e7ae6728d3316185c25614a220956526a3e0c4a506e40cb"),
    (0x00422820, 0x00422832, "65d49f460559c76322474dd3daa2cd042997ae2d2643b5b2cf3f47f974f1ef2d"),
    (0x00422832, 0x00422844, "6fbae9ad2d0b396ef4a43e12478c6571fbdebb31baf9ba24c16e8eed9ed04836"),
    (0x00422844, 0x00422852, "b552ee0f9ab3cc9530f3479a7bfc090ae478dfb17d185c0afdbc0eddd0d6d85d"),
    (0x00422852, 0x00422860, "cc2efa764fc8a6f57ea98cd3877f8cc1aa811c92d9c11a2ce8db3865254d81b1"),
    (0x00422860, 0x00422872, "cc762b8ff91a2a5f7d10485e9561b7e33b3093e475d6ea07c0fe44e876c93e20"),
)


class BootloaderDoubleHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        cls.libpath = Path(cls.tmp.name) / f"double_helpers{suffix}"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(cls.libpath)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.libpath))
        cls.frexp = cls.lib.open_cfw_bootloader_double_frexp_422628
        cls.frexp.argtypes = [ctypes.c_double, ctypes.POINTER(ctypes.c_int32)]
        cls.frexp.restype = ctypes.c_double
        cls.ldexp = cls.lib.open_cfw_bootloader_double_ldexp_422700
        cls.ldexp.argtypes = [ctypes.c_double, ctypes.c_int32]
        cls.ldexp.restype = ctypes.c_double
        for name in ("subtract", "divide", "multiply"):
            fn = getattr(cls.lib, f"open_cfw_bootloader_double_{name}_422" + {"subtract":"820", "divide":"832", "multiply":"860"}[name])
            fn.argtypes = [ctypes.c_double, ctypes.c_double]
            fn.restype = ctypes.c_double

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_bodies_padding_callers_and_apollo_twins(self) -> None:
        boot = OFFICIAL.read_bytes()
        apollo = APOLLO.read_bytes()
        for start, end, digest in RANGES:
            body = boot[start - 0x00410000:end - 0x00410000]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        self.assertEqual(boot[0x12712:0x12714], b"\x00\xbf")
        self.assertEqual(boot[0x12872:0x12874], b"\x00\x00")
        twins = ((0x422628,0x422634,0x51C170),(0x422634,0x422698,0x51C17C),(0x422698,0x4226CC,0x51C1E0),(0x422700,0x422712,0x51C214),(0x422804,0x422812,0x51C318),(0x422812,0x422820,0x51C326),(0x422820,0x422832,0x51C334),(0x422832,0x422844,0x51C346),(0x422844,0x422852,0x51C358),(0x422852,0x422860,0x51C366),(0x422860,0x422872,0x51C374))
        for start, end, peer in twins:
            self.assertEqual(boot[start-0x410000:end-0x410000], apollo[peer-0x480000:peer-0x480000+(end-start)])
        callers = {0x422628:(0x41EA32,),0x422698:(0x41EAA8,),0x4226CC:(0x41EACC,),0x422700:(0x41EAD4,),0x422804:(0x41EADC,),0x422812:(0x41EAE8,),0x422820:(0x41EAF4,0x41EC70),0x422832:(0x41EBEE,),0x422844:(0x41EC1E,),0x422852:(0x41EC64,),0x422860:(0x41EC7A,0x41F290,0x41F2A0)}
        for target, sites in callers.items():
            for site in sites:
                self.assertNotEqual(boot[site-0x410000:site-0x410000+4], b"\0"*4, hex(target))

    def test_frexp_normal_subnormal_zero_and_nonfinite(self) -> None:
        for value in (0.0, -0.0, 1.0, -6.5, float.fromhex("0x1p-1074"), float.fromhex("0x1.fffffffffffffp1023"), float("inf"), float("nan")):
            exponent = ctypes.c_int32(123)
            got = self.frexp(value, ctypes.byref(exponent))
            if math.isnan(value): self.assertTrue(math.isnan(got)); self.assertEqual(exponent.value, 0)
            elif math.isinf(value) or value == 0.0: self.assertEqual(got, value); self.assertEqual(exponent.value, 0)
            else:
                expected, exp = math.frexp(value)
                self.assertEqual(got, expected); self.assertEqual(exponent.value, exp)

    def test_ldexp_and_vfp_arithmetic(self) -> None:
        for value, exponent in ((1.5,4),(-3.25,-3),(0.0,20),(float.fromhex("0x1p-100"),-50)):
            self.assertEqual(self.ldexp(value, exponent), math.ldexp(value, exponent))
        self.assertEqual(self.lib.open_cfw_bootloader_double_subtract_422820(9.5, 2.25), 7.25)
        self.assertEqual(self.lib.open_cfw_bootloader_double_divide_422832(9.0, 4.0), 2.25)
        self.assertEqual(self.lib.open_cfw_bootloader_double_multiply_422860(-3.0, 2.5), -7.5)

    def test_comparisons_and_conversions(self) -> None:
        forward = self.lib.open_cfw_bootloader_double_compare_422698
        reverse = self.lib.open_cfw_bootloader_double_compare_reverse_4226cc
        forward.argtypes = reverse.argtypes = [ctypes.c_double, ctypes.c_double]
        forward.restype = reverse.restype = ctypes.c_int
        self.assertEqual(forward(-1.0, 2.0), 1); self.assertEqual(reverse(-1.0, 2.0), 0)
        d2i = self.lib.open_cfw_bootloader_double_to_i32_422804; d2i.argtypes=[ctypes.c_double]; d2i.restype=ctypes.c_int32
        i2d = self.lib.open_cfw_bootloader_i32_to_double_422812; i2d.argtypes=[ctypes.c_int32]; i2d.restype=ctypes.c_double
        d2u = self.lib.open_cfw_bootloader_double_to_u32_422844; d2u.argtypes=[ctypes.c_double]; d2u.restype=ctypes.c_uint32
        u2d = self.lib.open_cfw_bootloader_u32_to_double_422852; u2d.argtypes=[ctypes.c_uint32]; u2d.restype=ctypes.c_double
        self.assertEqual(d2i(-12.75), -12); self.assertEqual(i2d(-123456), -123456.0)
        self.assertEqual(d2u(1234.75), 1234); self.assertEqual(u2d(0xF0000000), float(0xF0000000))

    def test_source_cross_compiles(self) -> None:
        for cc in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(cc).exists():
                subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(self.tmp.name)/(Path(cc).parent.name+"-double.o"))],check=True,capture_output=True)


if __name__ == "__main__": unittest.main()
