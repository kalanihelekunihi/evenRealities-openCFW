#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_teleprompt.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_teleprompt_host.c"


class PbServiceTelepromptCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-teleprompt"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        selectors = {
            "OPEN_CFW_PB_TELEPROMPT_RX_ONLY":
                "APP_PbRxTelepromptFrameDataProcess",
            "OPEN_CFW_PB_TELEPROMPT_COMM_RESP_ONLY":
                "APP_PbTelepromptTxEncodeCommResp",
            "OPEN_CFW_PB_TELEPROMPT_STATUS_ONLY":
                "APP_PbTxEncodeStatusNotify",
            "OPEN_CFW_PB_TELEPROMPT_FILE_LIST_ONLY":
                "APP_PbTxEncodeFileListRequest",
            "OPEN_CFW_PB_TELEPROMPT_FILE_SELECT_ONLY":
                "APP_PbTxEncodeFileSelect",
            "OPEN_CFW_PB_TELEPROMPT_PAGE_DATA_ONLY":
                "APP_PbTxEncodePageDataRequest",
            "OPEN_CFW_PB_TELEPROMPT_SCROLL_SYNC_ONLY":
                "APP_PbTxEncodeScrollSync",
            "OPEN_CFW_PB_TELEPROMPT_BUFFER_WRITE_ONLY":
                "open_cfw_pb_service_teleprompt_buffer_write",
            "OPEN_CFW_PB_TELEPROMPT_ZERO_ONLY":
                "open_cfw_pb_service_teleprompt_zero",
        }
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in selectors.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-D" + selector + "=1", "-c", str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {parts[2] for line in symbols.splitlines()
                           if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {expected})

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 13432)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "403c917e094485afa896a3559bc5fcd8e32dfa234fc5534e168c400fda54fc74",
        )


if __name__ == "__main__":
    unittest.main()
