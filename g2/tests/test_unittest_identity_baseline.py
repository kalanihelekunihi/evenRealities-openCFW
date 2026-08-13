#!/usr/bin/env python3
"""Fail-closed checks for full-discovery regression evidence."""

from __future__ import annotations

import ast
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))

import unittest_identity_baseline as identity_baseline  # noqa: E402


NORMALIZED_EVIDENCE = (
    ROOT / "docs/research"
    / "nanopb-decode-varint32-pair-regression-evidence.json"
)
NORMALIZED_EVIDENCE_SHA256 = (
    "1300c8544b5ef5d7bb775ec5b25f93367f5312a10793dfaba1471855e0d0f417"
)
SKIP_RESOLVER_MAP = (
    ROOT / "docs/research"
    / "nanopb-decode-varint32-pair-skip-resolvers.json"
)
SKIP_RESOLVER_MAP_SHA256 = (
    "7b4a2c774d61096e74048111d77f81db385afb4b395cfff3f10c6e3fad95108b"
)
FULL_LOG = (
    ROOT / "build/baselines"
    / "varint32-task0-4abb9c10-full-discovery.log"
)

SKIP_STRING_EVIDENCE = {
    "apple-clang": {
        "path": (
            ROOT / "docs/research"
            / "nanopb-skip-string-regression-evidence-apple.json"
        ),
        "sha256": (
            "5887ae8b53ed5bf5ac0d052e7b6c3dc51a75d1cef189b8bd7b5389ca23bb7f62"
        ),
        "source_log_size": 370_227,
        "source_log_sha256": (
            "81459052c8c01c6157e6d3c09c4a5525b691abc16d40901b8c203b7c516e65d4"
        ),
        "tests": 2_660,
        "failures": 56,
        "errors": 0,
        "skips": 13,
        "anonymous_skips": 1,
    },
    "linux-clang": {
        "path": (
            ROOT / "docs/research"
            / "nanopb-skip-string-regression-evidence-linux.json"
        ),
        "sha256": (
            "1cf027edcce1b8b52f2b328c88918db0b6ce1eff431cc92a8e2d3005a92aa905"
        ),
        "source_log_size": 559_872,
        "source_log_sha256": (
            "7631c71ee91d64846fb01a11c94f5a29c694d6687648251b4bcb451317323343"
        ),
        "tests": 2_608,
        "failures": 29,
        "errors": 8,
        "skips": 331,
        "anonymous_skips": 0,
    },
}
SKIP_STRING_RESOLVER_MAP = (
    ROOT / "docs/research" / "nanopb-skip-string-skip-resolvers.json"
)
SKIP_STRING_RESOLVER_MAP_SHA256 = (
    "32bc885d9626d8589d87f89180f67ce2b798592c1bc3c38a6aff4697ef368795"
)

RULE = "-" * 70
SEPARATOR = "=" * 70


def ok_log(
    *,
    tests: int = 1,
    skips: tuple[tuple[str, str], ...] = (),
    command_status: int | None = 0,
) -> str:
    progress = "".join(
        f"{identity} ... skipped {reason!r}\n"
        for identity, reason in skips
    )
    if not skips:
        progress = "test_clean (example.CleanTests) ... ok\n"
    summary = "OK" if not skips else f"OK (skipped={len(skips)})"
    status = (
        "" if command_status is None else f"\ncommand_status={command_status}\n"
    )
    return (
        progress
        + f"\n{RULE}\nRan {tests} tests in 0.001s\n\n{summary}\n"
        + status
    )


def result_block(kind: str, identity: str, body: str) -> str:
    return f"{SEPARATOR}\n{kind}: {identity}\n{RULE}\n{body}\n\n"


