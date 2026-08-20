from __future__ import annotations

import os

import ctypes
import hashlib
import json
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
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_queue_delete.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_queue_delete_host.c"
)
UPSTREAM_ROOT = ROOT / "third_party" / "freertos-kernel"
UPSTREAM = UPSTREAM_ROOT / "queue.c"
PROVENANCE = UPSTREAM_ROOT / "PROVENANCE.json"
UPSTREAM_VERIFIER = UPSTREAM_ROOT / "verify_snapshot.py"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
CURRENT_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
OFFICIAL_PACKAGE_SIZE = 3_523_396
OFFICIAL_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
OFFICIAL_APPLICATION_SIZE = 3_523_364
OFFICIAL_APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_GIT_BLOB = "5c872e0302839d96aab90919788fdc2b0be1c09e"
UPSTREAM_SIZE = 125_614
UPSTREAM_SHA256 = (
    "5cdf4fa35fe059446effff5bf20deaf83"
    "ddffb08921bc198fda106b1d17dd894"
)
UPSTREAM_FUNCTION_SIZE = 1_282
UPSTREAM_FUNCTION_SHA256 = (
    "187b107325a8bb7f0a6b4a00e292137a"
    "1c6fcb137dbd412557d78cc982b260de"
)

STOCK_START = 0x0044_1EA2
STOCK_END = 0x0044_1EC4
STOCK_BYTES = bytes.fromhex(
    "80b5002806d1b8f1fcf800205ff0ff310860fee7"
    "90f84610002901d114f0a7f901bd"
)
STOCK_SHA256 = (
    "ab55f9fa6eb823935056d4b4030cc10d"
    "f52bc8b33318abea201e61348a026bc4"
)
STOCK_CALLERS = [
    (0x0044_9892, "f8f706fb"),
    (0x0044_9926, "f8f7bcfa"),
    (0x0044_9C0C, "f8f749f9"),
    (0x004D_46D2, "6df7e6fb"),
]
STOCK_CALLER_ADDRESS_SHA256 = (
    "8520448b9f8110d7a3cf643ab4bde5f"
    "283aa048b5c9f70b8852e3d2c6f7ccfde"
)
STOCK_CALLER_ENCODING_SHA256 = (
    "7a55e4d33d6231378002327418d6f902"
    "53350bee3f70bb3fc0a5fec640130713"
)
STOCK_OUTGOING = [
    (0x0044_1EA8, "b8f1fcf8", 0x005F_A0A4),
    (0x0044_1EBE, "14f0a7f9", 0x0045_6210),
]

SOURCE_SIZE = 5_851
SOURCE_SHA256 = (
    "fa8033f61e418dbfb304dd7443dea340b"
    "fff88958df493e276ea92db4491da2b"
)
TARGET_FUNCTION = "open_cfw_freertos_queue_delete"
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
TARGET_BYTES = bytes.fromhex(
    "80b540b190f84610002918bf80bdbde88040"
    "fff7febffff7feff4ff0ff300021016000bffee7"
)
TARGET_SHA256 = (
    "b0c3844d1a62895d7896ed285cb8cf84"
    "f3d11105113e393765d3054e3bef57be"
)
TARGET_RELOCATIONS = [
    (0x12, 30, "open_cfw_freertos_heap4_free"),
    (0x16, 10, "ulSetInterruptMask"),
]
PRODUCTION_OFFSET = 114_700
PRODUCTION_RUNTIME_ADDRESS = 0x007B_0330
PRODUCTION_SHA256 = (
    "078c97be19fff941ddb8ea3685dc5137f"
    "7e4d7e69e25ffaa0bdf21c22df509f2"
)
PRODUCTION_OVERLAY_SIZE = 164_536
PRODUCTION_OVERLAY_SHA256 = (
    "a437e33ec76c3531ecb2b66d7239229b3a1d905bdc76b00cb564bd05b7ac2546"
)
PRODUCTION_COMPONENT_SIZE = 3_687_932
PRODUCTION_COMPONENT_SHA256 = (
    "4fdb5af59a3ae68ce25c2d3255fcc4f4ea0c9a77f2ac89a1d16532496c082c07"
)
PRODUCTION_DEPENDENCIES = {
    "open_cfw_freertos_heap4_free": 0x007B_02BC,
    "ulSetInterruptMask": 0x007A_FF08,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_function(source: str, marker: str) -> bytes:
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1].encode()
    raise AssertionError(f"unterminated function starting at {marker!r}")


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class HostResult(ctypes.Structure):
    _fields_ = [
        ("assert_calls", ctypes.c_uint),
        ("mask_calls", ctypes.c_uint),
        ("free_calls", ctypes.c_uint),
        ("freed_pointer", ctypes.c_size_t),
    ]


