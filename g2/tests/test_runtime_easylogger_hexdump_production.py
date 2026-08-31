from __future__ import annotations

import ctypes
import copy
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components/apollo_main/core_overlay"
CONFIG = COMPONENT / "overlay.json"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
MAIN_SOURCE = COMPONENT / "runtime_easylogger_hexdump.c"
MAIN_HEADER = MAIN_SOURCE.with_suffix(".h")
SUPPORT_SOURCE = COMPONENT / "runtime_easylogger_hexdump_support.c"
SUPPORT_HEADER = SUPPORT_SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests/fixtures/runtime_easylogger_hexdump_production_support_host.c"
)
BASE = 0x0043_8000
PREAMBLE = 32

SPANS = {
    "replace_easylogger_hexdump": (
        0x0043_DACC,
        0x0043_DC88,
        "782cb65686dde396075abdd4f7c6a168bbf64962498d97446ab35e0e1670536c",
        "open_cfw_easylogger_hexdump",
    ),
    "replace_easylogger_hexdump_raw_submit": (
        0x0044_AA76,
        0x0044_AA80,
        "a509174409c14871498cd505c5246e02d78cd9cf067100b83aff576842b3e123",
        "open_cfw_easylogger_hexdump_raw_submit",
    ),
    "replace_easylogger_async_record_build_level_less": (
        0x0044_8CCC,
        0x0044_8D4E,
        "91ae986d5deaa816a662a842ecd71217c0deb0dff552ebbe04e382f16e8ebc55",
        "open_cfw_g2_easylogger_async_record_build_level_less_single_owner",
    ),
}

