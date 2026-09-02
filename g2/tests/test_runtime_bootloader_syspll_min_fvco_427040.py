"""Host semantic tests for the source-owned System PLL minimum-VCO route."""

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_min_fvco_427040.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_min_fvco_427040_host.c"


class BootloaderSyspllMinFvcoTests(unittest.TestCase):
    def test_source_is_reviewable_c(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("open_cfw_bootloader_syspll_min_fvco_427040", text)
        self.assertIn("open_cfw_bootloader_float_gcd_426d48", text)
        self.assertIn("open_cfw_bootloader_float_encoding_select_426f6c", text)
        self.assertIn("0x00431e70U", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)

    def test_host_minimum_vco_and_pfd_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-syspll-host-") as tmp:
            executable = Path(tmp) / "syspll-min-fvco"
            subprocess.run(
                [
                    "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-DOPEN_CFW_SYSPLL_HOST_TEST=1",
                    str(SOURCE), str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    unittest.main()
