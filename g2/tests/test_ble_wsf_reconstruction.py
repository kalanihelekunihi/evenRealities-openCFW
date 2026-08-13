import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "apollo_main" / "core_overlay"
FIXTURE = ROOT / "tests" / "fixtures"
SOURCES = [
    COMPONENT / "ble_wsf_task.c",
    COMPONENT / "ble_wsf_lifecycle.c",
    COMPONENT / "ble_wsf_flow.c",
]
EXPECTED_SYMBOLS = {
    "open_cfw_ble_wsf_task",
    "open_cfw_ble_wsf_start",
    "open_cfw_ble_wsf_resource_initialize",
    "open_cfw_ble_wsf_loop_initialize",
    "open_cfw_ble_wsf_enter",
    "open_cfw_ble_wsf_ready",
    "open_cfw_ble_wsf_initialize",
    "open_cfw_ble_wsf_deinitialize",
    "open_cfw_ble_wsf_take_tx_ready",
    "open_cfw_ble_wsf_wait_tx_ready",
    "open_cfw_ble_wsf_wait_once",
    "open_cfw_ble_wsf_tx_complete_notify",
}


class BleWsfReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"ble_wsf{suffix}"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O1",
                "-include",
                str(FIXTURE / "ble_wsf_host.h"),
                *map(str, SOURCES),
                str(FIXTURE / "ble_wsf_host.c"),
                "-o",
                str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_test_ble_wsf_reset.argtypes = []
        cls.loaded.open_cfw_ble_wsf_take_tx_ready.argtypes = [ctypes.c_ushort]
        cls.loaded.open_cfw_ble_wsf_take_tx_ready.restype = ctypes.c_uint
        cls.loaded.open_cfw_ble_wsf_wait_once.argtypes = [ctypes.c_ushort]
        cls.loaded.open_cfw_ble_wsf_wait_once.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_ble_wsf_reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def state(self):
        return (ctypes.c_uint * 6).in_dll(
            self.loaded, "open_cfw_test_ble_wsf_state_words"
        )

    def events(self):
        count = self.word("open_cfw_test_ble_wsf_event_count").value
        values = (ctypes.c_uint * 128).in_dll(
            self.loaded, "open_cfw_test_ble_wsf_events"
        )
        return list(values[:count])

    def initialize_resource(self) -> None:
        self.loaded.open_cfw_ble_wsf_resource_initialize()
        self.assertEqual(self.state()[5], 0x1234)

    def test_task_resource_and_lifecycle_contract(self) -> None:
        self.loaded.open_cfw_ble_wsf_task(None)
        self.assertEqual(
            self.events(),
            [
                0x15000009,
                0x10000101,
                0x30000101,
                0x11000000,
                0x13000000,
                0x16000009,
                0x14000000,
            ],
        )
        self.loaded.open_cfw_ble_wsf_initialize()
        self.assertEqual(self.state()[2], 0x5678)
        self.loaded.open_cfw_ble_wsf_deinitialize()
        self.assertEqual(self.state()[2], 0)
        self.assertEqual(self.events()[-2:], [0x12000000, 0x18005678])

    def test_take_and_bounded_wait_policy(self) -> None:
        self.assertEqual(self.loaded.open_cfw_ble_wsf_wait_once(0x12345), 0)
        self.initialize_resource()
        self.assertEqual(self.loaded.open_cfw_ble_wsf_wait_once(0x12345), 1)
        self.assertIn(0x20002345, self.events())

        self.word("open_cfw_test_ble_wsf_acquire_calls").value = 0
        self.word("open_cfw_test_ble_wsf_acquire_failures").value = 3
        self.word("open_cfw_test_ble_wsf_semaphore_value").value = 1
        self.loaded.open_cfw_ble_wsf_wait_tx_ready()
        self.assertEqual(self.word("open_cfw_test_ble_wsf_acquire_calls").value, 4)
        self.assertEqual(self.word("open_cfw_test_ble_wsf_tick").value, 20)
        self.assertIn(0x32001403, self.events())

        self.word("open_cfw_test_ble_wsf_acquire_calls").value = 0
        self.word("open_cfw_test_ble_wsf_acquire_failures").value = 100
        self.word("open_cfw_test_ble_wsf_semaphore_value").value = 1
        self.word("open_cfw_test_ble_wsf_tick").value = 0
        self.loaded.open_cfw_ble_wsf_wait_tx_ready()
        self.assertEqual(self.word("open_cfw_test_ble_wsf_acquire_calls").value, 21)
        self.assertEqual(self.word("open_cfw_test_ble_wsf_tick").value, 200)
        self.assertIn(0x31000000, self.events())
        self.assertIn(0x3200C814, self.events())

    def test_completion_credit_is_saturating(self) -> None:
        self.initialize_resource()
        self.loaded.open_cfw_ble_wsf_tx_complete_notify()
        self.assertEqual(self.word("open_cfw_test_ble_wsf_semaphore_value").value, 1)
        self.assertIn(0x34000001, self.events())

        self.word("open_cfw_test_ble_wsf_semaphore_value").value = 0
        self.loaded.open_cfw_ble_wsf_tx_complete_notify()
        self.assertEqual(self.word("open_cfw_test_ble_wsf_semaphore_value").value, 1)
        self.assertEqual(self.events()[-1], 0x22000000)

        self.word("open_cfw_test_ble_wsf_semaphore_value").value = 0
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_ble_wsf_release_result"
        ).value = -3
        self.loaded.open_cfw_ble_wsf_tx_complete_notify()
        self.assertEqual(self.word("open_cfw_test_ble_wsf_semaphore_value").value, 0)
        self.assertEqual(self.events()[-1], 0x3300FD00)

    def test_sources_compile_for_thumb_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            observed = set()
            for source in SOURCES:
                target = Path(directory) / f"{source.stem}.o"
                subprocess.run(
                    [
                        "clang",
                        "-target",
                        "thumbv7em-none-eabi",
                        "-mthumb",
                        "-O2",
                        "-ffreestanding",
                        "-fno-jump-tables",
                        "-fomit-frame-pointer",
                        "-fno-builtin",
                        "-mno-unaligned-access",
                        "-fno-unwind-tables",
                        "-fno-asynchronous-unwind-tables",
                        "-fropi",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                        "-c",
                        str(source),
                        "-o",
                        str(target),
                    ],
                    check=True,
                    cwd=ROOT,
                )
                symbols = subprocess.run(
                    ["nm", str(target)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                for line in symbols.splitlines():
                    fields = line.split()
                    if len(fields) == 3 and fields[1] == "T":
                        observed.add(fields[2])
            self.assertEqual(observed, EXPECTED_SYMBOLS)

    def test_source_hashes(self) -> None:
        expected = {
            "ble_wsf_flow.c": "76b8aedfc41b8bc759663700aa4428162299b4b9a241fa4e0ed6e7697e9717c3",
            "ble_wsf_lifecycle.c": "b64eca3f5494cbcdc54b0153c6b4cb159145ad36215e5c12e5e7010c7d314f02",
            "ble_wsf_task.c": "7fdb4351d3f8628a94e2e7fbca9fb08836fa1d8b3c2039c44df4ba5deb58ac35",
        }
        observed = {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in SOURCES
        }
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
