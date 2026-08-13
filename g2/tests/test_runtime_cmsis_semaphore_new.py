import os
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_cmsis_semaphore_new.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_cmsis_semaphore_new_host.c"
)
UPSTREAM_ROOT = ROOT / "third_party" / "cmsis-freertos"
UPSTREAM = (
    UPSTREAM_ROOT
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Source"
    / "cmsis_os2.c"
)
UPSTREAM_HEADER = (
    UPSTREAM_ROOT
    / "CMSIS_5"
    / "CMSIS"
    / "RTOS2"
    / "Include"
    / "cmsis_os2.h"
)
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
CURRENT_PACKAGE = (
    ROOT
    / "build"
    / "source"
    / "package"
    / "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
)
CURRENT_FLASH_PLAN = ROOT / "build" / "source" / "flash-plan.json"
QUEUE_DELETE_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_queue_delete.c"
)

APPLICATION_BASE = 0x0043_8000
STOCK_START = 0x0044_989A
STOCK_END = 0x0044_994E
STOCK_SHA256 = (
    "ebdcf69b866e35e468ba9ce84d7e7ac9"
    "b58377b5ffcc439762d729f7d99a098c"
)
STOCK_BYTES = bytes.fromhex(
    "f8b505000e0017000024fff7b3fb00284ed1002d4cd0b5424ad35ff0ff31002f"
    "0fd0b868002804d0f868502801d3012108e0b868002805d1f868002802d10021"
    "00e0002111f1010f32d0012d22d1012909d103200090bb68002200210120f7f7"
    "67fe040005e0032200210120f7f796fe0400002c1cd0002e1ad0002300220021"
    "2000f7f767ff012812d02000f8f7bcfa00240de0012906d1ba6831002800f7f7"
    "2aff040004e031002800f7f73dff04002000f2bd"
)
CALLERS = [
    (0x0045_D35A, "ecf79efa"),
    (0x004D_0A7A, "78f70eff"),
    (0x0050_4318, "45f7bffa"),
    (0x0058_4BD2, "c4f662fe"),
    (0x0059_CF32, "acf6b2fc"),
]
CALLER_SHA256 = (
    "b1bff9196e2fecc8b466bd89718cfb0b"
    "f0f3e825e4d220f08bbdd6e6d6598bcb"
)
OUTGOING = [
    (0x0044_98A4, "fff7b3fb", 0x0044_900E),
    (0x0044_98F8, "f7f767fe", 0x0044_15CA),
    (0x0044_9906, "f7f796fe", 0x0044_1636),
    (0x0044_991C, "f7f767ff", 0x0044_17EE),
    (0x0044_9926, "f8f7bcfa", 0x0044_1EA2),
    (0x0044_9938, "f7f72aff", 0x0044_1790),
    (0x0044_9944, "f7f73dff", 0x0044_17C2),
]

SOURCE_SIZE = 11_566
SOURCE_SHA256 = (
    "a947868d3fbcfc7f41d021210355e0ff"
    "777d49d3db84fa0da71a255d319c1527"
)
UPSTREAM_SHA256 = (
    "8a0d60b56ad30c4f7957f64fa5811580"
    "17b6812ec94b832d974c773ae4f2bc36"
)
UPSTREAM_FUNCTION_SIZE = 2_114
UPSTREAM_FUNCTION_SHA256 = (
    "1e4987ad6a3cb37c3564b0b9977a9a4b"
    "8d5845e7a49c2a737757ee74551a772c"
)

