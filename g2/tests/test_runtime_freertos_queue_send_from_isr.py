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
SOURCES = {
    "open_cfw_freertos_task_priority_disinherit": ROOT / "components/shared/freertos/runtime_freertos_task_priority_disinherit.c",
    "open_cfw_freertos_queue_copy_data_to_queue": ROOT / "components/shared/freertos/runtime_freertos_queue_copy_data_to_queue.c",
    "open_cfw_freertos_queue_generic_send_from_isr": ROOT / "components/shared/freertos/runtime_freertos_queue_generic_send_from_isr.c",
}
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_queue_send_from_isr_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


class RuntimeFreeRTOSQueueSendFromISRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("send.dylib" if sys.platform == "darwin" else "send.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_send_isr_host_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_send_isr_host_set_write_offset.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_set_read_offset.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_set_waiters.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_send.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_send_isr_host_send.restype = ctypes.c_int32
        cls.lib.open_cfw_send_isr_host_send_null.restype = ctypes.c_int32
        cls.lib.open_cfw_send_isr_host_priority_reset.argtypes = [ctypes.c_uint32] * 5
        cls.lib.open_cfw_send_isr_host_disinherit.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_disinherit.restype = ctypes.c_int32
        cls.lib.open_cfw_send_isr_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_get.restype = ctypes.c_uint32
        cls.lib.open_cfw_send_isr_host_storage.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_send_isr_host_storage.restype = ctypes.c_uint32

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.sections = {}
        cls.relocations = {}
        for function, source in SOURCES.items():
            target = temporary / f"{function}.o"
            subprocess.run([clang, *FLAGS, "-c", str(source), "-o", str(target)], check=True, capture_output=True, text=True)
            data, sections = apollo_overlay.parse_elf32(target)
            section = apollo_overlay.section_named(sections, f".text.{function}")
            cls.sections[function] = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            relocations = []
            for relocation_section in sections:
                if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                    continue
                symbols = sections[int(relocation_section["link"])]
                strings_section = sections[int(symbols["link"])]
                strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
                names = [apollo_overlay.elf_string(strings, struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)[0], "symbol") for index in range(int(symbols["size"]) // 16)]
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                    relocations.append((offset, information & 0xFF, names[information >> 8]))
            cls.relocations[function] = relocations

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, messages=0, length=4, lock=-1, task_count=3, remove=0) -> None:
        self.lib.open_cfw_send_isr_host_reset(messages, length, lock, task_count, remove)

    def get(self, selector: int) -> int:
        return self.lib.open_cfw_send_isr_host_get(selector)

    def test_sources_fixture_stock_target_and_relocations_are_pinned(self) -> None:
        source_pins = {
            "open_cfw_freertos_task_priority_disinherit": (5453, "b997d34508d2bfe6ad94cd59aefd7500ca6672ccc19759431d0219413e39e63a"),
            "open_cfw_freertos_queue_copy_data_to_queue": (2306, "eefe7aa38e547f3883adcab60b3cae91f0fdabcdebdc03f4533c56b2b53cffe8"),
            "open_cfw_freertos_queue_generic_send_from_isr": (3515, "df98fc66bc39269543638d9650c81b0ff592d698e05107235d6bc3bdfe6e6c0b"),
        }
        for function, source in SOURCES.items():
            self.assertEqual((source.stat().st_size, hashlib.sha256(source.read_bytes()).hexdigest()), source_pins[function])
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (9115, "9d847414195eec10123985d2ad4bafacf8a04c0e058d8fdb1d89d5db52f6eab9"))
        image = OFFICIAL.read_bytes()[32:]
        for start, end, digest in (
            (0x00441952, 0x00441A42, "09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08"),
            (0x00441ED8, 0x00441F5E, "35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36"),
            (0x0045596E, 0x00455A12, "34e2c3a8b02daf3ea3f8d3d382ef3d802d48f4d65ee26fa0353d0faab51c7e93"),
        ):
            body = image[start - 0x00438000:end - 0x00438000]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, digest))
        target_pins = {
            "open_cfw_freertos_task_priority_disinherit": (134, "f875b5c912b6de4eba5bec143deae0181a5ee06a52d2fa701197311c7d2ebd7a", [(22, 10, "ulSetInterruptMask"), (74, 10, "open_cfw_freertos_list_remove"), (112, 10, "open_cfw_freertos_list_insert_end"), (120, 10, "ulSetInterruptMask")]),
            "open_cfw_freertos_queue_copy_data_to_queue": (124, "57ae8ad8c06c3ef15229222e1ad66c2db9cf59d3d5124805f56813544f702ed4", [(18, 10, "__aeabi_memcpy"), (82, 10, "open_cfw_freertos_task_priority_disinherit"), (94, 10, "__aeabi_memcpy")]),
            "open_cfw_freertos_queue_generic_send_from_isr": (228, "bd6965a32d0288ddb4ea59a65da279357e3697852da9bfca51275f0a9ba7a5a3", [(114, 10, "open_cfw_freertos_queue_copy_data_to_queue"), (174, 10, "open_cfw_freertos_task_remove_from_event_list")]),
        }
        for function, (size, digest, relocations) in target_pins.items():
            self.assertEqual((len(self.sections[function]), hashlib.sha256(self.sections[function]).hexdigest(), self.relocations[function]), (size, digest, relocations))

    def test_send_to_back_advances_wraps_and_counts(self) -> None:
        self.reset()
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 1, 0), 1)
        self.assertEqual((self.get(0), self.get(1), self.get(7), self.get(11)), (1, 4, 1, 1))
        self.assertEqual([self.lib.open_cfw_send_isr_host_storage(i) for i in range(4)], [0xA0, 0xA1, 0xA2, 0xA3])
        self.reset()
        self.lib.open_cfw_send_isr_host_set_write_offset(12)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 0), 1)
        self.assertEqual(self.get(1), 0)

    def test_overwrite_full_queue_preserves_count_and_moves_read_pointer(self) -> None:
        self.reset(messages=1, length=1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 2), 1)
        self.assertEqual((self.get(0), self.get(2), self.get(7)), (1, 12, 1))
        self.assertEqual([self.lib.open_cfw_send_isr_host_storage(i) for i in range(4)], [0xA0, 0xA1, 0xA2, 0xA3])

    def test_full_waiter_wake_and_locked_saturation_paths(self) -> None:
        self.reset(messages=4, length=4)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 0), 0)
        self.assertEqual((self.get(7), self.get(11), self.get(12), self.get(5), self.get(6)), (0, 0, 1, 1, 1))
        self.reset(remove=1)
        self.lib.open_cfw_send_isr_host_set_waiters(1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 1, 0), 1)
        self.assertEqual((self.get(4), self.get(8)), (1, 1))
        self.reset(lock=0, task_count=3)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 0), 1)
        self.assertEqual(self.get(3), 1)
        self.reset(lock=2, task_count=2)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 0), 1)
        self.assertEqual(self.get(3), 2)

    def test_assertion_contracts_precede_unmasking(self) -> None:
        self.reset()
        self.assertEqual(self.lib.open_cfw_send_isr_host_send_null(), ctypes.c_int32(0x80000000).value)
        self.assertEqual(self.get(6), 0)
        self.reset()
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(0, 0, 0), ctypes.c_int32(0x80000000).value)
        self.reset(length=2)
        self.assertEqual(self.lib.open_cfw_send_isr_host_send(1, 0, 2), ctypes.c_int32(0x80000000).value)

    def test_priority_disinherit_matches_v1051_paths(self) -> None:
        self.reset()
        self.lib.open_cfw_send_isr_host_priority_reset(10, 3, 1, 2, 1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(1), 1)
        self.assertEqual((self.get(13), self.get(14), self.get(15), self.get(16)), (3, 53, 0, 3))
        self.assertEqual((self.get(8), self.get(9), self.get(17), self.get(18), self.get(19)), (1, 1, 1, 1, 1))
        self.lib.open_cfw_send_isr_host_priority_reset(10, 3, 2, 12, 1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(1), 0)
        self.assertEqual((self.get(13), self.get(15), self.get(8), self.get(9)), (10, 1, 0, 0))
        self.lib.open_cfw_send_isr_host_priority_reset(3, 3, 1, 12, 1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(1), 0)
        self.assertEqual((self.get(13), self.get(15)), (3, 0))
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(0), 0)

    def test_priority_disinherit_asserts_current_holder_and_mutex_count(self) -> None:
        self.reset()
        self.lib.open_cfw_send_isr_host_priority_reset(10, 3, 1, 0, 0)
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(1), ctypes.c_int32(0x80000000).value)
        self.lib.open_cfw_send_isr_host_priority_reset(10, 3, 0, 0, 1)
        self.assertEqual(self.lib.open_cfw_send_isr_host_disinherit(1), ctypes.c_int32(0x80000000).value)

    def test_production_overlay_and_manifest_admit_strict_send_closure(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        names = set(SOURCES)
        leaves = {item["function"]: item for item in config["relocated_leaves"] if item["function"] in names}
        self.assertEqual(set(leaves), names)
        apple = {
            "open_cfw_freertos_task_priority_disinherit": (134, "256082f997014120f12741e78e78da32adcfd165b8e2804c219c476ab847e030", 133796),
            "open_cfw_freertos_queue_copy_data_to_queue": (124, "a923f035bc0c9dcec275d432e44f3f6d2cb0e37c5b3a47b5965a8954f3e5eb07", 133932),
            "open_cfw_freertos_queue_generic_send_from_isr": (228, "8e9a44e2742b598558b7b2c86543c3f306734d6ad4160e45177fb48eb96928d0", 134056),
        }
        linux = {
            "open_cfw_freertos_task_priority_disinherit": (134, "33cdbf7dc5a2821562bd6a9fb8a8e736744d8c7e6861f26216c9531e83d5ea8d", 135672),
            "open_cfw_freertos_queue_copy_data_to_queue": (124, "061dca2d62ba0db1fd8ea7c68c762c201663a4a2aa489a2e1c8b8d01919e520b", 135808),
            "open_cfw_freertos_queue_generic_send_from_isr": (228, "953ada83ada93c6d94177180860238a49b709aca3d6097657c3a6f150cc3944e", 135932),
        }
        for function, leaf in leaves.items():
            self.assertEqual(leaf["source"]["upstream_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
            self.assertEqual((leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["offset"]), apple[function])
            profile = leaf["toolchain_profiles"]["linux-clang"]["expected"]
            self.assertEqual((profile["size"], profile["sha256"], profile["offset"]), linux[function])
        patches = {item["target_function"]: item["runtime_address"] for item in config["patch_sites"] if item["target_function"] in names}
        self.assertEqual(patches, {
            "open_cfw_freertos_task_priority_disinherit": 0x0045596E,
            "open_cfw_freertos_queue_copy_data_to_queue": 0x00441ED8,
            "open_cfw_freertos_queue_generic_send_from_isr": 0x00441952,
        })
        self.assertEqual((config["expected"]["overlay_size"], config["expected"]["component_size"]), (174816, 3698212))
        self.assertEqual((config["toolchain_profiles"]["linux-clang"]["expected"]["overlay_size"], config["toolchain_profiles"]["linux-clang"]["expected"]["component_size"]), (145208, 3668604))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual((main["provider"]["size"], main["provider"]["profiles"]["linux-clang"]["size"]), (3698212, 3668604))
        self.assertEqual((manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]), (4476706, "26bf3d84c06987461340f6af8773e0ae59bd3ae75c630c00a2158fe3a4945058"))
        self.assertEqual((manifest["package"]["profiles"]["linux-clang"]["expected_size"], manifest["package"]["profiles"]["linux-clang"]["expected_sha256"]), (4447098, "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e"))


if __name__ == "__main__":
    unittest.main()
