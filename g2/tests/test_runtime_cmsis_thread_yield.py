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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_thread_yield.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_thread_yield_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


class RuntimeCmsisThreadYieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("yield.dylib" if sys.platform == "darwin" else "yield.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(library))
        cls.call = loaded.open_cfw_cmsis_thread_yield
        cls.call.restype = ctypes.c_int32
        cls.reset = loaded.open_cfw_test_cmsis_yield_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.calls = loaded.open_cfw_test_cmsis_yield_calls
        cls.calls.restype = ctypes.c_uint32

        target = temporary / "leaf.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_thread_yield")
        cls.body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        cls.relocations = []
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]): continue
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

    def test_source_fixture_and_stock_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (1748, "c03ff1c35cd5ace0c26d927594960674b6e8a3c0fd1a8fb79f02d3d49c2552a5"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (592, "72702a749dc5d4116b522cd42544872a0bebb820ad727bb62b1f26d6989d33e1"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x004491E4 - 0x00438000:0x004491FE - 0x00438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (26, "b8041c6d93a504e7b04c942da7e83b370bf58ca1d567b2d938587ba8ecf1ffa7"))

    def test_target_closure_is_exact(self) -> None:
        self.assertEqual((len(self.body), hashlib.sha256(self.body).hexdigest()), (24, "603a20d58a9508fe505535ce6e7ab0084dc57f318eff1cfd9a201587926d7b7b"))
        self.assertEqual(self.relocations, [(2, 10, "open_cfw_cmsis_irq_context"), (16, 10, "open_cfw_freertos_port_yield")])

    def test_task_context_yields_once(self) -> None:
        self.reset(0)
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.calls(), 1)

    def test_isr_context_is_rejected(self) -> None:
        self.reset(1)
        self.assertEqual(self.call(), -6)
        self.assertEqual(self.calls(), 0)

    def test_production_registration_is_atomic(self) -> None:
        config = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
        manifest = json.loads((ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text())
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == "open_cfw_cmsis_thread_yield")
        self.assertEqual(leaf["expected"]["sha256"], "06afe2fbd2f46c349f1696fd235e58db5c2aaca8c593b774ca825a7899316bd6")
        self.assertEqual(leaf["toolchain_profiles"]["linux-clang"]["expected"]["sha256"], "1e01b52f42aff4bccd6bea11cf7515e08ad88eefe7de1fefefd579e0d33c9e69")
        self.assertEqual(sum(site["target_function"] == leaf["function"] for site in config["patch_sites"]), 1)
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        self.assertEqual(sum(region["name"] == "apollo_cmsis_thread_yield_source_leaf" for region in regions), 1)


if __name__ == "__main__": unittest.main()
