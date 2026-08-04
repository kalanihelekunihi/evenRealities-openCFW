from __future__ import annotations

import os

import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_record_metadata_host.c"
)
RECORD_SIZE = 200


class MramRecordMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_record_metadata.dylib"
            if sys.platform == "darwin"
            else "mram_record_metadata.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))

        cls.set_peer_hash = cls.loaded.open_cfw_mram_set_peer_db_hash
        cls.set_peer_hash.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.set_cache = cls.loaded.open_cfw_mram_set_cache_by_hash
        cls.set_cache.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_ccc = cls.loaded.open_cfw_mram_set_ccc_table_value
        cls.set_ccc.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.get_csf = cls.loaded.open_cfw_mram_get_csf_record
        cls.get_csf.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.set_csf = cls.loaded.open_cfw_mram_set_csf_record
        cls.set_csf.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
        ]
        cls.set_change_aware = (
            cls.loaded.open_cfw_mram_set_client_change_aware_state
        )
        cls.set_change_aware.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.get_device_hash = cls.loaded.open_cfw_mram_get_device_db_hash
        cls.get_device_hash.restype = ctypes.c_void_p
        cls.set_device_hash = cls.loaded.open_cfw_mram_set_device_db_hash
        cls.set_device_hash.argtypes = [ctypes.c_void_p]
        cls.set_discovery = cls.loaded.open_cfw_mram_set_discovery_status
        cls.set_discovery.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_handle_list = cls.loaded.open_cfw_mram_set_handle_list
        cls.set_handle_list.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.set_sign_counter = (
            cls.loaded.open_cfw_mram_set_peer_sign_counter
        )
        cls.set_sign_counter.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_address_resolution = (
            cls.loaded.open_cfw_mram_set_peer_address_resolution
        )
        cls.set_address_resolution.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.record = (ctypes.c_ubyte * RECORD_SIZE)()
        self.base = ctypes.addressof(self.record)
        self.records = (ctypes.c_ubyte * (10 * RECORD_SIZE)).in_dll(
            self.loaded,
            "open_cfw_test_mram_metadata_records",
        )
        self.device_hash = (ctypes.c_ubyte * 16).in_dll(
            self.loaded,
            "open_cfw_test_mram_metadata_device_hash",
        )
        self.trace = (ctypes.c_uint * 16).in_dll(
            self.loaded,
            "open_cfw_test_mram_metadata_trace",
        )
        for index in range(len(self.records)):
            self.records[index] = 0
        for index in range(len(self.device_hash)):
            self.device_hash[index] = 0
        self.reset_calls()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def signed_word(self, name: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def reset_calls(self) -> None:
        for name in (
            "open_cfw_test_mram_metadata_update_calls",
            "open_cfw_test_mram_metadata_verify_calls",
            "open_cfw_test_mram_metadata_connection_id_calls",
            "open_cfw_test_mram_metadata_connection_active_calls",
            "open_cfw_test_mram_metadata_connection_id",
            "open_cfw_test_mram_metadata_connection_active_argument",
            "open_cfw_test_mram_metadata_trace_count",
        ):
            self.word(name).value = 0
        self.signed_word(
            "open_cfw_test_mram_metadata_connection_active_result"
        ).value = 0
        self.pointer(
            "open_cfw_test_mram_metadata_update_record"
        ).value = None
        self.pointer(
            "open_cfw_test_mram_metadata_verify_record"
        ).value = None
        for index in range(len(self.trace)):
            self.trace[index] = 0

    def assert_persisted(self, expected_trace: list[int]) -> None:
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_metadata_update_calls"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_metadata_verify_calls"
            ).value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_metadata_update_record"
            ).value,
            self.base,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_metadata_verify_record"
            ).value,
            self.base,
        )
        count = self.word(
            "open_cfw_test_mram_metadata_trace_count"
        ).value
        self.assertEqual(list(self.trace)[:count], expected_trace)

    def test_persisted_peer_hash_and_cache_by_hash(self) -> None:
        peer_hash = (ctypes.c_ubyte * 16)(
            *(index ^ 0xA5 for index in range(16))
        )

        self.set_peer_hash(self.base, peer_hash)

        self.assertEqual(bytes(self.record[0x87:0x97]), bytes(peer_hash))
        self.assert_persisted([3, 4])

        self.reset_calls()
        self.set_cache(self.base, 0x123456A7)
        self.assertEqual(self.record[0x86], 0xA7)
        self.assert_persisted([3, 4])

    def test_ccc_value_truncates_inputs_and_gates_persistence(self) -> None:
        self.word(
            "open_cfw_test_mram_metadata_connection_id"
        ).value = 0xABCDEF42
        self.signed_word(
            "open_cfw_test_mram_metadata_connection_active_result"
        ).value = 0

        self.set_ccc(self.base, 0x10001, 0xDEAD1234)

        self.assertEqual(bytes(self.record[0x6E:0x70]), b"\x34\x12")
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_metadata_connection_active_argument"
            ).value,
            0x42,
        )
        self.assertEqual(
            (
                self.word(
                    "open_cfw_test_mram_metadata_connection_id_calls"
                ).value,
                self.word(
                    "open_cfw_test_mram_metadata_connection_active_calls"
                ).value,
                self.word(
                    "open_cfw_test_mram_metadata_update_calls"
                ).value,
                self.word(
                    "open_cfw_test_mram_metadata_verify_calls"
                ).value,
            ),
            (1, 1, 0, 0),
        )
        self.assertEqual(list(self.trace)[:2], [1, 2])

        self.reset_calls()
        self.word(
            "open_cfw_test_mram_metadata_connection_id"
        ).value = 0x1FF
        self.signed_word(
            "open_cfw_test_mram_metadata_connection_active_result"
        ).value = -7

        self.set_ccc(self.base, 2, 0xCAFE)

        self.assertEqual(bytes(self.record[0x70:0x72]), b"\xFE\xCA")
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_metadata_connection_active_argument"
            ).value,
            0xFF,
        )
        self.assert_persisted([1, 2, 3, 4])

    def test_csf_getter_and_null_guarded_setter(self) -> None:
        self.record[0x84] = 0x73
        self.record[0x85] = 0xA4
        state = ctypes.c_ubyte(0)
        features = ctypes.c_void_p()

        self.get_csf(
            self.base,
            ctypes.byref(state),
            ctypes.byref(features),
        )

        self.assertEqual(state.value, 0x73)
        self.assertEqual(features.value, self.base + 0x85)

        new_features = (ctypes.c_ubyte * 1)(0x5C)
        self.set_csf(self.base, 0x1234, new_features)
        self.assertEqual((self.record[0x84], self.record[0x85]), (0x34, 0x5C))

        before = bytes(self.record)
        self.set_csf(self.base, 0x99, None)
        self.set_csf(None, 0x99, new_features)
        self.assertEqual(bytes(self.record), before)

    def test_change_aware_state_targets_one_or_all_records(self) -> None:
        self.set_change_aware(self.base, 0x123456D2)
        self.assertEqual(self.record[0x84], 0xD2)

        for record_index in range(10):
            self.records[record_index * RECORD_SIZE + 0x84] = record_index
            self.records[record_index * RECORD_SIZE + 0x83] = 0xA5
            self.records[record_index * RECORD_SIZE + 0x85] = 0x5A

        self.set_change_aware(None, 0x1AB)

        for record_index in range(10):
            base = record_index * RECORD_SIZE
            self.assertEqual(self.records[base + 0x84], 0xAB)
            self.assertEqual(self.records[base + 0x83], 0xA5)
            self.assertEqual(self.records[base + 0x85], 0x5A)

    def test_device_hash_getter_and_null_guarded_setter(self) -> None:
        expected_pointer = ctypes.addressof(self.device_hash)
        self.assertEqual(self.get_device_hash(), expected_pointer)

        source = (ctypes.c_ubyte * 16)(
            *(255 - index for index in range(16))
        )
        self.set_device_hash(source)
        self.assertEqual(bytes(self.device_hash), bytes(source))

        before = bytes(self.device_hash)
        self.set_device_hash(None)
        self.assertEqual(bytes(self.device_hash), before)

    def test_discovery_handle_list_counter_and_address_resolution(self) -> None:
        handle_list = (ctypes.c_ubyte * 42)(
            *(index * 3 & 0xFF for index in range(42))
        )

        self.set_discovery(self.base, 0x1234569B)
        self.assertEqual(self.record[0xC2], 0x9B)
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_metadata_update_calls"
            ).value,
            0,
        )

        self.set_handle_list(self.base, handle_list)
        self.assertEqual(bytes(self.record[0x98:0xC2]), bytes(handle_list))
        self.assert_persisted([3, 4])

        self.reset_calls()
        self.set_sign_counter(self.base, 0x89ABCDEF)
        self.set_address_resolution(self.base, 0x12345678)
        self.assertEqual(
            bytes(self.record[0x80:0x84]),
            b"\xEF\xCD\xAB\x89",
        )
        self.assertEqual(self.record[0x31], 0x78)
        self.assertEqual(
            (
                self.word(
                    "open_cfw_test_mram_metadata_update_calls"
                ).value,
                self.word(
                    "open_cfw_test_mram_metadata_verify_calls"
                ).value,
            ),
            (0, 0),
        )

    def test_randomized_field_model_and_persistence_contract(self) -> None:
        generator = random.Random(0x47B3AE)

        for _ in range(500):
            raw = bytes(
                generator.randrange(256)
                for _ in range(RECORD_SIZE)
            )
            for index, value in enumerate(raw):
                self.record[index] = value
            peer_hash = bytes(generator.randrange(256) for _ in range(16))
            handle_list = bytes(
                generator.randrange(256) for _ in range(42)
            )
            peer_hash_array = (ctypes.c_ubyte * 16).from_buffer_copy(
                peer_hash
            )
            handle_array = (ctypes.c_ubyte * 42).from_buffer_copy(
                handle_list
            )
            cache = generator.getrandbits(32)
            discovery = generator.getrandbits(32)
            counter = generator.getrandbits(32)
            address_resolution = generator.getrandbits(32)

            self.reset_calls()
            self.set_peer_hash(self.base, peer_hash_array)
            self.assertEqual(
                bytes(self.record[0x87:0x97]),
                peer_hash,
            )
            self.assert_persisted([3, 4])

            self.reset_calls()
            self.set_cache(self.base, cache)
            self.assertEqual(self.record[0x86], cache & 0xFF)
            self.assert_persisted([3, 4])

            self.reset_calls()
            self.set_handle_list(self.base, handle_array)
            self.assertEqual(
                bytes(self.record[0x98:0xC2]),
                handle_list,
            )
            self.assert_persisted([3, 4])

            self.reset_calls()
            self.set_discovery(self.base, discovery)
            self.set_sign_counter(self.base, counter)
            self.set_address_resolution(self.base, address_resolution)
            self.assertEqual(self.record[0xC2], discovery & 0xFF)
            self.assertEqual(
                int.from_bytes(self.record[0x80:0x84], "little"),
                counter,
            )
            self.assertEqual(
                self.record[0x31],
                address_resolution & 0xFF,
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_metadata_trace_count"
                ).value,
                0,
            )


if __name__ == "__main__":
    unittest.main()
