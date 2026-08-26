from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
SOURCE = COMPONENT / "runtime_redirect_init.c"
HEADER = COMPONENT / "runtime_redirect_init.h"
FIXTURE = ROOT / "tests" / "fixtures" / "bootloader_redirect_init_host.c"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)

STOCK_ADDRESS = 0x00415590
STOCK_SIZE = 88
STOCK_SHA256 = (
    "b53b1d0eae9d2787d431ae1950d956c54429fb339a67ee7f219ff7c01ffc0cd6"
)
OVERLAY_ADDRESS = 0x00434478
FUNCTION_OFFSET = 664
FUNCTION_ADDRESS = OVERLAY_ADDRESS + FUNCTION_OFFSET
OVERLAY_SHA256 = (
    "6693a0fec4dfd7c9ba82639de56264a1ba1519768b6aa90b40885092f6fe4913"
)
PROVIDER_SHA256 = (
    "cb3ea4265d21ae37c0f7ec3671d67440f90cd0f05e3360b472716e69962aeb2d"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_bootloader_redirect_builder", BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bootloader builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BootloaderRedirectInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.library = cls.root / "redirect-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-dynamiclib",
                str(FIXTURE),
                "-o",
                str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_redirect_fixture_reset.argtypes = [
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        cls.lib.open_cfw_redirect_fixture_call.restype = ctypes.c_int
        for name in (
            "open_cfw_redirect_fixture_create_calls",
            "open_cfw_redirect_fixture_log_calls",
            "open_cfw_redirect_fixture_level",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint
        for name in (
            "open_cfw_redirect_fixture_stdout",
            "open_cfw_redirect_fixture_stdin",
        ):
            getattr(cls.lib, name).restype = ctypes.c_size_t
        cls.lib.open_cfw_redirect_fixture_line.restype = ctypes.c_long
        for name in (
            "open_cfw_redirect_fixture_tag",
            "open_cfw_redirect_fixture_file",
            "open_cfw_redirect_fixture_function",
            "open_cfw_redirect_fixture_message",
        ):
            getattr(cls.lib, name).restype = ctypes.c_char_p

        cls.builder = load_builder()
        cls.output = cls.root / "build"
        cls.report = cls.builder.build(
            root=ROOT,
            config_path=CONFIG,
            output_dir=cls.output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.overlay = (cls.output / "bootloader_core_overlay.bin").read_bytes()
        cls.provider = (cls.output / "ota_s200_bootloader.bin").read_bytes()
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _exercise(self, first: int, second: int) -> int:
        self.lib.open_cfw_redirect_fixture_reset(first, second)
        return self.lib.open_cfw_redirect_fixture_call()

    def test_success_creates_and_publishes_both_mutexes(self) -> None:
        self.assertEqual(self._exercise(0x1111, 0x2222), 0)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_create_calls(), 2)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_stdout(), 0x1111)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_stdin(), 0x2222)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_log_calls(), 1)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_level(), 3)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_line(), 0x275)
        self.assertEqual(
            self.lib.open_cfw_redirect_fixture_message(),
            b"redirect init with mutex protection.",
        )

    def test_either_allocation_failure_is_reported_after_both_attempts(self) -> None:
        for first, second in ((0, 0x2222), (0x1111, 0), (0, 0)):
            with self.subTest(first=first, second=second):
                self.assertEqual(self._exercise(first, second), -1)
                self.assertEqual(
                    self.lib.open_cfw_redirect_fixture_create_calls(), 2
                )
                self.assertEqual(
                    self.lib.open_cfw_redirect_fixture_stdout(), first
                )
                self.assertEqual(
                    self.lib.open_cfw_redirect_fixture_stdin(), second
                )
                self.assertEqual(self.lib.open_cfw_redirect_fixture_level(), 1)
                self.assertEqual(self.lib.open_cfw_redirect_fixture_line(), 0x271)
                self.assertEqual(
                    self.lib.open_cfw_redirect_fixture_message(),
                    b"Failed to create redirect mutex for IAR.",
                )

    def test_diagnostic_identity_matches_authenticated_entry(self) -> None:
        self.assertEqual(self._exercise(1, 2), 0)
        self.assertEqual(self.lib.open_cfw_redirect_fixture_tag(), b"redirect")
        self.assertEqual(
            self.lib.open_cfw_redirect_fixture_function(), b"redirect_init"
        )
        self.assertEqual(
            self.lib.open_cfw_redirect_fixture_file(),
            b"product\\s200\\bootloader\\config\\redirect.c",
        )

    def test_authenticated_stock_span_and_production_redirect(self) -> None:
        official = OFFICIAL.read_bytes()
        offset = STOCK_ADDRESS - 0x00410000
        self.assertEqual(sha256(official[offset : offset + STOCK_SIZE]), STOCK_SHA256)
        patch = next(
            item
            for item in self.report["overlay"]["patched_sites"]
            if item["name"] == "replace_bootloader_redirect_init"
        )
        self.assertEqual(patch["target_address"], FUNCTION_ADDRESS)
        self.assertEqual(patch["expected_size"], STOCK_SIZE)
        self.assertEqual(patch["expected_sha256"], STOCK_SHA256)
        self.assertEqual(patch["replacement_hex"][8:], "00bf" * 42)

    def test_relocated_closure_and_provider_are_pinned(self) -> None:
        self.assertEqual(len(self.overlay), 1856)
        self.assertEqual(sha256(self.overlay), OVERLAY_SHA256)
        self.assertEqual(len(self.provider), 150456)
        self.assertEqual(sha256(self.provider), PROVIDER_SHA256)
        function = self.report["overlay"]["functions"][
            "open_cfw_bootloader_redirect_init"
        ]
        self.assertEqual(function, {"offset": FUNCTION_OFFSET, "size": 132})
        leaf = next(
            item
            for item in self.report["relocated_leaves"]
            if item["extraction"]["function"]
            == "open_cfw_bootloader_redirect_init"
        )
        self.assertEqual(leaf["placement"]["size"], 275)
        self.assertEqual(leaf["extraction"]["relocation_count"], 12)
        self.assertEqual(
            {
                (item["symbol"], item["target_address"])
                for item in leaf["extraction"]["relocations"]
                if item["type"] == "R_ARM_THM_CALL"
            },
            {("osMutexNew", 0x00416610), ("elog_output", 0x004176CE)},
        )

    def test_source_and_config_are_fail_closed(self) -> None:
        self.assertEqual(sha256(SOURCE.read_bytes()), self.config[
            "relocated_leaves"
        ][0]["source"]["sha256"])
        self.assertIn("GPL-3.0-or-later", SOURCE.read_text(encoding="utf-8"))
        self.assertIn("0x2002712CU", HEADER.read_text(encoding="utf-8"))
        self.assertFalse(self.report["safety"]["flashing_performed"])
        self.assertEqual(self.report["safety"]["hardware_operations"], [])


if __name__ == "__main__":
    unittest.main()
