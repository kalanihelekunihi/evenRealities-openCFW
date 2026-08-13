from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_task_count.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_task_count_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_FREERTOS_H = (
    ROOT / "third_party" / "freertos-kernel" / "include" / "FreeRTOS.h"
)
UPSTREAM_PORTMACROCOMMON = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portmacrocommon.h"
)
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
RECOVERED_CONFIG = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "candidates"
    / "cmsis_freertos_constructors"
    / "FreeRTOSConfig.h"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OFFICIAL_PROVENANCE = OFFICIAL.parent / "PROVENANCE.md"

BASE = 0x00438000
TICK_START = 0x00454EFE
TICK_END = 0x00454F06
TICK_ISR_START = TICK_END
TICK_ISR_INTERIOR = 0x00454F08
TICK_ISR_END = 0x00454F10
TICK_COUNT_WORD = 0x20074A34
TICK_COUNT_LITERAL = 0x004557AC
TICK_BYTES = "dff8ac0800687047"
TICK_SHA256 = (
    "6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0"
)
TICK_ISR_BYTES = "0020dff8a00800687047"
TICK_ISR_SHA256 = (
    "8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a"
)
TICK_PAIR_SHA256 = (
    "d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077"
)
START = 0x00454F10
END = 0x00454F16
TASK_COUNT_WORD = 0x20074A30
TASK_COUNT_LITERAL = 0x004551A0
STOCK_BYTES = "a34800687047"
STOCK_SHA256 = (
    "43e18c3d205509129b075a8eb8c2c70afde30da1b933ac72d2963813aea8cfec"
)
TARGET_BYTES = "44f63020c2f2070000687047"
TARGET_SHA256 = (
    "1f9b9ecb6dcd1ec096f881d9f2c53d3fefe72abdbd7a569a6fb2583fd426a2b9"
)
TICK_CALLERS = [
    (0x004490DC, "0bf00fff"),
    (0x004492F6, "0bf002fe"),
    (0x0044933E, "0bf0defd"),
    (0x0047DC7C, "d7f73ff9"),
    (0x0047E91A, "d6f7f0fa"),
    (0x004C6932, "8ef7e4fa"),
    (0x0052A4AE, "2af726fd"),
    (0x0052A576, "2af7c2fc"),
    (0x00576084, "def63bff"),
]
TICK_ISR_CALLERS = [(0x004490D6, "0bf016ff")]
CALLERS = [
    (0x00441A06, "13f083fa"),
    (0x00441AD2, "13f01dfa"),
    (0x00441E2A, "13f071f8"),
    (0x0059446E, "c0f64ffd"),
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
    "-Wall",
    "-Wextra",
    "-Werror",
]


class RuntimeFreeRTOSTaskCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_task_count.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_task_count.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
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
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.set_count = cls.loaded.open_cfw_test_freertos_task_count_set
        cls.set_count.argtypes = [ctypes.c_uint32]
        cls.set_count.restype = None
        cls.get_count = cls.loaded.open_cfw_test_freertos_task_count_get
        cls.get_count.argtypes = []
        cls.get_count.restype = ctypes.c_uint32
        cls.count_reads = cls.loaded.open_cfw_test_freertos_task_count_reads
        cls.count_reads.argtypes = []
        cls.count_reads.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_task_count.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.text_relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.text_relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_official_package_and_source_snapshot_are_authenticated(
        self,
    ) -> None:
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            "19044a72bdfeb04c6b1b104d87da7b98"
            "e13cc18928528d84d999b6bcc0ba9701",
        )
        provenance = OFFICIAL_PROVENANCE.read_bytes()
        self.assertEqual(len(provenance), 1_438)
        self.assertEqual(
            hashlib.sha256(provenance).hexdigest(),
            "53c3819fb9cf9cc819861787a14fa84f6"
            "e084cf03396a3a5636718f8539f6809",
        )
        provenance_text = provenance.decode("utf-8")
        for token in (
            "version: `s200_v2.2.6.10`",
            "size: 4,301,227 bytes",
            "`ota_s200_firmware_ota.bin` | 3,523,396",
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        ):
            self.assertIn(token, provenance_text)
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            hashlib.sha256(UPSTREAM_TASKS.read_bytes()).hexdigest(),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

    def test_vendored_source_and_recovered_config_explain_tick_shape(
        self,
    ) -> None:
        tasks = UPSTREAM_TASKS.read_text(encoding="utf-8").replace(
            "\r\n",
            "\n",
        )
        self.assertIn(
            """TickType_t xTaskGetTickCount( void )
{
    TickType_t xTicks;

    /* Critical section required if running on a 16 bit processor. */
    portTICK_TYPE_ENTER_CRITICAL();
    {
        xTicks = xTickCount;
    }
    portTICK_TYPE_EXIT_CRITICAL();

    return xTicks;
}""",
            tasks,
        )
        self.assertIn(
            """    portASSERT_IF_INTERRUPT_PRIORITY_INVALID();

    uxSavedInterruptStatus = portTICK_TYPE_SET_INTERRUPT_MASK_FROM_ISR();
    {
        xReturn = xTickCount;
    }
    portTICK_TYPE_CLEAR_INTERRUPT_MASK_FROM_ISR( uxSavedInterruptStatus );

    return xReturn;""",
            tasks,
        )

        portmacro = UPSTREAM_PORTMACROCOMMON.read_bytes()
        self.assertEqual(len(portmacro), 12_636)
        self.assertEqual(
            hashlib.sha256(portmacro).hexdigest(),
            "c184e6b1727732bbdd0d4dd33b9af4e"
            "a25d13040620666123941fff464bffc99",
        )
        portmacro_text = portmacro.decode("utf-8")
        for token in (
            "#if ( configUSE_16_BIT_TICKS == 1 )",
            "typedef uint16_t     TickType_t;",
            "typedef uint32_t     TickType_t;",
            "#define portTICK_TYPE_IS_ATOMIC    1",
        ):
            self.assertIn(token, portmacro_text)

        freertos_h = UPSTREAM_FREERTOS_H.read_bytes()
        self.assertEqual(len(freertos_h), 51_577)
        self.assertEqual(
            hashlib.sha256(freertos_h).hexdigest(),
            "03e9c94aba57e3cf7f4f73bc2d3eb4a9"
            "6ae38f3425eedb5450622ca286475a0b",
        )
        freertos_h_text = freertos_h.decode("utf-8")
        for token in (
            "#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID()",
            "#define portTICK_TYPE_ENTER_CRITICAL()",
            "#define portTICK_TYPE_EXIT_CRITICAL()",
            "#define portTICK_TYPE_SET_INTERRUPT_MASK_FROM_ISR()         0",
            "#define portTICK_TYPE_CLEAR_INTERRUPT_MASK_FROM_ISR( x )"
            "    ( void ) ( x )",
        ):
            self.assertIn(token, freertos_h_text)

        config = RECOVERED_CONFIG.read_bytes()
        self.assertEqual(len(config), 5_184)
        self.assertEqual(
            hashlib.sha256(config).hexdigest(),
            "537e12cd879b06d7748f9b0e177f6ad0"
            "e17cd176405945771580e6d9c8312889",
        )
        config_text = config.decode("utf-8")
        self.assertIn(
            "#define configUSE_16_BIT_TICKS                   0",
            config_text,
        )
        self.assertIn(
            "not yet claim a complete byte-identical G2 FreeRTOSConfig.h",
            config_text,
        )

    def test_adjacent_tick_getters_have_exact_source_boundaries(
        self,
    ) -> None:
        tick = self.span(TICK_START, TICK_END)
        self.assertEqual(len(tick), 8)
        self.assertEqual(tick.hex(), TICK_BYTES)
        self.assertEqual(hashlib.sha256(tick).hexdigest(), TICK_SHA256)

        tick_isr = self.span(TICK_ISR_START, TICK_ISR_END)
        self.assertEqual(len(tick_isr), 10)
        self.assertEqual(tick_isr.hex(), TICK_ISR_BYTES)
        self.assertEqual(
            hashlib.sha256(tick_isr).hexdigest(),
            TICK_ISR_SHA256,
        )
        pair = self.span(TICK_START, TICK_ISR_END)
        self.assertEqual(len(pair), 18)
        self.assertEqual(
            hashlib.sha256(pair).hexdigest(),
            TICK_PAIR_SHA256,
        )

        self.assertEqual(tick_isr[:2].hex(), "0020")
        self.assertEqual(
            self.span(TICK_ISR_INTERIOR, TICK_ISR_INTERIOR + 4).hex(),
            "dff8a008",
        )
        self.assertNotEqual(TICK_ISR_INTERIOR, TICK_ISR_START)

        normal_immediate = struct.unpack("<H", tick[:2])[0]
        self.assertEqual(normal_immediate, 0xF8DF)
        normal_operand = struct.unpack("<H", tick[2:4])[0]
        self.assertEqual(normal_operand >> 12, 0)
        normal_literal = (
            ((TICK_START + 4) & ~3) + (normal_operand & 0x0FFF)
        )
        self.assertEqual(normal_literal, TICK_COUNT_LITERAL)

        isr_immediate = struct.unpack("<H", tick_isr[2:4])[0]
        self.assertEqual(isr_immediate, 0xF8DF)
        isr_operand = struct.unpack("<H", tick_isr[4:6])[0]
        self.assertEqual(isr_operand >> 12, 0)
        isr_literal = (
            ((TICK_ISR_INTERIOR + 4) & ~3)
            + (isr_operand & 0x0FFF)
        )
        self.assertEqual(isr_literal, TICK_COUNT_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(TICK_COUNT_LITERAL, TICK_COUNT_LITERAL + 4),
            )[0],
            TICK_COUNT_WORD,
        )

    def test_stock_body_bytes_hash_and_neighbors_are_exact(self) -> None:
        body = self.span(START, END)
        self.assertEqual(len(body), 6)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            hashlib.sha256(self.span(TICK_ISR_START, START)).hexdigest(),
            TICK_ISR_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x00454F38)).hexdigest(),
            "a25ace28ece3ca37f11da7e73945acb28"
            "f1f99d906203613e9856d2070c07817",
        )

    def test_stock_literal_names_the_current_task_count_word(self) -> None:
        instruction = struct.unpack("<H", self.span(START, START + 2))[0]
        self.assertEqual(instruction & 0xF800, 0x4800)
        self.assertEqual(instruction & 0x00FF, 0xA3)
        pc = (START + 4) & ~3
        literal = pc + (instruction & 0x00FF) * 4
        self.assertEqual(literal, TASK_COUNT_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(literal, literal + 4),
            )[0],
            TASK_COUNT_WORD,
        )
        self.assertEqual(self.span(START + 2, END).hex(), "00687047")

    def test_stock_writer_seams_confirm_live_task_population_role(
        self,
    ) -> None:
        self.assertEqual(
            self.span(0x00454A04, 0x00454A0E).hex(),
            "dff898170868401c0860",
        )
        create_literal = ((0x00454A04 + 4) & ~3) + 0x798
        self.assertEqual(create_literal, TASK_COUNT_LITERAL)

        self.assertEqual(
            self.span(0x00454B00, 0x00454B0A).hex(),
            "dff89c060168491e0160",
        )
        immediate_delete_literal = (
            ((0x00454B00 + 4) & ~3) + 0x69C
        )
        self.assertEqual(immediate_delete_literal, TASK_COUNT_LITERAL)

        self.assertEqual(
            self.span(0x004556F6, 0x00455700).hex(),
            "dff848090168491e0160",
        )
        deferred_delete_literal = (
            ((0x004556F6 + 4) & ~3) + 0x948
        )
        self.assertEqual(deferred_delete_literal, 0x00456040)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(
                    deferred_delete_literal,
                    deferred_delete_literal + 4,
                ),
            )[0],
            TASK_COUNT_WORD,
        )

    def test_host_candidate_returns_one_unsigned_word_read(self) -> None:
        for count in (0, 1, 2, 40, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF):
            with self.subTest(count=count):
                self.set_count(count)
                self.assertEqual(self.get_count(), count)
                self.assertEqual(self.count_reads(), 1)

    def test_target_candidate_is_one_bounded_relocation_free_leaf(
        self,
    ) -> None:
        function = self.symbols[
            "open_cfw_freertos_task_get_number_of_tasks"
        ]
        self.assertEqual((function[1], function[2]), (1, 12))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(self.target_text.hex(), TARGET_BYTES)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            TARGET_SHA256,
        )
        self.assertEqual(self.text_relocations, [])
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )
        self.assertEqual(
            {
                name
                for name, fields in self.symbols.items()
                if fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {"open_cfw_freertos_task_get_number_of_tasks"},
        )

    def test_source_is_a_pinned_upstream_algorithm_with_one_g2_seam(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "5cae3cac2e72f532844feac5eab4ab76"
            "2c7cb82e2c90ae4015f6ce24a48605ac",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "4f03a8934f3e128c64478408dd4b1ca0"
            "ad60b4ec52cf62edc754dd00fcf3bcea",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "uxTaskGetNumberOfTasks()",
            "tasks.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00454F10, 0x00454F16)",
            "0x20074A30U",
            "return OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT",
        ):
            self.assertIn(token, source)
        for disallowed in (
            "#include",
            "struct ",
            "->",
            "typedef void (*",
        ):
            self.assertNotIn(disallowed, source)

    def test_whole_image_direct_branch_topology_is_closed(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        entries = (TICK_START, TICK_ISR_START, TICK_ISR_INTERIOR, START)
        calls = {entry: [] for entry in entries}
        jumps = {entry: [] for entry in entries}
        interior = []
        tick_pair_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target in observed:
                    observed[target].append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )
                if (
                    TICK_START < target < TICK_ISR_END
                    and target != TICK_ISR_START
                    and not TICK_START <= address < TICK_ISR_END
                ):
                    tick_pair_interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(calls[TICK_START], TICK_CALLERS)
        self.assertEqual(calls[TICK_ISR_START], TICK_ISR_CALLERS)
        self.assertEqual(calls[TICK_ISR_INTERIOR], [])
        self.assertEqual(calls[START], CALLERS)
        self.assertEqual(jumps, {entry: [] for entry in entries})
        self.assertEqual(interior, [])
        self.assertEqual(tick_pair_interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in TICK_CALLERS
                )
            ).hexdigest(),
            "3b032511b7c47b3afe47149262380345e"
            "354dea6d00f2b9dda369d10ce89abcd",
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in TICK_ISR_CALLERS
                )
            ).hexdigest(),
            "e0dffc68b479317c00622e60e6d668de"
            "40625b43703d204f3800a0d4d337e14d",
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in CALLERS
                )
            ).hexdigest(),
            "b046158abaf3afa64a28952e51e719cb"
            "87acade8a1c757395d91c398accca7e9",
        )

        narrow_references = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if (
                    (
                        START <= target < END
                        and not START <= address < END
                    )
                    or (
                        TICK_START <= target < TICK_ISR_END
                        and not TICK_START <= address < TICK_ISR_END
                    )
                ):
                    narrow_references.append((address, target, halfword))
        self.assertEqual(narrow_references, [])

    def test_whole_image_has_no_stored_entry_or_interior_pointer(
        self,
    ) -> None:
        raw_stored = []
        tick_entries = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value in (
                TICK_START,
                TICK_START | 1,
                TICK_ISR_START,
                TICK_ISR_START | 1,
                TICK_ISR_INTERIOR,
                TICK_ISR_INTERIOR | 1,
            ):
                tick_entries.append((BASE + offset, value))
            if value in (START, START | 1):
                raw_stored.append((BASE + offset, value))
            if START < value < END:
                raw_stored.append((BASE + offset, value))
            if value & 1 and START < (value & ~1) < END:
                raw_stored.append((BASE + offset, value))
        self.assertEqual(raw_stored, [])
        self.assertEqual(tick_entries, [])

    @staticmethod
    def narrow_branch_targets(
        address: int,
        halfword: int,
    ) -> list[int]:
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
                ((halfword >> 9) & 1) << 6
                | ((halfword >> 3) & 0x1F) << 1
            )
            return [address + 4 + immediate]
        return []


if __name__ == "__main__":
    unittest.main()
