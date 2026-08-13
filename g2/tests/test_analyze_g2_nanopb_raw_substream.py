from __future__ import annotations

import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_nanopb_raw_substream as audit  # noqa: E402


CANDIDATE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_read_raw_value_candidate.c"
)
HEADER = CANDIDATE.with_suffix(".h")
PRODUCTION = ROOT / "components/shared/nanopb/runtime_nanopb_read_raw_value.c"
PRODUCTION_HEADER = PRODUCTION.with_suffix(".h")
FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_read_raw_value_candidate_host.c"
)
SUBSTREAM_CANDIDATE = (
    ROOT
    / "components/shared/nanopb/runtime_nanopb_make_string_substream_candidate.c"
)
SUBSTREAM_HEADER = SUBSTREAM_CANDIDATE.with_suffix(".h")
SUBSTREAM_FIXTURE = (
    ROOT
    / "tests/fixtures/runtime_nanopb_make_string_substream_candidate_host.c"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
CLANG = "/usr/bin/clang"
LLVM_OBJDUMP = (
    "/Applications/Xcode-beta.app/Contents/Developer/Toolchains/"
    "XcodeDefault.xctoolchain/usr/bin/llvm-objdump"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RawResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("read_calls", ctypes.c_uint32),
        ("total_requested", ctypes.c_uint32),
        ("error_kind", ctypes.c_uint32),
        ("buffer", ctypes.c_uint8 * 16),
    ]


class SubstreamResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_uint32),
        ("decode_calls", ctypes.c_uint32),
        ("parent_bytes_left", ctypes.c_uint64),
        ("substream_bytes_left", ctypes.c_uint64),
        ("parent_callback_kind", ctypes.c_uint32),
        ("substream_callback_kind", ctypes.c_uint32),
        ("parent_state_kind", ctypes.c_uint32),
        ("substream_state_kind", ctypes.c_uint32),
        ("parent_error_kind", ctypes.c_uint32),
        ("substream_error_kind", ctypes.c_uint32),
    ]


