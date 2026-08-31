#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_onboarding.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_onboarding_host.c"


class PbServiceOnboardingCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-onboarding"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        selectors = {
            "OPEN_CFW_PB_ONBOARDING_BUFFER_WRITE_ONLY":
                "open_cfw_pb_service_onboarding_buffer_write",
            "OPEN_CFW_PB_ONBOARDING_ZERO_ONLY":
                "open_cfw_pb_service_onboarding_zero",
            "OPEN_CFW_PB_ONBOARDING_ENCODE_ONLY":
                "open_cfw_pb_onboarding_encode_and_send",
            "OPEN_CFW_PB_ONBOARDING_DISPATCH_ONLY":
                "APP_PbRxOnboardingFrameDataProcess",
            "OPEN_CFW_PB_ONBOARDING_RX_CONFIG_ONLY":
                "PB_RxOnboardingConfig",
            "OPEN_CFW_PB_ONBOARDING_TX_CONFIG_ONLY":
                "APP_PbTxEncodeOnboardingConfig",
            "OPEN_CFW_PB_ONBOARDING_NOTIFY_CONFIG_ONLY":
                "APP_PbNotifyEncodeOnboardingConfig",
            "OPEN_CFW_PB_ONBOARDING_RX_HEARTBEAT_ONLY":
                "PB_RxOnboardingHeartbeat",
            "OPEN_CFW_PB_ONBOARDING_TX_HEARTBEAT_ONLY":
                "APP_PbTxEncodeOnboardingHeartbeat",
            "OPEN_CFW_PB_ONBOARDING_RX_EVENT_ONLY":
                "PB_RxOnboardingEvent",
            "OPEN_CFW_PB_ONBOARDING_TX_EVENT_ONLY":
                "APP_PbTxEncodeOnboardingEvent",
            "OPEN_CFW_PB_ONBOARDING_NOTIFY_EVENT_ONLY":
                "APP_PbNotifyEncodeOnboardingEvent",
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
        self.assertEqual(len(data), 14749)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "54a4eca39f6d9974f5c7bbb38dbb0188c62c21bab7be7d483ce99fda96c37e2a",
        )


if __name__ == "__main__":
    unittest.main()
