from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import itertools
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components" / "shared" / "freertos_cli"
    / "runtime_freertos_cli_console_task_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_cli_console_task_candidate_host.c"
)
AUDIT = (
    ROOT / "docs" / "research"
    / "freertos-cli-console-task-source-candidate-audit.md"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
ANALYZER = ROOT / "tools" / "analyze_g2_freertos_plus_cli.py"
OVERLAY = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MAKEFILE = ROOT / "Makefile"
MANIFESTS = ROOT / "manifests"

BASE = 0x0043_7FE0
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
TASK = (0x0054_1600, 0x0054_171C)
TASK_SHA256 = "c1b9332fb9c932550478f1c2fa80546883aae78259aa887a0ec23ffb007338ef"
PREDECESSOR = (0x0054_15E6, 0x0054_1600)
PREDECESSOR_SHA256 = "ee4e0f209aee689ec87471e940a88d9cf1a1aea323b342c3a72f87043faaeb1e"
SUCCESSOR = (0x0054_171C, 0x0054_176A)
SUCCESSOR_SHA256 = "70ee9cc99f94d99e53017290b5aedfac52d59b8fae2e3e9435622e388134dfe5"
LITERALS = (0x0054_176C, 0x0054_1790)
LITERALS_SHA256 = "0c59069ad8144fd2e3712fc42a3e63ba6e8462f657c42f39155d6b768cf49dba"
FALSE_BRANCH_DATA = (0x0054_157A, 0x0054_15B4)
FALSE_BRANCH_DATA_SHA256 = "d672f0e669a363d991186dfaf619e555ea115bc373776000166151bccfeeeef3"

HELPER_RANGES = {
    (0x0054_15B4, 0x0054_15C2): "f95db635787d3076786e44cf1c634d50ae9761506e0eadc2a5a71967c40e67ae",
    (0x0054_15C2, 0x0054_15D8): "c0046e8521fae144d8ff6cb85288d75d75c4ab7e9f5f58a56f47643906137367",
    (0x0054_15D8, 0x0054_15E6): "0a186e5409fd503e7170317faaeb2f527c7f31dfce0d30f4ace9909ef54dbe23",
    (0x0054_15E6, 0x0054_1600): PREDECESSOR_SHA256,
    (0x0057_E136, 0x0057_E220): "c22d5821764704899a68d46b9b1bf3dbc79294dcd354c6377467fa051add4b82",
    (0x0043_C0E4, 0x0043_C14A): "34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a",
    (0x0058_47FE, 0x0058_48FC): "a276b358abd3ec722f4da8e17928590941d16f06ae92ad1375a1baf963e2893d",
}

GROUPS = (
    (0x0057_E626, 0x0057_E666, 10, "e9bff22d2c4858dd367cbe53769e56bd344727a552339726a83b3b3895f95394"),
    (0x0057_E810, 0x0057_E826, 3, "f57208fb0938240e05e508bfb4248d7d7db290eb940876fa766128d2fa24fa8e"),
    (0x0057_FF40, 0x0057_FF9E, 15, "2928d98b67f576aa5a3112fecd80be2be92bb08167ec56bc5d4012ffff0c7ac9"),
    (0x0058_0392, 0x0058_03EA, 14, "e9e11b71d7a953f40add22fc6db7e2c140e512cd6e83358c653982bd00feb044"),
    (0x0058_07C0, 0x0058_07D6, 3, "b566ae9eb61d5562b53453d352def664bd39b47f7b96f70eecdf5d0c6f355ba3"),
    (0x0058_0C04, 0x0058_0C0E, 1, "04d951f1cba903cb2425f8cddc06348aa7b5ed23712701a81222234df00ce437"),
    (0x0058_0FEC, 0x0058_0FFC, 2, "ea8fb4e126f02084ed16fb26ec275bb4cc1401ad3136bb9bcc6d53fea29f8efb"),
    (0x0058_10D8, 0x0058_10E2, 1, "94d6bd6b2fc3984de1987419124a4b7f9818b89b9883f942b25396deccc70bb6"),
    (0x0058_1136, 0x0058_1140, 1, "a5ec3697352cd3f00c5a554f5daf143708b4f59c2369fef18f3f85f8a8ee607c"),
    (0x0058_1644, 0x0058_167E, 9, "27a190f2ff277e8f9f368cdb0de7f82dfce6b2c5a3c9c305b48604ea6de75ed7"),
    (0x0058_183A, 0x0058_1844, 1, "fe29b54f58fdaf01bf7500576797af8c199bde22d539a23f961aa8124a84e83a"),
    (0x0058_1960, 0x0058_1970, 2, "7544cd18573008959e85e849123a12417746c168d2877a8436254b2e875d0d84"),
    (0x0058_1D60, 0x0058_1D70, 2, "0b74d5cb46e5b1bca973d0197dbe3347b69752841d3ef10475d1ad19369c40f5"),
    (0x0058_27D0, 0x0058_27EC, 4, "9adfec854f08f1068db5b1a32dc14964562f0b566e8e75195878cd3750a46c9d"),
    (0x0058_36B8, 0x0058_36C2, 1, "4676a5fe42ac524ae3e0f9c1cecd44b23616bde1c18d741146bc77f97ec58a19"),
    (0x0058_3CEC, 0x0058_3CF6, 1, "7e0e6a3cf8169401b0615955c79a1db8d30ce349fcb8c54ef34e6c502bf83091"),
    (0x0058_3F74, 0x0058_3F7E, 1, "587c3ca5137a0a107b6406181eabdd6ac3abfd5003292e9fba521f5b01dd2a2f"),
    (0x0058_40F4, 0x0058_40FE, 1, "9a313a0b24e3397f40b3999b268716d2943115ded644c5bd8b635f715bbc58b2"),
    (0x0058_41EE, 0x0058_41F8, 1, "e3a09eef8aa716e15de7634d5471832dedcd706e0c9c4e4ee57f3b075a6844c7"),
    (0x0058_4320, 0x0058_432A, 1, "6a51a0e74eecbf9f31de152e6bec087f77fe35896ce7aa4fb920bf557dd13c9d"),
    (0x0058_4430, 0x0058_443A, 1, "cf6853f937ccc3ec295dade574912bd84597651dc5c5ffe2731f1f2587491ca8"),
    (0x0058_4702, 0x0058_470C, 1, "de3ae5de4bd36558588b8156ca0011f877dc2c0cb3bee65a01b42d4b3943ddca"),
)
GROUP_ENTRIES = tuple(group[0] for group in GROUPS)

TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)
TARGET_PROFILES = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (6_000, "ad0ad14954ff3d75f7df2abe418a189da6388b9355ed817af6d74de2c2c9230d"),
        "state_initialize": "3d694300590c4d2e4ff1d61da8cb7044910ab447da4212a9f2e491bbc3b3eeb6",
        "process_command": "7a7b64b6bb4f76840425ce752cab36ce327e5a1d08a4e39925abd47e38945fa1",
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (6_000, "be786a9ac53ec9adf5d12a14ec1846c13f30852e156c2dbcc7d8e67b5fe82e9d"),
        "state_initialize": "bae21e5eb489ef2f435b7cf7d0fbd1963a0109e69277e508f2abc544c3576e0b",
        "process_command": "e1d41153cef322979d8bc9935439cc492997df2e1cc2f5706ac50bcbb06a02f8",
    },
}
TARGET_COMMON_TEXT = {
    ".text.open_cfw_freertos_cli_console_fill": (276, "979d9df64d5c0eb79dc8646e3a998634bf64d0cf595d77d87a89f000abb89964"),
    ".text.open_cfw_freertos_cli_console_register_groups_candidate": (94, "c42b31b3c7edfc0f4c97d7c605496aba6d5f143e105896d4fc4044d450bc0de8"),
    ".text.open_cfw_freertos_cli_console_consume_byte_candidate": (96, "cf337e6ed1f74d74e05b1ee74360ade7d8f11e1d3fd9cf05c85ef6b221624ef5"),
    ".text.open_cfw_freertos_cli_console_poll_once_candidate": (60, "a8aeb41733c509e26af49069103693cf33f71b628b24a153e3724ec401d15df4"),
    ".text.open_cfw_freertos_cli_console_task_candidate": (40, "d562abce89e860a446e4355d9c2802cd53a440843f8ff7cfd128de8cd6ee77bd"),
}
TARGET_EXIDX = (8, "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d")
TARGET_UNDEFINED = {
    *(f"open_cfw_retained_freertos_cli_register_group_{address:06x}" for address in GROUP_ENTRIES),
    "open_cfw_retained_freertos_cli_console_display_byte",
    "open_cfw_retained_freertos_cli_console_display_string",
    "open_cfw_retained_freertos_cli_process_command",
    "open_cfw_retained_freertos_cli_console_receive_handle",
    "open_cfw_retained_freertos_cli_console_receive",
    "open_cfw_retained_freertos_cli_console_input",
    "open_cfw_retained_freertos_cli_console_output",
}

