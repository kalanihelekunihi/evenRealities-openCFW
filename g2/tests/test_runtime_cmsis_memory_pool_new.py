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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_memory_pool_new.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_memory_pool_new_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
TARGET_SIZE = 254
TARGET_SHA256 = "8ff778cf06ce1652e66b260a59b6f277295b727688d5c2ae080ea8250f96fca3"
TARGET_RELOCATIONS = [
    (12, 10, "open_cfw_cmsis_irq_context"),
    (88, 10, "open_cfw_freertos_heap4_malloc"),
    (136, 10, "open_cfw_freertos_queue_create_counting_semaphore_static"),
    (156, 10, "open_cfw_freertos_heap4_malloc"),
    (242, 10, "open_cfw_freertos_heap4_free"),
]


class RuntimeCmsisMemoryPoolNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("mpool.dylib" if sys.platform == "darwin" else "mpool.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_mpool_reset.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_size_t]
        cls.lib.open_cfw_test_mpool_call.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_size_t]
        cls.lib.open_cfw_test_mpool_call.restype = ctypes.c_void_p
        cls.getters = {}
        for name in ("malloc_calls", "free_calls", "sem_calls", "first_size", "second_size", "freed", "sem_buffer", "sem_maximum", "sem_initial", "static_control", "static_array", "head", "sem", "mem_arr", "mem_sz", "name", "block_size", "block_count", "index", "status"):
            function = getattr(cls.lib, f"open_cfw_test_mpool_{name}")
            function.restype = ctypes.c_size_t
            cls.getters[name] = function

        target = temporary / "mpool.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_memory_pool_new")
        cls.target = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        cls.relocations = []
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]): continue
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

    def get(self, name: str) -> int:
        return self.getters[name]()

    def reset(self, irq=0, malloc_fail=0, sem_fail=0, stale=0) -> None:
        self.lib.open_cfw_test_mpool_reset(irq, malloc_fail, sem_fail, stale)

    def call(self, count=3, size=5, attr=0, cb=0, cb_size=0, array=0, array_size=0, name=0):
        return self.lib.open_cfw_test_mpool_call(count, size, attr, cb, cb_size, array, array_size, name)

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (5668, "7f39930cd3a7a6532d733d443efb211c40594d116ec17d03c2ccb0602a732bb1"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (4155, "4f4f6dcd73eec33401c571576a534a26410923a0f936966ab20db7adcf577ae4"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x449C14 - 0x438000:0x449D3E - 0x438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (298, "c108de1748627d51427e2771a74fe9b3ddcd5b53c5816ebb2f82972e8bdc6136"))
        self.assertEqual((len(self.target), hashlib.sha256(self.target).hexdigest(), self.relocations), (TARGET_SIZE, TARGET_SHA256, TARGET_RELOCATIONS))

    def test_rejects_irq_and_zero_dimensions_without_side_effects(self) -> None:
        for irq, count, size in ((1, 3, 5), (0, 0, 5), (0, 3, 0)):
            self.reset(irq=irq)
            self.assertIsNone(self.call(count=count, size=size))
            self.assertEqual((self.get("malloc_calls"), self.get("sem_calls")), (0, 0))

    def test_dynamic_pool_rounds_array_and_sets_allocation_flags(self) -> None:
        self.reset()
        pool = self.call(count=3, size=5)
        self.assertIsNotNone(pool)
        self.assertEqual((self.get("malloc_calls"), self.get("first_size"), self.get("second_size")), (2, 116, 24))
        self.assertEqual((self.get("sem_calls"), self.get("sem_maximum"), self.get("sem_initial")), (1, 3, 3))
        self.assertEqual((self.get("head"), self.get("sem"), self.get("mem_sz"), self.get("block_size"), self.get("block_count"), self.get("index"), self.get("status")), (0, 0x5150, 24, 5, 3, 0, 0x5EED0003))

    def test_static_and_mixed_storage_modes(self) -> None:
        self.reset()
        self.assertEqual(self.call(count=4, size=7, attr=1, cb=1, cb_size=116, array=1, array_size=32, name=0xA5), self.get("static_control"))
        self.assertEqual((self.get("malloc_calls"), self.get("mem_arr"), self.get("mem_sz"), self.get("name"), self.get("status")), (0, self.get("static_array"), 32, 0xA5, 0x5EED0000))
        self.reset()
        self.call(attr=1, cb=0, cb_size=0, array=1, array_size=24)
        self.assertEqual((self.get("malloc_calls"), self.get("status")), (1, 0x5EED0001))
        self.reset()
        self.call(attr=1, cb=1, cb_size=116, array=0, array_size=0)
        self.assertEqual((self.get("malloc_calls"), self.get("status")), (1, 0x5EED0002))

    def test_preserves_v1051_nonnull_undersized_buffer_selection(self) -> None:
        self.reset()
        self.assertEqual(self.call(attr=1, cb=1, cb_size=115, array=1, array_size=1), self.get("static_control"))
        self.assertEqual((self.get("mem_arr"), self.get("status")), (self.get("static_array"), 0x5EED0000))
        self.reset()
        self.assertIsNone(self.call(attr=1, cb=0, cb_size=1, array=1, array_size=24))
        self.assertEqual(self.get("sem_calls"), 0)

    def test_allocation_and_semaphore_failures_cleanup_only_dynamic_control(self) -> None:
        self.reset(malloc_fail=1)
        self.assertIsNone(self.call())
        self.assertEqual((self.get("sem_calls"), self.get("free_calls")), (0, 0))
        self.reset(malloc_fail=2)
        self.assertIsNone(self.call())
        self.assertEqual((self.get("sem_calls"), self.get("free_calls")), (1, 1))
        self.reset(sem_fail=1)
        self.assertIsNone(self.call())
        self.assertEqual(self.get("free_calls"), 1)
        self.reset(sem_fail=1, stale=0xCAFE)
        self.assertEqual(self.call(attr=1, cb=1, cb_size=116, array=1, array_size=24), self.get("static_control"))
        self.assertEqual((self.get("sem"), self.get("mem_arr"), self.get("status")), (0, 0xCAFE, 0x5EED0000))

    def test_production_overlay_and_manifest_admit_constructor(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaf = next(
            item
            for item in config["relocated_leaves"]
            if item["function"] == "open_cfw_cmsis_memory_pool_new"
        )
        patch = next(
            item
            for item in config["patch_sites"]
            if item["target_function"] == "open_cfw_cmsis_memory_pool_new"
        )
        self.assertEqual(patch["runtime_address"], 0x00449C14)
        self.assertEqual(leaf["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
        self.assertEqual(leaf["source"]["upstream_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
        self.assertEqual(
            (leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]),
            (254, "ff4675969e47e4558d41506f657230e7dda578b43b342a0831f830ac777ebe82", 132792),
        )
        linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual(
            (linux["size"], linux["sha256"], linux["offset"]),
            (250, "fc11de9c673f30bef9ccbb880a4d4abd1de2ca27951f32cda68e10f190cb16eb", 134672),
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        region = next(
            item
            for item in main["regions"]
            if item["name"] == "apollo_cmsis_memory_pool_new_source_leaf"
        )
        self.assertEqual(
            (region["file_offset"], region["size"], region["target_address"]),
            (3_656_188, 254, 8_079_836),
        )
        self.assertEqual(
            (main["provider"]["size"], main["provider"]["profiles"]["linux-clang"]["size"]),
            (3_883_974, 3_676_308),
        )
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["profiles"]["linux-clang"]["expected_size"]),
            (4_677_046, 4_469_364),
        )


if __name__ == "__main__":
    unittest.main()
