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
TASK = ROOT / "components/shared/freertos/runtime_freertos_task_delay.c"
CMSIS = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_delay.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_delay_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeCmsisDelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        suffix = "dylib" if sys.platform == "darwin" else "so"
        lib = Path(cls.temporary.name) / f"delay.{suffix}"
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(lib)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.open_cfw_delay_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_delay_host_call.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_delay_host_call.restype = ctypes.c_int32
        cls.lib.open_cfw_delay_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_delay_host_get.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()
    def reset(self, irq=0, resume=0) -> None: self.lib.open_cfw_delay_host_reset(irq, resume)
    def get(self, selector: int) -> int: return self.lib.open_cfw_delay_host_get(selector)

    def test_source_fixture_and_stock_are_pinned(self) -> None:
        pins = [(TASK,1081,"f93d57e3fdc0f08ef60abd6a862e6e655dd5097b236582c3f6e4380f2550fffe"),(CMSIS,888,"13bd486c8d767cca2bf3387280e78025d5e2cb45c62d2ee826f7f229a7055c20"),(FIXTURE,1800,"7fb2883d9929bfea9632d0a403cdc4868bd85bd3c7a8349f5de8f669e9f729cf")]
        for path,size,digest in pins: self.assertEqual((path.stat().st_size,hashlib.sha256(path.read_bytes()).hexdigest()),(size,digest))
        image=OFFICIAL.read_bytes()[32:]
        for start,end,digest in [(0x449376,0x449398,"86584b9833b32e166acbeeea1a4c08671b20ac1fa10b15746d824c4b03311718"),(0x454B4C,0x454B88,"86f7d3b317ec02d559374d2bdb113698889a1291d8d4369f255d2c6874015738")]:
            self.assertEqual(hashlib.sha256(image[start-0x438000:end-0x438000]).hexdigest(),digest)

    def test_isr_and_zero_delay_do_not_enter_task_delay(self) -> None:
        self.reset(irq=1); self.assertEqual(self.lib.open_cfw_delay_host_call(9),-6)
        self.assertEqual(tuple(self.get(i) for i in range(4)),(0,0,0,0))
        self.reset(); self.assertEqual(self.lib.open_cfw_delay_host_call(0),0)
        self.assertEqual(tuple(self.get(i) for i in range(4)),(0,0,0,0))

    def test_task_delay_blocks_and_yields_only_when_resume_did_not(self) -> None:
        self.reset(resume=0); self.assertEqual(self.lib.open_cfw_delay_host_call(17),0)
        self.assertEqual(tuple(self.get(i) for i in range(5)),(1,1,1,1,17))
        self.reset(resume=1); self.assertEqual(self.lib.open_cfw_delay_host_call(23),0)
        self.assertEqual(tuple(self.get(i) for i in range(5)),(1,1,1,0,23))

    def test_production_admits_delay_pair_in_both_profiles(self) -> None:
        config=json.loads(CONFIG.read_text())
        task=next(x for x in config["relocated_leaves"] if x["function"]=="open_cfw_freertos_task_delay")
        cmsis=next(x for x in config["relocated_leaves"] if x["function"]=="open_cfw_cmsis_delay")
        self.assertEqual((task["expected"]["size"],task["expected"]["offset"],cmsis["expected"]["size"],cmsis["expected"]["offset"]),(70,135292,30,135364))
        self.assertEqual((task["toolchain_profiles"]["linux-clang"]["expected"]["offset"],cmsis["toolchain_profiles"]["linux-clang"]["expected"]["offset"]),(137168,137240))
        self.assertTrue(task["strict_relocation_contract"] and cmsis["strict_relocation_contract"])
        manifest=json.loads(MANIFEST.read_text());main=manifest["component_overrides"]["apollo_main"]
        region=next(x for x in main["regions"] if x["name"]=="apollo_cmsis_delay_source_leaf")
        self.assertEqual((region["file_offset"],region["size"],region["target_address"]),(3658760,30,8082408))
        self.assertEqual((manifest["package"]["expected_size"],manifest["package"]["expected_sha256"]),(4466426,"cc1642fdf85d2af71ba4c3c40335fe4e8b431eb5f578d501b1b260f43fcdd3f4"))


if __name__ == "__main__": unittest.main()
