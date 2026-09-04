import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ServiceAlgoRuntimeTests(unittest.TestCase):
    def test_host_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "service_algo_host"
            subprocess.run(
                [
                    "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(ROOT / "tests/fixtures/service_algo_host.c"),
                    "-o", str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(output)], check=True)

    def test_freestanding_arm_compile(self):
        source = ROOT / "components/apollo_main/core_overlay/service_algo.c"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "service_algo.o"
            subprocess.run(
                [
                    "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                    "-mthumb", "-mcpu=cortex-m55", "-mfloat-abi=hard",
                    "-mfpu=fpv5-d16", "-O2", "-ffreestanding", "-fno-builtin",
                    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source),
                    "-o", str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
