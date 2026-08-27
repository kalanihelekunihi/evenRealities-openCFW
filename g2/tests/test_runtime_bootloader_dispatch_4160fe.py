from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_dispatch_4160fe_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dispatch_4160fe.c"


class Options(ctypes.Structure):
    _fields_ = [
        ("argument_1", ctypes.c_uint),
        ("flags", ctypes.c_ubyte),
        ("reserved_05", ctypes.c_ubyte * 3),
        ("path_a_argument_6", ctypes.c_uint),
        ("path_a_minimum", ctypes.c_uint),
        ("path_a_argument_5", ctypes.c_uint),
        ("scaled_argument_2", ctypes.c_uint),
        ("argument_4", ctypes.c_uint),
    ]


class BootloaderRuntimeDispatch4160feTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-dispatch.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_runtime_dispatch_set.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint,
        ]
        cls.lib.open_cfw_bootloader_runtime_dispatch_4160fe.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(Options),
        ]
        cls.lib.open_cfw_bootloader_runtime_dispatch_4160fe.restype = ctypes.c_uint
        cls.lib.open_cfw_test_runtime_dispatch_argument.argtypes = [ctypes.c_uint]
        for name in ("critical_calls", "path_a_calls", "path_b_calls", "options_size"):
            getattr(cls.lib, f"open_cfw_test_runtime_dispatch_{name}").restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def set_behavior(self, critical: int = 0, path_a: int = 0xA0A0A0A0,
                     path_b_status: int = 1, path_b: int = 0xB0B0B0B0) -> None:
        self.lib.open_cfw_test_runtime_dispatch_set(critical, path_a, path_b_status, path_b)

    def calls(self) -> tuple[int, int, int]:
        return tuple(
            getattr(self.lib, f"open_cfw_test_runtime_dispatch_{name}")()
            for name in ("critical_calls", "path_a_calls", "path_b_calls")
        )

    def arguments(self) -> tuple[int, ...]:
        return tuple(self.lib.open_cfw_test_runtime_dispatch_argument(i) for i in range(7))

    def run_dispatch(self, a0: int, a3: int, options: Options | None) -> int:
        pointer = ctypes.byref(options) if options is not None else None
        return self.lib.open_cfw_bootloader_runtime_dispatch_4160fe(a0, a3, pointer)

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x60FE:0x61C6]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            200,
            "ee5d5e11a21632f16c94cfe5ae2ae6251386e1387ae3e4c090031b7695ed944f",
        ))
        self.assertEqual(image[0x1DDBE:0x1DDC2].hex(), "e8f79ef9")
        self.assertEqual(image[0x1E3AA:0x1E3AE].hex(), "e7f7a8fe")
        self.assertEqual(image[0x1E616:0x1E61A].hex(), "e7f772fd")

    def test_default_path_and_short_circuits(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_runtime_dispatch_options_size(), 28)
        self.set_behavior(critical=1)
        self.assertEqual(self.run_dispatch(7, 9, None), 0)
        self.assertEqual(self.calls(), (1, 0, 0))
        self.set_behavior()
        self.assertEqual(self.run_dispatch(0, 9, None), 0)
        self.assertEqual(self.calls(), (1, 0, 0))
        self.set_behavior(path_b_status=1, path_b=0x12345678)
        self.assertEqual(self.run_dispatch(7, 9, None), 0x12345678)
        self.assertEqual(self.calls(), (1, 0, 1))
        self.assertEqual(self.arguments()[:6], (7, 0, 0x100, 9, 0x18, 1))
        self.set_behavior(path_b_status=0, path_b=0x12345678)
        self.assertEqual(self.run_dispatch(7, 9, None), 0)

    def test_option_validation_and_path_selection(self) -> None:
        options = Options(argument_1=3, flags=0, argument_4=8)
        self.set_behavior()
        self.assertEqual(self.run_dispatch(7, 9, options), 0)
        self.assertEqual(self.calls(), (1, 0, 0))
        for invalid in (0x39, 0xFFFFFFFF):
            options = Options(flags=1, argument_4=invalid)
            self.set_behavior()
            self.assertEqual(self.run_dispatch(7, 9, options), 0)
            self.assertEqual(self.calls(), (1, 0, 0))

        options = Options(argument_1=3, flags=1, scaled_argument_2=0x12347, argument_4=8)
        self.set_behavior(path_b=0x55)
        self.assertEqual(self.run_dispatch(7, 9, options), 0x55)
        self.assertEqual(self.arguments()[:6], (7, 3, 0x48D1, 9, 8, 1))

        options = Options(
            argument_1=3, flags=1, path_a_argument_6=0x66,
            path_a_minimum=0x70, path_a_argument_5=0x55,
            scaled_argument_2=0x400, argument_4=8,
        )
        self.set_behavior(path_a=0xCAFEBABE)
        self.assertEqual(self.run_dispatch(7, 9, options), 0xCAFEBABE)
        self.assertEqual(self.calls(), (1, 1, 0))
        self.assertEqual(self.arguments(), (7, 3, 0x100, 9, 8, 0x55, 0x66))

        options.path_a_minimum = 0x6F
        self.set_behavior()
        self.assertEqual(self.run_dispatch(7, 9, options), 0)
        self.assertEqual(self.calls(), (1, 0, 0))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-dispatch.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
