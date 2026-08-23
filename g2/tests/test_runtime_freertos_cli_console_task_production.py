from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_freertos_cli_console_task_candidate as candidate_contract

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay


SOURCE_ROOT = ROOT / "components/shared/freertos_cli"
HEADER = SOURCE_ROOT / "runtime_freertos_cli_console.h"
SOURCE_KEYS = (
    "fill",
    "state_initialize",
    "register_groups",
    "process_command",
    "consume_byte",
    "poll_once",
    "task",
)
SOURCES = {
    key: SOURCE_ROOT / f"runtime_freertos_cli_console_{key}.c"
    for key in SOURCE_KEYS
}
FUNCTIONS = {
    key: f"open_cfw_freertos_cli_console_{key}"
    for key in SOURCE_KEYS
}
FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_freertos_cli_console_task_production_host.c"
)
CANDIDATE_SOURCE = SOURCE_ROOT / "runtime_freertos_cli_console_task_candidate.c"
CANDIDATE_FUNCTIONS = (
    "open_cfw_freertos_cli_console_register_groups_candidate",
    "open_cfw_freertos_cli_console_consume_byte_candidate",
    "open_cfw_freertos_cli_console_poll_once_candidate",
    "open_cfw_freertos_cli_console_task_candidate",
)
CAPACITY_SOURCE = (
    ROOT / "components/apollo_main/core_overlay"
    / "runtime_freertos_cli_collector_capacity_patch.S"
)
CAPACITY_FUNCTION = "open_cfw_freertos_cli_collector_capacity_patch"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
OFFICIAL = candidate_contract.OFFICIAL
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324
APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32

TARGET_FLAGS = candidate_contract.TARGET_FLAGS
EXIDX = (
    "0000000001000000",
    "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d",
)
RELOCATION_TYPE_NAMES = {
    10: "R_ARM_THM_CALL",
    30: "R_ARM_THM_JUMP24",
    47: "R_ARM_THM_MOVW_ABS_NC",
    48: "R_ARM_THM_MOVT_ABS",
    49: "R_ARM_THM_MOVW_PREL_NC",
    50: "R_ARM_THM_MOVT_PREL",
}

GROUP_UNDEFINED = [
    f"open_cfw_retained_freertos_cli_register_group_{address:06x}"
    for address in candidate_contract.GROUP_ENTRIES
]

LEAF_CONTRACTS = {
    "fill": {
        "undefined": [],
        "relocations": [],
    },
    "state_initialize": {
        "undefined": [FUNCTIONS["fill"]],
        "relocations": [
            (14, 10, FUNCTIONS["fill"]),
            (24, 30, FUNCTIONS["fill"]),
        ],
    },
    "register_groups": {
        "undefined": GROUP_UNDEFINED,
        "relocations": [
            *((2 + index * 4, 10, symbol)
              for index, symbol in enumerate(GROUP_UNDEFINED[:-1])),
            (90, 30, GROUP_UNDEFINED[-1]),
        ],
    },
    "process_command": {
        "undefined": [
            FUNCTIONS["fill"],
            "open_cfw_retained_freertos_cli_console_display_string",
            "open_cfw_retained_freertos_cli_process_command",
        ],
        "relocations": [
            (4, 49, ".L.str"),
            (8, 50, ".L.str"),
            (14, 10, "open_cfw_retained_freertos_cli_console_display_string"),
            (26, 10, "open_cfw_retained_freertos_cli_process_command"),
            (36, 10, "open_cfw_retained_freertos_cli_console_display_string"),
            (42, 10, FUNCTIONS["fill"]),
            (60, 30, FUNCTIONS["fill"]),
        ],
        "rodata": (
            ".rodata.str1.1",
            3,
            "0a2300",
            "e0b80d62fdb844abe788164f28a496176295a29c9216aebda18fbac9bc6e6958",
        ),
    },
    "consume_byte": {
        "undefined": [
            FUNCTIONS["process_command"],
            "open_cfw_retained_freertos_cli_console_display_byte",
        ],
        "relocations": [
            (14, 10, "open_cfw_retained_freertos_cli_console_display_byte"),
            (36, 30, FUNCTIONS["process_command"]),
            (56, 10, "open_cfw_retained_freertos_cli_console_display_byte"),
            (66, 30, "open_cfw_retained_freertos_cli_console_display_byte"),
        ],
    },
    "poll_once": {
        "undefined": [
            FUNCTIONS["consume_byte"],
            "open_cfw_retained_freertos_cli_console_receive",
            "open_cfw_retained_freertos_cli_console_receive_handle",
        ],
        "relocations": [
            (10, 47, "open_cfw_retained_freertos_cli_console_receive_handle"),
            (14, 48, "open_cfw_retained_freertos_cli_console_receive_handle"),
            (34, 10, "open_cfw_retained_freertos_cli_console_receive"),
            (48, 10, FUNCTIONS["consume_byte"]),
        ],
    },
    "task": {
        "undefined": [
            FUNCTIONS["poll_once"],
            FUNCTIONS["register_groups"],
            FUNCTIONS["state_initialize"],
            "open_cfw_retained_freertos_cli_console_input",
            "open_cfw_retained_freertos_cli_console_output",
        ],
        "relocations": [
            (2, 10, FUNCTIONS["register_groups"]),
            (10, 47, "open_cfw_retained_freertos_cli_console_input"),
            (14, 48, "open_cfw_retained_freertos_cli_console_input"),
            (18, 47, "open_cfw_retained_freertos_cli_console_output"),
            (22, 48, "open_cfw_retained_freertos_cli_console_output"),
            (26, 10, FUNCTIONS["state_initialize"]),
            (34, 10, FUNCTIONS["poll_once"]),
        ],
    },
}

