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


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_linked_list_accessors.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_accessors_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000

FUNCTIONS = {
    "head": (0x00482CD8, 0x00482CE4),
    "tail": (0x00482CE4, 0x00482CF0),
    "next": (0x00482CF0, 0x00482CFA),
    "previous": (0x00482CFA, 0x00482D02),
    "length": (0x00482D02, 0x00482D22),
    "empty": (0x00482D88, 0x00482DA4),
    "clear": (0x00482DA4, 0x00482DAE),
}


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedList(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListAccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_accessors.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_accessors.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)

        cls.loaded = ctypes.CDLL(str(library))
        cls.head = cls.loaded.open_cfw_runtime_linked_list_get_head
        cls.tail = cls.loaded.open_cfw_runtime_linked_list_get_tail
        cls.next = cls.loaded.open_cfw_runtime_linked_list_get_next
        cls.previous = cls.loaded.open_cfw_runtime_linked_list_get_previous
        cls.length = cls.loaded.open_cfw_runtime_linked_list_get_length
        cls.empty = cls.loaded.open_cfw_runtime_linked_list_is_empty
        cls.clear = cls.loaded.open_cfw_runtime_linked_list_clear
        cls.reset = cls.loaded.open_cfw_test_runtime_linked_list_reset

        cls.head.argtypes = [ctypes.POINTER(RuntimeLinkedList)]
        cls.tail.argtypes = [ctypes.POINTER(RuntimeLinkedList)]
        cls.next.argtypes = [
            ctypes.POINTER(RuntimeLinkedList),
            ctypes.c_uint32,
        ]
        cls.previous.argtypes = [
            ctypes.POINTER(RuntimeLinkedList),
            ctypes.c_uint32,
        ]
        cls.length.argtypes = [ctypes.POINTER(RuntimeLinkedList)]
        cls.empty.argtypes = [ctypes.POINTER(RuntimeLinkedList)]
        cls.clear.argtypes = [ctypes.POINTER(RuntimeLinkedList)]
        cls.head.restype = ctypes.c_uint32
        cls.tail.restype = ctypes.c_uint32
        cls.next.restype = ctypes.c_uint32
        cls.previous.restype = ctypes.c_uint32
        cls.length.restype = ctypes.c_uint32
        cls.empty.restype = ctypes.c_ubyte
        cls.clear.restype = None
        cls.reset.argtypes = []
        cls.reset.restype = None

        cls.storage = (ctypes.c_ubyte * 1024).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_storage",
        )
        cls.pointer_resolutions = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_pointer_resolutions",
        )
        cls.clear_calls = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_clear_calls",
        )
        cls.clear_list = ctypes.c_void_p.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_clear_list",
        )
        cls.clear_cleanup = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_clear_cleanup",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def setUp(self) -> None:
        self.reset()

    def store_pointer(self, offset: int, value: int) -> None:
        struct.pack_into("<I", self.storage, offset, value)

    def test_head_and_tail_accessors_preserve_null_semantics(self) -> None:
        linked_list = RuntimeLinkedList(
            0x20,
            0x12345678,
            0x9ABCDEF0,
        )
        self.assertEqual(self.head(ctypes.byref(linked_list)), 0x12345678)
        self.assertEqual(self.tail(ctypes.byref(linked_list)), 0x9ABCDEF0)
        self.assertEqual(self.head(None), 0)
        self.assertEqual(self.tail(None), 0)
        self.assertEqual(self.pointer_resolutions.value, 0)

    def test_next_and_previous_use_exact_node_metadata_offsets(self) -> None:
        for node_size in (0, 4, 12, 64, 128):
            node = 100
            linked_list = RuntimeLinkedList(node_size, node, node)
            expected_previous = 0x10203040 + node_size
            expected_next = 0x50607080 + node_size
            self.store_pointer(node + node_size, expected_previous)
            self.store_pointer(node + node_size + 4, expected_next)
            with self.subTest(node_size=node_size):
                self.assertEqual(
                    self.previous(ctypes.byref(linked_list), node),
                    expected_previous,
                )
                self.assertEqual(
                    self.next(ctypes.byref(linked_list), node),
                    expected_next,
                )
        self.assertEqual(self.pointer_resolutions.value, 10)

    def test_length_traverses_head_then_next_and_wraps_as_word(self) -> None:
        linked_list = RuntimeLinkedList(12, 0, 0)
        self.assertEqual(self.length(ctypes.byref(linked_list)), 0)
        self.assertEqual(self.pointer_resolutions.value, 0)

        nodes = [32, 96, 160, 224]
        linked_list.head = nodes[0]
        linked_list.tail = nodes[-1]
        for index, node in enumerate(nodes):
            next_node = nodes[index + 1] if index + 1 < len(nodes) else 0
            self.store_pointer(node + linked_list.node_size + 4, next_node)
        self.assertEqual(self.length(ctypes.byref(linked_list)), len(nodes))
        self.assertEqual(self.pointer_resolutions.value, len(nodes))

    def test_empty_predicate_requires_both_endpoints_to_be_zero(self) -> None:
        self.assertEqual(self.empty(None), 1)
        for head, tail, expected in (
            (0, 0, 1),
            (1, 0, 0),
            (0, 1, 0),
            (1, 1, 0),
            (0xFFFFFFFF, 0xFFFFFFFF, 0),
        ):
            linked_list = RuntimeLinkedList(4, head, tail)
            with self.subTest(head=head, tail=tail):
                self.assertEqual(
                    self.empty(ctypes.byref(linked_list)),
                    expected,
                )

    def test_clear_wrapper_forwards_list_and_null_cleanup_once(self) -> None:
        linked_list = RuntimeLinkedList(16, 0x11111111, 0x22222222)
        address = ctypes.addressof(linked_list)
        self.clear(ctypes.byref(linked_list))
        self.assertEqual(self.clear_calls.value, 1)
        self.assertEqual(self.clear_list.value, address)
        self.assertEqual(self.clear_cleanup.value, 0)
        self.assertEqual(
            (linked_list.node_size, linked_list.head, linked_list.tail),
            (16, 0x11111111, 0x22222222),
        )

    def test_all_stock_spans_and_adjacent_boundaries_are_exact(self) -> None:
        expected = {
            "head": (
                "002801d1002000e040687047",
                "52da3be9e77a64ae55928264f6f8b955"
                "294a7603e3dbcfaefab3b4150b2b52b3",
            ),
            "tail": (
                "002801d1002000e080687047",
                "6717bf57b1ac7ad781c851f7c28681c1"
                "78495a01508c9d99488d5d36ada09443",
            ),
            "next": (
                "00680844001d00687047",
                "2a717b6780c837377f451d1c683fff0e"
                "6406c048fc28554a03203e6ef5e3a128",
            ),
            "previous": (
                "0068084400687047",
                "10abde261a5ab42b61c57befe77bb9a1"
                "b8131964b4e24b9036b74e93366ce666",
            ),
            "length": (
                "38b5040000252000fff7e5ff04e06d1c"
                "01002000fff7ebff0028f8d1280032bd",
                "27641a54e1084d01df13666eb6430cb8"
                "0a978b18e0ce4091c954a60ae3bc8ffc",
            ),
            "empty": (
                "002801d1012008e04168002904d18068"
                "002801d1012000e000207047",
                "cf5902caebe020b900aca83cdc50964a"
                "9da9a4ba93ff742e08061b50daa3e350",
            ),
            "clear": (
                "80b50021fff777ff01bd",
                "0528fed662ee528664a6631b0b85ff07"
                "979195a55d4543a0e175074974c6801d",
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            body_hex, digest = expected[name]
            with self.subTest(name=name):
                self.assertEqual(body.hex(), body_hex)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        skipped_move = self.span(0x00482D22, 0x00482D88)
        self.assertEqual(len(skipped_move), 102)
        self.assertEqual(
            hashlib.sha256(skipped_move).hexdigest(),
            "723328d50c75adb0ac95e2bc70b3e934"
            "b1152c1176774f8cc2207761865b094e",
        )
        following_helpers = self.span(0x00482DAE, 0x00482DD8)
        self.assertEqual(len(following_helpers), 42)
        self.assertEqual(
            hashlib.sha256(following_helpers).hexdigest(),
            "3565b5bf9a474304896e0a7acdcab630"
            "e492df488323a00845064736babb0463",
        )

    def test_per_function_callers_dependencies_and_digests_are_exact(
        self,
    ) -> None:
        expected_callers = {
            "head": [
                0x0044CCEA, 0x0044D3A2, 0x0044D3E0, 0x0044D424,
                0x0044DC54, 0x0044FA2C, 0x00450510, 0x00450554,
                0x00450572, 0x00450778, 0x00450782, 0x004509E8,
                0x00450A8E, 0x00450AFC, 0x00452EE6, 0x004538DC,
                0x00453976, 0x004643B4, 0x004643EC, 0x004645F4,
                0x00482B6A, 0x00482C1A, 0x00482CA2, 0x00482D0A,
                0x00489324, 0x004B2108, 0x004B21A8, 0x004C70BE,
                0x005C2ECA, 0x005C2F10, 0x005C3196, 0x005C336A,
                0x005C5966, 0x005C5ACE, 0x005C5B88, 0x005C5BD2,
                0x005C69F8, 0x005C9CC8, 0x005C9F0A,
            ],
            "tail": [
                0x0044CA2E, 0x0044D3EC, 0x00482C46, 0x00482D40,
                0x005C3254, 0x005C608E, 0x005C6528, 0x005C6B34,
                0x005CA170, 0x005CA59E, 0x005CA752, 0x005CA896,
                0x005CB1E6, 0x005CB32C,
            ],
            "next": [
                0x0044CCF4, 0x0044D430, 0x0044DC5E, 0x0044FA38,
                0x0045051C, 0x0045057C, 0x00450904, 0x00450A9A,
                0x00452EF2, 0x00453930, 0x0045399C, 0x004643C6,
                0x0046440A, 0x004645FE, 0x00482C26, 0x00482C7E,
                0x00482CB6, 0x00482D16, 0x00489330, 0x004B2114,
                0x004B21B4, 0x004C70C8, 0x005C31E8, 0x005C3378,
                0x005C5976, 0x005C5AD6, 0x005C6A36, 0x005C9CD2,
            ],
            "previous": [
                0x0044CAA0, 0x00482B98, 0x00482C52, 0x00482C74,
                0x00482D36, 0x005C3262, 0x005C631C, 0x005C654E,
                0x005C6B9A, 0x005CA1A2, 0x005CA50A, 0x005CA806,
                0x005CA920, 0x005CB246, 0x005CB366,
            ],
            "length": [0x005C590E, 0x005C607E, 0x005C687C],
            "empty": [0x00453864, 0x005C5C98, 0x005C6AAE],
            "clear": [
                0x004539AC, 0x005C3216, 0x005C5BC8, 0x005C5BF2,
                0x005C9978, 0x005C9AF6, 0x005C9F2A,
            ],
        }
        expected_digests = {
            "head": "ac0f78901f957244e047d559519cf2e9"
                    "30b70bca8693e30646950af0cbdc79b1",
            "tail": "773de98d83bb937e8c354d9a76518bef"
                    "d775ef9032fb810a085e9d4e64a440b3",
            "next": "860b80fbab8b929d753cd67871111add"
                    "eea5abcff0334636b58550b955ac13b2",
            "previous": "231e4f1540bb13825760843195299b76"
                        "4a917938c7b21841a9cadfa6377a603b",
            "length": "62ca268d7974e451792f9a29dfa5b9b"
                      "0b7d02ce6e3cdc88aa58123c8efa9cd43",
            "empty": "7471361c8df74098c981b38129023559"
                     "aa244205bd8fef28adade3edffe20b1f",
            "clear": "638a711e6058275e5bd4badd77b9069e"
                     "5825aca53227ef79cc17c7da2a74b8ca",
        }
        expected_dependencies = {
            "head": [],
            "tail": [],
            "next": [],
            "previous": [],
            "length": [
                (0x00482D0A, 0x00482CD8, "fff7e5ff"),
                (0x00482D16, 0x00482CF0, "fff7ebff"),
            ],
            "empty": [],
            "clear": [(0x00482DA8, 0x00482C9A, "fff777ff")],
        }

        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interior = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
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
                for name, (start, end) in FUNCTIONS.items():
                    if target == start:
                        (callers if link else jumps)[name].append(address)
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[name].append((address, target, link))
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        for name in FUNCTIONS:
            digest = hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address in callers[name]
                )
            ).hexdigest()
            with self.subTest(name=name):
                self.assertEqual(callers[name], expected_callers[name])
                self.assertEqual(digest, expected_digests[name])
                self.assertEqual(
                    dependencies[name],
                    expected_dependencies[name],
                )
                self.assertEqual(jumps[name], [])
                self.assertEqual(interior[name], [])

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entry = {name: [] for name in FUNCTIONS}
        narrow_interior = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            for name, (start, end) in FUNCTIONS.items():
                if start in candidates:
                    narrow_entry[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in FUNCTIONS.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target)
                    )

        expected_stored = {
            "head": [(0x0044D5E4, 0x00482CD8)],
            "tail": [(0x0044D5F0, 0x00482CE4)],
            "next": [(0x0044D5E0, 0x00482CF0)],
            "previous": [(0x0044D5EC, 0x00482CFA)],
            "length": [],
            "empty": [],
            "clear": [],
        }
        for name in FUNCTIONS:
            with self.subTest(name=name):
                self.assertEqual(narrow_entry[name], [])
                self.assertEqual(narrow_interior[name], [])
                self.assertEqual(stored[name], expected_stored[name])

        stored_table = self.span(0x0044D5D8, 0x0044D5F8)
        self.assertEqual(
            hashlib.sha256(stored_table).hexdigest(),
            "bdc9beefc328b88e8f36b96b9026d1d"
            "63b49041a4d2ab1da2986fa1f9fad4911",
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_linked_list_get_head(",
            "open_cfw_runtime_linked_list_get_tail(",
            "open_cfw_runtime_linked_list_get_next(",
            "open_cfw_runtime_linked_list_get_previous(",
            "open_cfw_runtime_linked_list_get_length(",
            "open_cfw_runtime_linked_list_is_empty(",
            "open_cfw_runtime_linked_list_clear(",
            "0x00482C9BU",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_accessors.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
