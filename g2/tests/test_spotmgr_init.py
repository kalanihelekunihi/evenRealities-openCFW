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
SOURCE = COMPONENT_ROOT / "spotmgr_init.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_init_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000

PCM2P2 = (
    0x005A4D49,
    0x005A490D,
    0x005A4E0D,
    0,
    0,
    0,
    0,
    0x005A4D01,
    0,
    0,
    0x005A40B7,
    0x005A40CB,
    0,
    0,
    0,
)
PCM2P1 = (
    0x005A1C19,
    0x005A1739,
    0x005A1DA5,
    0,
    0,
    0x005A1BBD,
    0x005A1BCD,
    0x005A1BED,
    0,
    0,
    0,
    0x005A0BCD,
    0,
    0,
    0,
)
PCM2P0 = (
    0x005A08E5,
    0x005A0787,
    0x005A0A6D,
    0x005A07E7,
    0x005A07F1,
    0,
    0x005A081D,
    0x005A0843,
    0,
    0,
    0,
    0,
    0x005A085F,
    0x005A08B7,
    0x005A08CB,
)
PCM1P0 = (
    *PCM2P0[:6],
    0x0059FD83,
    0x0059FDA9,
    *PCM2P0[8:],
)
PCM0P7 = (
    0x005A0019,
    0x0059FD37,
    0,
    0,
    0,
    0,
    0x0059FD83,
    0x0059FDA9,
    0x0059FDC3,
    0x0059FE5B,
    0,
    0,
    0,
    0,
    0,
)
FIXED_B0 = (
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0x0059FDC3,
    0x0059FE5B,
    0,
    0,
    0,
    0,
    0,
)
EMPTY = (0,) * 15

HANDLER_LITERALS = (
    0x005A4D49,
    0x005A490D,
    0x005A4E0D,
    0x005A4D01,
    0x005A40B7,
    0x005A40CB,
    0x005A1C19,
    0x005A1739,
    0x005A1DA5,
    0x005A1BBD,
    0x005A1BCD,
    0x005A1BED,
    0x005A0BCD,
    0x005A08E5,
    0x005A0787,
    0x005A0A6D,
    0x005A07E7,
    0x005A07F1,
    0x005A085F,
    0x005A08B7,
    0x005A08CB,
    0x0059FD83,
    0x0059FDA9,
    0x005A081D,
    0x005A0843,
    0x005A0019,
    0x0059FD37,
    0x0059FDC3,
    0x0059FE5B,
)

MATRIX = (
    ("B3+", 0x24, 0, 1, PCM2P2, (0, 0, 0, 0, 1, 0)),
    ("B2 PCM2.2", 0x23, 2, 1, PCM2P2, (0, 0, 0, 0, 1, 0)),
    ("B2 PCM2.1", 0x23, 1, 1, PCM2P1, (1, 0, 0, 0, 0, 0)),
    ("B1 PCM2.1", 0x22, 2, 1, PCM2P1, (1, 0, 0, 0, 0, 0)),
    ("B2 PCM2.0", 0x23, 0, 1, PCM2P0, (0, 0, 0, 1, 0, 0)),
    ("B1 PCM2.0", 0x22, 1, 1, PCM2P0, (0, 0, 0, 1, 0, 0)),
    ("B1 PCM1.1", 0x22, 0, 1, PCM2P0, (0, 1, 0, 0, 0, 0)),
    ("B0 PCM1.1", 0x21, 3, 1, PCM2P0, (0, 1, 1, 0, 0, 0)),
    ("B0 PCM1.0", 0x21, 2, 1, PCM1P0, (0, 1, 0, 0, 0, 0)),
    ("B0 PCM0.7", 0x21, 1, 1, PCM0P7, (0, 0, 0, 0, 0, 0)),
    ("B0 fixed", 0x21, 0, 1, FIXED_B0, (0, 0, 0, 0, 0, 0)),
    ("unknown", 0x20, 7, 1, EMPTY, (0, 0, 0, 0, 0, 0)),
)


class SpotmgrInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_init.dylib"
            if sys.platform == "darwin"
            else "spotmgr_init.so"
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
        cls.reset = cls.loaded.open_cfw_test_spotmgr_init_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.initialize = cls.loaded.open_cfw_spotmgr_init
        cls.initialize.argtypes = []
        cls.initialize.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_init_{name}",
        )

    @classmethod
    def state(cls) -> ctypes.Array:
        return (ctypes.c_uint * 15).in_dll(
            cls.loaded,
            "open_cfw_test_spotmgr_init_state",
        )

    @classmethod
    def flags(cls) -> ctypes.Array:
        return (ctypes.c_ubyte * 6).in_dll(
            cls.loaded,
            "open_cfw_test_spotmgr_init_flags",
        )

    @classmethod
    def events(cls, field: str) -> ctypes.Array:
        return (ctypes.c_uint * 96).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_init_event_{field}",
        )

    def configure(
        self,
        revision: int,
        trim: int,
        patch_tracker0: int,
    ) -> None:
        self.word("chip_revision").value = revision
        self.word("trim_version").value = trim
        self.word("patch_tracker0").value = patch_tracker0

    def test_version_matrix_selects_exact_stock_handler_tables(self) -> None:
        for name, revision, trim, patch, expected, _ in MATRIX:
            with self.subTest(name=name):
                self.reset()
                self.configure(revision, trim, patch)
                self.initialize()
                self.assertEqual(tuple(self.state()), expected)

    def test_version_matrix_populates_all_six_cached_flags(self) -> None:
        for name, revision, trim, patch, _, expected in MATRIX:
            with self.subTest(name=name):
                self.reset()
                self.configure(revision, trim, patch)
                self.initialize()
                self.assertEqual(tuple(self.flags()), expected)

        for name, revision, trim in (
            ("B1", 0x22, 2),
            ("B2", 0x23, 1),
        ):
            with self.subTest(name=f"{name} PCM2.1 without patch"):
                self.reset()
                self.configure(revision, trim, 0)
                self.initialize()
                self.assertEqual(tuple(self.flags()), (1, 0, 0, 0, 0, 1))

    def test_state_is_cleared_in_slot_order_before_selection(self) -> None:
        self.reset()
        self.configure(0x23, 2, 1)
        self.initialize()

        count = self.word("event_count").value
        kinds = self.events("kind")
        addresses = self.events("address")
        values = self.events("value")
        self.assertGreater(count, 15)
        self.assertEqual(tuple(kinds[:15]), (1,) * 15)
        self.assertEqual(tuple(addresses[:15]), tuple(range(0, 0x3C, 4)))
        self.assertEqual(tuple(values[:15]), (0,) * 15)

    def test_analog_patch_preserves_bits_and_exact_rmw_order(self) -> None:
        for name, revision, trim, patch in (
            ("PCM1.0", 0x21, 2, 1),
            ("PCM1.1", 0x22, 0, 1),
            ("PCM2.0", 0x22, 1, 1),
            ("PCM2.1 without patch", 0x22, 2, 0),
        ):
            with self.subTest(name=name):
                self.reset()
                self.configure(revision, trim, patch)
                self.word("acrg").value = 0xA5A50002
                self.word("vrctrl").value = 0x55AA0000
                self.initialize()

                self.assertEqual(self.word("acrg").value, 0xA5A50001)
                self.assertEqual(self.word("vrctrl").value, 0x55AAE000)
                count = self.word("event_count").value
                events = [
                    (kind, address, value)
                    for kind, address, value in zip(
                        self.events("kind")[:count],
                        self.events("address")[:count],
                        self.events("value")[:count],
                    )
                    if kind in (2, 3, 4, 5)
                ]
                self.assertEqual(
                    events,
                    [
                        (2, 0x40020028, 0xA5A50002),
                        (3, 0x40020028, 0xA5A50000),
                        (2, 0x40020028, 0xA5A50000),
                        (3, 0x40020028, 0xA5A50001),
                        (4, 0x40020060, 0x55AA0000),
                        (5, 0x40020060, 0x55AA8000),
                        (4, 0x40020060, 0x55AA8000),
                        (5, 0x40020060, 0x55AAC000),
                        (4, 0x40020060, 0x55AAC000),
                        (5, 0x40020060, 0x55AAE000),
                    ],
                )

    def test_analog_patch_is_suppressed_for_unaffected_versions(self) -> None:
        for name, revision, trim, patch in (
            ("PCM2.2", 0x23, 2, 1),
            ("PCM2.1 patched", 0x23, 1, 1),
            ("PCM0.7", 0x21, 1, 1),
            ("unknown", 0x20, 0, 1),
        ):
            with self.subTest(name=name):
                self.reset()
                self.configure(revision, trim, patch)
                self.word("acrg").value = 0x11223344
                self.word("vrctrl").value = 0x55667788
                self.initialize()
                self.assertEqual(self.word("acrg").value, 0x11223344)
                self.assertEqual(self.word("vrctrl").value, 0x55667788)
                count = self.word("event_count").value
                self.assertFalse(
                    any(
                        kind in (2, 3, 4, 5)
                        for kind in self.events("kind")[:count]
                    )
                )

    def test_selected_initializer_result_is_returned(self) -> None:
        for name, revision, trim, _, expected, _ in MATRIX:
            with self.subTest(name=name):
                self.reset()
                self.configure(revision, trim, 1)
                result = self.initialize()
                if expected[0] == 0:
                    self.assertEqual(result, 0)
                    self.assertEqual(self.word("call_count").value, 0)
                    self.assertEqual(
                        self.word_array("handler_reads", 15)[0],
                        1,
                    )
                else:
                    self.assertEqual(
                        result,
                        expected[0] ^ 0xA5A55A5A,
                    )
                    self.assertEqual(self.word("call_count").value, 1)
                    self.assertEqual(
                        self.word("called_handler").value,
                        expected[0],
                    )
                    self.assertEqual(
                        self.word_array("handler_reads", 15)[0],
                        2,
                    )

    @classmethod
    def word_array(cls, name: str, size: int) -> ctypes.Array:
        return (ctypes.c_uint * size).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_init_{name}",
        )

    def test_initializer_call_uses_a_fresh_second_handler_read(self) -> None:
        self.reset()
        self.configure(0x23, 2, 1)
        self.word("override_second_handler").value = 1
        self.word("second_handler").value = 0x12345679

        result = self.initialize()

        self.assertEqual(result, 0x12345679 ^ 0xA5A55A5A)
        self.assertEqual(self.word("called_handler").value, 0x12345679)
        self.assertEqual(self.word_array("handler_reads", 15)[0], 2)

    def test_stock_body_pool_and_next_boundary_are_review_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        body = application[
            0x00480434 - APPLICATION_BASE:
            0x004806D0 - APPLICATION_BASE
        ]
        pool = application[
            0x004806D0 - APPLICATION_BASE:
            0x004807A0 - APPLICATION_BASE
        ]
        self.assertEqual(len(body), 668)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "892f39cd717b6f7ef3218fc23730c1ac"
            "2e2d10143effd59eedb6584b412dfd83",
        )
        self.assertEqual(len(pool), 208)
        self.assertEqual(
            hashlib.sha256(pool).hexdigest(),
            "d2ee77b38e4e3b895fa544672c1f244e"
            "13ac0ccce2afeff1b626758d2bbdf162",
        )
        self.assertEqual(
            hashlib.sha256(body + pool).hexdigest(),
            "b10962167a9d6faa0001d5ff9178f5e8"
            "647ce774b1941c0e5d14560fcc390148",
        )
        duration_delay = application[
            0x004807A0 - APPLICATION_BASE:
            0x004807FC - APPLICATION_BASE
        ]
        self.assertEqual(len(duration_delay), 92)
        self.assertEqual(
            hashlib.sha256(duration_delay).hexdigest(),
            "10ca20e1a01a30d82ec2e215caaa2abe"
            "57087c1e68ff4182e4e848d974326a6f",
        )

    def test_stock_topology_and_handler_literal_table_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        start = 0x00480434
        end = 0x004806D0
        calls = []
        jumps = []
        external_interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == start:
                    observed.append(address)
                if (
                    start < target < end
                    and not start <= address < end
                ):
                    external_interior.append((address, target, link))
                if link and start <= address < end:
                    dependencies.append((address, target))
        self.assertEqual(calls, [0x0047FBB2])
        self.assertEqual(jumps, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(dependencies, [(0x00480444, 0x0043C0E4)])

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and start <= target < end:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

        handlers = application[
            0x0048072C - APPLICATION_BASE:
            0x004807A0 - APPLICATION_BASE
        ]
        self.assertEqual(len(handlers), 116)
        self.assertEqual(
            hashlib.sha256(handlers).hexdigest(),
            "4e8425ee94ea1c0e3e94aff01227d696"
            "4d4d94223553911814c78f9e2083b858",
        )
        self.assertEqual(
            struct.unpack("<29I", handlers),
            HANDLER_LITERALS,
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0f5e08e17b869bd6ddf6ba1ad25b05a4"
            "b98f8c6ebd9f869999e1a2505b28fb67",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "958fe39da7cc0d30ada46120e2627b22c"
            "7645dbc9accfe2c2df7f8c2272dee34",
        )


if __name__ == "__main__":
    unittest.main()