# Filled from two independent, compile-twice runs.  The Linux records are
# intentionally first-class rather than inferred from the Apple objects.
PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "placements": {
            "fill": 123616,
            "state_initialize": 123824,
            "register_groups": 123852,
            "process_command": 123948,
            "consume_byte": 124016,
            "poll_once": 124112,
            "task": 124172,
        },
        "overlay": (174816, "b732d58cda6cf0a05c15e3eeb5beaa6bcf472a2822065ae6ca614a3417f7f6bf"),
        "component": (3698212, "125cfeb1bda76cbb2cc7d7d1e6fab92e00c63c4f00f5fa8a893c6f33912a55f3"),
        "package": (4476706, "26bf3d84c06987461340f6af8773e0ae59bd3ae75c630c00a2158fe3a4945058"),
        "patch_hex": "71f216b9",
        "patch_sha256": "6d870ddaa7df559599d4977303a6d74259f0c6b27fc79c71ace7e07747a1cfc5",
        "relocated": {
            "fill": "3e482cf70c10b7c75e961bd452cb69c80dfad902f0b33e7fa7d2304ff6e9bf03",
            "state_initialize": "f3861b92387a9260efc51eef08cf746ad6abdfde6f2696506f3b9528e8404066",
            "register_groups": "77cf8cf4becb393014f4c1b5d006a359d69f8fe2421b6fb95ce982e809b22dc2",
            "process_command": "cfcbb1262628b69310ca10ff57203fe53a7f6e3fe208b4e1df3a9aa67373c639",
            "consume_byte": "27039bbfe7164a1d112d05cb3144f1c2dc9fc481fcc0819e7f856ccf186199db",
            "poll_once": "b368973a74a54a8295aea421fc34cb49e8c65289e46fa82935d3784462bb5fff",
            "task": "7308944f96014c99315752549c093dca99120380e0883e297a3705a032921e9e",
        },
        "process_closure_sha256": "4737ac45442389bf1327152ee1cd9632ce3e42f085db2940096e3ae4944d06cb",
        "objects": {
            "fill": (996, "4a9e5bf44d84c84bffb46b104f1f7360fd4e6ed95a0a2858e2b7306f0b985781"),
            "state_initialize": (1004, "9837dea79438b7e4345c9cbfc9a0cad1c0a6dad590969ba45f9ed2ef69c2e614"),
            "register_groups": (2696, "fc7279947547fdae28a2a92d98092257da9b5511ae02abf672518138ec61c88b"),
            "process_command": (1288, "e70a2ffb8d901073589e955c76689378187ff3cb4d0dca01b620bec336f936e6"),
            "consume_byte": (1156, "3caf356c08a13a5c5ed4b719932a1f7b64528f2c38c91274da6c027d367d50a0"),
            "poll_once": (1172, "59195c9b4962b472dcbb42e983d3be27f7cccb5a68be1a9330a5cc80ee234b87"),
            "task": (1272, "f5562e330de86304088df24a716adafb6de9d99848dc63f0f859a8378e86edfe"),
        },
        "text": {
            "fill": (206, "3e482cf70c10b7c75e961bd452cb69c80dfad902f0b33e7fa7d2304ff6e9bf03"),
            "state_initialize": (28, "3d694300590c4d2e4ff1d61da8cb7044910ab447da4212a9f2e491bbc3b3eeb6"),
            "register_groups": (94, "c42b31b3c7edfc0f4c97d7c605496aba6d5f143e105896d4fc4044d450bc0de8"),
            "process_command": (64, "7a7b64b6bb4f76840425ce752cab36ce327e5a1d08a4e39925abd47e38945fa1"),
            "consume_byte": (96, "cf337e6ed1f74d74e05b1ee74360ade7d8f11e1d3fd9cf05c85ef6b221624ef5"),
            "poll_once": (60, "d56883f65afdfbc41d312439f138c328e3d75f858fec4363291dfad0e00dd644"),
            "task": (40, "3a81c83e46a5e3d9e2babdddebd4fef59f8ffa8bc898539358043aff9554a212"),
        },
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "placements": {
            "fill": 125436,
            "state_initialize": 125644,
            "register_groups": 125672,
            "process_command": 125768,
            "consume_byte": 125836,
            "poll_once": 125932,
            "task": 125992,
        },
        "overlay": (145208, "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826"),
        "component": (3668604, "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798"),
        "package": (4447098, "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e"),
        "patch_hex": "71f2a4bc",
        "patch_sha256": "a500c15f33dba7ea1c1b02c262fcf2d993336459df2d669deecc3387d769b27b",
        "relocated": {
            "fill": "3e482cf70c10b7c75e961bd452cb69c80dfad902f0b33e7fa7d2304ff6e9bf03",
            "state_initialize": "45dce30fe21d369072df14497e787e6beb54db6db930f4e040752985a351eb5c",
            "register_groups": "55eef014cbc30f5768759449f97aaa18c9aa6aab82386f9a0b0956f5dc059855",
            "process_command": "ef0050123f471950e8bcdac7ec05437b7ecccf444bc4da8d6956ccda112e9dda",
            "consume_byte": "560efcddc2a4cec87c884b841b98536647f8c5afe200f43bd31e663df5d90e53",
            "poll_once": "0f866da7b216323328df175244cc86a165517014118183cd519ea3674bf2ee00",
            "task": "7308944f96014c99315752549c093dca99120380e0883e297a3705a032921e9e",
        },
        "process_closure_sha256": "3a0924c92282bd855721d44b79a601bb67682b6ad75ae46b3072ce74bd057c74",
        "objects": {
            "fill": (996, "4a9e5bf44d84c84bffb46b104f1f7360fd4e6ed95a0a2858e2b7306f0b985781"),
            "state_initialize": (1004, "b5ffc8c42dc9e8bfee27ccc923b0c624d28eca6460025785533a15f82c15e176"),
            "register_groups": (2696, "fc7279947547fdae28a2a92d98092257da9b5511ae02abf672518138ec61c88b"),
            "process_command": (1288, "9abedbfa1610ee0dde5dde602192db3f212d606effdcc6411349dd9bdd7a804a"),
            "consume_byte": (1156, "3caf356c08a13a5c5ed4b719932a1f7b64528f2c38c91274da6c027d367d50a0"),
            "poll_once": (1172, "59195c9b4962b472dcbb42e983d3be27f7cccb5a68be1a9330a5cc80ee234b87"),
            "task": (1272, "f5562e330de86304088df24a716adafb6de9d99848dc63f0f859a8378e86edfe"),
        },
        "text": {
            "fill": (206, "3e482cf70c10b7c75e961bd452cb69c80dfad902f0b33e7fa7d2304ff6e9bf03"),
            "state_initialize": (28, "bae21e5eb489ef2f435b7cf7d0fbd1963a0109e69277e508f2abc544c3576e0b"),
            "register_groups": (94, "c42b31b3c7edfc0f4c97d7c605496aba6d5f143e105896d4fc4044d450bc0de8"),
            "process_command": (64, "e1d41153cef322979d8bc9935439cc492997df2e1cc2f5706ac50bcbb06a02f8"),
            "consume_byte": (96, "cf337e6ed1f74d74e05b1ee74360ade7d8f11e1d3fd9cf05c85ef6b221624ef5"),
            "poll_once": (60, "d56883f65afdfbc41d312439f138c328e3d75f858fec4363291dfad0e00dd644"),
            "task": (40, "3a81c83e46a5e3d9e2babdddebd4fef59f8ffa8bc898539358043aff9554a212"),
        },
    },
}