TASK_CALLS = (
    *(zip(range(0x0054_1604, 0x0054_165C, 4), GROUP_ENTRIES)),
    (0x0054_1660, 0x0054_15C2),
    (0x0054_166E, 0x0058_47FE),
    (0x0054_1676, 0x0054_15C2),
    (0x0054_1680, 0x0043_C0E4),
    (0x0054_1690, 0x0043_C0E4),
    (0x0054_16A0, 0x0057_E136),
    (0x0054_16B6, 0x0054_15D8),
    (0x0054_16F8, 0x0054_15D8),
    (0x0054_16FE, 0x0054_15D8),
)

EVENT_BYTE = 1
EVENT_STRING = 2
EVENT_PROCESS = 3
EVENT_REGISTER = 4
EVENT_RECEIVE = 5

LOCAL_PINS = {
    SOURCE: (5_892, "7c00b33a7b4f684d464058f7be1f48b164bc609b18d5a54ee2d712a19cf9dea6"),
    HEADER: (4_645, "8fbf5dceac3faf654de85c82a296f371cd51872a5fe4909fe455e3da181e5183"),
    FIXTURE: (8_433, "f42a160a21ddccd34debca32c005c8a56f2390d83aad6c83d85a24c92e12610f"),
    AUDIT: (17_792, "a1514574e9dc1815911fa67ea977d272ac463f730ffb58d6df792ab460c79739"),
}


