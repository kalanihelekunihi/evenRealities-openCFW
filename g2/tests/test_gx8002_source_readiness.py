#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYZER = TOOLS / "analyze_gx8002_source_readiness.py"
SOURCE = ROOT / "components/shared/gx8002/runtime_gx8002_kws_model_boundary.c"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
WEIGHT_START = 0x1B15C
WEIGHT_SIZE = 120800


def load_analyzer():
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("analyze_gx8002_source_readiness", ANALYZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int32,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
)


class Ports(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("provider", PROVIDER)]


class GX8002SourceReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()
        cls.compiler = shutil.which("clang") or shutil.which("cc")
        if cls.compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "libgx8002_model_boundary.so"
        subprocess.run([
            cls.compiler, "-std=c11", "-O2", "-fPIC", "-shared",
            "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
            "-Wall", "-Wextra", "-Werror",
            "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.function = ctypes.CDLL(str(library)).open_cfw_gx8002_kws_model_load
        cls.function.argtypes = [ctypes.POINTER(Ports), ctypes.POINTER(ctypes.c_uint8),
                                 ctypes.c_size_t]
        cls.function.restype = ctypes.c_int32
        blob = BLOB.read_bytes()
        cls.weights = blob[WEIGHT_START:WEIGHT_START + WEIGHT_SIZE]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_exhaustive_partition_and_totals(self):
        self.assertEqual(self.report["partition"], {
            "spans": 17, "bytes": 326092, "contiguous": True,
            "overlaps": 0, "gaps": 0,
        })
        self.assertEqual(self.report["readiness"], {
            "reconstructible_mit_format_metadata": {"spans": 6, "bytes": 92},
            "typed_unsupported_external_boundary": {"spans": 11, "bytes": 326000},
            "unavailable_proprietary_codec_firmware": {"spans": 0, "bytes": 0},
        })
        self.assertEqual(self.report["blocking_residual"], {"spans": 11, "bytes": 326000})

    def test_selected_cluster_and_redistribution_are_fail_closed(self):
        selected = self.report["selected_cluster"]
        self.assertEqual((selected["start"], selected["end_exclusive"], selected["size"]),
                         (0x1B15C, 0x3893C, 120800))
        self.assertEqual(selected["boundary_license"], "MIT")
        self.assertEqual(selected["payload_source_license"], "NOASSERTION")
        self.assertEqual(selected["payload_redistribution_authority"], "unresolved")
        self.assertFalse(selected["production_routed"])
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["hardware_validation"], "deferred by project direction")

    def test_provider_loads_only_exact_authenticated_model(self):
        destination = (ctypes.c_uint8 * WEIGHT_SIZE)()
        capacities = []

        @PROVIDER
        def provider(_context, output, capacity, written):
            capacities.append(capacity)
            ctypes.memmove(output, self.weights, WEIGHT_SIZE)
            written[0] = WEIGHT_SIZE
            return 0

        ports = Ports(None, provider)
        self.assertEqual(self.function(ctypes.byref(ports), destination, WEIGHT_SIZE), 0)
        self.assertEqual(capacities, [WEIGHT_SIZE])
        self.assertEqual(bytes(destination), self.weights)

    def test_missing_provider_and_invalid_arguments_fail_closed(self):
        destination = (ctypes.c_uint8 * WEIGHT_SIZE)()
        missing = Ports(None, PROVIDER())
        self.assertEqual(self.function(ctypes.byref(missing), destination, WEIGHT_SIZE), 2)
        self.assertEqual(self.function(None, destination, WEIGHT_SIZE), 1)
        self.assertEqual(self.function(ctypes.byref(missing), None, WEIGHT_SIZE), 1)
        self.assertEqual(self.function(ctypes.byref(missing), destination, WEIGHT_SIZE - 1), 1)

    def test_wrong_identity_and_short_write_are_rejected_and_cleared(self):
        destination = (ctypes.c_uint8 * WEIGHT_SIZE)()

        @PROVIDER
        def wrong(_context, output, _capacity, written):
            ctypes.memmove(output, self.weights, WEIGHT_SIZE)
            output[7] ^= 0x01
            written[0] = WEIGHT_SIZE
            return 0

        self.assertEqual(self.function(ctypes.byref(Ports(None, wrong)),
                                       destination, WEIGHT_SIZE), 4)
        self.assertEqual(bytes(destination), b"\0" * WEIGHT_SIZE)

        @PROVIDER
        def short(_context, output, _capacity, written):
            output[0] = 0xA5
            written[0] = 1
            return 0

        self.assertEqual(self.function(ctypes.byref(Ports(None, short)),
                                       destination, WEIGHT_SIZE), 4)
        self.assertEqual(bytes(destination), b"\0" * WEIGHT_SIZE)

    def test_provider_failure_is_distinct_and_clears_destination(self):
        destination = (ctypes.c_uint8 * WEIGHT_SIZE)(*([0xA5] * WEIGHT_SIZE))

        @PROVIDER
        def failed(_context, output, _capacity, written):
            output[0] = 0x5A
            written[0] = 1
            return -7

        self.assertEqual(self.function(ctypes.byref(Ports(None, failed)),
                                       destination, WEIGHT_SIZE), 3)
        self.assertEqual(bytes(destination), b"\0" * WEIGHT_SIZE)

    def test_host_and_cortex_m55_objects_have_no_undefined_imports(self):
        host_object = Path(self.temporary.name) / "gx8002-model-host.o"
        subprocess.run([
            self.compiler, "-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
            "-fno-stack-protector", "-Wall", "-Wextra", "-Werror",
            "-I", str(SOURCE.parent),
            "-c", str(SOURCE), "-o", str(host_object),
        ], check=True, capture_output=True, text=True)
        undefined = subprocess.run(["nm", "-u", str(host_object)], check=True,
                                   capture_output=True, text=True).stdout.strip()
        self.assertEqual(undefined, "")

        target_object = Path(self.temporary.name) / "gx8002-model-m55.o"
        subprocess.run([
            self.compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-fno-stack-protector",
            "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
            "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent),
            "-c", str(SOURCE), "-o", str(target_object),
        ], check=True, capture_output=True, text=True)
        undefined = subprocess.run(["nm", "-u", str(target_object)], check=True,
                                   capture_output=True, text=True).stdout.strip()
        self.assertEqual(undefined, "")

    def test_analyzer_fails_closed_on_blob_change(self):
        original = self.analyzer.BLOB

        class ChangedBlob:
            @staticmethod
            def read_bytes():
                return b"\0" * 326092

        self.analyzer.BLOB = ChangedBlob()
        try:
            with self.assertRaises(self.analyzer.ReadinessError):
                self.analyzer.run_audit()
        finally:
            self.analyzer.BLOB = original

    def test_json_cli(self):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run([sys.executable, str(ANALYZER), "--json"],
                                cwd=ROOT, env=environment, check=True,
                                capture_output=True, text=True)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["selected_cluster"]["size"], WEIGHT_SIZE)
        self.assertEqual(parsed["source_owned_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
