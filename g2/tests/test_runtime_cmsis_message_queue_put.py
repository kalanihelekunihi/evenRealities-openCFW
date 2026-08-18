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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_message_queue_put.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_message_queue_put_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisMessageQueuePutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("mq_put.dylib" if sys.platform == "darwin" else "mq_put.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_mq_put_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        cls.lib.open_cfw_mq_put_host_call.argtypes = [ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint8, ctypes.c_uint32]
        cls.lib.open_cfw_mq_put_host_call.restype = ctypes.c_int32
        cls.lib.open_cfw_mq_put_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_mq_put_host_get.restype = ctypes.c_size_t

        target = temporary / "target.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_message_queue_put")
        cls.target = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        cls.relocations = []
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                continue
            symbols = sections[int(relocation_section["link"])]
            strings_section = sections[int(symbols["link"])]
            strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
            names = [apollo_overlay.elf_string(strings, struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)[0], "symbol") for index in range(int(symbols["size"]) // 16)]
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                cls.relocations.append((offset, information & 0xFF, names[information >> 8]))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, irq=0, isr=1, task=1, yield_value=0) -> None:
        self.lib.open_cfw_mq_put_host_reset(irq, isr, task, yield_value)

    def call(self, queue=0x1111, message=0x2222, priority=7, timeout=0) -> int:
        return self.lib.open_cfw_mq_put_host_call(queue, message, priority, timeout)

    def get(self, selector: int) -> int:
        return self.lib.open_cfw_mq_put_host_get(selector)

    def test_source_fixture_stock_target_and_relocations_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (2838, "54c80b6f6f011185bffc7232d29c348d0808c639288af2de91639dd1a6a90f86"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (2291, "11a6b95599b783c2093f5ed9d1ba1e92494eadbbf05e6584b1d6b1193a0bd79b"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x00449ABE - 0x00438000:0x00449B3C - 0x00438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (126, "aba43426edc09754ce5ae6c619ba1bfe1f5ad0f0f36687b4315db9dc32a48998"))
        self.assertEqual((len(self.target), hashlib.sha256(self.target).hexdigest()), (144, "1d06629985e8a227dbc6714e841b462aa3dd0944a4e643cebc8e720dec2b157d"))
        self.assertEqual(self.relocations, [(10, 10, "open_cfw_cmsis_irq_context"), (58, 10, "open_cfw_freertos_queue_generic_send_from_isr"), (106, 10, "open_cfw_freertos_queue_generic_send")])

    def test_isr_parameter_validation_precedes_provider(self) -> None:
        for queue, message, timeout in ((0, 0x2222, 0), (0x1111, 0, 0), (0x1111, 0x2222, 1)):
            self.reset(irq=1)
            self.assertEqual(self.call(queue=queue, message=message, timeout=timeout), -4)
            self.assertEqual((self.get(0), self.get(1)), (0, 0))

    def test_isr_result_and_pendsv_mapping(self) -> None:
        self.reset(irq=1, isr=0, yield_value=1)
        self.assertEqual(self.call(), -3)
        self.assertEqual((self.get(0), self.get(2)), (1, 0))
        self.reset(irq=1, isr=1, yield_value=0)
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.get(2), 0)
        self.reset(irq=1, isr=1, yield_value=1)
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.get(2), 1)

    def test_task_parameter_and_status_mapping(self) -> None:
        self.reset()
        self.assertEqual(self.call(queue=0), -4)
        self.assertEqual(self.call(message=0), -4)
        self.reset(task=0)
        self.assertEqual(self.call(timeout=0), -3)
        self.reset(task=0)
        self.assertEqual(self.call(timeout=9), -2)
        self.reset(task=1)
        self.assertEqual(self.call(timeout=9), 0)

    def test_provider_arguments_and_ignored_priority(self) -> None:
        self.reset(irq=1)
        self.assertEqual(self.call(priority=255), 0)
        self.assertEqual((self.get(3), self.get(4), self.get(6)), (0x1111, 0x2222, 0))
        self.reset()
        self.assertEqual(self.call(priority=255, timeout=42), 0)
        self.assertEqual((self.get(3), self.get(4), self.get(5), self.get(6)), (0x1111, 0x2222, 42, 0))

    def test_production_overlay_and_manifest_admit_message_queue_put(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == "open_cfw_cmsis_message_queue_put")
        self.assertEqual((leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]), (144, "6001c89b532ca414f008b6dbb7bb56d353eb470cce938e1bbddc68aee56577df", 134284))
        linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual((linux["size"], linux["sha256"], linux["offset"]), (144, "b21783a89755996684ed2a5ef1bb5cf14e6e7d848f47072efb462751db5b2de7", 136160))
        patch = next(item for item in config["patch_sites"] if item["target_function"] == "open_cfw_cmsis_message_queue_put")
        self.assertEqual((patch["runtime_address"], patch["expected_size"]), (0x00449ABE, 126))
        self.assertEqual((config["expected"]["overlay_size"], config["expected"]["component_size"]), (143227, 3666623))
        self.assertEqual((config["toolchain_profiles"]["linux-clang"]["expected"]["overlay_size"], config["toolchain_profiles"]["linux-clang"]["expected"]["component_size"]), (144266, 3667662))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        region = next(item for item in main["regions"] if item["name"] == "apollo_cmsis_message_queue_put_source_leaf")
        self.assertEqual((region["file_offset"], region["size"], region["target_address"]), (3657680, 144, 8081328))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]), (4445117, "62569df0c68123922de03f482f0affae3975114186581dd30adce650d45f28f6"))
        self.assertEqual((manifest["package"]["profiles"]["linux-clang"]["expected_size"], manifest["package"]["profiles"]["linux-clang"]["expected_sha256"]), (4446156, "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3"))


if __name__ == "__main__":
    unittest.main()
