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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_semaphore_acquire.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_semaphore_acquire_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisSemaphoreAcquireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("sem.dylib" if sys.platform == "darwin" else "sem.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_sem_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        cls.lib.open_cfw_test_sem_call.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
        cls.lib.open_cfw_test_sem_call.restype = ctypes.c_int32
        cls.getters = {}
        for name in ("isr_calls", "task_calls", "pendsv", "queue", "timeout", "buffer"):
            function = getattr(cls.lib, f"open_cfw_test_sem_get_{name}")
            function.restype = ctypes.c_size_t
            cls.getters[name] = function

        target = temporary / "sem.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_semaphore_acquire")
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

    def reset(self, irq=0, isr_result=1, task_result=1, yield_value=0) -> None:
        self.lib.open_cfw_test_sem_reset(irq, isr_result, task_result, yield_value)

    def get(self, name: str) -> int:
        return self.getters[name]()

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (2429, "be223f6079ad88419b03fac01f14f46e56dc25234b6837aed54f9ff5f73e5663"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (2421, "ce479cd4799f3a8b98df656f7d14a514be881f8e89b496a59b6e10d4b5c6f5d7"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x0044994E - 0x00438000:0x004499B8 - 0x00438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (106, "c433dde9706e80eb67706ed801cbf64b544c39c88bab6a946d0fdcd02c23c700"))
        self.assertEqual((len(self.target), hashlib.sha256(self.target).hexdigest()), (108, "fc7ce83a71cb739e35ce79c2fbf5ca918b4d93b8b66bc4444ad28b0dd5ce2c91"))
        self.assertEqual(self.relocations, [(18, 10, "open_cfw_cmsis_irq_context"), (38, 10, "open_cfw_freertos_queue_semaphore_take_upstream_candidate"), (70, 10, "open_cfw_freertos_queue_receive_from_isr")])

    def test_null_handle_is_parameter_error_without_provider_calls(self) -> None:
        self.reset()
        self.assertEqual(self.lib.open_cfw_test_sem_call(0, 4), -4)
        self.assertEqual((self.get("isr_calls"), self.get("task_calls")), (0, 0))

    def test_task_success_and_resource_timeout_mapping(self) -> None:
        for result, timeout, expected in ((1, 0, 0), (0, 0, -3), (0, 7, -2)):
            with self.subTest(result=result, timeout=timeout):
                self.reset(task_result=result)
                self.assertEqual(self.lib.open_cfw_test_sem_call(0xCAFE, timeout), expected)
                self.assertEqual((self.get("task_calls"), self.get("isr_calls"), self.get("queue"), self.get("timeout")), (1, 0, 0xCAFE, timeout))

    def test_isr_rejects_timeout_and_maps_receive_result(self) -> None:
        self.reset(irq=1)
        self.assertEqual(self.lib.open_cfw_test_sem_call(0xCAFE, 1), -4)
        self.assertEqual(self.get("isr_calls"), 0)
        for result, expected in ((0, -3), (1, 0)):
            self.reset(irq=1, isr_result=result)
            self.assertEqual(self.lib.open_cfw_test_sem_call(0xCAFE, 0), expected)
            self.assertEqual((self.get("isr_calls"), self.get("task_calls"), self.get("buffer")), (1, 0, 0))

    def test_isr_yield_sets_pendsv_only_after_success(self) -> None:
        for result, yield_value, expected in ((1, 0, 0), (1, 1, 1), (0, 1, 0)):
            self.reset(irq=1, isr_result=result, yield_value=yield_value)
            self.lib.open_cfw_test_sem_call(1, 0)
            self.assertEqual(self.get("pendsv"), expected)

    def test_production_overlay_and_manifest_admit_acquire(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == "open_cfw_cmsis_semaphore_acquire")
        self.assertEqual(leaf["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
        self.assertEqual(leaf["source"]["upstream_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
        self.assertEqual((leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]), (108, "b2507700dbaf383fe30cf380b81e6c0bf37ccd49af692aed38c77299eaa2e8cc", 133292))
        linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual((linux["size"], linux["sha256"], linux["offset"]), (108, "97a333e6e5d71ea8ca1ab54bc909d12a338f7230a669420770ed6a4ebd5709b7", 135164))
        patch = next(item for item in config["patch_sites"] if item["target_function"] == "open_cfw_cmsis_semaphore_acquire")
        self.assertEqual(patch["runtime_address"], 0x0044994E)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        region = next(item for item in manifest["component_overrides"]["apollo_main"]["regions"] if item["name"] == "apollo_cmsis_semaphore_acquire_source_leaf")
        self.assertEqual((region["file_offset"], region["size"], region["target_address"]), (3656688, 108, 8080336))


if __name__ == "__main__":
    unittest.main()
