from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_freertos_tcb_patch.py"
PATCH = (
    ROOT / "components" / "shared" / "freertos" /
    "g2-tcb-v10.5.1.patch"
)
README = (
    ROOT / "components" / "shared" / "freertos" /
    "README.g2-tcb-patch.md"
)
FIXTURE = ROOT / "tests" / "fixtures" / "freertos_g2_tcb_layout_probe.c"
KERNEL = ROOT / "third_party" / "freertos-kernel"
TASKS = KERNEL / "tasks.c"
HEADER = KERNEL / "include" / "FreeRTOS.h"
IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" /
    "ota_s200_firmware_ota.bin"
)
CANDIDATE = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "candidates" /
    "cmsis_freertos_constructors"
)
PORT = KERNEL / "portable" / "IAR" / "ARM_CM55_NTZ" / "non_secure"

ANALYZER_SHA256 = "1ca114dca1679e2515ad0abdf67b4884c4ea48ccf0cf7d8894d6ca2e55e53779"
PATCH_SHA256 = "cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3"
PATCH_SIZE = 1_730
FIXTURE_SHA256 = "878853cddb6661c276f8344a6c6646523a3694bea115c00031a5fe57f0d945e7"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class G2FreeRTOSTCBPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        self.temp = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_analyzer(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ANALYZER), *arguments],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def stage_pristine_pair(self) -> Path:
        work = self.temp / "kernel"
        (work / "include").mkdir(parents=True)
        shutil.copy2(TASKS, work / "tasks.c")
        shutil.copy2(HEADER, work / "include" / "FreeRTOS.h")
        initialized = subprocess.run(
            ["git", "-C", str(work), "init", "-q"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            initialized.returncode, 0, initialized.stderr or initialized.stdout,
        )
        return work

    def apply_patch(self, work: Path) -> None:
        checked = subprocess.run(
            [
                "git", "-C", str(work), "apply", "--check",
                "--ignore-space-change", str(PATCH),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr or checked.stdout)
        applied = subprocess.run(
            [
                "git", "-C", str(work), "apply", "--ignore-space-change",
                str(PATCH),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr or applied.stdout)

    def test_analyzer_patch_and_fixture_are_pinned(self) -> None:
        self.assertEqual(sha256(ANALYZER), ANALYZER_SHA256)
        self.assertEqual(PATCH.stat().st_size, PATCH_SIZE)
        self.assertEqual(sha256(PATCH), PATCH_SHA256)
        self.assertEqual(sha256(FIXTURE), FIXTURE_SHA256)
        readme = README.read_text(encoding="utf-8")
        self.assertIn("def7d2df2b0506d3d249334974f51e427c17a41c", readme)
        self.assertIn("semantic reconstruction of a vendor delta", readme)

    def test_analyzer_authenticates_base_stock_spans_and_layout(self) -> None:
        result = self.run_analyzer("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "vendor-derived-minimal-patch")
        self.assertEqual(
            report["upstream"]["commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(report["upstream"]["patch_sha256"], PATCH_SHA256)
        self.assertEqual(len(report["stock"]["stock_spans"]), 4)
        self.assertEqual(
            report["stock"]["layout"],
            {
                "allocation_offset": 0x6D,
                "mutex_offsets": [0x60, 0x64],
                "name_offset": 0x34,
                "name_size": 0x20,
                "notification_offsets": [0x68, 0x6C],
                "stack_depth_offset": 0x54,
                "tcb_size": 0x70,
                "trace_offsets": [0x58, 0x5C],
            },
        )
        self.assertEqual(len(report["unknowns"]), 2)

    def test_patch_applies_cleanly_to_authenticated_v10_5_1_files(self) -> None:
        work = self.stage_pristine_pair()
        self.apply_patch(work)
        tasks = (work / "tasks.c").read_text(encoding="utf-8")
        header = (work / "include" / "FreeRTOS.h").read_text(encoding="utf-8")
        self.assertEqual(tasks.count("uint32_t ulG2StackDepth;"), 1)
        self.assertEqual(
            tasks.count("pxNewTCB->ulG2StackDepth = ulStackDepth;"), 1,
        )
        self.assertEqual(header.count("uint32_t ulDummyG2StackDepth;"), 1)

    def test_patched_public_static_tcb_has_exact_target_layout(self) -> None:
        work = self.stage_pristine_pair()
        self.apply_patch(work)
        output = self.temp / "layout.o"
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-mthumb",
            "-std=c11",
            "-Oz",
            "-ffreestanding",
            "-fno-builtin",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I", str(work / "include"),
            "-I", str(CANDIDATE),
            "-I", str(KERNEL / "include"),
            "-I", str(PORT),
            "-c", str(FIXTURE),
            "-o", str(output),
        ]
        compiled = subprocess.run(
            command, check=False, capture_output=True, text=True,
        )
        self.assertEqual(
            compiled.returncode, 0, compiled.stderr or compiled.stdout,
        )
        self.assertGreater(output.stat().st_size, 0)

    def test_mutated_stock_image_is_rejected(self) -> None:
        mutated = bytearray(IMAGE.read_bytes())
        mutated[32 + 0x0045_4976 - 0x0043_8000] ^= 0x01
        path = self.temp / "mutated.bin"
        path.write_bytes(mutated)
        result = self.run_analyzer(str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("official package SHA-256 mismatch", result.stderr)

    def test_mutated_patch_is_rejected(self) -> None:
        path = self.temp / "mutated.patch"
        path.write_text(
            PATCH.read_text(encoding="utf-8").replace(
                "ulDummyG2StackDepth", "ulMutatedDepth", 1,
            ),
            encoding="utf-8",
        )
        result = self.run_analyzer("--patch", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("patch marker is not unique", result.stderr)


if __name__ == "__main__":
    unittest.main()
