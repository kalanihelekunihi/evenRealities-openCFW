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
SOURCE = COMPONENT_ROOT / "spotmgr_dispatch.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_dispatch_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000

SPANS = (
    (
        "power_state_update",
        "open_cfw_spotmgr_power_state_update",
        0x00480312,
        0x0048032C,
        0x04,
        "7326c380a8adcc941d53fc273b9e504f"
        "ce5ee461ecd3203ec89d8393cdf20ffb",
        (
            0x0047EF96,
            0x0047F078,
            0x0047F090,
            0x0047F2D0,
            0x0047F3E4,
            0x0047F462,
            0x0047F496,
            0x0047F4E2,
            0x0047F646,
            0x0047F660,
            0x0047F67C,
            0x0047F8C4,
            0x0047F8E4,
            0x0047F8FE,
            0x0047FF82,
            0x0047FFAC,
            0x00480036,
        ),
    ),
    (
        "tempco_postpone",
        "open_cfw_spotmgr_tempco_postpone",
        0x0048032C,
        0x00480342,
        0x0C,
        "299afbf08eed5f6ac7e70ae1fefa733f"
        "3730c0f3dd7356ed5d4abd1de9632aa2",
        (0x0047F5F6, 0x0047F842),
    ),
    (
        "tempco_pending_handle",
        "open_cfw_spotmgr_tempco_pending_handle",
        0x00480342,
        0x00480358,
        0x10,
        "f2ee82053ae0491fe93d3a17bddb574e"
        "d57d92ebe459192f953cdd5a0adc868e",
        (0x0047F698, 0x0047F902),
    ),
    (
        "simobuck_init_bfr_ovr",
        "open_cfw_spotmgr_simobuck_init_bfr_ovr",
        0x00480358,
        0x0048036E,
        0x14,
        "184cb5fae243eafb29684d35c820556e"
        "29a45c9bd7f00bd31f3ad7903625bc63",
        (0x0047FEC2,),
    ),
    (
        "simobuck_init_bfr_enable",
        "open_cfw_spotmgr_simobuck_init_bfr_enable",
        0x0048036E,
        0x00480384,
        0x18,
        "836b2a110708d11267b365c0a14acfd7"
        "6f173aa870d8a614332e5a0cf45c7be9",
        (0x0047FEDE,),
    ),
    (
        "simobuck_init_aft_enable",
        "open_cfw_spotmgr_simobuck_init_aft_enable",
        0x00480384,
        0x0048039A,
        0x1C,
        "87803212ab023a17af86dde3bcf2c7ad"
        "e5196e180f5d0f7a3804e1e33b1ae717",
        (0x0047FEEC,),
    ),
    (
        "boost_timer_interrupt_service",
        "open_cfw_spotmgr_boost_timer_interrupt_service",
        0x0048039A,
        0x004803AC,
        0x2C,
        "7de30a98407fec1b6601009c1e4a51f3"
        "1415621d7809235b65717f45a2a04107",
        (0x004D58A8,),
    ),
    (
        "ton_config_init",
        "open_cfw_spotmgr_ton_config_init",
        0x004803AC,
        0x004803C2,
        0x20,
        "363e899b636d4d8ef9c6812f5229a8fe"
        "8de05cced2c893cb1cf7c183a565f79d",
        (0x0047FDDA,),
    ),
    (
        "ton_config_update",
        "open_cfw_spotmgr_ton_config_update",
        0x004803C2,
        0x004803DC,
        0x24,
        "b5b85f35f5dcf82a15c0319e949a8f0"
        "36018ece8cc078889686d523340dda3ad",
        (0x0047F19E, 0x0047F1F6, 0x0047FDE6, 0x0059FBB8, 0x0059FD2E),
    ),
    (
        "post_lptohp_handle",
        "open_cfw_spotmgr_post_lptohp_handle",
        0x004803DC,
        0x004803F2,
        0x28,
        "217ac111afb20339d761a7da1c03f040"
        "36ce8e07b2eb2165581a78a4bba087b5",
        (0x0047F026,),
    ),
    (
        "simobuck_lp_autosw_init",
        "open_cfw_spotmgr_simobuck_lp_autosw_init",
        0x004803F2,
        0x00480408,
        0x30,
        "63039daa4a33c14e015bdf7df23350d99"
        "9ec626843167d2cf5d5e976749fc341",
        (0x0047FDF0,),
    ),
    (
        "simobuck_lp_autosw_enable",
        "open_cfw_spotmgr_simobuck_lp_autosw_enable",
        0x00480408,
        0x0048041E,
        0x34,
        "b6d30d3b9553b0009331f4a22f543a4"
        "3f35f9daf7fc5bb78b96acc601fbb7b95",
        (),
    ),
    (
        "simobuck_lp_autosw_disable",
        "open_cfw_spotmgr_simobuck_lp_autosw_disable",
        0x0048041E,
        0x00480434,
        0x38,
        "a13a73f8052507b0d0757ae51acbbebb"
        "64fd0063ec537d7034e21148b9f02c11",
        (),
    ),
)


class SpotmgrDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_dispatch.dylib"
            if sys.platform == "darwin"
            else "spotmgr_dispatch.so"
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
        cls.reset = cls.loaded.open_cfw_test_spotmgr_dispatch_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.configure = cls.loaded.open_cfw_test_spotmgr_dispatch_configure
        cls.configure.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.configure.restype = None

        cls.functions = {}
        for _, symbol, _, _, offset, _, _ in SPANS:
            function = getattr(cls.loaded, symbol)
            if offset == 0x04:
                function.argtypes = [
                    ctypes.c_uint,
                    ctypes.c_uint,
                    ctypes.c_void_p,
                ]
                function.restype = ctypes.c_uint
            elif offset == 0x24:
                function.argtypes = [ctypes.c_uint, ctypes.c_uint]
                function.restype = ctypes.c_uint
            elif offset == 0x2C:
                function.argtypes = []
                function.restype = None
            else:
                function.argtypes = []
                function.restype = ctypes.c_uint
            cls.functions[offset] = function

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_dispatch_{name}",
        )

    @classmethod
    def pointer(cls, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_dispatch_{name}",
        )

    @classmethod
    def reads(cls) -> ctypes.Array:
        return (ctypes.c_uint * 15).in_dll(
            cls.loaded,
            "open_cfw_test_spotmgr_dispatch_reads",
        )

    @classmethod
    def invoke(cls, offset: int) -> int | None:
        if offset == 0x04:
            return cls.functions[offset](
                0x123,
                0x1FE,
                ctypes.c_void_p(0x12345678),
            )
        if offset == 0x24:
            return cls.functions[offset](0x1AB, 0x2CD)
        return cls.functions[offset]()

    def test_null_slots_are_successful_no_ops(self) -> None:
        for name, _, _, _, offset, _, _ in SPANS:
            with self.subTest(name=name):
                self.reset()
                self.configure(offset, 0)
                result = self.invoke(offset)
                if offset != 0x2C:
                    self.assertEqual(result, 0)
                self.assertEqual(self.reads()[offset // 4], 1)
                self.assertEqual(self.word("call_count").value, 0)

    def test_each_entry_uses_a_fresh_second_handler_read(self) -> None:
        secondary_result = self.word("secondary_result")
        for name, _, _, _, offset, _, _ in SPANS:
            with self.subTest(name=name):
                self.reset()
                self.configure(offset, 2)
                result = self.invoke(offset)
                if offset != 0x2C:
                    self.assertEqual(result, secondary_result.value)
                self.assertEqual(self.reads()[offset // 4], 2)
                self.assertEqual(self.word("call_count").value, 1)
                self.assertEqual(self.word("last_handler").value, 2)

    def test_power_dispatch_truncates_two_arguments_and_preserves_pointer(
        self,
    ) -> None:
        self.reset()
        self.configure(0x04, 1)

        result = self.functions[0x04](
            0x12345678,
            0xABCDEF02,
            ctypes.c_void_p(0x76543210),
        )

        self.assertEqual(result, self.word("primary_result").value)
        self.assertEqual(self.word("argument0").value, 0x78)
        self.assertEqual(self.word("argument1").value, 0x02)
        self.assertEqual(self.pointer("argument2").value, 0x76543210)

    def test_ton_update_truncates_both_arguments(self) -> None:
        self.reset()
        self.configure(0x24, 1)

        result = self.functions[0x24](0x123456AB, 0xFEDCBA09)

        self.assertEqual(result, self.word("primary_result").value)
        self.assertEqual(self.word("argument0").value, 0xAB)
        self.assertEqual(self.word("argument1").value, 0x09)

    def test_stock_cluster_and_each_function_are_review_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        cluster = application[
            0x00480312 - APPLICATION_BASE:
            0x00480434 - APPLICATION_BASE
        ]
        self.assertEqual(len(cluster), 290)
        self.assertEqual(
            hashlib.sha256(cluster).hexdigest(),
            "876fe6a7f24b8a6245bdbcf7e65d5102"
            "f23ec18720ee8111ed17f7b667c3d673",
        )

        for name, _, start, end, _, expected_sha256, _ in SPANS:
            with self.subTest(name=name):
                stock = application[
                    start - APPLICATION_BASE:end - APPLICATION_BASE
                ]
                self.assertEqual(len(stock), end - start)
                self.assertEqual(
                    hashlib.sha256(stock).hexdigest(),
                    expected_sha256,
                )

        self.assertEqual(
            struct.unpack_from(
                "<I",
                application,
                0x004806FC - APPLICATION_BASE,
            )[0],
            0x20073270,
        )

    def test_reviewed_direct_calls_target_only_public_entries(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        entries = {start: callers for _, _, start, _, _, _, callers in SPANS}
        ends = {start: end for _, _, start, end, _, _, _ in SPANS}
        raw_calls = {start: [] for start in entries}
        wide_jumps = []
        external_interior = []

        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, kind in ((True, "BL"), (False, "B.W")):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target in entries:
                    if link:
                        raw_calls[target].append(address)
                    else:
                        wide_jumps.append((address, target))
                for start, end in ends.items():
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        external_interior.append((kind, address, target))

        # The raw sweep also decodes eight instruction-like words in the
        # non-code table at 0x0044ABF0...0x0044B050.
        noncode_candidates = {
            0x00480312: {
                0x0044ABF0,
                0x0044AEEA,
                0x0044AEFC,
                0x0044B02A,
            },
            0x0048039A: {0x0044AE84},
            0x00480408: {0x0044AC8C, 0x0044AF22},
            0x0048041E: {0x0044B050},
        }
        for start, callers in entries.items():
            with self.subTest(entry=f"0x{start:08X}"):
                observed = set(raw_calls[start])
                self.assertEqual(
                    observed,
                    set(callers) | noncode_candidates.get(start, set()),
                )
        self.assertEqual(wide_jumps, [])
        self.assertEqual(external_interior, [])

    def test_reviewed_caller_inventory_is_review_pinned(self) -> None:
        packed = bytearray()
        for _, _, start, _, _, _, callers in SPANS:
            packed.extend(struct.pack("<II", start, len(callers)))
            for caller in callers:
                packed.extend(struct.pack("<I", caller))
        self.assertEqual(len(packed), 236)
        self.assertEqual(
            hashlib.sha256(packed).hexdigest(),
            "93371d8b6bd79e2783cb7129e0b10653"
            "91ea70e6824e8c18db88cba8f8294ba7",
        )

    def test_no_aligned_stored_pointer_targets_an_entry_or_interior(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and 0x00480312 <= target < 0x00480434:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_following_initializer_boundary_is_unchanged(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        following = application[
            0x00480434 - APPLICATION_BASE:
            0x00480454 - APPLICATION_BASE
        ]
        self.assertEqual(
            following,
            bytes.fromhex(
                "70b500243c210022dff8bc522e003000bbf74efedff8b412086800f0f"
                "f002328"
            ),
        )
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "cc46c26c0a4cebcbf51fc56979c5ad8b"
            "c8c0faa9e5b5f047a31ac8b234cd2f9b",
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "352a3510c3eee25acae7fea369c260fe5"
            "c184eefd582f9d808ef56703dce2aa2",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5416d4bfe5c72c567bfee62f0bf2b774"
            "a303f40f98e6b539b8a2c07b4e9482b3",
        )


if __name__ == "__main__":
    unittest.main()
