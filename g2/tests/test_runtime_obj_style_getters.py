from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_obj_style_getters.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_obj_style_getters_host.c"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000

# (address, size, stock body SHA-256, symbol, LV_STYLE_* property ID)
GETTERS = [
    (0x43EEA6, 10, "c85e8f548768d2fafd19c7a7c1229a33000825e62840c139ffefe42b9fb2b6fc", "open_cfw_runtime_obj_get_style_width", 0x01),
    (0x43EEB0, 10, "3bb76ad0fcc4dc49828cdd473166f0e01feacf1bfd82e6a09fd1c497b3f6e93d", "open_cfw_runtime_obj_get_style_min_width", 0x04),
    (0x43EEBA, 10, "0c0ac6428a6ed1062fda0b1c56ebad143e39fd1a47e4e4e2e6d87f78e688dd4c", "open_cfw_runtime_obj_get_style_max_width", 0x05),
    (0x43EEC4, 10, "0fd184d2a0f6494d4c321fb75712e331db44f642f11df5756640d65b6fc9769a", "open_cfw_runtime_obj_get_style_height", 0x02),
    (0x43EECE, 10, "725870146fed9b551a1561c3cb74872fd6295ac7ffeded7ccdbd392a58cfcb1c", "open_cfw_runtime_obj_get_style_min_height", 0x06),
    (0x43EED8, 10, "f119b60c77acac0b2aff4a1eab849bf5396c6680290104743ea122cfd763fb6e", "open_cfw_runtime_obj_get_style_max_height", 0x07),
    (0x43EEE2, 10, "65e4fe934e582e8e93e86fa28c55c8cb8a739de8f779aca1f347740c23be46bc", "open_cfw_runtime_obj_get_style_x", 0x08),
    (0x43EEEC, 10, "b4cb9d8be30e82f84aba8871a9b799a0118db6c6d35ba51e4e722ae988d2a0c9", "open_cfw_runtime_obj_get_style_y", 0x09),
    (0x43EEF6, 12, "d38a0826f0ec40fe7124dc2058c8c5231d712e66d1664691fd0f8d148d1c449a", "open_cfw_runtime_obj_get_style_align", 0x0A),
    (0x43EF02, 10, "6b20a6e2088975a421ec1f395c0da7a2556f62796b61d68f7a2fe1e76e338218", "open_cfw_runtime_obj_get_style_translate_x", 0x6C),
    (0x43EF0C, 10, "ec27ad8759a03a55216622be669b8a1626d9a7bc375d951bac203e49d7f66eb1", "open_cfw_runtime_obj_get_style_translate_y", 0x6D),
    (0x43EF16, 10, "8b5394a903487b437f9aeececf0ce5909953fadfb9621e017239073ffb755b48", "open_cfw_runtime_obj_get_style_transform_scale_x", 0x6E),
    (0x43EF20, 10, "e84dfc3c2d2f67f0b287b24c66c9552a59ac6650a77cf0676f3366d07d8d6c10", "open_cfw_runtime_obj_get_style_transform_scale_y", 0x6F),
    (0x43EF2A, 10, "2883f9afe3e947d357373e5fc78f5be2e907b5207e44d33c0cb86077f232c0fe", "open_cfw_runtime_obj_get_style_transform_rotation", 0x70),
    (0x43EF34, 10, "3e8018235e613152fd1b5a9aab4f39c1cc46ef05c03e247e1e1ad7bbefd0c234", "open_cfw_runtime_obj_get_style_transform_pivot_x", 0x71),
    (0x43EF3E, 10, "b41dfcb99128339f1370792aaddbf4b084fd4e41d1098a6828cb40877f4c219f", "open_cfw_runtime_obj_get_style_transform_pivot_y", 0x72),
    (0x43EF48, 10, "4b72243058ee631df63d343145b7ecfeeab292a7bc8a2a0de0c3a843acfe3ead", "open_cfw_runtime_obj_get_style_pad_top", 0x10),
    (0x43EF52, 10, "25b16ef9447a822939a5a09fb30a6caa4314ec67024a0f7275f43e5f17c305f5", "open_cfw_runtime_obj_get_style_pad_bottom", 0x11),
    (0x43EF5C, 10, "26596153d1aedaed7c1cec579f4abfafa286560cf18ae2503f50310e9a4980f5", "open_cfw_runtime_obj_get_style_pad_left", 0x12),
    (0x43EF66, 10, "d7c153b4052647094927b4bb145fd61017a1af01f13fec8211f02499bb640242", "open_cfw_runtime_obj_get_style_pad_right", 0x13),
]


class RuntimeObjStyleGettersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / (
            "a.dylib" if sys.platform == "darwin" else "a.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        command += (
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_style_getter_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.functions = {}
        for _, _, _, name, _ in GETTERS:
            fn = getattr(cls.loaded, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
            cls.functions[name] = fn

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def test_every_getter_forwards_obj_part_and_its_property_id(self) -> None:
        for _, _, _, name, property_id in GETTERS:
            with self.subTest(getter=name):
                self.reset(0xC0FFEE ^ property_id)
                result = self.functions[name](0xAAAA0000 | property_id, 0x03)
                self.assertEqual(self.uint(
                    "open_cfw_test_runtime_style_getter_calls"
                ), 1)
                self.assertEqual(self.uint(
                    "open_cfw_test_runtime_style_getter_obj"
                ), 0xAAAA0000 | property_id)
                self.assertEqual(self.uint(
                    "open_cfw_test_runtime_style_getter_part"
                ), 0x03)
                self.assertEqual(self.uint(
                    "open_cfw_test_runtime_style_getter_property"
                ), property_id)
                self.assertEqual(result, 0xC0FFEE ^ property_id)

    def test_stock_body_hashes_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        for address, size, expected_sha256, name, _ in GETTERS:
            with self.subTest(getter=name):
                body = application[address - BASE:address - BASE + size]
                self.assertEqual(len(body), size)
                self.assertEqual(
                    hashlib.sha256(body).hexdigest(), expected_sha256
                )

    def test_spans_are_contiguous_and_cover_the_item_tail(self) -> None:
        addresses = [address for address, _, _, _, _ in GETTERS]
        sizes = [size for _, size, _, _, _ in GETTERS]
        for index in range(len(addresses) - 1):
            self.assertEqual(
                addresses[index] + sizes[index], addresses[index + 1]
            )
        self.assertEqual(addresses[0], 0x43EEA6)
        self.assertEqual(addresses[-1] + sizes[-1], 0x43EF70)


if __name__ == "__main__":
    unittest.main()
