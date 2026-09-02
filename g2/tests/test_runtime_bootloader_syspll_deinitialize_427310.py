# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_deinitialize_427310.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_deinitialize_427310_host.c"


class SyspllDeinitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-deinitialize.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_deinitialize_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_row6_destroy_427310.argtypes = [
            ctypes.c_void_p,
        ]
        cls.lib.open_cfw_bootloader_row6_destroy_427310.restype = ctypes.c_uint32
        for name in (
            "open_cfw_host_syspll_deinitialize_call",
            "open_cfw_host_syspll_deinitialize_prefix",
            "open_cfw_host_syspll_deinitialize_stop_calls",
            "open_cfw_host_syspll_deinitialize_power_query_calls",
            "open_cfw_host_syspll_deinitialize_power_disable_calls",
            "open_cfw_host_syspll_deinitialize_trace",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def reset(self, prefix: int, *, stop: int = 0, query: int = 0,
              disable: int = 0, powered: bool = False) -> None:
        self.lib.open_cfw_host_syspll_deinitialize_reset(
            prefix, stop, query, disable, int(powered))

    def test_invalid_handles_have_no_side_effects(self) -> None:
        self.reset(0xA1504C31, powered=True)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_destroy_427310(None), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_call(), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_prefix(),
                         0xA1504C31)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_stop_calls(), 0)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_query_calls(), 0)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_disable_calls(), 0)

    def test_disabled_unpowered_handle_clears_only_init(self) -> None:
        self.reset(0xA1504C30, query=17, disable=19)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_prefix(),
                         0xA0504C30)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_stop_calls(), 0)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_query_calls(), 1)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_disable_calls(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_trace(), 2)

    def test_enabled_powered_handle_propagates_stop_status_and_orders_calls(self) -> None:
        self.reset(0xA3504C30, stop=23, query=29, disable=31, powered=True)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_call(), 23)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_prefix(),
                         0xA2504C30)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_stop_calls(), 1)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_query_calls(), 1)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_deinitialize_power_disable_calls(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_deinitialize_trace(), 123)

    def test_source_is_reviewable_c_with_authenticated_edges(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("am_hal_syspll_deinitialize", text)
        self.assertIn("open_cfw_bootloader_row6_stop_4273dc", text)
        self.assertIn("open_cfw_bootloader_pwrctrl_syspll_enabled_41cae8", text)
        self.assertIn("open_cfw_bootloader_pwrctrl_syspll_disable_41caa2", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
