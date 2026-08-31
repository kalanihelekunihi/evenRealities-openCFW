#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_setting.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_setting_host.c"
SELECTORS = {
    "BUFFER_WRITE": "open_cfw_pb_service_setting_buffer_write",
    "ZERO": "open_cfw_pb_service_setting_zero",
    "DUPLICATE": "setting_is_duplicate_message",
    "PARSE": "setting_parse_data_package",
    "RESPOND": "setting_respond_to_app",
    "BUILD_STATUS": "setting_build_full_status_package",
    "RESPOND_LOCAL": "setting_respond_with_local_data",
    "RESPOND_SERIALIZE": "setting_respond_to_app_serialize",
    "RESPOND_LOCAL_SERIALIZE": "setting_respond_with_local_data_serialize",
    "NOTIFY_COMMON": "setting_notify_common",
    "NOTIFY_STATUS": "setting_notify_device_status_to_app",
    "NOTIFY_RECALIBRATION": "setting_notify_recalibration_status_to_app",
    "NOTIFY_SILENT": "notify_silent_mode_to_app",
}


class PbServiceSettingCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-setting"
            subprocess.run([
                "clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, function in SELECTORS.items():
                obj = Path(directory) / f"{selector}.o"
                subprocess.run([
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror",
                    f"-DOPEN_CFW_PB_SETTING_{selector}_ONLY",
                    "-c", str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {
                    fields[2] for line in symbols.splitlines()
                    if len(fields := line.split()) == 3 and fields[1] == "T"
                }
                self.assertEqual(entries, {function})

    def test_source_pin(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 18384)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "faa899b9c966d073ef4e9740221a8e2940ee4baab874ddf63ae4ef5dec0b937f",
        )


if __name__ == "__main__":
    unittest.main()
