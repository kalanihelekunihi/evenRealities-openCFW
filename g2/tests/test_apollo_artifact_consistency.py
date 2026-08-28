#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from g2.tools.apollo_artifact_consistency import (
    validate_apollo_main_artifacts,
    validate_region_tiling,
)


class ArtifactError(RuntimeError):
    pass


class ApolloArtifactConsistencyTests(unittest.TestCase):
    def make_tree(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        paths = [
            root / "components/apollo_main/core_overlay/build",
            root / "manifests", root / "build/source/package", root / "build/source",
        ]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
        package = b"current package"
        digest = hashlib.sha256(package).hexdigest()
        overlay = {"expected": {"overlay_size": 7, "overlay_sha256": "overlay",
                                "component_size": 11, "component_sha256": "component"}}
        build = {"overlay": {"size": 7, "sha256": "overlay"},
                 "component": {"size": 11, "sha256": "component"}}
        manifest = {"component_overrides": {"apollo_main": {"provider": {
                        "size": 11, "sha256": "component"}}},
                    "package": {"output_name": "package.bin", "expected_size": len(package),
                                "expected_sha256": digest}}
        plan = {"package_sha256": digest, "flash_regions": [{}],
                "unresolved_flash_regions": [], "container_only_regions": [],
                "protected_regions": []}
        (root / "components/apollo_main/core_overlay/overlay.json").write_text(json.dumps(overlay))
        (root / "components/apollo_main/core_overlay/build/build-report.json").write_text(json.dumps(build))
        (root / "manifests/g2-2.2.6.10-core-source.json").write_text(json.dumps(manifest))
        (root / "build/source/package/package.bin").write_bytes(package)
        (root / "build/source/flash-plan.json").write_text(json.dumps(plan))
        return temporary, root

    def test_consistent_dynamic_artifacts_pass(self):
        temporary, root = self.make_tree()
        try:
            result = validate_apollo_main_artifacts(root, ArtifactError, "test")
            self.assertEqual((result["overlay"]["size"], result["component"]["size"]), (7, 11))
            self.assertEqual(result["unresolved_flash_regions"], 0)
        finally:
            temporary.cleanup()

    def test_each_cross_artifact_drift_fails_closed(self):
        mutations = (
            ("components/apollo_main/core_overlay/overlay.json",
             ("expected", "overlay_size"), 8),
            ("components/apollo_main/core_overlay/build/build-report.json",
             ("component", "sha256"), "changed"),
            ("manifests/g2-2.2.6.10-core-source.json",
             ("component_overrides", "apollo_main", "provider", "size"), 12),
            ("build/source/flash-plan.json", ("package_sha256",), "changed"),
            ("build/source/flash-plan.json", ("flash_regions",), []),
            ("build/source/flash-plan.json", ("unresolved_flash_regions",), [{}]),
            ("build/source/flash-plan.json", ("container_only_regions",), None),
            ("build/source/flash-plan.json", ("protected_regions",), None),
        )
        for relative, keys, value in mutations:
            temporary, root = self.make_tree()
            try:
                path = root / relative
                data = json.loads(path.read_text())
                parent = data
                for key in keys[:-1]:
                    parent = parent[key]
                if value is None:
                    del parent[keys[-1]]
                else:
                    parent[keys[-1]] = value
                path.write_text(json.dumps(data))
                with self.assertRaises(ArtifactError):
                    validate_apollo_main_artifacts(root, ArtifactError, "test")
            finally:
                temporary.cleanup()

    def test_package_byte_drift_fails_closed(self):
        temporary, root = self.make_tree()
        try:
            (root / "build/source/package/package.bin").write_bytes(b"changed")
            with self.assertRaises(ArtifactError):
                validate_apollo_main_artifacts(root, ArtifactError, "test")
        finally:
            temporary.cleanup()

    def test_real_workspace_is_currently_consistent(self):
        root = Path(__file__).resolve().parents[1]
        result = validate_apollo_main_artifacts(root, ArtifactError, "workspace")
        self.assertGreater(result["flash_regions"], 0)

    def test_region_tiling_tracks_conservation_not_mutable_distribution(self):
        regions = [
            {"target_address": 10, "size": 4, "address_status": "official_blob"},
            {"target_address": 14, "size": 6,
             "address_status": "generated_source_entry_replacement"},
        ]
        self.assertEqual(validate_region_tiling(regions, 10, 20, ArtifactError), {
            "official_blob": 4, "generated_source_entry_replacement": 6,
        })
        regions[1]["target_address"] = 15
        with self.assertRaises(ArtifactError):
            validate_region_tiling(regions, 10, 20, ArtifactError)


if __name__ == "__main__":
    unittest.main()