def failed_log(
    records: tuple[tuple[str, str, str], ...],
    *,
    tests: int | None = None,
    skips: tuple[tuple[str, str], ...] = (),
    command_status: int | None = 1,
    summary_counts: dict[str, int] | None = None,
) -> str:
    progress = "".join(
        f"{identity} ... {kind}\n" for kind, identity, _body in records
    )
    progress += "".join(
        f"{identity} ... skipped {reason!r}\n"
        for identity, reason in skips
    )
    blocks = "".join(result_block(*record) for record in records)
    counts = {
        "failures": sum(kind == "FAIL" for kind, _identity, _body in records),
        "errors": sum(kind == "ERROR" for kind, _identity, _body in records),
        "skipped": len(skips),
    }
    if summary_counts is not None:
        counts = summary_counts
    rendered = ", ".join(
        f"{key}={value}" for key, value in counts.items() if value
    )
    status = (
        "" if command_status is None else f"\ncommand_status={command_status}\n"
    )
    return (
        progress
        + "\n"
        + blocks
        + f"{RULE}\nRan {tests or max(len(records) + len(skips), 1)} "
        "tests in 0.002s\n\n"
        + f"FAILED ({rendered})\n"
        + status
    )


class RawUnittestLogParserTests(unittest.TestCase):
    def test_clean_ok_and_optional_consistent_command_status(self) -> None:
        for status in (None, 0):
            with self.subTest(command_status=status):
                parsed = identity_baseline.parse_raw_unittest_log(
                    ok_log(command_status=status)
                )
                self.assertEqual(parsed.tests_run, 1)
                self.assertEqual(parsed.outcome, "OK")
                self.assertEqual(parsed.command_status, status)
                self.assertEqual(parsed.failures, ())
                self.assertEqual(parsed.errors, ())
                self.assertEqual(parsed.skips, ())

    def test_failure_error_blocks_and_body_digests_are_structured(self) -> None:
        failure = (
            "FAIL",
            "test_bad (example.BadTests) (case=1)",
            "Traceback (most recent call last):\nAssertionError: left != right",
        )
        error = (
            "ERROR",
            "test_broken (example.BrokenTests)",
            "Traceback (most recent call last):\nRuntimeError: broken",
        )
        parsed = identity_baseline.parse_raw_unittest_log(
            failed_log((failure, error), tests=2)
        )
        self.assertEqual(parsed.outcome, "FAILED")
        self.assertEqual(parsed.command_status, 1)
        self.assertEqual([record.identity for record in parsed.failures], [failure[1]])
        self.assertEqual([record.identity for record in parsed.errors], [error[1]])
        self.assertEqual(
            parsed.failures[0].body_sha256,
            hashlib.sha256((failure[2] + "\n\n").encode()).hexdigest(),
        )
        self.assertRegex(parsed.failures[0].block_sha256, r"^[0-9a-f]{64}$")

    def test_skip_only_log_preserves_identity_and_reason(self) -> None:
        identity = "test_optional (example.OptionalTests)"
        parsed = identity_baseline.parse_raw_unittest_log(
            ok_log(skips=((identity, "optional tool unavailable"),))
        )
        self.assertEqual(parsed.skipped_count, 1)
        self.assertEqual(parsed.skips[0].raw_identity, identity)
        self.assertEqual(parsed.skips[0].reason, "optional tool unavailable")
        self.assertRegex(parsed.skips[0].line_sha256, r"^[0-9a-f]{64}$")

    def test_subtest_headings_remain_distinct(self) -> None:
        parsed = identity_baseline.parse_raw_unittest_log(
            failed_log((
                ("FAIL", "test_many (example.ManyTests) (case=1)", "one"),
                ("FAIL", "test_many (example.ManyTests) (case=2)", "two"),
            ), tests=2)
        )
        self.assertEqual(
            [record.identity for record in parsed.failures],
            [
                "test_many (example.ManyTests) (case=1)",
                "test_many (example.ManyTests) (case=2)",
            ],
        )

    def test_empty_truncated_vacuous_and_missing_summary_logs_are_rejected(self) -> None:
        malformed = (
            "",
            "test_clean (example.CleanTests) ... ok\n",
            f"{RULE}\nRan 1 tests in 0.001s\n",
            f"{RULE}\nRan 0 tests in 0.001s\n\nOK\n",
            result_block("FAIL", "test_bad (example.BadTests)", "broken"),
        )
        for output in malformed:
            with self.subTest(output=output):
                with self.assertRaises(identity_baseline.MalformedUnittestLog):
                    identity_baseline.parse_raw_unittest_log(output)

    def test_fake_unstructured_heading_is_rejected(self) -> None:
        fake = "FAIL: test_fake (example.FakeTests)\n" + ok_log()
        with self.assertRaisesRegex(
            identity_baseline.MalformedUnittestLog, "unstructured result heading"
        ):
            identity_baseline.parse_raw_unittest_log(fake)

    def test_duplicate_exact_result_heading_is_rejected(self) -> None:
        identity = "test_duplicate (example.DuplicateTests)"
        output = failed_log((
            ("FAIL", identity, "first"),
            ("FAIL", identity, "second"),
        ), tests=2)
        with self.assertRaisesRegex(
            identity_baseline.MalformedUnittestLog, "duplicate result identity"
        ):
            identity_baseline.parse_raw_unittest_log(output)

    def test_count_summary_and_command_status_contradictions_are_rejected(self) -> None:
        one_failure = (("FAIL", "test_bad (example.BadTests)", "bad"),)
        malformed = (
            failed_log(
                one_failure,
                summary_counts={"failures": 2, "errors": 0, "skipped": 0},
            ),
            failed_log(one_failure, command_status=0),
            ok_log(command_status=1),
            ok_log(
                skips=(("test_skip (example.SkipTests)", "why"),), tests=2
            ).replace("OK (skipped=1)", "OK (skipped=2)"),
            ok_log() + "\nRan 1 tests in 0.001s\n\nOK\n",
            ok_log() + "\nFAILED (failures=1)\n",
            ok_log() + "trailing junk\n",
            ok_log(command_status=None) + "trailing junk\n",
        )
        for output in malformed:
            with self.subTest(output=output[-120:]):
                with self.assertRaises(identity_baseline.MalformedUnittestLog):
                    identity_baseline.parse_raw_unittest_log(output)

    def test_non_whitespace_between_summary_and_command_status_is_rejected(self) -> None:
        output = ok_log().replace(
            "\ncommand_status=0\n",
            "\nTLSF post-summary diagnostic\ncommand_status=0\n",
        )
        with self.assertRaisesRegex(
            identity_baseline.MalformedUnittestLog,
            "non-whitespace between summary and command_status",
        ):
            identity_baseline.parse_raw_unittest_log(output)


