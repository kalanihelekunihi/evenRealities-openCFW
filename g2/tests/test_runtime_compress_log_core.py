import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompressLogCoreRuntimeTests(unittest.TestCase):
    def test_host_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "compress_log_core_host"
            subprocess.run(
                [
                    "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    str(ROOT / "tests/fixtures/compress_log_core_host.c"),
                    "-o", str(output),
                ],
                check=True,
                cwd=ROOT,
            )
            subprocess.run([str(output)], check=True, cwd=ROOT)

    def test_freestanding_arm_compile(self):
        source = ROOT / "components/apollo_main/core_overlay/compress_log_core.c"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "compress_log_core.o"
            subprocess.run(
                [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror", "-c", str(source), "-o",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
            )
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