LOCAL_PINS = {
    HEADER: (5130, "9e95cd8dc897c4e297ed0d40cba41b67d6ea5c3b074e38936a8b8ee6221f8cb9"),
    SOURCES["fill"]: (647, "ab462c7907249429fb42b1ec6a4bd10dfc45b3d229b00ea2566030d34f3f36eb"),
    SOURCES["state_initialize"]: (729, "a732d6b330ba38b24f1d087e39ac04878151630fcd13a9d0535780330c6d6946"),
    SOURCES["register_groups"]: (1733, "f450a90f191e7c38bb925ed7afe151f4a697a4ac6b46a93faa7e87135d1615d1"),
    SOURCES["process_command"]: (1086, "56ce2bedc38adbc159cce94b5819b63e76cd8734783a91aafc264d37386daa7e"),
    SOURCES["consume_byte"]: (1257, "fb0901dbea93c350c7d2d7428b02a0353c887299e881a91ea2bb4cae39d8bffd"),
    SOURCES["poll_once"]: (1388, "2a91f15ef412cdc2bb8496302497fb74a7b656cf2be3eec5832fdc409aa1a125"),
    SOURCES["task"]: (1472, "aff16ec008b73a0f732731220e1ec507220a283e2c4170bd6b100acefeeb5dae"),
    FIXTURE: (740, "31fc702b3a2bdad5b3c7ca8f68ba108196f17b2be96e683b445107057faa4d69"),
    candidate_contract.FIXTURE: candidate_contract.LOCAL_PINS[candidate_contract.FIXTURE],
}

