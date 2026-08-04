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
CANDIDATE = (
    ROOT / "research" / "candidates" / "freertos_scheduler_port_trio.c"
)
HEADER = CANDIDATE.with_suffix(".h")
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "freertos_scheduler_port_trio_candidate_host.c"
)
UPSTREAM_PORT = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "port.c"
)
UPSTREAM_PORTMACRO = UPSTREAM_PORT.with_name("portmacrocommon.h")
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
UPSTREAM_PORT_SHA256 = (
    "c2762e124d700d26ceb0dc737af706f3"
    "61dd45c9e40bf683b916f1e430e37a08"
)
UPSTREAM_PORTMACRO_SHA256 = (
    "c184e6b1727732bbdd0d4dd33b9af4e"
    "a25d13040620666123941fff464bffc99"
)

SOURCE_SIZE = 5_437
SOURCE_SHA256 = (
    "8fdefac8d8219c25b9a7a5424b6469b2"
    "882f9ae0331bfe33e69720b804a9a24e"
)
HEADER_SIZE = 814
HEADER_SHA256 = (
    "8b5e6fb78ae1c3211e7bf0925ede8c04"
    "c1bc8d7dd2102a1b11814c545a40c0f4"
)
FIXTURE_SIZE = 5_363
FIXTURE_SHA256 = (
    "e29a2dce133e12d75e13e72e53bf2336"
    "8ad54df0466e765fa95531f648c52693"
)

YIELD_START = 0x0044_20BC
ENTER_START = 0x0044_20D0
EXIT_START = 0x0044_20E8
TRIO_END = 0x0044_2114
STOCK = {
    "yield": {
        "start": YIELD_START,
        "end": ENTER_START,
        "bytes": (
            "5ff0805056490860bff34f8fbff36f8f70470000"
        ),
        "sha256": (
            "dd981b3e9196c6fd87bb79719c94628c"
            "89e564d5728b3fdd1ff08c397eccb397"
        ),
    },
    "enter": {
        "start": ENTER_START,
        "end": EXIT_START,
        "bytes": (
            "80b5b7f1e7ff4e480168491c0160"
            "bff34f8fbff36f8f01bd"
        ),
        "sha256": (
            "5809638c22f928d2b32cd21cc9b92a29"
            "2fad24cd8b8008de4ad92b9faeaba0d4"
        ),
    },
    "exit": {
        "start": EXIT_START,
        "end": TRIO_END,
        "bytes": (
            "80b549490868002806d1b7f1d7ff0020"
            "5ff0ff310860fee70868401e08600868"
            "002802d10020b7f1d4ff01bd"
        ),
        "sha256": (
            "bfd3ddb76c61ad634a3f58ed203260da"
            "3834895b646c9dffada546f9dc9d2a31"
        ),
    },
}
TRIO_SHA256 = (
    "ba9b86be2e0caa3b3bb32b45a7f1f47"
    "30fc94f6ad80153d470de5cb6e7a9b228"
)
PREDECESSOR_SHA256 = (
    "59f9a18538c1aab61aefe1664793178c"
    "6c16cc5f1c4d79b3c8502ddda0b742c8"
)
SUCCESSOR_SHA256 = (
    "2999c107f0c2c7a14aa1dffb07531b0"
    "b9389af39295a4ae606201faf02675a6f"
)

ICSR_ADDRESS = 0xE000_ED04
PENDSVSET_BIT = 0x1000_0000
CRITICAL_NESTING_ADDRESS = 0x2000_309C
CRITICAL_NESTING_LITERAL = 0x0044_2210
ICSR_LITERAL = 0x0044_221C
SET_MASK_START = 0x005F_A0A4
CLEAR_MASK_START = 0x005F_A0BA
CLEAR_MASK_END = 0x005F_A0C8
MASK_PAIR_SHA256 = (
    "422a4cac7b1abe90c7c7b0c431e2d85e"
    "f4d733cffb2da3b2708311f183cce849"
)

