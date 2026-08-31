import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "apollo_main" / "core_overlay"
FIXTURE = ROOT / "tests" / "fixtures"
SOURCES = [
    COMPONENT / "app_ble_callbacks.c",
    COMPONENT / "app_ble_handler.c",
    COMPONENT / "app_ble_processor.c",
    COMPONENT / "app_ble_startup.c",
]
EXPECTED_SYMBOLS = {
    "open_cfw_app_ble_subsystem_initialize",
    "open_cfw_app_ble_dm_callback",
    "open_cfw_app_ble_att_callback",
    "open_cfw_app_ble_ccc_callback",
    "open_cfw_app_ble_delayed_start_callback",
    "open_cfw_app_ble_handler",
    "open_cfw_app_ble_process_message",
    "open_cfw_app_ble_handler_initialize",
    "open_cfw_app_ble_stack_register",
    "open_cfw_app_ble_stack_initialize",
    "open_cfw_app_ble_address_get",
    "open_cfw_app_ble_start",
}


class AppBleCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"app_ble{suffix}"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O1",
                "-include",
                str(FIXTURE / "app_ble_host.h"),
                *map(str, SOURCES),
                str(FIXTURE / "app_ble_host.c"),
                "-o",
                str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_test_app_ble_reset.argtypes = []
        cls.loaded.open_cfw_app_ble_dm_callback.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_att_callback.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_ccc_callback.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_delayed_start_callback.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_handler_initialize.argtypes = [ctypes.c_uint]
        cls.loaded.open_cfw_app_ble_handler.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_process_message.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_app_ble_address_get.restype = ctypes.POINTER(ctypes.c_ubyte)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_app_ble_reset()

    def u32(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def addresses(self):
        count = self.u32("open_cfw_test_app_ble_event_count").value
        values = (ctypes.c_uint * 256).in_dll(
            self.loaded, "open_cfw_test_app_ble_event_address"
        )
        return list(values[:count])

    def arguments(self, ordinal: int):
        count = self.u32("open_cfw_test_app_ble_event_count").value
        self.assertLess(ordinal, count)
        result = []
        for suffix in ("argument0", "argument1", "argument2"):
            values = (ctypes.c_size_t * 256).in_dll(
                self.loaded, f"open_cfw_test_app_ble_event_{suffix}"
            )
            result.append(values[ordinal])
        return tuple(result)

    def control(self):
        return (ctypes.c_ubyte * 128).in_dll(
            self.loaded, "open_cfw_test_app_ble_control"
        )

    def last_message(self):
        size = self.u32("open_cfw_test_app_ble_last_message_size").value
        value = (ctypes.c_ubyte * 256).in_dll(
            self.loaded, "open_cfw_test_app_ble_last_message"
        )
        return bytes(value[:size])

    def set_input_payload(self, value: bytes):
        buffer = ctypes.create_string_buffer(value)
        ctypes.c_void_p.in_dll(
            self.loaded, "open_cfw_test_app_ble_input_payload"
        ).value = ctypes.addressof(buffer)
        return buffer

    def process_message(
        self,
        event: int,
        connection: int = 0,
        status: int = 0,
        extra: bytes = b"",
    ):
        message = (ctypes.c_ubyte * max(16, 4 + len(extra)))()
        message[0:2] = connection.to_bytes(2, "little")
        message[2] = event
        message[3] = status
        message[4:4 + len(extra)] = extra
        self.loaded.open_cfw_app_ble_process_message(message)
        return message

    def test_subsystem_and_event_copy_callbacks(self) -> None:
        self.control()[0x56] = 0x44
        self.loaded.open_cfw_app_ble_subsystem_initialize()
        self.assertEqual(
            self.addresses(),
            [0x503B76, 0x4B3C02, 0x534866, 0x532E52],
        )

        self.loaded.open_cfw_test_app_ble_reset()
        self.control()[0x56] = 0x44
        dm_payload = self.set_input_payload(b"xyz")
        dm_event = (ctypes.c_ubyte * 12)()
        dm_event[2] = 0x26
        dm_event[8] = 3
        self.loaded.open_cfw_app_ble_dm_callback(dm_event)
        self.assertEqual(self.u32("open_cfw_test_app_ble_last_allocation").value, 15)
        self.assertEqual(self.u32("open_cfw_test_app_ble_last_handler").value, 0x44)
        self.assertEqual(self.last_message()[12:15], b"xyz")
        self.assertEqual(bytes(dm_payload.raw[:3]), b"xyz")

        att_payload = self.set_input_payload(b"data")
        att_event = (ctypes.c_ubyte * 16)()
        att_event[8:10] = (4).to_bytes(2, "little")
        self.loaded.open_cfw_app_ble_att_callback(att_event)
        self.assertEqual(self.u32("open_cfw_test_app_ble_last_allocation").value, 20)
        self.assertEqual(self.last_message()[16:20], b"data")
        self.assertEqual(bytes(att_payload.raw[:4]), b"data")

    def test_ccc_and_delayed_start_callbacks(self) -> None:
        self.control()[0x56] = 7
        event = bytearray(10)
        struct.pack_into("<H", event, 0, 2)
        struct.pack_into("<H", event, 4, 0x123)
        struct.pack_into("<H", event, 6, 0x55)
        event[8] = 9
        buffer = ctypes.create_string_buffer(bytes(event))
        self.loaded.open_cfw_app_ble_ccc_callback(buffer)
        self.assertEqual(self.u32("open_cfw_test_app_ble_ccc_index").value, 9)
        self.assertEqual(self.u32("open_cfw_test_app_ble_ccc_value").value, 0x55)
        self.assertEqual(self.last_message(), bytes(event))

        self.loaded.open_cfw_test_app_ble_reset()
        self.loaded.open_cfw_app_ble_delayed_start_callback(None)
        self.assertEqual(self.last_message()[2], 0xBC)
        self.assertEqual(self.addresses(), [0x476ACE, 0x47697E])
        self.assertEqual(self.arguments(1)[2], 10000)

        self.loaded.open_cfw_test_app_ble_reset()
        self.u32("open_cfw_test_app_ble_allocate_fail").value = 1
        self.loaded.open_cfw_app_ble_delayed_start_callback(None)
        self.assertEqual(self.addresses(), [0x476ACE, 0x47697E])
        self.assertEqual(self.arguments(1)[2], 20000)

    def test_handler_configuration_and_registration_order(self) -> None:
        self.loaded.open_cfw_app_ble_handler_initialize(0x123)
        self.assertEqual(self.control()[0x56], 0x23)
        self.assertEqual(self.u32("open_cfw_test_app_ble_smp_config").value, 0x774D44)
        self.assertEqual(self.u32("open_cfw_test_app_ble_app_config").value, 0x78C9A4)
        runtime = (ctypes.c_ubyte * 16).in_dll(
            self.loaded, "open_cfw_test_app_ble_runtime_state"
        )
        self.assertEqual(runtime[0], 4)
        self.assertEqual(
            self.addresses(),
            [0x46ED94, 0x535488, 0x4A19F4, 0x503B76, 0x4B3C02, 0x534866, 0x532E52],
        )

        self.loaded.open_cfw_test_app_ble_reset()
        self.loaded.open_cfw_app_ble_stack_register()
        self.assertEqual(
            self.addresses(),
            [
                0x4D29CE, 0x4B6C64, 0x4B519E, 0x4B51C8, 0x52C224,
                0x532E7C, 0x52DC1C, 0x52DBF0, 0x53618C, 0x5361C6,
                0x5361BC, 0x5361DE, 0x5361D4, 0x5361F6, 0x5361EC,
                0x53620E, 0x536204, 0x536226, 0x53621C, 0x4B5A3A,
            ],
        )

    def test_registered_handler_routing(self) -> None:
        message = (ctypes.c_ubyte * 16)()
        message[2] = 2
        self.loaded.open_cfw_app_ble_handler(0x145, message)
        self.assertEqual(
            self.addresses(),
            [0x532924, 0x53484C, 0x46EF74, 0x4A19C0],
        )
        self.assertEqual(self.arguments(3)[0], 0x45)

        self.loaded.open_cfw_test_app_ble_reset()
        message[0:2] = (4).to_bytes(2, "little")
        message[2] = 0x21
        self.u32("open_cfw_test_app_ble_connection_role").value = 0
        self.loaded.open_cfw_app_ble_handler(7, message)
        self.assertEqual(
            self.addresses(),
            [
                0x4B73C4, 0xD1000000, 0x503B92, 0x503C32, 0x5322BC,
                0x46EF74, 0x4A19C0,
            ],
        )

        self.loaded.open_cfw_test_app_ble_reset()
        message[2] = 0x22
        self.u32("open_cfw_test_app_ble_connection_role").value = 1
        self.u32("open_cfw_test_app_ble_ring_connection").value = 1
        self.loaded.open_cfw_app_ble_handler(7, message)
        self.assertEqual(
            self.addresses(),
            [
                0x4B73C4, 0xD1000000, 0x46EF60, 0x4B45B0, 0x5322BC,
                0x46EF74, 0x4A19C0,
            ],
        )

    def test_message_processor_notification_and_connection_paths(self) -> None:
        self.process_message(0x20)
        self.assertEqual(self.addresses(), [0x52C6C0, 0x53527C, 0x4BD054])
        self.assertEqual(self.arguments(2)[0], 1)

        self.loaded.open_cfw_test_app_ble_reset()
        ctypes.c_ubyte.in_dll(
            self.loaded, "open_cfw_test_app_ble_processor_features"
        ).value = 0x08
        self.process_message(0x20)
        self.assertEqual(self.addresses(), [0x52C6C0, 0x5348EC, 0x4BD054])

        self.loaded.open_cfw_test_app_ble_reset()
        self.u32("open_cfw_test_app_ble_connection_role").value = 1
        self.process_message(0x27, connection=3)
        self.assertEqual(
            self.addresses(),
            [
                0x4B73C4, 0x4BB9B4, 0x4BBF44, 0x4D0C36,
                0x4BB07C, 0x47B488, 0x47B3CC, 0x4BD054,
            ],
        )
        self.assertEqual(self.arguments(7)[0], 8)

        self.loaded.open_cfw_test_app_ble_reset()
        self.process_message(0x2A, connection=4)
        self.assertEqual(
            self.addresses(),
            [0x5348EC, 0x4BB07C, 0x47C084, 0x47BC30, 0x4BD054],
        )

        self.loaded.open_cfw_test_app_ble_reset()
        self.process_message(0x2B, connection=5, status=7)
        self.assertEqual(
            self.addresses(),
            [0x476ACE, 0x47697E, 0x5348EC, 0x47C568, 0x4BD054],
        )
        self.assertEqual(self.arguments(0)[0], 0x4BB92D)
        self.assertEqual(self.arguments(1), (0x4BB92D, 0, 10))
        self.assertEqual(self.arguments(3)[:2], (5, 7))

    def test_message_processor_disconnect_and_restart_paths(self) -> None:
        self.u32("open_cfw_test_app_ble_processor_tick").value = 99
        self.u32("open_cfw_test_app_ble_connection_role").value = 1
        self.process_message(0x28, connection=2)
        self.assertEqual(
            self.addresses(),
            [0x4D0C36, 0x476ACE, 0x476ACE, 0x4B73C4, 0x4BB9B4, 0x4BD054],
        )
        self.assertEqual(self.arguments(1)[0], 0x5354C3)
        self.assertEqual(self.arguments(2)[0], 0x4B81B9)
        self.assertEqual(self.u32("open_cfw_test_app_ble_processor_tick").value, 0)

        self.loaded.open_cfw_test_app_ble_reset()
        self.u32("open_cfw_test_app_ble_connection_role").value = 1
        self.process_message(0x2C, connection=6)
        self.assertEqual(
            self.addresses(),
            [
                0x4BB07C, 0x47B488, 0x47B3CC, 0x4B73C4,
                0x476ACE, 0x47697E, 0x4B82E8, 0x4BB9BC,
                0x4BB9B4, 0x4490CC, 0x4B73C4, 0x4BD054,
            ],
        )
        self.assertEqual(self.arguments(5), (0x5354C3, 6, 1000))
        self.assertEqual(
            self.u32("open_cfw_test_app_ble_processor_tick").value,
            0x12345678,
        )

        self.loaded.open_cfw_test_app_ble_reset()
        self.u32("open_cfw_test_app_ble_query_004bb9bc").value = 1
        self.process_message(0x2C, connection=0)
        self.assertEqual(
            self.addresses(),
            [
                0x4BB07C, 0x47B488, 0x47B3CC, 0x4B82E8, 0x4BB9BC, 0x476ACE,
                0x47697E, 0x47697E, 0x47697E, 0x4490CC,
                0x4B73C4, 0x4C543E, 0x4BD054,
            ],
        )
        self.assertEqual(self.arguments(6), (0x4BB92D, 1, 200))
        self.assertEqual(self.arguments(7), (0x4BB92D, 1, 1000))
        self.assertEqual(self.arguments(8), (0x4BB92D, 1, 2000))

    def test_message_processor_remaining_event_surface(self) -> None:
        simple_notifications = {0x2D: 13, 0x79: 30}
        for event, notification in simple_notifications.items():
            with self.subTest(event=event):
                self.loaded.open_cfw_test_app_ble_reset()
                self.process_message(event)
                self.assertEqual(self.addresses(), [0x4BD054])
                self.assertEqual(self.arguments(0)[0], notification)

        direct_calls = {
            0x12: [0x4D0C36],
            0x2E: [0x4BAFDA],
            0x35: [0x4BB030],
            0xA6: [0x4B48A6, 0x4B3026],
        }
        for event, expected in direct_calls.items():
            with self.subTest(event=event):
                self.loaded.open_cfw_test_app_ble_reset()
                self.process_message(event)
                self.assertEqual(self.addresses(), expected)

        self.loaded.open_cfw_test_app_ble_reset()
        self.u32("open_cfw_test_app_ble_query_0052c914").value = 1
        message = self.process_message(0x34)
        self.assertEqual(self.addresses(), [0x5348FC, 0x52C914, 0x53527C])
        self.assertEqual(self.arguments(0)[0], ctypes.addressof(message) + 4)

        self.loaded.open_cfw_test_app_ble_reset()
        self.process_message(0xA5, connection=7)
        self.assertEqual(self.addresses(), [0x531D60])
        self.assertEqual(self.arguments(0)[0], 7)

        self.loaded.open_cfw_test_app_ble_reset()
        self.control()[0x55] = 1
        self.process_message(0xBC)
        self.assertEqual(
            self.addresses(),
            [0x46F32C, 0x476ACE, 0x4BC418, 0x476ACE, 0x47697E],
        )
        self.assertEqual(self.arguments(1)[0], 0x4BC419)
        self.assertEqual(self.arguments(3)[0], 0x4722CD)
        self.assertEqual(self.arguments(4), (0x4722CD, 0, 10000))

    def test_stack_and_startup_sequences(self) -> None:
        self.loaded.open_cfw_app_ble_stack_initialize()
        addresses = self.addresses()
        self.assertEqual(addresses[:3], [0x52B9B2, 0x52A474, 0x530364])
        self.assertEqual(addresses.count(0x52B980), 8)
        self.assertEqual(addresses[-1], 0x4B4A7C)
        self.assertIn(0x4D27E0, addresses)
        self.assertIn(0x4D250C, addresses)
        self.assertIn(0x52ACCE, addresses)

        self.loaded.open_cfw_test_app_ble_reset()
        self.loaded.open_cfw_app_ble_start()
        addresses = self.addresses()
        self.assertEqual(addresses[:4], [0x4B73E8, 0x4B49CE, 0x491102, 0x4B48A6])
        self.assertEqual(self.arguments(2)[0], 100)
        self.assertEqual(self.arguments(3)[0], 0)
        self.assertEqual(addresses[-2:], [0x4B3026, 0x47697E])
        self.assertEqual(self.arguments(len(addresses) - 1)[2], 10000)

    def test_address_getter(self) -> None:
        expected = bytes.fromhex("010203040506")
        address = (ctypes.c_ubyte * 6).in_dll(
            self.loaded, "open_cfw_test_app_ble_address"
        )
        address[:] = expected
        result = self.loaded.open_cfw_app_ble_address_get()
        self.assertEqual(bytes(result[:6]), expected)

    def test_sources_compile_for_thumb_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            observed = set()
            for source in SOURCES:
                target = Path(directory) / f"{source.stem}.o"
                subprocess.run(
                    [
                        "clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                        "-O2", "-ffreestanding", "-fno-jump-tables",
                        "-fomit-frame-pointer", "-fno-builtin",
                        "-mno-unaligned-access", "-fno-unwind-tables",
                        "-fno-asynchronous-unwind-tables", "-fropi",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(target),
                    ],
                    check=True,
                    cwd=ROOT,
                )
                symbols = subprocess.run(
                    ["nm", str(target)], check=True, capture_output=True, text=True
                ).stdout
                for line in symbols.splitlines():
                    fields = line.split()
                    if len(fields) == 3 and fields[1] == "T":
                        observed.add(fields[2])
            self.assertEqual(observed, EXPECTED_SYMBOLS)

    def test_source_hashes(self) -> None:
        expected = {
            "app_ble_callbacks.c": "8e26f4341e34e0c607a02a82d12c7c21977a072e153d94797ae23f4f9a84401d",
            "app_ble_handler.c": "7f0451b3964ff161e35307934a795db1705a1e3c768633792058bff768365d58",
            "app_ble_processor.c": "8ab54752a4bea42cf482332c6ee4129776f95786cc085387f3d24ddf51f76d78",
            "app_ble_startup.c": "d9549ada2d52eb70bb436f95dec4d7e2e5166446a8155a0edfce28fd5d238a74",
        }
        observed = {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in SOURCES
        }
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
