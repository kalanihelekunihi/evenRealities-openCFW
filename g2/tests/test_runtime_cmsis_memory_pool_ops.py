from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_memory_pool_ops.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_memory_pool_ops_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FUNCTION_PINS = {
    "open_cfw_cmsis_memory_pool_create_block": (28, "6581e2670d9d8b879a1e2b3d08c236301e29a3e234e93ae9d07838e62fbc1089"),
    "open_cfw_cmsis_memory_pool_alloc_block": (14, "5e4f31b882999b063cbf299ea839c111a0064f085f2950ac826b634ec4c6d75a"),
    "open_cfw_cmsis_memory_pool_free_block": (8, "27aa0f47deea05a316c7884bc0c03fc7213ef15943c97e602872743697375f32"),
    "open_cfw_cmsis_memory_pool_alloc": (144, "e7e4ffb55568567abcab1dcfda35081d6191072f923dd1186e204c63619d1424"),
    "open_cfw_cmsis_memory_pool_free": (198, "d29de1cbc9551f587588c047069ea7a9047dd675feeddc5132891477c3d0a0e8"),
}


class RuntimeCmsisMemoryPoolOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("pool_ops.dylib" if sys.platform == "darwin" else "pool_ops.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_pool_ops_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32]
        cls.lib.open_cfw_test_pool_ops_set_status.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_pool_ops_set_head.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_test_pool_ops_alloc.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_pool_ops_alloc.restype = ctypes.c_size_t
        cls.lib.open_cfw_test_pool_ops_alloc_null.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_pool_ops_alloc_null.restype = ctypes.c_size_t
        cls.lib.open_cfw_test_pool_ops_free.argtypes = [ctypes.c_int32]
        cls.lib.open_cfw_test_pool_ops_free.restype = ctypes.c_int32
        cls.lib.open_cfw_test_pool_ops_free_null_pool.restype = ctypes.c_int32
        cls.lib.open_cfw_test_pool_ops_head_offset.restype = ctypes.c_int32
        cls.getters = {}
        for name in ("index", "take_calls", "isr_take_calls", "count_calls", "isr_count_calls", "give_calls", "isr_give_calls", "enter_calls", "exit_calls", "set_mask_calls", "clear_mask_calls", "pendsv"):
            function = getattr(cls.lib, f"open_cfw_test_pool_ops_{name}" if name == "index" else f"open_cfw_test_pool_ops_get_{name}")
            function.restype = ctypes.c_uint32
            cls.getters[name] = function

        target = temporary / "pool_ops.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        cls.target = {}
        for function in FUNCTION_PINS:
            section = apollo_overlay.section_named(sections, f".text.{function}")
            cls.target[function] = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, irq=0, take=1, count=0, give=1, yield_value=0, invalidate=0) -> None:
        self.lib.open_cfw_test_pool_ops_reset(irq, take, count, give, yield_value, invalidate)

    def get(self, name: str) -> int:
        return self.getters[name]()

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (7637, "5c493699b0b539dbb1a42da23208d86a82fcbe6e386c97077c7a9a1417aff2d7"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (8133, "f87cfb51cf7e2a04fc156d3718bd66f1b8596c276e8e333e22d9678db6e96514"))
        image = OFFICIAL.read_bytes()[32:]
        stock_pins = (
            (0x00449D3E, 0x00449DD0, "048b16e65e5ea016a21f9061a83050d478077dba03ad165003c9c8e757913913"),
            (0x00449DD4, 0x00449E8E, "aa5d91c466dd3682f69892e9a19af8fd75c713afcf8938a601c1a8c550cf87e3"),
            (0x00449E98, 0x00449EB8, "d7701236547d60b1b890714e47bffb75daf6ce2c6d0493d4c3a7bfeaf4c54e06"),
            (0x00449EB8, 0x00449ECA, "b3c8efce0ea52d40cabb82e0e1cf6c24dee8b41b00eb94e33ca0562d05ad19d4"),
            (0x00449ECA, 0x00449ED2, "b91ff75c6b7ce4dba1f345e295ac3279f3aa2a6ada13b73105bbb40f78a37cca"),
        )
        for start, end, digest in stock_pins:
            body = image[start - 0x00438000:end - 0x00438000]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, digest))
        for function, pin in FUNCTION_PINS.items():
            body = self.target[function]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), pin)

    def test_task_alloc_creates_blocks_and_prefers_free_list(self) -> None:
        self.reset()
        self.assertEqual((self.lib.open_cfw_test_pool_ops_alloc(7), self.get("index")), (0, 1))
        self.assertEqual((self.lib.open_cfw_test_pool_ops_alloc(7), self.get("index")), (4, 2))
        self.assertEqual((self.get("take_calls"), self.get("enter_calls"), self.get("exit_calls")), (2, 2, 2))
        self.reset()
        self.lib.open_cfw_test_pool_ops_set_head(8, 12)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(0), 8)
        self.assertEqual((self.lib.open_cfw_test_pool_ops_head_offset(), self.get("index")), (12, 0))

    def test_alloc_validation_take_failure_recheck_and_isr_timeout(self) -> None:
        self.reset()
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc_null(0), 0)
        self.lib.open_cfw_test_pool_ops_set_status(0)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(0), ctypes.c_size_t(-1).value)
        self.reset(take=0)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(5), ctypes.c_size_t(-1).value)
        self.reset(invalidate=1)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(5), ctypes.c_size_t(-1).value)
        self.assertEqual(self.get("enter_calls"), 0)
        self.reset(irq=1)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(1), ctypes.c_size_t(-1).value)
        self.assertEqual(self.get("isr_take_calls"), 0)

    def test_isr_alloc_uses_mask_and_null_wake_pointer_path(self) -> None:
        self.reset(irq=1)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_alloc(0), 0)
        self.assertEqual((self.get("isr_take_calls"), self.get("take_calls"), self.get("set_mask_calls"), self.get("clear_mask_calls")), (1, 0, 1, 1))

    def test_task_free_validates_range_capacity_and_preserves_interior_quirk(self) -> None:
        self.reset(count=4)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_free(0), -3)
        self.reset()
        self.assertEqual(self.lib.open_cfw_test_pool_ops_free_null_pool(), -4)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_free(-1), -4)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_free(64), -4)
        self.assertEqual(self.lib.open_cfw_test_pool_ops_free(1), 0)
        self.assertEqual((self.lib.open_cfw_test_pool_ops_head_offset(), self.get("give_calls"), self.get("enter_calls"), self.get("exit_calls")), (1, 1, 1, 1))

    def test_isr_free_uses_count_mask_give_and_conditional_pendsv(self) -> None:
        for yield_value, expected_pendsv in ((0, 0), (1, 1)):
            self.reset(irq=1, yield_value=yield_value)
            self.assertEqual(self.lib.open_cfw_test_pool_ops_free(4), 0)
            self.assertEqual((self.get("isr_count_calls"), self.get("count_calls"), self.get("set_mask_calls"), self.get("clear_mask_calls"), self.get("isr_give_calls"), self.get("pendsv")), (1, 0, 1, 1, 1, expected_pendsv))

    def test_production_overlay_and_manifest_admit_complete_pool_ops(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        names = set(FUNCTION_PINS)
        leaves = {item["function"]: item for item in config["relocated_leaves"] if item["function"] in names}
        self.assertEqual(set(leaves), names)
        apple = {
            "open_cfw_cmsis_memory_pool_create_block": (28, "6581e2670d9d8b879a1e2b3d08c236301e29a3e234e93ae9d07838e62fbc1089", 133400),
            "open_cfw_cmsis_memory_pool_alloc_block": (14, "5e4f31b882999b063cbf299ea839c111a0064f085f2950ac826b634ec4c6d75a", 133428),
            "open_cfw_cmsis_memory_pool_free_block": (8, "27aa0f47deea05a316c7884bc0c03fc7213ef15943c97e602872743697375f32", 133444),
            "open_cfw_cmsis_memory_pool_alloc": (144, "f279adc27f5f4ffb1874da6ab34f0e0270304162237716d13e9de04828fa1500", 133452),
            "open_cfw_cmsis_memory_pool_free": (198, "d32f164a973d081f1d5b2b0bcaf468427de3203abd0e091da8e9d128ed93fba6", 133596),
        }
        linux = {
            "open_cfw_cmsis_memory_pool_create_block": (30, "f93336fe60fce969b06c6b8ec256c0f060211351a8b772f938058150c2dfb11c", 135272),
            "open_cfw_cmsis_memory_pool_alloc_block": (14, "5e4f31b882999b063cbf299ea839c111a0064f085f2950ac826b634ec4c6d75a", 135304),
            "open_cfw_cmsis_memory_pool_free_block": (8, "27aa0f47deea05a316c7884bc0c03fc7213ef15943c97e602872743697375f32", 135320),
            "open_cfw_cmsis_memory_pool_alloc": (144, "ce6e8726f1faf4aec581f97ce9c60270dd615676c736c706373bd720f4ef15fa", 135328),
            "open_cfw_cmsis_memory_pool_free": (198, "89122db987d67267d9e8f8d4475062b408bf704e06da8de22aef366746e33f4d", 135472),
        }
        for function in names:
            leaf = leaves[function]
            self.assertEqual(leaf["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
            self.assertEqual((leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]), apple[function])
            profile = leaf["toolchain_profiles"]["linux-clang"]["expected"]
            self.assertEqual((profile["size"], profile["sha256"], profile["offset"]), linux[function])
        patches = {item["target_function"]: item["runtime_address"] for item in config["patch_sites"] if item["target_function"] in names}
        self.assertEqual(patches, {
            "open_cfw_cmsis_memory_pool_alloc": 0x00449D3E,
            "open_cfw_cmsis_memory_pool_free": 0x00449DD4,
            "open_cfw_cmsis_memory_pool_create_block": 0x00449E98,
            "open_cfw_cmsis_memory_pool_alloc_block": 0x00449EB8,
            "open_cfw_cmsis_memory_pool_free_block": 0x00449ECA,
        })
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = {item["name"]: item for item in main["regions"]}
        self.assertEqual((regions["apollo_cmsis_memory_pool_create_block_source_leaf"]["file_offset"], regions["apollo_cmsis_memory_pool_free_source_leaf"]["file_offset"]), (3656796, 3656992))
        self.assertEqual((main["provider"]["size"], main["provider"]["profiles"]["linux-clang"]["size"]), (3883974, 3676308))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["profiles"]["linux-clang"]["expected_size"]), (4677046, 4469364))


if __name__ == "__main__":
    unittest.main()
