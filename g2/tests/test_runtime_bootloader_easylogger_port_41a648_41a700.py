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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_easylogger_port_41a648.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_easylogger_port_host.c"
RUN_BASE = 0x00410000
FUNCTIONS = (
    (0x0041A648, 0x0041A65C, "88fc734f91a9595fff96effb708c9b8e593b6bca403cf1590ec754ecb851c862", (0x0041A688,)),
    (0x0041A65C, 0x0041A672, "169a7ddcc907f767865c49a201f325c33770f7731e8359424abbe08bc380f34f", (0x0041A69C,)),
    (0x0041A672, 0x0041A684, "0538c89be6a767f59d04ff9ba0d37c6f8e98a3fffa5d35457104a277590e055a", (0x0041A6A4,)),
    (0x0041A684, 0x0041A692, "f0eefbc1594e2e86a7268d2ec186bf619fe4651b65e54a3d86b6b2c0bc3e1a30", (0x00417350,)),
    (0x0041A692, 0x0041A69A, "ececfe97080e5d40476e61bb0fa28b31ff6460285d33e9433047d4359d34e408", (0x00417AC2,)),
    (0x0041A69A, 0x0041A6A2, "f4f02ad3353ef68eadb1408b05bd4b2b89440a4f4656dd1075ba92268d770e35", (0x0041757E, 0x00417B9C)),
    (0x0041A6A2, 0x0041A6AA, "a56bdb9407dda49c85a75ce1e3c34b88b0744e3797b68725874d0e3df10eee3e", (0x004175A0, 0x00417BB2)),
    (0x0041A6AA, 0x0041A6C2, "d4721c085671021321dfc612a27220d9f5e2722f2b1c33c4bb479fbbada6b193", (0x00417888,)),
    (0x0041A6C2, 0x0041A6DA, "6369de337442570729fecc8933cc1d333aecd1a4356f2eadde26f623342e1472", (0x0041A6F2, 0x0041A6FA)),
    (0x0041A6F0, 0x0041A6F8, "3e76180d81350b11618fc002f8cd142d0ae1c44e2f587c61c2edf0342a72d65f", (0x004178C4,)),
    (0x0041A6F8, 0x0041A700, "981e6fe98ffa9b8a2e314502aafc3c1382cec761a7874d200491addc71da6244", (0x00417900,)),
)


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderEasyloggerPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "easylogger_port.dylib" if sys.platform == "darwin" else "easylogger_port.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_bodies_and_direct_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        for start, end, expected_sha, expected_callers in FUNCTIONS:
            with self.subTest(address=hex(start)):
                body = image[start - RUN_BASE:end - RUN_BASE]
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_sha)
                callers = tuple(
                    address
                    for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == start
                )
                self.assertEqual(callers, expected_callers)

    def test_mutex_output_time_and_task_name_semantics(self) -> None:
        for name in (
            "mutex_lifecycle",
            "null_mutex_is_noop",
            "output_forwards_all_arguments",
            "formats_tick",
            "task_name_policy",
        ):
            with self.subTest(case=name):
                function = getattr(self.loaded, f"open_cfw_test_easylogger_port_{name}")
                function.restype = ctypes.c_uint32
                self.assertEqual(function(), 1)

    def test_source_seams_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in (
            "0x200270E8U", "0x00433D28U", "0x20026F18U", "0x0041A6DCU",
            "0x00434084U", "0x00416611U", "0x004166ABU", "0x00416711U",
            "0x0041B855U", "0x004160E9U", "0x0041B219U", "1000U",
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "easylogger_port.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra", "-Werror",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
