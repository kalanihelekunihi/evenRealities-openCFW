from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party/tinyframe"
SHARED = ROOT / "components/shared/tinyframe"
SOURCE = SHARED / "runtime_tinyframe_g2_atomic_boundary_candidate.c"
FIXTURE = ROOT / "tests/fixtures/runtime_tinyframe_g2_atomic_boundary_candidate_host.c"
PRODUCTION_CONFIG = SNAPSHOT / "g2-production/TF_Config.h"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"


class TinyFrameG2AtomicBoundaryCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.clang = clang
        cls.compiler_version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        cls.tmp = tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-atomic-")
        temporary = Path(cls.tmp.name)
        common = [clang, "-O2", "-Wall", "-Wextra", "-Werror", "-fshort-enums",
                  "-I", str(SNAPSHOT / "g2-config"), "-I", str(SNAPSHOT),
                  "-I", str(SHARED)]
        core = temporary / "core.o"
        subprocess.run([*common,
                        "-DTF_Init=open_cfw_tinyframe_upstream_init",
                        "-DTF_InitStatic=open_cfw_tinyframe_upstream_init_static",
                        "-DTF_DeInit=open_cfw_tinyframe_upstream_deinit",
                        "-Dmemset=open_cfw_tinyframe_g2_memory_set",
                        "-c", str(SNAPSHOT / "TinyFrame.c"), "-o", str(core)],
                       check=True, capture_output=True, text=True)
        fixture = temporary / "fixture.o"
        subprocess.run([*common, "-fPIC", "-c", str(FIXTURE), "-o", str(fixture)],
                       check=True, capture_output=True, text=True)
        library = temporary / ("atomic.dylib" if sys.platform == "darwin" else "atomic.so")
        link = [clang, str(core), str(fixture),
                "-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin":
            link.append("-fPIC")
        subprocess.run([*link, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_tinyframe_g2_atomic_host_send.argtypes = [
            ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16
        ]
        cls.lib.open_cfw_tinyframe_g2_atomic_host_send.restype = ctypes.c_int
        cls.lib.open_cfw_tinyframe_g2_atomic_host_get.restype = ctypes.c_size_t
        cls.lib.open_cfw_tinyframe_g2_atomic_host_capture.restype = ctypes.POINTER(ctypes.c_uint8)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_stateless_boundary_preserves_master_wire_and_bookends(self):
        self.assertEqual(self.lib.open_cfw_tinyframe_g2_atomic_host_start(1), 1)
        payload = (ctypes.c_uint8 * 2)(0x10, 0x20)
        self.assertEqual(self.lib.open_cfw_tinyframe_g2_atomic_host_send(0x1234, payload, 2), 1)
        values = tuple(self.lib.open_cfw_tinyframe_g2_atomic_host_get(i) for i in range(6))
        self.assertEqual(values[0], 13)
        self.assertEqual(values[1], values[5])
        self.assertEqual(values[2:5], (100, 0xA5A5A5A5, 0x5A5A5A5A))
        self.assertEqual(bytes(self.lib.open_cfw_tinyframe_g2_atomic_host_capture()[:13]),
                         bytes.fromhex("01800000021234b7a31020180c"))

    def test_candidate_sources_are_exact(self):
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (3349, "295efb659b32e34a53cffe7bcd879960371607c45f32b2c95fb737acf1e476c0"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (2503, "f559bb661297997f7ee1babf119c976020a77d6e6d57096fd35318a65d9c717d"),
        )
        self.assertEqual(
            (PRODUCTION_CONFIG.stat().st_size,
             hashlib.sha256(PRODUCTION_CONFIG.read_bytes()).hexdigest()),
            (510, "427292d632399dd72d9a3f6a5f74959ca30e78cc54ddeb8ad34aa773f9a9b785"),
        )

    def test_target_live_atomic_function_closure_is_explicit(self):
        with tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-atomic-target-") as raw:
            temporary = Path(raw)
            flags = ["--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
                     "-fshort-enums", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
                     "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                     "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                     "-I", str(SNAPSHOT / "g2-compat"), "-I", str(SNAPSHOT / "g2-production"),
                     "-I", str(SNAPSHOT / "g2-config"),
                     "-I", str(SNAPSHOT), "-I", str(SHARED)]
            core = temporary / "core.o"
            subprocess.run([self.clang, *flags,
                            "-DTF_Init=open_cfw_tinyframe_upstream_init",
                            "-DTF_InitStatic=open_cfw_tinyframe_upstream_init_static",
                            "-DTF_DeInit=open_cfw_tinyframe_upstream_deinit",
                            "-Dmemset=open_cfw_tinyframe_g2_memory_set",
                            "-c", str(SNAPSHOT / "TinyFrame.c"), "-o", str(core)],
                           check=True, capture_output=True, text=True)
            boundary = temporary / "boundary.o"
            subprocess.run([self.clang, *flags, "-c", str(SOURCE), "-o", str(boundary)],
                           check=True, capture_output=True, text=True)
            sys.path.insert(0, str(ROOT / "tools"))
            import apollo_overlay

            graph = {}
            section_contracts = {}
            undefined = set()
            defined = set()
            for path in (core, boundary):
                data, sections = apollo_overlay.parse_elf32(path)
                symbols = apollo_overlay.parse_elf32_symbols(data, sections)
                undefined.update(item["name"] for item in symbols
                                 if item["name"] and int(item["section_index"]) == 0)
                defined.update(item["name"] for item in symbols
                               if item["name"] and int(item["section_index"]) != 0)
                for section in sections:
                    if not section["name"].startswith(".text.") or not int(section["size"]):
                        continue
                    deps = []
                    all_relocations = []
                    for relocation in sections:
                        if int(relocation["type"]) != 9 or int(relocation["info"]) != int(section["index"]):
                            continue
                        for index in range(int(relocation["size"]) // 8):
                            _offset, information = struct.unpack_from(
                                "<II", data, int(relocation["offset"]) + index * 8
                            )
                            name = symbols[information >> 8]["name"]
                            all_relocations.append([_offset, information & 0xFF, name])
                            if name and not name.startswith(".L") and name != "crc16_table":
                                deps.append(name)
                    graph[section["name"][6:]] = set(deps)
                    body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
                    section_contracts[section["name"][6:]] = [
                        len(body), hashlib.sha256(body).hexdigest(), all_relocations
                    ]

            roots = {"TF_Init", "TF_AddTypeListener", "TF_Accept", "TF_Respond",
                     "TF_Query_Multipart", "TF_Multipart_Payload", "TF_Multipart_Close", "TF_Tick"}
            reachable = set(roots)
            while True:
                expanded = reachable | {name for item in reachable for name in graph.get(item, ())
                                        if name in graph}
                if expanded == reachable:
                    break
                reachable = expanded
            self.assertEqual(reachable, {
                "TF_Init", "TF_AddTypeListener", "TF_Accept", "TF_AcceptChar",
                "TF_HandleReceivedMessage", "TF_Respond", "TF_SendFrame",
                "TF_Query_Multipart", "TF_Multipart_Payload", "TF_Multipart_Close", "TF_Tick",
                "TF_WriteImpl", "open_cfw_tinyframe_g2_memory_set",
                "open_cfw_tinyframe_upstream_init_static",
            })
            unresolved = undefined - defined
            self.assertEqual(unresolved & reachable, set())
            self.assertEqual(unresolved - {"malloc", "free"},
                             {"open_cfw_freertos_heap4_free", "open_cfw_freertos_heap4_malloc"})
            rows = [[name, *section_contracts[name]] for name in sorted(reachable)]
            serialized = json.dumps(rows, separators=(",", ":")).encode()
            if self.compiler_version.startswith("Apple clang version 21.0.0"):
                expected_contract = (
                    3390, 2102,
                    "0403dffc8730d70860e433975551ca0939e1c4576ef6f21fea3dc844c44b353a",
                )
            elif self.compiler_version.startswith("Homebrew clang version 22.1.8"):
                expected_contract = (
                    3466, 2195,
                    "a61c4395da031a480ed09f60ea245e5934d653c3085ebd1980bf4241dff17e4f",
                )
            else:
                self.fail(f"unreviewed TinyFrame target compiler: {self.compiler_version}")
            self.assertEqual(
                (sum(row[1] for row in rows), len(serialized), hashlib.sha256(serialized).hexdigest()),
                expected_contract,
            )

    def test_atomic_closure_is_production_routed_and_dual_profile_pinned(self):
        config = json.loads(OVERLAY_CONFIG.read_text())
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in {
                "open_cfw_tinyframe_g2_memory_set", "TF_WriteImpl",
                "open_cfw_tinyframe_upstream_init_static", "TF_Init",
                "TF_HandleReceivedMessage", "TF_AcceptChar", "TF_Accept",
                "TF_AddTypeListener", "TF_SendFrame", "TF_Respond",
                "TF_Query_Multipart", "TF_Multipart_Payload",
                "TF_Multipart_Close", "TF_Tick",
            }
        }
        expected = {
            "open_cfw_tinyframe_g2_memory_set": ((137368, 94, None), (139248, 94, None)),
            "TF_WriteImpl": ((137464, 16, None), (139344, 16, None)),
            "open_cfw_tinyframe_upstream_init_static": ((137480, 46, None), (139360, 46, None)),
            "TF_Init": ((137528, 80, None), (139408, 80, None)),
            "TF_HandleReceivedMessage": ((137608, 434, None), (139488, 434, None)),
            "TF_AcceptChar": ((138044, 450, 962), (139924, 450, 962)),
            "TF_Accept": ((139008, 36, None), (140888, 36, None)),
            "TF_AddTypeListener": ((139044, 370, None), (140924, 342, None)),
            "TF_SendFrame": ((139416, 1176, 1688), (141268, 1270, 1782)),
            "TF_Respond": ((141104, 28, None), (143052, 28, None)),
            "TF_Query_Multipart": ((141132, 26, None), (143080, 26, None)),
            "TF_Multipart_Payload": ((141160, 402, 914), (143108, 412, 924)),
            "TF_Multipart_Close": ((142076, 78, None), (144032, 78, None)),
            "TF_Tick": ((142156, 154, None), (144112, 154, None)),
        }
        self.assertEqual(set(leaves), set(expected))
        for name, (apple_pin, linux_pin) in expected.items():
            leaf = leaves[name]
            apple = leaf["expected"]
            linux = leaf["toolchain_profiles"]["linux-clang"].get("expected", apple)
            self.assertEqual((apple["offset"], apple["size"], apple.get("closure_size")), apple_pin)
            self.assertEqual((linux["offset"], linux["size"], linux.get("closure_size")), linux_pin)

        patches = [
            item for item in config["patch_sites"]
            if item["target_function"] in {
                "TF_Init", "TF_AddTypeListener", "TF_Accept", "TF_Respond",
                "TF_Query_Multipart", "TF_Multipart_Payload",
                "TF_Multipart_Close", "TF_Tick",
            }
        ]
        self.assertEqual(
            [(item["runtime_address"], item["expected_size"], item["target_function"])
             for item in patches],
            [(0x4917D2, 102, "TF_Init"), (0x491962, 134, "TF_AddTypeListener"),
             (0x491B9A, 28, "TF_Accept"), (0x49225A, 12, "TF_Respond"),
             (0x492266, 18, "TF_Query_Multipart"),
             (0x492278, 8, "TF_Multipart_Payload"),
             (0x492280, 8, "TF_Multipart_Close"), (0x492288, 110, "TF_Tick")],
        )

        manifest = json.loads(MANIFEST.read_text())
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(
            (main["provider"]["size"], main["provider"]["sha256"]),
            (3688808, "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c"),
        )
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            (4467302, "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"),
        )
        tinyframe_regions = [item for item in main["regions"]
                             if item["name"].startswith("apollo_tinyframe_")]
        self.assertEqual(
            (sum(item["address_status"] == "source_compiled" for item in tinyframe_regions),
             sum(item["address_status"] == "generated_source_entry_replacement"
                 for item in tinyframe_regions),
             sum(item["address_status"] == "generated_alignment" for item in tinyframe_regions)),
            (17, 8, 8),
        )


if __name__ == "__main__":
    unittest.main()
