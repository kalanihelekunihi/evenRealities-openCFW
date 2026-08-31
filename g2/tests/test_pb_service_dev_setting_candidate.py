import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_dev_setting.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_dev_setting_host.c"
SOURCE_SIZE = 15553
SOURCE_SHA256 = "eb006e7d29ca56b031faa28d3aad5425d7ca463219e855fd9a7d827f7cd5b850"
SELECTORS = (
    "BUFFER_WRITE", "TRANSMIT", "RX_RESTORE", "TX_RESTORE", "RX_RESTART",
    "TX_RESTART", "RX_HEARTBEAT", "TX_HEARTBEAT", "RX_TIME", "TX_TIME",
    "RX_AUDIO", "TX_AUDIO",
)


class PbServiceDevSettingCandidateTests(unittest.TestCase):
    def test_source_pin(self) -> None:
        raw = SOURCE.read_bytes()
        self.assertEqual(len(raw), SOURCE_SIZE)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)

    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "pb_service_dev_setting_host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE), "-o", str(binary),
            ], cwd=ROOT, check=True)
            subprocess.run([str(binary)], check=True)

    def test_selector_builds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector in SELECTORS:
                output = Path(directory) / f"{selector}.o"
                subprocess.run([
                    "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-Oz", "-ffreestanding",
                    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                    "-Wall", "-Wextra", "-Werror",
                    f"-DOPEN_CFW_PB_DEV_SETTING_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(output),
                ], cwd=ROOT, check=True)


if __name__ == "__main__":
    unittest.main()
