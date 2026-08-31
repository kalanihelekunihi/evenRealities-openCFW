from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/box_uart_mgr.c"
FIXTURE = ROOT / "tests/fixtures/box_uart_mgr_host.c"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


SELECTORS = {
    "UNPACK": "open_cfw_box_uart_unpack",
    "SEND": "open_cfw_box_uart_send",
    "RECEIVE": "open_cfw_box_uart_receive",
    "INIT": "open_cfw_box_uart_init",
    "HANDLE": "open_cfw_box_uart_handle",
}

FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]


class G2BoxUartManagerCandidateTests(unittest.TestCase):
    def test_source_and_fixture_are_pinned(self) -> None:
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (7426, "d7d419940733206f76e8d8661d261f3d0eb7435f2975315274c072b99e1f1ae2"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (8157, "7409fc4316bb0bcd1fcb8de13f9cb2bf2459c677ba59c8cdaece73bb046dad8e"),
        )

    def test_host_behavior_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / (
                "box_uart_mgr.dylib" if sys.platform == "darwin"
                else "box_uart_mgr.so"
            )
            command = ["/usr/bin/clang", "-O2", "-Wall", "-Wextra", "-Werror"]
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", str(FIXTURE), "-o", str(library)])
            else:
                command.extend(["-shared", "-fPIC", str(FIXTURE), "-o", str(library)])
            subprocess.run(command, check=True, capture_output=True, text=True)
            loaded = ctypes.CDLL(str(library))
            unpack = loaded.open_cfw_test_box_unpack
            unpack.argtypes = []
            unpack.restype = ctypes.c_uint32
            self.assertEqual(unpack(), 0x3F)
            receive = loaded.open_cfw_test_box_receive
            receive.argtypes = []
            receive.restype = ctypes.c_uint32
            self.assertEqual(receive(), 0x1F)
            init = loaded.open_cfw_test_box_init
            init.argtypes = []
            init.restype = ctypes.c_uint32
            self.assertEqual(init(), 1)
            handle = loaded.open_cfw_test_box_handle
            handle.argtypes = [ctypes.c_uint32]
            handle.restype = ctypes.c_uint32
            for scenario in range(6):
                with self.subTest(scenario=scenario):
                    self.assertEqual(handle(scenario), 1)

    def test_all_five_strict_cortex_m55_selectors_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, function in SELECTORS.items():
                with self.subTest(selector=selector):
                    object_path = Path(directory) / f"{selector}.o"
                    subprocess.run(
                        [
                            "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                            *FLAGS,
                            f"-DOPEN_CFW_BOX_UART_{selector}_ONLY=1",
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

    def test_production_analyzer_reports_exact_routing(self) -> None:
        path = ROOT / "tools/analyze_g2_box_uart_mgr.py"
        spec = importlib.util.spec_from_file_location("box_uart_audit", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        production = module.analyze()["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(
            (
                production["source_functions"],
                production["compiled_text_bytes"],
                production["alignment_bytes"],
                production["strict_relocations"],
                production["guarded_redirects"],
                production["routed_stock_bytes"],
                production["retained_compatibility_bytes"],
            ),
            (5, 514, 4, 21, 5, 1296, 114),
        )


if __name__ == "__main__":
    unittest.main()
