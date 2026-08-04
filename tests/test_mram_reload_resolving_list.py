from __future__ import annotations

import os

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mram_reload_resolving_list.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_reload_resolving_list_host.c"
)
CAPTURE_COUNT = 32


class MramReloadResolvingListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_reload_resolving_list.dylib"
            if sys.platform == "darwin"
            else "mram_reload_resolving_list.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_mram_reload_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.reload = cls.loaded.open_cfw_mram_reload_resolving_list
        cls.reload.argtypes = []
        cls.reload.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_ulong * count).in_dll(self.loaded, name)

    def order(self) -> list[int]:
        count = self.word("open_cfw_test_mram_reload_order_count").value
        return list(
            self.words(
                "open_cfw_test_mram_reload_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def test_full_diagnostics_and_reload_order(self) -> None:
        self.word("open_cfw_test_mram_reload_level_default").value = 7

        self.reload()

        self.assertEqual(
            self.order(),
            [1, 2, 1, 3, 4, 5, 1, 2, 1, 3],
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_reload_request_count").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_reload_sync_count").value,
            1,
        )
        logs = self.addresses(
            "open_cfw_test_mram_reload_logs",
            CAPTURE_COUNT * 6,
        )
        self.assertEqual(
            list(logs[:12]),
            [
                4, 0x0078A0D0, 0x006D84BC,
                0x007693F8, 0x706, 0x0071276C,
                4, 0x0078A0D0, 0x006D84BC,
                0x007693F8, 0x70E, 0x00726E24,
            ],
        )
        traces = self.addresses(
            "open_cfw_test_mram_reload_traces",
            CAPTURE_COUNT * 3,
        )
        self.assertEqual(
            list(traces[:6]),
            [
                0x10000000, 0x006F8564, 0x006F8564,
                0x10000000, 0x00709324, 0x00709324,
            ],
        )

    def test_structured_logging_does_not_imply_trace(self) -> None:
        self.word("open_cfw_test_mram_reload_level_default").value = 2

        self.reload()

        self.assertEqual(
            self.word("open_cfw_test_mram_reload_log_count").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_reload_trace_count").value,
            0,
        )
        self.assertEqual(
            self.order(),
            [1, 2, 1, 1, 4, 5, 1, 2, 1, 1],
        )

    def test_trace_primary_gate_skips_fallback_read(self) -> None:
        self.word("open_cfw_test_mram_reload_level_default").value = 1

        self.reload()

        self.assertEqual(
            self.word("open_cfw_test_mram_reload_log_count").value,
            0,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_reload_trace_count").value,
            2,
        )
        self.assertEqual(
            self.order(),
            [1, 1, 3, 4, 5, 1, 1, 3],
        )

    def test_trace_fallback_gate_uses_second_level_read(self) -> None:
        self.word("open_cfw_test_mram_reload_level_default").value = 4

        self.reload()

        self.assertEqual(
            self.word("open_cfw_test_mram_reload_log_count").value,
            0,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_reload_trace_count").value,
            2,
        )
        self.assertEqual(
            self.order(),
            [1, 1, 1, 3, 4, 5, 1, 1, 1, 3],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "329a524e1daadb7a7f65ca07cb3c49fdb1270e8cf40526be6da856fca4023e93",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "cd991e486b3559fc467bc21c9004d496d8a2f14f0ff336066d049112bd65ead5",
        )


if __name__ == "__main__":
    unittest.main()
