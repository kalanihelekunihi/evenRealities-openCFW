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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_queue_receive_from_isr.c"
COPY_SOURCE = ROOT / "components/shared/freertos/runtime_freertos_queue_copy_data_from_queue.c"
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_queue_receive_from_isr_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


class RuntimeFreeRTOSQueueReceiveFromISRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("queue_rx.dylib" if sys.platform == "darwin" else "queue_rx.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_queue_rx_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_queue_rx_host_set_read_offset.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_queue_rx_host_set_waiters.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_queue_rx_host_execute.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_queue_rx_host_execute.restype = ctypes.c_int32
        cls.lib.open_cfw_queue_rx_host_execute_null_queue.restype = ctypes.c_int32
        cls.lib.open_cfw_queue_rx_host_get_output.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_queue_rx_host_get_output.restype = ctypes.c_uint32
        cls.getters = {}
        for name in (
            "read_offset", "messages", "receive_lock", "flag", "set_mask_calls",
            "clear_mask_calls", "clear_mask_argument", "task_count_calls",
            "remove_calls", "copy_calls", "copy_size", "validate_calls",
            "trace_calls", "trace_failed_calls", "assert_calls",
        ):
            function = getattr(cls.lib, f"open_cfw_queue_rx_host_get_{name}")
            function.restype = ctypes.c_int32 if name in ("receive_lock", "flag") else ctypes.c_uint32
            cls.getters[name] = function

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.target_sections = {}
        cls.target_relocations = {}
        for function, source in (
            ("open_cfw_freertos_queue_copy_data_from_queue", COPY_SOURCE),
            ("open_cfw_freertos_queue_receive_from_isr", SOURCE),
        ):
            target = temporary / f"{function}.o"
            subprocess.run([clang, *TARGET_FLAGS, "-c", str(source), "-o", str(target)], check=True, capture_output=True, text=True)
            data, sections = apollo_overlay.parse_elf32(target)
            section = apollo_overlay.section_named(sections, f".text.{function}")
            cls.target_sections[function] = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            relocations = []
            for relocation_section in sections:
                if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                    continue
                symbols = sections[int(relocation_section["link"])]
                strings_section = sections[int(symbols["link"])]
                strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
                names = [
                    apollo_overlay.elf_string(
                        strings,
                        struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)[0],
                        "symbol",
                    )
                    for index in range(int(symbols["size"]) // 16)
                ]
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                    relocations.append((offset, information & 0xFF, names[information >> 8]))
            cls.target_relocations[function] = relocations

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, messages=1, item_size=4, receive_lock=-1, task_count=3, remove_result=0) -> None:
        self.lib.open_cfw_queue_rx_host_reset(messages, item_size, receive_lock, task_count, remove_result)

    def get(self, name: str) -> int:
        return self.getters[name]()

    def test_source_fixture_stock_target_and_relocation_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (4620, "5a9babbd2715ff4ffaf20cd31105dcc2874ec2adad54d00e2964a33f6d66e569"))
        self.assertEqual((COPY_SOURCE.stat().st_size, hashlib.sha256(COPY_SOURCE.read_bytes()).hexdigest()), (2095, "dcd4d015d9e71ebf88f6c084887c534af62455262523044927a9bd7e25220d9c"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (9043, "ac8d696c2180767836c6d1c21212911213592d8456e99d04ea6f1d25aeb2cf1d"))
        image = OFFICIAL.read_bytes()[32:]
        for start, end, expected in (
            (0x00441DA6, 0x00441E66, "cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4"),
            (0x00441F5E, 0x00441F88, "d788663fd093a939ebf3f23edb08bf534bda42f1c31a181b9e7f20347db229cc"),
        ):
            stock = image[start - 0x00438000:end - 0x00438000]
            self.assertEqual((len(stock), hashlib.sha256(stock).hexdigest()), (end - start, expected))
        pins = {
            "open_cfw_freertos_queue_copy_data_from_queue": (34, "253814d0f37d21183c8525132092277d91268dce923771a5fc3a80b32249d4bb", [(30, 30, "__aeabi_memcpy")]),
            "open_cfw_freertos_queue_receive_from_isr": (208, "1215747b197736125699ec2fa0b3e421d6fa1dfe89d31e07644c46d8f0b4de55", [(44, 10, "open_cfw_freertos_queue_copy_data_from_queue"), (150, 10, "open_cfw_freertos_task_remove_from_event_list")]),
        }
        for function, (size, digest, relocations) in pins.items():
            body = self.target_sections[function]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest(), self.target_relocations[function]), (size, digest, relocations))

    def test_data_receive_advances_and_wraps_read_pointer(self) -> None:
        self.reset(messages=2, item_size=4)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(1, 0, 0), 1)
        self.assertEqual((self.get("messages"), self.get("read_offset"), self.get("copy_calls"), self.get("copy_size")), (1, 4, 1, 4))
        self.assertEqual([self.lib.open_cfw_queue_rx_host_get_output(i) for i in range(4)], [0x44, 0x45, 0x46, 0x47])
        self.reset(messages=1, item_size=4)
        self.lib.open_cfw_queue_rx_host_set_read_offset(28)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(1, 0, 0), 1)
        self.assertEqual(self.get("read_offset"), 0)
        self.assertEqual([self.lib.open_cfw_queue_rx_host_get_output(i) for i in range(4)], [0x40, 0x41, 0x42, 0x43])

    def test_empty_and_semaphore_paths_preserve_mask_and_trace_semantics(self) -> None:
        self.reset(messages=0, item_size=4)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(1, 1, 7), 0)
        self.assertEqual((self.get("messages"), self.get("copy_calls"), self.get("trace_calls"), self.get("trace_failed_calls")), (0, 0, 0, 1))
        self.assertEqual((self.get("validate_calls"), self.get("set_mask_calls"), self.get("clear_mask_calls"), self.get("clear_mask_argument"), self.get("flag")), (1, 1, 1, 0x5A, 7))
        self.reset(messages=1, item_size=0)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(0, 0, 0), 1)
        self.assertEqual((self.get("messages"), self.get("copy_calls"), self.get("trace_calls")), (0, 0, 1))

    def test_unlocked_waiter_wake_is_optional_and_return_driven(self) -> None:
        for remove_result, use_flag, initial, expected in ((0, 1, 9, 9), (1, 1, 9, 1), (1, 0, 9, 9)):
            with self.subTest(remove_result=remove_result, use_flag=use_flag):
                self.reset(messages=1, item_size=0, remove_result=remove_result)
                self.lib.open_cfw_queue_rx_host_set_waiters(1)
                self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(0, use_flag, initial), 1)
                self.assertEqual((self.get("remove_calls"), self.get("flag")), (1, expected))

    def test_locked_queue_saturates_against_task_count(self) -> None:
        for lock, task_count, expected, loads in ((0, 3, 1, 1), (2, 2, 2, 1), (-2, 3, -2, 1)):
            with self.subTest(lock=lock, task_count=task_count):
                self.reset(messages=1, item_size=0, receive_lock=lock, task_count=task_count)
                self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(0, 0, 0), 1)
                self.assertEqual((self.get("receive_lock"), self.get("task_count_calls"), self.get("remove_calls")), (expected, loads, 0))

    def test_assertion_contracts_fail_before_unmasking(self) -> None:
        self.reset()
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute_null_queue(), ctypes.c_int32(0x80000000).value)
        self.assertEqual((self.get("assert_calls"), self.get("clear_mask_calls")), (1, 0))
        self.reset(item_size=4)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(0, 0, 0), ctypes.c_int32(0x80000000).value)
        self.assertEqual((self.get("assert_calls"), self.get("clear_mask_calls")), (1, 0))
        self.reset(item_size=0, receive_lock=127, task_count=128)
        self.assertEqual(self.lib.open_cfw_queue_rx_host_execute(0, 0, 0), ctypes.c_int32(0x80000000).value)
        self.assertEqual((self.get("messages"), self.get("assert_calls"), self.get("clear_mask_calls")), (0, 1, 0))

    def test_production_overlay_and_manifest_admit_the_complete_read_side_closure(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in {
                "open_cfw_freertos_queue_copy_data_from_queue",
                "open_cfw_freertos_queue_receive_from_isr",
            }
        }
        self.assertEqual(set(leaves), {
            "open_cfw_freertos_queue_copy_data_from_queue",
            "open_cfw_freertos_queue_receive_from_isr",
        })
        expected = {
            "open_cfw_freertos_queue_copy_data_from_queue": (
                COPY_SOURCE, 34,
                "30b597cf19f8b8b364291fabcd43c5d390087d197966a4f475964df42c9c9e5e",
                133048, 32,
                "de66629599322e68a02957c32bb6e62df66a6979596d118c0071a382459e1800",
                134924,
            ),
            "open_cfw_freertos_queue_receive_from_isr": (
                SOURCE, 208,
                "be7a8c14921ca2d9df57abd9a2d952b9f35961f870eb8e2df8a9828ad70bec93",
                133084, 208,
                "65324127fd078cdfa44390b23163255636c18a72263534711f25569c8986c739",
                134956,
            ),
        }
        for function, (source, size, digest, offset, linux_size, linux_digest, linux_offset) in expected.items():
            leaf = leaves[function]
            self.assertEqual(leaf["source"]["path"], source.relative_to(ROOT).as_posix())
            self.assertEqual(leaf["source"]["upstream_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
            self.assertEqual((leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]), (size, digest, offset))
            linux = leaf["toolchain_profiles"]["linux-clang"]["expected"]
            self.assertEqual((linux["size"], linux["sha256"], linux["offset"]), (linux_size, linux_digest, linux_offset))
        patches = {
            item["target_function"]: item["runtime_address"]
            for item in config["patch_sites"]
            if item["target_function"] in leaves
        }
        self.assertEqual(patches, {
            "open_cfw_freertos_queue_copy_data_from_queue": 0x00441F5E,
            "open_cfw_freertos_queue_receive_from_isr": 0x00441DA6,
        })
        self.assertEqual((config["expected"]["overlay_size"], config["expected"]["component_size"]), (147021, 3670417))
        self.assertEqual((config["toolchain_profiles"]["linux-clang"]["expected"]["overlay_size"], config["toolchain_profiles"]["linux-clang"]["expected"]["component_size"]), (144266, 3667662))

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = {item["name"]: item for item in main["regions"]}
        self.assertEqual((regions["apollo_freertos_queue_copy_data_from_queue_source_leaf"]["file_offset"], regions["apollo_freertos_queue_copy_data_from_queue_source_leaf"]["size"], regions["apollo_freertos_queue_copy_data_from_queue_source_leaf"]["target_address"]), (3656444, 34, 8080092))
        self.assertEqual((regions["apollo_freertos_queue_receive_from_isr_source_leaf"]["file_offset"], regions["apollo_freertos_queue_receive_from_isr_source_leaf"]["size"], regions["apollo_freertos_queue_receive_from_isr_source_leaf"]["target_address"]), (3656480, 208, 8080128))
        self.assertEqual((main["provider"]["size"], main["provider"]["profiles"]["linux-clang"]["size"]), (3670417, 3667662))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]), (4448911, "21ba9d6c32c73f390fd68ee9ef2808ad01c7206d746e67eca9c755732b0a6605"))
        self.assertEqual((manifest["package"]["profiles"]["linux-clang"]["expected_size"], manifest["package"]["profiles"]["linux-clang"]["expected_sha256"]), (4446156, "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3"))


if __name__ == "__main__":
    unittest.main()
