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
SOURCE = DIRECTORY / "runtime_gx8002_backup_runtime_boundary.c"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
START = 0x3B940
SIZE = 79132


def load_analyzer():
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("gx8002_readiness_backup", ANALYZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))


class Ports(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("provider", PROVIDER)]


class GX8002BackupRuntimeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()
        cls.compiler = shutil.which("clang") or shutil.which("cc")
        if cls.compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "libgx8002_backup.so"
        flags = ["-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
                 "-fno-stack-protector", "-Wall", "-Wextra", "-Werror",
                 "-I", str(DIRECTORY)]
        subprocess.run([cls.compiler, *flags, "-fPIC", "-shared", str(COMMON),
                        str(SOURCE), "-o", str(library)], check=True,
                       capture_output=True, text=True)
        cls.function = ctypes.CDLL(str(library)).open_cfw_gx8002_backup_runtime_load
        cls.function.argtypes = [ctypes.POINTER(Ports), ctypes.POINTER(ctypes.c_uint8),
                                 ctypes.c_size_t]
        cls.function.restype = ctypes.c_int32
        blob = BLOB.read_bytes()
        cls.body = blob[START:START + SIZE]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_latest_cluster_is_exact_and_not_routed(self):
        cluster = self.report["prior_cluster"]
        self.assertEqual((cluster["start"], cluster["end_exclusive"], cluster["size"]),
                         (0x3B940, 0x4EE5C, SIZE))
        self.assertEqual(cluster["entry"], "0x10003100")
        self.assertEqual(cluster["iram"], "[0x10003000, 0x1001651C)")
        self.assertEqual(cluster["boundary_license"], "MIT")
        self.assertEqual(cluster["payload_source_license"], "NOASSERTION")
        self.assertEqual(cluster["payload_redistribution_authority"], "unresolved")
        self.assertFalse(cluster["production_routed"])

    def test_exact_local_provider_is_accepted(self):
        output = (ctypes.c_uint8 * SIZE)()

        @PROVIDER
        def provider(_context, destination, capacity, written):
            self.assertEqual(capacity, SIZE)
            ctypes.memmove(destination, self.body, SIZE)
            written[0] = SIZE
            return 0

        self.assertEqual(self.function(ctypes.byref(Ports(None, provider)), output, SIZE), 0)
        self.assertEqual(bytes(output), self.body)

    def test_missing_mutated_short_and_failed_providers_fail_closed(self):
        output = (ctypes.c_uint8 * SIZE)(*([0xA5] * SIZE))
        self.assertEqual(self.function(ctypes.byref(Ports(None, PROVIDER())), output, SIZE), 2)

        @PROVIDER
        def mutated(_context, destination, _capacity, written):
            ctypes.memmove(destination, self.body, SIZE)
            destination[101] ^= 1
            written[0] = SIZE
            return 0

        self.assertEqual(self.function(ctypes.byref(Ports(None, mutated)), output, SIZE), 4)
        self.assertEqual(bytes(output), b"\0" * SIZE)

        @PROVIDER
        def short(_context, destination, _capacity, written):
            destination[0] = 0xA5
            written[0] = 1
            return 0

        self.assertEqual(self.function(ctypes.byref(Ports(None, short)), output, SIZE), 4)
        self.assertEqual(bytes(output), b"\0" * SIZE)

        @PROVIDER
        def failed(_context, destination, _capacity, written):
            destination[0] = 0x5A
            written[0] = 1
            return -1

        self.assertEqual(self.function(ctypes.byref(Ports(None, failed)), output, SIZE), 3)
        self.assertEqual(bytes(output), b"\0" * SIZE)

    def test_invalid_arguments(self):
        output = (ctypes.c_uint8 * SIZE)()
        ports = Ports(None, PROVIDER())
        self.assertEqual(self.function(None, output, SIZE), 1)
        self.assertEqual(self.function(ctypes.byref(ports), None, SIZE), 1)
        self.assertEqual(self.function(ctypes.byref(ports), output, SIZE - 1), 1)

    def test_host_and_cortex_m55_closure_has_no_undefined_symbols(self):
        for target, target_flags in (
            ("host", []),
            ("m55", ["--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb"]),
        ):
            objects = []
            for source in (COMMON, SOURCE):
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
            # The wrapper's one reference is resolved by the common object; no other import exists.
            symbols = [line.rsplit(maxsplit=1)[-1].lstrip("_")
                       for line in undefined.splitlines()
                       if line.strip() and not line.rstrip().endswith(":")]
            self.assertEqual(symbols, ["open_cfw_gx8002_authenticated_segment_load"])


if __name__ == "__main__":
    unittest.main()
