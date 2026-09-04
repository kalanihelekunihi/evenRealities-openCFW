from __future__ import annotations

import copy
import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "freertos"
    / "runtime_freertos_suspend_all.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_suspend_all_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_FREERTOS = (
    ROOT / "third_party" / "freertos-kernel" / "include" / "FreeRTOS.h"
)
UPSTREAM_PORT = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portmacrocommon.h"
)
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)

SOURCE_SIZE = 2258
SOURCE_SHA256 = (
    "792ffc64fab54de686dd36cbb0ea1bf80"
    "40a92ac8a105cfeda2d7b45e6986bcf"
)
HEADER_SIZE = 1619
HEADER_SHA256 = (
    "bf42ac5b89d64a76889c4fe9f75def51"
    "934af2f9fcc51776df495571e4d6ed77"
)
HOST_FIXTURE_SIZE = 4705
HOST_FIXTURE_SHA256 = (
    "292ef9bfd663a9085d3c41a872c1956b"
    "5b165ea8e2639872c787751992d01ed3"
)

BASE = 0x00438000
START = 0x00454D7C
END = 0x00454D88
STOCK_BYTES = "dff8e8060168491c01607047"
STOCK_SHA256 = (
    "3651c872be8fd55503df57fb49f5d0b7"
    "b94b0e784237141389a4b965b8edb6e2"
)
SUSPENDED_LITERAL = 0x00455468
SUSPENDED_WORD = 0x20074A58
SUSPENDED_LITERALS = [0x00455468, 0x00455644, 0x00456068]
SUSPENDED_REFERENCES = [
    0x00454B2E,
    0x00454B56,
    0x00454D7C,
    0x00454DD2,
    0x00455006,
    0x00455050,
    0x004551B6,
    0x004552C2,
    0x004553AE,
    0x0045547E,
    0x004558B2,
    0x00455EA8,
]

RESUME_START = 0x00454DCC
RESUME_END = 0x00454EFE
RESUME_SHA256 = (
    "548e05e1f8a2f498372dd1f4eb7c6536"
    "e093dbbfdb82fbe8f9b54231cedc8a09"
)
RESUME_DECREMENT_START = 0x00454DEA
RESUME_DECREMENT_END = 0x00454DF4
RESUME_DECREMENT_BYTES = "edf771f93068401e3060"

CALLERS = [
    (0x00441890, "13f074fa"),
    (0x00441B9A, "13f0eff8"),
    (0x00441CC6, "13f059f8"),
    (0x00454B6E, "00f005f9"),
    (0x00454F46, "fff719ff"),
    (0x00455622, "fff7abfb"),
    (0x00455778, "fff700fb"),
    (0x00456118, "fef730fe"),
    (0x0045625E, "fef78dfd"),
    (0x0047E892, "d6f773fa"),
    (0x0047EC6A, "d6f787f8"),
    (0x0047EDB0, "d5f7e4ff"),
    (0x0057E1F2, "d6f6c3fd"),
]
CALLER_ADDRESS_SHA256 = (
    "950b6ce1df6baf8575d53aba4036bdab"
    "a836597e31970710984083494511b7de"
)
CALLER_RECORD_SHA256 = (
    "020f8997cabb5201c1bf55b4d8f56ab"
    "96bab1cb44cc526f01ffad71d82370254"
)
RESUME_CALLERS = [
    (0x004418D8, "13f078fa"),
    (0x00441936, "13f049fa"),
    (0x0044194A, "13f03ffa"),
    (0x00441B76, "13f029f9"),
    (0x00441BEC, "13f0eef8"),
    (0x00441C32, "13f0cbf8"),
    (0x00441CA2, "13f093f8"),
    (0x00441D2E, "13f04df8"),
    (0x00441D78, "13f028f8"),
    (0x00454B7A, "00f027f9"),
    (0x00454FCE, "fff7fdfe"),
    (0x00455600, "fff7e4fb"),
    (0x00455786, "fff721fb"),
    (0x004561E8, "fef7f0fd"),
    (0x0045627A, "fef7a7fd"),
    (0x0047E8AC, "d6f78efa"),
    (0x0047E8DE, "d6f775fa"),
    (0x0047E8EC, "d6f76efa"),
    (0x0047ECBE, "d6f785f8"),
    (0x0047EE14, "d5f7daff"),
    (0x0057E216, "d6f6d9fd"),
]
RESUME_CALLER_ADDRESS_SHA256 = (
    "0376e19f832cae16a06c7f82772d8447"
    "c7b0ba259829731b5f2d9fd459bbcbbf"
)
RESUME_CALLER_RECORD_SHA256 = (
    "b6a64bf2fc5277484f9ec220ae171f77"
    "a520adb1bcf03c9b57f56360a9a769f2"
)

