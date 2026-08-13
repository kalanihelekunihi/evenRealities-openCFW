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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_timer_ops.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_timer_ops_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

STOCK = {
    "open_cfw_cmsis_timer_start": (
        0x00449498,
        0x004494D8,
        "db1c7749aa74828b87e3e52adb5aede0ec33854ae7a23f41becf56161727c71d",
    ),
    "open_cfw_cmsis_timer_stop": (
        0x004494D8,
        0x00449522,
        "4aa92a7e2312a8f631872730fb5f653cf9d161ec48921258d0f52d82ccab8002",
    ),
    "open_cfw_cmsis_timer_delete": (
        0x0044953E,
        0x00449590,
        "ff0de25911fdae3e67d317f6db72bf1121d224a73d4599c63910b841bc31fef9",
    ),
}

TARGET = {
    "open_cfw_cmsis_timer_start": (
        70,
        "b02533265ea281d9aadba64ee44f85a29b07117988ecd7dc2126c488bff1a530",
        [(8, 10, "open_cfw_cmsis_irq_context"), (50, 10, "open_cfw_rtos_timer_command")],
    ),
    "open_cfw_cmsis_timer_stop": (
        78,
        "8a1f722904cf138cf58da542aad91560e8105f7a7ace1f073754043175e8b226",
        [
            (6, 10, "open_cfw_cmsis_irq_context"),
            (24, 10, "open_cfw_rtos_timer_is_active"),
            (42, 10, "open_cfw_rtos_timer_command"),
        ],
    ),
    "open_cfw_cmsis_timer_delete": (
        86,
        "db4abb69f22056c19fc76d05c61bea417fad837095df8f260101901753ad6553",
        [
            (6, 10, "open_cfw_cmsis_irq_context"),
            (24, 10, "open_cfw_rtos_timer_get_context"),
            (46, 10, "open_cfw_rtos_timer_command"),
            (60, 10, "open_cfw_freertos_heap4_free"),
        ],
    ),
}

APPLE_LINKED = {
    "open_cfw_cmsis_timer_start": "1e6347dd38dd0cd0670369f77a2f68105d7f86635de0506eea95722fa3b3b971",
    "open_cfw_cmsis_timer_stop": "e8787ad34af5234c2bbbd8f7a5811b34e3318d16594b597b4f0fca9e9478baa1",
    "open_cfw_cmsis_timer_delete": "8fbce07385d2f8007b12964ee473db6062ccf6caacf8df70a6bbec6dc74c6e39",
}

LINUX_LINKED = {
    "open_cfw_cmsis_timer_start": "d9a5720f0b589297bf300e2d05f425ccb4ef68beecf737273cc98b04bb633110",
    "open_cfw_cmsis_timer_stop": "610b3c8dc4784fe490c77b3cfa9f81777805fe36b953cfd6a0acafb4f1eaae00",
    "open_cfw_cmsis_timer_delete": "d94f4f1f17ef764cf1702c785167f13a4cc6e4ab807c06875e4ea5fe886b576f",
}


class RuntimeCmsisTimerOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("timer.dylib" if sys.platform == "darwin" else "timer.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            command.append("-fPIC")
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.start = cls.loaded.open_cfw_cmsis_timer_start
        cls.start.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.start.restype = ctypes.c_int32
        cls.stop = cls.loaded.open_cfw_cmsis_timer_stop
        cls.stop.argtypes = [ctypes.c_void_p]
        cls.stop.restype = ctypes.c_int32
        cls.delete = cls.loaded.open_cfw_cmsis_timer_delete
        cls.delete.argtypes = [ctypes.c_void_p]
        cls.delete.restype = ctypes.c_int32
        cls.reset = cls.loaded.open_cfw_test_timer_ops_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_size_t]
        cls.get = {}
        for name in (
            "command_calls", "active_calls", "context_calls", "free_calls",
            "timer", "command_id", "optional_value", "ticks_to_wait", "freed",
        ):
            function = getattr(cls.loaded, f"open_cfw_test_timer_ops_{name}")
            function.restype = ctypes.c_int if name == "command_id" else ctypes.c_size_t
            cls.get[name] = function

        target = temporary / "timer.o"
        flags = [
            "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
            "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
            "-mno-unaligned-access", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
            "-fdata-sections", "-Wall", "-Wextra", "-Werror",
        ]
        subprocess.run([clang, *flags, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        cls.target = {}
        for function in TARGET:
            section = apollo_overlay.section_named(sections, f".text.{function}")
            start = int(section["offset"])
            body = data[start:start + int(section["size"])]
            relocations = []
            for relocation_section in sections:
                if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                    continue
                symbols = sections[int(relocation_section["link"])]
                strings_section = sections[int(symbols["link"])]
                strings = data[int(strings_section["offset"]):int(strings_section["offset"]) + int(strings_section["size"])]
                names = []
                for index in range(int(symbols["size"]) // 16):
                    fields = struct.unpack_from("<IIIBBH", data, int(symbols["offset"]) + index * 16)
                    names.append(apollo_overlay.elf_string(strings, fields[0], "symbol"))
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from("<II", data, int(relocation_section["offset"]) + index * 8)
                    relocations.append((offset, information & 0xFF, names[information >> 8]))
            cls.target[function] = (body, relocations)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def state(self) -> tuple[int, ...]:
        return tuple(self.get[name]() for name in ("command_calls", "active_calls", "context_calls", "free_calls"))

    def test_source_fixture_stock_and_target_contracts_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()), (3795, "1a89eed70dc2fe894f4b96615b1b346e3e321199fd5d0318bb434c19fd90f443"))
        self.assertEqual((FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()), (3145, "17ac355249c2eb5b212e0a3505c2c2bf1ca27695e8138a8bea2f5f0156c14b7d"))
        image = OFFICIAL.read_bytes()[32:]
        for function, (start, end, stock_sha256) in STOCK.items():
            with self.subTest(function=function, kind="stock"):
                body = image[start - 0x00438000:end - 0x00438000]
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, stock_sha256))
            with self.subTest(function=function, kind="target"):
                body, relocations = self.target[function]
                size, sha256, expected_relocations = TARGET[function]
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, sha256))
                self.assertEqual(relocations, expected_relocations)

    def test_start_validation_command_and_statuses(self) -> None:
        for irq, timer, ticks, result, status, calls in (
            (1, 0x1234, 7, 1, -6, 0), (0, 0, 7, 1, -4, 0),
            (0, 0x1234, 0, 1, -4, 0), (0, 0x1234, 7, 0, -3, 1),
            (0, 0x1234, 7, 1, 0, 1),
        ):
            with self.subTest(irq=irq, timer=timer, ticks=ticks, result=result):
                self.reset(irq, result, 1, 0)
                self.assertEqual(self.start(ctypes.c_void_p(timer), ticks), status)
                self.assertEqual(self.state(), (calls, 0, 0, 0))
                if calls:
                    self.assertEqual((self.get["timer"](), self.get["command_id"](), self.get["optional_value"](), self.get["ticks_to_wait"]()), (timer, 4, ticks, 0))

    def test_stop_validation_activity_command_and_statuses(self) -> None:
        for irq, timer, active, result, status, state in (
            (1, 0x1234, 1, 1, -6, (0, 0, 0, 0)),
            (0, 0, 1, 1, -4, (0, 0, 0, 0)),
            (0, 0x1234, 0, 1, -3, (0, 1, 0, 0)),
            (0, 0x1234, 1, 0, -1, (1, 1, 0, 0)),
            (0, 0x1234, 1, 1, 0, (1, 1, 0, 0)),
        ):
            with self.subTest(irq=irq, active=active, result=result):
                self.reset(irq, result, active, 0)
                self.assertEqual(self.stop(ctypes.c_void_p(timer)), status)
                self.assertEqual(self.state(), state)
                if state[0]:
                    self.assertEqual((self.get["command_id"](), self.get["optional_value"](), self.get["ticks_to_wait"]()), (3, 0, 0))

    def test_delete_context_tag_free_and_failure_paths(self) -> None:
        for irq, timer, result, context, status, state, freed in (
            (1, 0x1234, 1, 0x2001, -6, (0, 0, 0, 0), 0),
            (0, 0, 1, 0x2001, -4, (0, 0, 0, 0), 0),
            (0, 0x1234, 0, 0x2001, -3, (1, 0, 1, 0), 0),
            (0, 0x1234, 1, 0x2000, 0, (1, 0, 1, 0), 0),
            (0, 0x1234, 1, 0x2001, 0, (1, 0, 1, 1), 0x2000),
        ):
            with self.subTest(irq=irq, result=result, context=context):
                self.reset(irq, result, 1, context)
                self.assertEqual(self.delete(ctypes.c_void_p(timer)), status)
                self.assertEqual(self.state(), state)
                self.assertEqual(self.get["freed"](), freed)
                if state[0]:
                    self.assertEqual((self.get["command_id"](), self.get["optional_value"](), self.get["ticks_to_wait"]()), (5, 0, 0))

    def test_production_overlay_and_manifest_admit_timer_operations(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in TARGET
        }
        self.assertEqual(set(leaves), set(TARGET))
        self.assertEqual(
            {item["target_function"] for item in config["patch_sites"]}
            & set(TARGET),
            set(TARGET),
        )
        for name, item in leaves.items():
            with self.subTest(name=name):
                self.assertEqual(item["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
                self.assertEqual(item["source"]["sha256"], "1a89eed70dc2fe894f4b96615b1b346e3e321199fd5d0318bb434c19fd90f443")
                self.assertEqual(item["source"]["upstream_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
                self.assertEqual(item["expected"]["sha256"], APPLE_LINKED[name])
                self.assertEqual(item["toolchain_profiles"]["linux-clang"]["expected"]["sha256"], LINUX_LINKED[name])

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(main["provider"]["size"], 3_665_974)
        self.assertEqual(main["provider"]["profiles"]["linux-clang"]["size"], 3_667_662)
        region_names = {item["name"] for item in main["regions"]}
        self.assertTrue(
            {
                "apollo_cmsis_timer_start_source_leaf",
                "apollo_cmsis_timer_stop_source_leaf",
                "apollo_cmsis_timer_delete_source_leaf",
            }.issubset(region_names)
        )


if __name__ == "__main__":
    unittest.main()
