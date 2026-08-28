# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "components/apollo_main/core_overlay"
SOURCES = [
    CORE / "pt_protocol_procsr.c",
    CORE / "pt_protocol_handlers_basic.c",
    CORE / "pt_protocol_handlers_config.c",
    CORE / "pt_protocol_handlers_data.c",
    CORE / "pt_protocol_handlers_display.c",
    CORE / "pt_protocol_handlers_sensors.c",
    CORE / "pt_protocol_handlers_services.c",
    CORE / "pt_protocol_handlers_audio.c",
    CORE / "pt_protocol_handlers_transfer.c",
    CORE / "pt_protocol_service.c",
    CORE / "pt_protocol_platform_adapter.c",
]
FIXTURE = ROOT / "tests/fixtures/pt_protocol_platform_adapter_host.c"


class PtProtocolPlatformAdapterTests(unittest.TestCase):
    def test_host_adapter_and_fail_closed_backend(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-platform-host-") as tmp:
            executable = Path(tmp) / "oracle"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", "-I", str(CORE), *map(str, SOURCES), str(FIXTURE),
                "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True)

    def test_strict_cortex_m0plus_compile(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-platform-target-") as tmp:
            objects = []
            for source in SOURCES:
                output = Path(tmp) / f"{source.stem}.o"
                subprocess.run([
                    "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                    "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(CORE), "-c", str(source), "-o", str(output),
                ], check=True, capture_output=True, text=True)
                objects.append(output)
            linked = Path(tmp) / "pt-platform.o"
            subprocess.run(["/opt/homebrew/opt/lld/bin/ld.lld", "-r", "-o", str(linked),
                            *map(str, objects)], check=True, capture_output=True, text=True)
            undefined = subprocess.run([
                "/opt/homebrew/opt/llvm/bin/llvm-nm", "-u", str(linked),
            ], check=True, capture_output=True, text=True).stdout.strip()
            self.assertEqual(undefined, "")


if __name__ == "__main__":
    unittest.main()
