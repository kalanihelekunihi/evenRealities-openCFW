from __future__ import annotations

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/product_rtos.c"
FIXTURE = ROOT / "tests/fixtures/product_rtos_host.c"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import apollo_overlay  # noqa: E402


SELECTORS = {
    "FIND_SLOT": "open_cfw_product_rtos_find_slot",
    "FIND_FREE": "open_cfw_product_rtos_find_free_slot",
    "INIT": "open_cfw_product_rtos_init",
    "ACQUIRE_HANDLE": "open_cfw_product_rtos_acquire_for_handle",
    "RELEASE_HANDLE": "open_cfw_product_rtos_release_for_handle",
    "BLOCKS_SLEEP": "open_cfw_product_rtos_blocks_deep_sleep",
    "ACQUIRE_CURRENT": "open_cfw_product_rtos_acquire_current",
    "RELEASE_CURRENT": "open_cfw_product_rtos_release_current",
    "SLEEP": "am_freertos_sleep",
    "WAKEUP": "am_freertos_wakeup",
    "MALLOC_FAILED": "vApplicationMallocFailedHook",
    "STACK_OVERFLOW": "vApplicationStackOverflowHook",
    "IDLE": "vApplicationIdleHook",
}

FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]


class G2ProductRtosCandidateTests(unittest.TestCase):
    def test_source_and_fixture_are_pinned(self) -> None:
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (10408, "f342cf43b40021b278b76fd6d7bb89778caab5c67ea326b2c0867e69d75d476b"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (7183, "64ce139de0192ee0fe63e604cc13201197e45d1918e081cc376dfde47701b460"),
        )

    def test_host_behavior_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / (
                "product_rtos.dylib" if sys.platform == "darwin"
                else "product_rtos.so"
            )
            command = ["/usr/bin/clang", "-O2", "-Wall", "-Wextra", "-Werror"]
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", str(FIXTURE), "-o", str(library)])
            else:
                command.extend(["-shared", "-fPIC", str(FIXTURE), "-o", str(library)])
            subprocess.run(command, check=True, capture_output=True, text=True)
            loaded = ctypes.CDLL(str(library))
            scenarios = {
                "open_cfw_test_product_rtos_init_scenario": 0x0F,
                "open_cfw_test_product_rtos_vote_scenario": 0x7FF,
                "open_cfw_test_product_rtos_capacity_scenario": 0x0F,
                "open_cfw_test_product_rtos_current_scenario": 0x07,
                "open_cfw_test_product_rtos_power_scenario": 0x3F,
                "open_cfw_test_product_rtos_fatal_scenario": 0x3F,
            }
            for name, expected in scenarios.items():
                with self.subTest(name=name):
                    function = getattr(loaded, name)
                    function.argtypes = []
                    function.restype = ctypes.c_uint32
                    self.assertEqual(function(), expected)

    def test_all_thirteen_strict_cortex_m55_selectors_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, function in SELECTORS.items():
                with self.subTest(selector=selector):
                    object_path = Path(directory) / f"{selector}.o"
                    subprocess.run(
                        [
                            "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                            *FLAGS,
                            "-DOPEN_CFW_PRODUCT_RTOS_LEAF_ONLY=1",
                            f"-DOPEN_CFW_PRODUCT_RTOS_{selector}_ONLY=1",
                            "-c", str(SOURCE), "-o", str(object_path),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    data, sections = apollo_overlay.parse_elf32(object_path)
                    symbols = apollo_overlay.parse_elf32_symbols(data, sections)
                    defined = {
                        item["name"] for item in symbols
                        if item["type"] == apollo_overlay.STT_FUNC
                        and item["section_index"] != 0
                    }
                    self.assertEqual(defined, {function})


if __name__ == "__main__":
    unittest.main()
