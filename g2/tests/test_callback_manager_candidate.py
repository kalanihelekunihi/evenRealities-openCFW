from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/callback_manager.c"
FIXTURES = ROOT / "tests/fixtures"


class Node(ctypes.Structure):
    pass


Node._fields_ = [("callback", ctypes.c_size_t), ("next", ctypes.POINTER(Node))]


class Manager(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.POINTER(Node)),
        ("count", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
        ("type", ctypes.c_char_p),
    ]


class CallbackManagerCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("callback_manager" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-Wall", "-Wextra", "-Werror", "-include",
                str(FIXTURES / "callback_manager_host.h"), str(SOURCE),
                str(FIXTURES / "callback_manager_host.c"), "-o", str(library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_callback_mgr_init.argtypes = [ctypes.POINTER(Manager), ctypes.c_char_p]
        cls.lib.open_cfw_callback_mgr_init.restype = ctypes.c_uint32
        cls.lib.open_cfw_callback_mgr_deinit.argtypes = [ctypes.POINTER(Manager)]
        cls.lib.open_cfw_callback_mgr_register.argtypes = [ctypes.POINTER(Manager), ctypes.c_size_t]
        cls.lib.open_cfw_callback_mgr_register.restype = ctypes.c_uint32
        cls.lib.open_cfw_callback_mgr_unregister.argtypes = [ctypes.POINTER(Manager), ctypes.c_size_t]
        cls.lib.open_cfw_callback_mgr_is_registered.argtypes = [ctypes.POINTER(Manager), ctypes.c_size_t]
        cls.lib.open_cfw_callback_mgr_is_registered.restype = ctypes.c_uint32
        cls.lib.open_cfw_callback_mgr_notify.argtypes = [ctypes.POINTER(Manager), ctypes.c_uint32, ctypes.c_size_t]
        cls.lib.open_cfw_test_callback_host_fail_alloc.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_callback_host_word.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_callback_host_word.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.open_cfw_test_callback_host_reset()
        self.manager = Manager()
        self.assertEqual(self.lib.open_cfw_callback_mgr_init(ctypes.byref(self.manager), b"TEST"), 1)

    def address(self, symbol):
        return ctypes.cast(getattr(self.lib, symbol), ctypes.c_void_p).value

    def word(self, index):
        return self.lib.open_cfw_test_callback_host_word(index)

    def test_init_validation_and_layout_state(self):
        self.assertEqual(self.lib.open_cfw_callback_mgr_init(None, b"BAD"), 0)
        self.assertFalse(self.manager.head)
        self.assertEqual(self.manager.count, 0)
        self.assertEqual(self.manager.type, b"TEST")

    def test_registration_is_prepend_duplicate_safe_and_null_checked(self):
        one = self.address("open_cfw_test_callback_one")
        two = self.address("open_cfw_test_callback_two")
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(None, one), 0)
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), 0), 0)
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one), 1)
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one), 1)
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), two), 1)
        self.assertEqual((self.manager.count, self.word(0)), (2, 2))
        self.assertEqual(self.manager.head.contents.callback, two)
        self.assertEqual(self.manager.head.contents.next.contents.callback, one)

    def test_allocation_failure_is_reported_without_state_change(self):
        self.lib.open_cfw_test_callback_host_fail_alloc(1)
        one = self.address("open_cfw_test_callback_one")
        self.assertEqual(self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one), 0)
        self.assertFalse(self.manager.head)
        self.assertEqual((self.manager.count, self.word(0)), (0, 0))

    def test_unregister_handles_head_interior_and_miss(self):
        one = self.address("open_cfw_test_callback_one")
        two = self.address("open_cfw_test_callback_two")
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one)
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), two)
        self.lib.open_cfw_callback_mgr_unregister(ctypes.byref(self.manager), one)
        self.assertEqual((self.manager.count, self.word(1)), (1, 1))
        self.assertEqual(self.lib.open_cfw_callback_mgr_is_registered(ctypes.byref(self.manager), one), 0)
        self.lib.open_cfw_callback_mgr_unregister(ctypes.byref(self.manager), one)
        self.lib.open_cfw_callback_mgr_unregister(ctypes.byref(self.manager), two)
        self.assertEqual((self.manager.count, self.word(1)), (0, 2))
        self.assertFalse(self.manager.head)

    def test_notify_uses_prepend_order_and_forwards_both_arguments(self):
        one = self.address("open_cfw_test_callback_one")
        two = self.address("open_cfw_test_callback_two")
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one)
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), two)
        self.lib.open_cfw_callback_mgr_notify(ctypes.byref(self.manager), 7, 0x1234)
        self.assertEqual(
            tuple(self.word(i) for i in range(2, 7)),
            (4, 0x20000007, 0x1234, 0x10000007, 0x1234),
        )

    def test_deinit_frees_every_node_and_preserves_type(self):
        one = self.address("open_cfw_test_callback_one")
        two = self.address("open_cfw_test_callback_two")
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), one)
        self.lib.open_cfw_callback_mgr_register(ctypes.byref(self.manager), two)
        self.lib.open_cfw_callback_mgr_deinit(ctypes.byref(self.manager))
        self.assertFalse(self.manager.head)
        self.assertEqual((self.manager.count, self.manager.type, self.word(1)), (0, b"TEST", 2))

    def test_selector_builds_are_single_function(self):
        selectors = {
            "CREATE": "open_cfw_callback_mgr_create",
            "DELETE": "open_cfw_callback_mgr_delete",
            "INIT": "open_cfw_callback_mgr_init",
            "DEINIT": "open_cfw_callback_mgr_deinit",
            "IS_REGISTERED": "open_cfw_callback_mgr_is_registered",
            "REGISTER": "open_cfw_callback_mgr_register",
            "UNREGISTER": "open_cfw_callback_mgr_unregister",
            "NOTIFY": "open_cfw_callback_mgr_notify",
        }
        flags = [
            "-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
            "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
            "-mno-unaligned-access", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
            "-fdata-sections", "-Wall", "-Wextra", "-Werror",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run(
                    ["clang", *flags, f"-DOPEN_CFW_CALLBACK_MGR_{selector}_ONLY=1",
                     "-c", str(SOURCE), "-o", str(obj)],
                    check=True,
                    cwd=ROOT,
                )
                output = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                text_symbols = {
                    fields[2] for line in output.splitlines()
                    if len(fields := line.split()) == 3 and fields[1] == "T"
                }
                self.assertEqual(text_symbols, {symbol})


if __name__ == "__main__":
    unittest.main()
