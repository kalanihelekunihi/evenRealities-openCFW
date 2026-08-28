#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYZER = TOOLS / "analyze_gx8002_source_readiness.py"
DIRECTORY = ROOT / "components/shared/gx8002"
COMMON = DIRECTORY / "runtime_gx8002_kws_model_boundary.c"
SRAM_SOURCE = DIRECTORY / "runtime_gx8002_image_a_sram_text_boundary.c"
STAGE1_SOURCE = DIRECTORY / "runtime_gx8002_image_a_stage1_boundary.c"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
SEGMENTS = {
    "open_cfw_gx8002_image_a_sram_text_load": (0x15414, 12516),
    "open_cfw_gx8002_image_a_stage1_load": (0x958C, 12288),
}


def load_analyzer():
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("gx8002_readiness_wave5", ANALYZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))


class Ports(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("provider", PROVIDER)]


class GX8002ImageASramStage1BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()
        cls.compiler = shutil.which("clang") or shutil.which("cc")
        if cls.compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "libgx8002_wave5.so"
        flags = ["-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
                 "-fno-stack-protector", "-Wall", "-Wextra", "-Werror",
                 "-I", str(DIRECTORY)]
        subprocess.run([cls.compiler, *flags, "-fPIC", "-shared", str(COMMON),
                        str(SRAM_SOURCE), str(STAGE1_SOURCE), "-o", str(library)],
                       check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(library))
        cls.functions = {}
        for name in SEGMENTS:
            function = getattr(loaded, name)
            function.argtypes = [ctypes.POINTER(Ports), ctypes.POINTER(ctypes.c_uint8),
                                 ctypes.c_size_t]
            function.restype = ctypes.c_int32
            cls.functions[name] = function
        cls.blob = BLOB.read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_analyzer_pins_both_honest_boundaries(self):
        sram = self.report["prior_cluster_wave5_primary"]
        self.assertEqual((sram["name"], sram["start"], sram["end_exclusive"], sram["size"]),
                         ("image_a_sram_text", 0x15414, 0x184F8, 12516))
        self.assertEqual((sram["iram"], sram["entry"], sram["handler_set"]),
                         ("[0x10023400, 0x100264E4)", "0x10023500",
                          ["0x10023640", "0x10025574"]))
        stage1 = self.report["prior_cluster_wave5_additional"]
        self.assertEqual((stage1["name"], stage1["start"], stage1["end_exclusive"],
                          stage1["size"]), ("image_a_stage1", 0x958C, 0xC58C, 12288))
        self.assertEqual(stage1["stage1_block_crc32_mpeg2"], "0x21C58EDB")
        self.assertIn("no mapping invented", stage1["runtime_mapping"])
        for cluster in (sram, stage1):
            self.assertIn("no signature invented", cluster["internal_abi"])
            self.assertEqual(cluster["boundary_license"], "MIT")
            self.assertEqual(cluster["payload_source_license"], "NOASSERTION")
            self.assertEqual(cluster["payload_redistribution_authority"], "unresolved")
            self.assertFalse(cluster["production_routed"])

    def test_exact_local_segments_are_accepted(self):
        for name, (start, size) in SEGMENTS.items():
            body = self.blob[start:start + size]
            output = (ctypes.c_uint8 * size)()

            @PROVIDER
            def provider(_context, destination, capacity, written, body=body, size=size):
                self.assertEqual(capacity, size)
                ctypes.memmove(destination, body, size)
                written[0] = size
                return 0

            self.assertEqual(self.functions[name](ctypes.byref(Ports(None, provider)),
                                                  output, size), 0)
            self.assertEqual(bytes(output), body)

    def test_each_boundary_rejects_mutation_and_clears(self):
        for name, (start, size) in SEGMENTS.items():
            body = self.blob[start:start + size]
            output = (ctypes.c_uint8 * size)()

            @PROVIDER
            def mutated(_context, destination, _capacity, written,
                        body=body, size=size):
                ctypes.memmove(destination, body, size)
                destination[size // 2] ^= 1
                written[0] = size
                return 0

            self.assertEqual(self.functions[name](ctypes.byref(Ports(None, mutated)),
                                                  output, size), 4)
            self.assertEqual(bytes(output), b"\0" * size)

    def test_fail_closed_statuses_use_reviewed_common_verifier(self):
        name = "open_cfw_gx8002_image_a_sram_text_load"
        size = SEGMENTS[name][1]
        output = (ctypes.c_uint8 * size)(*([0xA5] * size))
        self.assertEqual(self.functions[name](ctypes.byref(Ports(None, PROVIDER())),
                                              output, size), 2)

        @PROVIDER
        def short(_context, destination, _capacity, written):
            destination[0] = 0xA5
            written[0] = 1
            return 0

        self.assertEqual(self.functions[name](ctypes.byref(Ports(None, short)),
                                              output, size), 4)
        self.assertEqual(bytes(output), b"\0" * size)

    def test_host_and_cortex_m55_objects_have_only_reviewed_provider_edge(self):
        for target, target_flags in (
            ("host", []),
            ("m55", ["--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb"]),
        ):
            objects = []
            for source in (COMMON, SRAM_SOURCE, STAGE1_SOURCE):
                output = Path(self.temporary.name) / f"{target}-{source.stem}.o"
                subprocess.run([
                    self.compiler, *target_flags, "-std=c11", "-Oz", "-ffreestanding",
                    "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                    "-I", str(DIRECTORY), "-c", str(source), "-o", str(output),
                ], check=True, capture_output=True, text=True)
                objects.append(output)
            undefined = subprocess.run(["nm", "-u", *map(str, objects)], check=True,
                                       capture_output=True, text=True).stdout
            symbols = [line.rsplit(maxsplit=1)[-1].lstrip("_")
                       for line in undefined.splitlines()
                       if line.strip() and not line.rstrip().endswith(":")]
            self.assertEqual(symbols, ["open_cfw_gx8002_authenticated_segment_load"] * 2)


if __name__ == "__main__":
    unittest.main()
