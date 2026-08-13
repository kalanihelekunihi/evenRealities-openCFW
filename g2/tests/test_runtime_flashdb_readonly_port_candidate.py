from __future__ import annotations

import ctypes
import hashlib
import json
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "components" / "shared" / "flashdb"
    / "runtime_flashdb_readonly_port_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_flashdb_readonly_port_candidate_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_flashdb_readonly_port_upstream_oracle_host.c"
)
UPSTREAM_PARTITION = (
    ROOT / "third_party" / "flashdb" / "port" / "fal" / "src"
    / "fal_partition.c"
)
UPSTREAM_FAL_DEF = (
    ROOT / "third_party" / "flashdb" / "port" / "fal" / "inc"
    / "fal_def.h"
)
UPSTREAM_FDB_UTILS = ROOT / "third_party" / "flashdb" / "src" / "fdb_utils.c"
UPSTREAM_PROVENANCE = ROOT / "third_party" / "flashdb" / "PROVENANCE.json"
UPSTREAM_VERIFIER = ROOT / "third_party" / "flashdb" / "verify_snapshot.py"
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MANIFESTS = ROOT / "manifests"
MAKEFILE = ROOT / "Makefile"

LOAD_BASE = 0x0043_7FE0
OFFICIAL_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
UPSTREAM_PINS = {
    UPSTREAM_PARTITION: (
        14_574,
        "25b7ade441576561e5ebee1ef43c92c9e"
        "03c494e0a459588d82a1ebccc7c498c",
    ),
    UPSTREAM_FAL_DEF: (
        3_643,
        "159d4cef03eeb27becff3fa41dd7f9a30"
        "265b4efce8900429ad37ae145530099",
    ),
    UPSTREAM_FDB_UTILS: (
        11_358,
        "f3ec5d0ec094ceb16f9ad4c73b277d29"
        "029b1b3f1b8c7699ddc9ee8ce0efc9a7",
    ),
}
LOCAL_PINS = {
    SOURCE: (
        8_019,
        "b711c22c470cbf09245b8e29946a63be"
        "7d4710c96bc7409dd402c61899bf5f14",
    ),
    HEADER: (
        5_296,
        "d9e72e7e70adfef60e330abed6f49a38"
        "63896284ac003e78101b2c70123a9d19",
    ),
    CANDIDATE_FIXTURE: (
        4_360,
        "2aca0dfacf1fa0beae0167dbc22228618"
        "54aea91a0b8b2fce9fb6b717c353285",
    ),
    UPSTREAM_FIXTURE: (
        4_470,
        "62306986bfc9429c9bec2f9c8c5ea65f"
        "59be680d6b49d74e32f179a80177c1fe",
    ),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]

FUNCTION_SECTION_PINS = {
    ".text.open_cfw_flashdb_readonly_partition": (
        24,
        4,
        "4dd915f71b808c0df59c25eeaf4196d0d1fbbcd20168c6f2c3aede1f4b923247",
    ),
    ".text.open_cfw_flashdb_readonly_mutex_lock": (
        46,
        4,
        "8e94c1e6c2fb0e513a7fff3945af53e42f50957a3cea9363fa0cf4c08439e010",
    ),
    ".text.open_cfw_flashdb_readonly_mutex_unlock": (
        42,
        4,
        "d398fb4b66d76003da85b0f406326edcd9b8529ddbd35b2b3422b92a2af9f07c",
    ),
    ".text.open_cfw_flashdb_readonly_norflash_read": (
        74,
        4,
        "69af9f6f2c9d7fc6e0f7e0aac46bda6c05d7b0eadc3509813265e80ab79474d1",
    ),
    ".text.open_cfw_flashdb_readonly_partition_read_unlocked": (
        80,
        4,
        "9a4644c7add1e6fdd1807efb3299b0e45014b747a56afadba8f658509b222b8f",
    ),
    ".text.open_cfw_flashdb_readonly_partition_read": (
        128,
        4,
        "873eb7947717b8c27c19799919b30a177ddfdd225c865537596594437f0feca7",
    ),
    ".text.open_cfw_flashdb_readonly_norflash_write_denied": (
        6,
        4,
        "1e44967eee00043de390be14be761c907461733e72d3f8c76da0dacb153efcb9",
    ),
    ".text.open_cfw_flashdb_readonly_norflash_erase_denied": (
        6,
        4,
        "1e44967eee00043de390be14be761c907461733e72d3f8c76da0dacb153efcb9",
    ),
}
RODATA_SECTION_PINS = {
    ".rodata.open_cfw_flashdb_readonly_stock_norflash_abi": (
        56,
        4,
        "1b0a0e976309b33c36a3744dea94ff402c659bd9d46233547299dd914367d323",
    ),
    ".rodata.open_cfw_flashdb_readonly_partitions": (
        128,
        4,
        "e02b51d53719be34d95fa474ebda33c47981611b1f90fb6694e6b8cfafa5aa3d",
    ),
}
RELOCATION_SHA256 = (
    "2065e910c013ad5424e02807f1f9820fd93b5a9994e88fe049ec61642a9000ed"
)
APPLE_TARGET_PIN = {
    "version": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
    "object_size": 3_800,
    "object_sha256": (
        "3c05501e866c7d1defd8504bcb3f13551e8287cae3177d8e7c9e5f30d8490429"
    ),
}
LINUX_IMAGE = "opencfw-linux-llvm:22.1.8"
LINUX_IMAGE_ID = (
    "sha256:92ccf0cddac1680db0d9912cf681735b"
    "39e729d21e052965e177fa3c97faef26"
)
LINUX_CLANG = "/home/linuxbrew/.linuxbrew/bin/clang"
LINUX_TARGET_PIN = {
    "version": "Homebrew clang version 22.1.8",
    "object_size": 3_780,
    "object_sha256": (
        "4559b527367faeced0109a91924dc949fbfb73fa596f02b31417aeb8077dd85b"
    ),
}


