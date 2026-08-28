from __future__ import annotations

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
LINUX_EXACT_ROOT = Path("/Users/kalani/Repo/SybilSightABCD/openCFW")
LINUX_EXACT_CLANG = Path("/home/linuxbrew/.linuxbrew/bin/clang")
FREERTOS = ROOT / "components" / "shared" / "freertos"
FIXTURES = ROOT / "tests" / "fixtures"
RESET_SOURCE = FREERTOS / "runtime_freertos_queue_generic_reset.c"
RESET_HEADER = RESET_SOURCE.with_suffix(".h")
RESET_CANDIDATE_FIXTURE = (
    FIXTURES / "runtime_freertos_queue_generic_reset_candidate_host.c"
)
RESET_ORACLE_FIXTURE = (
    FIXTURES / "runtime_freertos_queue_generic_reset_upstream_oracle_host.c"
)
UNORDERED_SOURCE = (
    FREERTOS
    / "runtime_freertos_task_remove_from_unordered_event_list.c"
)
UNORDERED_HEADER = UNORDERED_SOURCE.with_suffix(".h")
UNORDERED_CANDIDATE_FIXTURE = (
    FIXTURES
    / "runtime_freertos_task_remove_from_unordered_event_list_candidate_host.c"
)
UNORDERED_ORACLE_FIXTURE = (
    FIXTURES
    / "runtime_freertos_task_remove_from_unordered_event_list_upstream_oracle_host.c"
)
SHARED_ORACLE_FIXTURE = (
    FIXTURES / "runtime_freertos_task_increment_tick_upstream_oracle_host.c"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_LIST = ROOT / "third_party" / "freertos-kernel" / "list.c"
UPSTREAM_VERIFIER = ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
UPSTREAM_PROVENANCE = (
    ROOT / "third_party" / "freertos-kernel" / "PROVENANCE.json"
)
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
FREERTOS_PORT = (
    ROOT / "third_party" / "freertos-kernel" / "portable" / "IAR"
    / "ARM_CM55_NTZ" / "non_secure"
)
FREERTOS_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "candidates"
    / "cmsis_freertos_constructors"
)
ORACLE_CONFIG = FREERTOS_CONFIG / "FreeRTOSConfig.h"
ORACLE_PORT_ADAPTER = FREERTOS_CONFIG / "portmacro.h"
ORACLE_STRING_ADAPTER = FREERTOS_CONFIG / "string.h"
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

# Filled only after the files above are final.  These are provenance gates,
# not production-overlay pins.
FILE_PINS = {
    RESET_SOURCE: (
        4_002,
        "223758f605ee22220e5a534db4675545cc43a1f1fc5f24051c3c7c3cc92d556c",
    ),
    RESET_HEADER: (
        9_551,
        "eb47ede13109bfcc7ce0434bfcb14e4d3be7627e05b4348a399cc964e8038bb5",
    ),
    RESET_CANDIDATE_FIXTURE: (
        10_823,
        "04851ae9628e65d36b4f070a0be98ac671d2b55aa32adfe0ca5416a590e5af65",
    ),
    RESET_ORACLE_FIXTURE: (
        4_610,
        "84f20593a74bdd4650d64a2e1e8a3b39542a3b489d1a686aae1b8890dd72037a",
    ),
    UNORDERED_SOURCE: (
        4_452,
        "3656a2e24d63a2dd92743fde085be59ff4c830afb357535b38dbd4a4dc39f77c",
    ),
    UNORDERED_HEADER: (
        9_425,
        "4b21346b0c0ec7a60e0752b0c6c38bbf1eab576e07eb52d9f11b42a7b96e91d1",
    ),
    UNORDERED_CANDIDATE_FIXTURE: (
        13_110,
        "57ca256adc82b8a07f882cfc1ea7c62a46bb9598bbcbc6170342085618eb7e20",
    ),
    UNORDERED_ORACLE_FIXTURE: (
        4_951,
        "8b1bdb2144acebce47e0daa82bdd305b52ba4ab3bb0a22623eeca2f91c9ca199",
    ),
}

UPSTREAM_PINS = {
    UPSTREAM_QUEUE: (
        125_614,
        "5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894",
    ),
    UPSTREAM_TASKS: (
        223_695,
        "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463",
    ),
    UPSTREAM_LIST: (
        10_338,
        "db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4",
    ),
}

# These transitive host-oracle inputs are outside the authenticated upstream
# snapshot.  Pinning them prevents an unrelated recovered-configuration or
# adapter edit from silently changing the reference behavior.
ORACLE_BOUNDARY_PINS = {
    SHARED_ORACLE_FIXTURE: (
        16_051,
        "432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf",
    ),
    ORACLE_CONFIG: (
        5_184,
        "537e12cd879b06d7748f9b0e177f6ad0e17cd176405945771580e6d9c8312889",
    ),
    ORACLE_PORT_ADAPTER: (
        910,
        "6e1ac1013191a6bd3e4924656a03a1515a1d5f06df83b8fbb9073a489961e675",
    ),
    ORACLE_STRING_ADAPTER: (
        513,
        "1612795defaff20b3a0ad57b0106a1906a973d94557b2ac7c35d8d5307771f1d",
    ),
}

