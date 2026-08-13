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


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components" / "apollo_main" / "core_overlay" /
    "runtime_cmsis_count_leaves.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_cmsis_count_leaves_host.c"
UPSTREAM = (
    ROOT / "third_party" / "cmsis-freertos" / "CMSIS-FreeRTOS" / "CMSIS" /
    "RTOS2" / "FreeRTOS" / "Source" / "cmsis_os2.c"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" /
    "ota_s200_firmware_ota.bin"
)
CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

BASE = 0x0043_8000
STOCK = {
    "open_cfw_cmsis_semaphore_get_count": (
        0x0044_9A0E,
        0x0044_9A32,
        "0b2a6b35d6d4391bb5b28e36399afc11f3d697bd4a88dcf14c9e0169222ef9d0",
    ),
    "open_cfw_cmsis_message_queue_get_count": (
        0x0044_9BC8,
        0x0044_9BEC,
        "6edaf25d5366032cefe8cab997a6a3db472878543f7a42b99f3016eb81c75b56",
    ),
}
LEAVES = {
    "SEMAPHORE": "open_cfw_cmsis_semaphore_get_count",
    "MESSAGE_QUEUE": "open_cfw_cmsis_message_queue_get_count",
}
UNRELOCATED_SIZE = 36
UNRELOCATED_SHA256 = "dcec0ef689e4b3b991f06fe88e61e48d1b9c7a22862c9758d318db3ce524a0aa"
RELOCATIONS = [
    (6, 10, "open_cfw_cmsis_irq_context"),
    (18, 30, "open_cfw_freertos_queue_messages_waiting_from_isr"),
    (32, 30, "open_cfw_freertos_queue_messages_waiting"),
]
SOURCE_SIZE = 3_306
SOURCE_SHA256 = "cb17116f9e29706cb5e43dc718299d97a41db798b2a02905800266e9f9d285bf"
FIXTURE_SHA256 = "230908c5fad4390f80a7393060d205676b729a7ec22ef6e4ac2838d690ef4424"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeCmsisCountLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / (
            "runtime_cmsis_count_leaves.dylib"
            if sys.platform == "darwin"
            else "runtime_cmsis_count_leaves.so"
        )
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_cmsis_count_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.task_calls = cls.loaded.open_cfw_test_cmsis_count_task_calls
        cls.task_calls.restype = ctypes.c_uint32
        cls.isr_calls = cls.loaded.open_cfw_test_cmsis_count_isr_calls
        cls.isr_calls.restype = ctypes.c_uint32
        cls.semaphore = cls.loaded.open_cfw_cmsis_semaphore_get_count
        cls.semaphore.argtypes = [ctypes.c_void_p]
        cls.semaphore.restype = ctypes.c_uint32
        cls.message_queue = cls.loaded.open_cfw_cmsis_message_queue_get_count
        cls.message_queue.argtypes = [ctypes.c_void_p]
        cls.message_queue.restype = ctypes.c_uint32

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.target_results = {}
        for selector, function in LEAVES.items():
            target_object = temporary / f"{selector}.o"
            subprocess.run(
                [
                    clang,
                    *TARGET_FLAGS,
                    "-DOPEN_CFW_CMSIS_COUNT_BUILD_LEAF",
                    f"-DOPEN_CFW_CMSIS_COUNT_LEAF_{selector}",
                    "-c", str(SOURCE), "-o", str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            data, sections = apollo_overlay.parse_elf32(target_object)
            section = apollo_overlay.section_named(sections, f".text.{function}")
            body = data[
                int(section["offset"]):
                int(section["offset"]) + int(section["size"])
            ]
            relocations = []
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) != 9
                    or int(relocation_section["info"]) != int(section["index"])
                ):
                    continue
                symbol_table = sections[int(relocation_section["link"])]
                string_table = sections[int(symbol_table["link"])]
                strings = data[
                    int(string_table["offset"]):
                    int(string_table["offset"]) + int(string_table["size"])
                ]
                names = []
                for index in range(int(symbol_table["size"]) // 16):
                    fields = struct.unpack_from(
                        "<IIIBBH", data, int(symbol_table["offset"]) + index * 16,
                    )
                    names.append(apollo_overlay.elf_string(strings, fields[0], "symbol"))
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data,
                        int(relocation_section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (offset, information & 0xFF, names[information >> 8])
                    )
            cls.target_results[selector] = (body, relocations)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_source_fixture_and_upstream_are_pinned(self) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(FIXTURE), FIXTURE_SHA256)
        self.assertEqual(UPSTREAM.stat().st_size, 70_106)
        self.assertEqual(
            sha256(UPSTREAM),
            "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36",
        )

    def test_both_stock_entries_are_exact(self) -> None:
        for name, (start, end, expected) in STOCK.items():
            with self.subTest(name=name):
                body = self.application[start - BASE:end - BASE]
                self.assertEqual(len(body), 36)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_both_target_leaves_have_identical_bounded_closure(self) -> None:
        for selector, (body, relocations) in self.target_results.items():
            with self.subTest(selector=selector):
                self.assertEqual(len(body), UNRELOCATED_SIZE)
                self.assertEqual(hashlib.sha256(body).hexdigest(), UNRELOCATED_SHA256)
                self.assertEqual(relocations, RELOCATIONS)

    def test_null_handle_returns_zero_without_provider_call(self) -> None:
        for function in (self.semaphore, self.message_queue):
            with self.subTest(function=function.__name__):
                self.reset(0, 17, 29)
                self.assertEqual(function(None), 0)
                self.assertEqual(self.task_calls(), 0)
                self.assertEqual(self.isr_calls(), 0)

    def test_task_context_uses_normal_provider(self) -> None:
        for function in (self.semaphore, self.message_queue):
            with self.subTest(function=function.__name__):
                self.reset(0, 17, 29)
                self.assertEqual(function(ctypes.c_void_p(0x1234)), 17)
                self.assertEqual(self.task_calls(), 1)
                self.assertEqual(self.isr_calls(), 0)

    def test_irq_context_uses_isr_provider(self) -> None:
        for function in (self.semaphore, self.message_queue):
            with self.subTest(function=function.__name__):
                self.reset(1, 17, 29)
                self.assertEqual(function(ctypes.c_void_p(0x1234)), 29)
                self.assertEqual(self.task_calls(), 0)
                self.assertEqual(self.isr_calls(), 1)

    def test_production_overlay_and_manifest_register_both_leaves(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaves = {leaf["function"]: leaf for leaf in config["relocated_leaves"]}
        patches = {site["target_function"]: site for site in config["patch_sites"]}
        for function, (start, end, stock_hash) in STOCK.items():
            self.assertIn(function, leaves)
            self.assertEqual(leaves[function]["source"]["path"], str(SOURCE.relative_to(ROOT)))
            self.assertEqual(leaves[function]["source"]["sha256"], SOURCE_SHA256)
            self.assertEqual(patches[function]["runtime_address"], start)
            self.assertEqual(patches[function]["expected_size"], end - start)
            self.assertEqual(patches[function]["expected_sha256"], stock_hash)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        names = {
            region["name"]
            for region in manifest["component_overrides"]["apollo_main"]["regions"]
        }
        self.assertIn("apollo_cmsis_semaphore_get_count_source_leaf", names)
        self.assertIn("apollo_cmsis_message_queue_get_count_source_leaf", names)


if __name__ == "__main__":
    unittest.main()
