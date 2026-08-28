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
SOURCE = ROOT / "components/shared/easylogger/runtime_easylogger_async_consumer_candidate.c"
HEADER = SOURCE.with_suffix(".h")
QUEUE_HEADER = SOURCE.with_name("runtime_easylogger_async_queue_candidate.h")
FIXTURE = ROOT / "tests/fixtures/runtime_easylogger_async_consumer_candidate_host.c"
AUDIT = ROOT / "docs/research/easylogger-async-consumer-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000

FUNCTIONS = (
    "open_cfw_easylogger_async_primary_callback_configure",
    "open_cfw_easylogger_async_secondary_callback_configure",
    "open_cfw_easylogger_async_default_metadata_set",
    "open_cfw_easylogger_async_record_drain",
)

STOCK = {
    FUNCTIONS[0]: (0x0044_8CAC, 0x0044_8CB8, "1180c9bacb221aee63f27640eff748d5c5c520bcacf79741011346d7d2316e34", (0x005B_FA38,)),
    FUNCTIONS[1]: (0x0044_8CB8, 0x0044_8CC4, "42b6a860fc6638bac89dee864761d06efe0d53d358f157cf8ebc0ece251482bd", (0x0045_8E10, 0x0045_8E1C, 0x005B_FA40)),
    FUNCTIONS[2]: (0x0044_8CC4, 0x0044_8CCC, "97ebd76595cc6f18cf192034b671bc1ec2150350a9451f21e21db354baf99fde", (0x005B_FA46,)),
    FUNCTIONS[3]: (0x0044_8DD2, 0x0044_8E2A, "43ac9598579abc817bc013e3f65ad69639f72f7bf03cbe6ca3bdd8596e5612e7", (0x0044_8EAC,)),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

RELOCATIONS = {
    FUNCTIONS[0]: [(0, 47, "open_cfw_retained_easylogger_async_primary_enabled"), (4, 48, "open_cfw_retained_easylogger_async_primary_enabled"), (10, 47, "open_cfw_retained_easylogger_async_primary_callback"), (14, 48, "open_cfw_retained_easylogger_async_primary_callback")],
    FUNCTIONS[1]: [(0, 47, "open_cfw_retained_easylogger_async_secondary_enabled"), (4, 48, "open_cfw_retained_easylogger_async_secondary_enabled"), (10, 47, "open_cfw_retained_easylogger_async_secondary_callback"), (14, 48, "open_cfw_retained_easylogger_async_secondary_callback")],
    FUNCTIONS[2]: [(0, 47, "open_cfw_retained_easylogger_async_default_metadata"), (4, 48, "open_cfw_retained_easylogger_async_default_metadata")],
    FUNCTIONS[3]: [(4, 47, "open_cfw_retained_easylogger_async_ready"), (8, 48, "open_cfw_retained_easylogger_async_ready"), (18, 47, "open_cfw_retained_easylogger_async_queue_statistics"), (22, 47, "open_cfw_retained_easylogger_async_primary_enabled"), (26, 47, "open_cfw_retained_easylogger_async_primary_callback"), (30, 48, "open_cfw_retained_easylogger_async_queue_statistics"), (34, 48, "open_cfw_retained_easylogger_async_primary_enabled"), (38, 48, "open_cfw_retained_easylogger_async_primary_callback"), (44, 10, "open_cfw_easylogger_async_queue_record_recycle"), (62, 10, "open_cfw_easylogger_async_queue_record_dequeue")],
}

UNDEFINED = sorted({symbol for values in RELOCATIONS.values() for _, _, symbol in values})

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "object": (2996, "3304cd98addda539f567274e63cd134656eec268781bd798d8a34443eeb0a93b"),
        "functions": {
            FUNCTIONS[0]: (24, "9339e1916f5f27fa52c49d5a809968ae5455940c478fe35951e1d28694c473a9"),
            FUNCTIONS[1]: (24, "9339e1916f5f27fa52c49d5a809968ae5455940c478fe35951e1d28694c473a9"),
            FUNCTIONS[2]: (12, "47ad4861aac9d6170e4a0defe6f2c9fa1b978ad9e169b10ad8853bb07f1937d2"),
            FUNCTIONS[3]: (116, "b06601395cec6a6cfbcd2e34e54629ed46cfc892bc10fb28fad84a49e88d85b1"),
        },
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (2976, "2fcbb8785c1fac0dfeb66133cefb9582fcfc32ce9c9eab7a131ce28d971b1e33"),
        "functions": {
            FUNCTIONS[0]: (24, "9339e1916f5f27fa52c49d5a809968ae5455940c478fe35951e1d28694c473a9"),
            FUNCTIONS[1]: (24, "9339e1916f5f27fa52c49d5a809968ae5455940c478fe35951e1d28694c473a9"),
            FUNCTIONS[2]: (12, "47ad4861aac9d6170e4a0defe6f2c9fa1b978ad9e169b10ad8853bb07f1937d2"),
            FUNCTIONS[3]: (116, "b06601395cec6a6cfbcd2e34e54629ed46cfc892bc10fb28fad84a49e88d85b1"),
        },
    },
}

LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (2449, "189a2829bb478d4c6998dc9d081c188b30f70096de4bd0dc3ae6f4b04a5d8989"),
    HEADER: (1578, "28eba83c83b5453898135de077cfcb356f161f13ee15e7610ce8c7f86686c5fb"),
    FIXTURE: (5698, "f1392efbbaa29151805a82cf12d2a5e6829d6fcd1506383a5e8d10d27d84e472"),
    AUDIT: (3376, "3a1c557790ab961c369b2ebc56c5085888bcec259712d4295b842220f625a097"),
}


