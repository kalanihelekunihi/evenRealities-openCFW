#!/usr/bin/env python3

from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_update_indices_427754.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_cmdq_update_indices_427754_host.c"


class BootloaderCmdqUpdateIndicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-cmdq-update-")
        library = Path(cls.temporary.name) / "cmdq-update.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            check=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.reset = cls.library.open_cfw_cmdq_host_reset
        cls.reset.argtypes = [ctypes.c_uint32] * 4
        cls.execute = cls.library.open_cfw_cmdq_host_run
        cls.getters = {}
        for suffix in ("head", "current", "save_calls", "restore_calls",
                       "restored_token", "order"):
            function = getattr(cls.library, "open_cfw_cmdq_host_" + suffix)
            function.restype = ctypes.c_uint32
            cls.getters[suffix] = function

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, end_index: int, hardware_index: int,
                 queue_address: int) -> dict[str, int]:
        self.reset(0xA5A55A5A, end_index, hardware_index, queue_address)
        self.execute()
        return {name: function() for name, function in self.getters.items()}

    def test_same_epoch_index_and_head_snapshot(self) -> None:
        result = self.run_case(0x123456E0, 0xABCD34D0, 0x20001000)
        self.assertEqual(result["current"], 0x123456D0)
        self.assertEqual(result["head"], 0x20001000)

    def test_hardware_wrap_selects_previous_epoch(self) -> None:
        result = self.run_case(0x00000210, 0x000000F0, 0x20002000)
        self.assertEqual(result["current"], 0x000001F0)

    def test_hardware_index_is_limited_to_eight_bits(self) -> None:
        result = self.run_case(0x010203C0, 0xDEADBEB0, 0x20003000)
        self.assertEqual(result["current"], 0x010203B0)

    def test_critical_token_is_restored_after_updates(self) -> None:
        result = self.run_case(0x100, 0x80, 0x20004000)
        self.assertEqual(result["save_calls"], 1)
        self.assertEqual(result["restore_calls"], 1)
        self.assertEqual(result["restored_token"], 0xA5A55A5A)
        self.assertEqual(result["order"], 12)

    def test_source_is_reviewable_compilable_c(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("open_cfw_bootloader_cmdq_update_indices_427754", text)
        self.assertIn("queue->end_index & ~0xFFU", text)
        self.assertIn("queue->current_index -= 0x100U", text)
        self.assertIn("msr primask, %0", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
