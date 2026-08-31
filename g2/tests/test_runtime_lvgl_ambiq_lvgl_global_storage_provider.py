#!/usr/bin/env python3
"""Target ABI, placement, and fail-closed gates for LVGL global storage."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_g2_lvgl_ambiq_backend.py"
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_global_storage_provider.c"
ABI_FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_global_storage_provider_abi.c"
LINKER_SCRIPT = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_global_storage_provider.ld"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("lvgl_global_storage_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LVGLGlobalStorageProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.nm_tool = cls.builder._llvm_tool("llvm-nm")
        cls.objdump = cls.builder._llvm_tool("llvm-objdump")
        cls.lld = cls.builder._llvm_tool("ld.lld")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-global-storage-")
        cls.temp = Path(cls.temporary.name)
        cls.lvgl = cls.builder._stage_tree(cls.temp)
        cls.stubs = cls.temp / "stubs"
        cls.builder._write_stubs(cls.stubs)
        cls.flags = [
            *cls.builder._compiler_flags(cls.clang, cls.temp, cls.lvgl, cls.stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        cls.source_obj = cls.temp / "source.o"
        cls.abi_obj = cls.temp / "abi.o"
        cls.provider_obj = cls.temp / "provider.o"
        cls.placement_elf = cls.temp / "placement.elf"
        subprocess.run(
            [*cls.flags, "-c", str(SOURCE), "-o", str(cls.source_obj)],
            cwd=cls.temp, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [*cls.flags, "-c", str(ABI_FIXTURE), "-o", str(cls.abi_obj)],
            cwd=cls.temp, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [cls.lld, "-r", "--gc-sections", "-u", "lv_global", "-o",
             str(cls.provider_obj), str(cls.source_obj)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [cls.lld, "-T", str(LINKER_SCRIPT), "--entry=0", "-o",
             str(cls.placement_elf), str(cls.provider_obj)],
            check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_nm(self, path: Path, *options: str) -> str:
        return subprocess.run(
            [self.nm_tool, *options, str(path)], check=True,
            capture_output=True, text=True,
        ).stdout

    def test_target_object_abi_relocations_and_placement_are_exact(self) -> None:
        source_symbols = self.run_nm(self.source_obj, "--format=posix", "--print-size")
        self.assertEqual(source_symbols.strip(), "lv_global B 0 1ec")
        abi_relocations = subprocess.run(
            [self.objdump, "-r", str(self.abi_obj)], check=True,
            capture_output=True, text=True,
        ).stdout
        self.assertEqual(abi_relocations.count("R_ARM_THM_MOVW_ABS_NC    lv_global"), 1)
        self.assertEqual(abi_relocations.count("R_ARM_THM_MOVT_ABS       lv_global"), 1)
        self.assertEqual(
            self.run_nm(self.provider_obj, "--undefined-only").strip(), ""
        )
        self.assertEqual(
            self.run_nm(self.placement_elf, "--format=posix", "--print-size").strip(),
            "lv_global B 2006f548 1ec",
        )

    def test_manifest_pins_source_artifacts_and_fail_closed_qualification(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_global_storage_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_global_storage_provider.o",
            "size": 716,
            "sha256": "11ce9df99cecff701ba5ba4d8b8f3e17f6db562ac56f0c2b3a40378187c6dca3",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-global-storage-provider.o",
            "size": 796,
            "sha256": "a11c7c766758ae759bd4f0fc198246d3eab4425cb1a9b57b5d12905a6687966a",
        })
        self.assertEqual(provider["placement_proof_artifact"], {
            "path": "lvgl-ambiq-lvgl-global-storage-placement.elf",
            "size": 63_396,
            "sha256": "7165c79720cca1c7f333ac4eeb9d1e68ce223888ebb18722b15e7be200d0ef40",
        })
        self.assertEqual(provider["authenticated_stock_address"], "0x2006F548")
        self.assertFalse(provider["callable_hostile_input_surface"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])
        self.assertEqual(self.source_obj.stat().st_size, 716)
        self.assertEqual(sha256(self.source_obj), provider["target_source_artifact"]["sha256"])
        self.assertNotIn(
            "lv_global", {row["symbol"] for row in report["missing_provider_ledger"]}
        )

    def test_incompatible_global_layout_is_rejected_at_compile_time(self) -> None:
        incompatible_flags = [
            flag for flag in self.flags if flag != "-DLV_DRAW_SW_COMPLEX=0"
        ]
        incompatible = subprocess.run(
            [*incompatible_flags, "-DLV_DRAW_SW_COMPLEX=1", "-c", str(SOURCE),
             "-o", str(self.temp / "incompatible.o")],
            cwd=self.temp, capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(incompatible.returncode, 0)
        self.assertIn("G2 lv_global size changed", incompatible.stdout + incompatible.stderr)


if __name__ == "__main__":
    unittest.main()
