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


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_sync_ops.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_sync_ops_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

STOCK = {
    "open_cfw_cmsis_mutex_acquire": (
        0x004497B6,
        0x0044981C,
        "86928d597f8f7b7f8f4519b40983a9384dfb72830fd2cec49809678bb1ff88a7",
    ),
    "open_cfw_cmsis_mutex_release": (
        0x0044981C,
        0x0044986E,
        "290de52cf203c2aaf8c554a686c675212c79382a696e46e0b70030363714eb71",
    ),
    "open_cfw_cmsis_semaphore_release": (
        0x004499B8,
        0x00449A0E,
        "5ff08a165bcf058ae1696528b092d64cbe7f6464b949763bc429597ad77b9d65",
    ),
}

TARGET = {
    "open_cfw_cmsis_mutex_acquire": (
        72,
        "7c6c82e72e3edd4f081b91722d4bdbf1a8972867e25a58f23360fc4e0aa9b635",
        [
            (6, 10, "open_cfw_cmsis_irq_context"),
            (32, 10, "open_cfw_freertos_queue_semaphore_take_upstream_candidate"),
            (46, 10, "open_cfw_freertos_queue_take_mutex_recursive"),
        ],
    ),
    "open_cfw_cmsis_mutex_release": (
        64,
        "495bd59cc9bd9361d84e1753467c90a81b09207976442fe1b7838e0bb2de9fe4",
        [
            (4, 10, "open_cfw_cmsis_irq_context"),
            (34, 10, "open_cfw_freertos_queue_generic_send"),
            (46, 10, "open_cfw_freertos_queue_give_mutex_recursive"),
        ],
    ),
    "open_cfw_cmsis_semaphore_release": (
        84,
        "993c1b45a01e4c08abd7e0bd5ca4b9b6103dd373e18adb24130a743f51ce5115",
        [
            (12, 10, "open_cfw_cmsis_irq_context"),
            (22, 10, "open_cfw_freertos_queue_give_from_isr"),
            (64, 10, "open_cfw_freertos_queue_generic_send"),
        ],
    ),
}


class RuntimeCmsisSyncOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / (
            "sync.dylib" if sys.platform == "darwin" else "sync.so"
        )
        command = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
            "-dynamiclib" if sys.platform == "darwin" else "-shared",
        ]
        if sys.platform != "darwin":
            command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))

        cls.acquire = cls.loaded.open_cfw_cmsis_mutex_acquire
        cls.acquire.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.acquire.restype = ctypes.c_int32
        cls.release = cls.loaded.open_cfw_cmsis_mutex_release
        cls.release.argtypes = [ctypes.c_void_p]
        cls.release.restype = ctypes.c_int32
        cls.semaphore_release = cls.loaded.open_cfw_cmsis_semaphore_release
        cls.semaphore_release.argtypes = [ctypes.c_void_p]
        cls.semaphore_release.restype = ctypes.c_int32

        cls.reset = cls.loaded.open_cfw_test_sync_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
        ]
        cls.accessors = {}
        for name in (
            "take_recursive_calls",
            "take_calls",
            "give_recursive_calls",
            "send_calls",
            "give_isr_calls",
            "pendsv_calls",
            "timeout",
        ):
            function = getattr(cls.loaded, f"open_cfw_test_sync_{name}")
            function.restype = ctypes.c_uint32
            cls.accessors[name] = function
        cls.handle = cls.loaded.open_cfw_test_sync_handle
        cls.handle.restype = ctypes.c_size_t

        target = temporary / "sync.o"
        flags = [
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
        subprocess.run(
            [clang, *flags, "-c", str(SOURCE), "-o", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(target)
        cls.target = {}
        for function in TARGET:
            section = apollo_overlay.section_named(
                sections, f".text.{function}"
            )
            start = int(section["offset"])
            body = data[start : start + int(section["size"])]
            relocations = []
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) != 9
                    or int(relocation_section["info"]) != int(section["index"])
                ):
                    continue
                symbols = sections[int(relocation_section["link"])]
                strings_section = sections[int(symbols["link"])]
                strings_start = int(strings_section["offset"])
                strings = data[
                    strings_start : strings_start + int(strings_section["size"])
                ]
                names = []
                for index in range(int(symbols["size"]) // 16):
                    fields = struct.unpack_from(
                        "<IIIBBH", data, int(symbols["offset"]) + index * 16
                    )
                    names.append(
                        apollo_overlay.elf_string(strings, fields[0], "symbol")
                    )
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(relocation_section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (offset, information & 0xFF, names[information >> 8])
                    )
            cls.target[function] = (body, relocations)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset_state(
        self,
        *,
        irq: int = 0,
        take_recursive: int = 1,
        take: int = 1,
        give_recursive: int = 1,
        send: int = 1,
        give_isr: int = 1,
        give_isr_yield: int = 0,
    ) -> None:
        self.reset(
            irq,
            take_recursive,
            take,
            give_recursive,
            send,
            give_isr,
            give_isr_yield,
        )

    def counts(self) -> tuple[int, ...]:
        return tuple(
            self.accessors[name]()
            for name in (
                "take_recursive_calls",
                "take_calls",
                "give_recursive_calls",
                "send_calls",
                "give_isr_calls",
                "pendsv_calls",
            )
        )

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (4750, "22946b1e56b4fbae249618c088d0566fb49e2a9eb6edefb0eca07c3e92ade951"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (3873, "b0ba9b3661adfe04355c50f588a05351338759ce6b40a7fa6f9fb2ed6961291e"),
        )
        image = OFFICIAL.read_bytes()[32:]
        for function, (start, end, stock_sha256) in STOCK.items():
            with self.subTest(function=function, kind="stock"):
                body = image[start - 0x00438000 : end - 0x00438000]
                self.assertEqual(len(body), end - start)
                self.assertEqual(hashlib.sha256(body).hexdigest(), stock_sha256)
            with self.subTest(function=function, kind="target"):
                body, relocations = self.target[function]
                size, sha256, expected_relocations = TARGET[function]
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, sha256))
                self.assertEqual(relocations, expected_relocations)

    def test_mutex_acquire_validation_routing_and_statuses(self) -> None:
        cases = [
            (1, 0x1235, 7, 1, 1, -6, (0, 0, 0, 0, 0, 0)),
            (0, 1, 7, 1, 1, -4, (0, 0, 0, 0, 0, 0)),
            (0, 0x1235, 7, 1, 1, 0, (1, 0, 0, 0, 0, 0)),
            (0, 0x1235, 7, 0, 1, -2, (1, 0, 0, 0, 0, 0)),
            (0, 0x1235, 0, 0, 1, -3, (1, 0, 0, 0, 0, 0)),
            (0, 0x1234, 7, 1, 1, 0, (0, 1, 0, 0, 0, 0)),
            (0, 0x1234, 7, 1, 0, -2, (0, 1, 0, 0, 0, 0)),
            (0, 0x1234, 0, 1, 0, -3, (0, 1, 0, 0, 0, 0)),
        ]
        for irq, handle, timeout, recursive_result, take_result, status, counts in cases:
            with self.subTest(irq=irq, handle=handle, timeout=timeout):
                self.reset_state(
                    irq=irq,
                    take_recursive=recursive_result,
                    take=take_result,
                )
                self.assertEqual(self.acquire(ctypes.c_void_p(handle), timeout), status)
                self.assertEqual(self.counts(), counts)
                if sum(counts):
                    self.assertEqual(self.handle(), handle & ~1)
                    self.assertEqual(self.accessors["timeout"](), timeout)

    def test_mutex_release_validation_routing_and_statuses(self) -> None:
        cases = [
            (1, 0x1235, 1, 1, -6, (0, 0, 0, 0, 0, 0)),
            (0, 1, 1, 1, -4, (0, 0, 0, 0, 0, 0)),
            (0, 0x1235, 1, 1, 0, (0, 0, 1, 0, 0, 0)),
            (0, 0x1235, 0, 1, -3, (0, 0, 1, 0, 0, 0)),
            (0, 0x1234, 1, 1, 0, (0, 0, 0, 1, 0, 0)),
            (0, 0x1234, 1, 0, -3, (0, 0, 0, 1, 0, 0)),
        ]
        for irq, handle, recursive_result, send_result, status, counts in cases:
            with self.subTest(irq=irq, handle=handle):
                self.reset_state(
                    irq=irq,
                    give_recursive=recursive_result,
                    send=send_result,
                )
                self.assertEqual(self.release(ctypes.c_void_p(handle)), status)
                self.assertEqual(self.counts(), counts)
                if sum(counts):
                    self.assertEqual(self.handle(), handle & ~1)

    def test_semaphore_release_task_and_isr_paths(self) -> None:
        cases = [
            (0, 0, 1, 0, 1, -4, (0, 0, 0, 0, 0, 0)),
            (0, 0x1234, 1, 0, 1, 0, (0, 0, 0, 1, 0, 0)),
            (0, 0x1234, 0, 0, 1, -3, (0, 0, 0, 1, 0, 0)),
            (1, 0x1234, 1, 0, 0, -3, (0, 0, 0, 0, 1, 0)),
            (1, 0x1234, 1, 0, 1, 0, (0, 0, 0, 0, 1, 0)),
            (1, 0x1234, 1, 1, 1, 0, (0, 0, 0, 0, 1, 1)),
        ]
        for irq, handle, send_result, yield_value, isr_result, status, counts in cases:
            with self.subTest(irq=irq, handle=handle, yield_value=yield_value):
                self.reset_state(
                    irq=irq,
                    send=send_result,
                    give_isr=isr_result,
                    give_isr_yield=yield_value,
                )
                self.assertEqual(self.semaphore_release(ctypes.c_void_p(handle)), status)
                self.assertEqual(self.counts(), counts)
                if sum(counts):
                    self.assertEqual(self.handle(), handle)

    def test_production_registration_is_atomic(self) -> None:
        config = json.loads(
            (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
        )
        manifest = json.loads(
            (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text()
        )
        expected = {
            "open_cfw_cmsis_mutex_acquire": (
                "bfc87b7e4a95d7b265d81eddc03d89a6e4cc4052982eff5ff786360e7c9ff4a1",
                "932948962def396e1400fdeb9b2ef1136a0d0192a4317f527a990276d57ef37e",
                "apollo_cmsis_mutex_acquire_source_leaf",
            ),
            "open_cfw_cmsis_mutex_release": (
                "5e9a3f3fd88c0f312460d01f66bf4a538d12dbf29bd1dbf4ef965da6065a85b8",
                "dffdf9b597ac04a1b8a7077ae4b01768ded168469ee8ec09fd2d516bef308de0",
                "apollo_cmsis_mutex_release_source_leaf",
            ),
            "open_cfw_cmsis_semaphore_release": (
                "24ea1eb79a6592da1017624c46c3b51062619099a1e0f715f3a0d31d4fd5cd07",
                "819ac2d388226f988c03ae3bcafe4b46e455fa4d02fc2a5eca5af2349ccd7c7c",
                "apollo_cmsis_semaphore_release_source_leaf",
            ),
        }
        leaves = {leaf["function"]: leaf for leaf in config["relocated_leaves"]}
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        for function, (apple_sha256, linux_sha256, region_name) in expected.items():
            with self.subTest(function=function):
                leaf = leaves[function]
                self.assertEqual(leaf["expected"]["sha256"], apple_sha256)
                self.assertEqual(
                    leaf["toolchain_profiles"]["linux-clang"]["expected"]["sha256"],
                    linux_sha256,
                )
                self.assertEqual(
                    sum(site["target_function"] == function for site in config["patch_sites"]),
                    1,
                )
                self.assertEqual(
                    sum(region["name"] == region_name for region in regions),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
