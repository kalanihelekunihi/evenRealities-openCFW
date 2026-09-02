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
UPDATE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_update_42a878.c"
PROFILE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_profile_apply_42ab7c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x00410000
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


class Status(ctypes.Structure):
    _fields_ = [
        ("device", ctypes.c_uint32), ("audio", ctypes.c_uint32),
        ("memory", ctypes.c_uint32), ("ssram", ctypes.c_uint32),
        ("temperature", ctypes.c_uint8), ("cpu", ctypes.c_uint8),
        ("gpu", ctypes.c_uint8),
    ]


class Profile(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint32), ("reserved0", ctypes.c_uint32 * 7),
        ("word20", ctypes.c_uint32), ("reserved1", ctypes.c_uint32 * 17),
        ("word68", ctypes.c_uint32),
    ]


class SpotmgrUpdateProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "spot-update.dylib"
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
            "-Wextra", "-Werror", "-dynamiclib", str(UPDATE), str(PROFILE),
            "-o", str(cls.library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.update = cls.lib.open_cfw_bootloader_spotmgr_power_state_update_42a878_portable
        cls.update.argtypes = [ctypes.POINTER(Status), ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_void_p]
        cls.update.restype = ctypes.c_uint32
        cls.profile = cls.lib.open_cfw_bootloader_spotmgr_profile_apply_42ab7c
        cls.profile.argtypes = [ctypes.POINTER(Profile)] + [ctypes.POINTER(ctypes.c_uint32)] * 3
        cls.profile.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_stimulus_routes_and_null_contracts(self) -> None:
        for stimulus in range(9):
            for on in range(2):
                status = Status(1, 2, 3, 4, 1, 1, 1)
                argument = ctypes.c_uint32(0x00400005)
                result = self.update(ctypes.byref(status), stimulus, on,
                                     ctypes.byref(argument))
                self.assertEqual(result, 0 if stimulus < 7 else 6)
                if stimulus == 3 and on:
                    self.assertEqual(status.device, 0x00400005)
                if stimulus == 4 and on:
                    self.assertEqual(status.audio, 0x00400007)
                if stimulus == 5:
                    self.assertEqual(status.memory, 0x00400005)
                if stimulus == 6 and on:
                    self.assertEqual(status.ssram, 0x00400005)
        status = Status()
        for stimulus, on in ((0, 0), (1, 0), (2, 0), (3, 1), (4, 1),
                             (5, 0), (6, 1)):
            self.assertEqual(self.update(ctypes.byref(status), stimulus, on, None), 6)

    def test_profile_field_application_and_magic_guard(self) -> None:
        state = Profile(0x1F01600D, (ctypes.c_uint32 * 7)(),
                        0xABCDE780, (ctypes.c_uint32 * 17)(), 0x1234567B)
        a, b, c = ctypes.c_uint32(0xAAAAFC00), ctypes.c_uint32(0xBBBBFFC0), ctypes.c_uint32(0xCCCC7FFF)
        self.assertEqual(self.profile(ctypes.byref(state), ctypes.byref(a), ctypes.byref(b), ctypes.byref(c)), 0)
        self.assertEqual(a.value & 0x3FF, (state.word20 >> 7) & 0x3FF)
        self.assertEqual(b.value & 0x3F, (state.word68 >> 2) & 0x3F)
        self.assertEqual((c.value >> 15) & 3, state.word68 & 3)
        state.magic = 0
        before = (a.value, b.value, c.value)
        self.profile(ctypes.byref(state), ctypes.byref(a), ctypes.byref(b), ctypes.byref(c))
        self.assertEqual((a.value, b.value, c.value), before)

    def test_dispatch_table_entries_are_authenticated(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual(int.from_bytes(boot[0x0041D150 - BASE:0x0041D154 - BASE], "little"), 0x0042A879)
        self.assertEqual(int.from_bytes(boot[0x0041D158 - BASE:0x0041D15C - BASE], "little"), 0x0042AB7D)

    def test_both_reviewed_compilers_reproduce_exact_bodies(self) -> None:
        specs = (
            (UPDATE, "open_cfw_bootloader_spotmgr_power_state_update_42a878",
             0x0042A878, 0x0042AB6E,
             "2939cbe9bff77ff31332559da4bf012f95b30ea65fd52954eba693168367e137",
             ((0x38, 0x0041B8EC), (0x16A, 0x00427E0C),
              (0x202, 0x0042A08C), (0x27C, 0x0042A19C),
              (0x2B2, 0x0042A550), (0x2DA, 0x0042A4BC))),
            (PROFILE, "open_cfw_bootloader_spotmgr_profile_apply_42ab7c",
             0x0042AB7C, 0x0042ABB2,
             "686b1225442297793c2d963c1903f0d2fa5dde214abdae1352ad5ade61c326f3", ()),
        )
        boot = BOOT.read_bytes()
        for clang, version in (
            (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
            (Path("/opt/homebrew/opt/llvm@22/bin/clang"), "Homebrew clang version 22.1.8"),
        ):
            if not clang.exists():
                self.skipTest(f"reviewed compiler unavailable: {clang}")
            self.assertTrue(subprocess.run([str(clang), "--version"], check=True,
                                            capture_output=True, text=True).stdout.startswith(version))
            for source, function, start, end, raw_sha, relocations in specs:
                output = Path(self.temp.name) / f"{clang.parent.name}-{function}.o"
                subprocess.run([
                    str(clang), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
                    "-c", str(source), "-o", str(output),
                ], check=True, capture_output=True, text=True)
                payload, sections = apollo_overlay.parse_elf32(output)
                section = apollo_overlay.section_named(sections, f".text.{function}")
                body = bytearray(payload[int(section["offset"]):int(section["offset"]) + int(section["size"])])
                self.assertEqual(hashlib.sha256(body).hexdigest(), raw_sha)
                for offset, target in relocations:
                    body[offset:offset + 4] = apollo_overlay.encode_thumb_bl(start + offset, target)
                self.assertEqual(bytes(body), boot[start - BASE:end - BASE])


if __name__ == "__main__":
    unittest.main()
