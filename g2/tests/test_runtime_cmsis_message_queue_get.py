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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_message_queue_get.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_message_queue_get_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisMessageQueueGetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        suffix = "dylib" if sys.platform == "darwin" else "so"
        library = Path(cls.temporary.name) / f"mq_get.{suffix}"
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_mq_get_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        cls.lib.open_cfw_mq_get_host_call.argtypes = [ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32]
        cls.lib.open_cfw_mq_get_host_call.restype = ctypes.c_int32
        cls.lib.open_cfw_mq_get_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_mq_get_host_get.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()
    def reset(self, irq=0, isr=1, task=1, wake=0) -> None: self.lib.open_cfw_mq_get_host_reset(irq, isr, task, wake)
    def call(self, queue=0x1111, message=0x2222, priority=0, timeout=0) -> int: return self.lib.open_cfw_mq_get_host_call(queue, message, priority, timeout)
    def get(self, selector: int) -> int: return self.lib.open_cfw_mq_get_host_get(selector)

    def test_source_fixture_and_stock_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (2579, "16b4218a09a53a2d2de38c5f9c400ba598a5f79b4c95d2f2377e98a4ad3de8da"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (1861, "c110dcbb4e3b069d07b741be3c3af09a926344f5c29ae70beff3bf0ee0f5296b"))
        image = OFFICIAL.read_bytes()[32:]
        body = image[0x449B3C - 0x438000:0x449BBC - 0x438000]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (128, "ba577117e8cc2833921c4d0ab5f8dcf8122fab6090ccb32571ff62231dfd52ba"))

    def test_isr_validation_status_and_pendsv(self) -> None:
        for queue, message, timeout in ((0, 1, 0), (1, 0, 0), (1, 1, 1)):
            self.reset(irq=1); self.assertEqual(self.call(queue, message, timeout=timeout), -4)
        self.reset(irq=1, isr=0, wake=1); self.assertEqual(self.call(), -3); self.assertEqual(self.get(2), 0)
        self.reset(irq=1, isr=1, wake=1); self.assertEqual(self.call(priority=0x3333), 0); self.assertEqual(self.get(2), 1)

    def test_task_status_and_ignored_priority(self) -> None:
        self.reset(); self.assertEqual(self.call(queue=0), -4); self.assertEqual(self.call(message=0), -4)
        self.reset(task=0); self.assertEqual(self.call(timeout=0), -3)
        self.reset(task=0); self.assertEqual(self.call(timeout=9), -2)
        self.reset(task=1); self.assertEqual(self.call(priority=0x3333, timeout=9), 0)
        self.assertEqual((self.get(1), self.get(5)), (1, 9))

    def test_production_admits_final_message_queue_wrapper(self) -> None:
        config = json.loads(CONFIG.read_text())
        leaf = next(x for x in config["relocated_leaves"] if x["function"] == "open_cfw_cmsis_message_queue_get")
        self.assertEqual((leaf["expected"]["size"], leaf["expected"]["offset"], leaf["expected"]["sha256"]), (132, 135160, "836d2d1b5ec73c9db04e9ca0742a9ad607203e71d7205ad449aebbc368c002ec"))
        linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual((linux["size"], linux["offset"], linux["sha256"]), (132, 137036, "8053225658c68aa3b5f90a6bc35a455300611a9f775b112b726149796af7fbf7"))
        patch = next(x for x in config["patch_sites"] if x["target_function"] == "open_cfw_cmsis_message_queue_get")
        self.assertEqual((patch["runtime_address"], patch["expected_size"]), (0x449B3C, 128))
        manifest = json.loads(MANIFEST.read_text())
        main = manifest["component_overrides"]["apollo_main"]
        region = next(x for x in main["regions"] if x["name"] == "apollo_cmsis_message_queue_get_source_leaf")
        self.assertEqual((region["file_offset"], region["size"], region["target_address"]), (3658556, 132, 8082204))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]), (4750780, "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771"))


if __name__ == "__main__": unittest.main()
