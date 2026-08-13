from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_style_reset.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_style_reset_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482796
STOCK_END = 0x004827B0
FREE_START = 0x0044F758
FREE_END = 0x0044F76A


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStyleResetDescriptor(ctypes.Structure):
    _fields_ = [
        ("table", ctypes.c_uint32),
        ("property_groups", ctypes.c_uint32),
        ("count_or_static", ctypes.c_ubyte),
        ("reserved_09", ctypes.c_ubyte),
        ("reserved_0a", ctypes.c_ubyte),
        ("reserved_0b", ctypes.c_ubyte),
    ]


class RuntimeStyleResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_reset.dylib"
            if sys.platform == "darwin"
            else "runtime_style_reset.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.install = cls.loaded.open_cfw_test_runtime_style_reset_install
        cls.install.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.install.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_style_reset_execute
        cls.execute.argtypes = []
        cls.execute.restype = None
        cls.style = RuntimeStyleResetDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_reset_descriptor",
        )
        cls.before = (ctypes.c_ubyte * 12).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_reset_zero_before",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def test_all_mutable_counts_release_table_then_zero_descriptor(
        self,
    ) -> None:
        for count in range(255):
            table = (0x10203040 + count * 0x01010101) & 0xFFFFFFFF
            groups = (0x89ABCDEF ^ (count * 0x11111111)) & 0xFFFFFFFF
            self.install(table, groups, count)
            expected_before = struct.pack(
                "<IIBBBB",
                table,
                groups,
                count,
                0x19,
                0x2A,
                0x3B,
            )
            self.execute()
            with self.subTest(count=count):
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_reset_free_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.pointer(
                        "open_cfw_test_runtime_style_reset_free_allocation"
                    ).value,
                    table,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_reset_free_order"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_reset_zero_order"
                    ).value,
                    2,
                )
                self.assertEqual(bytes(self.before), expected_before)
                self.assertEqual(
                    bytes(ctypes.string_at(ctypes.byref(self.style), 12)),
                    bytes(12),
                )

    def test_static_table_is_not_released_but_descriptor_is_zeroed(
        self,
    ) -> None:
        self.install(0xCAFEBABE, 0xA5A55A5A, 0xFF)
        self.execute()
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_reset_free_calls"
            ).value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_reset_zero_calls").value,
            1,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_reset_zero_size").value,
            12,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_runtime_style_reset_zero_destination"
            ).value,
            ctypes.addressof(self.style),
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_reset_zero_order").value,
            1,
        )
        self.assertEqual(
            bytes(ctypes.string_at(ctypes.byref(self.style), 12)),
            bytes(12),
        )

    def test_mutable_null_and_allocator_sentinel_are_forwarded(self) -> None:
        for table in (0, 0x2006F5AC):
            self.install(table, 0x13579BDF, 0)
            self.execute()
            with self.subTest(table=f"{table:#010x}"):
                observed = self.pointer(
                    "open_cfw_test_runtime_style_reset_free_allocation"
                ).value
                self.assertEqual(observed, None if table == 0 else table)
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_reset_free_calls"
                    ).value,
                    1,
                )

    def test_stock_boundary_callers_and_adjacent_functions_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x0048278C, STOCK_START)
        self.assertEqual(previous.hex(), "80b50c21fff7b4ff01bd")
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "32dde2f27cf8bbf895887f8ee6cb5b8a"
            "3c984cbd1c06e5c14187215bc9884e61",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(
            stock.hex(),
            "10b50400207aff2802d02068ccf7d9ff"
            "0c212000fff7a7ff10bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "a6778c79bfe8434836675b4a11922ac8"
            "43309a8a5e08af876bf2a1e2007bb975",
        )

        following = span(STOCK_END, 0x00482868)
        self.assertEqual(len(following), 184)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "7301b5de7a8104a456296a6d2b4a74e6"
            "f978ed913109aeae4d02b54865d46360",
        )

        contexts = {
            (0x0044BB88, 0x0044BBA4):
                "229afcdc67ae42c2e5ccbcd5560dfbdd"
                "932e36ff3c9a8d9cfa64b54e759b6d5b",
            (0x0048819C, 0x004881B4):
                "c3e41069d4cd2d5adc525cc1e8e00163"
                "9a8d7a3f784988471630ad2256e9ad4a",
        }
        for (start, end), expected in contexts.items():
            context = span(start, end)
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(hashlib.sha256(context).hexdigest(), expected)

    def test_reset_wide_call_and_dependency_topology_is_complete(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x0044BB94, "36f0fffd"),
                (0x004881A8, "faf7f5fa"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x004827A2, FREE_START, "ccf7d9ff"),
                (0x004827AA, 0x004826FC, "fff7a7ff"),
            ],
        )

    def test_retained_free_wrapper_abi_and_all_callers_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(FREE_START, FREE_END)
        self.assertEqual(
            stock.hex(),
            "80b51249884203d0002801d034f0e8fd01bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "f4c5f66b61c9e19b839c553e4f8173b"
            "0073543ac72c0ab57c199ff51c07f67d4",
        )
        self.assertEqual(
            struct.unpack("<I", span(0x0044F7A4, 0x0044F7A8))[0],
            0x2006F5AC,
        )
        backend = span(0x00484338, 0x00484344)
        self.assertEqual(
            backend.hex(),
            "80b501000b48fff7aeff01bd",
        )
        self.assertEqual(
            hashlib.sha256(backend).hexdigest(),
            "faf392e39c380a7622fdf8194c285455"
            "f7e82e5705ae9eb8118e0c1b846521da",
        )

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == FREE_START:
                    observed.append(address)
                if (
                    FREE_START < target < FREE_END
                    and not FREE_START <= address < FREE_END
                ):
                    interior.append((address, target, link))
                if link and FREE_START <= address < FREE_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(len(callers), 122)
        self.assertEqual(
            hashlib.sha256(
                b"".join(struct.pack("<I", address) for address in callers)
            ).hexdigest(),
            "fed63006a21f2f806a155ea3aae0eed73"
            "1bb1169d7605b2a539f028e8cca3e1f",
        )
        self.assertIn(0x004827A2, callers)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x0044F764, 0x00484338, "34f0e8fd")],
        )

        recovered_unindexed = {
            (0x0050EBA8, 0x0050EBCC):
                "85de03537d8d518f729aba3210f905144"
                "10ce2259eb3081ebd52b280a82079e5",
            (0x005C46B2, 0x005C46D6):
                "6a3daafe730a5cb2fcd923f40998e58b"
                "9c91537f8d4c5cf070935e93bd803dbd",
            (0x005C7E56, 0x005C7E7A):
                "802c4f3eb839b882180938f957babf88"
                "5f23a9e26e082076875675b23f5dadc4",
        }
        for (start, end), expected in recovered_unindexed.items():
            context = span(start, end)
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(hashlib.sha256(context).hexdigest(), expected)

    def test_reset_and_free_have_no_external_narrow_or_pointer_entries(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        expected_internal = {
            (STOCK_START, STOCK_END): [
                (0x0048279E, 0x004827A6, 0xD002),
            ],
            (FREE_START, FREE_END): [
                (0x0044F75E, 0x0044F768, 0xD003),
                (0x0044F762, 0x0044F768, 0xD001),
            ],
        }
        for (start, end), expected in expected_internal.items():
            narrow_entry = []
            narrow_interior = []
            internal = []
            for offset in range(0, len(application) - 1, 2):
                address = APPLICATION_BASE + offset
                halfword = struct.unpack_from("<H", application, offset)[0]
                candidates = []
                if halfword & 0xF800 == 0xE000:
                    candidates.append(
                        address
                        + 4
                        + _sign_extend((halfword & 0x7FF) << 1, 12)
                    )
                condition = (halfword >> 8) & 0xF
                if halfword & 0xF000 == 0xD000 and condition < 0xE:
                    candidates.append(
                        address
                        + 4
                        + _sign_extend((halfword & 0xFF) << 1, 9)
                    )
                if halfword & 0xF500 == 0xB100:
                    immediate = (
                        ((halfword >> 9) & 1) << 6
                        | ((halfword >> 3) & 0x1F) << 1
                    )
                    candidates.append(address + 4 + immediate)
                if start in candidates:
                    narrow_entry.append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior.append(
                            (address, target, halfword)
                        )
                    if (
                        start <= address < end
                        and start <= target < end
                    ):
                        internal.append((address, target, halfword))

            stored = []
            for offset in range(0, len(application) - 3):
                value = struct.unpack_from("<I", application, offset)[0]
                target = value & ~1
                if value & 1 and start <= target < end:
                    stored.append((APPLICATION_BASE + offset, target))

            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(narrow_entry, [])
                self.assertEqual(narrow_interior, [])
                self.assertEqual(internal, expected)
                self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "void open_cfw_runtime_style_reset(void *style_pointer)",
            "style->count_or_static != 0xFFU",
            "OPEN_CFW_RUNTIME_STYLE_RESET_FREE(",
            "0x0044F759U",
            "OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO(",
            "sizeof(*style)",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_style_reset.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