def result_tuple(result: HostResult) -> tuple[int, int, int, int]:
    return (
        result.assert_calls,
        result.mask_calls,
        result.free_calls,
        result.freed_pointer,
    )


class RuntimeFreeRTOSQueueDeleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[PACKAGE_PREAMBLE_SIZE:]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-freertos-queue-delete-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_queue_delete.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_queue_delete.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        host_compile = subprocess.run(
            host_command,
            check=False,
            capture_output=True,
            text=True,
        )
        if host_compile.returncode:
            raise AssertionError(host_compile.stderr or host_compile.stdout)

        cls.loaded = ctypes.CDLL(str(library))
        cls.call = cls.loaded.open_cfw_test_queue_delete_call
        cls.call.argtypes = [
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(HostResult),
        ]
        cls.call.restype = None
        cls.oracle = cls.loaded.open_cfw_test_queue_delete_oracle
        cls.oracle.argtypes = cls.call.argtypes
        cls.oracle.restype = None
        cls.queue_pointer = (
            cls.loaded.open_cfw_test_queue_delete_queue_pointer
        )
        cls.queue_pointer.argtypes = []
        cls.queue_pointer.restype = ctypes.c_size_t
        cls.queue_size = cls.loaded.open_cfw_test_queue_delete_queue_size
        cls.queue_size.argtypes = []
        cls.queue_size.restype = ctypes.c_uint
        cls.marker_offset = (
            cls.loaded.open_cfw_test_queue_delete_marker_offset
        )
        cls.marker_offset.argtypes = []
        cls.marker_offset.restype = ctypes.c_uint

        cls.target_object = temporary / "runtime_freertos_queue_delete.o"
        target_compile = subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if target_compile.returncode:
            raise AssertionError(
                target_compile.stderr or target_compile.stdout
            )
        cls.target_compile_stderr = target_compile.stderr

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.elf, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.symbols = apollo_overlay.parse_elf32_symbols(
            cls.elf,
            cls.sections,
        )
        cls.sections_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        text = cls.sections_by_name[f".text.{TARGET_FUNCTION}"]
        cls.target_text = cls.elf[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        cls.current_config = json.loads(CURRENT_CONFIG.read_text())
        cls.current_output = temporary / "current-overlay"
        cls.current_report = apollo_overlay.build(
            root=ROOT,
            config_path=CURRENT_CONFIG,
            output_dir=cls.current_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.current_overlay = (
            cls.current_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.current_component = (
            cls.current_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_upstream_and_source_algorithm_are_exact(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM.stat().st_size, UPSTREAM_SIZE)
        self.assertEqual(sha256(UPSTREAM.read_bytes()), UPSTREAM_SHA256)
        upstream_block = extract_function(
            UPSTREAM.read_text(),
            "void vQueueDelete( QueueHandle_t xQueue )",
        )
        self.assertEqual(len(upstream_block), UPSTREAM_FUNCTION_SIZE)
        self.assertEqual(
            sha256(upstream_block),
            UPSTREAM_FUNCTION_SHA256,
        )

        provenance = json.loads(PROVENANCE.read_text())
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        self.assertEqual(
            provenance["files"]["queue.c"],
            {
                "size": UPSTREAM_SIZE,
                "sha256": UPSTREAM_SHA256,
                "git_blob_sha1": UPSTREAM_GIT_BLOB,
            },
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        self.assertIn("Git blobs", verifier.stdout)

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text()
        source_block = extract_function(
            source,
            "void vQueueDelete( QueueHandle_t xQueue )",
        )
        self.assertEqual(source_block, upstream_block)
        for marker in (
            "SPDX-License-Identifier: MIT",
            UPSTREAM_COMMIT,
            "#define configSUPPORT_DYNAMIC_ALLOCATION 1",
            "#define configSUPPORT_STATIC_ALLOCATION 1",
            "#define configQUEUE_REGISTRY_SIZE 0",
            "#define configUSE_TRACE_FACILITY 1",
            "ucStaticallyAllocated) == 0x46U",
            "open_cfw_freertos_heap4_free",
            "ulSetInterruptMask",
        ):
            self.assertIn(marker, source)

    def test_official_package_stock_body_and_boundaries_are_exact(
        self,
    ) -> None:
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), OFFICIAL_PACKAGE_SIZE)
        self.assertEqual(sha256(package), OFFICIAL_PACKAGE_SHA256)
        self.assertEqual(len(self.application), OFFICIAL_APPLICATION_SIZE)
        self.assertEqual(
            sha256(self.application),
            OFFICIAL_APPLICATION_SHA256,
        )

        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(body, STOCK_BYTES)
        self.assertEqual(len(body), 34)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(
            self.span(STOCK_START - 8, STOCK_START).hex(),
            "0860fee7806b02bd",
        )
        self.assertEqual(
            self.span(STOCK_END, STOCK_END + 8).hex(),
            "416a002904d0006b",
        )

    def test_stock_calls_and_whole_image_reference_topology_are_exact(
        self,
    ) -> None:
        direct_bl: list[tuple[int, str]] = []
        direct_bw: list[tuple[int, str]] = []
        external_interior: list[tuple[int, int, str]] = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in (
                (True, direct_bl),
                (False, direct_bw),
            ):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target == STOCK_START and not (
                    STOCK_START <= address < STOCK_END
                ):
                    destination.append((address, encoded.hex()))
                if STOCK_START < target < STOCK_END and not (
                    STOCK_START <= address < STOCK_END
                ):
                    external_interior.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(direct_bl, STOCK_CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(
            sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoding in direct_bl
                )
            ),
            STOCK_CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(
                b"".join(
                    bytes.fromhex(encoding)
                    for _address, encoding in direct_bl
                )
            ),
            STOCK_CALLER_ENCODING_SHA256,
        )

        narrow: list[tuple[int, int]] = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                if STOCK_START <= target < STOCK_END and not (
                    STOCK_START <= address < STOCK_END
                ):
                    narrow.append((address, target))
        self.assertEqual(narrow, [])

        stored: list[tuple[int, int]] = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if STOCK_START <= (value & ~1) < STOCK_END:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [])

        outgoing: list[tuple[int, str, int]] = []
        for address in range(STOCK_START, STOCK_END - 3, 2):
            encoded = self.span(address, address + 4)
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    address,
                    encoded,
                    link=True,
                )
            except self.apollo_overlay.BuildError:
                continue
            if not STOCK_START <= target < STOCK_END:
                outgoing.append((address, encoded.hex(), target))
        self.assertEqual(outgoing, STOCK_OUTGOING)

    def test_host_matches_oracle_exhaustively_for_queue_marker_byte(
        self,
    ) -> None:
        self.assertEqual(self.queue_size(), 0x50)
        self.assertEqual(self.marker_offset(), 0x46)
        queue_pointer = self.queue_pointer()

        for use_null_queue in (0, 1):
            for allocation_marker in range(0x100):
                with self.subTest(
                    null=bool(use_null_queue),
                    marker=allocation_marker,
                ):
                    actual = HostResult()
                    expected = HostResult()
                    self.call(
                        use_null_queue,
                        allocation_marker,
                        ctypes.byref(actual),
                    )
                    actual_bytes = ctypes.string_at(queue_pointer, 0x50)
                    self.oracle(
                        use_null_queue,
                        allocation_marker,
                        ctypes.byref(expected),
                    )
                    self.assertEqual(
                        result_tuple(actual),
                        result_tuple(expected),
                    )

                    if use_null_queue:
                        self.assertEqual(
                            result_tuple(actual),
                            (1, 1, 0, 0),
                        )
                        self.assertEqual(actual_bytes, b"\xA5" * 0x50)
                    elif allocation_marker == 0:
                        self.assertEqual(
                            result_tuple(actual),
                            (0, 0, 1, queue_pointer),
                        )
                    else:
                        self.assertEqual(
                            result_tuple(actual),
                            (0, 0, 0, 0),
                        )

                    if not use_null_queue:
                        expected_bytes = bytearray(b"\xA5" * 0x50)
                        expected_bytes[0x46] = allocation_marker
                        self.assertEqual(
                            actual_bytes,
                            bytes(expected_bytes),
                        )

    def test_host_marker_conversion_uses_the_low_eight_bits(self) -> None:
        queue_pointer = self.queue_pointer()
        for allocation_marker in (
            0x100,
            0x101,
            0x1FF,
            0xFFFF_FF00,
            0xFFFF_FFFF,
        ):
            with self.subTest(marker=allocation_marker):
                actual = HostResult()
                expected = HostResult()
                self.call(
                    0,
                    allocation_marker,
                    ctypes.byref(actual),
                )
                self.oracle(
                    0,
                    allocation_marker,
                    ctypes.byref(expected),
                )
                self.assertEqual(
                    result_tuple(actual),
                    result_tuple(expected),
                )
                if allocation_marker & 0xFF:
                    self.assertEqual(
                        result_tuple(actual),
                        (0, 0, 0, 0),
                    )
                else:
                    self.assertEqual(
                        result_tuple(actual),
                        (0, 0, 1, queue_pointer),
                    )

    def test_target_text_sections_relocations_and_symbol_closure_are_exact(
        self,
    ) -> None:
        self.assertEqual(self.target_compile_stderr, "")
        self.assertEqual(self.target_text, TARGET_BYTES)
        self.assertEqual(len(self.target_text), 38)
        self.assertEqual(sha256(self.target_text), TARGET_SHA256)

        text = self.sections_by_name[f".text.{TARGET_FUNCTION}"]
        self.assertEqual(int(text["alignment"]), 4)
        self.assertEqual(int(text["flags"]) & 7, 6)

        symbols_by_name = {
            str(symbol["name"]): symbol for symbol in self.symbols
        }
        function = symbols_by_name[TARGET_FUNCTION]
        self.assertEqual(int(function["binding"]), 1)
        self.assertEqual(int(function["type"]), 2)
        self.assertEqual(
            int(function["section_index"]),
            int(text["index"]),
        )
        self.assertEqual(int(function["value"]) & ~1, 0)
        self.assertEqual(int(function["size"]), 38)

        relocation_section = self.sections_by_name[
            f".rel.text.{TARGET_FUNCTION}"
        ]
        relocations = []
        for entry in range(
            int(relocation_section["offset"]),
            int(relocation_section["offset"])
            + int(relocation_section["size"]),
            8,
        ):
            offset, information = struct.unpack_from(
                "<II",
                self.elf,
                entry,
            )
            relocations.append(
                (
                    offset,
                    information & 0xFF,
                    str(self.symbols[information >> 8]["name"]),
                )
            )
        self.assertEqual(relocations, TARGET_RELOCATIONS)
        self.assertEqual(
            {
                name
                for _offset, _kind, name in relocations
                if int(symbols_by_name[name]["section_index"]) == 0
            },
            {"open_cfw_freertos_heap4_free", "ulSetInterruptMask"},
        )

        allocatable = [
            {
                "name": str(section["name"]),
                "size": int(section["size"]),
                "flags": int(section["flags"]),
                "alignment": int(section["alignment"]),
            }
            for section in self.sections
            if int(section["flags"]) & 2 and int(section["size"])
        ]
        self.assertEqual(
            allocatable,
            [
                {
                    "name": f".text.{TARGET_FUNCTION}",
                    "size": 38,
                    "flags": 6,
                    "alignment": 4,
                },
                {
                    "name": f".ARM.exidx.text.{TARGET_FUNCTION}",
                    "size": 8,
                    "flags": 130,
                    "alignment": 4,
                },
            ],
        )

    def test_production_dependency_policy_is_explicit_and_stock_free_is_gone(
        self,
    ) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "extern open_cfw_queue_delete_ubase_type "
            "ulSetInterruptMask(void);",
            source,
        )
        self.assertIn(
            "extern void open_cfw_freertos_heap4_free(void *allocation);",
            source,
        )
        self.assertIn(
            "(void)ulSetInterruptMask();",
            source,
        )
        self.assertIn(
            "open_cfw_freertos_heap4_free((allocation))",
            source,
        )
        for retained_stock_seam in (
            "0x005FA0A5",
            "0x00456211",
            "0x00456210",
        ):
            self.assertNotIn(retained_stock_seam, source)
        self.assertIn(
            "future source-owned heap_4 vPortFree adapter",
            source,
        )

    @_APPLE_ONLY
    def test_production_redirect_relocation_and_artifacts_are_exact(
        self,
    ) -> None:
        config_leaf = next(
            leaf
            for leaf in self.current_config["relocated_leaves"]
            if leaf["function"] == TARGET_FUNCTION
        )
        self.assertEqual(config_leaf["function"], TARGET_FUNCTION)
        self.assertEqual(
            {
                "path": config_leaf["source"]["path"],
                "size": config_leaf["source"]["size"],
                "sha256": config_leaf["source"]["sha256"],
            },
            {
                "path": (
                    "components/apollo_main/core_overlay/"
                    "runtime_freertos_queue_delete.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
            },
        )
        self.assertEqual(
            config_leaf["expected"],
            {
                "size": 38,
                "sha256": PRODUCTION_SHA256,
                "alignment": 4,
                "offset": PRODUCTION_OFFSET,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        self.assertEqual(
            self.current_config["functions"].count(TARGET_FUNCTION),
            1,
        )
        config_patch = next(
            patch
            for patch in self.current_config["patch_sites"]
            if patch["name"] == "replace_freertos_queue_delete"
        )
        self.assertEqual(
            config_patch,
            {
                "name": "replace_freertos_queue_delete",
                "runtime_address": STOCK_START,
                "expected_size": len(STOCK_BYTES),
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": TARGET_FUNCTION,
            },
        )
        self.assertEqual(
            self.current_config["expected"],
            {
                "overlay_size": PRODUCTION_OVERLAY_SIZE,
                "overlay_sha256": PRODUCTION_OVERLAY_SHA256,
                "component_size": PRODUCTION_COMPONENT_SIZE,
                "component_sha256": PRODUCTION_COMPONENT_SHA256,
            },
        )

        report_leaf = next(
            leaf
            for leaf in self.current_report["relocated_leaves"]
            if leaf["extraction"]["function"] == TARGET_FUNCTION
        )
        self.assertEqual(
            report_leaf["placement"],
            {
                "alignment": 4,
                "offset": PRODUCTION_OFFSET,
                "padding_before": 2,
                "runtime_address": PRODUCTION_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B0330",
                "size": 38,
            },
        )
        extraction = report_leaf["extraction"]
        self.assertEqual(extraction["sha256"], PRODUCTION_SHA256)
        self.assertEqual(
            extraction["unrelocated_sha256"],
            TARGET_SHA256,
        )
        self.assertEqual(
            [
                (
                    relocation["offset"],
                    relocation["type"],
                    relocation["symbol"],
                    relocation["target_address"],
                )
                for relocation in extraction["relocations"]
            ],
            [
                (
                    offset,
                    (
                        "R_ARM_THM_CALL"
                        if kind == 10
                        else "R_ARM_THM_JUMP24"
                    ),
                    symbol,
                    PRODUCTION_DEPENDENCIES[symbol],
                )
                for offset, kind, symbol in TARGET_RELOCATIONS
            ],
        )
        self.assertEqual(
            self.current_report["overlay"]["functions"][TARGET_FUNCTION],
            {"offset": PRODUCTION_OFFSET, "size": 38},
        )
        self.assertEqual(
            (
                len(self.current_overlay),
                sha256(self.current_overlay),
                len(self.current_component),
                sha256(self.current_component),
            ),
            (
                PRODUCTION_OVERLAY_SIZE,
                PRODUCTION_OVERLAY_SHA256,
                PRODUCTION_COMPONENT_SIZE,
                PRODUCTION_COMPONENT_SHA256,
            ),
        )
        self.assertEqual(
            sha256(
                self.current_overlay[
                    PRODUCTION_OFFSET:PRODUCTION_OFFSET + 38
                ]
            ),
            PRODUCTION_SHA256,
        )

        patch = next(
            item
            for item in self.current_report["overlay"]["patched_sites"]
            if item["name"] == "replace_freertos_queue_delete"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["name"], "replace_freertos_queue_delete")
        self.assertEqual(patch["payload_offset"], 40_642)
        self.assertEqual(len(replacement), len(STOCK_BYTES))
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                replacement[:4],
                link=False,
            ),
            PRODUCTION_RUNTIME_ADDRESS,
        )
        self.assertEqual(
            self.current_component[
                40_642:40_642 + len(STOCK_BYTES)
            ],
            replacement,
        )
        self.assertEqual(
            sha256(self.span(STOCK_START, STOCK_END)),
            STOCK_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
