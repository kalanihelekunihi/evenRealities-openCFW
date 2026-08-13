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

import analyze_g2_nanopb_skip_field as audit  # noqa: E402


SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_skip_field_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
PRODUCTION_SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_skip_field.c"
PRODUCTION_HEADER = PRODUCTION_SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_nanopb_skip_field_candidate_host.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
CLANG = "/usr/bin/clang"
LLVM_OBJDUMP = (
    "/Applications/Xcode-beta.app/Contents/Developer/Toolchains/"
    "XcodeDefault.xctoolchain/usr/bin/llvm-objdump"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CandidateResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_uint32),
        ("provider", ctypes.c_uint32),
        ("count", ctypes.c_uint32),
        ("error_kind", ctypes.c_uint32),
    ]


class NanopbSkipFieldAuditTests(unittest.TestCase):
    def test_authenticated_report_closes_stock_boundary(self) -> None:
        report = audit.analyze()
        self.assertEqual(report["stock"]["size"], 74)
        self.assertEqual(len(report["stock"]["callers"]), 2)
        self.assertEqual(len(report["stock"]["outgoing"]), 4)
        self.assertEqual(
            {item["provider"] for item in report["stock"]["outgoing"]},
            {"pb_skip_varint", "pb_read_8", "pb_skip_string", "pb_read_4"},
        )
        self.assertEqual(report["upstream"]["compatibility_range"], "0.4.7--0.4.9")
        self.assertEqual(
            report["decision"]["status"],
            "production-integrated for apple-clang",
        )
        self.assertFalse(report["decision"]["ready_for_promotion"])

    def test_mutated_stock_body_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        blob[audit.DISPATCHER[0] - audit.LOAD_BASE + 8] ^= 0x01
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "mutated.bin"
            mutated.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(mutated)

    def test_mutated_caller_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        caller = next(iter(audit.EXPECTED_CALLERS))
        blob[caller - audit.LOAD_BASE] ^= 0x01
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "mutated.bin"
            mutated.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(mutated)

    def test_candidate_is_absent_from_production_inputs(self) -> None:
        relative = SOURCE.relative_to(ROOT).as_posix()
        function = "open_cfw_nanopb_skip_field_candidate"
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            self.assertNotIn(relative, text)
            self.assertNotIn(function, text)

    def test_candidate_source_and_header_are_pinned(self) -> None:
        pins = {
            SOURCE: (
                2_477,
                "95bb1ab1dfda6c031613ef48939356cf2ee6c784015628718261a2716ed0bc21",
            ),
            HEADER: (
                2_029,
                "3ed7bb3bb6a998fba82e2a1bbdd9343e3d3c82f821ad4e2080a558622454976d",
            ),
            FIXTURE: (
                1_723,
                "2a56174f37a8bc25fd882515e07968b1608ddbbd336ffdca3b6195bbd6858643",
            ),
        }
        for path, expected in pins.items():
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)
            self.assertEqual((path.stat().st_size, sha256(path)), expected)

    def test_production_source_header_and_registration_are_pinned(self) -> None:
        pins = {
            PRODUCTION_SOURCE: (
                2_417,
                "b0fbb6fc99f0a47a40e53662393a43c88b01d29d4b4457910b9f6be8063e7353",
            ),
            PRODUCTION_HEADER: (
                2_152,
                "9a76c3455119f814be099085c5fac2e2394c4a293e10c2e74d9bc33cf21866a4",
            ),
        }
        for path, expected in pins.items():
            self.assertEqual((path.stat().st_size, sha256(path)), expected)

        config = json.loads(OVERLAY.read_text())
        leaves = [
            item
            for item in config["relocated_leaves"]
            if item["function"] == "open_cfw_nanopb_skip_field"
        ]
        patches = [
            item
            for item in config["patch_sites"]
            if item["name"] == "replace_nanopb_skip_field"
        ]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(len(patches), 1)
        self.assertEqual(config["functions"].count("open_cfw_nanopb_skip_field"), 1)
        self.assertEqual(
            leaves[0]["expected"],
            {
                "size": 66,
                "sha256": "31037e87e7a667852271b7fa3be6543232376b1ee6e10443517d75f1dc4126ca",
                "alignment": 4,
                "offset": 125260,
                "unrelocated_sha256": "893a37e8366996cbea7d54f63bcc81700e7feab62c4414d01b1f818aa9b77dd4",
                "closure_size": 84,
                "closure_sha256": "72fad2dba75d1fbbc06b3c0e3d250579b5116a1cb793b7886ff5c62b49f3004e",
                "rodata_offset": 66,
            },
        )
        self.assertEqual(
            patches[0],
            {
                "name": "replace_nanopb_skip_field",
                "runtime_address": 4_781_728,
                "expected_size": 74,
                "expected_sha256": "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d",
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_skip_field",
            },
        )


class NanopbSkipFieldCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        directory = Path(cls.temporary.name)
        cls.library = directory / "libnanopb_skip_field_candidate.dylib"
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
                str(SOURCE.parent),
                str(SOURCE),
                str(FIXTURE),
                "-o",
                str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.module = ctypes.CDLL(str(cls.library))
        cls.run_candidate = cls.module.open_cfw_test_nanopb_skip_field_candidate
        cls.run_candidate.argtypes = [
            ctypes.c_uint8,
            ctypes.c_bool,
            ctypes.c_bool,
            ctypes.POINTER(CandidateResult),
        ]
        cls.run_candidate.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def execute(
        self, wire_type: int, *, succeed: bool = True, preset: bool = False
    ) -> CandidateResult:
        result = CandidateResult()
        self.run_candidate(wire_type, succeed, preset, ctypes.byref(result))
        return result

    def test_dispatches_all_four_valid_wire_types(self) -> None:
        expected = {
            0: (1, 0),
            1: (3, 8),
            2: (2, 0),
            5: (3, 4),
        }
        for wire_type, (provider, count) in expected.items():
            with self.subTest(wire_type=wire_type):
                result = self.execute(wire_type)
                self.assertEqual(result.status, 1)
                self.assertEqual((result.provider, result.count), (provider, count))
                self.assertEqual(result.error_kind, 0)

    def test_propagates_provider_failure(self) -> None:
        for wire_type in (0, 1, 2, 5):
            with self.subTest(wire_type=wire_type):
                result = self.execute(wire_type, succeed=False)
                self.assertEqual(result.status, 0)
                self.assertNotEqual(result.provider, 0)
                self.assertEqual(result.error_kind, 0)

    def test_invalid_wire_type_sets_only_an_empty_error_slot(self) -> None:
        for wire_type in (3, 4, 6, 255):
            with self.subTest(wire_type=wire_type):
                result = self.execute(wire_type)
                self.assertEqual((result.status, result.provider), (0, 0))
                self.assertEqual(result.error_kind, 2)
                preserved = self.execute(wire_type, preset=True)
                self.assertEqual(preserved.error_kind, 1)

    def test_target_object_has_closed_relocation_and_rodata_shape(self) -> None:
        if not Path(CLANG).is_file() or not Path(LLVM_OBJDUMP).is_file():
            self.skipTest("reviewed Apple target tools are unavailable")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "production.o"
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
                    str(SOURCE.parent),
                    "-c",
                    str(PRODUCTION_SOURCE),
                    "-o",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [LLVM_OBJDUMP, "-h", "-r", "-d", str(target)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn(".text.open_cfw_nanopb_skip_field", result)
            self.assertIn("00000042", result)
            self.assertIn("00000012", result)
            self.assertEqual(result.count("R_ARM_THM_JUMP24"), 4)
            self.assertEqual(result.count("R_ARM_THM_MOVW_PREL_NC"), 1)
            self.assertEqual(result.count("R_ARM_THM_MOVT_PREL"), 1)
            for symbol in (
                "open_cfw_nanopb_read",
                "open_cfw_nanopb_skip_varint",
                "open_cfw_nanopb_skip_string",
                "open_cfw_nanopb_invalid_wire_type_error",
            ):
                self.assertIn(symbol, result)


if __name__ == "__main__":
    unittest.main()
