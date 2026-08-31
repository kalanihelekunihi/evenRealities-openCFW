#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_quicklist.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_quicklist_host.c"
SOURCE_SIZE = 16271
SOURCE_SHA256 = "f64b59b3cd70b1f51b4e39a24aa1977c004917bfc442ede92134c4c71649d53b"
SELECTORS = {
    "BUFFER_WRITE": "open_cfw_pb_service_quicklist_buffer_write",
    "ZERO": "open_cfw_pb_service_quicklist_zero",
    "TRANSMIT": "open_cfw_pb_service_quicklist_transmit",
    "RX_FRAME": "APP_PbRxQuicklistFrameDataProcess",
    "DECODE_DATA": "APP_DecodePbRxQuicklistData",
    "RX_ITEM": "PB_RxQuicklistItem",
    "TX_ITEM": "APP_PbTxEncodeQuicklistItem",
    "RX_MULTI": "PB_RxQuicklistMultItems",
    "TX_MULTI": "APP_PbTxEncodeQuicklistMultItems",
    "NOTIFY_MULTI": "APP_PbNotifyEncodeQuicklistMultItems",
    "RX_EVENT": "PB_RxQuicklistEvent",
    "TX_EVENT": "APP_PbTxEncodeQuicklistEvent",
    "NOTIFY_EVENT": "APP_PbNotifyEncodeQuicklistEvent",
}


class PbServiceQuicklistCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-quicklist"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in SELECTORS.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-mllvm", "-enable-machine-outliner=never",
                    "-DOPEN_CFW_PB_QUICKLIST_" + selector + "_ONLY=1",
                    "-c", str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {parts[2] for line in symbols.splitlines()
                           if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {expected})

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), SOURCE_SIZE)
        self.assertEqual(hashlib.sha256(data).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