CALLERS = {
    "yield": [
        0x00441596, 0x00441908, 0x00441912, 0x0044193E,
        0x00441BF4, 0x00441C18, 0x00441D36, 0x00441D5E,
        0x004491F6, 0x00454AA8, 0x00454B46, 0x00454B82,
        0x00454CE2, 0x00454EF2, 0x00455612, 0x00455B40,
        0x00455BE0, 0x00455DAC, 0x0047E8E6, 0x0047ECCA,
        0x0052B918,
    ],
    "enter": [
        0x0043C98E, 0x0044154A, 0x00441894, 0x004418DC,
        0x00441B7A, 0x00441B9E, 0x00441CA6, 0x00441CCA,
        0x00441D0E, 0x00441D8A, 0x00441E7C, 0x00441F8C,
        0x00441FC2, 0x00441FFA, 0x00442016, 0x00442038,
        0x00449DB0, 0x00449E6E, 0x00454A00, 0x00454AB2,
        0x00454BAC, 0x00454C32, 0x00454DEA, 0x00455030,
        0x00455590, 0x004556E4, 0x00455B16, 0x00455B48,
        0x00455BA2, 0x00455BE8, 0x00455C7C, 0x00455F80,
        0x004767B4, 0x00476912, 0x0047EABA, 0x0047EB0C,
        0x0047EB3C, 0x0047ECDA, 0x0047ED3C, 0x004D46FA,
        0x004D472E, 0x004D47D6, 0x004D4804, 0x0057E17E,
        0x005847E2,
    ],
    "exit": [
        0x0043C9F8, 0x004415AC, 0x0044188C, 0x004418B8,
        0x00441916, 0x0044191E, 0x00441B96, 0x00441BC2,
        0x00441C1C, 0x00441C24, 0x00441CC2, 0x00441CEE,
        0x00441D1A, 0x00441D62, 0x00441D6A, 0x00441D9C,
        0x00441E82, 0x00441FBE, 0x00441FF0, 0x0044200A,
        0x00442028, 0x0044205C, 0x00449DC8, 0x00449E7A,
        0x00454A90, 0x00454B0E, 0x00454BBE, 0x00454CE6,
        0x00454EF6, 0x0045503E, 0x004555DE, 0x00455706,
        0x00455B44, 0x00455B7C, 0x00455BE4, 0x00455C28,
        0x00455DB0, 0x00455FA0, 0x004767BE, 0x00476918,
        0x0047EAF0, 0x0047EB1E, 0x0047EB42, 0x0047ED02,
        0x0047ED4A, 0x004D470A, 0x004D4740, 0x004D47E6,
        0x004D4814, 0x0057E1B0, 0x005847F4,
    ],
}
CALLER_ADDRESS_SHA256 = {
    "yield": "a3e06a6ce5af90723601814b9ab099b79ec4240fcfb185ae287630f5b2ab90a7",
    "enter": "65bc28cb458bf50bb2b30160bf661f686d8ce2d9fcdae800244ed901933f3993",
    "exit": "61250f3aa182674a0ee06462d2efaf5308511f36178f58561040dac2c1d5b631",
}
CALLER_RECORD_SHA256 = {
    "yield": "82bf0d7ac31cb2985e55ebbe5e31791d74e3c826be25da010fd121d281bd7001",
    "enter": "8365ac4db9e8d5531c7791a7462440c5999ce30de0ef75c43e004233c3295792",
    "exit": "605cbb784ec11f6d07fbf7e4f26d16d8b6c51263be5d10e88f46a76f81a0cafd",
}
RAW_EXIT_INTERIOR_LOCATIONS = [
    0x00492595, 0x004926C3, 0x00492701, 0x004927DD,
    0x0049281B, 0x00492833, 0x0049286B, 0x00492885,
    0x004A5D5B, 0x004BF0D7, 0x004FE07D, 0x0050BC29,
    0x0050BCC3, 0x0050BDEF, 0x0053A473, 0x0053A48F,
    0x0053A551, 0x0058318F, 0x005943F5, 0x005D2973,
]

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGET_TEXT = {
    "open_cfw_freertos_port_yield": (
        "4ef60450cef200004ff080510160bff34f8fbff36f8f7047",
        "105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235",
    ),
    "open_cfw_freertos_port_enter_critical": (
        "80b5fff7feff43f29c00c2f20000016801310160bff34f8fbff36f8f80bd",
        "18797972899b42b6333a1353a25820dc720a5e477d0275b3fb4f039cbc0ef158",
    ),
    "open_cfw_freertos_port_exit_critical": (
        "43f29c00c2f20000016849b10168013901600068002818bf70470020"
        "fff7febf80b5fff7feff4ff0ff3000210160bde8804000bffee7",
        "1106c10ba143e84c0335da8c09658f88594e4578a8dfece201e73ee36f00900f",
    ),
}
TARGET_RELOCATIONS = {
    ".text.open_cfw_freertos_port_yield": [],
    ".text.open_cfw_freertos_port_enter_critical": [
        (0x02, 10, "ulSetInterruptMask"),
    ],
    ".text.open_cfw_freertos_port_exit_critical": [
        (0x1C, 30, "vClearInterruptMask"),
        (0x22, 10, "ulSetInterruptMask"),
    ],
}


class FreeRTOSSchedulerPortTrioCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[PACKAGE_PREAMBLE_SIZE:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if version.startswith("Apple clang version 21.0.0"):
            cls.toolchain_profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.toolchain_profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed clang family: {version.splitlines()[0]}")

        library = temporary / (
            "scheduler_port_trio.dylib"
            if sys.platform == "darwin"
            else "scheduler_port_trio.so"
        )
        host_command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls._configure_host_functions()

        cls.target_object = temporary / "scheduler_port_trio.o"
        subprocess.run(
            [
                cls.clang,
                *TARGET_FLAGS,
                "-c",
                str(CANDIDATE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.object_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.section_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        cls.symbols, cls.relocations = cls._parse_object_contract()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def _configure_host_functions(cls) -> None:
        for name in (
            "open_cfw_test_port_icsr",
            "open_cfw_test_port_nesting",
            "open_cfw_test_port_set_calls",
            "open_cfw_test_port_clear_calls",
            "open_cfw_test_port_clear_value",
            "open_cfw_test_port_event_code",
            "open_cfw_test_port_event_value",
        ):
            getattr(cls.loaded, name).restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_port_event_count.restype = ctypes.c_size_t
        cls.loaded.open_cfw_test_port_run_exit.restype = ctypes.c_int
        cls.loaded.open_cfw_test_port_reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_port_event_code.argtypes = [ctypes.c_size_t]
        cls.loaded.open_cfw_test_port_event_value.argtypes = [ctypes.c_size_t]

    @classmethod
    def _parse_object_contract(cls):
        symbol_table = cls.apollo_overlay.section_named(
            cls.sections, ".symtab"
        )
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.object_data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.object_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = cls.apollo_overlay.elf_string(
                strings, fields[0], "symbol"
            )
            parsed.append((name, fields))
        symbols = {name: fields for name, fields in parsed if name}
        relocations = {}
        for section in cls.sections:
            if int(section["type"]) != 9:
                continue
            target = str(cls.sections[int(section["info"])]["name"])
            records = []
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    cls.object_data,
                    int(section["offset"]) + index * 8,
                )
                symbol_name, symbol = parsed[information >> 8]
                if not symbol_name and int(symbol[5]) < len(cls.sections):
                    symbol_name = (
                        "<section:"
                        + str(cls.sections[int(symbol[5])]["name"])
                        + ">"
                    )
                records.append(
                    (offset, information & 0xFF, symbol_name)
                )
            relocations[target] = records
        return symbols, relocations

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def section_bytes(self, name: str) -> bytes:
        section = self.section_by_name[name]
        return self.object_data[
            int(section["offset"]):
            int(section["offset"]) + int(section["size"])
        ]

    def events(self):
        count = self.loaded.open_cfw_test_port_event_count()
        return [
            (
                self.loaded.open_cfw_test_port_event_code(index),
                self.loaded.open_cfw_test_port_event_value(index),
            )
            for index in range(count)
        ]

    @staticmethod
    def narrow_branch_targets(address: int, halfword: int) -> list[int]:
        if halfword & 0xF800 == 0xE000:
            immediate = halfword & 0x07FF
            if immediate & 0x0400:
                immediate -= 0x0800
            return [address + 4 + immediate * 2]
        if (
            halfword & 0xF000 == 0xD000
            and ((halfword >> 8) & 0x0F) < 0x0E
        ):
            immediate = halfword & 0x00FF
            if immediate & 0x0080:
                immediate -= 0x0100
            return [address + 4 + immediate * 2]
        if halfword & 0xF500 == 0xB100:
            immediate = (
                (((halfword >> 9) & 1) << 5)
                | ((halfword >> 3) & 0x1F)
            )
            return [address + 4 + immediate * 2]
        return []

    def test_official_upstream_and_candidate_inputs_are_authenticated(self):
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), 3_523_396)
        self.assertEqual(hashlib.sha256(package).hexdigest(), PACKAGE_SHA256)
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            APPLICATION_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_PORT.read_bytes()).hexdigest(),
            UPSTREAM_PORT_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_PORTMACRO.read_bytes()).hexdigest(),
            UPSTREAM_PORTMACRO_SHA256,
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        for path, size, digest in (
            (CANDIDATE, SOURCE_SIZE, SOURCE_SHA256),
            (HEADER, HEADER_SIZE, HEADER_SHA256),
            (FIXTURE, FIXTURE_SIZE, FIXTURE_SHA256),
        ):
            data = path.read_bytes()
            self.assertEqual(len(data), size)
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_released_source_and_recovered_configuration_are_explicit(self):
        upstream = UPSTREAM_PORT.read_text(encoding="utf-8")
        portmacro = UPSTREAM_PORTMACRO.read_text(encoding="utf-8")
        for fragment in (
            "void vPortYield( void )",
            "portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT;",
            "void vPortEnterCritical( void )",
            "portDISABLE_INTERRUPTS();",
            "ulCriticalNesting++;",
            "void vPortExitCritical( void )",
            "configASSERT( ulCriticalNesting );",
            "ulCriticalNesting--;",
            "portENABLE_INTERRUPTS();",
        ):
            self.assertIn(fragment, upstream)
        for fragment in (
            "0xe000ed04",
            "1UL << 28UL",
            "vPortEnterCritical()",
            "vPortExitCritical()",
        ):
            self.assertIn(fragment, portmacro)
        candidate = CANDIDATE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for fragment in (
            "SPDX-License-Identifier: MIT",
            "Permission is hereby granted",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "The production overlay compiles these three entry points",
            "OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() - 1U",
        ):
            self.assertIn(fragment, candidate)
        for fragment in (
            "0xE000ED04U",
            "0x10000000U",
            "0x2000309CU",
            "0x30U",
        ):
            self.assertIn(fragment, header)

    def test_stock_trio_boundaries_literals_and_outgoing_calls_are_exact(self):
        bodies = []
        for contract in STOCK.values():
            body = self.span(contract["start"], contract["end"])
            bodies.append(body)
            self.assertEqual(body.hex(), contract["bytes"])
            self.assertEqual(
                hashlib.sha256(body).hexdigest(), contract["sha256"]
            )
        self.assertEqual(hashlib.sha256(b"".join(bodies)).hexdigest(), TRIO_SHA256)
        self.assertEqual(
            struct.unpack("<I", self.span(
                CRITICAL_NESTING_LITERAL, CRITICAL_NESTING_LITERAL + 4
            ))[0],
            CRITICAL_NESTING_ADDRESS,
        )
        self.assertEqual(
            struct.unpack("<I", self.span(ICSR_LITERAL, ICSR_LITERAL + 4))[0],
            ICSR_ADDRESS,
        )
        self.assertEqual(
            hashlib.sha256(self.span(0x004420A6, YIELD_START)).hexdigest(),
            PREDECESSOR_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.span(TRIO_END, 0x00442134)).hexdigest(),
            SUCCESSOR_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.span(SET_MASK_START, CLEAR_MASK_END)).hexdigest(),
            MASK_PAIR_SHA256,
        )
        for site, target in (
            (0x004420D2, SET_MASK_START),
            (0x004420F2, SET_MASK_START),
            (0x0044210E, CLEAR_MASK_START),
        ):
            encoded = self.span(site, site + 4)
            self.assertEqual(
                self.apollo_overlay.decode_thumb_bl(site, encoded), target
            )

    def test_complete_direct_call_and_interior_entry_topology_is_pinned(self):
        entries = {
            name: (contract["start"], contract["end"])
            for name, contract in STOCK.items()
        }
        calls = {name: [] for name in entries}
        jumps = {name: [] for name in entries}
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            first, second = struct.unpack("<HH", encoded)
            if first & 0xF800 != 0xF000 or second & 0x9000 != 0x9000:
                continue
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    address, encoded
                )
            except self.apollo_overlay.BuildError:
                continue
            destination = calls if second & 0x4000 else jumps
            for name, (start, end) in entries.items():
                if target == start:
                    destination[name].append((address, encoded))
                if start < target < end and not start <= address < end:
                    interior.append((address, target, encoded))
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in self.narrow_branch_targets(address, halfword):
                for start, end in entries.values():
                    if start <= target < end and not start <= address < end:
                        interior.append((address, target, halfword))
        self.assertEqual(interior, [])
        for name in entries:
            self.assertEqual([address for address, _ in calls[name]], CALLERS[name])
            self.assertEqual(jumps[name], [])
            address_payload = b"".join(
                struct.pack("<I", address) for address, _ in calls[name]
            )
            record_payload = b"".join(
                struct.pack("<I", address) + encoded
                for address, encoded in calls[name]
            )
            self.assertEqual(
                hashlib.sha256(address_payload).hexdigest(),
                CALLER_ADDRESS_SHA256[name],
            )
            self.assertEqual(
                hashlib.sha256(record_payload).hexdigest(),
                CALLER_RECORD_SHA256[name],
            )

    def test_stored_pointer_scan_has_no_aligned_entry_or_interior_owner(self):
        matches = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1 if value & 1 else value
            if YIELD_START <= canonical < TRIO_END:
                matches.append((APPLICATION_BASE + offset, value, canonical))
        self.assertEqual(
            [address for address, _, _ in matches],
            RAW_EXIT_INTERIOR_LOCATIONS,
        )
        self.assertTrue(all(address % 2 == 1 for address, _, _ in matches))
        self.assertTrue(
            all(value == 0x004420F0 for _, value, _ in matches)
        )
        self.assertEqual(
            hashlib.sha256(b"".join(
                struct.pack("<III", *record) for record in matches
            )).hexdigest(),
            "ce7c5d1626f4674601c631282988e55400d74fa286ead46cd2d573c4bd23ec4f",
        )

    def test_host_yield_and_enter_preserve_side_effect_ordering(self):
        self.loaded.open_cfw_test_port_reset(7, 0xA5A5A5A5)
        self.loaded.open_cfw_test_port_run_yield()
        self.assertEqual(self.loaded.open_cfw_test_port_icsr(), PENDSVSET_BIT)
        self.assertEqual(self.events(), [(1, PENDSVSET_BIT), (5, 0), (6, 0)])

        self.loaded.open_cfw_test_port_reset(7, 0xA5A5A5A5)
        self.loaded.open_cfw_test_port_run_enter()
        self.assertEqual(self.loaded.open_cfw_test_port_nesting(), 8)
        self.assertEqual(self.loaded.open_cfw_test_port_set_calls(), 1)
        self.assertEqual(
            self.events(),
            [(2, 0xA5A5A5A5), (3, 7), (4, 8), (5, 0), (6, 0)],
        )

        self.loaded.open_cfw_test_port_reset(0xFFFFFFFF, 0x30)
        self.loaded.open_cfw_test_port_run_enter()
        self.assertEqual(self.loaded.open_cfw_test_port_nesting(), 0)
        self.assertEqual(self.events()[1:3], [(3, 0xFFFFFFFF), (4, 0)])

    def test_host_exit_preserves_assert_decrement_and_unmask_ordering(self):
        self.loaded.open_cfw_test_port_reset(2, 0x30)
        self.assertEqual(self.loaded.open_cfw_test_port_run_exit(), 0)
        self.assertEqual(self.loaded.open_cfw_test_port_nesting(), 1)
        self.assertEqual(self.loaded.open_cfw_test_port_clear_calls(), 0)
        self.assertEqual(self.events(), [(3, 2), (3, 2), (4, 1), (3, 1)])

        self.loaded.open_cfw_test_port_reset(1, 0x30)
        self.assertEqual(self.loaded.open_cfw_test_port_run_exit(), 0)
        self.assertEqual(self.loaded.open_cfw_test_port_nesting(), 0)
        self.assertEqual(self.loaded.open_cfw_test_port_clear_calls(), 1)
        self.assertEqual(self.loaded.open_cfw_test_port_clear_value(), 0)
        self.assertEqual(
            self.events(),
            [(3, 1), (3, 1), (4, 0), (3, 0), (7, 0)],
        )

        self.loaded.open_cfw_test_port_reset(0, 0x30)
        self.assertEqual(self.loaded.open_cfw_test_port_run_exit(), 1)
        self.assertEqual(self.loaded.open_cfw_test_port_nesting(), 0)
        self.assertEqual(self.events(), [(3, 0), (8, 0)])

    def test_target_profile_output_symbols_and_relocations_are_exact(self):
        self.assertIn(self.toolchain_profile, ("apple-clang", "linux-clang"))
        for symbol_name, (expected_hex, expected_sha) in TARGET_TEXT.items():
            section_name = ".text." + symbol_name
            body = self.section_bytes(section_name)
            self.assertEqual(body.hex(), expected_hex)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_sha)
            self.assertEqual(int(self.section_by_name[section_name]["alignment"]), 4)
            symbol = self.symbols[symbol_name]
            self.assertEqual(int(symbol[1]), 1)
            self.assertEqual(int(symbol[2]), len(body))
            self.assertEqual(int(symbol[3]) & 0x0F, 2)
            self.assertEqual(
                self.relocations.get(section_name, []),
                TARGET_RELOCATIONS[section_name],
            )
            exidx_name = ".ARM.exidx." + section_name[1:]
            self.assertEqual(
                self.section_bytes(exidx_name),
                bytes.fromhex("0000000001000000"),
            )
            self.assertEqual(
                self.relocations[exidx_name],
                [(0, 42, f"<section:{section_name}>")],
            )
        writable = [
            section["name"]
            for section in self.sections
            if int(section["size"]) and int(section["flags"]) & 0x1
        ]
        self.assertEqual(writable, [])


if __name__ == "__main__":
    unittest.main()
