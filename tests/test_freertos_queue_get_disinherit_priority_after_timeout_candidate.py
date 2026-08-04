from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "components" / "shared" / "freertos"
    / "runtime_freertos_queue_get_disinherit_priority_after_timeout.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_queue_get_disinherit_priority_after_timeout_candidate_host.c"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
PRODUCTION_QUEUE_SOURCE = (
    ROOT / "components" / "apollo_main" / "core_overlay"
    / "runtime_freertos_queue.c"
)
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

SOURCE_SIZE = 2_620
SOURCE_SHA256 = "37a4ea5a258befb3b607bf5b0c3e6f28b60ed11279b98e13910e0a125519db3a"
HEADER_SIZE = 4_456
HEADER_SHA256 = "cd97393461faefa962b91b286977226e1e7c3f1e3dc5a5167c415d5e33c5bd1f"
HOST_FIXTURE_SIZE = 3_214
HOST_FIXTURE_SHA256 = "720ca6753e4b92e05313fa0d2911c218bc55e0b4cd06757237d83a9c447b9ce6"
UPSTREAM_SIZE = 125_614
UPSTREAM_SHA256 = "5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894"

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
APPLICATION_SHA256 = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
START = 0x0044_1EC4
END = 0x0044_1ED8
STOCK_BYTES = "416a002904d0006b0068d0f1380000e000207047"
STOCK_SHA256 = "21721e8f80852df9a1d4f0f23db76d3144a4c8c04a81606dccee5b3ff132819c"
CALLER = 0x0044_1D90
CALLER_ENCODING = "00f098f8"
CALLER_START = 0x0044_1C44
CALLER_END = 0x0044_1DA6
CALLER_SHA256 = "4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c"
CALLER_ADDRESS_SHA256 = "25ca43d09e0faba36b1006f32225b564051e8eef631986dbdd473da20700ec1d"
CALLER_RECORD_SHA256 = "95c27cb70bd833d0db95c2934751679b9b3357f598b8782c324277d24f3dcc0b"
PREDECESSOR_START = 0x0044_1EA2
PREDECESSOR_SHA256 = "ab55f9fa6eb823935056d4b4030cc10df52bc8b33318abea201e61348a026bc4"
SUCCESSOR_END = 0x0044_1F5E
SUCCESSOR_SHA256 = "35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36"

FUNCTION = "open_cfw_freertos_queue_get_disinherit_priority_after_timeout"
FUNCTION_SECTION = ".text." + FUNCTION
TARGET_FUNCTION_BYTES = "416a00290fbf0020006b0068c0f138007047"
TARGET_FUNCTION_SHA256 = "fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519"
TARGETS = {
    "apple-clang": {
        "size": 18,
        "alignment": 4,
        "hex": TARGET_FUNCTION_BYTES,
        "sha256": TARGET_FUNCTION_SHA256,
    },
    "linux-clang": {
        "size": 18,
        "alignment": 4,
        "hex": TARGET_FUNCTION_BYTES,
        "sha256": TARGET_FUNCTION_SHA256,
    },
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


def sha256(data: bytes | Path) -> str:
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        (imm10 << 12) | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5) |
            ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


class FreeRTOSQueueDisinheritPriorityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed target compiler: {version!r}")

        library = temporary / library_name("freertos_disinherit_candidate")
        host_command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            str(HOST_FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.candidate = cls.loaded.open_cfw_test_disinherit_candidate
        cls.oracle = cls.loaded.open_cfw_test_disinherit_oracle
        for function in (cls.candidate, cls.oracle):
            function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            function.restype = ctypes.c_uint32

        cls.target_objects = [temporary / "candidate-1.o", temporary / "candidate-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.elf_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_objects[0]
        )
        symbol_table = apollo_overlay.section_named(cls.sections, ".symtab")
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.elf_data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.elf_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields for name, fields in cls.parsed_symbols if name
        }
        cls.relocations = []
        for section in cls.sections:
            if int(section["type"]) != 9:
                continue
            target = cls.sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    cls.elf_data,
                    int(section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    (
                        str(section["name"]), str(target["name"]), offset,
                        information & 0xFF,
                        cls.parsed_symbols[information >> 8][0],
                    )
                )

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def test_authenticated_upstream_candidate_and_recovered_abi_are_pinned(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_QUEUE.stat().st_size, UPSTREAM_SIZE)
        self.assertEqual(sha256(UPSTREAM_QUEUE), UPSTREAM_SHA256)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        for path, size, digest in (
            (SOURCE, SOURCE_SIZE, SOURCE_SHA256),
            (HEADER, HEADER_SIZE, HEADER_SHA256),
            (HOST_FIXTURE, HOST_FIXTURE_SIZE, HOST_FIXTURE_SHA256),
        ):
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)

        upstream = UPSTREAM_QUEUE.read_text(encoding="utf-8")
        for token in (
            "static UBaseType_t prvGetDisinheritPriorityAfterTimeout(",
            "listCURRENT_LIST_LENGTH( &( pxQueue->xTasksWaitingToReceive ) ) > 0U",
            "configMAX_PRIORITIES - ( UBaseType_t ) listGET_ITEM_VALUE_OF_HEAD_ENTRY",
            "uxHighestPriorityOfWaitingTasks = tskIDLE_PRIORITY;",
            "return uxHighestPriorityOfWaitingTasks;",
        ):
            self.assertIn(token, upstream)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "prvGetDisinheritPriorityAfterTimeout()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00441EC4, 0x00441ED8)",
            "OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE(queue)",
            "Production binds the source-owned semaphore-take call directly",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_DISINHERIT_MAX_PRIORITIES = 56U",
            "OPEN_CFW_FREERTOS_DISINHERIT_RECEIVE_WAIT_OFFSET = 0x24U",
            "OPEN_CFW_FREERTOS_DISINHERIT_HEAD_POINTER_OFFSET = 0x30U",
            "sizeof(struct open_cfw_freertos_disinherit_list_item_layout) == 20U",
            "_Alignof(struct open_cfw_freertos_disinherit_list_item_layout) == 4U",
            "sizeof(struct open_cfw_freertos_disinherit_list_layout) == 20U",
            "_Alignof(struct open_cfw_freertos_disinherit_list_layout) == 4U",
        ):
            self.assertIn(token, header)

    def test_pristine_oracle_equivalence_covers_empty_nonempty_and_edges(
        self,
    ) -> None:
        cases = [
            (0, 0),
            (0, 0xFFFF_FFFF),
            (1, 0),
            (1, 1),
            (1, 55),
            (1, 56),
            (1, 57),
            (1, 0xFFFF_FFFF),
            (2, 7),
            (0xFFFF_FFFF, 32),
        ]
        for number_of_items, head_item_value in cases:
            with self.subTest(
                number_of_items=number_of_items,
                head_item_value=head_item_value,
            ):
                candidate = int(self.candidate(number_of_items, head_item_value))
                oracle = int(self.oracle(number_of_items, head_item_value))
                expected = (
                    (56 - head_item_value) & 0xFFFF_FFFF
                    if number_of_items > 0 else 0
                )
                self.assertEqual(candidate, oracle)
                self.assertEqual(candidate, expected)

    def test_official_body_boundary_and_upstream_operations_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 20)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        self.assertEqual(
            sha256(self.span(PREDECESSOR_START, START)),
            PREDECESSOR_SHA256,
        )
        self.assertEqual(
            sha256(self.span(END, SUCCESSOR_END)),
            SUCCESSOR_SHA256,
        )

        # LDR queue+0x24, empty branch, LDR queue+0x30, LDR head item +0,
        # RSB #56, join, zero, BX LR.
        self.assertEqual(
            [stock[index:index + 2].hex() for index in range(0, 10, 2)],
            ["416a", "0029", "04d0", "006b", "0068"],
        )
        self.assertEqual(stock[10:14].hex(), "d0f13800")
        self.assertEqual(stock[14:].hex(), "00e000207047")

        outgoing = []
        internal = []
        for offset in range(0, len(stock), 2):
            address = START + offset
            if offset + 4 <= len(stock):
                first, second = struct.unpack_from("<HH", stock, offset)
                for link in (True, False):
                    target = thumb_wide_branch_target(
                        address, first, second, link=link
                    )
                    if target is not None:
                        outgoing.append((address, target, link))
            halfword = struct.unpack_from("<H", stock, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END:
                    internal.append((address, target))
        self.assertEqual(outgoing, [])
        self.assertEqual(
            internal,
            [(0x0044_1EC8, 0x0044_1ED4), (0x0044_1ED2, 0x0044_1ED6)],
        )

    def test_sole_caller_and_whole_image_entry_interior_pointer_closure(
        self,
    ) -> None:
        self.assertEqual(
            sha256(self.span(CALLER_START, CALLER_END)),
            CALLER_SHA256,
        )
        encoding = self.span(CALLER, CALLER + 4)
        self.assertEqual(encoding.hex(), CALLER_ENCODING)
        self.assertEqual(sha256(struct.pack("<I", CALLER)), CALLER_ADDRESS_SHA256)
        self.assertEqual(
            sha256(struct.pack("<I", CALLER) + encoding),
            CALLER_RECORD_SHA256,
        )

        direct_bl = []
        direct_bw = []
        external_interior = []
        external_narrow = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            body = self.application[offset:offset + 4]
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target is None or not START <= target < END:
                    continue
                record = (address, target, body.hex())
                if target == START:
                    (direct_bl if link else direct_bw).append(record)
                elif not START <= address < END:
                    external_interior.append((link, *record))
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END and not START <= address < END:
                    external_narrow.append((address, target, halfword))

        self.assertEqual(
            direct_bl,
            [(CALLER, START, CALLER_ENCODING)],
        )
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(external_narrow, [])

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = self.application.find(needle, position)
                    if position < 0:
                        break
                    stored.append((BASE + position, value, canonical, position % 4))
                    position += 1
        self.assertEqual(stored, [])

    def test_isolated_target_object_is_closed_deterministic_and_profile_pinned(
        self,
    ) -> None:
        for profile, pins in TARGETS.items():
            with self.subTest(recorded_profile=profile):
                recorded = bytes.fromhex(pins["hex"])
                self.assertEqual(len(recorded), pins["size"])
                self.assertEqual(sha256(recorded), pins["sha256"])

        target = TARGETS[self.profile]
        parsed = [
            self.apollo_overlay.parse_elf32(path)
            for path in self.target_objects
        ]
        function_bodies = []
        for data, sections in parsed:
            section = next(
                item for item in sections if item["name"] == FUNCTION_SECTION
            )
            body = data[
                int(section["offset"]):
                int(section["offset"]) + int(section["size"])
            ]
            function_bodies.append(body)
            self.assertEqual(int(section["type"]), 1)
            self.assertEqual(int(section["flags"]), 0x6)
            self.assertEqual(int(section["alignment"]), target["alignment"])
            self.assertEqual(len(body), target["size"])
            self.assertEqual(body.hex(), target["hex"])
            self.assertEqual(sha256(body), target["sha256"])
            executable = [
                item["name"] for item in sections
                if int(item["size"]) > 0 and int(item["flags"]) & 0x4
            ]
            self.assertEqual(executable, [FUNCTION_SECTION])
            writable_allocated = [
                item["name"] for item in sections
                if int(item["size"]) > 0
                and int(item["flags"]) & 0x2
                and int(item["flags"]) & 0x1
            ]
            self.assertEqual(writable_allocated, [])
        self.assertEqual(function_bodies[0], function_bodies[1])

        section = next(
            item for item in self.sections if item["name"] == FUNCTION_SECTION
        )
        fields = self.symbols[FUNCTION]
        self.assertEqual(fields[1] & 1, 1)
        self.assertEqual(fields[2], target["size"])
        self.assertEqual(fields[3] >> 4, 1)
        self.assertEqual(fields[3] & 0xF, 2)
        self.assertEqual(fields[5], int(section["index"]))
        undefined = [
            name for name, symbol in self.parsed_symbols
            if name and symbol[5] == 0
        ]
        self.assertEqual(undefined, [])
        self.assertEqual(len(self.relocations), 1)
        relocation = self.relocations[0]
        self.assertTrue(relocation[0].startswith(".rel.ARM.exidx."))
        self.assertTrue(relocation[1].startswith(".ARM.exidx."))
        self.assertEqual(relocation[2:], (0, 42, ""))
        self.assertFalse(
            any(target_name == FUNCTION_SECTION
                for _, target_name, *_ in self.relocations)
        )

    def test_qualified_helper_is_production_linked_while_stock_stays_opaque(
        self,
    ) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        relative_source = SOURCE.relative_to(ROOT).as_posix()
        self.assertIn(FUNCTION, config["functions"])
        leaves = [
            item for item in config["relocated_leaves"]
            if item.get("function") == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0]["source"]["path"], relative_source)
        self.assertEqual(leaves[0]["relocations"], [])
        self.assertFalse(any(
            item.get("runtime_address") == START or
            item.get("target_function") == FUNCTION
            for item in config["patch_sites"]
        ))
        production_queue_source = PRODUCTION_QUEUE_SOURCE.read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "OPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE",
            production_queue_source,
        )
        self.assertIn("(__UINTPTR_TYPE__)0x00441C45U", production_queue_source)

        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
        provider = manifest["component_overrides"]["apollo_main"]["provider"]
        self.assertEqual(provider["size"], 3_645_114)
        self.assertEqual(
            provider["sha256"],
            "c32ff5c5daf946812df503cfaa328c1c"
            "c22dc4206201da0b752a365f235e0108",
        )
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        covering = [
            item for item in regions
            if item.get("target_address", END) <= START
            and item.get("target_address", END) + item["size"] >= END
        ]
        self.assertEqual(len(covering), 1)
        self.assertEqual(covering[0]["name"],
                         "opaque_between_freertos_queue_delete_and_state_helpers")
        self.assertEqual(covering[0]["address_status"], "official_blob")
        self.assertEqual(covering[0]["target_address"], START)
        self.assertEqual(covering[0]["size"], 306)


if __name__ == "__main__":
    unittest.main()