HEXDUMP_CALLERS_SHA256 = (
    "eddd8dc16569623d78608b9f6b476c2279e51243d822f4732eed39d56a8c1ad3"
)
LEAF_ORDER = (
    "open_cfw_easylogger_hexdump_put",
    "open_cfw_easylogger_hexdump_put_hex",
    "open_cfw_easylogger_hexdump_fill",
    "open_cfw_easylogger_hexdump_format_header",
    "open_cfw_easylogger_hexdump_format_hex",
    "open_cfw_easylogger_hexdump_format_character",
    "open_cfw_easylogger_hexdump_blank_hex",
    "open_cfw_g2_easylogger_async_record_build_level_less_single_owner",
    "open_cfw_easylogger_hexdump_raw_submit",
    "open_cfw_easylogger_hexdump",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ (((second >> 13) & 1) ^ sign)
    i2 = 1 ^ (((second >> 11) & 1) ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    return ()


def wide_conditional_branch_target(
    address: int, first: int, second: int
) -> int | None:
    """Decode Thumb-2 B<cond>.W (T3), excluding reserved conditions."""
    condition = (first >> 6) & 0x0F
    if (
        first & 0xF800 != 0xF000
        or second & 0xD000 != 0x8000
        or condition >= 0x0E
    ):
        return None
    immediate = (
        (((first >> 10) & 1) << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 20):
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


class RuntimeEasyLoggerHexdumpProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PREAMBLE:]
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE", "apple-clang"
        )
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-hexdump-production-",
            dir=ROOT / "build",
        )
        stage_config = copy.deepcopy(cls.config)
        stage_config["expected"] = stage_config["core_stage_expected"]
        for profile in stage_config.get("toolchain_profiles", {}).values():
            if "core_stage_expected" in profile:
                profile["expected"] = profile["core_stage_expected"]
        stage_config_path = Path(cls.temporary.name) / "core-stage-overlay.json"
        stage_config_path.write_text(
            json.dumps(stage_config, indent=2) + "\n", encoding="utf-8"
        )
        cls.report = apollo_overlay.build(
            root=ROOT,
            config_path=stage_config_path,
            output_dir=Path(cls.temporary.name),
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )
        cls.component = (
            ROOT / cls.report["component"]["artifact"]
        ).read_bytes()
        library = Path(cls.temporary.name) / (
            "hexdump-production.dylib"
            if sys.platform == "darwin"
            else "hexdump-production.so"
        )
        subprocess.run(
            [
                cls.clang,
                *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared"] ),
                "-fPIC",
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(HOST_FIXTURE),
                "-o",
                str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.host = ctypes.CDLL(str(library))
        cls.host.open_cfw_test_easylogger_hexdump_production_format_hex.argtypes = [
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_char),
        ]
        cls.host.open_cfw_test_easylogger_hexdump_production_put_hex.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_uint32,
        ]
        cls.host.open_cfw_test_easylogger_hexdump_production_put_hex.restype = (
            ctypes.c_uint32
        )
        cls.host.open_cfw_test_easylogger_hexdump_production_format_header.argtypes = [
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.host.open_cfw_test_easylogger_hexdump_production_format_header.restype = (
            ctypes.c_int
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exact_stock_spans_and_complete_ingress_topology(self) -> None:
        callers = {start: [] for start, _, _, _ in SPANS.values()}
        wide_entries: list[tuple[int, int, bool]] = []
        wide_interiors: list[tuple[int, int, bool]] = []
        wide_conditional: list[tuple[int, int]] = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link in (True, False):
                target = wide_branch_target(address, first, second, link=link)
                if target in callers:
                    if link:
                        callers[target].append(address)
                    else:
                        wide_entries.append((address, target, link))
                for start, end, _, _ in SPANS.values():
                    if (
                        target is not None
                        and start < target < end
                        and not start <= address < end
                    ):
                        wide_interiors.append((address, target, link))
            conditional_target = wide_conditional_branch_target(
                address, first, second
            )
            if conditional_target is not None:
                for start, end, _, _ in SPANS.values():
                    if (
                        start <= conditional_target < end
                        and not start <= address < end
                    ):
                        wide_conditional.append((address, conditional_target))

        hexdump_callers = callers[0x0043_DACC]
        self.assertEqual(len(hexdump_callers), 41)
        self.assertEqual(
            sha256(",".join(f"{site:08X}" for site in hexdump_callers).encode()),
            HEXDUMP_CALLERS_SHA256,
        )
        self.assertEqual(callers[0x0044_AA76], [0x0043_DB3C])
        self.assertEqual(callers[0x0044_8CCC], [0x0044_AA7A])
        self.assertEqual(wide_entries, [])
        self.assertEqual(wide_interiors, [])
        self.assertEqual(wide_conditional, [])

        narrow_interiors = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                for start, end, _, _ in SPANS.values():
                    if start <= target < end and not start <= address < end:
                        narrow_interiors.append((address, target))
        self.assertEqual(narrow_interiors, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1 and any(
                start <= target < end for start, end, _, _ in SPANS.values()
            ):
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        for start, end, digest, _ in SPANS.values():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(len(body), end - start)
            self.assertEqual(sha256(body), digest)

    def test_patch_ranges_are_exact_adjacent_and_branch_to_production(self) -> None:
        sites = {site["name"]: site for site in self.config["patch_sites"]}
        self.assertEqual(
            sites["replace_easylogger_async_record_build"]["runtime_address"],
            0x0044_8D4E,
        )
        self.assertEqual(
            sites["replace_easylogger_async_submit"]["runtime_address"],
            0x0044_AA80,
        )
        self.assertEqual(SPANS["replace_easylogger_async_record_build_level_less"][1], 0x0044_8D4E)
        self.assertEqual(SPANS["replace_easylogger_hexdump_raw_submit"][1], 0x0044_AA80)

        intervals = []
        for site in self.config["patch_sites"]:
            size = site.get("expected_size")
            if size is None:
                size = len(bytes.fromhex(site["expected_hex"]))
            intervals.append(
                (int(site["runtime_address"]), int(site["runtime_address"]) + int(size), site["name"])
            )
        intervals.sort()
        for left, right in zip(intervals, intervals[1:]):
            self.assertLessEqual(left[1], right[0], (left, right))
        for name, (start, end, digest, target) in SPANS.items():
            site = sites[name]
            self.assertEqual(
                (site["runtime_address"], site["expected_size"],
                 site["expected_sha256"], site["branch"],
                 site["target_function"]),
                (start, end - start, digest, "b_w", target),
            )

        patched = {
            site["name"]: site for site in self.report["overlay"]["patched_sites"]
        }
        functions = self.report["overlay"]["functions"]
        overlay_base = self.report["overlay"]["overlay_runtime_address"]
        component = self.component
        for name, (start, end, _, target) in SPANS.items():
            generated = bytes.fromhex(patched[name]["replacement_hex"])
            self.assertEqual(len(generated), end - start)
            target_address = overlay_base + functions[target]["offset"]
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    start, generated[:4], link=False
                ),
                target_address,
            )
            self.assertEqual(generated[4:], b"\x00\xBF" * ((len(generated) - 4) // 2))
            file_offset = PREAMBLE + start - BASE
            self.assertEqual(component[file_offset:file_offset + len(generated)], generated)

    def test_literal_pool_after_hexdump_is_preserved(self) -> None:
        start = 0x0043_DC88
        end = 0x0043_DCC0
        original = self.package[PREAMBLE + start - BASE:PREAMBLE + end - BASE]
        built = self.component
        rebuilt = built[PREAMBLE + start - BASE:PREAMBLE + end - BASE]
        self.assertEqual(rebuilt, original)
        self.assertEqual(original[:2], b"\n\0")

    def test_production_leaf_order_profiles_and_source_ownership_are_explicit(self) -> None:
        leaves = self.config["relocated_leaves"]
        selected = [leaf for leaf in leaves if leaf["function"] in LEAF_ORDER]
        self.assertEqual(tuple(leaf["function"] for leaf in selected), LEAF_ORDER)
        for leaf in selected:
            self.assertTrue(leaf["strict_relocation_contract"])
            self.assertIn("linux-clang", leaf["toolchain_profiles"])
            self.assertIn("expected", leaf["toolchain_profiles"]["linux-clang"])
            self.assertNotIn("candidate", leaf["source"]["path"])

        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (MAIN_SOURCE, MAIN_HEADER, SUPPORT_SOURCE, SUPPORT_HEADER)
        )
        self.assertNotIn("NONPRODUCTION", text)
        self.assertIn("digit < 10U ? '0' + digit : 'A' + digit - 10U", text)
        self.assertEqual(text.count("record->reserved_level"), 0)
        self.assertEqual(
            SUPPORT_SOURCE.read_text(encoding="utf-8").count(
                "open_cfw_retained_easylogger_async_record_enqueue(record)"
            ),
            1,
        )
        self.assertNotIn("record_recycle", text)

    def test_each_profile_has_closed_transport_relocations(self) -> None:
        leaves = {
            leaf["function"]: leaf for leaf in self.config["relocated_leaves"]
        }
        names = {
            "main": "open_cfw_easylogger_hexdump",
            "builder": (
                "open_cfw_g2_easylogger_async_record_build_level_less_single_owner"
            ),
            "raw": "open_cfw_easylogger_hexdump_raw_submit",
        }
        expected_builder_symbols = [
            "open_cfw_retained_easylogger_async_ready",
            "open_cfw_retained_easylogger_async_ready",
            "open_cfw_retained_easylogger_async_default_metadata",
            "open_cfw_retained_easylogger_async_default_metadata",
            "open_cfw_retained_easylogger_async_record_allocate",
            "open_cfw_retained_easylogger_async_record_enqueue",
            "open_cfw_easylogger_hexdump_enqueue_error",
            "open_cfw_easylogger_hexdump_enqueue_error",
            "open_cfw_retained_easylogger_async_diagnostic",
        ]
        expected_main_functions = {
            "open_cfw_easylogger_hexdump_fill",
            "open_cfw_easylogger_hexdump_raw_submit",
            "open_cfw_easylogger_hexdump_format_header",
            "open_cfw_easylogger_hexdump_format_hex",
            "open_cfw_easylogger_hexdump_blank_hex",
            "open_cfw_easylogger_hexdump_format_character",
        }
        forbidden = (
            "recycle",
            "event_set",
            "record_build_single_owner",
            "open_cfw_g2_easylogger_async_submit",
        )
        for profile in ("apple-clang", "linux-clang"):
            resolved = {}
            for key, function in names.items():
                leaf = leaves[function]
                profile_data = leaf.get("toolchain_profiles", {}).get(
                    profile, {}
                )
                resolved[key] = profile_data.get(
                    "relocations", leaf["relocations"]
                )
            self.assertEqual(
                tuple(len(resolved[key]) for key in ("main", "builder", "raw")),
                (23, 9, 1),
            )
            self.assertEqual(
                [item["symbol"] for item in resolved["builder"]],
                expected_builder_symbols,
            )
            self.assertEqual(
                resolved["raw"][0].get("target_function"), names["builder"]
            )
            self.assertEqual(
                {
                    item["target_function"]
                    for item in resolved["main"]
                    if "target_function" in item
                },
                expected_main_functions,
            )
            serialized = json.dumps(resolved, sort_keys=True)
            for token in forbidden:
                self.assertNotIn(token, serialized)

    def test_production_arithmetic_hex_leaves_execute_against_oracles(self) -> None:
        format_hex = (
            self.host.open_cfw_test_easylogger_hexdump_production_format_hex
        )
        for value in range(256):
            output = (ctypes.c_char * 4)()
            format_hex(value, output)
            self.assertEqual(bytes(output), f"{value:02X} ".encode() + b"\0")

        put_hex = self.host.open_cfw_test_easylogger_hexdump_production_put_hex
        for value, minimum_digits in (
            (0, 0),
            (0, 2),
            (0xA, 2),
            (0xAB, 0),
            (0x1234, 4),
            (0x89ABCDEF, 8),
        ):
            expected = f"{value:0{minimum_digits}X}".encode()
            for size in (0, 1, 2, 4, 16):
                output = (ctypes.c_char * 16)(*([b"\xA5"] * 16))
                length = put_hex(value, minimum_digits, output, size)
                self.assertEqual(length, len(expected))
                written = min(len(expected), max(size - 1, 0))
                self.assertEqual(bytes(output)[:written], expected[:written])
                self.assertEqual(bytes(output)[written:], b"\xA5" * (16 - written))

        header = (
            self.host.open_cfw_test_easylogger_hexdump_production_format_header
        )
        expected_header = b"D/HEX bus: 001A-002F: "
        for size in (0, 1, 2, 8, 32):
            output = (ctypes.c_char * 32)(*([b"\xA5"] * 32))
            length = header(output, size, b"bus", 0x1A, 0x2F)
            self.assertEqual(length, len(expected_header))
            if size == 0:
                self.assertEqual(bytes(output), b"\xA5" * 32)
                continue
            written = min(len(expected_header), size - 1)
            self.assertEqual(bytes(output)[:written], expected_header[:written])
            self.assertEqual(bytes(output)[written], 0)
            self.assertEqual(
                bytes(output)[written + 1:], b"\xA5" * (31 - written)
            )


if __name__ == "__main__":
    unittest.main()
