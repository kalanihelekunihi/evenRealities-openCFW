#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_even_ai.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_even_ai_host.c"


class PbServiceEvenAICandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-even-ai"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        selectors = {
            "OPEN_CFW_PB_EVEN_AI_RX_FRAME_ONLY":
                "APP_PbRxEvenAIFrameDataProcess",
            "OPEN_CFW_PB_EVEN_AI_RX_CTRL_ONLY": "PB_RxEvenAICtrl",
            "OPEN_CFW_PB_EVEN_AI_TX_CTRL_ONLY": "APP_PbTxEncodeEvenAICtrl",
            "OPEN_CFW_PB_EVEN_AI_NOTIFY_CTRL_ONLY":
                "APP_PbNotifyEncodeEvenAICtrl",
            "OPEN_CFW_PB_EVEN_AI_RX_VAD_ONLY": "PB_RxEvenAIVADInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_VAD_ONLY":
                "APP_PbTxEncodeEvenAIVADInfo",
            "OPEN_CFW_PB_EVEN_AI_NOTIFY_VAD_ONLY":
                "APP_PbNotifyEncodeEvenAIVADInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_ASK_ONLY": "PB_RxEvenAIAskInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_ASK_ONLY":
                "APP_PbTxEncodeEvenAIAskInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_ANALYSE_ONLY": "PB_RxEvenAIAnalyseInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_ANALYSE_ONLY":
                "APP_PbTxEncodeEvenAIAnalyseInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_REPLY_ONLY": "PB_RxEvenAIReplyInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_REPLY_ONLY":
                "APP_PbTxEncodeEvenAIReplyInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_SKILL_ONLY": "PB_RxEvenAISkillInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_SKILL_ONLY":
                "APP_PbTxEncodeEvenAISkillInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_PROMPT_ONLY": "PB_RxEvenAIPromptInfo",
            "OPEN_CFW_PB_EVEN_AI_TX_PROMPT_ONLY":
                "APP_PbTxEncodeEvenAIPromptInfo",
            "OPEN_CFW_PB_EVEN_AI_RX_EVENT_ONLY": "PB_RxEvenAIEvent",
            "OPEN_CFW_PB_EVEN_AI_TX_EVENT_ONLY":
                "APP_PbTxEncodeEvenAIEvent",
            "OPEN_CFW_PB_EVEN_AI_NOTIFY_EVENT_ONLY":
                "APP_PbNotifyEncodeEvenAIEvent",
            "OPEN_CFW_PB_EVEN_AI_RX_HEARTBEAT_ONLY": "PB_RxEvenAIHeartbeat",
            "OPEN_CFW_PB_EVEN_AI_TX_HEARTBEAT_ONLY":
                "APP_PbTxEncodeEvenAIHeartbeat",
            "OPEN_CFW_PB_EVEN_AI_RX_CONFIG_ONLY": "PB_RxEvenAIConfig",
            "OPEN_CFW_PB_EVEN_AI_TX_CONFIG_ONLY":
                "APP_PbTxEncodeEvenAIConfig",
            "OPEN_CFW_PB_EVEN_AI_COMM_RESP_ONLY":
                "APP_PbTxEncodeEvenAICommResp",
            "OPEN_CFW_PB_EVEN_AI_BUFFER_WRITE_ONLY":
                "open_cfw_pb_service_even_ai_buffer_write",
            "OPEN_CFW_PB_EVEN_AI_ZERO_ONLY":
                "open_cfw_pb_service_even_ai_zero",
        }
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in selectors.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                    "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror", "-D" + selector + "=1", "-c",
                    str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {parts[2] for line in symbols.splitlines()
                           if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {expected})

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 23766)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "8b6afa020c4cbfc372ade7d9824080a52cf0ae11cb132f71ae140af122ba8588",
        )


if __name__ == "__main__":
    unittest.main()
