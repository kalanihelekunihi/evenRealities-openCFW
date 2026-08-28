# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch application packet batch 12."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
PACKET = TOUCH / "runtime_touch_application_packet_pipeline.c"
STATE = TOUCH / "runtime_touch_application_state_pipeline.c"
LEAF = TOUCH / "runtime_touch_leaf_primitives.c"
RECORD = TOUCH / "runtime_touch_record_primitives.c"
FIXTURE = ROOT / "tests/fixtures/touch_application_state_pipeline_host.c"
SOURCES = (PACKET, STATE, LEAF, RECORD)
U8 = ctypes.c_uint8
U8P = ctypes.POINTER(U8)


def put16(buffer, offset, value):
    buffer[offset] = value & 0xFF
    buffer[offset + 1] = (value >> 8) & 0xFF


def get16(buffer, offset):
    return buffer[offset] | (buffer[offset + 1] << 8)


def put32(buffer, offset, value):
    for index in range(4):
        buffer[offset + index] = (value >> (8 * index)) & 0xFF


def get32(buffer, offset):
    return sum(buffer[offset + index] << (8 * index) for index in range(4))


def mask3(words, mask, flags):
    return [((word & ~mask) | (mask if flags & (4 >> index) else 0)) & 0xFFFFFFFF
            for index, word in enumerate(words)]


class PointerRegistry:
    def __init__(self, library):
        self.library = library
        self.next_token = 1
        self.keepalive = []

    def store(self, owner, offset, pointee):
        token = self.next_token
        self.next_token += 1
        self.keepalive.append(pointee)
        self.library.open_cfw_touch_host_register_pointer(token, pointee)
        put32(owner, offset, token)


class TouchApplicationPacketPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_application_packet.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-DOPEN_CFW_TOUCH_HOST_POINTER_RESOLVER",
            "-I", str(TOUCH), *(str(source) for source in SOURCES),
            str(FIXTURE), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_host_register_pointer.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_packet_2248_build_entry.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, U8P, U8P]
        cls.lib.open_cfw_touch_packet_2248_build_entry.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_packet_23a4_build_group.argtypes = [ctypes.c_uint32, U8P]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def make_graph(self, mode=1):
        registry = PointerRegistry(self.lib)
        context = (U8 * 0x38)()
        root = (U8 * 0x40)()
        global_config = (U8 * 0x80)()
        objects = (U8 * 144)()
        object_root = (U8 * 0x90)()
        records = (U8 * 30)()
        descriptors = (U8 * 60)()
        map0 = (U8 * 20)()
        map1 = (U8 * 16)()
        output0 = (U8 * (5 * 28))()
        output1 = (U8 * (4 * 44))()
        first_list = (U8 * 16)()
        second_list = (U8 * 16)()
        registry.store(context, 0, root)
        registry.store(context, 4, global_config)
        registry.store(context, 8, global_config)
        registry.store(context, 12, objects)
        registry.store(context, 16, descriptors)
        registry.store(context, 0x14, first_list)
        registry.store(context, 0x18, second_list)
        registry.store(context, 0x28, output0)
        registry.store(context, 0x2C, output1)
        registry.store(context, 0x30, map0)
        registry.store(context, 0x34, map1)
        registry.store(objects, 0, object_root)
        registry.store(objects, 4, records)
        objects[0x7A] = mode
        objects[0x84] = 2
        objects[0x8C] = 0x5A
        put16(objects, 0x80, 9)
        object_root[0x2E], object_root[0x2F] = 0x11, 0x22
        object_root[0x30], object_root[0x31] = 3, 4
        object_root[0x33] = 5
        records[9], records[19] = 0x66, 0x77
        put16(descriptors, 0x0C, 0x2A)
        put16(descriptors, 0x0E, 0x20)
        put16(descriptors, 0x1A, 0x1234)
        put16(descriptors, 0x1C, 0x5678)
        descriptors[0x20] = 2
        put16(descriptors, 0x2C, 7)
        descriptors[0x34] = 1
        put16(descriptors, 0x36, 3)
        descriptors[0x38] = 1
        for index in range(5):
            put16(map0, index * 4, 0)
            put16(map0, index * 4 + 2, index % 2)
        for index in range(4):
            put16(map1, index * 4, 0)
            put16(map1, index * 4 + 2, index % 2)
        return {
            "registry": registry, "context": context, "root": root,
            "global": global_config, "objects": objects,
            "object_root": object_root, "records": records,
            "descriptors": descriptors, "map0": map0, "map1": map1,
            "output0": output0, "output1": output1,
            "first_list": first_list, "second_list": second_list,
        }

    def test_build_entry_group0_non_mode1(self):
        graph = self.make_graph(mode=2)
        output = (U8 * 28)()
        result = self.lib.open_cfw_touch_packet_2248_build_entry(
            0, 0, output, graph["context"])
        self.assertEqual(result, 1)
        self.assertEqual(get32(output, 0x18), 0x5A000000)
        self.assertEqual(get32(output, 0x0C), 0x0002C006)
        self.assertEqual(get32(output, 0x10), 0x00430011)

    def test_build_entry_group1_mode1_preamble_and_scale(self):
        graph = self.make_graph(mode=1)
        global_config = graph["global"]
        global_config[0x5D:0x61] = (1, 2, 3, 4)
        output = (U8 * 48)()
        result = self.lib.open_cfw_touch_packet_2248_build_entry(
            1, 0, output, graph["context"])
        self.assertEqual(result, 0)
        expected0 = 4 | (1 << 4) | (2 << 8) | ((0x2A << 16) & 0x003F0000) | (3 << 24)
        self.assertEqual(get32(output, 0), expected0)
        self.assertEqual(get32(output, 4), 0x56781234)
        self.assertEqual(get32(output, 8), 0x00020000)
        self.assertEqual(get32(output, 20 + 0x18), 0x5A000000)
        expected_scale = (((8 - 1) << 16) & 0x0FFF0000) | (2 << 28) | (1 << 30) | 3
        self.assertEqual(get32(output, 20 + 0x14), expected_scale)

    def test_build_group0_masks_and_stride(self):
        graph = self.make_graph(mode=2)
        root, global_config = graph["root"], graph["global"]
        first_list, second_list, output = graph["first_list"], graph["second_list"], graph["output0"]
        put16(root, 0x0C, 1)
        root[0x2C] = 1
        first_list[5] = 1
        second_list[5] = 3
        global_config[0x75] = 2
        global_config[0x64] = 5
        global_config[0x74] = 0
        global_config[0x63] = 3
        for item in range(5):
            for word in range(3):
                put32(output, item * 28 + word * 4, 0xFFFFFFFF)
        self.lib.open_cfw_touch_packet_23a4_build_group(0, graph["context"])
        for item in range(5):
            words = [get32(output, item * 28 + word * 4) for word in range(3)]
            self.assertEqual(words, mask3([0xFFFFFFFF] * 3, 0x0A, 5))
            self.assertEqual(get32(output, item * 28 + 0x18), 0x5A000000)

    def test_build_group1_mode1_child_mask_and_stride(self):
        graph = self.make_graph(mode=1)
        registry = graph["registry"]
        root, global_config, objects = graph["root"], graph["global"], graph["objects"]
        first_list, output = graph["first_list"], graph["output1"]
        descriptor_list = (U8 * (2 * 8))()
        child_list = (U8 * (2 * 8))()
        registry.store(objects, 8, descriptor_list)
        registry.store(descriptor_list, 0, child_list)
        registry.store(descriptor_list, 8, child_list)
        descriptor_list[5] = 2
        descriptor_list[13] = 2
        child_list[5], child_list[13] = 2, 4
        put16(root, 0x0C, 1)
        root[0x2C] = 0
        first_list[5] = 1
        global_config[0x74] = 4
        global_config[0x6B] = 5
        global_config[0x68] = 2
        self.lib.open_cfw_touch_packet_23a4_build_group(1, graph["context"])
        for item in range(4):
            base = item * 44 + 20
            expected = mask3([0, 0, 0], 1 << 1, 5)
            expected = mask3(expected, (1 << 2) | (1 << 4), 2)
            self.assertEqual([get32(output, base + word * 4) for word in range(3)], expected)
            self.assertEqual(get32(output, item * 44), get32(output, 0))

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        objects = []
        for source in SOURCES:
            output = Path(self.temp.name) / (source.stem + "-batch12.o")
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            objects.append(output)
        defined, undefined = set(), set()
        for output in objects:
            listing = subprocess.run([nm, "-g", str(output)], check=True,
                                     capture_output=True, text=True).stdout
            for line in listing.splitlines():
                fields = line.split()
                if len(fields) >= 2 and fields[-2] == "U":
                    undefined.add(fields[-1])
                elif len(fields) >= 3 and fields[-2].upper() in {"T", "D", "B", "R"}:
                    defined.add(fields[-1])
        self.assertEqual(undefined - defined, set())


if __name__ == "__main__":
    unittest.main()
