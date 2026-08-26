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
SOURCE = ROOT / "components/apollo_main/core_overlay/lvgl_font_manager.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_font_manager_host.c"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import apollo_overlay  # noqa: E402


SELECTORS = {
    "CREATE_CHAIN": "open_cfw_font_manager_create_chain",
    "GET_FONT": "open_cfw_font_manager_get_font",
    "CREATE_SINGLE": "open_cfw_font_manager_create_single",
    "ADD": "open_cfw_font_manager_add",
    "CLEANUP_SINGLE": "open_cfw_font_manager_cleanup_single",
    "CONFIGURE_XIP": "open_cfw_font_manager_configure_xip",
    "INIT": "open_cfw_font_manager_init",
    "XIP_NAME": "open_cfw_font_manager_xip_name",
}

FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]


class G2LvglFontManagerCandidateTests(unittest.TestCase):
    def test_source_and_fixture_are_pinned(self) -> None:
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (16940, "f11f98dd4c2eda815512e3e9b2e23ab7401b7cfdc439f272e69d59b684bbb080"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (10311, "629dd394cf28b0035f79f6185ae20cefbaf6623b41ecceeed3dd799610eced9a"),
        )

    def test_host_behavior_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / (
                "lvgl_font_manager.dylib" if sys.platform == "darwin"
                else "lvgl_font_manager.so"
            )
            command = ["/usr/bin/clang", "-O2", "-Wall", "-Wextra", "-Werror"]
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", str(FIXTURE), "-o", str(library)])
            else:
                command.extend(["-shared", "-fPIC", str(FIXTURE), "-o", str(library)])
            subprocess.run(command, check=True, capture_output=True, text=True)
            loaded = ctypes.CDLL(str(library))

            chain = loaded.open_cfw_test_font_chain_scenario
            chain.argtypes = [ctypes.c_uint32]
            chain.restype = ctypes.c_uint32
            self.assertEqual(chain(0), 0x3F)
            self.assertEqual(chain(1), 0)
            self.assertEqual(chain(2), 0)

            for name, expected in (
                ("open_cfw_test_font_invalid_scenario", 0x0F),
                ("open_cfw_test_font_cleanup_scenario", 1),
                ("open_cfw_test_font_init_scenario", 0x7F),
            ):
                function = getattr(loaded, name)
                function.argtypes = []
                function.restype = ctypes.c_uint32
                self.assertEqual(function(), expected)
            xip = loaded.open_cfw_test_font_xip_scenario
            xip.argtypes = [ctypes.c_uint32]
            xip.restype = ctypes.c_uint32
            self.assertEqual(xip(0), 0x7FF)
            self.assertEqual(xip(1), 0x7FF)

    def test_all_eight_strict_cortex_m55_selectors_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, function in SELECTORS.items():
                with self.subTest(selector=selector):
                    object_path = Path(directory) / f"{selector}.o"
                    subprocess.run(
                        [
                            "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                            *FLAGS,
                            f"-DOPEN_CFW_FONT_MANAGER_{selector}_ONLY=1",
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
        path = TOOLS / "analyze_g2_lvgl_font_manager.py"
        spec = importlib.util.spec_from_file_location("font_manager_audit", path)
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
            (8, 904, 10, 19, 8, 2590, 382),
        )


if __name__ == "__main__":
    unittest.main()
