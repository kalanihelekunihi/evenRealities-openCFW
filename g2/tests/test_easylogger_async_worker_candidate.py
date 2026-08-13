from __future__ import annotations

import ctypes
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components/shared/easylogger/runtime_easylogger_async_worker_candidate.c"
HEADER = SOURCE.with_suffix(".h")
CONSUMER_HEADER = SOURCE.with_name("runtime_easylogger_async_consumer_candidate.h")
QUEUE_HEADER = SOURCE.with_name("runtime_easylogger_async_queue_candidate.h")
FIXTURE = ROOT / "tests/fixtures/runtime_easylogger_async_worker_candidate_host.c"
AUDIT = ROOT / "docs/research/easylogger-async-worker-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000

FUNCTIONS = (
    "open_cfw_easylogger_async_event_dispatch",
    "open_cfw_easylogger_async_event_worker",
    "open_cfw_easylogger_async_event_worker_initialize",
)

STOCK = {
    "worker": (
        0x0044_8E8E,
        0x0044_8F3C,
        "85d2ceaa34ffcbc26f644ad3ca331e5720f9cca5a3b84191cedffda9b019aeec",
        (),
        ((0x0044_9008, 0x0044_8E8F),),
    ),
    "initialize": (
        0x0044_8F44,
        0x0044_8F78,
        "fd00bc4276ff3b9a0ebdf1f5b48dac48433f61741a3c169b694aa88642496b81",
        (0x005B_FA2C,),
        (),
    ),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

TARGET_FUNCTIONS = {
    FUNCTIONS[0]: (120, 4, "6af59b20f8132059631830746d9c1d86fde1308ea176829a95bf8151d96a8d47"),
    FUNCTIONS[1]: (44, 4, "645596373db13e429cabf90ce06c98054655f4e84cc368eed466711ca1c1df52"),
    FUNCTIONS[2]: (92, 4, "76990e4ee32b01a331a683ad09c4b60433ca1ffb8e97b8b0ed6d83a92fe365c2"),
}

TARGET_RELOCATIONS = {
    FUNCTIONS[0]: [
        (2, 47, "open_cfw_retained_easylogger_async_event_flags"),
        (10, 48, "open_cfw_retained_easylogger_async_event_flags"),
        (24, 10, "open_cfw_retained_easylogger_upload_event_handler"),
        (32, 10, "open_cfw_retained_easylogger_event_flags_clear"),
        (42, 10, "open_cfw_retained_easylogger_kv_event_diagnostic"),
        (46, 10, "open_cfw_retained_easylogger_settings_save_handler"),
        (50, 10, "open_cfw_retained_easylogger_history_save_handler"),
        (54, 10, "open_cfw_retained_easylogger_onboarding_save_handler"),
        (58, 10, "open_cfw_retained_easylogger_device_save_handler"),
        (62, 10, "open_cfw_retained_easylogger_user_save_handler"),
        (66, 10, "open_cfw_retained_easylogger_contacts_save_handler"),
        (70, 10, "open_cfw_retained_easylogger_preferences_save_handler"),
        (82, 30, "open_cfw_retained_easylogger_event_flags_clear"),
        (86, 10, "open_cfw_easylogger_async_record_drain"),
        (94, 10, "open_cfw_retained_easylogger_event_flags_clear"),
        (102, 10, "open_cfw_retained_easylogger_database_event_handler"),
        (110, 10, "open_cfw_retained_easylogger_event_flags_clear"),
    ],
    FUNCTIONS[1]: [
        (0, 49, "open_cfw_easylogger_async_worker_start_message"),
        (4, 50, "open_cfw_easylogger_async_worker_start_message"),
        (10, 10, "open_cfw_retained_easylogger_diagnostic"),
        (14, 47, "open_cfw_retained_easylogger_async_event_flags"),
        (18, 48, "open_cfw_retained_easylogger_async_event_flags"),
        (34, 10, "open_cfw_retained_easylogger_event_flags_wait"),
        (38, 10, "open_cfw_easylogger_async_event_dispatch"),
    ],
    FUNCTIONS[2]: [
        (4, 49, ".L__const.open_cfw_easylogger_async_event_worker_initialize.attributes"),
        (8, 50, ".L__const.open_cfw_easylogger_async_event_worker_initialize.attributes"),
        (34, 10, "open_cfw_retained_easylogger_event_flags_new"),
        (38, 47, "open_cfw_retained_easylogger_async_event_flags"),
        (42, 48, "open_cfw_retained_easylogger_async_event_flags"),
        (50, 49, "open_cfw_easylogger_async_event_worker"),
        (54, 50, "open_cfw_easylogger_async_event_worker"),
        (64, 10, "open_cfw_retained_easylogger_thread_new"),
        (72, 49, "open_cfw_easylogger_async_event_create_failure_message"),
        (76, 50, "open_cfw_easylogger_async_event_create_failure_message"),
        (88, 30, "open_cfw_retained_easylogger_diagnostic"),
    ],
}

TARGET_UNDEFINED = [
    "open_cfw_easylogger_async_record_drain",
    "open_cfw_retained_easylogger_async_event_flags",
    "open_cfw_retained_easylogger_contacts_save_handler",
    "open_cfw_retained_easylogger_database_event_handler",
    "open_cfw_retained_easylogger_device_save_handler",
    "open_cfw_retained_easylogger_diagnostic",
    "open_cfw_retained_easylogger_event_flags_clear",
    "open_cfw_retained_easylogger_event_flags_new",
    "open_cfw_retained_easylogger_event_flags_wait",
    "open_cfw_retained_easylogger_history_save_handler",
    "open_cfw_retained_easylogger_kv_event_diagnostic",
    "open_cfw_retained_easylogger_onboarding_save_handler",
    "open_cfw_retained_easylogger_preferences_save_handler",
    "open_cfw_retained_easylogger_settings_save_handler",
    "open_cfw_retained_easylogger_thread_new",
    "open_cfw_retained_easylogger_upload_event_handler",
    "open_cfw_retained_easylogger_user_save_handler",
]

TARGET_PINS: dict[str, dict[str, object]] = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (3984, "31cb546015d03f291c2b8fd33ce5b8f588508d165f2dc34264a3371092c6a18a"),
        "functions": TARGET_FUNCTIONS,
        "relocations": TARGET_RELOCATIONS,
        "undefined": TARGET_UNDEFINED,
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (3964, "2efc693539aed187c24a7b766dde449130107760c50f59c9ba23dfb031226130"),
        "functions": TARGET_FUNCTIONS,
        "relocations": TARGET_RELOCATIONS,
        "undefined": TARGET_UNDEFINED,
    },
}

LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (5968, "b1f848f8f181e1de4417ff3a21a6a39ddfa6aa2281617636f752a5149425fd4b"),
    HEADER: (1412, "be7c2882d7b636b8aca304420f695ca0ac26b3103c11edd24c8ba783b314951f"),
    FIXTURE: (5662, "52f56bdc52f9f0ab1ea5e2d5a33ec89700178fcda3bbef158bb63939e0e06e32"),
    AUDIT: (3175, "2be5e4f62e104f0c01b186a6f0dc74d5c8a76e7f3a57b014032a1fbee55cf681"),
}


class ThreadAttributes(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("attribute_bits", ctypes.c_uint32),
        ("control_block_memory", ctypes.c_void_p),
        ("control_block_size", ctypes.c_uint32),
        ("stack_memory", ctypes.c_void_p),
        ("stack_size", ctypes.c_uint32),
        ("priority", ctypes.c_uint32),
        ("trustzone_module", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class EasyLoggerAsyncWorkerCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("worker.dylib" if sys.platform == "darwin" else "worker.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_easylogger_worker_reset.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_easylogger_async_event_dispatch.argtypes = [ctypes.c_uint32]
        cls.target_object = temp / "worker.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)], check=True, capture_output=True, text=True)
        cls.version = subprocess.run([clang, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cls.target = cls.parse_target(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def u32(cls, name: str) -> int:
        return ctypes.c_uint32.in_dll(cls.loaded, name).value

    @classmethod
    def u32_array(cls, name: str, count: int) -> list[int]:
        values = (ctypes.c_uint32 * count).in_dll(cls.loaded, name)
        return list(values)

    @staticmethod
    def parse_target(path: Path) -> dict[str, object]:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(path)
        symtab = apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[int(symtab["link"])]
        strings = data[int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])]
        symbols = []
        for index in range(int(symtab["size"]) // 16):
            fields = struct.unpack_from("<IIIBBH", data, int(symtab["offset"]) + index * 16)
            symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"), fields))
        functions, relocations = {}, {}
        for function in FUNCTIONS:
            section = apollo_overlay.section_named(sections, ".text." + function)
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            functions[function] = (len(body), int(section["alignment"]), hashlib.sha256(body).hexdigest())
            values = []
            for relsec in sections:
                if int(relsec["type"]) == 9 and int(relsec["info"]) == int(section["index"]):
                    for index in range(int(relsec["size"]) // 8):
                        offset, info = struct.unpack_from("<II", data, int(relsec["offset"]) + index * 8)
                        values.append((offset, info & 0xFF, symbols[info >> 8][0]))
            relocations[function] = values
        undefined = sorted(name for name, fields in symbols if name and fields[5] == 0)
        return {"object": (len(data), hashlib.sha256(data).hexdigest()), "functions": functions, "relocations": relocations, "undefined": undefined}

    def test_dispatch_preserves_stock_bit_order_and_clear_order(self) -> None:
        self.loaded.open_cfw_test_easylogger_worker_reset(0)
        self.loaded.open_cfw_easylogger_async_event_dispatch(0xFFFF_FFFF)
        self.assertEqual(
            self.u32_array("open_cfw_test_easylogger_worker_order", 15),
            [1, 101, 2, 102, 8, 108, 4, 40, 41, 42, 43, 44, 45, 46, 104],
        )
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_clear_count"), 4)
        self.assertEqual(
            self.u32_array("open_cfw_test_easylogger_worker_clear_masks", 4),
            [1, 2, 8, 4],
        )
        handles = (ctypes.c_size_t * 4).in_dll(
            self.loaded, "open_cfw_test_easylogger_worker_clear_handles"
        )
        self.assertEqual(list(handles), [0xCAFE_BABE] * 4)

    def test_dispatch_ignores_unselected_bits(self) -> None:
        self.loaded.open_cfw_test_easylogger_worker_reset(0)
        self.loaded.open_cfw_easylogger_async_event_dispatch(0x8000_000A)
        self.assertEqual(
            self.u32_array("open_cfw_test_easylogger_worker_order", 4),
            [2, 102, 8, 108],
        )
        self.loaded.open_cfw_test_easylogger_worker_reset(0)
        self.loaded.open_cfw_easylogger_async_event_dispatch(0x8000_0000)
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_order_count"), 0)

    def test_all_sixteen_low_nibble_combinations(self) -> None:
        blocks = {
            1: [1, 101],
            2: [2, 102],
            8: [8, 108],
            4: [4, 40, 41, 42, 43, 44, 45, 46, 104],
        }
        for mask in range(16):
            with self.subTest(mask=mask):
                self.loaded.open_cfw_test_easylogger_worker_reset(0)
                self.loaded.open_cfw_easylogger_async_event_dispatch(mask)
                expected = [value for bit in (1, 2, 8, 4) if mask & bit for value in blocks[bit]]
                count = self.u32("open_cfw_test_easylogger_worker_order_count")
                self.assertEqual(
                    self.u32_array("open_cfw_test_easylogger_worker_order", count),
                    expected,
                )

    def test_initializer_copies_exact_thread_contract(self) -> None:
        self.loaded.open_cfw_test_easylogger_worker_reset(0)
        self.loaded.open_cfw_easylogger_async_event_worker_initialize()
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_new_count"), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_thread_count"), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_diagnostic_count"), 0)
        event = ctypes.c_void_p.in_dll(
            self.loaded, "open_cfw_retained_easylogger_async_event_flags"
        ).value
        self.assertEqual(event, 0x1234_5678)
        attrs = ThreadAttributes.in_dll(
            self.loaded, "open_cfw_test_easylogger_worker_thread_attributes"
        )
        self.assertEqual(attrs.name, b"elog_async_handler_thread")
        self.assertEqual(attrs.attribute_bits, 0)
        self.assertFalse(attrs.control_block_memory)
        self.assertEqual(attrs.control_block_size, 0)
        self.assertFalse(attrs.stack_memory)
        self.assertEqual(attrs.stack_size, 0x800)
        self.assertEqual(attrs.priority, 0x17)
        self.assertEqual(attrs.trustzone_module, 0)
        self.assertEqual(attrs.reserved, 0)
        self.assertTrue(ctypes.c_void_p.in_dll(self.loaded, "open_cfw_test_easylogger_worker_thread_entry").value)
        self.assertFalse(ctypes.c_void_p.in_dll(self.loaded, "open_cfw_test_easylogger_worker_thread_argument").value)

    def test_initializer_fails_closed_when_event_creation_fails(self) -> None:
        self.loaded.open_cfw_test_easylogger_worker_reset(1)
        self.loaded.open_cfw_easylogger_async_event_worker_initialize()
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_new_count"), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_thread_count"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_worker_diagnostic_count"), 1)
        message = ctypes.c_char_p.in_dll(
            self.loaded, "open_cfw_test_easylogger_worker_last_diagnostic"
        ).value
        self.assertEqual(
            message,
            b"Failed to create elog_async_handler_thread EventFlags\n",
        )

    @staticmethod
    def decode_bl(application: bytes, address: int) -> int | None:
        first, second = struct.unpack_from("<HH", application, address - BASE)
        if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
            return None
        sign = first >> 10 & 1; i10 = first & 0x3FF; j1 = second >> 13 & 1; j2 = second >> 11 & 1; i11 = second & 0x7FF
        i1 = (~(j1 ^ sign)) & 1; i2 = (~(j2 ^ sign)) & 1
        immediate = sign << 24 | i1 << 23 | i2 << 22 | i10 << 12 | i11 << 1
        if sign: immediate -= 1 << 25
        return address + 4 + immediate

    def test_stock_spans_topology_literals_and_attributes_are_exact(self) -> None:
        for role, (start, end, digest, callers, expected_stored) in STOCK.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, digest))
            actual_callers = tuple(
                BASE + offset
                for offset in range(0, len(self.application) - 3, 2)
                if self.decode_bl(self.application, BASE + offset) == start
            )
            self.assertEqual(actual_callers, callers, role)
            stored = []
            for offset in range(len(self.application) - 3):
                value = struct.unpack_from("<I", self.application, offset)[0]
                if start <= (value & ~1) < end:
                    stored.append((BASE + offset, value))
            self.assertEqual(tuple(stored), expected_stored, role)
        self.assertEqual(
            self.application[0x0075_42F0 - BASE:0x0075_4314 - BASE],
            struct.pack("<9I", 0x0076_B650, 0, 0, 0, 0, 0x800, 0x17, 0, 0),
        )
        for address, expected in {
            0x0076_B650: b"elog_async_handler_thread",
            0x0073_EA54: b"elog_async_handler_thread_handler start\n",
            0x0071_EA00: b"Failed to create elog_async_handler_thread EventFlags\n",
        }.items():
            offset = address - BASE
            self.assertEqual(self.application[offset:self.application.index(b"\0", offset)], expected)

    def test_target_closure_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        pin = TARGET_PINS[profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual(self.target["object"], pin["object"])
        self.assertEqual(self.target["undefined"], pin["undefined"])
        for function, expected in pin["functions"].items():
            self.assertEqual(self.target["functions"][function], expected)
            self.assertEqual(self.target["relocations"][function], pin["relocations"][function])

    def test_artifacts_are_pinned_and_production_excluded(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            body = path.read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, digest))
        forbidden = (SOURCE.name, HEADER.name, *FUNCTIONS)
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
