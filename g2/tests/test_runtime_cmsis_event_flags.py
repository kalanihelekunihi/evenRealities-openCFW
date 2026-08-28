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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_event_flags.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_event_flags_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

STOCK = {
    "open_cfw_cmsis_event_flags_new": (0x449590, 0x4495E4, "6dfae64ebf472c51d4105d50434acfccd26b723a6d6da790eee981a529f4ed83"),
    "open_cfw_cmsis_event_flags_set": (0x4495E4, 0x449642, "11de6c596381befd11300bd6383f97b334847c3eafc74a7392bfe956629acce7"),
    "open_cfw_cmsis_event_flags_clear": (0x449642, 0x449694, "40de3905b1832d076c51eed224d82c791e472d36de1ec4307b57cd518e54e647"),
    "open_cfw_cmsis_event_flags_wait": (0x44969C, 0x44971C, "55efe563c27f16d40c0488e9a86351c934313b894a1428c89ddde96194ea8a08"),
}

TARGET = {
    "open_cfw_cmsis_event_flags_new": (46, "bd2e832709a840738c5295716eedddcc84609b9df0859a0b4fd769c00e808e5b", [(4, 10, "open_cfw_cmsis_irq_context"), (30, 30, "open_cfw_rtos_event_group_static_create"), (42, 30, "open_cfw_rtos_event_group_dynamic_create")]),
    "open_cfw_cmsis_event_flags_set": (96, "7d4aad54dc932207023f964dba1d0d89298e85b3ff0839e8959cd94d35f5d3bf", [(26, 10, "open_cfw_cmsis_irq_context"), (38, 10, "open_cfw_rtos_event_group_set_from_isr"), (46, 10, "open_cfw_rtos_event_group_get_bits_from_isr"), (84, 30, "open_cfw_rtos_event_group_set")]),
    "open_cfw_cmsis_event_flags_clear": (84, "e5ef32883674a2f55872c54e44cfb2b421a05013d21d591490721bd15cae8841", [(24, 10, "open_cfw_cmsis_irq_context"), (32, 10, "open_cfw_rtos_event_group_get_bits_from_isr"), (42, 10, "open_cfw_rtos_event_group_clear_from_isr"), (74, 30, "open_cfw_rtos_event_group_clear")]),
    "open_cfw_cmsis_event_flags_wait": (108, "631e010562314a31075733e5d62f3dad99252b032732a0f84fa2410506d66049", [(28, 10, "open_cfw_cmsis_irq_context"), (74, 10, "open_cfw_rtos_event_group_wait")]),
}

APPLE_LINKED = {
    "open_cfw_cmsis_event_flags_new": "9384df0fd67281679e892b0ff2d56ea93d5973a9f7ff2a84b4efb1c7aa2403ef",
    "open_cfw_cmsis_event_flags_set": "cfafe4800b70542164196782e26393b1456f27a1616258226c8267d7bcc7bdbd",
    "open_cfw_cmsis_event_flags_clear": "74a50cafe379d32e425861d1ece6e4fd617f3b10045ffd5c4c65ce2cb44c92b9",
    "open_cfw_cmsis_event_flags_wait": "beebdf924c3402ae52381289c0189168b53fb9208a66d2eb65a7e5700ec98f46",
}

LINUX_LINKED = {
    "open_cfw_cmsis_event_flags_new": "45d83f93d80793055b5aba49185d74d2969b979f7c2f3f9dfb1c9d551adb2074",
    "open_cfw_cmsis_event_flags_set": "2df6d2df3cc983950e8086bef6e679ff9699089b6ff700aa392474086f7825e8",
    "open_cfw_cmsis_event_flags_clear": "8049f2357fffa5cef2b08543bf9b257e069c1c625a931475d89c8dd47e6cd4c4",
    "open_cfw_cmsis_event_flags_wait": "41a4c4a60035438042aa7e4fa81295dd7f91b6cc3e7048340578623da4381e90",
}


class RuntimeCmsisEventFlagsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("event.dylib" if sys.platform == "darwin" else "event.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_event_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_test_event_new.argtypes = [ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_test_event_new.restype = ctypes.c_void_p
        for name, argc in (("set", 2), ("clear", 2), ("wait", 4)):
            fn = getattr(cls.lib, f"open_cfw_cmsis_event_flags_{name}")
            fn.argtypes = [ctypes.c_void_p, ctypes.c_uint32] + ([ctypes.c_uint32, ctypes.c_uint32] if argc == 4 else [])
            fn.restype = ctypes.c_uint32
        for name in ("call", "bits", "clear_on_exit", "wait_all", "timeout", "pendsv"):
            getattr(cls.lib, f"open_cfw_test_event_{name}").restype = ctypes.c_int64

        target = temporary / "event.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        cls.target = {}
        for function in TARGET:
            section = apollo_overlay.section_named(sections, f".text.{function}")
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            relocations = []
            for relocation_section in sections:
                if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]): continue
                symbols = sections[int(relocation_section["link"])]
                strings_section = sections[int(symbols["link"])]
                strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
                names = [apollo_overlay.elf_string(strings, struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)[0], "symbol") for index in range(int(symbols["size"]) // 16)]
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                    relocations.append((offset, information & 0xFF, names[information >> 8]))
            cls.target[function] = body, relocations

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, irq=0, isr=1, yield_value=0, set_result=0x12, get_result=0x20, clear_result=0x34, wait_result=0x56):
        self.lib.open_cfw_test_event_reset(irq, isr, yield_value, set_result, get_result, clear_result, wait_result)

    def call(self, index: int) -> int:
        return self.lib.open_cfw_test_event_call(index)

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (6667, "7b1aedf76715b46870aea818eb1391221dfae5f290d09af32fa038297c4c7c03"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (3220, "83f80921c5f55b6a17e408d6360adad7cfaa494ec4d2ca54d98089b636e28caf"))
        image = OFFICIAL.read_bytes()[32:]
        for function, (start, end, stock_sha) in STOCK.items():
            with self.subTest(function=function):
                body = image[start - 0x438000:end - 0x438000]
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, stock_sha))
                target, relocations = self.target[function]
                size, sha, expected_relocations = TARGET[function]
                self.assertEqual((len(target), hashlib.sha256(target).hexdigest()), (size, sha))
                self.assertEqual(relocations, expected_relocations)

    def test_new_selects_dynamic_static_invalid_and_irq_paths(self) -> None:
        for irq, cb, size, mode, expected, calls in ((0,0,0,0,0x2468,(0,1)), (0,0x1234,32,1,0x1234,(1,0)), (0,0x1234,31,1,0,(0,0)), (0,0,1,1,0,(0,0)), (1,0,0,0,0,(0,0))):
            with self.subTest(irq=irq, cb=cb, size=size, mode=mode):
                self.reset(irq=irq)
                self.assertEqual(self.lib.open_cfw_test_event_new(cb,size,mode), expected or None)
                self.assertEqual((self.call(0), self.call(1)), calls)

    def test_set_task_isr_validation_failure_and_yield(self) -> None:
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_set(0, 1), 0xFFFFFFFC)
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_set(0x1000, 0x1000000), 0xFFFFFFFC)
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_set(0x1000, 3), 0x12); self.assertEqual(self.call(2), 1)
        self.reset(irq=1,isr=0); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_set(0x1000, 3), 0xFFFFFFFD)
        self.reset(irq=1,isr=1,yield_value=1,get_result=0x20); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_set(0x1000, 3), 0x23); self.assertEqual((self.call(3),self.call(4),self.lib.open_cfw_test_event_pendsv()), (1,1,1))

    def test_clear_task_isr_failure_and_forced_yield(self) -> None:
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_clear(0,1), 0xFFFFFFFC)
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_clear(0x1000,1), 0x34); self.assertEqual(self.call(5),1)
        self.reset(irq=1,isr=0,get_result=0x20); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_clear(0x1000,1),0xFFFFFFFD); self.assertEqual(self.lib.open_cfw_test_event_pendsv(),0)
        self.reset(irq=1,isr=1,get_result=0x20); self.assertEqual(self.lib.open_cfw_cmsis_event_flags_clear(0x1000,1),0x20); self.assertEqual(self.lib.open_cfw_test_event_pendsv(),1)

    def test_wait_options_success_timeout_resource_and_isr(self) -> None:
        wait = self.lib.open_cfw_cmsis_event_flags_wait
        self.reset(); self.assertEqual(wait(0,1,0,0),0xFFFFFFFC)
        self.reset(irq=1); self.assertEqual(wait(0x1000,1,0,0),0xFFFFFFFA)
        self.reset(irq=1); self.assertEqual(wait(0x1000,1,0,2),0xFFFFFFFC)
        for options,result,timeout,expected,clear_on_exit,wait_all in ((0,1,0,1,1,0),(1,3,0,3,1,1),(2,1,0,1,0,0),(0,0,0,0xFFFFFFFD,1,0),(0,0,4,0xFFFFFFFE,1,0),(1,1,4,0xFFFFFFFE,1,1)):
            with self.subTest(options=options,result=result,timeout=timeout):
                self.reset(wait_result=result)
                self.assertEqual(wait(0x1000,3,options,timeout),expected)
                self.assertEqual((self.lib.open_cfw_test_event_clear_on_exit(),self.lib.open_cfw_test_event_wait_all(),self.lib.open_cfw_test_event_timeout()),(clear_on_exit,wait_all,timeout))

    def test_production_overlay_and_manifest_admit_event_flags(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaves = {item["function"]: item for item in config["relocated_leaves"] if item["function"] in TARGET}
        self.assertEqual(set(leaves), set(TARGET))
        self.assertEqual({item["target_function"] for item in config["patch_sites"]} & set(TARGET), set(TARGET))
        for name, item in leaves.items():
            with self.subTest(name=name):
                self.assertEqual(item["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
                self.assertEqual(item["source"]["sha256"], "7b1aedf76715b46870aea818eb1391221dfae5f290d09af32fa038297c4c7c03")
                self.assertEqual(item["source"]["upstream_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
                self.assertEqual(item["expected"]["sha256"], APPLE_LINKED[name])
                self.assertEqual(item["toolchain_profiles"]["linux-clang"]["expected"]["sha256"], LINUX_LINKED[name])
        self.assertEqual(config["expected"]["component_size"], 3_952_346)
        self.assertEqual(config["toolchain_profiles"]["linux-clang"]["expected"]["component_size"], 3_728_356)

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        region_names = {item["name"] for item in main["regions"]}
        self.assertTrue({"apollo_cmsis_event_flags_new_source_leaf", "apollo_cmsis_event_flags_set_source_leaf", "apollo_cmsis_event_flags_clear_source_leaf", "apollo_cmsis_event_flags_wait_source_leaf"}.issubset(region_names))


if __name__ == "__main__":
    unittest.main()
