#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_terminal.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_terminal_host.c"


class PbServiceTerminalCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-terminal"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        selectors = {
            "OPEN_CFW_PB_TERMINAL_ENCODE_ONLY":
                "open_cfw_pb_terminal_encode_and_send",
            "OPEN_CFW_PB_TERMINAL_RX_ONLY":
                "APP_PbTerminalRxFrameDataProcess",
            "OPEN_CFW_PB_TERMINAL_COMM_RESP_ONLY":
                "APP_PbTerminalTxEncodeCommResp",
            "OPEN_CFW_PB_TERMINAL_STATUS_REPLY_ONLY":
                "APP_PbTerminalTxEncodeStatusReply",
            "OPEN_CFW_PB_TERMINAL_VOICE_INPUT_ONLY":
                "APP_PbTerminalTxEncodeVoiceInput",
            "OPEN_CFW_PB_TERMINAL_QUERY_REPLY_ONLY":
                "APP_PbTerminalTxEncodeQueryReply",
            "OPEN_CFW_PB_TERMINAL_AGENT_INTERRUPT_ONLY":
                "APP_PbTerminalTxEncodeAgentInterrupt",
            "OPEN_CFW_PB_TERMINAL_SESSION_SWITCH_ONLY":
                "APP_PbTerminalTxEncodeSessionSwitchRequest",
            "OPEN_CFW_PB_TERMINAL_NEW_SESSION_ONLY":
                "APP_PbTerminalTxEncodeNewSessionRequest",
            "OPEN_CFW_PB_TERMINAL_NEW_SESSION_CANCEL_ONLY":
                "APP_PbTerminalTxEncodeNewSessionCancel",
            "OPEN_CFW_PB_TERMINAL_DISPLAY_STATE_ONLY":
                "APP_PbTerminalTxEncodeDisplayStateNotify",
            "OPEN_CFW_PB_TERMINAL_LIST_FOCUS_ONLY":
                "APP_PbTerminalTxEncodeListFocus",
            "OPEN_CFW_PB_TERMINAL_OVERLAY_FOCUS_ONLY":
                "APP_PbTerminalTxEncodeOverlayFocus",
            "OPEN_CFW_PB_TERMINAL_BUFFER_WRITE_ONLY":
                "open_cfw_pb_service_terminal_buffer_write",
            "OPEN_CFW_PB_TERMINAL_ZERO_ONLY":
                "open_cfw_pb_service_terminal_zero",
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
        self.assertEqual(len(data), 14852)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "d045ebff68a95c0539974477ea50405505fe9e4635e3dab82ec96a2431e36027",
        )


if __name__ == "__main__":
    unittest.main()