class AsyncStatistics(ctypes.Structure):
    _fields_ = [("drained_record_count", ctypes.c_uint32), ("rest", ctypes.c_uint8 * 44)]


class EasyLoggerAsyncConsumerCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("consumer.dylib" if sys.platform == "darwin" else "consumer.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_easylogger_consumer_reset.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_easylogger_consumer_set_record.argtypes = [ctypes.c_uint32, ctypes.c_uint16, ctypes.c_char_p, ctypes.c_uint16, ctypes.c_uint8]
        cls.loaded.open_cfw_test_easylogger_consumer_drain.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_easylogger_consumer_configure_primary.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        cls.loaded.open_cfw_test_easylogger_consumer_configure_primary.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_easylogger_consumer_configure_secondary.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        cls.loaded.open_cfw_test_easylogger_consumer_configure_secondary.restype = ctypes.c_uint32
        cls.target_object = temp / "consumer.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)], check=True, capture_output=True, text=True)
        cls.version = subprocess.run([clang, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cls.target = cls.parse_target(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def u32(name: str) -> int:
        return ctypes.c_uint32.in_dll(EasyLoggerAsyncConsumerCandidateTests.loaded, name).value

    @staticmethod
    def u8(name: str) -> int:
        return ctypes.c_uint8.in_dll(EasyLoggerAsyncConsumerCandidateTests.loaded, name).value

    @staticmethod
    def parse_target(path: Path) -> dict[str, object]:
        sys.path.insert(0, str(ROOT / "tools"))
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
        return {"object": (len(data), hashlib.sha256(data).hexdigest()), "functions": functions, "relocations": relocations, "undefined": sorted(name for name, fields in symbols if name and fields[5] == 0)}

    def test_callback_setters_and_metadata_setter(self) -> None:
        self.loaded.open_cfw_test_easylogger_consumer_reset(0)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_configure_primary(0xA5, 1), 0)
        self.assertEqual(self.u8("open_cfw_retained_easylogger_async_primary_enabled"), 0xA5)
        self.assertNotEqual(ctypes.c_void_p.in_dll(self.loaded, "open_cfw_retained_easylogger_async_primary_callback").value, 0)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_configure_secondary(0x6A, 0), 0)
        self.assertEqual(self.u8("open_cfw_retained_easylogger_async_secondary_enabled"), 0x6A)
        self.assertFalse(ctypes.c_void_p.in_dll(self.loaded, "open_cfw_retained_easylogger_async_secondary_callback").value)
        self.loaded.open_cfw_easylogger_async_default_metadata_set(0x33)
        self.assertEqual(self.u8("open_cfw_retained_easylogger_async_default_metadata"), 0x33)

    def test_ready_and_callback_gates_recycle_every_record(self) -> None:
        self.loaded.open_cfw_test_easylogger_consumer_reset(3)
        payloads = (b"one", b"two", b"three")
        for index, (metadata, payload) in enumerate(zip((1, 0, 3), payloads)):
            self.loaded.open_cfw_test_easylogger_consumer_set_record(index, metadata, payload, len(payload), index + 1)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_drain(), 3)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_recycle_count"), 3)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_callback_count"), 2)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_callback_bytes"), 8)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_callback_checksum"), sum(b"onethree"))
        stats = AsyncStatistics.in_dll(self.loaded, "open_cfw_retained_easylogger_async_queue_statistics")
        self.assertEqual(stats.drained_record_count, 3)

        self.loaded.open_cfw_test_easylogger_consumer_reset(2)
        ctypes.c_uint8.in_dll(self.loaded, "open_cfw_retained_easylogger_async_ready").value = 0
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_drain(), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_dequeue_index"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_recycle_count"), 0)

        self.loaded.open_cfw_test_easylogger_consumer_reset(1)
        self.loaded.open_cfw_test_easylogger_consumer_configure_primary(0, 1)
        self.loaded.open_cfw_test_easylogger_consumer_set_record(0, 1, b"x", 1, 7)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_drain(), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_callback_count"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_recycle_count"), 1)

    def test_drain_caps_each_wake_at_256(self) -> None:
        self.loaded.open_cfw_test_easylogger_consumer_reset(300)
        self.loaded.open_cfw_test_easylogger_consumer_configure_primary(0, 0)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_drain(), 256)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_dequeue_index"), 256)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_consumer_drain(), 44)
        self.assertEqual(self.u32("open_cfw_test_easylogger_consumer_recycle_count"), 300)
        stats = AsyncStatistics.in_dll(self.loaded, "open_cfw_retained_easylogger_async_queue_statistics")
        self.assertEqual(stats.drained_record_count, 300)

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

    def test_stock_spans_and_direct_callers_are_exact(self) -> None:
        for function, (start, end, digest, expected_callers) in STOCK.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, digest))
            callers = []
            for offset in range(0, len(self.application) - 3, 2):
                address = BASE + offset
                if self.decode_bl(self.application, address) == start:
                    callers.append(address)
            self.assertEqual(tuple(callers), expected_callers, function)
            stored = []
            for offset in range(len(self.application) - 3):
                value = struct.unpack_from("<I", self.application, offset)[0] & ~1
                if start <= value < end:
                    stored.append((BASE + offset, value))
            self.assertEqual(stored, [], function)

    def test_target_closure_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        pin = TARGET_PINS[profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual(self.target["object"], pin["object"])
        self.assertEqual(self.target["undefined"], UNDEFINED)
        for function, (size, digest) in pin["functions"].items():
            self.assertEqual(self.target["functions"][function], (size, 4, digest))
            self.assertEqual(self.target["relocations"][function], RELOCATIONS[function])

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