def sha256(data: bytes | Path) -> str:
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def decode_bl(address: int, encoded: bytes) -> int | None:
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def sign_extend(value: int, width: int) -> int:
    return value - (1 << width) if value & (1 << (width - 1)) else value


def decode_wide_unconditional(address: int, encoded: bytes) -> int | None:
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0x9000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def decode_wide_conditional(address: int, encoded: bytes) -> int | None:
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    condition = (first >> 6) & 0xF
    if condition >= 0xE:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20) | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18) | ((first & 0x3F) << 12)
        | ((second & 0x7FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


class Oracle:
    def __init__(self) -> None:
        self.input = bytearray(128)
        self.output = bytearray(128)
        self.length = 0
        self.events: list[tuple[int, int, str]] = []

    def consume(self, value: int) -> None:
        if value == 0x7F:
            value = 0x08
        self.events.append((EVENT_BYTE, value, ""))
        if value in (0x0A, 0x0D):
            self.events.append((EVENT_STRING, 0, "\n#"))
            text = bytes(self.input[:self.length]).decode("latin1")
            self.events.append((EVENT_PROCESS, 128, text))
            self.events.append((EVENT_STRING, 0, ""))
            self.output[:] = b"\0" * 128
            self.input[:] = b"\0" * 128
            self.length = 0
        elif value == 0x08:
            if self.length:
                self.length -= 1
                self.input[self.length] = 0
                self.events.extend([
                    (EVENT_BYTE, 0x20, ""),
                    (EVENT_BYTE, 0x08, ""),
                ])
        elif self.length < 127:
            self.input[self.length] = value
            self.length += 1
            self.input[self.length] = 0


class ConsoleCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = OFFICIAL.read_bytes()
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        cls.library_path = Path(cls.temp.name) / ("console" + suffix)
        compiler = shutil.which("cc") or shutil.which("clang")
        if compiler is None:
            raise unittest.SkipTest("native C compiler unavailable")
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), str(FIXTURE),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
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
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_freertos_cli_console_host_reset()

    def span(self, start: int, end: int) -> bytes:
        return self.image[start - BASE:end - BASE]

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

    def test_official_task_boundary_calls_literals_and_adjacent_helpers_are_exact(self) -> None:
        self.assertEqual((len(self.image), sha256(self.image)), (PACKAGE_SIZE, PACKAGE_SHA256))
        for bounds, digest in (
            (TASK, TASK_SHA256),
            (PREDECESSOR, PREDECESSOR_SHA256),
            (SUCCESSOR, SUCCESSOR_SHA256),
            (LITERALS, LITERALS_SHA256),
            (FALSE_BRANCH_DATA, FALSE_BRANCH_DATA_SHA256),
            *HELPER_RANGES.items(),
        ):
            self.assertEqual(sha256(self.span(*bounds)), digest)
        calls = []
        for address in range(TASK[0], TASK[1] - 3, 2):
            target = decode_bl(address, self.span(address, address + 4))
            if target is not None:
                calls.append((address, target))
        self.assertEqual(tuple(calls), TASK_CALLS)
        self.assertEqual(
            struct.unpack("<9I", self.span(*LITERALS)),
            (
                0x0000230A, 0x200748BC, 0x20071B48, 0x20071BC8,
                0x005415C3, 0x005415E7, 0x200748B8, 0x0075B958,
                0x00541601,
            ),
        )
        self.assertEqual(
            self.span(0x0054_1704, 0x0054_171C).hex(),
            "2000c0b28028c3da9df8000019492200d2b28854641cbbe7",
        )

    def test_registration_group_bodies_and_all_76_descriptors_are_exact(self) -> None:
        self.assertEqual(sum(group[2] for group in GROUPS), 76)
        for start, end, count, digest in GROUPS:
            body = self.span(start, end)
            self.assertEqual(sha256(body), digest)
            targets = [
                decode_bl(address, self.span(address, address + 4))
                for address in range(start, end - 3, 2)
            ]
            self.assertEqual([target for target in targets if target is not None], [0x0058_47AC] * count)

        spec = importlib.util.spec_from_file_location("cli_analyzer_console", ANALYZER)
        assert spec is not None and spec.loader is not None
        analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyzer)
        report = analyzer.audit_image(self.image)
        self.assertEqual(
            tuple(item["command"] for item in report["vendor_glue"]["commands"]),
            analyzer.VENDOR_COMMAND_NAMES,
        )

    def test_initializer_and_thread_attributes_close_creation_topology(self) -> None:
        self.assertEqual(sha256(self.span(*SUCCESSOR)), SUCCESSOR_SHA256)
        self.assertEqual(decode_bl(0x0054_1726, self.span(0x0054_1726, 0x0054_172A)), 0x0047_2C7C)
        self.assertEqual(decode_bl(0x0054_173E, self.span(0x0054_173E, 0x0054_1742)), 0x0057_DEEA)
        self.assertEqual(decode_bl(0x0054_174E, self.span(0x0054_174E, 0x0054_1752)), 0x0044_90E2)
        self.assertEqual(
            struct.unpack("<9I", self.span(0x0075_B958, 0x0075_B97C)),
            (0x0078C614, 0, 0x200724C0, 0x70, 0x2036EE40, 0x1000, 0x18, 1, 0),
        )

    def test_only_real_entry_reference_is_the_initializer_task_pointer(self) -> None:
        collisions = []
        for offset in range(len(self.image) - 3):
            value = struct.unpack_from("<I", self.image, offset)[0]
            if TASK[0] <= (value & ~1) < TASK[1]:
                collisions.append((BASE + offset, value))
        self.assertEqual(collisions, [(0x0054_178C, 0x0054_1601)])

        # A naive halfword scan sees CBZ r0,0x541618 at 0x5415A4.  The site is
        # the aligned literal word 0x2037B3C0 inside the authenticated pool,
        # not executable predecessor code.
        self.assertEqual(struct.unpack("<I", self.span(0x0054_15A4, 0x0054_15A8))[0], 0x2037B3C0)
        halfword = struct.unpack("<H", self.span(0x0054_15A4, 0x0054_15A6))[0]
        immediate = (((halfword >> 9) & 1) << 6) | (((halfword >> 3) & 0x1F) << 1)
        self.assertEqual(0x0054_15A4 + 4 + immediate, 0x0054_1618)

        apparent_entries = []
        for offset in range(0, len(self.image) - 3, 2):
            address = BASE + offset
            if TASK[0] <= address < TASK[1]:
                continue
            encoded = self.image[offset:offset + 4]
            for kind, target in (
                ("wide", decode_wide_unconditional(address, encoded)),
                ("wide_conditional", decode_wide_conditional(address, encoded)),
            ):
                if target is not None and TASK[0] <= target < TASK[1]:
                    apparent_entries.append((address, target, kind))

            narrow = struct.unpack_from("<H", self.image, offset)[0]
            target = None
            kind = ""
            if narrow & 0xF800 == 0xE000:
                target = address + 4 + (sign_extend(narrow & 0x7FF, 11) << 1)
                kind = "narrow"
            elif narrow & 0xF000 == 0xD000 and ((narrow >> 8) & 0xF) < 0xE:
                target = address + 4 + (sign_extend(narrow & 0xFF, 8) << 1)
                kind = "narrow_conditional"
            elif narrow & 0xF500 == 0xB100:
                displacement = (((narrow >> 9) & 1) << 6) | (((narrow >> 3) & 0x1F) << 1)
                target = address + 4 + displacement
                kind = "cbz_cbnz"
            if target is not None and TASK[0] <= target < TASK[1]:
                apparent_entries.append((address, target, kind))

        self.assertEqual(apparent_entries, [(0x0054_15A4, 0x0054_1618, "cbz_cbnz")])

    def test_exhaustive_short_state_machine_matches_independent_oracle(self) -> None:
        alphabet = (ord("A"), ord("B"), 0x08, 0x7F, 0x0A, 0x0D)
        for length in range(5):
            for values in itertools.product(alphabet, repeat=length):
                with self.subTest(values=values):
                    self.lib.open_cfw_freertos_cli_console_host_reset()
                    oracle = Oracle()
                    for value in values:
                        oracle.consume(value)
                        self.lib.open_cfw_freertos_cli_console_host_consume(value)
                    host_input, host_output = self.buffers()
                    self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), oracle.length)
                    self.assertEqual(host_input, bytes(oracle.input))
                    self.assertEqual(host_output, bytes(oracle.output))
                    self.assertEqual(self.events(), oracle.events)

    def test_process_continuation_prompt_output_order_and_full_clears(self) -> None:
        self.lib.open_cfw_freertos_cli_console_host_set_process_count(3)
        for index, (output, result) in enumerate(((b"one", 1), (b"two", -7), (b"done", 0))):
            self.lib.open_cfw_freertos_cli_console_host_set_process_step(index, output, result)
        for value in b"get\r":
            self.lib.open_cfw_freertos_cli_console_host_consume(value)
        self.assertEqual(
            self.events(),
            [
                (EVENT_BYTE, ord("g"), ""),
                (EVENT_BYTE, ord("e"), ""),
                (EVENT_BYTE, ord("t"), ""),
                (EVENT_BYTE, 0x0D, ""),
                (EVENT_STRING, 0, "\n#"),
                (EVENT_PROCESS, 128, "get"),
                (EVENT_STRING, 0, "one"),
                (EVENT_PROCESS, 128, "get"),
                (EVENT_STRING, 0, "two"),
                (EVENT_PROCESS, 128, "get"),
                (EVENT_STRING, 0, "done"),
            ],
        )
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_process_calls(), 3)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 0)
        self.assertEqual(self.buffers(), (bytes(128), bytes(128)))

    def test_backspace_del_and_reserved_terminator_behavior(self) -> None:
        for value in b"AB":
            self.lib.open_cfw_freertos_cli_console_host_consume(value)
        self.lib.open_cfw_freertos_cli_console_host_consume(0x7F)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 1)
        self.assertEqual(self.buffers()[0][:3], b"A\0\0")
        self.assertEqual(self.events()[-3:], [(EVENT_BYTE, 8, ""), (EVENT_BYTE, 32, ""), (EVENT_BYTE, 8, "")])

        self.lib.open_cfw_freertos_cli_console_host_reset()
        for _ in range(128):
            self.lib.open_cfw_freertos_cli_console_host_consume(ord("X"))
        input_buffer, _ = self.buffers()
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 127)
        self.assertEqual(input_buffer, b"X" * 127 + b"\0")
        self.assertEqual(len(self.events()), 128)  # ignored byte is still echoed

    def test_receive_abi_is_exact_and_failed_receive_is_discarded(self) -> None:
        self.lib.open_cfw_freertos_cli_console_host_set_receive(0, ord("Q"), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_poll(), 0)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 0)
        self.assertEqual(self.events(), [(EVENT_RECEIVE, 0, "")])
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_handle(), 0x200748BC)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_length(), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_receive_timeout(), -1)

        self.lib.open_cfw_freertos_cli_console_host_set_receive(1, ord("Q"), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_poll(), 1)
        self.assertEqual(self.lib.open_cfw_freertos_cli_console_host_length(), 1)
        self.assertEqual(self.buffers()[0][:2], b"Q\0")
        self.assertEqual(self.events()[-2:], [(EVENT_RECEIVE, 1, ""), (EVENT_BYTE, ord("Q"), "")])

    def test_candidate_registration_order_matches_task_fanout(self) -> None:
        self.lib.open_cfw_freertos_cli_console_host_register()
        self.assertEqual(
            self.events(),
            [(EVENT_REGISTER, address, "") for address in GROUP_ENTRIES],
        )

    def test_candidate_target_compiles_and_remains_production_excluded(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            raise unittest.SkipTest("target clang unavailable")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True,
        ).stdout.splitlines()[0]
        profiles = [
            name for name, profile in TARGET_PROFILES.items()
            if version == profile["version"]
        ]
        self.assertEqual(len(profiles), 1, f"unreviewed target compiler: {version}")
        profile = TARGET_PROFILES[profiles[0]]

        with tempfile.TemporaryDirectory() as directory:
            objects = [Path(directory) / "console-1.o", Path(directory) / "console-2.o"]
            for output in objects:
                subprocess.run(
                    [
                        clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(
                [(path.stat().st_size, sha256(path)) for path in objects],
                [profile["object"], profile["object"]],
            )

            spec = importlib.util.spec_from_file_location(
                "console_apollo_overlay", ROOT / "tools" / "apollo_overlay.py",
            )
            assert spec is not None and spec.loader is not None
            apollo_overlay = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(apollo_overlay)
            object_data, sections = apollo_overlay.parse_elf32(objects[0])
            observed_text = {}
            exidx = []
            relocation_count = 0
            for section in sections:
                name = str(section["name"])
                size = int(section["size"])
                body = object_data[
                    int(section["offset"]):int(section["offset"]) + size
                ]
                if name.startswith(".text."):
                    observed_text[name] = (size, sha256(body))
                    self.assertEqual(int(section["alignment"]), 4)
                if name.startswith(".ARM.exidx.text."):
                    exidx.append((size, sha256(body)))
                if int(section["type"]) == 9:
                    relocation_count += size // 8

            expected_text = {
                **TARGET_COMMON_TEXT,
                ".text.open_cfw_freertos_cli_console_state_initialize": (
                    28, profile["state_initialize"],
                ),
                ".text.open_cfw_freertos_cli_console_process_command": (
                    64, profile["process_command"],
                ),
            }
            self.assertEqual(observed_text, expected_text)
            self.assertEqual(sum(size for size, _ in observed_text.values()), 658)
            self.assertEqual(exidx, [TARGET_EXIDX] * 7)
            self.assertEqual(relocation_count, 53)

            symbol_table = apollo_overlay.section_named(sections, ".symtab")
            strings_section = sections[int(symbol_table["link"])]
            strings = object_data[
                int(strings_section["offset"]):
                int(strings_section["offset"]) + int(strings_section["size"])
            ]
            undefined = set()
            for index in range(int(symbol_table["size"]) // 16):
                fields = struct.unpack_from(
                    "<IIIBBH",
                    object_data,
                    int(symbol_table["offset"]) + index * 16,
                )
                name = apollo_overlay.elf_string(strings, fields[0], "symbol")
                if name and fields[5] == 0:
                    undefined.add(name)
            self.assertEqual(undefined, TARGET_UNDEFINED)

        needle = SOURCE.name
        self.assertNotIn(needle, OVERLAY.read_text())
        self.assertNotIn(needle, MAKEFILE.read_text())
        for manifest in MANIFESTS.glob("*.json"):
            self.assertNotIn(needle, manifest.read_text(), manifest)
        self.assertIn("Production-excluded", HEADER.read_text())
        self.assertIn("deliberately absent from every production", SOURCE.read_text())
        self.assertTrue(AUDIT.is_file())
        for artifact, (size, digest) in LOCAL_PINS.items():
            self.assertEqual((artifact.stat().st_size, sha256(artifact)), (size, digest))


if __name__ == "__main__":
    unittest.main()