TARGET_FUNCTION = "open_cfw_cmsis_semaphore_new"
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
    "70b582b0eff3058313b1002002b070bd15460c460646fff7feff3246012816d1"
    "002a4ff00000f1d09442efd82146cdb1ab68e868a3b14f28e7d9012a2ed10326"
    "0120002100220096fff7feff11e0eff310800028d9d1eff311800028d5d1dfe7"
    "0028d2d1012a13d1012000210322fff7feff002c18bf0028c8d0002100220023"
    "0446fff7feff01280fd1204602b070bd104602b0bde87040fff7febf10461a46"
    "02b0bde87040fff7febf2046fff7feffabe7"
)
TARGET_SHA256 = (
    "70d7f154b29f5acc3654bb729bd1f5e8"
    "13fd1ff6dbadeb0bac80ff602141f998"
)
TARGET_RELOCATIONS = [
    (
        0x16,
        10,
        "open_cfw_freertos_task_get_scheduler_state",
    ),
    (
        0x48,
        10,
        "open_cfw_freertos_queue_generic_create_static",
    ),
    (
        0x6E,
        10,
        "open_cfw_freertos_queue_generic_create",
    ),
    (
        0x82,
        10,
        "open_cfw_freertos_queue_generic_send",
    ),
    (
        0x98,
        30,
        "open_cfw_freertos_queue_create_counting_semaphore",
    ),
    (
        0xA6,
        30,
        "open_cfw_freertos_queue_create_counting_semaphore_static",
    ),
    (
        0xAC,
        10,
        "open_cfw_freertos_queue_delete",
    ),
]
CURRENT_DEPENDENCY_ADDRESSES = {
    "open_cfw_freertos_task_get_scheduler_state": 0x007A_EAAC,
    "open_cfw_freertos_queue_generic_create_static": 0x007A_EB14,
    "open_cfw_freertos_queue_generic_create": 0x007A_EBC0,
    "open_cfw_freertos_queue_generic_send": 0x007A_E120,
    "open_cfw_freertos_queue_create_counting_semaphore_static":
        0x007A_EC94,
    "open_cfw_freertos_queue_create_counting_semaphore": 0x007A_ECD4,
    "open_cfw_freertos_queue_delete": 0x007B_0330,
}
PRODUCTION_OFFSET = 114_740
PRODUCTION_RUNTIME_ADDRESS = 0x007B_0358
PRODUCTION_SHA256 = (
    "5e1105ed86ca0f43effdf1e11e59ee7c"
    "6ce094b3321c127234c492a9cc70b8a4"
)
PRODUCTION_OVERLAY_SIZE = 142_578
PRODUCTION_OVERLAY_SHA256 = (
    "3d5c9fe87fd46cbc40bb5670653f45d3"
            "d61f9d777168aa47b70fb10712698ab4"
)
PRODUCTION_COMPONENT_SIZE = 3_665_974
PRODUCTION_COMPONENT_SHA256 = (
    "5cef32ba7350e7f6476336fa6a087010"
            "e6143e3e692205215c271430aa110d22"
)
PRODUCTION_PACKAGE_SIZE = 4_444_468
PRODUCTION_PACKAGE_SHA256 = (
    "e6472064c2536c055fb9a47efe49c9d9"
            "b553ce15ed1bc308115730454e3b94bc"
)
PRODUCTION_FLASH_PLAN_SHA256 = (
    "97230c89e27b9fea1db1d0cc9c2ca6bed"
    "5449ece6d35ea98cf101d7a219b1d9e"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_upstream_function(source: str) -> bytes:
    marker = "osSemaphoreId_t osSemaphoreNew ("
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
    raise AssertionError("unterminated upstream osSemaphoreNew")


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


def expected_route(
    maximum_count: int,
    initial_count: int,
    provide_attr: bool,
    provide_cb: bool,
    cb_size: int,
) -> str:
    if maximum_count == 0 or initial_count > maximum_count:
        return "none"
    if not provide_attr:
        memory = "dynamic"
    elif provide_cb and cb_size >= 80:
        memory = "static"
    elif not provide_cb and cb_size == 0:
        memory = "dynamic"
    else:
        return "none"
    kind = "binary" if maximum_count == 1 else "counting"
    return f"{kind}_{memory}"


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeCmsisSemaphoreNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_cmsis_semaphore_new.dylib"
            if sys.platform == "darwin"
            else "runtime_cmsis_semaphore_new.so"
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
        cls.host_compile = subprocess.run(
            host_command,
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.host_compile.returncode:
            raise AssertionError(
                cls.host_compile.stderr or cls.host_compile.stdout
            )

        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_cmsis_semaphore_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.call = cls.loaded.open_cfw_test_cmsis_semaphore_call
        cls.call.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        cls.call.restype = ctypes.c_size_t
        for name in ("control", "dynamic"):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_cmsis_semaphore_{name}_pointer",
            )
            function.argtypes = []
            function.restype = ctypes.c_size_t
            setattr(cls, f"{name}_pointer", function)
        for name in (
            "static_size",
            "attr_size",
            "attr_offset_name",
            "attr_offset_attr_bits",
            "attr_offset_cb_mem",
            "attr_offset_cb_size",
        ):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_cmsis_semaphore_{name}",
            )
            function.argtypes = []
            function.restype = ctypes.c_uint32
            setattr(cls, name, function)

        cls.target_object = temporary / "runtime_cmsis_semaphore_new.o"
        cls.target_compile = subprocess.run(
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
        if cls.target_compile.returncode:
            raise AssertionError(
                cls.target_compile.stderr or cls.target_compile.stdout
            )

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

    def get_uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def get_int(self, name: str) -> int:
        return ctypes.c_int.in_dll(self.loaded, name).value

    def get_pointer(self, name: str) -> int:
        value = ctypes.c_void_p.in_dll(self.loaded, name).value
        return 0 if value is None else value

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint.in_dll(self.loaded, name).value = value

    def set_int(self, name: str, value: int) -> None:
        ctypes.c_int.in_dll(self.loaded, name).value = value

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_upstream_and_bounded_source_are_exact(self) -> None:
        self.assertEqual(UPSTREAM.stat().st_size, 70_106)
        self.assertEqual(sha256(UPSTREAM.read_bytes()), UPSTREAM_SHA256)
        block = extract_upstream_function(UPSTREAM.read_text())
        self.assertEqual(len(block), UPSTREAM_FUNCTION_SIZE)
        self.assertEqual(sha256(block), UPSTREAM_FUNCTION_SHA256)

        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CMSIS-FreeRTOS v10.5.1", verifier.stdout)
        self.assertIn("Git blobs", verifier.stdout)

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        source = SOURCE.read_text()
        self.assertEqual(sha256(source.encode()), SOURCE_SHA256)
        self.assertIn("SPDX-License-Identifier: Apache-2.0", source)
        self.assertIn(
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            source,
        )
        for marker in (
            "#define configSUPPORT_STATIC_ALLOCATION 1",
            "#define configSUPPORT_DYNAMIC_ALLOCATION 1",
            "#define configQUEUE_REGISTRY_SIZE 0",
            "sizeof(open_cfw_cmsis_static_semaphore) == 0x50U",
            "sizeof(open_cfw_cmsis_semaphore_attr) == 0x10U",
            "#define xTaskGetSchedulerState",
            "#define xQueueGenericCreateStatic",
            "#define xQueueGenericCreate",
            "#define xQueueGenericSend",
            "#define vQueueDelete",
            "#define xQueueCreateCountingSemaphoreStatic",
            "#define xQueueCreateCountingSemaphore",
            "open_cfw_cmsis_semaphore_irq_context",
        ):
            self.assertIn(marker, source)

        header = UPSTREAM_HEADER.read_text()
        self.assertIn("} osSemaphoreAttr_t;", header)

    def test_stock_body_boundaries_calls_and_reference_topology(self) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(body, STOCK_BYTES)
        self.assertEqual(len(body), 180)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(
            self.span(STOCK_START - 8, STOCK_START).hex(),
            "f8f706fb280032bd",
        )
        self.assertEqual(
            self.span(STOCK_END, STOCK_END + 8).hex(),
            "7cb505000c000026",
        )

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
        self.assertEqual(direct_bl, CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(
            sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoding in direct_bl
                )
            ),
            CALLER_SHA256,
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
        self.assertEqual(outgoing, OUTGOING)

    def test_host_layout_and_default_creation_paths(self) -> None:
        self.assertEqual(self.static_size(), 80)
        self.assertEqual(
            (
                self.attr_size(),
                self.attr_offset_name(),
                self.attr_offset_attr_bits(),
                self.attr_offset_cb_mem(),
                self.attr_offset_cb_size(),
            ),
            (32, 0, 8, 16, 24),
        )

        self.reset()
        result = self.call(1, 0, 0, 0, 0, 0)
        self.assertEqual(result, self.dynamic_pointer())
        self.assertEqual(
            (
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_binary_dynamic_calls"
                ),
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_binary_dynamic_length"
                ),
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_binary_dynamic_item_size"
                ),
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_binary_dynamic_type"
                ),
            ),
            (1, 1, 0, 3),
        )
        self.assertEqual(
            self.get_uint("open_cfw_test_cmsis_semaphore_give_calls"),
            0,
        )

        self.reset()
        result = self.call(7, 3, 0, 0, 0, 1)
        self.assertEqual(result, self.dynamic_pointer())
        self.assertEqual(
            (
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_counting_dynamic_calls"
                ),
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_counting_dynamic_maximum"
                ),
                self.get_uint(
                    "open_cfw_test_cmsis_semaphore_counting_dynamic_initial"
                ),
            ),
            (1, 7, 3),
        )

    def test_irq_and_scheduler_policy_matrix(self) -> None:
        cases = [
            (1, 2, 1, 1, False, (1, 0, 0, 0)),
            (0, 1, 1, 1, True, (1, 1, 0, 0)),
            (0, 0, 0, 0, True, (1, 1, 1, 1)),
            (0, 2, 1, 0, False, (1, 1, 1, 0)),
            (0, 2, 0, 1, False, (1, 1, 1, 1)),
            (0, 2, 0, 0, True, (1, 1, 1, 1)),
        ]
        for ipsr, state, primask, basepri, allowed, reads in cases:
            with self.subTest(
                ipsr=ipsr,
                state=state,
                primask=primask,
                basepri=basepri,
            ):
                self.reset()
                self.set_uint(
                    "open_cfw_test_cmsis_semaphore_ipsr",
                    ipsr,
                )
                self.set_int(
                    "open_cfw_test_cmsis_semaphore_scheduler_state",
                    state,
                )
                self.set_uint(
                    "open_cfw_test_cmsis_semaphore_primask",
                    primask,
                )
                self.set_uint(
                    "open_cfw_test_cmsis_semaphore_basepri",
                    basepri,
                )
                result = self.call(3, 1, 0, 0, 0, 0)
                self.assertEqual(
                    result,
                    self.dynamic_pointer() if allowed else 0,
                )
                self.assertEqual(
                    (
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_ipsr_reads"
                        ),
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_scheduler_calls"
                        ),
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_primask_reads"
                        ),
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_basepri_reads"
                        ),
                    ),
                    reads,
                )

    def test_binary_give_failure_deletes_and_nulls_handle(self) -> None:
        for provide_attr, provide_cb, cb_size in (
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 80),
        ):
            with self.subTest(
                provide_attr=provide_attr,
                provide_cb=provide_cb,
            ):
                self.reset()
                self.set_int(
                    "open_cfw_test_cmsis_semaphore_give_result",
                    0,
                )
                result = self.call(
                    1,
                    1,
                    provide_attr,
                    provide_cb,
                    cb_size,
                    1,
                )
                expected_handle = (
                    self.control_pointer()
                    if provide_attr and provide_cb
                    else self.dynamic_pointer()
                )
                self.assertEqual(result, 0)
                self.assertEqual(
                    (
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_give_calls"
                        ),
                        self.get_pointer(
                            "open_cfw_test_cmsis_semaphore_give_queue"
                        ),
                        self.get_pointer(
                            "open_cfw_test_cmsis_semaphore_give_item"
                        ),
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_give_ticks"
                        ),
                        self.get_int(
                            "open_cfw_test_cmsis_semaphore_give_position"
                        ),
                        self.get_uint(
                            "open_cfw_test_cmsis_semaphore_delete_calls"
                        ),
                        self.get_pointer(
                            "open_cfw_test_cmsis_semaphore_delete_queue"
                        ),
                    ),
                    (1, expected_handle, 0, 0, 0, 1, expected_handle),
                )

    def test_exhaustive_attributes_counts_failures_and_give_oracle(
        self,
    ) -> None:
        values = (0, 1, 2, 0xFFFFFFFF)
        sizes = (0, 79, 80, 0xFFFFFFFF)
        for maximum_count in values:
            for initial_count in values:
                for provide_attr in (False, True):
                    for provide_cb in (False, True):
                        for cb_size in sizes:
                            for provide_name in (False, True):
                                for creator_success in (False, True):
                                    for give_success in (False, True):
                                        inputs = (
                                            maximum_count,
                                            initial_count,
                                            provide_attr,
                                            provide_cb,
                                            cb_size,
                                            provide_name,
                                            creator_success,
                                            give_success,
                                        )
                                        self.reset()
                                        for name in (
                                            "binary_static_success",
                                            "binary_dynamic_success",
                                            "counting_static_success",
                                            "counting_dynamic_success",
                                        ):
                                            self.set_uint(
                                                "open_cfw_test_cmsis_"
                                                f"semaphore_{name}",
                                                int(creator_success),
                                            )
                                        self.set_int(
                                            "open_cfw_test_cmsis_"
                                            "semaphore_give_result",
                                            int(give_success),
                                        )

                                        result = self.call(
                                            maximum_count,
                                            initial_count,
                                            int(provide_attr),
                                            int(provide_cb),
                                            cb_size,
                                            int(provide_name),
                                        )
                                        route = expected_route(
                                            maximum_count,
                                            initial_count,
                                            provide_attr,
                                            provide_cb,
                                            cb_size,
                                        )
                                        expected_calls = {
                                            "binary_static": (1, 0, 0, 0),
                                            "binary_dynamic": (0, 1, 0, 0),
                                            "counting_static": (0, 0, 1, 0),
                                            "counting_dynamic": (0, 0, 0, 1),
                                            "none": (0, 0, 0, 0),
                                        }[route]
                                        observed_calls = (
                                            self.get_uint(
                                                "open_cfw_test_cmsis_"
                                                "semaphore_binary_static_"
                                                "calls"
                                            ),
                                            self.get_uint(
                                                "open_cfw_test_cmsis_"
                                                "semaphore_binary_dynamic_"
                                                "calls"
                                            ),
                                            self.get_uint(
                                                "open_cfw_test_cmsis_"
                                                "semaphore_counting_static_"
                                                "calls"
                                            ),
                                            self.get_uint(
                                                "open_cfw_test_cmsis_"
                                                "semaphore_counting_dynamic_"
                                                "calls"
                                            ),
                                        )
                                        self.assertEqual(
                                            observed_calls,
                                            expected_calls,
                                            inputs,
                                        )

                                        expected_pointer = (
                                            self.control_pointer()
                                            if route.endswith("_static")
                                            else self.dynamic_pointer()
                                        )
                                        if (
                                            route == "none"
                                            or not creator_success
                                        ):
                                            expected_result = 0
                                            expected_give = 0
                                            expected_delete = 0
                                        elif (
                                            route.startswith("binary")
                                            and initial_count != 0
                                        ):
                                            expected_give = 1
                                            expected_delete = int(
                                                not give_success
                                            )
                                            expected_result = (
                                                expected_pointer
                                                if give_success
                                                else 0
                                            )
                                        else:
                                            expected_result = expected_pointer
                                            expected_give = 0
                                            expected_delete = 0

                                        self.assertEqual(
                                            (
                                                result,
                                                self.get_uint(
                                                    "open_cfw_test_cmsis_"
                                                    "semaphore_give_calls"
                                                ),
                                                self.get_uint(
                                                    "open_cfw_test_cmsis_"
                                                    "semaphore_delete_calls"
                                                ),
                                            ),
                                            (
                                                expected_result,
                                                expected_give,
                                                expected_delete,
                                            ),
                                            inputs,
                                        )

                                        if route == "binary_static":
                                            self.assertEqual(
                                                (
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_static_length"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_static_"
                                                        "item_size"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_static_type"
                                                    ),
                                                    self.get_pointer(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_static_"
                                                        "storage"
                                                    ),
                                                    self.get_pointer(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_static_"
                                                        "control"
                                                    ),
                                                ),
                                                (
                                                    1,
                                                    0,
                                                    3,
                                                    0,
                                                    self.control_pointer(),
                                                ),
                                                inputs,
                                            )
                                        elif route == "binary_dynamic":
                                            self.assertEqual(
                                                (
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_dynamic_"
                                                        "length"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_dynamic_"
                                                        "item_size"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "binary_dynamic_type"
                                                    ),
                                                ),
                                                (1, 0, 3),
                                                inputs,
                                            )
                                        elif route == "counting_static":
                                            self.assertEqual(
                                                (
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "counting_static_"
                                                        "maximum"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "counting_static_"
                                                        "initial"
                                                    ),
                                                    self.get_pointer(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "counting_static_"
                                                        "control"
                                                    ),
                                                ),
                                                (
                                                    maximum_count,
                                                    initial_count,
                                                    self.control_pointer(),
                                                ),
                                                inputs,
                                            )
                                        elif route == "counting_dynamic":
                                            self.assertEqual(
                                                (
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "counting_dynamic_"
                                                        "maximum"
                                                    ),
                                                    self.get_uint(
                                                        "open_cfw_test_"
                                                        "cmsis_semaphore_"
                                                        "counting_dynamic_"
                                                        "initial"
                                                    ),
                                                ),
                                                (
                                                    maximum_count,
                                                    initial_count,
                                                ),
                                                inputs,
                                            )

    @_APPLE_ONLY
    def test_target_text_alignment_relocations_and_symbol_closure(self) -> None:
        self.assertEqual(self.target_compile.stderr, "")
        self.assertEqual(self.target_text, TARGET_BYTES)
        self.assertEqual(len(self.target_text), 178)
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
        self.assertEqual(int(function["section_index"]), int(text["index"]))
        self.assertEqual(int(function["value"]) & ~1, 0)
        self.assertEqual(int(function["size"]), 178)

        relocation_section = self.sections_by_name[
            f".rel.text.{TARGET_FUNCTION}"
        ]
        relocations = []
        for entry in range(
            int(relocation_section["offset"]),
            int(relocation_section["offset"]) +
            int(relocation_section["size"]),
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
            {name for _offset, _kind, name in TARGET_RELOCATIONS},
        )

        allocatable = [
            {
                "name": str(section["name"]),
                "size": int(section["size"]),
                "flags": int(section["flags"]),
            }
            for section in self.sections
            if int(section["flags"]) & 2 and int(section["size"])
        ]
        self.assertEqual(
            allocatable,
            [
                {
                    "name": f".text.{TARGET_FUNCTION}",
                    "size": 178,
                    "flags": 6,
                },
                {
                    "name": f".ARM.exidx.text.{TARGET_FUNCTION}",
                    "size": 8,
                    "flags": 130,
                },
            ],
        )

    @_APPLE_ONLY
    def test_production_source_closure_redirect_and_artifacts_are_exact(
        self,
    ) -> None:
        functions = self.current_report["overlay"]["functions"]
        base = int(
            self.current_report["overlay"]["overlay_runtime_address"]
        )
        self.assertEqual(
            {
                name: base + int(functions[name]["offset"])
                for name in CURRENT_DEPENDENCY_ADDRESSES
            },
            CURRENT_DEPENDENCY_ADDRESSES,
        )
        self.assertTrue(
            set(CURRENT_DEPENDENCY_ADDRESSES).issubset(
                set(self.current_config["functions"])
            )
        )

        self.assertTrue(QUEUE_DELETE_SOURCE.exists())
        queue_delete_source = QUEUE_DELETE_SOURCE.read_text()
        self.assertIn(
            "open_cfw_freertos_heap4_free",
            queue_delete_source,
        )
        self.assertEqual(
            self.current_config["functions"].count(
                "open_cfw_freertos_queue_delete"
            ),
            1,
        )
        self.assertEqual(
            self.current_config["functions"].count(TARGET_FUNCTION),
            1,
        )
        config_leaves = [
            item
            for item in self.current_config["relocated_leaves"]
            if item["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(config_leaves), 1)
        config_leaf = config_leaves[0]
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
                    "runtime_cmsis_semaphore_new.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
            },
        )
        self.assertEqual(
            config_leaf["expected"],
            {
                "size": 178,
                "sha256": PRODUCTION_SHA256,
                "alignment": 4,
                "offset": PRODUCTION_OFFSET,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        config_patches = [
            item
            for item in self.current_config["patch_sites"]
            if item["name"] == "replace_cmsis_semaphore_new"
        ]
        self.assertEqual(len(config_patches), 1)
        self.assertEqual(
            config_patches[0],
            {
                "name": "replace_cmsis_semaphore_new",
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

        report_leaves = [
            item
            for item in self.current_report["relocated_leaves"]
            if item["extraction"]["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(report_leaves), 1)
        report_leaf = report_leaves[0]
        self.assertEqual(
            report_leaf["placement"],
            {
                "alignment": 4,
                "offset": PRODUCTION_OFFSET,
                "padding_before": 2,
                "runtime_address": PRODUCTION_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B0358",
                "size": 178,
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
                    CURRENT_DEPENDENCY_ADDRESSES[symbol],
                )
                for offset, kind, symbol in TARGET_RELOCATIONS
            ],
        )
        self.assertEqual(
            self.current_report["overlay"]["functions"][TARGET_FUNCTION],
            {"offset": PRODUCTION_OFFSET, "size": 178},
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
                    PRODUCTION_OFFSET:PRODUCTION_OFFSET + 178
                ]
            ),
            PRODUCTION_SHA256,
        )
        patches = [
            item
            for item in self.current_report["overlay"]["patched_sites"]
            if item["name"] == "replace_cmsis_semaphore_new"
        ]
        self.assertEqual(len(patches), 1)
        patch = patches[0]
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["name"], "replace_cmsis_semaphore_new")
        self.assertEqual(patch["payload_offset"], 71_866)
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
                71_866:71_866 + len(STOCK_BYTES)
            ],
            replacement,
        )
        self.assertEqual(
            sha256(self.span(STOCK_START, STOCK_END)),
            STOCK_SHA256,
        )

        package = CURRENT_PACKAGE.read_bytes()
        self.assertEqual(
            (len(package), sha256(package)),
            (PRODUCTION_PACKAGE_SIZE, PRODUCTION_PACKAGE_SHA256),
        )
        flash_plan = CURRENT_FLASH_PLAN.read_bytes()
        self.assertEqual(
            sha256(flash_plan),
            PRODUCTION_FLASH_PLAN_SHA256,
        )
        parsed_plan = json.loads(flash_plan)
        self.assertEqual(len(parsed_plan["flash_regions"]), 1328)
        self.assertEqual(
            len(parsed_plan["unresolved_flash_regions"]),
            2,
        )
        source = SOURCE.read_text()
        self.assertIn(
            "#define vQueueDelete \\\n"
            "    open_cfw_freertos_queue_delete",
            source,
        )
        self.assertIn(
            "The production relocation closes cleanup through the "
            "source-owned",
            source,
        )


if __name__ == "__main__":
    unittest.main()
