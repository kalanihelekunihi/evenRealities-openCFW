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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_thread_new.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_thread_new_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisThreadNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        lib = Path(cls.tmp.name) / ("new.dylib" if sys.platform == "darwin" else "new.so")
        cmd = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
               "-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": cmd.append("-fPIC")
        subprocess.run([*cmd, "-o", str(lib)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.open_cfw_thread_new_host_set_irq.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_new_host_set_dynamic_result.argtypes = [ctypes.c_int32]
        cls.lib.open_cfw_thread_new_host_call.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32,
            ctypes.c_size_t, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_uint32,
            ctypes.c_int32,
        ]
        cls.lib.open_cfw_thread_new_host_call.restype = ctypes.c_size_t
        cls.lib.open_cfw_thread_new_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_new_host_get.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def reset(self): self.lib.open_cfw_thread_new_host_reset()
    def get(self, index): return self.lib.open_cfw_thread_new_host_get(index)
    def call(self, *, null_function=0, null_attributes=0, name=None,
             bits=0, cb=0, cb_size=0, stack=0, stack_size=0, priority=0):
        return self.lib.open_cfw_thread_new_host_call(
            null_function, null_attributes, name, bits, cb, cb_size,
            stack, stack_size, priority,
        )

    def test_source_and_stock_body_are_pinned(self):
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (3530, "c6628d4f95bf6cc351a3d485f1fcc7f7d9ad46dec39e9f4fbb94fe8c71b97b39"),
        )
        self.assertEqual(
            hashlib.sha256(OFFICIAL.read_bytes()[32:][0x4490E2-0x438000:0x4491AA-0x438000]).hexdigest(),
            "9c6a8120325e47a0a098156f0a03d4716d0c8cb99df99144bb33f869d7b7aac6",
        )

    def test_irq_and_null_function_are_rejected_without_creation(self):
        self.reset(); self.lib.open_cfw_thread_new_host_set_irq(1)
        self.assertEqual(self.call(null_attributes=1), 0)
        self.reset(); self.assertEqual(self.call(null_function=1, null_attributes=1), 0)
        self.assertEqual((self.get(0), self.get(1)), (0, 0))

    def test_default_dynamic_creation(self):
        self.reset(); self.assertEqual(self.call(null_attributes=1), 0x12345678)
        self.assertEqual((self.get(0), self.get(1), self.get(4), self.get(5), self.get(6)),
                         (1, 0, 1024, 24, 0xAABBCCDD))

    def test_dynamic_attributes_and_stack_depth_cast(self):
        self.reset(); name = b"worker"
        self.assertEqual(self.call(name=name, stack_size=0x40004, priority=37), 0x12345678)
        self.assertEqual((self.get(0), self.get(4), self.get(5)), (1, 1, 37))
        self.assertNotEqual(self.get(3), 0)
        self.reset(); self.lib.open_cfw_thread_new_host_set_dynamic_result(0)
        self.assertEqual(self.call(stack_size=400), 0)

    def test_static_creation_uses_g2_control_block_threshold(self):
        self.reset()
        self.assertEqual(self.call(cb=0x20001000, cb_size=112, stack=0x20002000,
                                   stack_size=1024, priority=1), 0x87654321)
        self.assertEqual((self.get(0), self.get(1), self.get(4), self.get(5),
                          self.get(7), self.get(8)),
                         (0, 1, 256, 1, 0x20002000, 0x20001000))

    def test_invalid_attributes_do_not_fall_back_to_dynamic(self):
        for kwargs in ({"priority": -1}, {"priority": 57}, {"bits": 1},
                       {"cb": 1}, {"cb_size": 1}, {"stack": 1}):
            self.reset(); self.assertEqual(self.call(**kwargs), 0)
            self.assertEqual((self.get(0), self.get(1)), (0, 0))

    def test_production_admission_is_pinned(self):
        config = json.loads(OVERLAY.read_text())
        leaves = {item["function"]: item for item in config["relocated_leaves"]}
        leaf = leaves["open_cfw_cmsis_thread_new"]
        self.assertEqual(
            (leaf["expected"]["size"], leaf["expected"]["offset"], leaf["expected"]["sha256"]),
            (168, 196940, "1d52aae3021ef42d596f1f900c9f4504e77670f7d0b05611573da212973be6ac"),
        )
        linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual((linux["size"], linux["offset"], linux["sha256"]),
                         (166, 198724, "28c827ccf124ef6ceb052ae015696b1f278d251d81ee55e1b569345a7437198e"))
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            [(item["offset"], item["symbol"], item.get("target_address")) for item in leaf["relocations"]],
            [(16, "open_cfw_cmsis_irq_context", None),
             (104, "open_cfw_retained_freertos_task_create_static", 0x454820),
             (134, "open_cfw_retained_freertos_task_create", 0x4548BA)],
        )
        self.assertEqual(
            (config["expected"]["overlay_size"], config["expected"]["overlay_sha256"],
             config["expected"]["component_size"], config["expected"]["component_sha256"]),
            (429058, "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd",
             3952454, "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb"),
        )
        linux_config = config["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual(
            (linux_config["overlay_size"], linux_config["overlay_sha256"],
             linux_config["component_size"], linux_config["component_sha256"]),
            (212664, "1074b19c5f24f6bb454860f53a38fdf321ae29da6762617c36b1e47925dd0b18",
             3736060, "fc7e2a8363e7d8a78c28c64cbaf7dcc3a03a1089c716d2d83f8d1a9bb5c10b97"),
        )
        manifest = json.loads(MANIFEST.read_text())
        regions = {item["name"]: item for item in manifest["component_overrides"]["apollo_main"]["regions"]}
        self.assertEqual(
            (regions["apollo_cmsis_thread_new_alignment"]["file_offset"],
             regions["apollo_cmsis_thread_new_alignment"]["size"],
             regions["apollo_cmsis_thread_new_source_leaf"]["file_offset"],
             regions["apollo_cmsis_thread_new_source_leaf"]["size"]),
            (3720334, 2, 3720336, 168),
        )
        replacement = regions["cmsis_thread_new_source_replacement"]
        self.assertEqual(
            (replacement["file_offset"], replacement["size"],
             replacement["target_address"], replacement["address_status"]),
            (69890, 200, 0x4490E2, "generated_source_entry_replacement"),
        )
        main = manifest["component_overrides"]["apollo_main"]["provider"]
        self.assertEqual((main["size"], main["sha256"]),
                         (3952454, "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb"))
        self.assertEqual((main["profiles"]["linux-clang"]["size"],
                          main["profiles"]["linux-clang"]["sha256"]),
                         (3736060, "fc7e2a8363e7d8a78c28c64cbaf7dcc3a03a1089c716d2d83f8d1a9bb5c10b97"))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
                         (4745526, "4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934"))
        self.assertEqual((manifest["package"]["profiles"]["linux-clang"]["expected_size"],
                          manifest["package"]["profiles"]["linux-clang"]["expected_sha256"]),
                         (4529116, "f0526433c366a85ab79e27df6d28ffc70d6a2ed93e608652885b49b404e380ef"))


if __name__ == "__main__": unittest.main()
