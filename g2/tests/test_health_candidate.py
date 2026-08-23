from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/health.c"
FIXTURE = ROOT / "tests/fixtures"


class HealthCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / ("health" + suffix)
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "health_host.h"),
                str(SOURCE), str(FIXTURE / "health_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.init = cls.loaded.open_cfw_health_data_mutex_init
        cls.init.restype = ctypes.c_int
        cls.lock = cls.loaded.open_cfw_health_lock_storage
        cls.lock.restype = ctypes.c_uint
        cls.unlock = cls.loaded.open_cfw_health_unlock_storage
        cls.handler = cls.loaded.open_cfw_health_common_data_handler
        cls.handler.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
        ]
        cls.handler.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def word(self, name):
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def reset(self, create=1, acquire=0, provider=0, lens=1, running=1, matches=1):
        self.loaded.open_cfw_test_health_reset(
            create, acquire, provider, lens, running, matches
        )

    def test_mutex_init_is_lazy_and_failure_is_explicit(self):
        self.reset(create=0)
        self.assertEqual(self.init(), -1)
        self.assertEqual(self.word("open_cfw_test_health_new_calls"), 1)

        self.reset(create=1)
        self.assertEqual(self.init(), 0)
        self.assertEqual(self.init(), 0)
        self.assertEqual(self.word("open_cfw_test_health_new_calls"), 1)

    def test_lock_and_unlock_preserve_cmsis_contract(self):
        self.reset(acquire=0)
        self.assertEqual(self.lock(), 0)
        self.assertEqual(self.init(), 0)
        self.assertEqual(self.lock(), 1)
        self.assertEqual(self.word("open_cfw_test_health_acquire_timeout"), 0xFFFFFFFF)
        self.unlock()
        self.assertEqual(self.word("open_cfw_test_health_release_calls"), 1)

        self.reset(acquire=-2)
        self.assertEqual(self.init(), 0)
        self.assertEqual(self.lock(), 0)

    def test_event_zero_posts_only_after_all_policy_gates(self):
        payload = (ctypes.c_ubyte * 2)(0x11, 0x22)
        self.reset()
        self.assertEqual(self.handler(0, payload, 0x10002), 0)
        self.assertEqual(self.word("open_cfw_test_health_provider_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_health_provider_length"), 2)
        self.assertEqual(self.word("open_cfw_test_health_post_calls"), 1)
        self.assertEqual(self.word("open_cfw_test_health_post_service"), 1)
        self.assertEqual(self.word("open_cfw_test_health_post_length"), 6)
        self.assertEqual(self.word("open_cfw_test_health_post_flags"), 0)
        record = (ctypes.c_ubyte * 6).in_dll(
            self.loaded, "open_cfw_test_health_post_record"
        )
        self.assertEqual(bytes(record), b"\x06\x00\x00\x00\x00\x00")

        for provider, lens, running, matches in (
            (1, 1, 1, 1),
            (0, 0, 1, 1),
            (0, 1, 0, 1),
            (0, 1, 1, 0),
        ):
            with self.subTest(
                provider=provider, lens=lens, running=running, matches=matches
            ):
                self.reset(provider=provider, lens=lens, running=running, matches=matches)
                self.assertEqual(self.handler(0, payload, 2), 0)
                self.assertEqual(self.word("open_cfw_test_health_post_calls"), 0)

    def test_common_and_unknown_events_are_side_effect_free(self):
        one = (ctypes.c_ubyte * 1)(1)
        other = (ctypes.c_ubyte * 1)(7)
        for event, payload, length in (
            (5, None, 0),
            (5, one, 1),
            (5, other, 1),
            (9, other, 1),
        ):
            with self.subTest(event=event, length=length):
                self.reset()
                self.assertEqual(self.handler(event, payload, length), 0)
                self.assertEqual(self.word("open_cfw_test_health_provider_calls"), 0)
                self.assertEqual(self.word("open_cfw_test_health_post_calls"), 0)
                self.assertEqual(self.word("open_cfw_test_health_new_calls"), 1)

    def test_thumb_object_exposes_exactly_four_text_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "health.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            text_symbols = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(
                text_symbols,
                {
                    "open_cfw_health_data_mutex_init",
                    "open_cfw_health_lock_storage",
                    "open_cfw_health_unlock_storage",
                    "open_cfw_health_common_data_handler",
                },
            )


if __name__ == "__main__":
    unittest.main()