EVENT_BYTE = candidate_contract.EVENT_BYTE
EVENT_STRING = candidate_contract.EVENT_STRING
EVENT_PROCESS = candidate_contract.EVENT_PROCESS
EVENT_REGISTER = candidate_contract.EVENT_REGISTER
EVENT_RECEIVE = candidate_contract.EVENT_RECEIVE


def normalize_registration_text(value: str) -> str:
    value = value.replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while "/./" in value:
        value = value.replace("/./", "/")
    return value


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


class RuntimeFreeRTOSCLIConsoleTaskProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profiles = [
            name for name, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(profiles) != 1:
            raise AssertionError(f"unreviewed target compiler: {(cls.clang, version)!r}")
        cls.profile = profiles[0]
        cls.pins = PROFILE_PINS[cls.profile]

        (ROOT / "build").mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-freertos-cli-console-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)
        cls.objects: dict[str, list[Path]] = {}
        for key, source in SOURCES.items():
            outputs = [temporary / f"{key}-a.o", temporary / f"{key}-b.o"]
            for output in outputs:
                subprocess.run(
                    [
                        cls.clang,
                        *TARGET_FLAGS,
                        "-c",
                        source.relative_to(ROOT).as_posix(),
                        "-o",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            cls.objects[key] = outputs

        library = temporary / (
            "freertos-cli-console-production.dylib"
            if sys.platform == "darwin"
            else "freertos-cli-console-production.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(SOURCE_ROOT),
            *(str(SOURCES[key]) for key in SOURCE_KEYS),
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))

        cls.lib.open_cfw_freertos_cli_console_host_reset.argtypes = []
        cls.lib.open_cfw_freertos_cli_console_host_consume.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_freertos_cli_console_host_poll.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_register.argtypes = []
        cls.lib.open_cfw_freertos_cli_console_host_set_process_count.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_freertos_cli_console_host_set_process_step.argtypes = [
            ctypes.c_uint32, ctypes.c_char_p, ctypes.c_int32,
        ]
        cls.lib.open_cfw_freertos_cli_console_host_set_receive.argtypes = [
            ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_freertos_cli_console_host_length.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_input.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_freertos_cli_console_host_output.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_freertos_cli_console_host_event_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_event_type.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_freertos_cli_console_host_event_type.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_event_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_freertos_cli_console_host_event_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_event_text.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_freertos_cli_console_host_event_text.restype = ctypes.c_char_p
        cls.lib.open_cfw_freertos_cli_console_host_process_calls.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_receive_handle.restype = ctypes.c_size_t
        cls.lib.open_cfw_freertos_cli_console_host_receive_length.restype = ctypes.c_uint32
        cls.lib.open_cfw_freertos_cli_console_host_receive_timeout.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_freertos_cli_console_host_reset()

    def events(self) -> list[tuple[int, int, str]]:
        result = []
        for index in range(self.lib.open_cfw_freertos_cli_console_host_event_count()):
            text = self.lib.open_cfw_freertos_cli_console_host_event_text(index)
            result.append((
                self.lib.open_cfw_freertos_cli_console_host_event_type(index),
                self.lib.open_cfw_freertos_cli_console_host_event_value(index),
                "" if text is None else text.decode("latin1"),
            ))
        return result

    def buffers(self) -> tuple[bytes, bytes]:
        return (
            bytes(self.lib.open_cfw_freertos_cli_console_host_input()[:128]),
            bytes(self.lib.open_cfw_freertos_cli_console_host_output()[:128]),
        )

    def test_production_sources_and_per_tu_object_contracts_are_exact(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual((path.stat().st_size, sha256(path)), (size, digest))

        for key, contract in LEAF_CONTRACTS.items():
            objects = self.objects[key]
            self.assertEqual(objects[0].read_bytes(), objects[1].read_bytes(), key)
            for path in objects:
                with self.subTest(profile=self.profile, leaf=key, object=path.name):
                    self.assertEqual(
                        (path.stat().st_size, sha256(path)),
                        self.pins["objects"][key],
                    )
                    data, sections = apollo_overlay.parse_elf32(path)
                    function = FUNCTIONS[key]
                    text_section = ".text." + function
                    section = apollo_overlay.section_named(sections, text_section)
                    body = data[
                        int(section["offset"]):
                        int(section["offset"]) + int(section["size"])
                    ]
                    self.assertEqual(int(section["alignment"]), 4)
                    self.assertEqual(
                        (len(body), sha256(body)),
                        self.pins["text"][key],
                    )
                    executable = [
                        item["name"] for item in sections
                        if int(item["size"]) and int(item["flags"]) & 0x4
                    ]
                    self.assertEqual(executable, [text_section])

                    symbols = apollo_overlay.parse_elf32_symbols(data, sections)
                    undefined = sorted(
                        item["name"] for item in symbols
                        if item["name"] and int(item["section_index"]) == 0
                    )
                    self.assertEqual(undefined, sorted(contract["undefined"]))
                    by_name = {item["name"]: item for item in symbols if item["name"]}
                    self.assertEqual(int(by_name[function]["size"]), len(body))

                    text_relocations = []
                    exidx_relocations = []
                    for relocation_section in sections:
                        if int(relocation_section["type"]) != 9:
                            continue
                        target = sections[int(relocation_section["info"])]
                        records = []
                        for index in range(int(relocation_section["size"]) // 8):
                            offset, information = struct.unpack_from(
                                "<II",
                                data,
                                int(relocation_section["offset"]) + index * 8,
                            )
                            records.append((
                                offset,
                                information & 0xFF,
                                symbols[information >> 8]["name"],
                            ))
                        if target["name"] == text_section:
                            text_relocations.extend(records)
                        elif target["name"] == ".ARM.exidx" + text_section:
                            exidx_relocations.extend(records)
                    self.assertEqual(text_relocations, contract["relocations"])
                    self.assertEqual(exidx_relocations, [(0, 42, "")])

                    exidx = apollo_overlay.section_named(
                        sections, ".ARM.exidx" + text_section,
                    )
                    exidx_body = data[
                        int(exidx["offset"]):
                        int(exidx["offset"]) + int(exidx["size"])
                    ]
                    self.assertEqual((exidx_body.hex(), sha256(exidx_body)), EXIDX)

                    rodata = contract.get("rodata")
                    observed_rodata = [
                        item for item in sections
                        if int(item["size"]) and str(item["name"]).startswith(".rodata")
                    ]
                    if rodata is None:
                        self.assertEqual(observed_rodata, [])
                    else:
                        self.assertEqual(len(observed_rodata), 1)
                        item = observed_rodata[0]
                        rodata_body = data[
                            int(item["offset"]):
                            int(item["offset"]) + int(item["size"])
                        ]
                        self.assertEqual(
                            (item["name"], len(rodata_body), rodata_body.hex(), sha256(rodata_body)),
                            rodata,
                        )

    def test_exhaustive_short_state_machine_matches_independent_oracle(self) -> None:
        alphabet = (ord("A"), ord("B"), 0x08, 0x7F, 0x0A, 0x0D)
        for length in range(5):
            for values in itertools.product(alphabet, repeat=length):
                with self.subTest(values=values):
                    self.lib.open_cfw_freertos_cli_console_host_reset()
                    oracle = candidate_contract.Oracle()
                    for value in values:
                        oracle.consume(value)
                        self.lib.open_cfw_freertos_cli_console_host_consume(value)
                    self.assertEqual(
                        self.lib.open_cfw_freertos_cli_console_host_length(),
                        oracle.length,
                    )
                    self.assertEqual(self.buffers(), (bytes(oracle.input), bytes(oracle.output)))
                    self.assertEqual(self.events(), oracle.events)

    def test_127_byte_bound_continuation_and_failed_receive_are_exact(self) -> None:
        for _ in range(128):
            self.lib.open_cfw_freertos_cli_console_host_consume(ord("X"))
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 127)
        self.assertEqual(self.buffers()[0], b"X" * 127 + b"\0")
        self.assertEqual(len(self.events()), 128)

        self.lib.open_cfw_freertos_cli_console_host_reset()
        self.lib.open_cfw_freertos_cli_console_host_set_process_count(3)
        for index, (output, result) in enumerate(((b"one", 1), (b"two", -7), (b"done", 0))):
            self.lib.open_cfw_freertos_cli_console_host_set_process_step(index, output, result)
        for value in b"get\r":
            self.lib.open_cfw_freertos_cli_console_host_consume(value)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_process_calls(), 3)
        self.assertEqual(self.events()[-7:], [
            (EVENT_STRING, 0, "\n#"),
            (EVENT_PROCESS, 128, "get"),
            (EVENT_STRING, 0, "one"),
            (EVENT_PROCESS, 128, "get"),
            (EVENT_STRING, 0, "two"),
            (EVENT_PROCESS, 128, "get"),
            (EVENT_STRING, 0, "done"),
        ])
        self.assertEqual(self.buffers(), (bytes(128), bytes(128)))

        self.lib.open_cfw_freertos_cli_console_host_reset()
        for result in (0, 2, 0xFFFF_FFFF):
            with self.subTest(receive_count=result):
                self.lib.open_cfw_freertos_cli_console_host_set_receive(
                    result, ord("Q"), 1,
                )
                self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_poll(), 0)
                self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 0)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_handle(), 0x200748BC)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_length(), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_timeout(), -1)

        self.lib.open_cfw_freertos_cli_console_host_set_receive(1, ord("Q"), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_poll(), 1)
        self.assertEqual(self.buffers()[0][:2], b"Q\0")

    def test_stock_topology_ingress_and_all_registration_groups_are_exact(self) -> None:
        image = OFFICIAL.read_bytes()
        self.assertEqual(
            (len(image), sha256(image)),
            (candidate_contract.PACKAGE_SIZE, candidate_contract.PACKAGE_SHA256),
        )

        def span(start: int, end: int) -> bytes:
            return image[start - candidate_contract.BASE:end - candidate_contract.BASE]

        self.assertEqual(sha256(span(*candidate_contract.TASK)), candidate_contract.TASK_SHA256)
        calls = []
        for address in range(candidate_contract.TASK[0], candidate_contract.TASK[1] - 3, 2):
            target = candidate_contract.decode_bl(address, span(address, address + 4))
            if target is not None:
                calls.append((address, target))
        self.assertEqual(tuple(calls), candidate_contract.TASK_CALLS)
        self.assertEqual(len(candidate_contract.GROUPS), 22)
        self.assertEqual(sum(group[2] for group in candidate_contract.GROUPS), 76)
        for start, end, count, digest in candidate_contract.GROUPS:
            self.assertEqual(sha256(span(start, end)), digest)
            targets = [
                candidate_contract.decode_bl(address, span(address, address + 4))
                for address in range(start, end - 3, 2)
            ]
            self.assertEqual(
                [target for target in targets if target is not None],
                [0x0058_47AC] * count,
            )

        literals = struct.unpack("<9I", span(*candidate_contract.LITERALS))
        self.assertEqual(literals[-1], 0x0054_1601)
        pointers = []
        for offset in range(len(image) - 3):
            value = struct.unpack_from("<I", image, offset)[0]
            if candidate_contract.TASK[0] <= (value & ~1) < candidate_contract.TASK[1]:
                pointers.append((candidate_contract.BASE + offset, value))
        self.assertEqual(pointers, [(0x0054_178C, 0x0054_1601)])

        apparent_branch_ingress = []
        for offset in range(0, len(image) - 3, 2):
            address = candidate_contract.BASE + offset
            if candidate_contract.TASK[0] <= address < candidate_contract.TASK[1]:
                continue
            encoded = image[offset:offset + 4]
            for kind, target in (
                ("wide", candidate_contract.decode_wide_unconditional(address, encoded)),
                ("wide_conditional", candidate_contract.decode_wide_conditional(address, encoded)),
            ):
                if (
                    target is not None
                    and candidate_contract.TASK[0] <= target < candidate_contract.TASK[1]
                ):
                    apparent_branch_ingress.append((address, target, kind))

            halfword = struct.unpack_from("<H", image, offset)[0]
            target = None
            kind = ""
            if halfword & 0xF800 == 0xE000:
                target = address + 4 + (
                    candidate_contract.sign_extend(halfword & 0x7FF, 11) << 1
                )
                kind = "narrow"
            elif halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0xF) < 0xE:
                target = address + 4 + (
                    candidate_contract.sign_extend(halfword & 0xFF, 8) << 1
                )
                kind = "narrow_conditional"
            elif halfword & 0xF500 == 0xB100:
                displacement = (
                    (((halfword >> 9) & 1) << 6)
                    | (((halfword >> 3) & 0x1F) << 1)
                )
                target = address + 4 + displacement
                kind = "cbz_cbnz"
            if (
                target is not None
                and candidate_contract.TASK[0] <= target < candidate_contract.TASK[1]
            ):
                apparent_branch_ingress.append((address, target, kind))
        self.assertEqual(
            apparent_branch_ingress,
            [(0x0054_15A4, 0x0054_1618, "cbz_cbnz")],
        )
        self.assertEqual(
            struct.unpack("<I", span(0x0054_15A4, 0x0054_15A8))[0],
            0x2037_B3C0,
        )
        self.assertEqual(
            candidate_contract.decode_bl(0x0054_1726, span(0x0054_1726, 0x0054_172A)),
            0x0047_2C7C,
        )
        self.assertEqual(
            struct.unpack("<9I", span(0x0075_B958, 0x0075_B97C)),
            (0x0078C614, 0, 0x200724C0, 0x70, 0x2036EE40, 0x1000, 0x18, 1, 0),
        )

        self.lib.open_cfw_freertos_cli_console_host_register()
        self.assertEqual(
            self.events(),
            [(EVENT_REGISTER, address, "") for address in candidate_contract.GROUP_ENTRIES],
        )

    def test_candidate_and_obsolete_capacity_leaf_are_absent_from_production(self) -> None:
        candidate_path = CANDIDATE_SOURCE.relative_to(ROOT).as_posix()
        capacity_path = CAPACITY_SOURCE.relative_to(ROOT).as_posix()
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = normalize_registration_text(path.read_text(encoding="utf-8"))
            self.assertNotIn(candidate_path, text, path)
            self.assertNotIn(CAPACITY_FUNCTION, text, path)
            self.assertNotIn(capacity_path, text, path)
            for function in CANDIDATE_FUNCTIONS:
                self.assertNotIn(function, text, (path, function))
        self.assertNotIn(
            "collector_capacity",
            normalize_registration_text(MANIFEST.read_text(encoding="utf-8")),
        )

    def test_candidate_exclusion_normalizes_equivalent_path_spellings(self) -> None:
        candidate_path = CANDIDATE_SOURCE.relative_to(ROOT).as_posix()
        capacity_path = CAPACITY_SOURCE.relative_to(ROOT).as_posix()
        variants = (
            candidate_path,
            candidate_path.replace("/freertos_cli/", "/freertos_cli/./"),
            candidate_path.replace("/freertos_cli/", "/freertos_cli//"),
            candidate_path.replace("/", "\\"),
            capacity_path,
            capacity_path.replace("/core_overlay/", "/core_overlay/./"),
            capacity_path.replace("/core_overlay/", "/core_overlay//"),
            capacity_path.replace("/", "\\"),
        )
        for variant in variants:
            with self.subTest(variant=variant):
                normalized = normalize_registration_text(variant)
                self.assertTrue(
                    candidate_path in normalized or capacity_path in normalized,
                    normalized,
                )

    def test_overlay_and_manifest_register_exact_seven_leaf_replacement(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        for function in FUNCTIONS.values():
            self.assertEqual(config["functions"].count(function), 1)
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in FUNCTIONS.values()
        }
        self.assertEqual(set(leaves), set(FUNCTIONS.values()))
        for key, function in FUNCTIONS.items():
            leaf = leaves[function]
            self.assertEqual(
                leaf["source"]["path"],
                SOURCES[key].relative_to(ROOT).as_posix(),
            )
            self.assertEqual(
                (leaf["source"]["size"], leaf["source"]["sha256"]),
                LOCAL_PINS[SOURCES[key]],
            )
            self.assertTrue(leaf["strict_relocation_contract"])
            self.assertEqual(
                [
                    (item["offset"], item["type"], item["symbol"])
                    for item in leaf["relocations"]
                ],
                [
                    (offset, RELOCATION_TYPE_NAMES[kind], symbol)
                    for offset, kind, symbol in LEAF_CONTRACTS[key]["relocations"]
                ],
            )
            for profile, pins in PROFILE_PINS.items():
                expected = (
                    leaf["expected"]
                    if profile == "apple-clang"
                    else leaf["toolchain_profiles"][profile]["expected"]
                )
                self.assertEqual(
                    (expected["size"], expected["unrelocated_sha256"]),
                    pins["text"][key],
                )
                self.assertEqual(expected["sha256"], pins["relocated"][key])
                self.assertEqual(expected["offset"], pins["placements"][key])
                if key == "process_command":
                    self.assertEqual(
                        expected["closure_sha256"],
                        pins["process_closure_sha256"],
                    )

        process_closure = leaves[FUNCTIONS["process_command"]]["closure"]
        self.assertEqual(
            process_closure,
            {
                "text_section": ".text." + FUNCTIONS["process_command"],
                "rodata": {
                    "section": ".rodata.str1.1",
                    "size": 3,
                    "sha256": LEAF_CONTRACTS["process_command"]["rodata"][3],
                    "alignment": 1,
                    "symbols": [{"name": ".L.str", "offset": 0, "size": 3}],
                },
            },
        )

        patch = next(
            item for item in config["patch_sites"]
            if item["name"] == "replace_freertos_cli_console_task"
        )
        self.assertEqual(patch, {
            "name": "replace_freertos_cli_console_task",
            "runtime_address": candidate_contract.TASK[0],
            "expected_size": candidate_contract.TASK[1] - candidate_contract.TASK[0],
            "expected_sha256": candidate_contract.TASK_SHA256,
            "branch": "b_w",
            "target_function": FUNCTIONS["task"],
        })
        self.assertNotIn("harden_freertos_cli_console_capacity", {
            item["name"] for item in config["patch_sites"]
        })
        for profile, pins in PROFILE_PINS.items():
            aggregate = (
                config["expected"]
                if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["overlay"],
            )
            self.assertEqual(
                (aggregate["component_size"], aggregate["component_sha256"]),
                pins["component"],
            )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        for profile, pins in PROFILE_PINS.items():
            provider = (
                main["provider"]
                if profile == "apple-clang"
                else main["provider"]["profiles"][profile]
            )
            package = (
                manifest["package"]
                if profile == "apple-clang"
                else manifest["package"]["profiles"][profile]
            )
            self.assertEqual(
                (provider["size"], provider["sha256"]),
                pins["component"],
            )
            self.assertEqual(
                (package["expected_size"], package["expected_sha256"]),
                pins["package"],
            )
        regions = {item["name"]: item for item in main["regions"]}
        replacement = regions["freertos_cli_console_task_source_replacement"]
        self.assertEqual(
            (replacement["size"], replacement["target_address"], replacement["address_status"]),
            (284, candidate_contract.TASK[0], "generated_source_entry_replacement"),
        )
        source_regions = [
            item for item in main["regions"]
            if item["address_status"] == "source_compiled"
            and "freertos_cli_console" in item["name"]
        ]
        self.assertEqual(
            {item["name"] for item in source_regions},
            {
                *(f"apollo_freertos_cli_console_{key}_source_leaf"
                  for key in SOURCE_KEYS),
                "apollo_freertos_cli_console_process_command_source_rodata",
            },
        )

        output = Path(self.temporary.name) / "registered-overlay"
        report = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
            output_dir=output,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            self.pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            self.pins["component"],
        )
        report_leaves = {
            item["extraction"]["function"]: item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] in FUNCTIONS.values()
        }
        for key, function in FUNCTIONS.items():
            placement = report_leaves[function]["placement"]
            self.assertEqual(placement["offset"], self.pins["placements"][key])
            self.assertEqual(
                placement["runtime_address"],
                OVERLAY_RUNTIME_ADDRESS + self.pins["placements"][key],
            )

        patch_report = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_freertos_cli_console_task"
        )
        replacement_bytes = bytes.fromhex(patch_report["replacement_hex"])
        task_runtime = (
            OVERLAY_RUNTIME_ADDRESS + self.pins["placements"]["task"]
        )
        self.assertEqual(len(replacement_bytes), 284)
        self.assertEqual(replacement_bytes[:4].hex(), self.pins["patch_hex"])
        self.assertEqual(replacement_bytes[4:], b"\x00\xbf" * 140)
        self.assertEqual(sha256(replacement_bytes), self.pins["patch_sha256"])
        self.assertEqual(patch_report["target_address"], task_runtime)
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                candidate_contract.TASK[0],
                replacement_bytes[:4],
                link=False,
            ),
            task_runtime,
        )

        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        official = OFFICIAL.read_bytes()
        patch_offset = (
            PACKAGE_PREAMBLE + candidate_contract.TASK[0] - APPLICATION_BASE
        )
        self.assertEqual(
            component[patch_offset:patch_offset + len(replacement_bytes)],
            replacement_bytes,
        )
        pointer_offset = PACKAGE_PREAMBLE + 0x0054_178C - APPLICATION_BASE
        self.assertEqual(
            component[pointer_offset:pointer_offset + 4],
            official[pointer_offset:pointer_offset + 4],
        )
        self.assertEqual(
            struct.unpack_from("<I", component, pointer_offset)[0],
            0x0054_1601,
        )


if __name__ == "__main__":
    unittest.main()
