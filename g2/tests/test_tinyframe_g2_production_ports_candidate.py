from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/tinyframe/runtime_tinyframe_g2_production_ports_candidate.c"
FIXTURE = ROOT / "tests/fixtures/runtime_tinyframe_g2_production_ports_candidate_host.c"
SNAPSHOT = ROOT / "third_party/tinyframe"
ADAPTER = ROOT / "components/shared/tinyframe"


class TinyFrameG2ProductionPortsCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang: raise unittest.SkipTest("clang is unavailable")
        cls.tmp = tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-ports-")
        temporary = Path(cls.tmp.name)
        library = temporary / ("ports.dylib" if sys.platform == "darwin" else "ports.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", "-fshort-enums",
                   "-I", str(SNAPSHOT / "g2-config"), "-I", str(SNAPSHOT),
                   "-I", str(ADAPTER), str(FIXTURE),
                   "-dynamiclib" if sys.platform == "darwin" else "-shared"]
        if sys.platform != "darwin": command.append("-fPIC")
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_tinyframe_g2_production_host_init.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_tinyframe_g2_production_host_init.restype = ctypes.c_size_t
        cls.lib.open_cfw_tinyframe_g2_production_host_get.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_tinyframe_g2_production_host_get.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_concrete_ports_bind_heap_and_retained_transport(self):
        self.lib.open_cfw_tinyframe_g2_production_host_reset()
        self.assertEqual(self.lib.open_cfw_tinyframe_g2_production_host_init(1), 0x12345678)
        self.lib.open_cfw_tinyframe_g2_production_host_exercise()
        self.assertEqual(tuple(self.lib.open_cfw_tinyframe_g2_production_host_get(i) for i in range(6)),
                         (1, 0x7160, 0x20001000, 0x20002000, 0x123, 100))
        self.assertTrue(all(self.lib.open_cfw_tinyframe_g2_production_host_get(i) for i in range(6, 10)))

    def test_source_and_transport_oracles_are_pinned(self):
        self.assertEqual(
            (SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
            (2298, "c96a6d3beb02e8ff7c7ae07aeb6882835cf5113816929d7b7fc107672d4a72f9"),
        )
        self.assertEqual(
            (FIXTURE.stat().st_size, hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),
            (2628, "8c7a22984c0c773bc87c90322578c15cf64df4e871d99fb319dc54ec4cd9c2ed"),
        )
        image = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
        base = 0x438000
        self.assertEqual(hashlib.sha256(image[0x541790-base:0x5417A4-base]).hexdigest(),
                         "f9ba82957a18e3ae966a6f8b6af0d7160d2ba237a61024b98cd5c938b8734d67")
        self.assertEqual(hashlib.sha256(image[0x584C98-base:0x584DB6-base]).hexdigest(),
                         "0a13941f278f566dff230b8fea27c85b231070ed2109d5b490ef48aa1943d18c")

    def test_target_candidate_compiles(self):
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        with tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-ports-target-") as raw:
            target = Path(raw) / "ports.o"
            subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-O2", "-ffreestanding", "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                            "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                            "-fno-asynchronous-unwind-tables",
                            "-I", str(SNAPSHOT / "g2-compat"), "-I", str(SNAPSHOT / "g2-config"),
                            "-I", str(SNAPSHOT), "-I", str(ADAPTER), "-c", str(SOURCE), "-o", str(target)],
                           check=True, capture_output=True)
            sys.path.insert(0, str(ROOT / "tools"))
            import apollo_overlay
            data, sections = apollo_overlay.parse_elf32(target)
            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            expected = {
                ".text.open_cfw_tinyframe_g2_init_production": (
                    26, "41d58e9a8bbe87a0af310faab3ad0695dfd1bf83bc6abe8b2b318198976c2f37",
                    [(4, 47, "open_cfw_tinyframe_g2_init_production.ports"),
                     (8, 48, "open_cfw_tinyframe_g2_init_production.ports"),
                     (12, 10, "open_cfw_tinyframe_g2_configure"),
                     (22, 30, "open_cfw_tinyframe_g2_init")],
                ),
                ".text.open_cfw_tinyframe_g2_production_allocate": (
                    4, "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f",
                    [(0, 30, "open_cfw_freertos_heap4_malloc")],
                ),
                ".text.open_cfw_tinyframe_g2_production_release": (
                    4, "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f",
                    [(0, 30, "open_cfw_freertos_heap4_free")],
                ),
                ".text.open_cfw_tinyframe_g2_production_write": (
                    4, "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f",
                    [(0, 30, "open_cfw_retained_sync_transport_write")],
                ),
                ".text.open_cfw_tinyframe_g2_production_vlog": (
                    2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", [],
                ),
                ".rodata.open_cfw_tinyframe_g2_init_production.ports": (
                    20, "de47c9b27eb8d300dbb5f2c353e632c393262cf06340c4fa7f1b40c4cbd36f90",
                    [(0, 2, "open_cfw_tinyframe_g2_production_allocate"),
                     (4, 2, "open_cfw_tinyframe_g2_production_release"),
                     (8, 2, "open_cfw_tinyframe_g2_production_write"),
                     (12, 2, "open_cfw_tinyframe_g2_production_vlog")],
                ),
            }
            for name, (size, digest, expected_relocations) in expected.items():
                section = apollo_overlay.section_named(sections, name)
                body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
                relocations = []
                for relocation_section in sections:
                    if int(relocation_section["type"]) != 9 or int(relocation_section["info"]) != int(section["index"]):
                        continue
                    for index in range(int(relocation_section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II", data, int(relocation_section["offset"]) + index * 8
                        )
                        relocations.append((offset, information & 0xFF, symbols[information >> 8]["name"]))
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest(), relocations),
                                 (size, digest, expected_relocations))


if __name__ == "__main__": unittest.main()
