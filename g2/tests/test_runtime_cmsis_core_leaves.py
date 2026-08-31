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
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_cmsis_core_leaves.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_cmsis_core_leaves_host.c"
UPSTREAM = (
    ROOT
    / "third_party"
    / "cmsis-freertos"
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Source"
    / "cmsis_os2.c"
)
VERIFIER = ROOT / "third_party" / "cmsis-freertos" / "verify_snapshot.py"
CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

BASE = 0x00438000
STOCK = {
    "open_cfw_cmsis_irq_context": (
        0x0044900E,
        0x0044903C,
        "702b19799a5ff8295597cd1b903ba5a5b6f9db91d872fdf311c9221c44660f33",
    ),
    "open_cfw_cmsis_kernel_get_tick_count": (
        0x004490CC,
        0x004490E2,
        "e71b740a75cc5b6be604febe03034833fd10def82df65b66e453bcca1402564d",
    ),
    "open_cfw_cmsis_thread_get_id": (
        0x004491AA,
        0x004491B2,
        "a6178d2c6ee09a3f8dd462980fd9a198af2b57d83776da3d9c7914b5dd5959c6",
    ),
    "open_cfw_cmsis_message_queue_get_capacity": (
        0x00449BBC,
        0x00449BC8,
        "9f79c94a7cfd4e3f855e902cf158167326d290169a09053a13c5a88775e88d32",
    ),
}
LEAVES = {
    "IRQ_CONTEXT": (
        "open_cfw_cmsis_irq_context",
        46,
        "b40be5ceee29cd41d4ce92600914b8ab0fae47e8fdcc632e5ee821b39967da44",
        [(12, 10, "open_cfw_freertos_task_get_scheduler_state")],
    ),
    "KERNEL_TICK": (
        "open_cfw_cmsis_kernel_get_tick_count",
        24,
        "563b6ab3fb7c401ccbd66a3b12963c9134ec11f7c148a149ae70f20f74d1da23",
        [
            (2, 10, "open_cfw_cmsis_irq_context"),
            (12, 30, "open_cfw_freertos_task_get_tick_count_from_isr"),
            (20, 30, "open_cfw_freertos_task_get_tick_count"),
        ],
    ),
    "THREAD_ID": (
        "open_cfw_cmsis_thread_get_id",
        4,
        "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f",
        [(0, 30, "open_cfw_freertos_task_get_current_task_handle")],
    ),
    "QUEUE_CAPACITY": (
        "open_cfw_cmsis_message_queue_get_capacity",
        10,
        "a202d458704814857c225bdfe44ce4f5e585c1af08925b3a3de5daf49ea94960",
        [],
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


class RuntimeCmsisCoreLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / (
            "runtime_cmsis_core_leaves.dylib"
            if sys.platform == "darwin"
            else "runtime_cmsis_core_leaves.so"
        )
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))

        cls.set_context = cls.loaded.open_cfw_test_cmsis_set_context
        cls.set_context.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int32,
        ]
        cls.set_ticks = cls.loaded.open_cfw_test_cmsis_set_ticks
        cls.set_ticks.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_current = cls.loaded.open_cfw_test_cmsis_set_current_task
        cls.set_current.argtypes = [ctypes.c_size_t]
        cls.irq_context = cls.loaded.open_cfw_cmsis_irq_context
        cls.irq_context.restype = ctypes.c_uint32
        cls.tick_count = cls.loaded.open_cfw_cmsis_kernel_get_tick_count
        cls.tick_count.restype = ctypes.c_uint32
        cls.thread_id = cls.loaded.open_cfw_cmsis_thread_get_id
        cls.thread_id.restype = ctypes.c_void_p
        cls.capacity = cls.loaded.open_cfw_cmsis_message_queue_get_capacity
        cls.capacity.argtypes = [ctypes.c_void_p]
        cls.capacity.restype = ctypes.c_uint32

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.target_results = {}
        for leaf, expected in LEAVES.items():
            target_object = temporary / f"{leaf}.o"
            subprocess.run(
                [
                    clang,
                    *TARGET_FLAGS,
                    "-DOPEN_CFW_CMSIS_CORE_BUILD_LEAF",
                    f"-DOPEN_CFW_CMSIS_CORE_LEAF_{leaf}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            data, sections = apollo_overlay.parse_elf32(target_object)
            section = apollo_overlay.section_named(
                sections, f".text.{expected[0]}"
            )
            body = data[
                int(section["offset"]):
                int(section["offset"]) + int(section["size"])
            ]
            relocations = []
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) != 9
                    or int(relocation_section["info"]) != int(section["index"])
                ):
                    continue
                symbol_table = sections[int(relocation_section["link"])]
                string_table = sections[int(symbol_table["link"])]
                strings = data[
                    int(string_table["offset"]):
                    int(string_table["offset"]) + int(string_table["size"])
                ]
                names = []
                for index in range(int(symbol_table["size"]) // 16):
                    fields = struct.unpack_from(
                        "<IIIBBH",
                        data,
                        int(symbol_table["offset"]) + index * 16,
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
            cls.target_results[leaf] = (body, relocations)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_authenticated_inputs_and_source_identity(self) -> None:
        self.assertEqual(len(OFFICIAL.read_bytes()), 3_523_396)
        self.assertEqual(
            hashlib.sha256(OFFICIAL.read_bytes()).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(UPSTREAM.stat().st_size, 70_106)
        self.assertEqual(
            hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
            "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36",
        )
        verified = subprocess.run(
            [sys.executable, str(VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CMSIS-FreeRTOS v10.5.1", verified.stdout)

    def test_all_four_stock_spans_are_exact(self) -> None:
        for name, (start, end, expected_hash) in STOCK.items():
            with self.subTest(name=name):
                body = self.span(start, end)
                self.assertEqual(len(body), end - start)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)

    def test_irq_context_matches_cmsis_policy(self) -> None:
        cases = [
            ((1, 0, 0, 1), 1),
            ((0, 1, 1, 1), 0),
            ((0, 0, 0, 2), 0),
            ((0, 1, 0, 2), 1),
            ((0, 0, 0x30, 2), 1),
            ((0, 0, 1, 0), 1),
        ]
        for inputs, expected in cases:
            with self.subTest(inputs=inputs):
                self.set_context(*inputs)
                self.assertEqual(self.irq_context(), expected)

    def test_tick_count_selects_thread_or_isr_provider(self) -> None:
        self.set_ticks(0x12345678, 0xA5A55A5A)
        self.set_context(0, 0, 0, 2)
        self.assertEqual(self.tick_count(), 0x12345678)
        self.set_context(7, 0, 0, 2)
        self.assertEqual(self.tick_count(), 0xA5A55A5A)

    def test_thread_id_forwards_opaque_handle(self) -> None:
        for value in (0, 1, 0x20074A20, 0xFFFFFFFF):
            with self.subTest(value=value):
                self.set_current(value)
                self.assertEqual(self.thread_id() or 0, value)

    def test_queue_capacity_reads_only_offset_0x3c(self) -> None:
        queue = (ctypes.c_ubyte * 80)()
        sentinel = 0xFEDCBA98
        ctypes.c_uint32.from_buffer(queue, 0x3C).value = sentinel
        self.assertEqual(self.capacity(ctypes.addressof(queue)), sentinel)
        self.assertEqual(self.capacity(None), 0)

    def test_each_target_leaf_is_bounded_and_relocation_pinned(self) -> None:
        for leaf, (_, size, expected_hash, expected_relocations) in LEAVES.items():
            with self.subTest(leaf=leaf):
                body, relocations = self.target_results[leaf]
                self.assertEqual(len(body), size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
                self.assertEqual(relocations, expected_relocations)

    def test_candidate_source_and_fixture_are_pinned(self) -> None:
        self.assertEqual(SOURCE.stat().st_size, 5_750)
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "483723544fed146ef9d843c215736a748a5fcab13196ee2bd8938c5419f6570b",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "50c241ed3c0c7d6a1224f5f0ca53604345e855464a784ce7b070722cd52d13c4",
        )
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "SPDX-License-Identifier: Apache-2.0",
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "13acfbef7be85119fc6bc56832c455d4547d92c7",
            "OPEN_CFW_CMSIS_QUEUE_LENGTH_OFFSET = 0x3C",
            "open_cfw_freertos_task_get_current_task_handle",
        ):
            self.assertIn(token, source)

    def test_production_overlay_and_manifest_admit_all_four_leaves(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        names = set(STOCK)
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in names
        }
        self.assertEqual(set(leaves), names)
        self.assertEqual(
            {item["target_function"] for item in config["patch_sites"]}
            & names,
            names,
        )
        for name, item in leaves.items():
            with self.subTest(name=name):
                self.assertEqual(item["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
                self.assertEqual(
                    item["source"]["sha256"],
                    "483723544fed146ef9d843c215736a748a5fcab13196ee2bd8938c5419f6570b",
                )
                self.assertEqual(item["source"]["license"], "Apache-2.0")
                self.assertEqual(
                    item["source"]["upstream_commit"],
                    "d213f261b5be6bb29a7cce8b84071706b72f4d53",
                )
                self.assertIn("linux-clang", item["toolchain_profiles"])
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": 360578,
                "overlay_sha256": "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
                "component_size": 3883974,
                "component_sha256": "a3d36ad784519c7193976e1bbfe1b5dc7c6a07fd3bba185166e12fce2a0f19d9",
            },
        )
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(main["provider"]["size"], 3883974)
        self.assertEqual(
            main["provider"]["sha256"],
            "a3d36ad784519c7193976e1bbfe1b5dc7c6a07fd3bba185166e12fce2a0f19d9",
        )
        region_names = {item["name"] for item in main["regions"]}
        self.assertTrue(
            {
                "apollo_cmsis_irq_context_source_leaf",
                "apollo_cmsis_kernel_get_tick_count_source_leaf",
                "apollo_cmsis_thread_get_id_source_leaf",
                "apollo_cmsis_message_queue_get_capacity_source_leaf",
            }.issubset(region_names)
        )


if __name__ == "__main__":
    unittest.main()