CALLER_SPANS = {
    (0x004417EE, 0x00441952): (
        356,
        "d8a463345ca0e7754eb0808ebf3a725a"
        "3ca66541b6e85220b6d5459166aac11d",
    ),
    (0x00441B0A, 0x00441C44): (
        314,
        "f96de373691fb5d916ccbe25e0bc1d34"
        "74b918c16968b540b601fe6e36575560",
    ),
    (0x00441C44, 0x00441DA6): (
        354,
        "4d112cee107085a6606d4704c6f9edb4"
        "83264086cc9f954991ac76818c08b34c",
    ),
    (0x00454B4C, 0x00454B88): (
        60,
        "86f7d3b317ec02d559374d2bdb113698"
        "889a1291d8d4369f255d2c6874015738",
    ),
    (0x00454F38, 0x00454FD8): (
        160,
        "2f3e621b8fa875589d416ce45a79227f"
        "6bbb9b3f2aedfe5187ae8d3feae2d6de",
    ),
    (0x004555F0, 0x00455642): (
        82,
        "c89de77c94db7c1ee04f59ea89ae3bf9"
        "7d0f533cf868dbc6faffbff7857c497b",
    ),
    (0x00455728, 0x004557A8): (
        128,
        "53d97f8c2e506f69df7908f9b3d2c644"
        "fd4f21b456f5961311f1ce34d975f626",
    ),
    (0x00456110, 0x00456210): (
        256,
        "8d86a7daf341ad836729e4abdd25b66b4"
        "5f97a56d6d1077c07bf0c5718f8dc57",
    ),
    (0x00456210, 0x00456280): (
        112,
        "d754aec282080b2deafeb6756cbacc156"
        "af70a311499ee4d73eeb7497f12b032",
    ),
    (0x0047E88C, 0x0047E8F2): (
        102,
        "1a91d5140d4c19e02b094cf31c6b9477"
        "7c036771accc734d7a3c2fcae1c4a5c9",
    ),
    (0x0047EBF8, 0x0047ED10): (
        280,
        "03d202c1154dc2084d02ce51526300623"
        "f3d75ffa263abf331276bfa950bbc79",
    ),
    (0x0047ED76, 0x0047EE1E): (
        168,
        "38b05fcf35bc59fd639e8a540e0e211d"
        "5d2a7026d1ad5fce97cd27f573084133",
    ),
    (0x0057E136, 0x0057E220): (
        234,
        "c22d5821764704899a68d46b9b1bf3d"
        "bc79294dcd354c6377467fa051add4b82",
    ),
}

FUNCTION = "open_cfw_freertos_task_suspend_all"
TARGET_BYTES = "44f65820c2f207000168013101607047"
TARGET_SHA256 = (
    "0928ce291a4a96b18baf7304bc7f87fb"
    "828ac06902619f1f42500e04c73883be"
)
APPLE_OFFSET = 115_408
LINUX_OFFSET = 117_240
APPLE_RUNTIME_ADDRESS = 0x007B_05F4
LINUX_RUNTIME_ADDRESS = 0x007B_0D1C
APPLE_REPLACEMENT = "5bf33abc" + "00bf" * 4
APPLE_REPLACEMENT_SHA256 = (
    "ed883582c9d9aad0dcd8d43b167ba8cb"
    "c66702afc5b34db59d126afd75d61b0e"
)
LINUX_REPLACEMENT = "5bf3cebf" + "00bf" * 4
LINUX_REPLACEMENT_SHA256 = (
    "854d8a4af83e289595b6e1964ff060ef"
    "88772b8f07ad52d8f6c8cc8a90b1f4e0"
)
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

