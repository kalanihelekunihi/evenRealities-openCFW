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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_queue_receive.c"
HEADER = ROOT / "components/shared/freertos/runtime_freertos_queue_receive.h"
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_queue_receive_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class RuntimeFreeRTOSQueueReceiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        suffix = "dylib" if sys.platform == "darwin" else "so"
        library = Path(cls.temporary.name) / f"queue_receive.{suffix}"
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_queue_receive_host_delayed.argtypes = [ctypes.c_uint32, ctypes.c_int]
        cls.lib.open_cfw_queue_receive_host_delayed.restype = ctypes.c_size_t
        cls.lib.open_cfw_queue_receive_host_immediate.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_queue_receive_host_immediate.restype = ctypes.c_int
        cls.lib.open_cfw_queue_receive_host_timeout.restype = ctypes.c_int
        cls.lib.open_cfw_queue_receive_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_queue_receive_host_get.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()

    def reset(self) -> None: self.lib.open_cfw_queue_receive_host_reset()
    def get(self, selector: int) -> int: return self.lib.open_cfw_queue_receive_host_get(selector)

    def test_source_fixture_and_stock_bodies_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (8567, "58e28ce3ae04f2034b0c74bd5125952e4eec211c32a29a9b4217014996ae43b1"))
        self.assertEqual((HEADER.stat().st_size, hashlib.sha256(HEADER.read_bytes()).hexdigest()), (4819, "a204ec66a3704142bffbb7ae1c3a69dd5812907c124ff80817c0d19e22eea89d"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (6696, "018f460d65509e9ff060cbcdd81931b4f9dc67e65ec013874a4b399884769430"))
        image = OFFICIAL.read_bytes()[32:]
        for start, end, digest in (
            (0x441B0A, 0x441C44, "f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560"),
            (0x441F88, 0x441FF6, "25eb09eeb3f819a998a8d56ebac062fb54fcc5140af8445c5d39c514187b9f7d"),
            (0x455282, 0x4552AE, "2821a3c55358d806ed227c81a27746f8d9c35b648182fc9abb647de72ed9025d"),
            (0x455FA8, 0x45601E, "918fddb6333958607bec10181d39ffee564ca44f4db6cb43ee362cc62ba4f764"),
        ):
            body = image[start - 0x438000:end - 0x438000]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_delayed_list_routes_finite_overflow_and_indefinite(self) -> None:
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_delayed(5, 1), 1)
        self.assertEqual((self.get(1), self.get(3)), (1, 105))
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_delayed(0xFFFFFFF0, 1), 2)
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_delayed(0xFFFFFFFF, 1), 3)

    def test_receive_immediate_empty_and_timeout_paths(self) -> None:
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_immediate(1, 0), 3)
        self.assertEqual((self.get(7), self.get(8)), (1, 1))
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_immediate(0, 0), 0)
        self.reset(); self.assertEqual(self.lib.open_cfw_queue_receive_host_timeout(), 0)
        self.assertEqual((self.get(4), self.get(5), self.get(6)), (1, 1, 1))

    def test_production_admits_complete_task_receive_chain(self) -> None:
        config = json.loads(CONFIG.read_text())
        expected = {
            "open_cfw_freertos_task_add_current_to_delayed_list": (126, 134428, 136304),
            "open_cfw_freertos_task_place_on_event_list": (54, 134556, 136432),
            "open_cfw_freertos_queue_unlock": (116, 134612, 136488),
            "open_cfw_freertos_queue_receive": (432, 134728, 136604),
        }
        for name, (size, apple_offset, linux_offset) in expected.items():
            leaf = next(x for x in config["relocated_leaves"] if x["function"] == name)
            self.assertEqual((leaf["expected"]["size"], leaf["expected"]["offset"]), (size, apple_offset))
            self.assertEqual(leaf["toolchain_profiles"]["linux-clang"]["expected"]["offset"], linux_offset)
            self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual((config["expected"]["overlay_size"], config["expected"]["component_size"]), (147021, 3670417))
        manifest = json.loads(MANIFEST.read_text())
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        receive = next(x for x in regions if x["name"] == "apollo_freertos_queue_receive_source_leaf")
        self.assertEqual((receive["file_offset"], receive["size"], receive["target_address"]), (3658124, 432, 8081772))


if __name__ == "__main__": unittest.main()
