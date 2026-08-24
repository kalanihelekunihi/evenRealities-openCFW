#!/usr/bin/env python3
import hashlib
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_legacy_sm.c"
FIXTURE = ROOT / "tests/fixtures/cordio_smp_legacy_sm_host.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x437FE0


class CordioSmpLegacySmTests(unittest.TestCase):
    def test_source_and_host_behavior(self):
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 8797)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "9a90b81d01f83ca8daa21cf645594188a6e7feb61a40f61b2afee089063d5c01")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "legacy-sm"
            subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(output)], check=True)
            subprocess.run([str(output)], check=True)

    def test_compiled_dispatch_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            obj = Path(temp) / "legacy-sm.o"
            subprocess.run(["xcrun", "clang", "-target", "armv7m-none-eabi",
                "-mcpu=cortex-m55", "-mthumb", "-O2", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-DOPEN_CFW_SMP_LEGACY_SM_DATA_ONLY=1", "-c", str(SOURCE),
                "-o", str(obj)], check=True)
            dump = subprocess.run(["xcrun", "llvm-objdump", "-s",
                "--section=.rodata.open_cfw_cordio_smp_legacy_dispatch", str(obj)],
                check=True, capture_output=True, text=True).stdout
            payload = bytearray()
            for line in dump.splitlines():
                fields = line.split()
                if fields and 1 <= len(fields[0]) <= 8 and all(
                        character in "0123456789abcdefABCDEF" for character in fields[0]):
                    for field in fields[1:]:
                        if len(field) < 2 or len(field) > 8 or len(field) % 2: break
                        try: payload.extend(bytes.fromhex(field))
                        except ValueError: break
            self.assertEqual(len(payload), 705)
            self.assertEqual(hashlib.sha256(payload).hexdigest(),
                "3f64e85789a57cd89df7ab2430791d143db0567a016cf0632d76ff32af16728e")

    def test_dispatch_matches_all_authenticated_stock_tables(self):
        # Derive the same closed graph directly so this test has no generated fixture.
        blob = IMAGE.read_bytes(); chunks = []
        def read(address, size): return blob[address - BASE:address - BASE + size]
        def table(address):
            out = bytearray()
            while True:
                row = read(address + len(out), 3); out.extend(row)
                if row == b"\0\0\0": return bytes(out)
        for interface, actions, states in ((0x78C344, 25, 14), (0x78C4AC, 27, 15)):
            raw = read(interface, 12); state_root, action_root, common = struct.unpack("<III", raw)
            chunks.extend((raw, read(action_root, actions * 4), read(state_root, states * 4), table(common)))
            for address in struct.unpack("<" + "I" * states, read(state_root, states * 4)):
                chunks.append(table(address))
        payload = b"".join(chunks)
        self.assertEqual((len(payload), hashlib.sha256(payload).hexdigest()),
            (705, "3f64e85789a57cd89df7ab2430791d143db0567a016cf0632d76ff32af16728e"))


if __name__ == "__main__":
    unittest.main()
