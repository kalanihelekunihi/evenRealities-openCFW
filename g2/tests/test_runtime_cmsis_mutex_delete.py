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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_mutex_delete.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_mutex_delete_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


class RuntimeCmsisMutexDeleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("mdelete.dylib" if sys.platform == "darwin" else "mdelete.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(library))
        cls.call = loaded.open_cfw_cmsis_mutex_delete
        cls.call.argtypes = [ctypes.c_void_p]
        cls.call.restype = ctypes.c_int32
        cls.reset = loaded.open_cfw_test_mutex_delete_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.calls = loaded.open_cfw_test_mutex_delete_calls
        cls.calls.restype = ctypes.c_uint32
        cls.handle = loaded.open_cfw_test_mutex_delete_handle
        cls.handle.restype = ctypes.c_size_t

        target = temporary / "leaf.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_mutex_delete")
        cls.body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        cls.relocations = []
        for rs in sections:
            if int(rs["type"]) != 9 or int(rs["info"]) != int(section["index"]): continue
            symbols = sections[int(rs["link"])]
            strings_section = sections[int(symbols["link"])]
            strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
            names = []
            for index in range(int(symbols["size"]) // 16):
                fields = struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)
                names.append(apollo_overlay.elf_string(strings, fields[0], "symbol"))
            for index in range(int(rs["size"]) // 8):
                offset, information = struct.unpack_from("<II", data, int(rs["offset"]) + index * 8)
                cls.relocations.append((offset, information & 0xFF, names[information >> 8]))

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()

    def test_source_fixture_stock_and_target_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (1462, "91d73236a38148437740f7cdb5816acbbe8965991f29a1282271d63193394895"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (726, "b60ae636bfed9efdf3705272269ff52013397d040d5cf51bfaf6ac9d24287370"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x0044986E - 0x00438000:0x0044989A - 0x00438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (44, "649cee0eb99f62128cd191253b2d15f446b0867ab11fd406e36eb2d527102a40"))
        self.assertEqual((len(self.body), hashlib.sha256(self.body).hexdigest()), (38, "a64571d42510649fc779b82295401a6542614657c1f0cce88d072d01aca0568b"))
        self.assertEqual(self.relocations, [(4, 10, "open_cfw_cmsis_irq_context"), (24, 10, "open_cfw_freertos_queue_delete")])

    def test_validation_and_recursive_tag_stripping(self) -> None:
        for irq, handle, status, calls, deleted in [(1, 0x1235, -6, 0, 0), (0, 1, -4, 0, 0), (0, 0x1235, 0, 1, 0x1234)]:
            with self.subTest(irq=irq, handle=handle):
                self.reset(irq)
                self.assertEqual(self.call(ctypes.c_void_p(handle)), status)
                self.assertEqual(self.calls(), calls)
                self.assertEqual(self.handle(), deleted)

    def test_production_registration_is_atomic(self) -> None:
        config = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
        manifest = json.loads((ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text())
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == "open_cfw_cmsis_mutex_delete")
        self.assertEqual(leaf["expected"]["sha256"], "d55a21146fce1f3975eec6ee9c83112cc4350a94197c400a326898a259b6391e")
        self.assertEqual(leaf["toolchain_profiles"]["linux-clang"]["expected"]["sha256"], "48dc2ae50f54f7bea4fc713171129027501c737f3d28a51b21607f046665f696")
        self.assertEqual(sum(site["target_function"] == leaf["function"] for site in config["patch_sites"]), 1)
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        self.assertEqual(sum(region["name"] == "apollo_cmsis_mutex_delete_source_leaf" for region in regions), 1)


if __name__ == "__main__": unittest.main()
