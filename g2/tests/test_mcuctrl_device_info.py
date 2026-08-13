from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mcuctrl_device_info.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mcuctrl_device_info_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00480874
STOCK_END = 0x004809C4

REGISTER_ADDRESSES = (
    0x40020000,
    0x40020004,
    0x40020008,
    0x4002000C,
    0x40020010,
    0x40020014,
    0xE00FEFE0,
    0xE00FEFE4,
    0xE00FEFE8,
    0xE00FEFEC,
    0xE00FEFF0,
    0xE00FEFF4,
    0xE00FEFF8,
    0xE00FEFFC,
)

RAM_SIZES_KIB = (
    (128, 256, 1024),
    (128, 256, 2048),
    (256, 512, 2048),
    (256, 512, 3072),
)
MRAM_SIZES_KIB = (1024, 2048, 3072, 4096)


class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ("chip_part_number", ctypes.c_uint),
        ("chip_id0", ctypes.c_uint),
        ("chip_id1", ctypes.c_uint),
        ("chip_revision", ctypes.c_uint),
        ("vendor_id", ctypes.c_uint),
        ("sku", ctypes.c_uint),
        ("qualified", ctypes.c_uint),
        ("flash_size", ctypes.c_uint),
        ("itcm_size", ctypes.c_uint),
        ("dtcm_size", ctypes.c_uint),
        ("shared_sram_size", ctypes.c_uint),
        ("mram_size", ctypes.c_uint),
        ("jedec_part_number", ctypes.c_uint),
        ("jedec_manufacturer_id", ctypes.c_uint),
        ("jedec_chip_revision", ctypes.c_uint),
        ("jedec_coresight_id", ctypes.c_uint),
    ]


class McuctrlDeviceInfoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mcuctrl_device_info.dylib"
            if sys.platform == "darwin"
            else "mcuctrl_device_info.so"
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
        cls.reset = cls.loaded.open_cfw_test_mcuctrl_device_info_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.get_info = cls.loaded.open_cfw_mcuctrl_device_info_get
        cls.get_info.argtypes = [ctypes.POINTER(DeviceInfo)]
        cls.get_info.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_device_info_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_device_info_{name}",
        )

    def events(self) -> list[tuple[int, int, int]]:
        count = self.word("event_count").value
        return list(
            zip(
                self.words("event_kind", 64)[:count],
                self.words("event_address", 64)[:count],
                self.words("event_value", 64)[:count],
            )
        )

    def run_model(self, values: list[int]) -> DeviceInfo:
        registers = self.words("registers", 14)
        for index, value in enumerate(values):
            registers[index] = value
        result = DeviceInfo(*([0xCCCCCCCC] * 16))
        self.get_info(ctypes.byref(result))
        return result

    @staticmethod
    def observed(result: DeviceInfo) -> tuple[int, ...]:
        return tuple(
            getattr(result, field)
            for field, _ctype in DeviceInfo._fields_
        )

    @staticmethod
    def expected(values: list[int]) -> tuple[int, ...]:
        sku = values[5]
        ram = RAM_SIZES_KIB[sku & 3]
        return (
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            sku,
            1,
            0xCCCCCCCC,
            ram[0] * 1024,
            ram[1] * 1024,
            ram[2] * 1024,
            MRAM_SIZES_KIB[(sku >> 2) & 3] * 1024,
            (values[6] & 0xFF) | ((values[7] & 0x0F) << 8),
            ((values[7] >> 4) & 0x0F) | ((values[8] & 0x0F) << 4),
            (values[8] & 0xF0) | ((values[9] >> 4) & 0x0F),
            (
                ((values[13] & 0xFF) << 24)
                | ((values[12] & 0xFF) << 16)
                | ((values[11] & 0xFF) << 8)
                | (values[10] & 0xFF)
            ),
        )

    def test_all_sku_size_combinations(self) -> None:
        for sku in range(16):
            with self.subTest(sku=sku):
                self.reset()
                values = [0] * 14
                values[5] = sku
                result = self.run_model(values)
                self.assertEqual(self.observed(result), self.expected(values))

    def test_register_fields_jedec_masks_and_qualified_word(self) -> None:
        values = [
            0x12345678,
            0x89ABCDEF,
            0x0BADF00D,
            0x01020304,
            0xA5A55A5A,
            0xFFFFFFF6,
            0xAABBCCDD,
            0x11223344,
            0x55667788,
            0x99AABBCC,
            0x10203040,
            0x50607080,
            0x90A0B0C0,
            0xD0E0F001,
        ]
        result = self.run_model(values)
        self.assertEqual(self.observed(result), self.expected(values))

    def test_each_derived_size_uses_a_fresh_sku_read(self) -> None:
        sequence = self.words("sku_sequence", 8)
        sequence[:5] = (
            0xA5A50000 | 0,
            0x0000000C,
            0x00000001,
            0x00000002,
            0x00000003,
        )
        self.word("sku_count").value = 5
        result = DeviceInfo(*([0] * 16))

        self.get_info(ctypes.byref(result))

        self.assertEqual(result.sku, 0xA5A50000)
        self.assertEqual(result.mram_size, 4096 * 1024)
        self.assertEqual(result.itcm_size, 128 * 1024)
        self.assertEqual(result.dtcm_size, 512 * 1024)
        self.assertEqual(result.shared_sram_size, 3072 * 1024)
        self.assertEqual(self.word("sku_index").value, 5)

    def test_read_and_delay_event_order_is_exact(self) -> None:
        values = [index * 0x11111111 for index in range(14)]
        self.run_model(values)
        expected_reads = list(REGISTER_ADDRESSES[:6])
        expected_reads.extend([0x40020014] * 4)
        expected_reads.extend(
            (
                0xE00FEFE0,
                0xE00FEFE4,
                0xE00FEFE4,
                0xE00FEFE8,
                0xE00FEFE8,
                0xE00FEFEC,
                0xE00FEFFC,
                0xE00FEFF8,
                0xE00FEFF4,
                0xE00FEFF0,
            )
        )
        expected_events = [(1, address, values[REGISTER_ADDRESSES.index(address)])
                           for address in expected_reads[:10]]
        for address in expected_reads[10:]:
            expected_events.append(
                (1, address, values[REGISTER_ADDRESSES.index(address)])
            )
            expected_events.append((2, 0, 10))
        self.assertEqual(self.events(), expected_events)

    def test_randomized_register_model(self) -> None:
        rng = random.Random(0x480874)
        for iteration in range(400):
            with self.subTest(iteration=iteration):
                self.reset()
                values = [rng.getrandbits(32) for _ in range(14)]
                result = self.run_model(values)
                self.assertEqual(self.observed(result), self.expected(values))

    def test_stock_body_next_boundary_and_lookup_tables_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        body = application[
            STOCK_START - APPLICATION_BASE:STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(body), 336)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "fc0ab63e464dbd21244bbfe1df929801"
            "f9857a6ca6cdaa1b90e04d09f1928da5",
        )
        following = application[
            STOCK_END - APPLICATION_BASE:
            0x00480C56 - APPLICATION_BASE
        ]
        self.assertEqual(len(following), 658)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "eb3d3bb0a11febea901aa2630257bf91"
            "b9993e4b363b608e875ac34871df3624",
        )
        mram_table = application[
            0x0078C97C - APPLICATION_BASE:
            0x0078C984 - APPLICATION_BASE
        ]
        ram_table = application[
            0x00774BAC - APPLICATION_BASE:
            0x00774BC4 - APPLICATION_BASE
        ]
        self.assertEqual(
            struct.unpack("<4H", mram_table),
            MRAM_SIZES_KIB,
        )
        self.assertEqual(
            struct.unpack("<12H", ram_table),
            tuple(value for row in RAM_SIZES_KIB for value in row),
        )
        self.assertEqual(
            hashlib.sha256(mram_table).hexdigest(),
            "dd7ee6eef507a502f9e1c859b8462f273"
            "c779591a37ed189ffe88db2ca68a21e",
        )
        self.assertEqual(
            hashlib.sha256(ram_table).hexdigest(),
            "c69689bd915b0380c557fb108959845f"
            "fd678b7c195f825ae2d23ad33af03e66",
        )

    def test_stock_topology_and_delay_dependencies_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

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
                if target == STOCK_START:
                    observed.append(address)
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    external_interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target))
        self.assertEqual(calls, [0x00480E62])
        self.assertEqual(jumps, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(
            dependencies,
            [
                (address, 0x00491102)
                for address in (
                    0x00480904,
                    0x0048091C,
                    0x0048092A,
                    0x00480942,
                    0x00480952,
                    0x00480968,
                    0x00480978,
                    0x00480990,
                    0x004809A8,
                    0x004809BE,
                )
            ],
        )

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if (
                value & 1
                and STOCK_START <= target < STOCK_END
            ):
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_uses_source_owned_delay_wrapper_and_exact_tables(
        self,
    ) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_ENTRY 0x00491103U",
            source,
        )
        self.assertEqual(source.count(
            "OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);"
        ), 10)
        for token in (
            "{128U, 256U, 1024U}",
            "{128U, 256U, 2048U}",
            "{256U, 512U, 2048U}",
            "{256U, 512U, 3072U}",
            "sizeof(open_cfw_mcuctrl_device_info) == 64U",
        ):
            self.assertIn(token, source)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ffe5d5c2a3e94c15ab4a87b13a20a1aeb9ee9f8fb4223cb617da4a4636d86888",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "f9169598e70f6469b3c522a9e6331efb4e6f4e31c9d2cb6c29cf8b1f83838547",
        )


if __name__ == "__main__":
    unittest.main()
