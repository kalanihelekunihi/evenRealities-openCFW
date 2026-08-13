from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_nanopb_decode_varint_candidate as candidate_contract

sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay


SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint.c"
HEADER = SOURCE.with_suffix(".h")
CANDIDATE = SOURCE.with_name("runtime_nanopb_decode_varint_candidate.c")
PRODUCTION_FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_decode_varint_production_host.c"
)
CANDIDATE_FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_decode_varint_candidate_host.c"
)
UPSTREAM = ROOT / "third_party/nanopb/pb_decode.c"
SNAPSHOT = ROOT / "third_party/nanopb"
CONFIG_HEADER = SNAPSHOT / "g2-config/pb_g2_options.h"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
NOTICE = ROOT / "components/apollo_main/core_overlay/NOTICE.md"
EVIDENCE = ROOT / "components/apollo_main/core_overlay/EVIDENCE.md"
AUDIT = ROOT / "docs/research/nanopb-decode-varint-source-candidate-audit.md"

FUNCTION = "open_cfw_nanopb_decode_varint"
SEAM = "open_cfw_nanopb_readbyte"
SECTION = ".text." + FUNCTION
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
CANDIDATE_PATH = CANDIDATE.relative_to(ROOT).as_posix()
START = 0x0048_F5B8
END = 0x0048_F628
READBYTE = 0x0048_F454
RUN_BASE = 0x0043_8000
PREAMBLE = 32
ERROR = b"varint overflow\0"

LOCAL_PINS = {
    SOURCE: (
        2_224,
        "b1de68b98ee043bd07d1e10706166a13b13693534e382705bbad6866411fbe05",
    ),
    HEADER: (
        2_574,
        "73b98e49e6b97a84365b8eae582db2b0a65242808ce7de3bb22a0be44d6344ce",
    ),
    PRODUCTION_FIXTURE: (
        3_093,
        "d4d0b4e3277a73eff9b68fc78e5bcbd266b76f50332c60de72252775caa854bd",
    ),
}

TARGET_FLAGS = candidate_contract.TARGET_FLAGS
PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (
            1_244,
            "29cebc44eddfd9c79aceccf6da2bec1dd577c555619f3a2b9b0c74500daea7a7",
        ),
        "text_size": 128,
        "text_sha256": (
            "b3f040de87b4fd22ba1e66c81121194d"
            "daa03f56253b5d9e0a322a9671247e94"
        ),
        "text_relocations": [
            (24, 10, SEAM),
            (108, 49, ".L.str"),
            (112, 50, ".L.str"),
        ],
        "runtime": 0x007B_2560,
        "relocated_sha256": (
            "b518bc546a90560c6f2f4dc4add6af92"
            "83e05e20cc0eef00edf7a906c2bb600a"
        ),
        "closure_sha256": (
            "7a2fd744206ecd66e3188dfcb4ab3d30"
            "b6ed59b005b5a023ad7be561ee5f1327"
        ),
        "overlay": (
            128_264,
            "742e44dd839010c3c14ae59419fc06bcd50a7fe91e7ba06b4946f5c4154c870b",
        ),
        "component": (
            3_651_660,
            "ea39a91f574b464d9071e581f5104d870e1f7e484d52de9b86407f0a90ac5d2e",
        ),
        "predecessor_target": 0x007B_2C40,
        "skip_string_target": 0x007B_2C4C,
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (
            1_220,
            "0f19f9419ddc74d50e58f5e63737fe7224de35fdf7a0395267e987748e5064ed",
        ),
        "text_size": 124,
        "text_sha256": (
            "e820aa1b54f20ec1454462d356562177"
            "f8d03d98f21dff4bba77fa39fe282fa5"
        ),
        "text_relocations": [
            (24, 10, SEAM),
            (104, 49, ".L.str"),
            (108, 50, ".L.str"),
        ],
        "runtime": 0x007B_2C80,
        "relocated_sha256": (
            "a9894de4e5f2d29750822d203e19cab1"
            "afa5f1dea85edb7bfcb72c74f7326a37"
        ),
        "closure_sha256": (
            "3bc2300414cd1030f838cad1e9804e9d"
            "7f4c375c3ef43524d6e2681036778083"
        ),
        "overlay": (
            132_888,
            "7036c0e07a36376e5d98700c922ffeec7a6826388b75060a2b98b4228a411c61",
        ),
        "component": (
            3_656_284,
            "d5daf89121f44a61b303fa953da78550edd31e9159cf9b0b397aeb1b5cfef54d",
        ),
        "predecessor_target": 0x007B_3360,
        "skip_string_target": 0x007B_336C,
    },
}


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


class HostResult(ctypes.Structure):
    _fields_ = candidate_contract.HostResult._fields_

    def tuple(self) -> tuple[int, ...]:
        return (
            self.status,
            self.value,
            self.bytes_left,
            self.consumed,
            self.calls,
            self.error,
        )


class NanopbDecodeVarintProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed compiler: {version!r}")
        cls.pins = PROFILE_PINS[cls.profile]
        if cls.clang != cls.pins["compiler"] or version != cls.pins["version"]:
            raise AssertionError((cls.clang, version, cls.pins))

        (ROOT / "build").mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-varint-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "production-a.o", temporary / "production-b.o"]
        for output in cls.objects:
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    SOURCE_PATH,
                    "-o",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        library = temporary / (
            "nanopb-varint-production.dylib"
            if sys.platform == "darwin"
            else "nanopb-varint-production.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT),
            "-I",
            str(SNAPSHOT),
            "-include",
            str(CONFIG_HEADER),
            str(SOURCE),
            str(CANDIDATE),
            str(PRODUCTION_FIXTURE),
            str(CANDIDATE_FIXTURE),
            str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.runners = [
            cls.library.open_cfw_test_nanopb_run_production,
            cls.library.open_cfw_test_nanopb_run_candidate,
            cls.library.open_cfw_test_nanopb_run_upstream,
        ]
        for function in cls.runners:
            function.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint64,
                ctypes.POINTER(HostResult),
            ]
            function.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_host(
        self,
        function: ctypes._CFuncPtr,
        data: bytes,
        bytes_left: int,
        fail_call: int,
        preexisting_error: int,
        initial_value: int,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            ctypes.memmove(storage, data, len(data))
        result = HostResult()
        function(
            storage,
            len(data),
            bytes_left,
            fail_call,
            preexisting_error,
            initial_value,
            ctypes.byref(result),
        )
        return result.tuple()

    def test_production_source_license_and_compatibility_boundary_are_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "Copyright (c) 2011 Petteri Aimonen",
            "This notice may not be removed or altered",
            "Altered production source",
            "compatibility with nanopb 0.4.7 through",
            "not proof of the vendor's historical point release",
            "open_cfw_nanopb_decode_varint",
            "open_cfw_nanopb_readbyte",
        ):
            self.assertIn(token, source + header)
        self.assertNotIn("_candidate", source + header)

    def test_production_candidate_and_authenticated_upstream_match(self) -> None:
        initial = 0xA55A_F00D_C33C_9696
        cases = [
            (b"", 0, 0, 0, initial),
            (b"\x00", 1, 0, 0, initial),
            (b"\x80", 1, 0, 0, initial),
            (b"\x80\x00", 2, 1, 0, initial),
            (b"\xff" * 10, 10, 0, 0, initial),
            (b"\xff" * 9 + b"\x01", 10, 0, 0, initial),
            (b"\xff" * 10, 10, 0, 1, initial),
        ]
        generator = random.Random(0x7B2564)
        for _ in range(1_000):
            size = generator.randrange(0, 14)
            cases.append(
                (
                    bytes(generator.randrange(0, 256) for _ in range(size)),
                    generator.randrange(0, 15),
                    generator.randrange(0, 15),
                    generator.randrange(0, 2),
                    generator.randrange(0, 1 << 64),
                )
            )
        for case in cases:
            observed = [self.run_host(function, *case) for function in self.runners]
            self.assertEqual(observed[0], observed[1], case)
            self.assertEqual(observed[0], observed[2], case)

    def test_both_profile_objects_rodata_and_relocations_are_pinned(self) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        leaf = next(
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        )
        for profile, pins in PROFILE_PINS.items():
            expected = (
                leaf["expected"] if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(expected["size"], pins["text_size"])
            self.assertEqual(expected["unrelocated_sha256"], pins["text_sha256"])
            self.assertEqual(expected["sha256"], pins["relocated_sha256"])
            self.assertEqual(expected["closure_sha256"], pins["closure_sha256"])
            aggregate = (
                config["expected"] if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["overlay"],
            )
            self.assertEqual(
                (aggregate["component_size"], aggregate["component_sha256"]),
                pins["component"],
            )

        parsed = [apollo_overlay.parse_elf32(path) for path in self.objects]
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        for path, (data, sections) in zip(self.objects, parsed):
            self.assertEqual((path.stat().st_size, sha256(path)), self.pins["object"])
            text = next(section for section in sections if section["name"] == SECTION)
            body = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
            self.assertEqual((len(body), sha256(body)), (
                self.pins["text_size"], self.pins["text_sha256"]
            ))
            rodata = next(
                section for section in sections if section["name"] == ".rodata.str1.1"
            )
            value = data[
                int(rodata["offset"]):int(rodata["offset"]) + int(rodata["size"])
            ]
            self.assertEqual(value, ERROR)

        data, sections = parsed[0]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append((
                apollo_overlay.elf_string(strings, fields[0], "symbol"),
                fields,
            ))
        text_relocations = []
        exidx_relocations = []
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"]) + index * 8
                )
                record = (offset, information & 0xFF, symbols[information >> 8][0])
                if target["name"] == SECTION:
                    text_relocations.append(record)
                else:
                    exidx_relocations.append((target["name"], *record))
        self.assertEqual(text_relocations, self.pins["text_relocations"])
        undefined = [
            name for name, fields in symbols if name and fields[5] == 0
        ]
        self.assertEqual(undefined, [SEAM])
        self.assertEqual(
            exidx_relocations,
            [(".ARM.exidx" + SECTION, 0, 42, "")],
        )

    def test_registration_patch_neighbors_and_whole_component_ingress(self) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(len(config["functions"]), 684)
        self.assertEqual(len(config["patch_sites"]), 632)
        self.assertEqual(len(config["relocated_leaves"]), 115)
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaf = next(item for item in config["relocated_leaves"] if item["function"] == FUNCTION)
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(leaf["source"]["license"], "Zlib")
        self.assertEqual(
            leaf["relocations"][0],
            {
                "offset": 24,
                "type": "R_ARM_THM_CALL",
                "symbol": SEAM,
                "symbol_type": "STT_NOTYPE",
                "target_address": READBYTE,
            },
        )
        production_text = OVERLAY_CONFIG.read_text(encoding="utf-8")
        manifest_text = MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn(CANDIDATE_PATH, production_text + manifest_text)
        self.assertNotIn("open_cfw_nanopb_decode_varint_candidate", production_text + manifest_text)

        output = Path(self.temporary.name) / "component"
        report = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY_CONFIG,
            output_dir=output,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            self.pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            self.pins["component"],
        )
        extracted = next(
            item["extraction"] for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(extracted["function"], FUNCTION)
        self.assertEqual(extracted["runtime_address"], self.pins["runtime"])
        self.assertEqual(extracted["relocation_count"], 3)
        self.assertEqual(extracted["relocations"][0]["target_address"], READBYTE)
        self.assertEqual(extracted["rodata"]["runtime_address"], (
            self.pins["runtime"] + self.pins["text_size"]
        ))

        patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_decode_varint"
        )
        self.assertEqual(patch["name"], "replace_nanopb_decode_varint")
        self.assertEqual(patch["target_address"], self.pins["runtime"])
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(len(replacement), END - START)
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(START, replacement[:4], link=False),
            self.pins["runtime"],
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 54)

        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        offset = PREAMBLE + START - RUN_BASE
        self.assertEqual(component[offset:offset + len(replacement)], replacement)
        predecessor = (
            apollo_overlay.encode_thumb_b_w(
                START - 10, self.pins["predecessor_target"]
            )
            + b"\x00\xbf" * 3
        )
        self.assertEqual(
            component[offset - 10:offset],
            predecessor,
        )
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                START - 10, predecessor[:4], link=False
            ),
            self.pins["predecessor_target"],
        )
        public_patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_decode_varint32"
        )
        self.assertEqual(
            public_patch["target_address"], self.pins["predecessor_target"]
        )
        self.assertEqual(bytes.fromhex(public_patch["replacement_hex"]), predecessor)
        skip_string_patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_skip_string"
        )
        skip_string_replacement = bytes.fromhex(
            skip_string_patch["replacement_hex"]
        )
        self.assertEqual(
            skip_string_patch["target_address"],
            self.pins["skip_string_target"],
        )
        self.assertEqual(len(skip_string_replacement), 32)
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                START + 148,
                skip_string_replacement[:4],
                link=False,
            ),
            self.pins["skip_string_target"],
        )
        self.assertEqual(skip_string_replacement[4:], b"\x00\xbf" * 14)
        self.assertEqual(
            component[offset + 148:offset + 180],
            skip_string_replacement,
        )

        other_profile = "linux-clang" if self.profile == "apple-clang" else "apple-clang"
        other_target = PROFILE_PINS[other_profile]["predecessor_target"]
        self.assertNotEqual(other_target, self.pins["predecessor_target"])
        self.assertNotEqual(
            apollo_overlay.encode_thumb_b_w(START - 10, other_target),
            predecessor[:4],
        )

        # Keep every independent ingress decoder live even when the assembled
        # component contains no matching external edge of that form.
        first, second = struct.unpack(
            "<HH", apollo_overlay.encode_thumb_b_w(0x1000, 0x1010)
        )
        self.assertEqual(
            candidate_contract.thumb_wide_branch_target(
                0x1000, first, second, link=False
            ),
            0x1010,
        )
        self.assertEqual(
            candidate_contract.wide_conditional_target(0x1000, 0xF000, 0x8000),
            0x1004,
        )
        self.assertEqual(candidate_contract.narrow_targets(0x1000, 0xE000), (0x1004,))
        self.assertEqual(candidate_contract.narrow_targets(0x1000, 0xD000), (0x1004,))
        self.assertEqual(candidate_contract.narrow_targets(0x1000, 0xB100), (0x1004,))

        direct_bl = []
        direct_bw = []
        interior = []
        conditional_or_narrow = []
        application = component[PREAMBLE:]
        for relative in range(0, len(application) - 3, 2):
            address = RUN_BASE + relative
            first, second = struct.unpack_from("<HH", application, relative)
            for link in (True, False):
                target = candidate_contract.thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(address)
                elif not START <= address < END:
                    interior.append((address, target, link))
            conditional = candidate_contract.wide_conditional_target(
                address, first, second
            )
            for target in (
                *((conditional,) if conditional is not None else ()),
                *candidate_contract.narrow_targets(address, first),
            ):
                if (
                    START <= target < END
                    and not START <= address < END
                    and not 0x0048_F5AE <= address < START
                ):
                    conditional_or_narrow.append((address, target))
        self.assertEqual(
            direct_bl,
            [],
        )
        self.assertEqual(direct_bw, [])
        self.assertEqual(interior, [])
        self.assertEqual(conditional_or_narrow, [])

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = application.find(needle, position)
                    if position < 0:
                        break
                    stored.append((RUN_BASE + position, value, canonical, position % 4))
                    position += 1
        self.assertEqual(stored, [])

    def test_manifest_tiling_ownership_package_and_notices_are_exact(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        component = manifest["component_overrides"]["apollo_main"]
        provider = component["provider"]
        self.assertEqual(
            (provider["size"], provider["sha256"]),
            PROFILE_PINS["apple-clang"]["component"],
        )
        self.assertEqual(
            (provider["profiles"]["linux-clang"]["size"],
             provider["profiles"]["linux-clang"]["sha256"]),
            PROFILE_PINS["linux-clang"]["component"],
        )
        regions = component["regions"]
        self.assertEqual(len(regions), 1022)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(left["file_offset"] + left["size"], right["file_offset"])
        self.assertEqual(regions[-1]["file_offset"] + regions[-1]["size"], provider["size"])
        by_name = {item["name"]: item for item in regions}
        self.assertEqual(
            by_name["nanopb_decode_varint_source_replacement"]["address_status"],
            "generated_source_entry_replacement",
        )
        self.assertEqual(
            by_name["apollo_nanopb_decode_varint_source_text"]["target_address"],
            PROFILE_PINS["apple-clang"]["runtime"],
        )
        self.assertEqual(
            by_name["apollo_nanopb_decode_varint_source_rodata"]["size"], 16
        )
        ownership = {}
        ownership_counts = {}
        for region in regions:
            ownership.setdefault(region["address_status"], 0)
            ownership[region["address_status"]] += region["size"]
            ownership_counts.setdefault(region["address_status"], 0)
            ownership_counts[region["address_status"]] += 1
        self.assertEqual(
            {key: (ownership_counts[key], ownership[key]) for key in ownership},
            {
                "container_only": (1, 32),
                "generated_alignment": (65, 128),
                "generated_source_entry_replacement": (618, 88_870),
                "generated_source_exact_load_image": (1, 6),
                "generated_source_exact_replacement": (7, 134),
                "official_blob": (187, 3_434_136),
                "source_compiled": (143, 128_354),
            },
        )
        package = manifest["package"]
        self.assertEqual(
            (package["expected_size"], package["expected_sha256"]),
            (
                4_430_154,
                "aa71330ceed2775494fb7ff599a23701ef746a25452a8d335574a3bac12674a9",
            ),
        )
        self.assertEqual(
            package["profiles"]["linux-clang"],
            {
                "expected_size": 4_434_778,
                "expected_sha256": "63d5cd1d1cbab2c3ece4a48f96b58a0cb14a7487917831f4c6d370b40ed41d90",
            },
        )
        for path, tokens in {
            NOTICE: ("nanopb", "Zlib", "98bf4db69897b53434f3d0ba72e0a3ab1a902824"),
            EVIDENCE: ("0x0048F5B8", "0x0048F454", "compatibility baseline"),
            AUDIT: ("Production promotion", "B.W", "whole-component ingress"),
            ROOT / "docs/memory-map.md": ("0x007B2564", "0x007B25E4", "pb_decode_varint"),
            ROOT / "docs/source-coverage.md": ("0x0048F5B8", "123,745", "nanopb"),
            ROOT / "docs/upstream-inventory.md": ("nanopb", "production", "0.4.9"),
            ROOT / "components/README.md": ("nanopb", "123,600", "125,420"),
            ROOT / "docs/linux-reproducible-build.md": ("nanopb", "125,420", "exact-root"),
        }.items():
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                self.assertIn(token, text, (path, token))


if __name__ == "__main__":
    unittest.main()
