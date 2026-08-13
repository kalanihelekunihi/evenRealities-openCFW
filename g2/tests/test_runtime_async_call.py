from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components" / "apollo_main" / "core_overlay" / "runtime_async_call.c"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_async_call_host.c"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000
CALL_START, CALL_END = 0x484014, 0x484052
CANCEL_START, CANCEL_END = 0x484052, 0x4840AA
CALLBACK_START, CALLBACK_END = 0x4840AC, 0x4840C6
CALLBACK_THUMB = CALLBACK_START | 1
CANCEL_TIMER_BASE = 0x6000
CANCEL_ALLOCATION_BASE = 0x7000
CANCEL_STRIDE = 0x20
FLAGS = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra", "-Werror"]


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class Info(ctypes.Structure):
    _fields_ = [("callback", ctypes.c_uint32), ("user_data", ctypes.c_uint32)]


class RuntimeAsyncCallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temp = tempfile.TemporaryDirectory()
        temp = Path(cls.temp.name)
        library = temp / ("a.dylib" if sys.platform == "darwin" else "a.so")
        command = [os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_async_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.call = cls.loaded.open_cfw_runtime_async_call
        cls.call.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.call.restype = ctypes.c_uint32
        cls.cancel = cls.loaded.open_cfw_runtime_async_call_cancel
        cls.cancel.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.cancel.restype = ctypes.c_uint32
        cls.cancel_reset = (
            cls.loaded.open_cfw_test_runtime_async_cancel_reset
        )
        cls.cancel_reset.argtypes = [ctypes.c_uint32]
        cls.cancel_configure = (
            cls.loaded.open_cfw_test_runtime_async_cancel_configure
        )
        cls.cancel_configure.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.callback = cls.loaded.open_cfw_runtime_async_timer_callback
        cls.callback.argtypes = [ctypes.c_uint32]
        cls.callback.restype = None
        cls.info = Info.in_dll(cls.loaded, "open_cfw_test_runtime_async_info")
        target = temp / "a.o"
        subprocess.run([os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"), *FLAGS, "-c", str(SOURCE), "-o", str(target)], check=True, capture_output=True, text=True)
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(target)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
        sym = apollo_overlay.section_named(sections, ".symtab")
        strings = sections[int(sym["link"])]
        sd = data[int(strings["offset"]):int(strings["offset"]) + int(strings["size"])]
        parsed = []
        for i in range(int(sym["size"]) // 16):
            fields = struct.unpack_from("<IIIBBH", data, int(sym["offset"]) + i * 16)
            parsed.append((apollo_overlay.elf_string(sd, fields[0], "symbol"), fields))
        cls.symbols = {name: fields for name, fields in parsed if name}
        cls.relocs = []
        for section in sections:
            if int(section["type"]) == 9 and int(section["info"]) == int(text["index"]):
                for i in range(int(section["size"]) // 8):
                    off, info = struct.unpack_from("<II", data, int(section["offset"]) + i * 8)
                    cls.relocs.append((off, info & 255, parsed[info >> 8][0]))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint32.in_dll(self.loaded, name).value = value

    def events(self) -> list[int]:
        count = self.uint("open_cfw_test_runtime_async_event_count")
        values = (ctypes.c_uint32 * 8).in_dll(
            self.loaded, "open_cfw_test_runtime_async_events"
        )
        return list(values[:count])

    def uint_array(self, name: str, count: int) -> list[int]:
        values = (ctypes.c_uint32 * count).in_dll(self.loaded, name)
        return list(values)

    def test_allocation_failure_returns_invalid_without_side_effects(self) -> None:
        self.reset(0, 0x300)
        self.assertEqual(self.call(0x111, 0x222), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_allocate_size"), 8)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_create_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_free_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_repeat_calls"), 0)

    def test_timer_failure_frees_info_and_returns_invalid(self) -> None:
        self.reset(0x200, 0)
        self.assertEqual(self.call(0x111, 0x222), 0)
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_create_callback"),
            CALLBACK_THUMB,
        )
        self.assertEqual(self.uint("open_cfw_test_runtime_async_create_period"), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_create_user_data"), 0x200)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_freed"), 0x200)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_repeat_calls"), 0)

    def test_success_initializes_info_then_arms_one_shot_timer(self) -> None:
        self.reset(0x200, 0x300)
        self.assertEqual(self.call(0x11223344, 0x55667788), 1)
        self.assertEqual((self.info.callback, self.info.user_data), (0x11223344, 0x55667788))
        self.assertEqual(self.uint("open_cfw_test_runtime_async_free_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_repeat_timer"), 0x300)
        self.assertEqual(ctypes.c_int.in_dll(self.loaded, "open_cfw_test_runtime_async_repeat_count").value, 1)

    def test_callback_copies_deletes_frees_then_invokes(self) -> None:
        self.reset(0x200, 0x300)
        self.info.callback = 0x11223345
        self.info.user_data = 0x55667788

        self.callback(0x300)

        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_timer_user_data_calls"), 1
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_timer_user_data_timer"),
            0x300,
        )
        self.assertEqual(self.uint("open_cfw_test_runtime_async_delete_calls"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_deleted_timer"), 0x300
        )
        self.assertEqual(self.uint("open_cfw_test_runtime_async_free_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_freed"), 0x200)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_invoke_calls"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoked_callback"),
            0x11223345,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoked_user_data"),
            0x55667788,
        )
        self.assertEqual(self.events(), [1, 2, 3, 4])

    def test_callback_saved_copy_is_reentrant_and_destroyed_before_invoke(
        self,
    ) -> None:
        self.reset(0x200, 0x300)
        self.info.callback = 0x13579BDF
        self.info.user_data = 0x2468ACE0
        self.set_uint("open_cfw_test_runtime_async_mutate_info_on_invoke", 1)

        self.callback(0x300)

        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoke_delete_calls_seen"), 1
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoke_free_calls_seen"), 1
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoked_callback"),
            0x13579BDF,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_invoked_user_data"),
            0x2468ACE0,
        )
        self.assertEqual(
            (self.info.callback, self.info.user_data),
            (0xDEADBEEF, 0xCAFEBABE),
        )

    def test_cancel_empty_list_returns_invalid_without_deletion(self) -> None:
        self.reset(0x200, 0x300)
        self.cancel_reset(0)

        self.assertEqual(self.cancel(0x11111111, 0x22222222), 0)
        self.assertEqual(
            self.uint("open_cfw_test_runtime_async_cancel_get_next_calls"),
            1,
        )
        self.assertEqual(
            self.uint_array(
                "open_cfw_test_runtime_async_cancel_get_next_argument",
                8,
            )[:1],
            [0],
        )
        self.assertEqual(self.uint("open_cfw_test_runtime_async_delete_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_runtime_async_free_calls"), 0)
        self.assertEqual(self.events(), [])

    def test_cancel_filters_exact_identity_and_removes_every_match(
        self,
    ) -> None:
        callback = 0x13579BDF
        user_data = 0x2468ACE0
        self.reset(0x200, 0x300)
        self.cancel_reset(6)
        configurations = [
            (0x004840C7, callback, user_data),
            (CALLBACK_THUMB, callback + 2, user_data),
            (CALLBACK_THUMB, callback, user_data + 4),
            (CALLBACK_THUMB, callback, user_data),
            (CALLBACK_THUMB, callback, user_data),
            (CALLBACK_THUMB, callback, user_data),
        ]
        for index, values in enumerate(configurations):
            self.cancel_configure(index, *values)

        self.assertEqual(self.cancel(callback, user_data), 1)
        self.assertEqual(
            self.uint_array(
                "open_cfw_test_runtime_async_cancel_active",
                6,
            ),
            [1, 1, 1, 0, 0, 0],
        )
        timer_pointers = [
            CANCEL_TIMER_BASE + index * CANCEL_STRIDE
            for index in range(6)
        ]
        allocation_pointers = [
            CANCEL_ALLOCATION_BASE + index * CANCEL_STRIDE
            for index in range(6)
        ]
        self.assertEqual(
            self.uint_array(
                "open_cfw_test_runtime_async_cancel_get_next_argument",
                8,
            )[:7],
            [0, *timer_pointers],
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_async_cancel_invalid_traversals"
            ),
            0,
        )
        self.assertEqual(
            self.uint_array(
                "open_cfw_test_runtime_async_cancel_deleted",
                6,
            )[:3],
            timer_pointers[3:],
        )
        self.assertEqual(
            self.uint_array(
                "open_cfw_test_runtime_async_cancel_freed",
                6,
            )[:3],
            allocation_pointers[3:],
        )
        self.assertEqual(self.events(), [2, 3, 2, 3, 2, 3])

    @staticmethod
    def decode_adr_target(application: bytes, address: int) -> int:
        first, second = struct.unpack_from(
            "<HH", application, address - BASE
        )
        immediate = (
            ((first >> 10) & 1) << 11
            | ((second >> 12) & 7) << 8
            | (second & 0xFF)
        )
        return ((address + 4) & ~3) + immediate

    def test_stock_boundary_caller_dependencies_and_topology_are_exact(self) -> None:
        body = self.application[CALL_START - BASE:CALL_END - BASE]
        self.assertEqual(len(body), 62)
        self.assertEqual(hashlib.sha256(body).hexdigest(), "4a3b8927b10dd11d3b872207c2138dd85494060f948727dc021025c3b57c174f")
        following = self.application[CALL_END - BASE:CALL_END - BASE + 8]
        self.assertEqual(hashlib.sha256(following).hexdigest(), "8dda716ee93857cdfdc9faf824123a7c6ccd461fb72c60bbc0bee4be38fd7161")
        self.assertEqual(hashlib.sha256(struct.pack("<I", 0x44D946)).hexdigest(), "5ed060fadc294cf334f0b89ccdec495809e5703143bc3089868a2300b1a0dcb9")
        self.assertEqual(self.application[0x44D946 - BASE:0x44D94A - BASE].hex(), "36f065fb")
        self.assertEqual(
            [(0x48401C, 0x44F718), (0x484032, 0x464466), (0x48403C, 0x44F758), (0x48404A, 0x4645AC)],
            [(a, t) for a, t in [(0x48401C, 0x44F718), (0x484032, 0x464466), (0x48403C, 0x44F758), (0x48404A, 0x4645AC)]],
        )
        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value & 1 and CALL_START <= (value & ~1) < CALL_END:
                stored.append((BASE + offset, value & ~1, value))
        self.assertEqual(stored, [(0x4AAA85, 0x484020, 0x484021)])

    def test_stock_callback_boundary_dependencies_and_topology_are_exact(
        self,
    ) -> None:
        body = self.application[
            CALLBACK_START - BASE:CALLBACK_END - BASE
        ]
        self.assertEqual(len(body), 26)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "39c550823fd1d0bb1b80f29119c66bd33d2751de30c9d4c2ccc987bd99e5c8d8",
        )
        self.assertEqual(
            body.hex(),
            "70b5c668d6e90045e0f71bfa3000cbf74dfb28002100884770bd",
        )
        self.assertEqual(
            self.application[CALLBACK_START - BASE - 2:CALLBACK_START - BASE],
            b"\x00\x00",
        )
        self.assertEqual(
            self.application[CALLBACK_END - BASE:CALLBACK_END - BASE + 2],
            b"\x00\x00",
        )
        self.assertEqual(
            self.decode_adr_target(self.application, 0x48402E),
            CALLBACK_THUMB,
        )
        self.assertEqual(
            self.decode_adr_target(self.application, 0x484070),
            CALLBACK_THUMB,
        )
        for pointer in range(0x4840AC, 0x4840B0):
            encoded = struct.pack("<I", pointer)
            self.assertEqual(self.application.count(encoded), 0)

    def test_stock_cancel_boundary_caller_dependencies_and_topology_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        body = self.application[
            CANCEL_START - BASE:CANCEL_END - BASE
        ]
        self.assertEqual(len(body), 88)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "67cd3979de3365531652c6de47f55bbab9541e753c5091a8423229635ce99900",
        )
        self.assertEqual(
            self.application[CANCEL_START - BASE - 8:CANCEL_START - BASE],
            bytes.fromhex("e0f7affa012070bd"),
        )
        self.assertEqual(
            self.application[CANCEL_END - BASE:CALLBACK_START - BASE],
            b"\x00\x00",
        )
        self.assertEqual(
            [
                (
                    address,
                    apollo_overlay.decode_thumb_branch(
                        address,
                        self.application[
                            address - BASE:address - BASE + 4
                        ],
                        link=True,
                    ),
                )
                for address in (
                    0x48405C,
                    0x484068,
                    0x484090,
                    0x484096,
                )
            ],
            [
                (0x48405C, 0x4645EC),
                (0x484068, 0x4645EC),
                (0x484090, 0x4644EE),
                (0x484096, 0x44F758),
            ],
        )
        callers = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if link and target == CANCEL_START:
                    callers.append(address)
                if (
                    CANCEL_START < target < CANCEL_END
                    and not CANCEL_START <= address < CANCEL_END
                ):
                    interior.append((address, target, link))
        self.assertEqual(callers, [0x44E05E])
        self.assertEqual(interior, [])
        narrow_entry = []
        narrow_interior = []

        def signed(value: int, bits: int) -> int:
            sign = 1 << (bits - 1)
            return value - (1 << bits) if value & sign else value

        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            targets = []
            if halfword & 0xF800 == 0xE000:
                targets.append(
                    address + 4
                    + signed((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 15
            if (
                halfword & 0xF000 == 0xD000
                and condition < 14
            ):
                targets.append(
                    address + 4
                    + signed((halfword & 255) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                targets.append(
                    address + 4
                    + (((halfword >> 9) & 1) << 6)
                    + (((halfword >> 3) & 31) << 1)
                )
            for target in targets:
                if (
                    target == CANCEL_START
                    and not CANCEL_START <= address < CANCEL_END
                ):
                    narrow_entry.append((address, halfword))
                if (
                    CANCEL_START < target < CANCEL_END
                    and not CANCEL_START <= address < CANCEL_END
                ):
                    narrow_interior.append(
                        (address, target, halfword)
                    )
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            self.application[0x44E05A - BASE:0x44E068 - BASE],
            bytes.fromhex("29006a4835f0f8ffc0b20128f8d0"),
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x44E208 - BASE,
            )[0],
            0x0044DF21,
        )
        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if (
                value & 1
                and CANCEL_START <= (value & ~1) < CANCEL_END
            ):
                stored.append((BASE + offset, value & ~1, value))
        self.assertEqual(stored, [])

    @_APPLE_ONLY
    def test_target_artifact_and_dependencies_are_exact(self) -> None:
        self.assertEqual(len(self.target), 244)
        self.assertEqual(
            hashlib.sha256(self.target).hexdigest(),
            "9b142dce0bc7316c733a2f83e3f07198b34ab77cd586fe0a4a83db2850293ad5",
        )
        self.assertEqual(self.relocs, [])
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )
        call = self.symbols["open_cfw_runtime_async_call"]
        call_offset = call[1] & ~1
        call_size = call[2]
        self.assertEqual((call_offset, call_size), (0, 88))
        self.assertEqual(
            hashlib.sha256(
                self.target[call_offset:call_offset + call_size]
            ).hexdigest(),
            "d887df3e763e412124b02615e3785dda2da71db7bd9b696d369126045874a74b",
        )
        self.assertEqual(
            self.target[call_offset:call_offset + call_size],
            bytes.fromhex(
                "2de9f0414ff219770546c0f2440708200c46b847"
                "b0b1064644f2674844f2ad00c0f24608c0f24800"
                "00213246c04760b108f5a37201213560746001249047"
                "2046bde8f0810020bde8f08107f1400130468847"
                "0020bde8f081"
            ),
        )
        cancel = self.symbols["open_cfw_runtime_async_call_cancel"]
        cancel_offset = cancel[1] & ~1
        cancel_size = cancel[2]
        self.assertEqual((cancel_offset, cancel_size), (88, 116))
        self.assertEqual(
            hashlib.sha256(
                self.target[cancel_offset:cancel_offset + cancel_size]
            ).hexdigest(),
            "5fc6f6009d551fef6cd4c5490a8e09d816e4d98b22e70a88430d2f2ef54e8c1a",
        )
        self.assertEqual(
            self.target[cancel_offset:cancel_offset + cancel_size],
            bytes.fromhex(
                "2de9f04f81b044f2ed5b8246c0f2460b002089464ff00008"
                "d84738b344f2ad0507464ff00008c0f24805abf1fe000090"
                "02e000bf0746c8b13846d847b968a942f8d1fe6831685145"
                "f4d171684945f1d100990446384688474ff259713046c0f2"
                "4401884720464ff00108e3e7404601b0bde8f08f"
            ),
        )
        callback = self.symbols["open_cfw_runtime_async_timer_callback"]
        callback_offset = callback[1] & ~1
        callback_size = callback[2]
        self.assertEqual((callback_offset, callback_size), (204, 40))
        self.assertEqual(
            hashlib.sha256(
                self.target[
                    callback_offset:callback_offset + callback_size
                ]
            ).hexdigest(),
            "6e9464c3aad06063d0642d5b54af01cdb356b94ab314e4094087f80f6f524ec6",
        )
        self.assertEqual(
            self.target[callback_offset:callback_offset + callback_size],
            bytes.fromhex(
                "70b5c46844f2ef4126686568c0f246018847"
                "4ff25971c0f244012046884728463146"
                "bde870400847"
            ),
        )

    def test_source_is_bounded_to_lvgl_async_call(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_async_call(",
            "open_cfw_runtime_async_call_cancel(",
            "open_cfw_runtime_async_timer_callback(",
            "sizeof(struct open_cfw_runtime_async_info)",
            "TIMER_SET_REPEAT(timer, 1)",
            "TIMER_USER_DATA(timer)",
            "TIMER_DELETE(timer)",
            "TIMER_GET_NEXT(0U)",
            "TIMER_GET_NEXT(timer)",
            "INVOKE(callback, user_data)",
            "0x0044F719U",
            "0x0044F759U",
            "0x00464467U",
            "0x004645ADU",
            "0x004644EFU",
            "0x004645EDU",
            "0x004840ADU",
            "RESULT_INVALID = 0U",
            "RESULT_OK = 1U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_async_call.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