class NormalizedEvidenceTests(unittest.TestCase):
    def resolver_map(self):
        return identity_baseline.load_skip_resolver_map(
            json.loads(SKIP_RESOLVER_MAP.read_text(encoding="utf-8"))
        )

    def test_comparison_rejects_synthetic_new_failure_and_error(self) -> None:
        evidence = identity_baseline.load_normalized_evidence(
            json.loads(NORMALIZED_EVIDENCE.read_text(encoding="utf-8")),
            self.resolver_map(),
        )
        current = identity_baseline.parse_raw_unittest_log(failed_log((
            ("FAIL", "test_new_failure (example.NewFailureTests)", "new"),
            ("ERROR", "test_new_error (example.NewErrorTests)", "new"),
        ), tests=2))
        with self.assertRaisesRegex(
            identity_baseline.IdentityRegression,
            r"new failures:.*test_new_failure.*new errors:.*test_new_error",
        ):
            identity_baseline.require_no_new_failures_or_errors(
                evidence, current
            )

    def test_tracked_evidence_is_content_pinned_for_clean_checkouts(self) -> None:
        raw = NORMALIZED_EVIDENCE.read_bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(), NORMALIZED_EVIDENCE_SHA256
        )
        evidence = identity_baseline.load_normalized_evidence(
            json.loads(raw.decode("utf-8")), self.resolver_map()
        )
        self.assertEqual(evidence.format, "openCFW.unittest-regression-evidence")
        self.assertEqual(evidence.version, 2)
        self.assertEqual(evidence.source_log_size, 366005)
        self.assertEqual(
            evidence.source_log_sha256,
            "6c22440df5ca4a2238f9c920652872e6afee5b46ebeb8d056b00484055b12124",
        )
        self.assertEqual(evidence.tests_run, 2617)
        self.assertEqual(len(evidence.failures), 58)
        self.assertEqual(evidence.errors, ())
        self.assertEqual(len(evidence.skips), 12)
        self.assertIn(
            "test_candidate_sources_exist "
            "(test_runtime_nanopb_decode_varint32_candidate."
            "NanopbDecodeVarint32CandidateTests)",
            {record.identity for record in evidence.failures},
        )
        self.assertEqual(
            hashlib.sha256(SKIP_RESOLVER_MAP.read_bytes()).hexdigest(),
            SKIP_RESOLVER_MAP_SHA256,
        )

        resolved = {skip.resolved_identity: skip for skip in evidence.skips}
        self.assertEqual(len(resolved), 12)
        set_up = resolved[
            "setUpClass "
            "(test_runtime_nanopb_decode_svarint_production."
            "NanopbDecodeSvarintLinuxBuildMutationTests)"
        ]
        self.assertIsNone(set_up.raw_identity)
        self.assertEqual(
            set_up.resolution_provenance,
            {
                "method": "source_test_class_setUpClass",
                "source_path": (
                    "tests/test_runtime_nanopb_decode_svarint_production.py"
                ),
                "source_class": "NanopbDecodeSvarintLinuxBuildMutationTests",
                "source_blob_sha1": (
                    "6b93a951c6c0be881a7758b8da729163f765bf52"
                ),
                "source_revision": (
                    "4abb9c10935c244e365fd4d3ebc911a960a20e5b"
                ),
                "source_sha256": (
                    "e7d21035166e3d7b10a9b767f007331c08e1b64b22e2c1d214da4b06e889adf8"
                ),
            },
        )
        for skip in evidence.skips:
            self.assertTrue(skip.resolved_identity)
            if skip.raw_identity is not None:
                self.assertEqual(skip.resolved_identity, skip.raw_identity)
                self.assertEqual(
                    skip.resolution_provenance,
                    {"method": "raw_unittest_output"},
                )

    def test_local_supporting_log_matches_tracked_evidence_when_present(self) -> None:
        if not FULL_LOG.is_file():
            self.skipTest("ignored supporting full-discovery log is absent")
        evidence = identity_baseline.load_normalized_evidence(
            json.loads(NORMALIZED_EVIDENCE.read_text(encoding="utf-8")),
            self.resolver_map(),
        )

        current_bytes = FULL_LOG.read_bytes()
        self.assertEqual(len(current_bytes), evidence.source_log_size)
        self.assertEqual(
            hashlib.sha256(current_bytes).hexdigest(),
            evidence.source_log_sha256,
        )
        current = identity_baseline.parse_raw_unittest_log(
            current_bytes.decode("utf-8")
        )
        self.assertEqual(
            identity_baseline.normalized_evidence_dict(
                current, current_bytes, self.resolver_map()
            ),
            json.loads(NORMALIZED_EVIDENCE.read_text(encoding="utf-8")),
        )
        identity_baseline.require_no_new_failures_or_errors(evidence, current)
        self.assertEqual(current.failures, evidence.failures)
        self.assertEqual(current.errors, evidence.errors)
        self.assertEqual(
            [
                (skip.raw_identity, skip.reason, skip.line_sha256)
                for skip in current.skips
            ],
            [
                (skip.raw_identity, skip.reason, skip.line_sha256)
                for skip in evidence.skips
            ],
        )

    def test_normalized_loader_rejects_schema_and_count_contradictions(self) -> None:
        good = {
            "format": "openCFW.unittest-regression-evidence",
            "version": 2,
            "source_log": {
                "size": 100,
                "sha256": "0" * 64,
                "command_status": 0,
            },
            "run": {
                "tests": 1,
                "outcome": "OK",
                "failures": 0,
                "errors": 0,
                "skips": 0,
            },
            "results": [],
            "skips": [],
        }
        loaded = identity_baseline.load_normalized_evidence(
            good, self.resolver_map()
        )
        self.assertEqual((loaded.version, loaded.tests_run), (2, 1))
        mutations = (
            {**good, "format": "unknown"},
            {**good, "version": 1},
            {**good, "version": 3},
            {**good, "extra": True},
            {**good, "run": {**good["run"], "failures": 1}},
            {
                **good,
                "source_log": {**good["source_log"], "command_status": 1},
            },
        )
        for data in mutations:
            with self.subTest(data=data):
                with self.assertRaises(identity_baseline.MalformedEvidence):
                    identity_baseline.load_normalized_evidence(
                        data, self.resolver_map()
                    )

    def test_skip_resolution_and_provenance_mutations_fail_closed(self) -> None:
        baseline = json.loads(NORMALIZED_EVIDENCE.read_text(encoding="utf-8"))
        unnamed_index = next(
            index for index, skip in enumerate(baseline["skips"])
            if skip["raw_identity"] is None
        )
        named_index = next(
            index for index, skip in enumerate(baseline["skips"])
            if skip["raw_identity"] is not None
        )

        mutations = []
        for field in ("resolved_identity", "resolution_provenance"):
            missing = copy.deepcopy(baseline)
            del missing["skips"][unnamed_index][field]
            mutations.append(missing)
            null = copy.deepcopy(baseline)
            null["skips"][unnamed_index][field] = None
            mutations.append(null)

        mutated_identity = copy.deepcopy(baseline)
        mutated_identity["skips"][unnamed_index]["resolved_identity"] += "Mutated"
        mutations.append(mutated_identity)

        mutated_method = copy.deepcopy(baseline)
        mutated_method["skips"][unnamed_index]["resolution_provenance"][
            "method"
        ] = "raw_unittest_output"
        mutations.append(mutated_method)

        mutated_source = copy.deepcopy(baseline)
        mutated_source["skips"][unnamed_index]["resolution_provenance"][
            "source_sha256"
        ] = "0" * 64
        mutations.append(mutated_source)

        named_mismatch = copy.deepcopy(baseline)
        named_mismatch["skips"][named_index]["resolved_identity"] = "mutated"
        mutations.append(named_mismatch)

        for data in mutations:
            with self.subTest(skip=data["skips"][unnamed_index]):
                with self.assertRaises(identity_baseline.MalformedEvidence):
                    identity_baseline.load_normalized_evidence(
                        data, self.resolver_map()
                    )

    def test_resolver_map_rejects_mutated_source_provenance(self) -> None:
        good = json.loads(SKIP_RESOLVER_MAP.read_text(encoding="utf-8"))
        provenance = good["resolutions"][0]["provenance"]
        loaded = identity_baseline.load_skip_resolver_map(good)
        self.assertEqual((loaded.version, loaded.format), (2, good["format"]))
        head_revision = subprocess.run(
            ["git", "rev-parse", "HEAD^{commit}"],
            cwd=ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        mutations = []
        for field in ("source_revision", "source_blob_sha1"):
            missing = copy.deepcopy(good)
            del missing["resolutions"][0]["provenance"][field]
            mutations.append(missing)
            null = copy.deepcopy(good)
            null["resolutions"][0]["provenance"][field] = None
            mutations.append(null)
            uppercase = copy.deepcopy(good)
            uppercase["resolutions"][0]["provenance"][field] = (
                provenance[field].upper()
            )
            mutations.append(uppercase)

        wrong_revision = copy.deepcopy(good)
        wrong_revision["resolutions"][0]["provenance"][
            "source_revision"
        ] = head_revision

        noncommit_revision = copy.deepcopy(good)
        noncommit_revision["resolutions"][0]["provenance"][
            "source_revision"
        ] = provenance["source_blob_sha1"]

        unavailable_revision = copy.deepcopy(good)
        unavailable_revision["resolutions"][0]["provenance"][
            "source_revision"
        ] = "f" * 40

        wrong_blob = copy.deepcopy(good)
        wrong_blob["resolutions"][0]["provenance"]["source_blob_sha1"] = (
            "0" * 40
        )

        wrong_path = copy.deepcopy(good)
        wrong_path["resolutions"][0]["provenance"]["source_path"] = (
            "tests/test_runtime_nanopb_decode_varint32_production.py"
        )

        nonblob_path = copy.deepcopy(good)
        nonblob_path["resolutions"][0]["provenance"]["source_path"] = "tests"
        nonblob_path["resolutions"][0]["provenance"][
            "source_blob_sha1"
        ] = "17ee2e051fdc6b53279fb9c6c65945544a080b4c"

        unsafe_path = copy.deepcopy(good)
        unsafe_path["resolutions"][0]["provenance"]["source_path"] = (
            "../outside.py"
        )

        wrong_hash = copy.deepcopy(good)
        wrong_hash["resolutions"][0]["provenance"]["source_sha256"] = (
            "0" * 64
        )

        old_version = copy.deepcopy(good)
        old_version["version"] = 1
        new_version = copy.deepcopy(good)
        new_version["version"] = 3

        for data in mutations:
            with self.subTest(provenance=data["resolutions"][0]["provenance"]):
                with self.assertRaises(identity_baseline.MalformedEvidence):
                    identity_baseline.load_skip_resolver_map(data)

        guarded_mutations = (
            (wrong_revision, "source blob differs"),
            (
                noncommit_revision,
                "source revision is unavailable from Git history",
            ),
            (
                unavailable_revision,
                "source revision is unavailable from Git history",
            ),
            (wrong_blob, "source blob differs"),
            (wrong_path, "source path is unavailable from Git history"),
            (nonblob_path, "source object is not a blob"),
            (unsafe_path, "source_path is unsafe"),
            (wrong_hash, "source SHA-256 differs"),
            (old_version, "unsupported skip resolver format/version"),
            (new_version, "unsupported skip resolver format/version"),
        )
        for data, message in guarded_mutations:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    identity_baseline.MalformedEvidence, message
                ):
                    identity_baseline.load_skip_resolver_map(data)

        with tempfile.TemporaryDirectory() as directory:
            non_repository_root = Path(directory) / "openCFW"
            non_repository_root.mkdir()
            with self.assertRaisesRegex(
                identity_baseline.MalformedEvidence,
                "repository is unavailable from Git history",
            ):
                identity_baseline.load_skip_resolver_map(
                    good, source_root=non_repository_root
                )

    def test_resolver_uses_pinned_history_instead_of_mutable_head(self) -> None:
        data = json.loads(SKIP_RESOLVER_MAP.read_text(encoding="utf-8"))
        provenance = data["resolutions"][0]["provenance"]
        mutable_source = ROOT / provenance["source_path"]
        self.assertNotEqual(
            hashlib.sha256(mutable_source.read_bytes()).hexdigest(),
            provenance["source_sha256"],
        )
        resolver_map = identity_baseline.load_skip_resolver_map(data)
        resolution = next(iter(resolver_map.resolutions.values()))
        self.assertEqual(resolution.provenance, provenance)

    def test_resolver_rejects_reason_bound_to_different_class(self) -> None:
        data = json.loads(SKIP_RESOLVER_MAP.read_text(encoding="utf-8"))
        resolution = data["resolutions"][0]
        resolution["provenance"]["source_class"] = (
            "NanopbDecodeSvarintProductionTests"
        )
        resolution["resolved_identity"] = (
            "setUpClass "
            "(test_runtime_nanopb_decode_svarint_production."
            "NanopbDecodeSvarintProductionTests)"
        )
        with self.assertRaisesRegex(
            identity_baseline.MalformedEvidence,
            "reason is not raised by the selected class setUpClass",
        ):
            identity_baseline.load_skip_resolver_map(data)

    def test_skip_reason_ast_binding_accepts_only_skip_operations(self) -> None:
        reason = "historical toolchain is unavailable"

        def binding(source: str, *, include_import: bool = True) -> bool:
            prefix = "import unittest\n" if include_import else ""
            tree = ast.parse(prefix + source)
            selected = next(
                node
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name == "Selected"
            )
            set_up_class = identity_baseline._unique_set_up_class(selected)
            return bool(
                set_up_class is not None
                and identity_baseline._module_authenticates_unittest(
                    tree, selected, set_up_class
                )
                and identity_baseline._set_up_class_raises_skip_reason(
                    set_up_class, reason
                )
            )

        positive_sources = (
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        if enabled:\n"
            "            raise unittest.SkipTest(\n"
            "                'historical toolchain is unavailable'\n"
            "            )\n",
        )
        for source in positive_sources:
            with self.subTest(positive=source):
                self.assertTrue(binding(source))

        negative_sources = (
            "class Selected:\n"
            "    reason = 'historical toolchain is unavailable'\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        pass\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        unittest.SkipTest('historical toolchain is unavailable')\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise ValueError('historical toolchain is unavailable')\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        pass\n"
            "    def another_method(self):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        def nested():\n"
            "            raise unittest.SkipTest(\n"
            "                'historical toolchain is unavailable'\n"
            "            )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        callback = lambda: unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        class Nested:\n"
            "            raise unittest.SkipTest(\n"
            "                'historical toolchain is unavailable'\n"
            "            )\n",
            "class Other:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n"
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        pass\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest('a different reason')\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise SkipTest('historical toolchain is unavailable')\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        cls.skipTest('historical toolchain is unavailable')\n",
            "class Selected:\n"
            "    def setUpClass(self):\n"
            "        self.skipTest('historical toolchain is unavailable')\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable', 'extra'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            reason='historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        unittest = Fake\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    unittest = Fake\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        unittest.SkipTest = ValueError\n"
            "        raise unittest.SkipTest(\n"
            "            'historical toolchain is unavailable'\n"
            "        )\n",
        )
        for source in negative_sources:
            with self.subTest(negative=source):
                self.assertFalse(binding(source))

        exact_source = positive_sources[0]
        self.assertFalse(binding(exact_source, include_import=False))
        self.assertFalse(
            binding("class unittest:\n    SkipTest = ValueError\n" + exact_source)
        )
        self.assertFalse(
            binding("import unittest\n" + exact_source)
        )
        self.assertFalse(
            binding(
                "import unittest as unit_test\n" + exact_source,
                include_import=False,
            )
        )
        self.assertFalse(
            binding(
                exact_source.replace(
                    "        raise unittest.SkipTest(\n",
                    "        try:\n"
                    "            pass\n"
                    "        except Exception as unittest:\n"
                    "            pass\n"
                    "        raise unittest.SkipTest(\n",
                )
            )
        )

        duplicate = ast.parse(
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        pass\n"
            "    async def setUpClass(cls):\n"
            "        pass\n"
        ).body[0]
        self.assertIsNone(identity_baseline._unique_set_up_class(duplicate))

        duplicate_class = ast.parse(
            "class Selected:\n"
            "    pass\n"
            "class Selected:\n"
            "    pass\n"
        )
        self.assertIsNone(
            identity_baseline._unique_top_level_class(
                duplicate_class, "Selected"
            )
        )

        invalid_setups = (
            "class Selected:\n"
            "    async def setUpClass(cls):\n"
            "        pass\n",
            "class Selected:\n"
            "    def setUpClass(cls):\n"
            "        pass\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    @other\n"
            "    def setUpClass(cls):\n"
            "        pass\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(self):\n"
            "        pass\n",
            "class Selected:\n"
            "    @classmethod\n"
            "    def setUpClass(cls, extra):\n"
            "        pass\n",
        )
        for source in invalid_setups:
            selected = ast.parse(source).body[0]
            with self.subTest(invalid_setup=source):
                self.assertIsNone(
                    identity_baseline._unique_set_up_class(selected)
                )


