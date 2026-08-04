#!/usr/bin/env python3
"""Read-only compile/ELF audit for three CMSIS-FreeRTOS constructors.

This test compiles the exact authenticated v10.5.1 cmsis_os2.c translation
unit.  It does not link an overlay, modify a firmware image, or claim that
Clang output is byte-identical to the stock IAR output.
"""

from __future__ import annotations

import os

import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLANG = Path(os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"))

CANDIDATE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "candidates"
    / "cmsis_freertos_constructors"
)
CMSIS_SNAPSHOT = ROOT / "third_party" / "cmsis-freertos"
CMSIS_SOURCE = (
    CMSIS_SNAPSHOT
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Source"
    / "cmsis_os2.c"
)
CMSIS_FREERTOS_INCLUDE = (
    CMSIS_SNAPSHOT
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Include"
)
CMSIS_RTOS_INCLUDE = (
    CMSIS_SNAPSHOT / "CMSIS_5" / "CMSIS" / "RTOS2" / "Include"
)
CMSIS_CORE_INCLUDE = (
    CMSIS_SNAPSHOT / "CMSIS_5" / "CMSIS" / "Core" / "Include"
)
FREERTOS = ROOT / "third_party" / "freertos-kernel"
FREERTOS_INCLUDE = FREERTOS / "include"
FREERTOS_PORT = (
    FREERTOS / "portable" / "IAR" / "ARM_CM55_NTZ" / "non_secure"
)

OFFICIAL_PACKAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000

SOURCE_SHA256 = (
    "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36"
)

COMPILE_FLAGS = [
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-std=c11",
    "-Oz",
    "-mno-outline",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-common",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
]

ROOTS = (
    "osMessageQueueNew",
    "osMutexNew",
    "osSemaphoreNew",
)
CODE_SECTIONS = {
    "IRQ_Context": (
        46,
        "b40be5ceee29cd41d4ce92600914b8ab0fae47e8fdcc632e5ee821b39967da44",
    ),
    "osMessageQueueNew": (
        88,
        "3ec0ffdfef3a4455017c88d0ba942973a56baa82c8b208922d03a6cd38607a54",
    ),
    "osMutexNew": (
        98,
        "b1aa7cfad0de5b4cb6069150e2c47d21408b4bf05625264c978ad7eb94f41991",
    ),
    "osSemaphoreNew": (
        138,
        "5771f4d856d66c37aa2194986684712078e3a17b9f58841cf303016b064f5191",
    ),
}

# (offset, ELF32 R_ARM type, symbol)
RELOCATIONS = {
    "IRQ_Context": [
        (0x0C, 10, "xTaskGetSchedulerState"),
    ],
    "osMessageQueueNew": [
        (0x08, 10, "IRQ_Context"),
        (0x34, 10, "xQueueGenericCreateStatic"),
        (0x54, 30, "xQueueGenericCreate"),
    ],
    "osMutexNew": [
        (0x04, 10, "IRQ_Context"),
        (0x28, 10, "xQueueCreateMutexStatic"),
        (0x3A, 10, "xQueueCreateMutex"),
        (0x4E, 30, "xQueueCreateMutex"),
        (0x5E, 30, "xQueueCreateMutexStatic"),
    ],
    "osSemaphoreNew": [
        (0x08, 10, "IRQ_Context"),
        (0x34, 10, "xQueueGenericCreateStatic"),
        (0x48, 10, "xQueueGenericCreate"),
        (0x5E, 10, "xQueueGenericSend"),
        (0x68, 10, "vQueueDelete"),
        (0x78, 30, "xQueueCreateCountingSemaphore"),
        (0x86, 30, "xQueueCreateCountingSemaphoreStatic"),
    ],
}

UNDEFINED_CLOSURES = {
    "osMessageQueueNew": {
        "xTaskGetSchedulerState",
        "xQueueGenericCreateStatic",
        "xQueueGenericCreate",
    },
    "osMutexNew": {
        "xTaskGetSchedulerState",
        "xQueueCreateMutexStatic",
        "xQueueCreateMutex",
    },
    "osSemaphoreNew": {
        "xTaskGetSchedulerState",
        "xQueueGenericCreateStatic",
        "xQueueGenericCreate",
        "xQueueGenericSend",
        "vQueueDelete",
        "xQueueCreateCountingSemaphore",
        "xQueueCreateCountingSemaphoreStatic",
    },
}