class NanopbRawSubstreamAuditTests(unittest.TestCase):
    def test_boundaries_topology_and_upstream_are_closed(self) -> None:
        report = audit.analyze()
        raw = report["functions"]["read_raw_value"]
        sub = report["functions"]["pb_make_string_substream"]
        self.assertEqual(raw["stock"]["size"], 148)
        self.assertEqual(len(raw["stock"]["callers"]), 1)
        self.assertEqual(len(raw["stock"]["outgoing"]), 3)
        self.assertEqual(raw["upstream"]["size"], 1044)
        self.assertEqual(sub["stock"]["size"], 76)
        self.assertEqual(len(sub["stock"]["callers"]), 3)
        self.assertEqual(
            {item["provider"] for item in sub["stock"]["outgoing"]},
            {"open_cfw_nanopb_decode_varint32", "retained___aeabi_memcpy"},
        )
        self.assertEqual(set(report["diagnostics"]), {
            "varint_overflow",
            "invalid_wire_type",
            "parent_stream_too_short",
        })
        self.assertEqual(
            report["stock_copy_seam"],
            {
                "provider": "__aeabi_memcpy",
                "provider_start": 0x00439BE4,
                "provider_end": 0x00439C8A,
                "provider_size": 166,
                "provider_sha256": "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd",
                "aligned_interior_entry": 0x00439C04,
                "call_site": 0x0048F79A,
                "call_window_start": 0x0048F794,
                "call_window_end": 0x0048F79E,
                "call_window_sha256": "addbebce1de320dc5ebfd1dd97eea54a4b1e6b2678ef52db109c9015f2c03022",
                "destination": "substream",
                "source": "parent stream",
                "count": 16,
                "candidate_policy": (
                    "four named 32-bit ABI-field assignments; no compiler-runtime "
                    "provider retained"
                ),
            },
        )
        self.assertTrue(report["decision"]["production_integrated"])

    def test_mutated_function_and_pointer_fail_closed(self) -> None:
        original = audit.DEFAULT_IMAGE.read_bytes()
        mutations = (
            audit.FUNCTIONS["read_raw_value"][0] - audit.LOAD_BASE,
            audit.ERRORS["parent_stream_too_short"][0] - audit.LOAD_BASE,
        )
        for offset in mutations:
            with self.subTest(offset=offset), tempfile.TemporaryDirectory() as tmp:
                blob = bytearray(original)
                blob[offset] ^= 1
                path = Path(tmp) / "mutated.bin"
                path.write_bytes(blob)
                with self.assertRaises(audit.AuditError):
                    audit.analyze(path)

    def test_candidate_files_are_pinned_and_production_excluded(self) -> None:
        pins = {
            CANDIDATE: (
                2_811,
                "e2eef942879e1f2bda6d84e84e33c9dcf8f24ee55240fa689c4a14b102dc7358",
            ),
            HEADER: (
                1_760,
                "def05d3f047d9665f896b1d548de51e8e9b7ef0c69c303c3392ce287ead27d81",
            ),
            FIXTURE: (
                2_363,
                "ab6e60611f66acde14aaaa81cec28d02027c2f877f6b6b643db80cd806c360dc",
            ),
            SUBSTREAM_CANDIDATE: (
                2_861,
                "96497ab30f11c1ae552045ef3c23a700a0e602af8953410b1f7e9ad73ba8c9bb",
            ),
            SUBSTREAM_HEADER: (
                1_603,
                "92113410ce095dbe5ac076b2885f4a1024419a7b7d367afbf91336e8fb364b3d",
            ),
            SUBSTREAM_FIXTURE: (
                4_234,
                "e860f8fad92326ccb5ef513c4f0ce163d08e7dc80dfb00b7d6859fdf99ae8c0e",
            ),
        }
        for path, expected in pins.items():
            self.assertEqual((path.stat().st_size, file_sha256(path)), expected)
        relative = CANDIDATE.relative_to(ROOT).as_posix()
        symbol = "open_cfw_nanopb_read_raw_value_candidate"
        substream_relative = SUBSTREAM_CANDIDATE.relative_to(ROOT).as_posix()
        substream_symbol = "open_cfw_nanopb_make_string_substream_candidate"
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            self.assertNotIn(relative, text)
            self.assertNotIn(symbol, text)
            self.assertNotIn(substream_relative, text)
            self.assertNotIn(substream_symbol, text)

    def test_target_object_has_closed_text_and_rodata_shape(self) -> None:
        if not Path(CLANG).is_file() or not Path(LLVM_OBJDUMP).is_file():
            self.skipTest("reviewed Apple target tools are unavailable")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "candidate.o"
            subprocess.run(
                [
                    CLANG,
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-O2",
                    "-ffreestanding",
                    "-fno-jump-tables",
                    "-fomit-frame-pointer",
                    "-fno-builtin",
                    "-mno-unaligned-access",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-fropi",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fno-ident",
                    "-I",
                    str(CANDIDATE.parent),
                    "-c",
                    str(CANDIDATE),
                    "-o",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                (target.stat().st_size, file_sha256(target)),
                (
                    1_356,
                    "46c8d8373360f7c538a9a7ac75887d415635e8c5c9f67da9eef8b6c3e63b554a",
                ),
            )
            result = subprocess.run(
                [LLVM_OBJDUMP, "-h", "-r", "-t", str(target)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn(
                ".text.open_cfw_nanopb_read_raw_value_candidate", result
            )
            self.assertIn("00000084", result)
            self.assertIn("00000010", result)
            self.assertIn("00000012", result)
            self.assertEqual(result.count("R_ARM_THM_CALL"), 1)
            self.assertEqual(result.count("R_ARM_THM_JUMP24"), 1)
            self.assertEqual(result.count("R_ARM_THM_MOVW_PREL_NC"), 2)
            self.assertEqual(result.count("R_ARM_THM_MOVT_PREL"), 2)
            self.assertNotIn("*UND*", result.replace(
                "00000000         *UND*\t00000000 open_cfw_nanopb_read", ""
            ))

    def test_substream_target_object_closes_without_memcpy(self) -> None:
        if not Path(CLANG).is_file() or not Path(LLVM_OBJDUMP).is_file():
            self.skipTest("reviewed Apple target tools are unavailable")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "substream_candidate.o"
            subprocess.run(
                [
                    CLANG,
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-O2",
                    "-ffreestanding",
                    "-fno-jump-tables",
                    "-fomit-frame-pointer",
                    "-fno-builtin",
                    "-mno-unaligned-access",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-fropi",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fno-ident",
                    "-I",
                    str(SUBSTREAM_CANDIDATE.parent),
                    "-c",
                    str(SUBSTREAM_CANDIDATE),
                    "-o",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                (target.stat().st_size, file_sha256(target)),
                (
                    1_184,
                    "7b20f668c60c429b10205360c184c69f7ae546b68e6c2a662c7858817b06600d",
                ),
            )
            result = subprocess.run(
                [LLVM_OBJDUMP, "-h", "-r", "-t", str(target)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn(
                ".text.open_cfw_nanopb_make_string_substream_candidate", result
            )
            self.assertIn("00000048", result)
            self.assertIn("00000018", result)
            self.assertEqual(result.count("R_ARM_THM_CALL"), 1)
            self.assertEqual(result.count("R_ARM_THM_MOVW_PREL_NC"), 1)
            self.assertEqual(result.count("R_ARM_THM_MOVT_PREL"), 1)
            self.assertNotIn("memcpy", result)
            self.assertNotIn("__aeabi", result)

    def test_production_source_and_registration_are_exact(self) -> None:
        self.assertEqual(
            (PRODUCTION.stat().st_size, file_sha256(PRODUCTION)),
            (2_762, "e8d9e5da342086614ef842849bba068daf72bbca52a24a24293f3ec7ac6e20f5"),
        )
        self.assertEqual(
            (PRODUCTION_HEADER.stat().st_size, file_sha256(PRODUCTION_HEADER)),
            (1_719, "59caa890004c376aa08d9eff6fe6525694a05d0cc878484be7a83b51c413aca4"),
        )
        overlay = json.loads(OVERLAY.read_text())
        leaves = [
            item for item in overlay["relocated_leaves"]
            if item["function"] == "open_cfw_nanopb_read_raw_value"
        ]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0]["expected"]["closure_size"], 168)
        self.assertEqual(leaves[0]["expected"]["offset"], 125_344)
        patches = [
            item for item in overlay["patch_sites"]
            if item["target_function"] == "open_cfw_nanopb_read_raw_value"
        ]
        self.assertEqual(
            [(item["runtime_address"], item["expected_size"]) for item in patches],
            [(0x0048F6EA, 148)],
        )
        manifest = json.loads(MANIFEST.read_text())
        regions = {
            item["name"]: item
            for item in manifest["component_overrides"]["apollo_main"]["regions"]
        }
        self.assertEqual(
            regions["apollo_nanopb_read_raw_value_source_leaf"]["target_address"],
            0x007B2CC4,
        )
        self.assertEqual(
            regions["apollo_nanopb_read_raw_value_error_rodata"]["target_address"],
            0x007B2D4A,
        )


class NanopbMakeStringSubstreamCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "libsubstream_candidate.dylib"
        subprocess.run(
            [
                CLANG,
                "-std=c11",
                "-shared",
                "-fPIC",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(SUBSTREAM_CANDIDATE.parent),
                str(SUBSTREAM_CANDIDATE),
                str(SUBSTREAM_FIXTURE),
                "-o",
                str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.module = ctypes.CDLL(str(cls.library))
        cls.entry = cls.module.open_cfw_test_nanopb_make_string_substream_candidate
        cls.entry.argtypes = [
            ctypes.c_uint32,
            ctypes.c_bool,
            ctypes.c_bool,
            ctypes.c_uint64,
            ctypes.c_bool,
            ctypes.c_bool,
            ctypes.POINTER(SubstreamResult),
        ]
        cls.entry.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_candidate(
        self,
        decoded_size: int,
        *,
        decode_status: bool = True,
        mutate_stream: bool = True,
        parent_bytes_left: int = 40,
        preset_parent_error: bool = False,
        alias_streams: bool = False,
    ) -> SubstreamResult:
        result = SubstreamResult()
        self.entry(
            decoded_size,
            decode_status,
            mutate_stream,
            parent_bytes_left,
            preset_parent_error,
            alias_streams,
            ctypes.byref(result),
        )
        return result

    def test_success_copies_post_decode_stream_and_partitions_bytes(self) -> None:
        result = self.run_candidate(12, parent_bytes_left=40)
        self.assertEqual(result.status, 1)
        self.assertEqual(result.decode_calls, 1)
        self.assertEqual(result.parent_bytes_left, 28)
        self.assertEqual(result.substream_bytes_left, 12)
        self.assertEqual(
            (result.parent_callback_kind, result.substream_callback_kind),
            (2, 2),
        )
        self.assertEqual(
            (result.parent_state_kind, result.substream_state_kind),
            (2, 2),
        )
        self.assertEqual(
            (result.parent_error_kind, result.substream_error_kind),
            (0, 0),
        )

    def test_zero_and_exact_length_succeed(self) -> None:
        zero = self.run_candidate(0, parent_bytes_left=40)
        self.assertEqual(
            (zero.status, zero.parent_bytes_left, zero.substream_bytes_left),
            (1, 40, 0),
        )
        exact = self.run_candidate(40, parent_bytes_left=40)
        self.assertEqual(
            (exact.status, exact.parent_bytes_left, exact.substream_bytes_left),
            (1, 0, 40),
        )

    def test_decode_failure_leaves_substream_untouched(self) -> None:
        result = self.run_candidate(
            12,
            decode_status=False,
            mutate_stream=True,
            parent_bytes_left=40,
        )
        self.assertEqual(result.status, 0)
        self.assertEqual(result.decode_calls, 1)
        self.assertEqual(result.parent_callback_kind, 2)
        self.assertEqual(result.parent_state_kind, 2)
        self.assertEqual(result.substream_bytes_left, 0xA5A5)
        self.assertEqual(result.substream_callback_kind, 3)
        self.assertEqual(result.substream_state_kind, 3)
        self.assertEqual(result.substream_error_kind, 2)

    def test_parent_too_short_copies_before_first_error(self) -> None:
        result = self.run_candidate(41, parent_bytes_left=40)
        self.assertEqual(result.status, 0)
        self.assertEqual(result.parent_bytes_left, 40)
        self.assertEqual(result.substream_bytes_left, 40)
        self.assertEqual(result.parent_error_kind, 3)
        self.assertEqual(result.substream_error_kind, 0)
        self.assertEqual(result.substream_callback_kind, 2)
        self.assertEqual(result.substream_state_kind, 2)

    def test_parent_too_short_preserves_existing_error(self) -> None:
        result = self.run_candidate(
            41,
            parent_bytes_left=40,
            preset_parent_error=True,
        )
        self.assertEqual(result.status, 0)
        self.assertEqual(
            (result.parent_error_kind, result.substream_error_kind),
            (1, 1),
        )

    def test_aliasing_matches_upstream_assignment_order(self) -> None:
        result = self.run_candidate(
            12,
            parent_bytes_left=40,
            alias_streams=True,
        )
        self.assertEqual(result.status, 1)
        self.assertEqual(
            (result.parent_bytes_left, result.substream_bytes_left),
            (0, 0),
        )
        self.assertEqual(
            (result.parent_callback_kind, result.substream_callback_kind),
            (2, 2),
        )


class NanopbReadRawValueCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "libraw_candidate.dylib"
        subprocess.run(
            [
                CLANG,
                "-std=c11",
                "-shared",
                "-fPIC",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(CANDIDATE.parent),
                str(CANDIDATE),
                str(FIXTURE),
                "-o",
                str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.module = ctypes.CDLL(str(cls.library))
        cls.run_candidate = (
            cls.module.open_cfw_test_nanopb_read_raw_value_candidate
        )
        cls.run_candidate.argtypes = [
            ctypes.c_uint8,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_bool,
            ctypes.POINTER(RawResult),
        ]
        cls.run_candidate.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def execute(
        self,
        wire_type: int,
        maximum_size: int,
        payload: bytes,
        *,
        fail_call: int = 0,
        preset_error: bool = False,
    ) -> RawResult:
        source = (ctypes.c_uint8 * max(1, len(payload)))()
        source[: len(payload)] = payload
        result = RawResult()
        self.run_candidate(
            wire_type,
            maximum_size,
            source,
            len(payload),
            fail_call,
            preset_error,
            ctypes.byref(result),
        )
        return result

    def test_varint_lengths_and_exact_buffer_copy(self) -> None:
        for payload in (b"\x00", b"\x80\x01", b"\xff" * 9 + b"\x01"):
            with self.subTest(payload=payload):
                result = self.execute(0, len(payload), payload)
                self.assertEqual(result.status, 1)
                self.assertEqual(result.size, len(payload))
                self.assertEqual(result.read_calls, len(payload))
                self.assertEqual(result.total_requested, len(payload))
                self.assertEqual(bytes(result.buffer[: len(payload)]), payload)
                self.assertEqual(result.error_kind, 0)

    def test_varint_capacity_overflow_precedes_extra_read(self) -> None:
        result = self.execute(0, 2, b"\x80\x80\x01")
        self.assertEqual((result.status, result.size), (0, 3))
        self.assertEqual((result.read_calls, result.total_requested), (2, 2))
        self.assertEqual(bytes(result.buffer[:2]), b"\x80\x80")
        self.assertEqual(result.error_kind, 2)
        zero = self.execute(0, 0, b"\x00")
        self.assertEqual((zero.status, zero.size, zero.read_calls), (0, 1, 0))
        self.assertEqual(zero.error_kind, 2)

    def test_provider_failure_preserves_count_and_error(self) -> None:
        result = self.execute(0, 2, b"\x80\x01", fail_call=2)
        self.assertEqual((result.status, result.size), (0, 2))
        self.assertEqual((result.read_calls, result.total_requested), (2, 2))
        self.assertEqual(result.error_kind, 0)
        self.assertEqual(result.buffer[0], 0x80)

    def test_fixed_width_paths_set_size_before_provider_result(self) -> None:
        for wire_type, size in ((1, 8), (5, 4)):
            with self.subTest(wire_type=wire_type):
                payload = bytes(range(size))
                good = self.execute(wire_type, 0, payload)
                self.assertEqual((good.status, good.size), (1, size))
                self.assertEqual((good.read_calls, good.total_requested), (1, size))
                self.assertEqual(bytes(good.buffer[:size]), payload)
                failed = self.execute(wire_type, 99, payload, fail_call=1)
                self.assertEqual((failed.status, failed.size), (0, size))
                self.assertEqual(failed.error_kind, 0)

    def test_invalid_wire_types_preserve_size_and_first_error(self) -> None:
        for wire_type in (2, 3, 4, 6, 255):
            with self.subTest(wire_type=wire_type):
                result = self.execute(wire_type, 7, b"")
                self.assertEqual((result.status, result.size), (0, 7))
                self.assertEqual(result.read_calls, 0)
                self.assertEqual(result.error_kind, 3)
                preset = self.execute(
                    wire_type, 7, b"", preset_error=True
                )
                self.assertEqual(preset.error_kind, 1)

    def test_overflow_preserves_existing_error(self) -> None:
        result = self.execute(0, 0, b"\x00", preset_error=True)
        self.assertEqual((result.status, result.size, result.read_calls), (0, 1, 0))
        self.assertEqual(result.error_kind, 1)


if __name__ == "__main__":
    unittest.main()