class NanopbSkipStringRegressionEvidenceTests(unittest.TestCase):
    def resolver_map(self):
        return identity_baseline.load_skip_resolver_map(
            json.loads(SKIP_STRING_RESOLVER_MAP.read_text(encoding="utf-8"))
        )

    def test_platform_evidence_is_content_pinned_and_closed(self) -> None:
        resolver_map = self.resolver_map()
        for profile, expected in SKIP_STRING_EVIDENCE.items():
            with self.subTest(profile=profile):
                raw = expected["path"].read_bytes()
                self.assertEqual(
                    hashlib.sha256(raw).hexdigest(), expected["sha256"]
                )
                evidence = identity_baseline.load_normalized_evidence(
                    json.loads(raw.decode("utf-8")), resolver_map
                )
                self.assertEqual(evidence.version, 2)
                self.assertEqual(evidence.source_log_size, expected["source_log_size"])
                self.assertEqual(
                    evidence.source_log_sha256,
                    expected["source_log_sha256"],
                )
                self.assertEqual(evidence.command_status, 1)
                self.assertEqual(evidence.tests_run, expected["tests"])
                self.assertEqual(len(evidence.failures), expected["failures"])
                self.assertEqual(len(evidence.errors), expected["errors"])
                self.assertEqual(len(evidence.skips), expected["skips"])
                self.assertEqual(
                    sum(skip.raw_identity is None for skip in evidence.skips),
                    expected["anonymous_skips"],
                )
                self.assertEqual(
                    len({skip.resolved_identity for skip in evidence.skips}),
                    expected["skips"],
                )

                result_identities = {
                    record.identity
                    for record in (*evidence.failures, *evidence.errors)
                }
                self.assertNotIn(
                    "setUpClass "
                    "(test_runtime_nanopb_private_read_pair."
                    "NanopbPrivateReadPairProductionTests)",
                    result_identities,
                )

    def test_common_resolver_authenticates_the_frozen_source_hook(self) -> None:
        raw = SKIP_STRING_RESOLVER_MAP.read_bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            SKIP_STRING_RESOLVER_MAP_SHA256,
        )
        resolver_map = self.resolver_map()
        self.assertEqual(len(resolver_map.resolutions), 1)
        resolution = next(iter(resolver_map.resolutions.values()))
        self.assertEqual(
            resolution.resolved_identity,
            "setUpClass "
            "(test_runtime_nanopb_decode_svarint_production."
            "NanopbDecodeSvarintLinuxBuildMutationTests)",
        )
        self.assertEqual(
            resolution.provenance,
            {
                "method": "source_test_class_setUpClass",
                "source_blob_sha1": "eb29b429684523718b39055259642a8696ddc4cd",
                "source_class": "NanopbDecodeSvarintLinuxBuildMutationTests",
                "source_path": (
                    "tests/test_runtime_nanopb_decode_svarint_production.py"
                ),
                "source_revision": (
                    "7e78e38e4401bc095cca266e8708249f6da47780"
                ),
                "source_sha256": (
                    "247e6c8e5493e4851675407b0d7bfec4bc0f0b8fac8b2b09967d99327dbfaf8b"
                ),
            },
        )


if __name__ == "__main__":
    unittest.main()
