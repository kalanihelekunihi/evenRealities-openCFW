import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/system_monitor.c"
FIXTURE = ROOT / "tests/fixtures"
REBOOT = (ctypes.c_ubyte * 6)(0x55, 0x04, 0x12, 0x34, 0x56, 0x78)


class SystemMonitorCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / ("system_monitor" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "system_monitor_host.h"),
                str(SOURCE), str(FIXTURE / "system_monitor_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.handler = cls.loaded.open_cfw_system_monitor_common_data_handler
        cls.handler.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint]
        cls.handler.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def word(self, name):
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def reset(self, display=0, foreground=0, background=0, lens=0):
        self.loaded.open_cfw_test_system_monitor_reset(display, foreground, background, lens)

    def assert_reset_chain(self):
        self.assertEqual(self.word("open_cfw_test_system_monitor_dashboard_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_app_state_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_app_state_reason"), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_onboarding_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_terminal_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_lens_status_calls"), 1)

    def test_nonmatching_and_short_records_are_side_effect_free(self):
        for event, data, length in (
            (4, REBOOT, 6),
            (5, None, 0),
            (5, REBOOT, 5),
            (5, (ctypes.c_ubyte * 6)(0, 4, 0x12, 0x34, 0x56, 0x78), 6),
        ):
            with self.subTest(event=event, length=length):
                self.reset()
                self.assertEqual(self.handler(event, data, length), 0)
                self.assertEqual(self.word("open_cfw_test_system_monitor_dashboard_calls"), 0)
                self.assertEqual(self.word("open_cfw_test_system_monitor_command_calls"), 0)

    def test_reboot_quiesces_foreground_and_runs_complete_reset_chain(self):
        self.reset(display=3, foreground=1, lens=1)
        self.assertEqual(self.handler(5, REBOOT, 6), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_command_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_command_a"), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_command_b"), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_command_c"), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_delay_calls"), 2)
        self.assertEqual(self.word("open_cfw_test_system_monitor_delay_ticks"), 100)
        self.assertEqual(self.word("open_cfw_test_system_monitor_idle_calls"), 1)
        self.assert_reset_chain()

    def test_background_path_and_wait_are_bounded_to_eleven_delays(self):
        self.reset(display=100, background=1, lens=0)
        self.assertEqual(self.handler(5, REBOOT, 6), 0)
        self.assertEqual(self.word("open_cfw_test_system_monitor_command_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_system_monitor_delay_calls"), 11)
        self.assertEqual(self.word("open_cfw_test_system_monitor_idle_calls"), 0)
        self.assert_reset_chain()

    def test_thumb_object_exposes_one_text_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "system_monitor.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            text_symbols = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(text_symbols, {"open_cfw_system_monitor_common_data_handler"})


if __name__ == "__main__":
    unittest.main()
