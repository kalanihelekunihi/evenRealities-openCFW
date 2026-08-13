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
CANDIDATE = (
    ROOT
    / "research"
    / "candidates"
    / "freertos_pc_task_get_name.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "freertos_pc_task_get_name_candidate_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
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

BASE = 0x00438000
START = 0x00454F16
END = 0x00454F38
CURRENT_TCB_WORD = 0x20074A20
CURRENT_TCB_LITERAL = 0x004551A4
NAME_OFFSET = 0x34
STACK_DEPTH_OFFSET = 0x54
STOCK_BYTES = (
    "80b5002802d1a1480068ffe7002806d1"
    "a5f1bdf800205ff0ff310860fee7343002bd"
)
STOCK_SHA256 = (
    "a25ace28ece3ca37f11da7e73945acb2"
    "8f1f99d906203613e9856d2070c07817"
)
CALLERS = [(0x0044AAEE, "0af012fa")]
RAW_POINTER_FALSE_POSITIVE = (0x004A56B7, 0x00454F20)
TARGET_TEXT = (
    "28b944f62020c2f20700006808b13430704700f001f8"
    "00bffff7feff4ff0ff3000210160fee7"
)
TARGET_TEXT_SHA256 = (
    "fb4c24b6071973df5bdae74251b5fc8b"
    "2fe1ccef8d065188398b7b8c8761540d"
)
TARGET_FUNCTION_BYTES = (
    "28b944f62020c2f20700006808b13430704700f001f8"
)
TARGET_FUNCTION_SHA256 = (
    "b25b4e6b432db1958db52b71a623c5a"
    "0b1b71bf119497b4e0f96fab118602d14"
)
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


class FreeRTOSTaskGetNameCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "freertos_pc_task_get_name_candidate.dylib"
            if sys.platform == "darwin"
            else "freertos_pc_task_get_name_candidate.so"
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
        cls.reset = cls.loaded.open_cfw_test_pc_task_get_name_reset
        cls.reset.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls.reset.restype = None
        cls.explicit = cls.loaded.open_cfw_test_pc_task_get_name_explicit
        cls.explicit.argtypes = []
        cls.explicit.restype = ctypes.c_char_p
        cls.current = cls.loaded.open_cfw_test_pc_task_get_name_current
        cls.current.argtypes = []
        cls.current.restype = ctypes.c_char_p
        cls.delta = (
            cls.loaded.open_cfw_test_pc_task_get_name_explicit_delta
        )
        cls.delta.argtypes = []
        cls.delta.restype = ctypes.c_size_t
        cls.mask_calls = (
            cls.loaded.open_cfw_test_pc_task_get_name_mask_calls
        )
        cls.mask_calls.argtypes = []
        cls.mask_calls.restype = ctypes.c_uint32

        cls.target_object = temporary / "candidate.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
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
                (((halfword >> 9) & 1) << 5)
                | ((halfword >> 3) & 0x1F)
            )
            return [address + 4 + immediate * 2]
        return []

    def test_official_package_and_upstream_snapshot_are_authenticated(
        self,
    ) -> None:
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            "19044a72bdfeb04c6b1b104d87da7b98"
            "e13cc18928528d84d999b6bcc0ba9701",
        )
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

    def test_stock_body_boundary_literal_and_outgoing_dependency_are_exact(
        self,
    ) -> None:
        body = self.span(START, END)
        self.assertEqual(len(body), 34)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            hashlib.sha256(self.span(0x00454F10, START)).hexdigest(),
            "43e18c3d205509129b075a8eb8c2c70a"
            "fde30da1b933ac72d2963813aea8cfec",
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x00454F44)).hexdigest(),
            "29d9d5a1c65067aa3d10780636da13d3"
            "1b3fe14eb136d506df195690a0fb497e",
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(CURRENT_TCB_LITERAL, CURRENT_TCB_LITERAL + 4),
            )[0],
            CURRENT_TCB_WORD,
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x005FA0A4, 0x005FA0BA)
            ).hexdigest(),
            "f6bd0708e653c8e8880e33e298f9dc8"
            "ede1305c9386ea4ca5ff554d4022dc323",
        )

    def test_stock_name_writer_proves_offset_and_extension_order(
        self,
    ) -> None:
        self.assertEqual(
            self.span(0x00454976, 0x0045499E).hex(),
            "c6f85490002c0fd0002100e0491c2029"
            "07d2605c06eb010282f83400605c0028"
            "f4d1002086f85300",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00454976, 0x0045499E)
            ).hexdigest(),
            "f59595f8a0b62d16cbeedde20fca564d"
            "9d2687162a2a2bd9208197c382960c10",
        )
        source = UPSTREAM_TASKS.read_text(encoding="utf-8")
        for token in (
            "#define prvGetTCBFromHandle",
            "char * pcTaskGetName( TaskHandle_t xTaskToQuery )",
            "pxTCB = prvGetTCBFromHandle( xTaskToQuery );",
            "configASSERT( pxTCB );",
            "return &( pxTCB->pcTaskName[ 0 ] );",
            "char pcTaskName[ configMAX_TASK_NAME_LEN ];",
        ):
            self.assertIn(token, source)
        candidate = CANDIDATE.read_text(encoding="utf-8")
        self.assertIn("task_name) == 0x34", candidate)
        self.assertIn("sizeof(open_cfw_freertos_tcb_name_prefix) == 0x54", candidate)
        self.assertEqual(NAME_OFFSET, 0x34)
        self.assertEqual(STACK_DEPTH_OFFSET, 0x54)

    def test_only_direct_caller_and_no_external_interior_branch_exist(
        self,
    ) -> None:
        import apollo_overlay

        calls = []
        jumps = []
        interior = []
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
                if target == START:
                    observed.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(calls, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])
        self.assertEqual(
            hashlib.sha256(
                struct.pack("<I", CALLERS[0][0])
            ).hexdigest(),
            "6b6b656546449e21e970d725927d278f"
            "881d1c0bf448fd732bf3759f73366ee4",
        )

    def test_byte_granular_pointer_candidate_is_classified_false(
        self,
    ) -> None:
        possible = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1 if value & 1 else value
            if START <= canonical < END:
                possible.append((BASE + offset, canonical))
        self.assertEqual(possible, [RAW_POINTER_FALSE_POSITIVE])
        self.assertEqual(
            self.span(0x004A56B0, 0x004A56BC).hex(),
            "4c4500204e4500204f450020",
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(0x004A56B4, 0x004A56B8),
            )[0],
            0x2000454E,
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(0x004A56B8, 0x004A56BC),
            )[0],
            0x2000454F,
        )

    def test_host_candidate_preserves_handle_selection_and_name_offset(
        self,
    ) -> None:
        self.reset(b"explicit-task", b"current-task")
        self.assertEqual(self.explicit(), b"explicit-task")
        self.assertEqual(self.current(), b"current-task")
        self.assertEqual(self.delta(), NAME_OFFSET)
        self.assertEqual(self.mask_calls(), 0)

        self.reset(b"x" * 40, b"y" * 40)
        self.assertEqual(self.explicit(), b"x" * 31)
        self.assertEqual(self.current(), b"y" * 31)
        self.assertEqual(self.mask_calls(), 0)

    def test_target_candidate_is_bounded_and_retains_port_relocation(
        self,
    ) -> None:
        self.assertEqual(self.target_text.hex(), TARGET_TEXT)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            TARGET_TEXT_SHA256,
        )
        function = self.symbols[
            "open_cfw_freertos_pc_task_get_name"
        ]
        self.assertEqual(function[1] & ~1, 0)
        self.assertEqual(function[2], 22)
        self.assertEqual(
            self.target_text[:function[2]].hex(),
            TARGET_FUNCTION_BYTES,
        )
        self.assertEqual(
            hashlib.sha256(
                self.target_text[:function[2]]
            ).hexdigest(),
            TARGET_FUNCTION_SHA256,
        )
        assertion = self.symbols[
            "open_cfw_freertos_pc_task_get_name_assert"
        ]
        self.assertEqual(assertion[1] & ~1, 24)
        self.assertEqual(assertion[2], 14)
        mask = self.symbols["ulSetInterruptMask"]
        self.assertEqual(mask[5], 0)
        self.assertEqual(
            self.text_relocations,
            [(0x18, 10, "ulSetInterruptMask")],
        )

    def test_candidate_provenance_and_nonproduction_status_are_pinned(
        self,
    ) -> None:
        self.assertEqual(
            hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            "cd80886bfec8eb99df0a07ca721685f3"
            "87a44c079c1da8139fa944e99ff8a278",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "31f0d146f5d49b39d00dc73cf40b32e3"
            "fc798739e9908f8ee54f24f5f4d7cf8c",
        )
        source = CANDIDATE.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "[0x00454F16, 0x00454F38)",
            "0x20074A20U",
            "ulSetInterruptMask",
            "deliberately not registered by the production overlay",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
