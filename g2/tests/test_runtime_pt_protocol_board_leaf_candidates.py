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
LC3_SOURCE = (ROOT / "components/apollo_main/core_overlay" /
              "pt_protocol_lc3_setup.c")


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
        self.assertIn("open_cfw_pt_lc3_setup_encoder", text)
        self.assertIn("UINT32_C(0x80100000)", text)
        self.assertIn("UINT32_C(0x80700000)", text)
        self.assertNotIn("0x0058F209", text)
        self.assertNotIn("OPEN_CFW_PT_FONT_CRC_VALIDATE", text)
        self.assertIn("SPDX-License-Identifier: MIT", HEADER.read_text())

    def test_lc3_adaptation_has_a_separate_upstream_license_boundary(self) -> None:
        leaf = SOURCE.read_text()
        lc3 = LC3_SOURCE.read_text()
        self.assertNotRegex(
            leaf,
            r"(?m)^void\s*\*\s*open_cfw_pt_lc3_setup_encoder\s*\(",
        )
        self.assertNotIn("SPDX-License-Identifier: Apache-2.0", leaf)
        self.assertEqual(
            lc3.count("SPDX-License-Identifier: Apache-2.0"), 1
        )
        self.assertIn("Copyright 2022 Google LLC", lc3)
        self.assertIn("third_party/liblc3/src/lc3.c", lc3)
        self.assertIn(
            "96a3af0beb5487aca3b98a4b992a539a1f6d80d1", lc3
        )
        self.assertIn("../../../third_party/liblc3/LICENSE", lc3)
        self.assertRegex(
            lc3,
            r"(?m)^void\s*\*\s*open_cfw_pt_lc3_setup_encoder\s*\(",
        )
        self.assertRegex(
            lc3,
            r"(?m)^void\s*\*\s*open_cfw_pt_lc3_setup_encoder_bounded\s*\(",
        )
        self.assertIn("required > storage_capacity", lc3)
        self.assertIn("OPEN_CFW_PT_AUDIO_CODEC_SLOT_BYTES UINT32_C(0xA44)",
                      leaf)
        self.assertIn("OPEN_CFW_PT_AUDIO_CODEC_STORAGE_BYTES", leaf)
        self.assertIn("bytes[0] = (uint8_t)duration_index", lc3)
        self.assertIn("pcm_samples_4m = 192U", lc3)
        self.assertNotIn("words[0] = duration_index", lc3)


if __name__ == "__main__":
    unittest.main()
