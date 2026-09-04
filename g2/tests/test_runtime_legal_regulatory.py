"""Runtime and target-compile tests for the legal/regulatory event policy."""

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/legal_regulatory.c"
FIXTURE = ROOT / "tests/fixtures"


class Event(ctypes.Structure):
    _fields_ = [("action", ctypes.c_uint32), ("scroll_delta", ctypes.c_int32)]


class LegalRegulatoryRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temporary.name) / ("legal_regulatory" + suffix)
        subprocess.run([
            "clang", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
            "-include", str(FIXTURE / "legal_regulatory_host.h"), str(SOURCE),
            str(FIXTURE / "legal_regulatory_host.c"), "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_legal_reset.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_legal_regulatory_ui_event_handler.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(Event), ctypes.c_uint32, ctypes.c_size_t,
        ]
        cls.lib.open_cfw_legal_regulatory_ui_event_handler.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def u32(self, name):
        return ctypes.c_uint32.in_dll(self.lib, name).value

    def uptr(self, name):
        return ctypes.c_size_t.in_dll(self.lib, name).value

    def invoke(self, event_id, event=None, context=0x3344):
        self.lib.open_cfw_test_legal_reset(0x1122)
        pointer = ctypes.pointer(event) if event is not None else None
        return self.lib.open_cfw_legal_regulatory_ui_event_handler(
            event_id, pointer, 8 if event is not None else 0, context)

    def test_startup_constructs_and_animates_active_root(self):
        self.assertEqual(self.invoke(2), 0)
        self.assertEqual(self.u32("open_cfw_test_legal_page_calls"), 1)
        self.assertEqual(self.uptr("open_cfw_test_legal_page_context"), 0x3344)
        self.assertEqual(self.uptr("open_cfw_test_legal_animation_object"), 0x1122)
        self.assertEqual(self.u32("open_cfw_test_legal_animate_calls"), 1)
        self.assertEqual(self.uptr("open_cfw_test_legal_animate_object"), 0x1122)
        self.assertEqual(self.u32("open_cfw_test_legal_animate_duration"), 250)
        self.assertEqual(self.u32("open_cfw_test_legal_animate_delay"), 0)

    def test_scroll_action_forwards_signed_delta(self):
        self.assertEqual(self.invoke(3, Event(1, -73)), 0)
        self.assertEqual(self.u32("open_cfw_test_legal_scroll_calls"), 1)
        self.assertEqual(self.uptr("open_cfw_test_legal_scroll_object"), 0x1122)
        self.assertEqual(ctypes.c_int32.in_dll(
            self.lib, "open_cfw_test_legal_scroll_delta").value, -73)
        self.assertEqual(self.u32("open_cfw_test_legal_scroll_animated"), 1)

    def test_other_actions_events_and_null_payload_are_noop(self):
        for event_id, event in ((3, Event(0, 9)), (3, None), (4, None), (5, None), (99, None)):
            with self.subTest(event_id=event_id, event=event):
                self.assertEqual(self.invoke(event_id, event), 0)
                self.assertEqual(self.u32("open_cfw_test_legal_scroll_calls"), 0)
                self.assertEqual(self.u32("open_cfw_test_legal_animate_calls"), 0)

    def test_target_compiles_as_freestanding_c(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "legal_regulatory.o"
            subprocess.run([
                "clang", "--target=thumbv7em-none-eabi", "-mthumb", "-mcpu=cortex-m55",
                "-O2", "-ffreestanding", "-fno-builtin", "-fno-jump-tables",
                "-fomit-frame-pointer", "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
                "-enable-machine-outliner=never", "-c", str(SOURCE), "-o", str(output),
            ], check=True)
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