class FalFlashDeviceAbi32(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 24),
        ("address", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("block_size", ctypes.c_uint32),
        ("init_entry", ctypes.c_uint32),
        ("read_entry", ctypes.c_uint32),
        ("write_entry", ctypes.c_uint32),
        ("erase_entry", ctypes.c_uint32),
        ("write_granularity_bits", ctypes.c_uint32),
    ]


class FalPartitionAbi32(ctypes.Structure):
    _fields_ = [
        ("magic_word", ctypes.c_uint32),
        ("name", ctypes.c_char * 24),
        ("flash_name", ctypes.c_char * 24),
        ("offset", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _c_string(table: bytes, offset: int) -> str:
    end = table.find(b"\0", offset)
    if end < 0:
        raise AssertionError("unterminated ELF string")
    return table[offset:end].decode("ascii")


def _parse_elf(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4:6] != b"\x01\x01":
        raise AssertionError("target object is not ELF32 little-endian")
    section_offset = struct.unpack_from("<I", data, 32)[0]
    section_entry_size = struct.unpack_from("<H", data, 46)[0]
    section_count = struct.unpack_from("<H", data, 48)[0]
    section_names_index = struct.unpack_from("<H", data, 50)[0]
    raw_sections = [
        struct.unpack_from(
            "<IIIIIIIIII", data, section_offset + index * section_entry_size
        )
        for index in range(section_count)
    ]
    names_header = raw_sections[section_names_index]
    names = data[names_header[4] : names_header[4] + names_header[5]]
    section_names = [
        _c_string(names, section[0]) if section[0] else ""
        for section in raw_sections
    ]
    sections = {
        name: {
            "data": data[section[4] : section[4] + section[5]],
            "alignment": section[8],
            "type": section[1],
        }
        for name, section in zip(section_names, raw_sections)
    }

    relocations: list[tuple[str, int, int, str]] = []
    undefined: list[str] = []
    for section in raw_sections:
        if section[1] == 2:  # SHT_SYMTAB
            strings_header = raw_sections[section[6]]
            strings = data[
                strings_header[4] : strings_header[4] + strings_header[5]
            ]
            for cursor in range(section[4], section[4] + section[5], section[9]):
                symbol = struct.unpack_from("<IIIBBH", data, cursor)
                if symbol[5] == 0 and symbol[0] != 0:
                    undefined.append(_c_string(strings, symbol[0]))
        if section[1] != 9:  # SHT_REL
            continue
        symbols_header = raw_sections[section[6]]
        strings_header = raw_sections[symbols_header[6]]
        strings = data[
            strings_header[4] : strings_header[4] + strings_header[5]
        ]
        target = section_names[section[7]]
        for cursor in range(section[4], section[4] + section[5], section[9]):
            offset, info = struct.unpack_from("<II", data, cursor)
            symbol_index = info >> 8
            relocation_type = info & 0xFF
            symbol = struct.unpack_from(
                "<IIIBBH",
                data,
                symbols_header[4] + symbol_index * symbols_header[9],
            )
            symbol_name = (
                _c_string(strings, symbol[0])
                if symbol[0]
                else section_names[symbol[5]]
            )
            relocations.append((target, offset, relocation_type, symbol_name))
    return {
        "data": data,
        "sections": sections,
        "relocations": relocations,
        "undefined": sorted(undefined),
    }


def _normalized_relocations(
    records: list[tuple[str, int, int, str]],
) -> bytes:
    return "\n".join(
        f"{section}|{offset}|{kind}|{symbol}"
        for section, offset, kind, symbol in records
    ).encode("ascii")


class RuntimeFlashDbReadonlyPortCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        cls.candidate_library = temp / f"candidate{suffix}"
        cls.oracle_library = temp / f"oracle{suffix}"
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        link = ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run(
            [
                clang,
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                *link,
                str(CANDIDATE_FIXTURE),
                "-o",
                str(cls.candidate_library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                clang,
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-Wno-unused-function",
                *link,
                str(UPSTREAM_FIXTURE),
                "-I",
                str(ROOT / "third_party" / "flashdb" / "port" / "fal" / "inc"),
                "-o",
                str(cls.oracle_library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.candidate = ctypes.CDLL(str(cls.candidate_library))
        cls.oracle = ctypes.CDLL(str(cls.oracle_library))
        pointer = ctypes.POINTER(ctypes.c_uint8)
        cls.candidate.open_cfw_test_flashdb_reset.argtypes = [
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_uint32,
        ]
        cls.candidate.open_cfw_test_flashdb_read.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            pointer,
            ctypes.c_uint32,
        ]
        cls.candidate.open_cfw_test_flashdb_read.restype = ctypes.c_int32
        cls.candidate.open_cfw_test_flashdb_write.argtypes = [
            ctypes.c_uint32,
            pointer,
            ctypes.c_uint32,
        ]
        cls.candidate.open_cfw_test_flashdb_write.restype = ctypes.c_int32
        cls.candidate.open_cfw_test_flashdb_erase.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.candidate.open_cfw_test_flashdb_erase.restype = ctypes.c_int32
        cls.candidate.open_cfw_test_flashdb_counter.argtypes = [ctypes.c_uint32]
        cls.candidate.open_cfw_test_flashdb_counter.restype = ctypes.c_uint32
        cls.candidate.open_cfw_test_flashdb_mutex_matches.restype = ctypes.c_uint32
        cls.oracle.open_cfw_test_flashdb_oracle_reset.argtypes = [ctypes.c_int32]
        cls.oracle.open_cfw_test_flashdb_oracle_partition_read.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            pointer,
            ctypes.c_uint32,
        ]
        cls.oracle.open_cfw_test_flashdb_oracle_partition_read.restype = ctypes.c_int32
        cls.oracle.open_cfw_test_flashdb_oracle_counter.argtypes = [ctypes.c_uint32]
        cls.oracle.open_cfw_test_flashdb_oracle_counter.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _candidate_read(
        self,
        partition: int,
        address: int,
        size: int,
        status: int = 0,
        acquire: int = 0,
        release: int = 0,
        mutex_present: int = 1,
    ) -> tuple[int, bytes]:
        buffer = (ctypes.c_uint8 * max(size, 1))()
        self.candidate.open_cfw_test_flashdb_reset(
            status, acquire, release, mutex_present
        )
        result = self.candidate.open_cfw_test_flashdb_read(
            partition, address, buffer, size
        )
        return result, bytes(buffer[:size])

    def _oracle_read(
        self,
        partition: int,
        address: int,
        size: int,
        status: int = 0,
    ) -> tuple[int, bytes]:
        buffer = (ctypes.c_uint8 * max(size, 1))()
        self.oracle.open_cfw_test_flashdb_oracle_reset(status)
        result = self.oracle.open_cfw_test_flashdb_oracle_partition_read(
            partition, address, buffer, size
        )
        return result, bytes(buffer[:size])

    def test_authenticated_upstream_source_and_provenance(self) -> None:
        for path, (size, digest) in UPSTREAM_PINS.items():
            with self.subTest(path=path.name):
                data = path.read_bytes()
                self.assertEqual(len(data), size)
                self.assertEqual(_sha(data), digest)
        provenance = json.loads(UPSTREAM_PROVENANCE.read_text())
        self.assertEqual(provenance["upstream"]["selected_tag"], "2.1.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            "714d6159e7e6afb267a3953756abca445c350e61",
        )
        self.assertEqual(provenance["license"], "Apache-2.0")
        result = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("verification passed", result.stdout)

    def test_local_candidate_boundary_is_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.name):
                data = path.read_bytes()
                self.assertEqual(len(data), size)
                self.assertEqual(_sha(data), digest)

    def test_recovered_records_match_the_authenticated_image(self) -> None:
        image = OFFICIAL.read_bytes()
        self.assertEqual(_sha(image), OFFICIAL_SHA256)
        device = FalFlashDeviceAbi32.in_dll(
            self.candidate, "open_cfw_flashdb_readonly_stock_norflash_abi"
        )
        partitions_type = FalPartitionAbi32 * 2
        partitions = partitions_type.in_dll(
            self.candidate, "open_cfw_flashdb_readonly_partitions"
        )
        self.assertEqual(bytes(device), image[0x0072_2B30 - LOAD_BASE : 0x0072_2B68 - LOAD_BASE])
        self.assertEqual(
            bytes(partitions),
            image[0x006D_5358 - LOAD_BASE : 0x006D_53D8 - LOAD_BASE],
        )
        self.assertEqual(ctypes.sizeof(FalFlashDeviceAbi32), 0x38)
        self.assertEqual(ctypes.sizeof(FalPartitionAbi32), 0x40)
        self.assertEqual(FalFlashDeviceAbi32.read_entry.offset, 0x28)
        self.assertEqual(FalFlashDeviceAbi32.write_entry.offset, 0x2C)
        self.assertEqual(FalFlashDeviceAbi32.erase_entry.offset, 0x30)
        self.assertEqual(FalPartitionAbi32.offset.offset, 0x34)
        self.assertEqual(FalPartitionAbi32.length.offset, 0x38)

    def test_host_differential_matches_upstream_partition_read(self) -> None:
        rng = random.Random(0xF1A5_2DB)
        lengths = (0x38000, 0x8000)
        cases = [
            (0, 0, 1),
            (0, 0x37FF0, 16),
            (1, 0, 17),
            (1, 0x7FFF, 1),
            (0, 0x38000, 1),
            (1, 0x8000, 1),
        ]
        for partition, length in enumerate(lengths):
            for _ in range(48):
                size = rng.randrange(1, 97)
                address = rng.randrange(0, length + 65)
                cases.append((partition, address, size))
        for status in (0, -7, 1, 3):
            for partition, address, size in cases:
                with self.subTest(
                    status=status,
                    partition=partition,
                    address=address,
                    size=size,
                ):
                    candidate = self._candidate_read(
                        partition, address, size, status=status
                    )
                    oracle = self._oracle_read(
                        partition, address, size, status=status
                    )
                    self.assertEqual(candidate, oracle)

    def test_partition_offsets_short_like_returns_and_overflow_fail_closed(self) -> None:
        result, output = self._candidate_read(0, 0x123, 11)
        self.assertEqual(result, 11)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(3), 0x01FC0123)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(4), 11)
        self.assertEqual(output, bytes(((0x01FC0123 + i) ^ 0xA5) & 0xFF for i in range(11)))
        result, _ = self._candidate_read(1, 0x40, 8)
        self.assertEqual(result, 8)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(3), 0x01FF8040)

        # Any nonzero MX25 status is an incomplete/error transfer, even when
        # it resembles a positive short byte count. FlashDB requires < 0.
        result, _ = self._candidate_read(0, 0, 8, status=7)
        self.assertEqual(result, -1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(0), 1)
        result, _ = self._candidate_read(0, 0xFFFF_FFF0, 0x40)
        self.assertEqual(result, -1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(0), 0)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(1), 0)

    def test_shared_cmsis_mutex_boundary_and_error_release(self) -> None:
        result, _ = self._candidate_read(0, 0, 4)
        self.assertEqual(result, 4)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(1), 1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(2), 1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(5), 0xFFFF_FFFF)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_mutex_matches(), 1)

        result, _ = self._candidate_read(0, 0, 4, acquire=-3)
        self.assertEqual(result, -1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(0), 0)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(2), 0)
        result, _ = self._candidate_read(0, 0, 4, status=-2)
        self.assertEqual(result, -1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(2), 1)
        result, _ = self._candidate_read(0, 0, 4, release=-4)
        self.assertEqual(result, -1)
        result, _ = self._candidate_read(0, 0, 4, mutex_present=0)
        self.assertEqual(result, -1)
        self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(0), 0)

    def test_write_and_erase_are_unconditionally_denied(self) -> None:
        buffer = (ctypes.c_uint8 * 4)(1, 2, 3, 4)
        self.candidate.open_cfw_test_flashdb_reset(0, 0, 0, 1)
        self.assertEqual(
            self.candidate.open_cfw_test_flashdb_write(0x01FC0000, buffer, 4),
            -1,
        )
        self.assertEqual(
            self.candidate.open_cfw_test_flashdb_erase(0x01FC0000, 0x1000),
            -1,
        )
        for index in range(3):
            self.assertEqual(self.candidate.open_cfw_test_flashdb_counter(index), 0)

        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            *TARGET_FLAGS,
            "-DOPEN_CFW_FLASHDB_ENABLE_MUTATION=1",
            "-c",
            str(SOURCE),
            "-o",
            str(Path(self.temporary.name) / "forbidden.o"),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no mutation-capable build mode", result.stderr)

    def _check_target_object(self, path: Path, pin: dict[str, object]) -> None:
        parsed = _parse_elf(path)
        data = parsed["data"]
        self.assertEqual(len(data), pin["object_size"])
        self.assertEqual(_sha(data), pin["object_sha256"])
        sections = parsed["sections"]
        for section_name, (size, alignment, digest) in {
            **FUNCTION_SECTION_PINS,
            **RODATA_SECTION_PINS,
        }.items():
            with self.subTest(section=section_name):
                section = sections[section_name]
                self.assertEqual(len(section["data"]), size)
                self.assertEqual(section["alignment"], alignment)
                self.assertEqual(_sha(section["data"]), digest)
        relocations = parsed["relocations"]
        self.assertEqual(
            _sha(_normalized_relocations(relocations)),
            RELOCATION_SHA256,
        )
        self.assertEqual(parsed["undefined"], [])
        for mutation_name in (
            ".text.open_cfw_flashdb_readonly_norflash_write_denied",
            ".text.open_cfw_flashdb_readonly_norflash_erase_denied",
        ):
            code_relocations = [
                record for record in relocations if record[0] == mutation_name
            ]
            self.assertEqual(code_relocations, [])
            self.assertEqual(sections[mutation_name]["data"].hex(), "4ff0ff307047")

    def test_apple_target_sections_and_relocations_are_pinned(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        if version != APPLE_TARGET_PIN["version"]:
            self.skipTest(f"Apple compiler profile unavailable: {version}")
        output = Path(self.temporary.name) / "candidate-apple.o"
        subprocess.run(
            [clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
            check=True,
            capture_output=True,
            text=True,
        )
        self._check_target_object(output, APPLE_TARGET_PIN)

    def test_linux_target_sections_and_relocations_are_pinned(self) -> None:
        docker = os.environ.get("OPENCFW_DOCKER", "docker")
        if shutil.which(docker) is None:
            self.skipTest("Docker is unavailable")
        inspect = subprocess.run(
            [docker, "image", "inspect", LINUX_IMAGE, "--format", "{{.Id}}"],
            capture_output=True,
            text=True,
        )
        if inspect.returncode != 0:
            self.skipTest("pinned Linux compiler image is unavailable")
        self.assertEqual(inspect.stdout.strip(), LINUX_IMAGE_ID)
        output_dir = Path(self.temporary.name) / "linux-output"
        output_dir.mkdir()
        source_mount = str(ROOT.parent)
        command = [
            docker,
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "-v",
            f"{source_mount}:{source_mount}:ro",
            "-v",
            f"{output_dir}:/output",
            "-w",
            source_mount,
            LINUX_IMAGE,
            LINUX_CLANG,
            *TARGET_FLAGS,
            "-c",
            str(SOURCE),
            "-o",
            "/output/candidate-linux.o",
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        version = subprocess.run(
            [
                docker,
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                LINUX_IMAGE,
                LINUX_CLANG,
                "--version",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        self.assertEqual(version, LINUX_TARGET_PIN["version"])
        self._check_target_object(
            output_dir / "candidate-linux.o", LINUX_TARGET_PIN
        )

    def test_candidate_is_production_excluded_and_has_no_mount_policy(self) -> None:
        registrations = [OVERLAY, MAKEFILE, *sorted(MANIFESTS.glob("*.json"))]
        for path in registrations:
            text = path.read_text()
            self.assertNotIn(SOURCE.name, text, path)
            self.assertNotIn(HEADER.name, text, path)
        source = SOURCE.read_text()
        for forbidden in (
            "fdb_kvdb_init(",
            "fdb_kv_set_default(",
            "fal_partition_write(",
            "fal_partition_erase(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
