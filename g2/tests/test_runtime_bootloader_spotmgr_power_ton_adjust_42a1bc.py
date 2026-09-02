import ctypes
import hashlib
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_ton_adjust_42a1bc.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ADDRESS = 0x0042A1BC
SIZE = 232
FUNCTION = "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc"
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


class State(ctypes.Structure):
    _fields_ = [
        ("gpu_vddc_ton", ctypes.c_uint32),
        ("gpu_vddf_ton", ctypes.c_uint32),
        ("stm_ton", ctypes.c_uint32),
        ("default_ton", ctypes.c_uint32),
        ("simobuck2", ctypes.c_uint32),
        ("simobuck6", ctypes.c_uint32),
        ("simobuck7", ctypes.c_uint32),
    ]


def field(value: int, shift: int) -> int:
    return (value >> shift) & 31


def expected(ton: int, power: int, values: list[int]) -> tuple[int, int]:
    if power == 8:
        ton = 7
    if ton == 0:
        vddc, vddf = field(values[2], 0), field(values[2], 10)
    elif ton == 1:
        vddc, vddf = field(values[2], 5), field(values[2], 15)
    elif ton == 2:
        vddc, vddf = field(values[0], 0), field(values[1], 0)
    elif ton == 3:
        vddc, vddf = field(values[0], 10), field(values[1], 10)
    elif ton == 4:
        vddc, vddf = field(values[0], 5), field(values[1], 5)
    elif ton == 6:
        vddc, vddf = field(values[3], 0), field(values[3], 10)
    elif ton == 7:
        vddc, vddf = field(values[4], 11), field(values[5], 17)
    else:
        vddc, vddf = field(values[0], 15), field(values[1], 15)
    return (
        (values[4] & ~(31 << 25)) | (vddc << 25),
        (values[6] & ~(31 << 8)) | (vddf << 8),
    )


class BootloaderSpotmgrPowerTonAdjust42a1bcTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_ton.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.function = getattr(ctypes.CDLL(str(library)), FUNCTION)
        cls.function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.POINTER(State)]
        cls.function.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_source_is_reviewable_bsd_c_without_raw_opcodes(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("if (power_state == 8U)", body)
        self.assertIn("case 7U:", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)

    def test_portable_ton_selection_over_randomized_trim_words(self):
        rng = random.Random(0x42A1BC)
        for _ in range(50_000):
            values = [rng.getrandbits(32) for _ in range(7)]
            ton = rng.getrandbits(32)
            power = rng.getrandbits(32)
            state = State(*values)
            simobuck2, simobuck7 = expected(ton, power, values)
            self.function(ton, power, ctypes.byref(state))
            self.assertEqual(state.simobuck2, simobuck2)
            self.assertEqual(state.simobuck7, simobuck7)
            self.assertEqual(state.simobuck6, values[5])

    def test_dual_toolchain_body_is_exact_without_relocations(self):
        stock = BOOT.read_bytes()[ADDRESS - 0x00410000:ADDRESS - 0x00410000 + SIZE]
        expected_sha = "8964efd235151acf974a0248acac460c57de14ed8effbb879293a54d97f6dfd0"
        self.assertEqual(hashlib.sha256(stock).hexdigest(), expected_sha)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=ADDRESS,
                    relocation_configs=[], strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["unrelocated_sha256"], expected_sha)
                self.assertEqual(report["relocation_count"], 0)


if __name__ == "__main__":
    unittest.main()