EVENT_SOFTWARE_BARRIER = 1
EVENT_DEPTH_READ = 2
EVENT_DEPTH_WRITE = 3
EVENT_MEMORY_BARRIER = 4

_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang")
    == "apple-clang",
    "production byte-exact build uses the reviewed Apple-clang profile",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSSuspendAllTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / library_name("runtime_freertos_suspend_all")
        host_command = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(HOST_FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))

        cls.reset = cls.loaded.open_cfw_test_suspend_all_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.invoke = cls.loaded.open_cfw_test_suspend_all_invoke
        cls.invoke.argtypes = []
        cls.invoke.restype = None
        cls.depth_get = cls.loaded.open_cfw_test_suspend_all_depth_get
        cls.depth_get.argtypes = []
        cls.depth_get.restype = ctypes.c_uint32
        cls.event_count = cls.loaded.open_cfw_test_suspend_all_event_count
        cls.event_count.argtypes = []
        cls.event_count.restype = ctypes.c_uint32
        cls.event_kind = cls.loaded.open_cfw_test_suspend_all_event_kind
        cls.event_kind.argtypes = [ctypes.c_uint32]
        cls.event_kind.restype = ctypes.c_uint32
        cls.event_value = cls.loaded.open_cfw_test_suspend_all_event_value
        cls.event_value.argtypes = [ctypes.c_uint32]
        cls.event_value.restype = ctypes.c_uint32
        cls.depth_read_count = (
            cls.loaded.open_cfw_test_suspend_all_depth_read_count
        )
        cls.depth_read_count.argtypes = []
        cls.depth_read_count.restype = ctypes.c_uint32
        cls.depth_write_count = (
            cls.loaded.open_cfw_test_suspend_all_depth_write_count
        )
        cls.depth_write_count.argtypes = []
        cls.depth_write_count.restype = ctypes.c_uint32
        cls.software_barrier_count = (
            cls.loaded.open_cfw_test_suspend_all_software_barrier_count
        )
        cls.software_barrier_count.argtypes = []
        cls.software_barrier_count.restype = ctypes.c_uint32
        cls.memory_barrier_count = (
            cls.loaded.open_cfw_test_suspend_all_memory_barrier_count
        )
        cls.memory_barrier_count.argtypes = []
        cls.memory_barrier_count.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_suspend_all.o"
        subprocess.run(
            [
                clang,
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.config = json.loads(
            OVERLAY_CONFIG.read_text(encoding="utf-8")
        )
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

        cls.production = None
        if (
            os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang"
        ) == "apple-clang":
            build_config = copy.deepcopy(cls.config)
            build_config["expected"] = build_config["core_stage_expected"]
            for profile in build_config.get("toolchain_profiles", {}).values():
                if "core_stage_expected" in profile:
                    profile["expected"] = profile["core_stage_expected"]
            unpinned_config = temporary / "overlay-unpinned-final.json"
            unpinned_config.write_text(
                json.dumps(build_config, indent=2) + "\n",
                encoding="utf-8",
            )
            cls.production = apollo_overlay.build(
                root=ROOT,
                config_path=unpinned_config,
                output_dir=temporary / "production",
                clang=clang,
                toolchain_profile="apple-clang",
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def test_authenticated_upstream_and_local_source_are_pinned(self) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        self.assertIn(
            """void vTaskSuspendAll( void )
{
    /* A critical section is not required as the variable is of type
     * BaseType_t.""",
            upstream,
        )
        self.assertIn(
            """portSOFTWARE_BARRIER();

    /* The scheduler is suspended if uxSchedulerSuspended is non-zero.""",
            upstream,
        )
        self.assertIn("++uxSchedulerSuspended;", upstream)
        self.assertIn("portMEMORY_BARRIER();", upstream)
        self.assertIn(
            "static volatile UBaseType_t uxSchedulerSuspended",
            upstream,
        )
        self.assertIn(
            "typedef unsigned long    UBaseType_t;",
            UPSTREAM_PORT.read_text(encoding="utf-8"),
        )
        freertos_header = UPSTREAM_FREERTOS.read_text(encoding="utf-8")
        self.assertIn("#define portMEMORY_BARRIER()", freertos_header)
        self.assertIn("#define portSOFTWARE_BARRIER()", freertos_header)

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(HOST_FIXTURE.stat().st_size, HOST_FIXTURE_SIZE)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vTaskSuspendAll()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00454D7C, 0x00454D88)",
            "OPEN_CFW_FREERTOS_SUSPEND_ALL_SOFTWARE_BARRIER()",
            "OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_READ()",
            "OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_WRITE(suspended_depth)",
            "OPEN_CFW_FREERTOS_SUSPEND_ALL_MEMORY_BARRIER()",
        ):
            self.assertIn(token, source)
        for token in (
            "0x20074A58U",
            "__UINT32_TYPE__",
            "sizeof(open_cfw_freertos_suspend_all_ubase_type) == 4U",
            '__asm__ __volatile__("" ::: "memory")',
        ):
            self.assertIn(token, header)

    def test_host_observes_barriers_one_read_write_and_unsigned_wrap(
        self,
    ) -> None:
        for initial in (
            0,
            1,
            0x7FFFFFFF,
            0x80000000,
            0xFFFFFFFE,
            0xFFFFFFFF,
        ):
            expected = (initial + 1) & 0xFFFFFFFF
            with self.subTest(initial=initial):
                self.reset(initial)
                self.invoke()

                self.assertEqual(self.depth_get(), expected)
                self.assertEqual(self.depth_read_count(), 1)
                self.assertEqual(self.depth_write_count(), 1)
                self.assertEqual(self.software_barrier_count(), 1)
                self.assertEqual(self.memory_barrier_count(), 1)
                self.assertEqual(self.event_count(), 4)
                self.assertEqual(
                    [self.event_kind(index) for index in range(4)],
                    [
                        EVENT_SOFTWARE_BARRIER,
                        EVENT_DEPTH_READ,
                        EVENT_DEPTH_WRITE,
                        EVENT_MEMORY_BARRIER,
                    ],
                )
                self.assertEqual(
                    [self.event_value(index) for index in range(4)],
                    [initial, initial, expected, expected],
                )

    def test_official_body_global_and_resume_coupling_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        body = self.span(START, END)
        self.assertEqual(len(body), 12)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

        first, second = struct.unpack_from("<HH", body)
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second & 0x0FFF, 0x6E8)
        self.assertEqual(
            ((START + 4) & ~3) + (second & 0x0FFF),
            SUSPENDED_LITERAL,
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(SUSPENDED_LITERAL, SUSPENDED_LITERAL + 4),
            )[0],
            SUSPENDED_WORD,
        )
        self.assertEqual(body[4:].hex(), "0168491c01607047")

        resume = self.span(RESUME_START, RESUME_END)
        self.assertEqual(len(resume), 306)
        self.assertEqual(hashlib.sha256(resume).hexdigest(), RESUME_SHA256)
        self.assertEqual(
            self.span(
                RESUME_DECREMENT_START,
                RESUME_DECREMENT_END,
            ).hex(),
            RESUME_DECREMENT_BYTES,
        )
        resume_first, resume_second = struct.unpack(
            "<HH",
            self.span(0x00454DD2, 0x00454DD6),
        )
        self.assertEqual(resume_first, 0xF8DF)
        self.assertEqual(
            ((0x00454DD2 + 4) & ~3) + (resume_second & 0x0FFF),
            SUSPENDED_LITERAL,
        )

        raw_literals = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value == SUSPENDED_WORD:
                raw_literals.append(BASE + offset)
        self.assertEqual(raw_literals, SUSPENDED_LITERALS)
        self.assertEqual(self.suspended_literal_references(), SUSPENDED_REFERENCES)

    def test_official_topology_and_all_caller_contexts_are_closed(
        self,
    ) -> None:
        calls = {START: [], RESUME_START: []}
        jumps = {START: [], RESUME_START: []}
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            first, second = struct.unpack("<HH", encoded)
            if first & 0xF800 != 0xF000 or second & 0x8000 == 0:
                continue
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target in observed:
                    observed[target].append((address, encoded.hex()))
                for start, end in (
                    (START, END),
                    (RESUME_START, RESUME_END),
                ):
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior.append(
                            (address, target, link, encoded.hex())
                        )

        self.assertEqual(calls[START], CALLERS)
        self.assertEqual(jumps[START], [])
        self.assertEqual(calls[RESUME_START], RESUME_CALLERS)
        self.assertEqual(jumps[RESUME_START], [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in CALLERS
                )
            ).hexdigest(),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in CALLERS
                )
            ).hexdigest(),
            CALLER_RECORD_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in RESUME_CALLERS
                )
            ).hexdigest(),
            RESUME_CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in RESUME_CALLERS
                )
            ).hexdigest(),
            RESUME_CALLER_RECORD_SHA256,
        )

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        for (start, end), (size, digest) in CALLER_SPANS.items():
            caller = self.span(start, end)
            self.assertEqual(len(caller), size)
            self.assertEqual(hashlib.sha256(caller).hexdigest(), digest)

    def test_target_object_is_one_relocation_free_16_byte_leaf(self) -> None:
        data, sections = self.apollo_overlay.parse_elf32(
            self.target_object
        )
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        function = next(
            symbol for symbol in symbols if symbol["name"] == FUNCTION
        )
        function_section = sections[int(function["section_index"])]
        self.assertEqual(
            function_section["name"],
            f".text.{FUNCTION}",
        )
        self.assertEqual(int(function_section["flags"]), 0x6)
        self.assertEqual(int(function_section["alignment"]), 4)
        self.assertEqual(
            (int(function["value"]), int(function["size"])),
            (1, 16),
        )
        self.assertEqual(int(function["type"]), 2)
        leaf = data[
            int(function_section["offset"]):
            int(function_section["offset"]) + int(function_section["size"])
        ]
        self.assertEqual(leaf.hex(), TARGET_BYTES)
        self.assertEqual(hashlib.sha256(leaf).hexdigest(), TARGET_SHA256)
        self.assertEqual(
            {
                symbol["name"]
                for symbol in symbols
                if (
                    symbol["name"]
                    and int(symbol["type"]) == 2
                    and int(symbol["section_index"]) != 0
                )
            },
            {FUNCTION},
        )
        self.assertEqual(
            {
                symbol["name"]
                for symbol in symbols
                if (
                    symbol["name"]
                    and int(symbol["section_index"]) == 0
                )
            },
            set(),
        )
        self.assertEqual(
            [
                section["name"]
                for section in sections
                if (
                    int(section["type"]) == 9
                    and int(section["info"])
                    == int(function_section["index"])
                    and int(section["size"]) != 0
                )
            ],
            [],
        )
        writable = []
        for section in sections:
            flags = int(section["flags"])
            if (
                flags & 0x3 == 0x3
                and int(section["size"]) != 0
            ):
                writable.append(section["name"])
        self.assertEqual(writable, [])

    def test_dual_profile_configuration_and_redirect_are_exact(self) -> None:
        leaf = next(
            leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] == FUNCTION
        )
        self.assertNotIn("profiles", leaf)
        self.assertEqual(
            {
                key: leaf["source"][key]
                for key in (
                    "path",
                    "size",
                    "sha256",
                    "license",
                    "upstream_commit",
                    "evidence",
                )
            },
            {
                "path": (
                    "components/shared/freertos/"
                    "runtime_freertos_suspend_all.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "upstream_commit": (
                    "def7d2df2b0506d3d249334974f51e427c17a41c"
                ),
                "evidence": (
                    "docs/research/"
                    "freertos-suspend-all-source-boundary-audit.md"
                ),
            },
        )
        expected = {
            "size": 16,
            "sha256": TARGET_SHA256,
            "alignment": 4,
            "offset": APPLE_OFFSET,
            "unrelocated_sha256": TARGET_SHA256,
        }
        self.assertEqual(leaf["expected"], expected)
        self.assertEqual(leaf["relocations"], [])
        self.assertEqual(
            leaf["toolchain_profiles"]["linux-clang"],
            {
                "reviewed_version_prefix": (
                    "Homebrew clang version 22.1.8"
                ),
                "expected": {**expected, "offset": LINUX_OFFSET},
                "relocations": [],
            },
        )
        expected_functions = {
            FUNCTION,
            "open_cfw_freertos_task_internal_set_timeout_state",
        }
        self.assertEqual(
            [
                item["function"]
                for item in self.config["relocated_leaves"]
                if item["function"] in expected_functions
            ],
            [
                FUNCTION,
                "open_cfw_freertos_task_internal_set_timeout_state",
            ],
        )

        patch = next(
            patch
            for patch in self.config["patch_sites"]
            if patch["target_function"] == FUNCTION
        )
        self.assertEqual(
            patch,
            {
                "name": "replace_freertos_task_suspend_all",
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )
        for target, replacement_hex, replacement_sha256 in (
            (
                APPLE_RUNTIME_ADDRESS,
                APPLE_REPLACEMENT,
                APPLE_REPLACEMENT_SHA256,
            ),
            (
                LINUX_RUNTIME_ADDRESS,
                LINUX_REPLACEMENT,
                LINUX_REPLACEMENT_SHA256,
            ),
        ):
            replacement = (
                self.apollo_overlay.encode_thumb_branch(
                    START,
                    target,
                    link=False,
                )
                + b"\x00\xbf" * 4
            )
            self.assertEqual(replacement.hex(), replacement_hex)
            self.assertEqual(
                hashlib.sha256(replacement).hexdigest(),
                replacement_sha256,
            )

    @_APPLE_ONLY
    def test_production_placement_redirect_aggregate_and_manifest_are_exact(
        self,
    ) -> None:
        self.assertIsNotNone(self.production)
        report_leaf = next(
            leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(
            report_leaf["placement"],
            {
                "alignment": 4,
                "offset": APPLE_OFFSET,
                "padding_before": 0,
                "runtime_address": APPLE_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B05F4",
                "size": 16,
            },
        )
        self.assertEqual(report_leaf["extraction"]["sha256"], TARGET_SHA256)
        self.assertEqual(report_leaf["extraction"]["relocation_count"], 0)

        overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        self.assertEqual(
            overlay[APPLE_OFFSET:APPLE_OFFSET + 16].hex(),
            TARGET_BYTES,
        )
        patch = next(
            patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["target_function"] == FUNCTION
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["payload_offset"], 118_172)
        self.assertEqual(patch["target_address"], APPLE_RUNTIME_ADDRESS)
        self.assertEqual(replacement.hex(), APPLE_REPLACEMENT)
        self.assertEqual(
            hashlib.sha256(replacement).hexdigest(),
            APPLE_REPLACEMENT_SHA256,
        )
        self.assertEqual(
            (
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
                len(self.production["overlay"]["functions"]),
                len(self.production["overlay"]["patched_sites"]),
            ),
            (
                380_444,
                (
                    "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622"
                ),
                2_563,
                2_448,
            ),
        )
        component = self.production["component"]
        self.assertEqual(
            {
                key: component[key]
                for key in (
                    "size",
                    "sha256",
                    "generated_patch_site_bytes",
                    "replaced_stock_function_bytes",
                    "source_owned_bytes",
                    "source_owned_in_place_bytes",
                    "opaque_base_bytes",
                )
            },
            {
                "size": 3_903_840,
                "sha256": (
                    "2fe63dbce04257b3961fa80702e62fe4e5ee9859df5908b9245377f272c60752"
                ),
                "generated_patch_site_bytes": 422_476,
                "replaced_stock_function_bytes": 422_658,
                "source_owned_bytes": 382_878,
                "source_owned_in_place_bytes": 186,
                "opaque_base_bytes": 3_098_454,
            },
        )

        manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["package"],
            {
                "output_name": (
                    "g2-openCFW-s200_v2.2.6.10-core-source."
                    "evenota.bin"
                ),
                "expected_size": 4_750_780,
                "expected_sha256": (
                    "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771"
                ),
                "profiles": {
                    "linux-clang": {
                        "expected_size": 4_750_764,
                        "expected_sha256": (
                            "50f2ee3722aeaa720eed1a7c65381b02ac3ec0ceabecf9eb57d661d8e060a6d0"
                        ),
                    },
                },
            },
        )
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        selected_names = {
            "freertos_task_start_scheduler_source_replacement",
            "freertos_task_suspend_all_source_replacement",
            "opaque_between_freertos_task_suspend_all_and_resume_all",
            "apollo_freertos_task_suspend_all_source_leaf",
        }
        selected = {
            region["name"]: (
                region["file_offset"],
                region["size"],
                region["target_address"],
                region["address_status"],
            )
            for region in regions
            if region["name"] in selected_names
        }
        self.assertEqual(
            selected,
            {
                "freertos_task_start_scheduler_source_replacement": (
                    118_028,
                    144,
                    0x0045_4CEC,
                    "generated_source_entry_replacement",
                ),
                "freertos_task_suspend_all_source_replacement": (
                    118_172,
                    12,
                    START,
                    "generated_source_entry_replacement",
                ),
                "opaque_between_freertos_task_suspend_all_and_resume_all": (
                    118_184,
                    68,
                    END,
                    "official_blob",
                ),
                "apollo_freertos_task_suspend_all_source_leaf": (
                    3_638_804,
                    16,
                    APPLE_RUNTIME_ADDRESS,
                    "source_compiled",
                ),
            },
        )

    def suspended_literal_references(self) -> list[int]:
        references = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from(
                "<HH",
                self.application,
                offset,
            )
            candidates = []
            if first & 0xF800 == 0x4800:
                candidates.append(
                    ((address + 4) & ~3) + (first & 0x00FF) * 4
                )
            if first == 0xF8DF:
                candidates.append(
                    ((address + 4) & ~3) + (second & 0x0FFF)
                )
            if first == 0xF85F:
                candidates.append(
                    ((address + 4) & ~3) - (second & 0x0FFF)
                )
            for target in candidates:
                if not BASE <= target <= BASE + len(self.application) - 4:
                    continue
                if struct.unpack_from(
                    "<I",
                    self.application,
                    target - BASE,
                )[0] == SUSPENDED_WORD:
                    references.append(address)
        return references

    @staticmethod
    def narrow_branch_targets(
        address: int,
        halfword: int,
    ) -> list[int]:
        if halfword & 0xF800 == 0xE000:
            immediate = halfword & 0x07FF
            if immediate & 0x0400:
                immediate -= 0x0800
            return [address + 4 + immediate * 2]
        if (
            halfword & 0xF000 == 0xD000
            and ((halfword >> 8) & 0x0F) < 0x0E
        ):
            immediate = halfword & 0x00FF
            if immediate & 0x0080:
                immediate -= 0x0100
            return [address + 4 + immediate * 2]
        if halfword & 0xF500 == 0xB100:
            immediate = (
                ((halfword >> 9) & 1) << 6
                | ((halfword >> 3) & 0x1F) << 1
            )
            return [address + 4 + immediate]
        return []


if __name__ == "__main__":
    unittest.main()
