#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_translate.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_translate_host.c"


class PbServiceTranslateCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-translate"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        selectors = {
            "OPEN_CFW_PB_TRANSLATE_ENCODE_ONLY":
                "open_cfw_pb_translate_encode_and_send",
            "OPEN_CFW_PB_TRANSLATE_RX_ONLY":
                "APP_PbTranslateRxFrameDataProcess",
            "OPEN_CFW_PB_TRANSLATE_NOTIFY_ONLY":
                "APP_PbTranslateTxEncodeNotify",
            "OPEN_CFW_PB_TRANSLATE_COMM_RESP_ONLY":
                "APP_PbTranslateTxEncodeCommResp",
            "OPEN_CFW_PB_TRANSLATE_MODE_SWITCH_ONLY":
                "APP_PbTranslateTxEncodeModeSwitch",
            "OPEN_CFW_PB_TRANSLATE_BUFFER_WRITE_ONLY":
                "open_cfw_pb_service_translate_buffer_write",
            "OPEN_CFW_PB_TRANSLATE_ZERO_ONLY":
                "open_cfw_pb_service_translate_zero",
        }
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in selectors.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi",
                    "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror", "-D" + selector + "=1", "-c",
                    str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {
                    parts[2] for line in symbols.splitlines()
                    if len(parts := line.split()) == 3 and parts[1] == "T"
                }
                self.assertEqual(entries, {expected})

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 9285)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "939587d5af46481234ce3ad7debfa0809c7fc8ff905349a6fa055ea72bb55c83",
        )


if __name__ == "__main__":
    unittest.main()
