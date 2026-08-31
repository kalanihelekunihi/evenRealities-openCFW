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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_kernel_get_state.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_kernel_get_state_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


class RuntimeCmsisKernelGetStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("kstate.dylib" if sys.platform == "darwin" else "kstate.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(library))
        cls.call = loaded.open_cfw_cmsis_kernel_get_state
        cls.call.restype = ctypes.c_int32
        cls.reset = loaded.open_cfw_test_cmsis_kernel_state_reset
        cls.reset.argtypes = [ctypes.c_int32, ctypes.c_int32]

        target = temporary / "leaf.o"
        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        section = apollo_overlay.section_named(sections, ".text.open_cfw_cmsis_kernel_get_state")
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

    def test_source_fixture_and_stock_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (1741, "4a8af24ddb5a0bd0449322f98a681c9903eb6406739a27153cac9b4cccf2e34f"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (541, "8ea9fab4166dcb09db270b85941653f0e4ca80a25425b86a6b9941d258b05bf7"))
        image = OFFICIAL.read_bytes()[32:]
        stock = image[0x0044906C - 0x00438000:0x00449094 - 0x00438000]
        self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (40, "279b1f9ba1e6f1a319637906efa9c1dd9ccbc54e5e343ed60f351d0add2e4dda"))

    def test_target_closure_is_exact(self) -> None:
        self.assertEqual((len(self.body), hashlib.sha256(self.body).hexdigest()), (38, "bdb63a444adb684059befa22bd854d08db9b8dba7b122c436f2de048ae6d3ab0"))
        self.assertEqual(self.relocations, [(2, 10, "open_cfw_freertos_task_get_scheduler_state")])

    def test_scheduler_states_and_prestart_word(self) -> None:
        for scheduler, kernel, expected in [(2, 0, 2), (0, 0, 3), (1, 1, 1), (1, 0, 0), (1, 2, 0)]:
            with self.subTest(scheduler=scheduler, kernel=kernel):
                self.reset(scheduler, kernel)
                self.assertEqual(self.call(), expected)

    def test_production_registration_is_atomic(self) -> None:
        config = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
        manifest = json.loads((ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text())
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == "open_cfw_cmsis_kernel_get_state")
        self.assertEqual(leaf["expected"]["sha256"], "7b4328e12ec4d911c8ae88820c2bf73f661ab233bd144ef57e478037809a7ff7")
        self.assertEqual(leaf["toolchain_profiles"]["linux-clang"]["expected"]["sha256"], "b0cd0bb92000f35609928d234c561af59ddfee0d4036641e2674a35c93563b2f")
        self.assertEqual(sum(site["target_function"] == leaf["function"] for site in config["patch_sites"]), 1)
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        self.assertEqual(sum(region["name"] == "apollo_cmsis_kernel_get_state_source_leaf" for region in regions), 1)


if __name__ == "__main__": unittest.main()
