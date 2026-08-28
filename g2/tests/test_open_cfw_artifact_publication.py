# SPDX-License-Identifier: MIT
"""Transactional publication and strict release checks for ``open_cfw``."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock


G2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2_ROOT / "tools"))

import open_cfw  # noqa: E402


MANIFEST = G2_ROOT / "manifests/g2-2.2.6.10.json"


def _write_generation(root: Path, generation: str) -> dict[str, bytes]:
    package = f"{generation}-package".encode()
    region = f"{generation}-region".encode()
    package_relative = "package/release.bin"
    region_relative = "regions/controller/region.bin"
    open_cfw.atomic_write(root / package_relative, package)
    open_cfw.atomic_write(root / region_relative, region)
    report = {
        "generation": generation,
        "package": {
            "artifact": package_relative,
            "size": len(package),
            "sha256": open_cfw.sha256_bytes(package),
        },
    }
    plan = {
        "package_artifact": package_relative,
        "package_sha256": open_cfw.sha256_bytes(package),
        "flash_regions": [
            {
                "artifact": region_relative,
                "size": len(region),
                "sha256": open_cfw.sha256_bytes(region),
            }
        ],
        "unresolved_flash_regions": [],
        "container_only_regions": [],
    }
    open_cfw.atomic_write_json(root / "flash-plan.json", plan)
    open_cfw.atomic_write_json(root / "build-report.json", report)
    paths = {
        package_relative,
        region_relative,
        "flash-plan.json",
        "build-report.json",
    }
    open_cfw.write_sha256s(root, paths)
    return {
        relative: (root / relative).read_bytes()
        for relative in (*sorted(paths), "SHA256SUMS")
    }


def _managed_bytes(root: Path) -> dict[str, bytes]:
    ledger = open_cfw.parse_sha256s(root)
    return {
        relative: (root / relative).read_bytes()
        for relative in (*sorted(ledger), "SHA256SUMS")
    }


class OpenCFWPublicationTests(unittest.TestCase):
    def test_managed_readers_reject_symlinks_and_special_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.bin"
            target.write_bytes(b"managed")

            artifact = root / "artifact.bin"
            artifact.symlink_to(target.name)
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "symlink"):
                open_cfw.write_sha256s(root, {"artifact.bin"})

            report = root / "build-report.json"
            report.symlink_to(target.name)
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "build report"):
                open_cfw._read_json_object(report, "build report")

            ledger_target = root / "ledger.txt"
            ledger_target.write_text(
                f"{open_cfw.sha256_bytes(target.read_bytes())}  target.bin\n",
                encoding="utf-8",
            )
            ledger = root / "SHA256SUMS"
            ledger.symlink_to(ledger_target.name)
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "checksum ledger"):
                open_cfw.parse_sha256s(root)

            special = root / "special"
            os.mkfifo(special)
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "not a regular file"):
                open_cfw._read_regular_file_below(
                    root, "special", "managed special file"
                )

    def test_generation_lock_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protected = root / "protected.txt"
            protected.write_text("preserve", encoding="utf-8")
            (root / ".open-cfw-publish.lock").symlink_to(protected.name)
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "output generation lock"
            ):
                with open_cfw.output_generation_lock(root):
                    self.fail("symlinked lock must not be acquired")
            self.assertEqual(protected.read_text(encoding="utf-8"), "preserve")

    def test_stable_publication_preserves_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            staging = base / "staging"
            output = base / "output"
            staging.mkdir()
            output.mkdir()
            _write_generation(staging, "stable")
            unrelated = output / "user-notes.txt"
            unrelated.write_text("preserve me", encoding="utf-8")
            open_cfw.publish_staged_generation(staging, output)
            self.assertEqual(_managed_bytes(output), _managed_bytes(staging))
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "preserve me")

    def test_failed_publication_restores_prior_whole_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            output = base / "output"
            for path in (first, second, output):
                path.mkdir()
            _write_generation(first, "first")
            _write_generation(second, "second")
            open_cfw.publish_staged_generation(first, output)
            before = _managed_bytes(output)
            real_atomic_write = open_cfw.atomic_write
            failed = False

            def fail_once(path: Path, payload: bytes) -> None:
                nonlocal failed
                if path.name == "flash-plan.json" and not failed:
                    failed = True
                    raise OSError("injected publication failure")
                real_atomic_write(path, payload)

            with mock.patch.object(
                open_cfw, "atomic_write", side_effect=fail_once
            ):
                with self.assertRaisesRegex(OSError, "injected"):
                    open_cfw.publish_staged_generation(second, output)
            self.assertTrue(failed)
            self.assertEqual(_managed_bytes(output), before)

    def test_concurrent_publishers_leave_one_whole_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            output = base / "output"
            output.mkdir()
            stages = []
            expected: dict[str, dict[str, bytes]] = {}
            for generation in ("alpha", "beta"):
                stage = base / generation
                stage.mkdir()
                expected[generation] = _write_generation(stage, generation)
                stages.append(stage)
            barrier = threading.Barrier(len(stages))

            def publish(stage: Path) -> None:
                barrier.wait()
                open_cfw.publish_staged_generation(stage, output)

            with ThreadPoolExecutor(max_workers=2) as executor:
                list(executor.map(publish, stages))
            report = json.loads(
                (output / "build-report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                _managed_bytes(output), expected[report["generation"]]
            )

    def test_forged_ledger_cannot_authorize_unrelated_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            output = base / "output"
            for path in (first, second, output):
                path.mkdir()
            _write_generation(first, "first")
            _write_generation(second, "second")
            open_cfw.publish_staged_generation(first, output)
            unrelated = output / "regions/user-owned.bin"
            unrelated.write_bytes(b"do not delete")
            with (output / "SHA256SUMS").open("a", encoding="utf-8") as ledger:
                ledger.write(
                    f"{open_cfw.sha256_file(unrelated)}  "
                    "regions/user-owned.bin\n"
                )
            open_cfw.publish_staged_generation(second, output)
            self.assertEqual(unrelated.read_bytes(), b"do not delete")

    def test_unique_atomic_writes_leave_no_shared_temporary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "artifact.bin"
            payloads = [bytes([index]) * (2048 + index) for index in range(16)]
            with ThreadPoolExecutor(max_workers=8) as executor:
                list(executor.map(
                    lambda payload: open_cfw.atomic_write(target, payload),
                    payloads,
                ))
            self.assertIn(target.read_bytes(), payloads)
            self.assertEqual(list(root.glob(".artifact.bin.*")), [])


class OpenCFWStrictReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest, _, cls.payloads = open_cfw.verify_manifest(MANIFEST)

    def validate(self, manifest: dict) -> None:
        open_cfw.validate_release_manifest(
            manifest,
            toolchain_profile="apple-clang",
            payloads=self.payloads,
        )

    def test_canonical_manifest_passes_strict_contract(self) -> None:
        self.validate(copy.deepcopy(self.manifest))

    def test_missing_package_pin_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["package"].pop("expected_sha256")
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "mandatory SHA-256"):
            self.validate(manifest)

    def test_changed_component_set_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"].pop()
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "exactly six"):
            self.validate(manifest)

    def test_duplicate_entry_identity_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"][1]["entry_id"] = (
            manifest["components"][0]["entry_id"]
        )
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "identities"):
            self.validate(manifest)

    def test_cross_component_output_collision_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"][1]["regions"][0]["output"] = (
            manifest["components"][0]["regions"][0]["output"]
        )
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "duplicated"):
            self.validate(manifest)

    def test_unknown_address_status_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"][0]["regions"][0]["address_status"] = "guess"
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "not allowed"):
            self.validate(manifest)

    def test_unsafe_region_output_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"][0]["regions"][0]["output"] = "../escape.bin"
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "safe relative"):
            self.validate(manifest)

    def test_unpinned_selected_profile_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "pins are mandatory"):
            open_cfw.validate_release_manifest(
                manifest,
                toolchain_profile="not-reviewed",
                payloads=self.payloads,
            )

    def test_changed_protected_boundary_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["protected_regions"][0]["end_exclusive"] += 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "boundaries changed"):
            self.validate(manifest)


class OpenCFWArtifactVerificationTests(unittest.TestCase):
    def test_complete_generation_verifies_and_region_tamper_fails(self) -> None:
        build_parent = G2_ROOT / "build"
        build_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_parent) as temporary:
            output = Path(temporary)
            report = open_cfw.build(MANIFEST, output)
            verified = open_cfw.verify_artifacts(MANIFEST, output)
            self.assertEqual(verified, report)
            with open_cfw.output_generation_lock(output):
                self.assertEqual(
                    open_cfw.verify_artifacts_with_lock_held(MANIFEST, output),
                    report,
                )
            self.assertEqual(
                open_cfw.main([
                    "verify-artifacts",
                    "--manifest", str(MANIFEST),
                    "--output-dir", str(output),
                    "--toolchain-profile", "apple-clang",
                ]),
                0,
            )
            self.assertEqual(report["toolchain_profile"], "apple-clang")
            self.assertEqual(
                report["manifest_sha256"],
                open_cfw.effective_manifest_sha256(
                    open_cfw.load_manifest(MANIFEST)
                ),
            )
            plan = json.loads(
                (output / "flash-plan.json").read_text(encoding="utf-8")
            )
            region = output / plan["flash_regions"][0]["artifact"]
            original = region.read_bytes()
            region.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "region artifact differs"
            ):
                open_cfw.verify_artifacts(MANIFEST, output)
            region.write_bytes(original)

            package = output / report["package"]["artifact"]
            original = package.read_bytes()
            package.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "package differs"
            ):
                open_cfw.verify_artifacts(MANIFEST, output)
            package.write_bytes(original)

            plan_path = output / "flash-plan.json"
            original = plan_path.read_bytes()
            changed = json.loads(original)
            changed["toolchain_profile"] = "tampered"
            plan_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "flash plan differs"
            ):
                open_cfw.verify_artifacts(MANIFEST, output)
            plan_path.write_bytes(original)

            report_path = output / "build-report.json"
            original = report_path.read_bytes()
            changed = json.loads(original)
            changed["entries"][0]["entry_id"] = 99
            report_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "build report differs"
            ):
                open_cfw.verify_artifacts(MANIFEST, output)
            report_path.write_bytes(original)

            ledger_path = output / "SHA256SUMS"
            original = ledger_path.read_bytes()
            ledger_path.write_bytes(b"0" + original[1:])
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "checksum ledger mismatch"
            ):
                open_cfw.verify_artifacts(MANIFEST, output)


if __name__ == "__main__":
    unittest.main()