STOCK_SPANS = {
    "IRQ_Context": (
        0x0044_900E,
        0x0044_903C,
        "702b19799a5ff8295597cd1b903ba5a5b6f9db91d872fdf311c9221c44660f33",
    ),
    "osMutexNew": (
        0x0044_971C,
        0x0044_97B6,
        "09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec",
    ),
    "osSemaphoreNew": (
        0x0044_989A,
        0x0044_994E,
        "ebdcf69b866e35e468ba9ce84d7e7ac9b58377b5ffcc439762d729f7d99a098c",
    ),
    "osMessageQueueNew": (
        0x0044_9A32,
        0x0044_9ABE,
        "52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class CmsisFreeRTOSConstructorCompileClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.temporary = tempfile.TemporaryDirectory()
        cls.object_path = Path(cls.temporary.name) / "cmsis_os2.o"

        command = [
            str(CLANG),
            *COMPILE_FLAGS,
            "-include",
            str(CANDIDATE / "cmsis_freertos_target.h"),
        ]
        for include in (
            CANDIDATE,
            FREERTOS_INCLUDE,
            FREERTOS_PORT,
            CMSIS_FREERTOS_INCLUDE,
            CMSIS_RTOS_INCLUDE,
            CMSIS_CORE_INCLUDE,
        ):
            command.extend(("-I", str(include)))
        command.extend(("-c", str(CMSIS_SOURCE), "-o", str(cls.object_path)))

        cls.compile = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.compile.returncode:
            raise AssertionError(
                "exact cmsis_os2.c compile failed:\n"
                + (cls.compile.stderr or cls.compile.stdout)
            )

        cls.elf, cls.sections = apollo_overlay.parse_elf32(cls.object_path)
        cls.symbols = apollo_overlay.parse_elf32_symbols(
            cls.elf,
            cls.sections,
        )
        cls.sections_by_name = {
            str(section["name"]): section for section in cls.sections
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def section_bytes(cls, name: str) -> bytes:
        section = cls.sections_by_name[name]
        start = int(section["offset"])
        return cls.elf[start:start + int(section["size"])]

    @classmethod
    def relocations_for(cls, function: str) -> list[tuple[int, int, str]]:
        text = cls.sections_by_name[f".text.{function}"]
        relocation = cls.sections_by_name[f".rel.text.{function}"]
        if int(relocation["info"]) != int(text["index"]):
            raise AssertionError(
                f"{relocation['name']} does not target {text['name']}"
            )
        if int(relocation["entry_size"]) != 8:
            raise AssertionError(
                f"{relocation['name']} is not an ELF32 REL table"
            )
        result: list[tuple[int, int, str]] = []
        for entry in range(
            int(relocation["offset"]),
            int(relocation["offset"]) + int(relocation["size"]),
            8,
        ):
            offset, info = struct.unpack_from("<II", cls.elf, entry)
            symbol = cls.symbols[info >> 8]
            result.append((offset, info & 0xFF, str(symbol["name"])))
        return result

    def test_authenticated_inputs_and_no_rte_guess(self) -> None:
        self.assertEqual(sha256(CMSIS_SOURCE.read_bytes()), SOURCE_SHA256)

        for verifier in (
            CMSIS_SNAPSHOT / "verify_snapshot.py",
            FREERTOS / "verify_snapshot.py",
        ):
            completed = subprocess.run(
                [sys.executable, str(verifier)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stderr or completed.stdout,
            )
            self.assertIn(": OK", completed.stdout)

        config = (CANDIDATE / "FreeRTOSConfig.h").read_text()
        port = (CANDIDATE / "portmacro.h").read_text()
        target = (CANDIDATE / "cmsis_freertos_target.h").read_text()
        self.assertNotIn("#define configENABLE_MVE", config)
        self.assertNotIn("_RTE_", config + port + target)
        self.assertIn("#define configMINIMAL_STACK_SIZE", config)
        self.assertIn("0x400U", config)
        self.assertIn("#define configTIMER_TASK_STACK_DEPTH", config)
        self.assertIn("0x1000U", config)
        self.assertIn("#define configQUEUE_REGISTRY_SIZE", config)
        self.assertIn("SystemCoreClock", config)
        self.assertIn('include "portmacrocommon.h"', port)

    def test_stock_spans_and_recovered_stack_depths_are_pinned(self) -> None:
        package = OFFICIAL_PACKAGE.read_bytes()
        self.assertEqual(len(package), PACKAGE_SIZE)
        self.assertEqual(sha256(package), PACKAGE_SHA256)
        application = package[PACKAGE_PREAMBLE:]

        for start, end, expected_hash in STOCK_SPANS.values():
            span = application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]
            self.assertEqual(len(span), end - start)
            self.assertEqual(sha256(span), expected_hash)

        idle_callback = application[
            0x0048_D558 - APPLICATION_BASE:
            0x0048_D568 - APPLICATION_BASE
        ]
        timer_callback = application[
            0x004D_3610 - APPLICATION_BASE:
            0x004D_3620 - APPLICATION_BASE
        ]
        self.assertEqual(
            idle_callback.hex(),
            "034b0360034808604ff4806010607047",
        )
        self.assertEqual(
            timer_callback.hex(),
            "034b0360034808604ff4805010607047",
        )

    @_APPLE_ONLY
    def test_exact_source_compiles_into_isolated_constructor_sections(self) -> None:
        self.assertEqual(self.compile.stderr, "")
        self.assertEqual(self.elf[:4], b"\x7fELF")

        for function, (expected_size, expected_hash) in CODE_SECTIONS.items():
            code = self.section_bytes(f".text.{function}")
            self.assertEqual(len(code), expected_size)
            self.assertEqual(
                sha256(code),
                expected_hash,
                "compiler-stability pin only; not a stock byte-identity claim",
            )

        # Joint executable closure: 3 roots plus the shared IRQ helper.
        self.assertEqual(sum(size for size, _digest in CODE_SECTIONS.values()), 370)

    def test_relocation_and_undefined_symbol_closures_are_exact(self) -> None:
        for function, expected in RELOCATIONS.items():
            self.assertEqual(self.relocations_for(function), expected)

        symbols_by_name = {
            str(symbol["name"]): symbol for symbol in self.symbols
        }
        irq = symbols_by_name["IRQ_Context"]
        self.assertNotEqual(int(irq["section_index"]), 0)

        for root in ROOTS:
            undefined: set[str] = set()
            pending = [root]
            visited: set[str] = set()
            while pending:
                function = pending.pop()
                if function in visited:
                    continue
                visited.add(function)
                for _offset, _kind, name in self.relocations_for(function):
                    symbol = symbols_by_name[name]
                    if int(symbol["section_index"]) == 0:
                        undefined.add(name)
                    elif name in RELOCATIONS:
                        pending.append(name)
            self.assertEqual(undefined, UNDEFINED_CLOSURES[root])

    def test_retained_constructor_closure_has_no_rodata_or_writable_data(self) -> None:
        closed_functions = {"IRQ_Context", *ROOTS}
        closed_section_indexes = {
            int(self.sections_by_name[f".text.{name}"]["index"])
            for name in closed_functions
        }

        referenced_data_sections: set[str] = set()
        for function in closed_functions:
            for _offset, _kind, name in self.relocations_for(function):
                symbol = next(
                    item for item in self.symbols if item["name"] == name
                )
                section_index = int(symbol["section_index"])
                if section_index not in (0, *closed_section_indexes):
                    referenced_data_sections.add(
                        str(self.sections[section_index]["name"])
                    )
        self.assertEqual(referenced_data_sections, set())

        # Apple Clang still emits one 8-byte read-only EHABI exidx section per
        # function despite the no-unwind flags.  No root reaches writable data.
        for function in closed_functions:
            exidx = self.sections_by_name[f".ARM.exidx.text.{function}"]
            self.assertEqual(int(exidx["size"]), 8)
            self.assertFalse(int(exidx["flags"]) & 1)  # SHF_WRITE

        whole_tu_bss = {
            name: int(section["size"])
            for name, section in self.sections_by_name.items()
            if name.startswith(".bss.")
        }
        self.assertEqual(
            whole_tu_bss,
            {
                ".bss.KernelState": 4,
                ".bss.vApplicationGetIdleTaskMemory.Idle_TCB": 108,
                ".bss.vApplicationGetIdleTaskMemory.Idle_Stack": 4096,
                ".bss.vApplicationGetTimerTaskMemory.Timer_TCB": 108,
                ".bss.vApplicationGetTimerTaskMemory.Timer_Stack": 16384,
            },
        )
        self.assertEqual(sum(whole_tu_bss.values()), 20_700)

    def test_candidate_output_is_explicitly_not_stock_byte_identity(self) -> None:
        stock_sizes = {
            name: end - start
            for name, (start, end, _digest) in STOCK_SPANS.items()
        }
        for name in ("osMessageQueueNew", "osMutexNew", "osSemaphoreNew"):
            candidate_size = len(self.section_bytes(f".text.{name}"))
            self.assertNotEqual(candidate_size, stock_sizes[name])
            self.assertNotEqual(
                CODE_SECTIONS[name][1],
                STOCK_SPANS[name][2],
            )


if __name__ == "__main__":
    unittest.main()
