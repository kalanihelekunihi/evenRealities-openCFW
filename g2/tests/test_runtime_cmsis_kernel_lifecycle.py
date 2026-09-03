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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_kernel_lifecycle.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_kernel_lifecycle_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisKernelLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        temporary = Path(cls.tmp.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("lifecycle.dylib" if sys.platform == "darwin" else "lifecycle.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cmsis_kernel_initialize.restype = ctypes.c_int32
        cls.lib.open_cfw_cmsis_kernel_start.restype = ctypes.c_int32
        cls.lib.open_cfw_cmsis_kernel_lifecycle_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32]
        cls.lib.open_cfw_cmsis_kernel_lifecycle_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_cmsis_kernel_lifecycle_host_get.restype = ctypes.c_int32

        flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.closures = {}
        for name, selector in (
            ("open_cfw_cmsis_kernel_initialize", "OPEN_CFW_BUILD_CMSIS_KERNEL_INITIALIZE"),
            ("open_cfw_cmsis_kernel_start", "OPEN_CFW_BUILD_CMSIS_KERNEL_START"),
        ):
            target = temporary / f"{name}.o"
            subprocess.run([clang, *flags, f"-D{selector}", "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True)
            data, sections = apollo_overlay.parse_elf32(target)
            section = apollo_overlay.section_named(sections, f".text.{name}")
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            relocations = []
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
                    relocations.append((offset, information & 0xFF, names[information >> 8]))
            cls.closures[name] = (body, relocations)

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def reset(self, irq=0, scheduler=1, kernel=0):
        self.lib.open_cfw_cmsis_kernel_lifecycle_host_reset(irq, scheduler, kernel)

    def get(self, index): return self.lib.open_cfw_cmsis_kernel_lifecycle_host_get(index)

    def test_stock_and_retained_scheduler_start_are_pinned(self):
        image = OFFICIAL.read_bytes()[32:]
        base = 0x438000
        spans = {
            (0x44903C, 0x44906C): "70065824750aff11e5e4b17a7996f4aa72d42be6a4739515a6b7a22d5679b775",
            (0x449094, 0x4490CC): "01d0e472c73fbab1af81f34ee5916c26978d5358e7a24075b790028aeabe8911",
            (0x454CEC, 0x454D7C): "2fabf4882dc6db88c73cd573ba3f454e7f6f0cafb1329670ad52e39ef1cbe01d",
        }
        for (start, end), expected in spans.items():
            self.assertEqual(hashlib.sha256(image[start-base:end-base]).hexdigest(), expected)
        self.assertEqual(image[0x44900C-base:0x44900E-base], b"\x70\x47")

    def test_source_fixture_and_target_closures_are_pinned(self):
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (2385, "ec75881048b6fd4536baaed046cc1c5aeb00909b3cac58dbf7bdba1d91140f24"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (1265, "80c7f84b0a38f5825049a5e6647c40d0baafcfbf2d595458205df0af38c8874d"),
        )
        initialize, start = (
            self.closures["open_cfw_cmsis_kernel_initialize"],
            self.closures["open_cfw_cmsis_kernel_start"],
        )
        self.assertEqual((len(initialize[0]), hashlib.sha256(initialize[0]).hexdigest()),
                         (50, "c5cc9f2380f5bbaa4d4ac610d4e104765fa52abb227ed06ef24069d81b2257a8"))
        self.assertEqual((len(start[0]), hashlib.sha256(start[0]).hexdigest()),
                         (56, "f2ee18ec358566d7e41cb39c682ac2db5c2131ff9c8ac4fafb0bdb75fa0b8c09"))

    def test_initialize_gates_and_single_transition(self):
        self.reset(); self.assertEqual(self.lib.open_cfw_cmsis_kernel_initialize(), 0)
        self.assertEqual(self.get(0), 1)
        self.assertEqual(self.lib.open_cfw_cmsis_kernel_initialize(), -1)
        for irq, scheduler, kernel, expected in ((1, 1, 0, -6), (0, 2, 0, -1), (0, 1, 1, -1), (0, 1, 2, -1)):
            with self.subTest(irq=irq, scheduler=scheduler, kernel=kernel):
                self.reset(irq, scheduler, kernel)
                self.assertEqual(self.lib.open_cfw_cmsis_kernel_initialize(), expected)
                self.assertEqual(self.get(0), kernel)

    def test_start_gates_and_writes_running_before_provider(self):
        self.reset(kernel=1)
        self.assertEqual(self.lib.open_cfw_cmsis_kernel_start(), 0)
        self.assertEqual((self.get(0), self.get(1), self.get(2)), (2, 1, 2))
        for irq, scheduler, kernel, expected in ((1, 1, 1, -6), (0, 2, 1, -1), (0, 1, 0, -1), (0, 1, 2, -1)):
            with self.subTest(irq=irq, scheduler=scheduler, kernel=kernel):
                self.reset(irq, scheduler, kernel)
                self.assertEqual(self.lib.open_cfw_cmsis_kernel_start(), expected)
                self.assertEqual((self.get(0), self.get(1)), (kernel, 0))

    def test_target_closures_have_only_reviewed_calls(self):
        initialize = self.closures["open_cfw_cmsis_kernel_initialize"]
        start = self.closures["open_cfw_cmsis_kernel_start"]
        self.assertEqual([item[2] for item in initialize[1]], [
            "open_cfw_cmsis_irq_context", "open_cfw_freertos_task_get_scheduler_state"
        ])
        self.assertEqual([item[2] for item in start[1]], [
            "open_cfw_cmsis_irq_context", "open_cfw_freertos_task_get_scheduler_state",
            "open_cfw_retained_freertos_task_start_scheduler"
        ])
        self.assertGreater(len(initialize[0]), 0)
        self.assertGreater(len(start[0]), 0)

    def test_production_admission_is_atomic_and_dual_profile_pinned(self):
        config = json.loads(OVERLAY.read_text())
        leaves = {item["function"]: item for item in config["relocated_leaves"]}
        initialize = leaves["open_cfw_cmsis_kernel_initialize"]
        start = leaves["open_cfw_cmsis_kernel_start"]
        self.assertEqual(
            (initialize["expected"]["size"], initialize["expected"]["offset"], initialize["expected"]["sha256"]),
            (50, 137260, "2da493da67483c1f6fdb77b7958fcb79d531948b24d77ab8f7d7a31967a4c1ab"),
        )
        self.assertEqual(
            (start["expected"]["size"], start["expected"]["offset"], start["expected"]["sha256"]),
            (56, 137312, "e6b14852638048830f9777c1ada618148fc0c7a0e9ff69859a48cebb67eadf60"),
        )
        self.assertEqual(
            (initialize["toolchain_profiles"]["linux-clang"]["expected"]["offset"],
             initialize["toolchain_profiles"]["linux-clang"]["expected"]["sha256"],
             start["toolchain_profiles"]["linux-clang"]["expected"]["offset"],
             start["toolchain_profiles"]["linux-clang"]["expected"]["sha256"]),
            (139140, "7c915db88585f25e0f03db84a3ed7aa950c7b9de1862d71fadf50cb7c8651e70",
             139192, "7f61a7b8b6cb04c286cd3ddf7baef6c3bfa9d64a886053b3966353b29aac0f15"),
        )
        self.assertEqual(start["relocations"][-1]["target_address"], 0x454CEC)
        self.assertEqual(
            {site["target_function"] for site in config["patch_sites"] if site["target_function"] in {initialize["function"], start["function"]}},
            {initialize["function"], start["function"]},
        )

        manifest = json.loads(MANIFEST.read_text())
        regions = {item["name"]: item for item in manifest["component_overrides"]["apollo_main"]["regions"]}
        expected = {
            "cmsis_kernel_initialize_source_replacement": (69724, 48, 0x44903C),
            "cmsis_kernel_get_state_source_replacement": (69772, 40, 0x44906C),
            "cmsis_kernel_start_source_replacement": (69812, 56, 0x449094),
            "apollo_cmsis_kernel_initialize_source_leaf": (3660656, 50, 0x7B5B50),
            "apollo_cmsis_kernel_start_alignment": (3660706, 2, 0x7B5B82),
            "apollo_cmsis_kernel_start_source_leaf": (3660708, 56, 0x7B5B84),
        }
        self.assertEqual(
            {name: (regions[name]["file_offset"], regions[name]["size"], regions[name]["target_address"]) for name in expected},
            expected,
        )
        self.assertEqual(
            (config["expected"]["overlay_size"], config["expected"]["overlay_sha256"],
             config["expected"]["component_size"], config["expected"]["component_sha256"]),
            (362272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae",
             3956672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef"),
        )


if __name__ == "__main__": unittest.main()