PROVENANCE_GATE_PINS = {
    UPSTREAM_VERIFIER: (
        19_109,
        "a140aca673c0516e2dd2d948bd9cdb673445729b7593c5e79a0f70e50dd04b1b",
    ),
    UPSTREAM_PROVENANCE: (
        13_785,
        "810d28df622a96646dd70d56311355c3531393fcf0fac1feac585f9cd799f99a",
    ),
}

BASE = 0x0043_8000
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
)
STOCK = {
    "reset": (
        0x0044_1516,
        0x0044_15CA,
        "e5b7c5e487374e7966b8f2febb8aa1b804efa516c92f9e436a369ec5df100ad8",
    ),
    "unordered": (
        0x0045_547C,
        0x0045_5556,
        "aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b",
    ),
}
CALLERS = {
    "reset": [(0x0044_16AE, "fff732ff")],
    "unordered": [(0x0047_EE02, "d6f73bfb")],
}
CALLER_ADDRESS_SHA256 = {
    "reset": "08afd3a5c3d78375eb18903997a05d47149dc307e6f99419c57f5cceb542ad84",
    "unordered": "3294692df13736bddb4a8f78d24f0d8845c4af17630e3851e461cee721294dc0",
}
CALLER_RECORD_SHA256 = {
    "reset": "d1757b72e2dab8e691c80387ce2efea7f86315e2c28387edbf919d6908d4b332",
    "unordered": "1f50b74aa3b56987fd3161abb610dccb67d1dd72b7cea450d43fe62042629808",
}
OUTGOING = {
    "reset": [
        (0x0044_1522, 0x005F_A0A4),
        (0x0044_154A, 0x0044_20D0),
        (0x0044_158E, 0x0045_5370),
        (0x0044_1596, 0x0044_20BC),
        (0x0044_15A0, 0x0045_607C),
        (0x0044_15A8, 0x0045_607C),
        (0x0044_15AC, 0x0044_20E8),
        (0x0044_15B8, 0x005F_A0A4),
    ],
    "unordered": [
        (0x0045_5486, 0x005F_A0A4),
        (0x0045_54A0, 0x005F_A0A4),
        (0x0045_54D0, 0x0045_5876),
    ],
}
RAW_POINTER_HITS = {
    "reset": [],
    "unordered": [
        (0x0055_0F7F, 0x0045_5520),
        (0x0055_1AA3, 0x0045_5500),
        (0x0055_28AF, 0x0045_5520),
        (0x0073_FCB2, 0x0045_554E),
        (0x0074_0416, 0x0045_554E),
        (0x0078_0B55, 0x0045_5554),
        (0x0078_4769, 0x0045_5554),
        (0x0078_48BD, 0x0045_5554),
        (0x0078_744B, 0x0045_5554),
        (0x0078_9D6B, 0x0045_5554),
        (0x0078_CA2D, 0x0045_5552),
    ],
}
RAW_POINTER_SHA256 = {
    "reset": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "unordered": "1e53cb6a968ed5792d96b4a5088072522ffad1ccdf5adb0bde2cace3ded5ccc4",
}
CALLER_SPANS = {
    "reset": (
        0x0044_1696,
        0x0044_16B8,
        "a95e0e593a7afb1fbc642b83c9bc54ab0dc6d994ad4e109bf14dc914d3c2add7",
    ),
    "unordered": (
        0x0047_ED76,
        0x0047_EE1E,
        "38b05fcf35bc59fd639e8a540e0e211d5d2a7026d1ad5fce97cd27f573084133",
    ),
}
RAM_LITERALS = {
    0x0045_5644: 0x2007_4A58,
    0x0045_5C40: 0x2007_4A38,
    0x0045_5DBC: 0x2006_A49C,
    0x0045_5C34: 0x2007_4A20,
    0x0045_5C44: 0x2007_4A44,
}
RETAINED_SOURCE_PROVIDERS = {
    0x005F_A0A4: ("replace_freertos_ul_set_interrupt_mask", "ulSetInterruptMask"),
    0x0044_20BC: ("replace_freertos_port_yield", "open_cfw_freertos_port_yield"),
    0x0044_20D0: (
        "replace_freertos_port_enter_critical",
        "open_cfw_freertos_port_enter_critical",
    ),
    0x0044_20E8: (
        "replace_freertos_port_exit_critical",
        "open_cfw_freertos_port_exit_critical",
    ),
    0x0045_5370: (
        "replace_freertos_task_remove_from_event_list",
        "open_cfw_freertos_task_remove_from_event_list",
    ),
    0x0045_5876: (
        "replace_freertos_task_reset_next_task_unblock_time",
        "open_cfw_freertos_task_reset_next_task_unblock_time",
    ),
    0x0045_607C: (
        "replace_freertos_list_initialise",
        "open_cfw_freertos_list_initialise",
    ),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
APPLE_TARGETS = {
    "reset": {
        "function": "open_cfw_freertos_queue_generic_reset",
        "size": 172,
        "alignment": 4,
        "sha256": "689da8cc4cd4757e609cdf77b3675ff7330fb46ea9b1efc29f4d96772f066baa",
        "object_size": 1_064,
        "object_sha256": (
            "c1132e92072ee465c713c9b9c219a27d2577e3b785593843939ece0f6117fc6d"
        ),
        "hex": (
            "70b580b1c26b1ab1036ca2fb0323a3b14af2a500c0f25f0080474ff0ff300021"
            "016000bffee74af2a500c0f25f0080474ff0ff3000210160fee742f2bd04c0f2"
            "440404f1140205460e4690472868ea6b2b6c294603fb0205013a8d60002502fb"
            "03028d634860ff20ca6081f8440081f8450001f110006eb146f27d05c0f24505"
            "0e46a84706f12400a84704f12c008047012070bd01680029f7d045f27131c0f2"
            "450188470028f0d0a047eee7"
        ),
    },
    "unordered": {
        "function": (
            "open_cfw_freertos_task_remove_from_unordered_event_list"
        ),
        "size": 214,
        "alignment": 4,
        "sha256": "c4a89f560a07598f3af72a4ca0e3a6bda1f23bd86e6f777ecea690f6db67ecdd",
        "object_size": 1_144,
        "object_sha256": (
            "d2cb4e4f7fc199bce1259be94a03bde381cfe6652a6314a54d235f0f548a6b23"
        ),
        "hex": (
            "2de9f04144f63828c2f20708d8f82020002a4bd0c56841f00041002d016050d0"
            "0169436882684c689a608442536008bf4a600022026108680138086045f67700c0"
            "f2450080476969ab684c68ea68281d84429a60536008bf4a600a684af29c4301"
            "3a0a60e96ad8f80020c2f20603914284bfc8f80010e96a01eb810203eb820466"
            "686c61b768ae60ef607860b06053f82200013043f8220058f8180cc06a814284"
            "bf0120c8f80c00bde8f0814af2a500c0f25f0080474ff0ff300021016000bffe"
            "e74af2a500c0f25f0080474ff0ff3000210160fee7"
        ),
    },
}
LINUX_TARGETS = {
    "reset": {
        "function": "open_cfw_freertos_queue_generic_reset",
        "size": 174,
        "alignment": 4,
        "sha256": "18f27b60f944abbc4a8c703e4aa6e4fba0bac243a4010ea32474e9f8d9fe31ff",
        "object_size": 1_048,
        "object_sha256": (
            "c5adf0faa71999de6d020bf8c9653dd4ec50da56104bc4f297e5bd6086bb568e"
        ),
        "hex": (
            "f0b581b078b1c26b1ab1036ca2fb03239bb14af2a500c0f25f0080474ff0ff30"
            "00210160fee74af2a500c0f25f0080474ff0ff3000210160fee742f2bd07c0f2"
            "440707f1140205460e4690472868d5e90f23294603fb0205013a002402fb0302"
            "8c63c1e90105ff20ca6081f8440081f8450001f1100076b146f27d04c0f24504"
            "0d46a04705f12400a04707f12c008047012001b0f0bd01680029f6d045f27131"
            "c0f2450188470028efd0b847ede7"
        ),
    },
    "unordered": {
        "function": (
            "open_cfw_freertos_task_remove_from_unordered_event_list"
        ),
        "size": 210,
        "alignment": 4,
        "sha256": "b2e29e859cae0b43dadddf1dad7f44f9740ae5b6ed93a3febf3a28a7128331e4",
        "object_size": 1_120,
        "object_sha256": (
            "67ef01829118d020bafaee3d1c0f600645fd6c19ea831d77c29f9c180c254028"
        ),
        "hex": (
            "f0b581b044f63827c2f207073a6a002a4bd0c56841f00041002d01604fd00169"
            "d0e901324c689a608442536008bf4a600022026108680138086045f67700c0f2"
            "450080476969d5e902324c6805f1040c9a606445536008bf4a600a684af29c43"
            "013a0a60e96a3a68c2f20603914284bf3960e96a01eb810203eb820460686c61"
            "8668c5e90206c6f804c0c0f808c053f82200013043f8220057f8180cc06a8142"
            "84bf0120f86001b0f0bd4af2a500c0f25f0080474ff0ff3000210160fee74af2"
            "a500c0f25f0080474ff0ff3000210160fee7"
        ),
    },
}
TARGETS_BY_PROFILE = {
    "apple-clang": APPLE_TARGETS,
    "linux-clang": LINUX_TARGETS,
}
NO_WAITER = 0xFFFF_FFFF
ASSERTED = ctypes.c_int32(0x8000_0000).value
SENTINEL = 0xFFFF_FFFE
NULL_ID = 0xFFFF_FFFF


def sha256(path: Path | bytes) -> str:
    data = path.read_bytes() if isinstance(path, Path) else path
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def thumb_wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ (((second >> 13) & 1) ^ sign)
    i2 = 1 ^ (((second >> 11) & 1) ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    return ()


def thumb_wide_conditional_branch_target(
    address: int, first: int, second: int
) -> int | None:
    """Decode Thumb-2 B<c>.W (T3), excluding reserved AL/NV conditions."""
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    condition = (first >> 6) & 0x0F
    if condition >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20) | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18) | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


class FreeRTOSAgentAExactSourceCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.compiler_version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout
        if cls.compiler_version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif cls.compiler_version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
            if Path(cls.clang) != LINUX_EXACT_CLANG:
                raise AssertionError(
                    "Linux candidate pins require explicit compiler "
                    f"{LINUX_EXACT_CLANG}, got {cls.clang}"
                )
            if ROOT != LINUX_EXACT_ROOT:
                raise AssertionError(
                    "Linux candidate pins require exact source root "
                    f"{LINUX_EXACT_ROOT}, got {ROOT}"
                )
        else:
            raise AssertionError(
                f"unreviewed candidate compiler: {cls.compiler_version!r}"
            )
        requested_profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        if requested_profile is not None and requested_profile != cls.profile:
            raise AssertionError(
                "OPENCFW_TOOLCHAIN_PROFILE/compiler mismatch: "
                f"{requested_profile!r} != {cls.profile!r}"
            )

        cls.reset_candidate = cls.compile_host(
            temporary / library_name("queue_reset_candidate"),
            RESET_CANDIDATE_FIXTURE,
            [],
        )
        cls.reset_oracle = cls.compile_host(
            temporary / library_name("queue_reset_oracle"),
            RESET_ORACLE_FIXTURE,
            cls.oracle_includes(),
        )
        cls.unordered_candidate = cls.compile_host(
            temporary / library_name("unordered_candidate"),
            UNORDERED_CANDIDATE_FIXTURE,
            [],
        )
        cls.unordered_oracle = cls.compile_host(
            temporary / library_name("unordered_oracle"),
            UNORDERED_ORACLE_FIXTURE,
            cls.oracle_includes(),
        )
        cls.bind_reset(cls.reset_candidate, "open_cfw_queue_reset_host_", True)
        cls.bind_reset(cls.reset_oracle, "open_cfw_oracle_queue_reset_", False)
        cls.bind_unordered(
            cls.unordered_candidate, "open_cfw_unordered_host_", True
        )
        cls.bind_unordered(
            cls.unordered_oracle, "open_cfw_oracle_unordered_", False
        )

        cls.target_objects = {}
        for name, source in (
            ("reset", RESET_SOURCE), ("unordered", UNORDERED_SOURCE)
        ):
            outputs = [
                temporary / f"{name}-candidate-1.o",
                temporary / f"{name}-candidate-2.o",
            ]
            for output in outputs:
                subprocess.run(
                    [cls.clang, *TARGET_FLAGS, "-c", str(source), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
            cls.target_objects[name] = outputs

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def oracle_includes(cls) -> list[str]:
        return [
            "-ffreestanding", "-fno-builtin", "-I", str(FREERTOS_CONFIG),
            "-I", str(FREERTOS_INCLUDE), "-I", str(FREERTOS_PORT),
        ]

    @classmethod
    def compile_host(cls, output: Path, source: Path, extra: list[str]):
        command = [
            cls.clang, "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra",
            "-Werror", *extra, str(source),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_reset(library, prefix: str, candidate: bool) -> None:
        reset = getattr(library, prefix + "reset")
        reset.argtypes = [ctypes.c_uint32] * 6
        execute = getattr(library, prefix + "execute")
        execute.argtypes = [ctypes.c_int32]
        execute.restype = ctypes.c_int32
        for name in ("receive_lock", "transmit_lock"):
            getattr(library, prefix + "get_" + name).restype = ctypes.c_int32
        for name in (
            "tail", "write", "read", "messages", "send_count", "receive_count"
        ):
            getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32
        if candidate:
            getattr(library, prefix + "execute_null").restype = ctypes.c_int32
            for name in (
                "event_count", "remove_calls", "yield_calls", "enter_calls",
                "exit_calls", "list_init_calls", "assert_calls",
            ):
                getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32
            event = getattr(library, prefix + "get_event")
            event.argtypes = [ctypes.c_uint32]
            event.restype = ctypes.c_uint32

    @staticmethod
    def bind_unordered(library, prefix: str, candidate: bool) -> None:
        getattr(library, prefix + "reset").argtypes = [ctypes.c_uint32] * 6
        getattr(library, prefix + "set_indexes").argtypes = [ctypes.c_uint32] * 3
        execute = getattr(library, prefix + "execute")
        execute.argtypes = [ctypes.c_uint32]
        execute.restype = ctypes.c_int32
        for name in (
            "event_value", "event_count", "blocked_count", "ready_count",
            "event_index", "blocked_index", "ready_index", "ready_head",
            "ready_tail", "state_container", "event_container", "top",
            "yield", "next",
        ):
            getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32
        if candidate:
            ownerless = getattr(library, prefix + "execute_ownerless")
            ownerless.argtypes = [ctypes.c_uint32]
            ownerless.restype = ctypes.c_int32
            for name in (
                "reset_calls", "reset_before_state_remove", "trace_calls",
                "assert_calls",
            ):
                getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32

    @staticmethod
    def snapshot(library, prefix: str, names: tuple[str, ...]) -> dict[str, int]:
        return {
            name: int(getattr(library, prefix + "get_" + name)())
            for name in names
        }

    def test_queue_reset_matches_pristine_upstream(self) -> None:
        names = (
            "tail", "write", "read", "messages", "receive_lock",
            "transmit_lock", "send_count", "receive_count",
        )
        scenarios = [
            # current, waiter, length, item size, messages, receive seed, new
            (3, NO_WAITER, 4, 3, 2, 1, 1),
            (3, NO_WAITER, 4, 3, 2, 1, -7),
            (3, NO_WAITER, 4, 3, 2, 1, 0),
            (4, 2, 5, 2, 4, 1, 0),
            (4, 4, 5, 2, 4, 0, 0),
            (2, 5, 5, 2, 4, 0, 0),
            (0, NO_WAITER, 1, 0, 1, 0, 1),
        ]
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                for library, prefix in (
                    (self.reset_candidate, "open_cfw_queue_reset_host_"),
                    (self.reset_oracle, "open_cfw_oracle_queue_reset_"),
                ):
                    getattr(library, prefix + "reset")(*scenario[:-1])
                candidate_result = self.reset_candidate.open_cfw_queue_reset_host_execute(
                    scenario[-1]
                )
                oracle_result = self.reset_oracle.open_cfw_oracle_queue_reset_execute(
                    scenario[-1]
                )
                self.assertEqual(candidate_result, oracle_result)
                self.assertEqual(candidate_result, 1)
                self.assertEqual(
                    self.snapshot(
                        self.reset_candidate, "open_cfw_queue_reset_host_", names
                    ),
                    self.snapshot(
                        self.reset_oracle, "open_cfw_oracle_queue_reset_", names
                    ),
                )
                event_count = (
                    self.reset_candidate.open_cfw_queue_reset_host_get_event_count()
                )
                events = [
                    self.reset_candidate.open_cfw_queue_reset_host_get_event(i)
                    for i in range(event_count)
                ]
                if scenario[-1] != 0:
                    self.assertEqual(events, [2, 5, 5, 6])
                elif scenario[1] == NO_WAITER:
                    self.assertEqual(events, [2, 6])
                elif scenario[1] > scenario[0]:
                    self.assertEqual(events, [2, 3, 4, 6])
                else:
                    self.assertEqual(events, [2, 3, 6])

    def test_queue_reset_assert_and_overflow_edges_are_fail_closed(self) -> None:
        reset = self.reset_candidate.open_cfw_queue_reset_host_reset
        execute = self.reset_candidate.open_cfw_queue_reset_host_execute
        for length, item_size in ((0, 1), (0x8000_0000, 2), (3, 0x8000_0000)):
            with self.subTest(length=length, item_size=item_size):
                reset(1, NO_WAITER, length, item_size, 7, 1)
                self.assertEqual(execute(0), ASSERTED)
                self.assertEqual(
                    self.reset_candidate.open_cfw_queue_reset_host_get_assert_calls(),
                    1,
                )
                self.assertEqual(
                    self.reset_candidate.open_cfw_queue_reset_host_get_enter_calls(),
                    0,
                )
        reset(1, NO_WAITER, 3, 2, 7, 1)
        self.assertEqual(
            self.reset_candidate.open_cfw_queue_reset_host_execute_null(),
            ASSERTED,
        )
        self.assertEqual(
            self.reset_candidate.open_cfw_queue_reset_host_get_assert_calls(), 1
        )

    def test_unordered_remove_matches_pristine_upstream_graph(self) -> None:
        names = (
            "event_value", "event_count", "blocked_count", "ready_count",
            "event_index", "blocked_index", "ready_index", "ready_head",
            "ready_tail", "state_container", "event_container", "top",
            "yield", "next",
        )
        scenarios = [
            # current, waiter, top, wake, seed, event/state/ready indexes, value
            (2, 5, 2, 100, 0, (0, 0, 0), 0),
            (5, 5, 5, 0, 0, (1, 1, 0), 0x7FFF_FFFF),
            (6, 2, 4, 0xFFFF_FFFE, 0, (1, 0, 0), 0x8000_0000),
            (2, 4, 4, 77, 1, (0, 1, 0), 0x1234_5678),
            (2, 4, 3, 77, 1, (1, 1, 1), 0xFFFF_FFFF),
        ]
        for current, waiter, top, wake, seed, indexes, value in scenarios:
            with self.subTest(
                current=current, waiter=waiter, top=top, wake=wake,
                seed=seed, indexes=indexes, value=value,
            ):
                for library, prefix in (
                    (self.unordered_candidate, "open_cfw_unordered_host_"),
                    (self.unordered_oracle, "open_cfw_oracle_unordered_"),
                ):
                    getattr(library, prefix + "reset")(
                        1, current, waiter, top, wake, seed
                    )
                    getattr(library, prefix + "set_indexes")(*indexes)
                self.assertEqual(
                    self.unordered_candidate.open_cfw_unordered_host_execute(value),
                    self.unordered_oracle.open_cfw_oracle_unordered_execute(value),
                )
                self.assertEqual(
                    self.snapshot(
                        self.unordered_candidate, "open_cfw_unordered_host_", names
                    ),
                    self.snapshot(
                        self.unordered_oracle, "open_cfw_oracle_unordered_", names
                    ),
                )
                self.assertEqual(
                    self.unordered_candidate.open_cfw_unordered_host_get_event_value(),
                    value | 0x8000_0000,
                )
                self.assertEqual(
                    self.unordered_candidate.open_cfw_unordered_host_get_reset_calls(),
                    1,
                )
                self.assertEqual(
                    self.unordered_candidate
                        .open_cfw_unordered_host_get_reset_before_state_remove(),
                    1,
                )
                self.assertEqual(
                    self.unordered_candidate.open_cfw_unordered_host_get_trace_calls(),
                    1,
                )

    def test_unordered_assert_paths_stop_before_invalid_graph_use(self) -> None:
        reset = self.unordered_candidate.open_cfw_unordered_host_reset
        reset(0, 2, 4, 2, 100, 0)
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_execute(7), ASSERTED
        )
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_get_assert_calls(), 1
        )
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_get_event_value(), 17
        )

        reset(1, 2, 4, 2, 100, 0)
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_execute_ownerless(7),
            ASSERTED,
        )
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_get_assert_calls(), 1
        )
        self.assertEqual(
            self.unordered_candidate.open_cfw_unordered_host_get_event_value(),
            0x8000_0007,
        )

    def test_upstream_and_candidate_provenance_are_pinned(self) -> None:
        for path, (size, digest) in FILE_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        for path, (size, digest) in UPSTREAM_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        for path, (size, digest) in ORACLE_BOUNDARY_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        for path, (size, digest) in PROVENANCE_GATE_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        provenance = json.loads(
            (ROOT / "third_party" / "freertos-kernel" / "PROVENANCE.json")
                .read_text()
        )
        upstream = provenance["upstream"]
        self.assertEqual(upstream["selected_tag"], "V10.5.1")
        self.assertEqual(
            upstream["selected_commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "7496dfa815c3cea2f45a090c6e92d113f494b930",
        )
        queue_source = UPSTREAM_QUEUE.read_text()
        tasks_source = UPSTREAM_TASKS.read_text()
        for token in (
            "BaseType_t xQueueGenericReset( QueueHandle_t xQueue,",
            "pxQueue->u.xQueue.pcTail = pxQueue->pcHead",
            "xTaskRemoveFromEventList( &( pxQueue->xTasksWaitingToSend ) )",
            "vListInitialise( &( pxQueue->xTasksWaitingToReceive ) );",
        ):
            self.assertIn(token, queue_source)
        for token in (
            "void vTaskRemoveFromUnorderedEventList(",
            "xItemValue | taskEVENT_LIST_ITEM_VALUE_IN_USE",
            "prvResetNextTaskUnblockTime();",
            "prvAddTaskToReadyList( pxUnblockedTCB );",
            "xYieldPending = pdTRUE;",
        ):
            self.assertIn(token, tasks_source)

    def test_production_registration_is_complete_and_exact(self) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text())
        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text())
        functions = set(overlay["functions"])
        production_functions = {
            "open_cfw_freertos_queue_generic_reset",
            "open_cfw_freertos_task_remove_from_unordered_event_list",
        }
        self.assertEqual(
            sum(name in production_functions for name in overlay["functions"]),
            2,
        )
        self.assertEqual(
            sum(
                item["function"] in production_functions
                for item in overlay["relocated_leaves"]
            ),
            2,
        )
        leaves = {
            item["function"]: item for item in overlay["relocated_leaves"]
        }
        production_patches = {
            "replace_freertos_queue_generic_reset",
            "replace_freertos_task_remove_from_unordered_event_list",
        }
        self.assertEqual(
            sum(
                item["name"] in production_patches
                for item in overlay["patch_sites"]
            ),
            2,
        )
        patches = {item["name"]: item for item in overlay["patch_sites"]}
        expected = {
            "reset": (
                "open_cfw_freertos_queue_generic_reset",
                "replace_freertos_queue_generic_reset",
                RESET_SOURCE,
            ),
            "unordered": (
                "open_cfw_freertos_task_remove_from_unordered_event_list",
                "replace_freertos_task_remove_from_unordered_event_list",
                UNORDERED_SOURCE,
            ),
        }
        for name, (function, patch_name, source) in expected.items():
            with self.subTest(name=name):
                self.assertIn(function, functions)
                self.assertEqual(
                    leaves[function]["source"]["path"],
                    source.relative_to(ROOT).as_posix(),
                )
                self.assertEqual(leaves[function]["relocations"], [])
                self.assertTrue(leaves[function]["strict_relocation_contract"])
                self.assertEqual(
                    patches[patch_name]["target_function"], function
                )
                self.assertEqual(patches[patch_name]["branch"], "b_w")

        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        production_regions = {
            "freertos_queue_generic_reset_source_replacement",
            "freertos_task_remove_from_unordered_event_list_source_replacement",
        }
        self.assertEqual(
            sum(item["name"] in production_regions for item in regions), 2
        )
        by_name = {item["name"]: item for item in regions}
        self.assertEqual(
            (
                by_name["freertos_queue_generic_reset_source_replacement"]
                ["file_offset"],
                by_name["freertos_queue_generic_reset_source_replacement"]
                ["size"],
                by_name["freertos_queue_generic_reset_source_replacement"]
                ["target_address"],
            ),
            (38_198, 180, STOCK["reset"][0]),
        )
        self.assertEqual(
            (
                by_name[
                    "freertos_task_remove_from_unordered_event_list_"
                    "source_replacement"
                ]["file_offset"],
                by_name[
                    "freertos_task_remove_from_unordered_event_list_"
                    "source_replacement"
                ]["size"],
                by_name[
                    "freertos_task_remove_from_unordered_event_list_"
                    "source_replacement"
                ]["target_address"],
            ),
            (119_964, 218, STOCK["unordered"][0]),
        )

    def test_retained_callable_dependencies_are_source_owned(self) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text())
        functions = set(overlay["functions"])
        patches_by_address: dict[int, list[dict[str, object]]] = {}
        for patch in overlay["patch_sites"]:
            patches_by_address.setdefault(int(patch["runtime_address"]), []).append(
                patch
            )

        self.assertEqual(
            set(RETAINED_SOURCE_PROVIDERS),
            {
                target
                for calls in OUTGOING.values()
                for _site, target in calls
            },
        )
        for address, (name, target_function) in RETAINED_SOURCE_PROVIDERS.items():
            with self.subTest(address=hex(address), provider=target_function):
                self.assertEqual(len(patches_by_address.get(address, [])), 1)
                patch = patches_by_address[address][0]
                self.assertEqual(patch["name"], name)
                self.assertEqual(patch["target_function"], target_function)
                self.assertIn(target_function, functions)
                self.assertIn(patch["branch"], ("b_w", "copy"))

    def test_official_bodies_and_complete_reference_topology_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        for name, (start, end, digest) in STOCK.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(len(body), end - start)
            self.assertEqual(sha256(body), digest)
            observed_callers = []
            entry_jumps = []
            outgoing = []
            external_interior = []
            narrow_entry = []
            wide_conditional_entry = []
            for offset in range(0, len(self.application) - 3, 2):
                address = BASE + offset
                first, second = struct.unpack_from("<HH", self.application, offset)
                encoded = self.application[offset:offset + 4]
                for link in (True, False):
                    target = thumb_wide_branch_target(
                        address, first, second, link=link
                    )
                    if target is None:
                        continue
                    if target == start:
                        (observed_callers if link else entry_jumps).append(
                            (address, encoded.hex())
                        )
                    if start <= address < end and link:
                        outgoing.append((address, target))
                    if start < target < end and not start <= address < end:
                        external_interior.append((address, target, link))
                for target in narrow_branch_targets(address, first):
                    if target == start:
                        narrow_entry.append((address, target))
                    if start < target < end and not start <= address < end:
                        external_interior.append((address, target, False))
                conditional_target = thumb_wide_conditional_branch_target(
                    address, first, second
                )
                if conditional_target == start:
                    wide_conditional_entry.append(
                        (address, conditional_target)
                    )
                if (
                    conditional_target is not None
                    and start < conditional_target < end
                    and not start <= address < end
                ):
                    external_interior.append(
                        (address, conditional_target, False)
                    )
            self.assertEqual(observed_callers, CALLERS[name])
            self.assertEqual(entry_jumps, [])
            self.assertEqual(narrow_entry, [])
            self.assertEqual(wide_conditional_entry, [])
            self.assertEqual(external_interior, [])
            self.assertEqual(outgoing, OUTGOING[name])
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in observed_callers
                )).hexdigest(),
                CALLER_ADDRESS_SHA256[name],
            )
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in observed_callers
                )).hexdigest(),
                CALLER_RECORD_SHA256[name],
            )
            raw_hits = []
            for offset in range(0, len(self.application) - 3):
                value = struct.unpack_from("<I", self.application, offset)[0]
                if start <= (value & ~1) < end:
                    raw_hits.append((BASE + offset, value))
            self.assertEqual(raw_hits, RAW_POINTER_HITS[name])
            self.assertNotIn(start, {value & ~1 for _address, value in raw_hits})
            self.assertTrue(all(address % 4 != 0 for address, _ in raw_hits))
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<II", *record) for record in raw_hits
                )).hexdigest(),
                RAW_POINTER_SHA256[name],
            )
            caller_start, caller_end, caller_digest = CALLER_SPANS[name]
            caller = self.application[caller_start - BASE:caller_end - BASE]
            self.assertEqual(sha256(caller), caller_digest)
            self.assertTrue(caller_start <= CALLERS[name][0][0] < caller_end)
        for address, value in RAM_LITERALS.items():
            self.assertEqual(
                struct.unpack_from("<I", self.application, address - BASE)[0],
                value,
            )

    def test_target_sections_are_deterministic_and_relocation_free(self) -> None:
        for name, outputs in self.target_objects.items():
            self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())
            expected = TARGETS_BY_PROFILE[self.profile][name]
            for output in outputs:
                self.assertEqual(
                    output.stat().st_size,
                    expected["object_size"],
                )
                self.assertEqual(
                    sha256(output),
                    expected["object_sha256"],
                )
                data, sections = self.apollo_overlay.parse_elf32(output)
                symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
                symbol = next(
                    item for item in symbols if item["name"] == expected["function"]
                )
                section = sections[int(symbol["section_index"])]
                body = data[
                    int(section["offset"]):
                    int(section["offset"]) + int(section["size"])
                ]
                self.assertEqual(int(section["alignment"]), expected["alignment"])
                self.assertEqual(
                    (int(symbol["value"]), int(symbol["size"])),
                    (1, expected["size"]),
                )
                self.assertEqual(body.hex(), expected["hex"])
                self.assertEqual(sha256(body), expected["sha256"])
                symbol_table = self.apollo_overlay.section_named(
                    sections, ".symtab"
                )
                string_table = sections[int(symbol_table["link"])]
                strings = data[
                    int(string_table["offset"]):
                    int(string_table["offset"]) + int(string_table["size"])
                ]
                parsed_symbols = []
                for index in range(int(symbol_table["size"]) // 16):
                    fields = struct.unpack_from(
                        "<IIIBBH", data,
                        int(symbol_table["offset"]) + index * 16,
                    )
                    parsed_symbols.append((
                        self.apollo_overlay.elf_string(strings, fields[0], "symbol"),
                        fields,
                    ))
                self.assertEqual(
                    [
                        symbol_name for symbol_name, fields in parsed_symbols
                        if symbol_name and fields[5] == 0
                    ],
                    [],
                )
                text_relocations = []
                for relocation_section in sections:
                    if int(relocation_section["type"]) != 9:
                        continue
                    relocated = sections[int(relocation_section["info"])]
                    for index in range(int(relocation_section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II", data,
                            int(relocation_section["offset"]) + index * 8,
                        )
                        if str(relocated["name"]).startswith(".text"):
                            text_relocations.append((
                                relocated["name"], offset, information & 0xFF,
                                parsed_symbols[information >> 8][0],
                            ))
                self.assertEqual(text_relocations, [])
                for section_item in sections:
                    if section_item["name"] in (".data", ".bss", ".rodata"):
                        self.assertEqual(int(section_item["size"]), 0)


if __name__ == "__main__":
    unittest.main()
