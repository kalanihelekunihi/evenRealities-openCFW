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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_message_queue_delete.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_message_queue_delete_host.c"
UPSTREAM = ROOT / "third_party/cmsis-freertos/CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

STOCK_START = 0x0044_9BEC
STOCK_END = 0x0044_9C14
STOCK_SHA256 = "dc66684591191cbe28c76ffd3154eef13bd038db3bde6184e65b4cca6a336212"
SOURCE_SHA256 = "2a58f7ecbbc10e3a36430c5afbbd78483475afa68baf0023cd6d587c10846994"
FIXTURE_SHA256 = "82f864f48f6072b66f373db6192eaf3a6f67d013284ff218b2b30c8c190c8b9f"
TARGET_SHA256 = "2630db26e0e251aae8f4e6548ee2e318a3a81a708fbfc281145d104023ec6282"
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeCmsisMessageQueueDeleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("mq_delete.dylib" if sys.platform == "darwin" else "mq_delete.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.delete = cls.loaded.open_cfw_cmsis_message_queue_delete
        cls.delete.argtypes = [ctypes.c_void_p]
        cls.delete.restype = ctypes.c_int32
        cls.reset = cls.loaded.open_cfw_test_cmsis_mq_delete_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.calls = cls.loaded.open_cfw_test_cmsis_mq_delete_calls
        cls.calls.restype = ctypes.c_uint32
        cls.deleted = cls.loaded.open_cfw_test_cmsis_mq_deleted_queue
        cls.deleted.restype = ctypes.c_size_t

        target = temporary / "leaf.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_message_queue_delete")
        cls.body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        cls.relocations = []
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                continue
            symbols = sections[int(relocation_section["link"])]
            strings_section = sections[int(symbols["link"])]
            strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
            names = []
            for index in range(int(symbols["size"]) // 16):
                fields = struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)
                names.append(apollo_overlay.elf_string(strings, fields[0], "symbol"))
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                cls.relocations.append((offset, information & 0xFF, names[information >> 8]))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_source_fixture_and_upstream_are_pinned(self) -> None:
        self.assertEqual(SOURCE.stat().st_size, 2254)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(FIXTURE), FIXTURE_SHA256)
        self.assertEqual(sha256(UPSTREAM), "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36")

    def test_complete_stock_entry_is_exact(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        body = application[STOCK_START - 0x0043_8000:STOCK_END - 0x0043_8000]
        self.assertEqual(len(body), 40)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

    def test_target_leaf_and_relocations_are_exact(self) -> None:
        self.assertEqual(len(self.body), 36)
        self.assertEqual(hashlib.sha256(self.body).hexdigest(), TARGET_SHA256)
        self.assertEqual(self.relocations, [(4, 10, "open_cfw_cmsis_irq_context"), (22, 10, "open_cfw_freertos_queue_delete")])

    def test_isr_precedes_null_validation(self) -> None:
        self.reset(1)
        self.assertEqual(self.delete(None), -6)
        self.assertEqual(self.calls(), 0)

    def test_task_null_is_parameter_error(self) -> None:
        self.reset(0)
        self.assertEqual(self.delete(None), -4)
        self.assertEqual(self.calls(), 0)

    def test_task_delete_forwards_handle_once(self) -> None:
        self.reset(0)
        self.assertEqual(self.delete(ctypes.c_void_p(0x1234)), 0)
        self.assertEqual(self.calls(), 1)
        self.assertEqual(self.deleted(), 0x1234)

    def test_production_registration_is_atomic(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        function = "open_cfw_cmsis_message_queue_delete"
        leaves = {leaf["function"]: leaf for leaf in config["relocated_leaves"]}
        patches = {site["target_function"]: site for site in config["patch_sites"]}
        self.assertEqual(leaves[function]["source"]["sha256"], SOURCE_SHA256)
        self.assertEqual(patches[function]["runtime_address"], STOCK_START)
        self.assertEqual(patches[function]["expected_size"], 40)
        names = {region["name"] for region in json.loads(MANIFEST.read_text(encoding="utf-8"))["component_overrides"]["apollo_main"]["regions"]}
        self.assertIn("apollo_cmsis_message_queue_delete_source_leaf", names)


if __name__ == "__main__":
    unittest.main()
