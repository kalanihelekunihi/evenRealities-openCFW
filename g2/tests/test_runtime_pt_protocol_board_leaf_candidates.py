# SPDX-License-Identifier: MIT
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/pt_protocol_board_leaf_candidates_host.c"
SOURCE = (ROOT / "components/apollo_main/core_overlay" /
          "pt_protocol_board_leaf_candidates.c")
HEADER = (ROOT / "components/apollo_main/core_overlay" /
          "pt_protocol_board_leaf_candidates.h")


class PtProtocolBoardLeafCandidateTests(unittest.TestCase):
    def test_host_semantics(self) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="g2-pt-board-leaves-") as tmp:
            executable = Path(tmp) / "fixture"
            subprocess.run([
                compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE), "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True)

    def test_target_source_is_semantic_c(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".inst", text)
        self.assertIn("open_cfw_pt_board_ambient_read", text)
        self.assertIn("open_cfw_pt_board_production_reset", text)
        self.assertIn("open_cfw_pt_font_crc_validate", text)
        self.assertIn("UINT32_C(0x80100000)", text)
        self.assertIn("UINT32_C(0x80700000)", text)
        self.assertNotIn("0x0058F209", text)
        self.assertNotIn("OPEN_CFW_PT_FONT_CRC_VALIDATE", text)
        self.assertIn("SPDX-License-Identifier: MIT", HEADER.read_text())


if __name__ == "__main__":
    unittest.main()
