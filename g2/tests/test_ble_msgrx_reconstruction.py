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
SOURCE_HASHES = {
    "ble_msgrx_dispatch.c": "b9b7663b54d889ac123d12ad440358e807ea445c8e6b4abfae6fd0f6fbd25e26",
    "ble_msgrx_enqueue.c": "a1f69270a03e1065790fa2fc9ff096fe97c359e11562f256d828af0ac71b2d74",
    "ble_msgrx_lifecycle.c": "e3fcdd7561a6ef1a24dbd7c12e74bd3106ba3ffb1748ee927c67d232b4575bab",
    "ble_msgrx_runtime.c": "c21a203a2ff0b853c4011a5d8f76a7969416f4184e55571e0cdbea9e59ebba26",
    "ble_msgrx_thread.c": "f2780d00b5fff63cedc7948465fba5a0f78b7cec5d85d6e264cc89adb0da0267",
}


class BleMsgRxReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"ble_msgrx{suffix}"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O1",
                "-include",
                str(FIXTURE / "ble_msgrx_host.h"),
                str(COMPONENT / "ble_msgrx_thread.c"),
                str(COMPONENT / "ble_msgrx_runtime.c"),
                str(COMPONENT / "ble_msgrx_lifecycle.c"),
                str(COMPONENT / "ble_msgrx_dispatch.c"),
                str(COMPONENT / "ble_msgrx_enqueue.c"),
                str(FIXTURE / "ble_msgrx_host.c"),
                "-o",
                str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_test_ble_msgrx_reset.argtypes = []
        cls.loaded.open_cfw_ble_msgrx_enqueue.argtypes = [
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_ushort,
        ]
        cls.loaded.open_cfw_ble_msgrx_enqueue.restype = ctypes.c_uint
        cls.loaded.open_cfw_ble_msgrx_queue_drain.argtypes = []
        cls.loaded.open_cfw_ble_msgrx_queue_clear.argtypes = []
        cls.loaded.open_cfw_ble_msgrx_queue_clear.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_ble_msgrx_reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def state(self):
        return (ctypes.c_uint * 4).in_dll(
            self.loaded, "open_cfw_test_ble_msgrx_state_words"
        )

    def events(self):
        count = self.word("open_cfw_test_ble_msgrx_event_count").value
        values = (ctypes.c_uint * 128).in_dll(
            self.loaded, "open_cfw_test_ble_msgrx_events"
        )
        return list(values[:count])

    def initialize_queue(self) -> None:
        self.loaded.open_cfw_ble_msgrx_queue_initialize()
        self.assertEqual(self.state()[3], 1)

    def enqueue(self, kind: int, payload: bytes) -> int:
        buffer = ctypes.create_string_buffer(payload)
        return self.loaded.open_cfw_ble_msgrx_enqueue(
            kind, ctypes.cast(buffer, ctypes.c_void_p), len(payload)
        )

    def test_queue_and_lifecycle_contract(self) -> None:
        self.initialize_queue()
        self.assertEqual(self.events()[:2], [0x10000096, 4])
        self.loaded.open_cfw_ble_msgrx_stage_enter()
        self.loaded.open_cfw_ble_msgrx_stage_ready()
        self.loaded.open_cfw_ble_msgrx_thread_create()
        self.assertEqual(self.state()[2], 2)
        self.loaded.open_cfw_ble_msgrx_thread_destroy()
        self.assertEqual(self.state()[2], 0)
        self.assertIn(0x20000007, self.events())
        self.assertIn(0x21000007, self.events())
        self.assertIn(0x23000002, self.events())

    def test_enqueue_record_shape_and_failure_paths(self) -> None:
        payload = b"abcde"
        self.assertEqual(self.enqueue(0xC2, payload), 0xFFFFFFFF)
        self.initialize_queue()
        self.state()[2] = 9
        self.assertEqual(self.enqueue(0xC2, payload), 0)
        self.assertEqual(self.word("open_cfw_test_ble_msgrx_last_allocation").value, 16)
        self.assertEqual(self.word("open_cfw_test_ble_msgrx_last_timeout").value, 500)
        self.assertEqual(self.word("open_cfw_test_ble_msgrx_last_flag").value, 0x400000)

        self.word("open_cfw_test_ble_msgrx_queue_put_result").value = 3
        self.assertEqual(self.enqueue(0x80, payload), 0xFFFFFFFF)
        self.assertEqual(self.events()[-1], 0x30000000)

    def test_all_receive_routes_and_freeing(self) -> None:
        self.initialize_queue()
        self.state()[2] = 9
        payload = bytes(range(16))
        kinds = [0x80, 0xC0, 0xC3, 0xC4, 0xC7, 0x200, 0x400, 0x999]
        for kind in kinds:
            self.assertEqual(self.enqueue(kind, payload), 0)
        self.loaded.open_cfw_ble_msgrx_queue_drain()
        events = self.events()
        self.assertIn(0x80, events)
        self.assertEqual(events.count(0xC0), 2)
        self.assertEqual(events.count(0xC4), 2)
        self.assertIn(0xD00, events)
        self.assertIn(0x200, events)
        self.assertIn(0x400, events)
        self.assertEqual(events.count(0x30000000), len(kinds))

    def test_queue_clear_and_thread_entry(self) -> None:
        self.initialize_queue()
        self.state()[2] = 9
        self.assertEqual(self.enqueue(0x80, b"one"), 0)
        self.assertEqual(self.enqueue(0x80, b"two"), 0)
        self.assertEqual(self.loaded.open_cfw_ble_msgrx_queue_clear(), 2)
        self.loaded.open_cfw_ble_msgrx_thread(None)

    def test_sources_compile_for_thumb_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            expected = {
                "open_cfw_ble_msgrx_thread",
                "open_cfw_ble_msgrx_application_initialize",
                "open_cfw_ble_msgrx_queue_initialize",
                "open_cfw_ble_msgrx_thread_initialize",
                "open_cfw_ble_msgrx_stage_enter",
                "open_cfw_ble_msgrx_stage_ready",
                "open_cfw_ble_msgrx_thread_create",
                "open_cfw_ble_msgrx_thread_destroy",
                "open_cfw_ble_msgrx_queue_drain",
                "open_cfw_ble_msgrx_dispatch_flags",
                "open_cfw_ble_msgrx_exit",
                "open_cfw_ble_msgrx_queue_clear",
                "open_cfw_ble_msgrx_enqueue",
            }
            observed = set()
            for source in sorted(COMPONENT.glob("ble_msgrx_*.c")):
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
            self.assertEqual(observed, expected)

    def test_source_hashes(self) -> None:
        observed = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(COMPONENT.glob("ble_msgrx_*.c"))
        }
        self.assertEqual(observed, SOURCE_HASHES)


if __name__ == "__main__":
    unittest.main()
