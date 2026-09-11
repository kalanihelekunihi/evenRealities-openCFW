# SPDX-License-Identifier: MIT
"""Pin the Touch source image as the production provider in a manifest
profile: g2-2.2.6.10-touch-source-experimental.json overrides the `touch`
component from `official_blob` to this repository's `source_build` output,
and the assembled package must exactly match what the manifest declares.
No hardware is touched; this only exercises the host-side manifest/build
machinery.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/g2-2.2.6.10-touch-source-experimental.json"
BUILDER = ROOT / "components/touch/source_image/build_image.py"
OPEN_CFW = ROOT / "tools/open_cfw.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER_MODULE = _load(BUILDER, "touch_source_manifest_routing_builder")
OPEN_CFW_MODULE = _load(OPEN_CFW, "touch_source_manifest_routing_open_cfw")


class TouchSourceManifestRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_data = json.loads(MANIFEST.read_text())
        cls.merged = OPEN_CFW_MODULE.load_manifest(MANIFEST)
        cls.touch = next(
            component for component in cls.merged["components"]
            if component["name"] == "touch")

    def test_manifest_overrides_touch_to_source_build(self) -> None:
        self.assertEqual(
            self.manifest_data["component_overrides"]["touch"]
            ["provider"]["kind"], "source_build")
        self.assertEqual(self.touch["provider"]["kind"], "source_build")
        # Every other component stays the untouched official reference; this
        # item routes touch only.
        for component in self.merged["components"]:
            if component["name"] != "touch":
                self.assertEqual(component["provider"]["kind"],
                                 "official_blob")

    def test_touch_application_region_is_source_compiled(self) -> None:
        regions = {region["name"]: region for region in self.touch["regions"]}
        self.assertEqual(
            regions["touch_application"]["address_status"], "source_compiled")
        self.assertEqual(regions["fwpk_wrapper"]["address_status"],
                         "container_only")

    def test_provider_pins_match_the_freshly_built_source_image(self) -> None:
        project_root = OPEN_CFW_MODULE.project_root_for_manifest(MANIFEST)
        with_temp = project_root / "build" / "touch-source-image"
        report = BUILDER_MODULE.build(with_temp)
        provider = self.touch["provider"]
        self.assertEqual(provider["size"], report["fwpk"]["size"])
        self.assertEqual(provider["sha256"], report["fwpk"]["sha256"])
        expected_path = (project_root / provider["path"]).resolve()
        self.assertEqual(expected_path,
                         (with_temp / report["fwpk"]["path"]).resolve())

    def test_manifest_verifies_and_assembles_deterministically(self) -> None:
        BUILDER_MODULE.build(ROOT / "build" / "touch-source-image")
        manifest, project_root, payloads = OPEN_CFW_MODULE.verify_manifest(
            MANIFEST, toolchain_profile="apple-clang", strict_release=True)
        image_one, _ = OPEN_CFW_MODULE.assemble_evenota(manifest, payloads)
        image_two, _ = OPEN_CFW_MODULE.assemble_evenota(manifest, payloads)
        self.assertEqual(image_one, image_two)
        self.assertEqual(len(image_one), manifest["package"]["expected_size"])
        self.assertEqual(OPEN_CFW_MODULE.sha256_bytes(image_one),
                         manifest["package"]["expected_sha256"])

    def test_hardware_qualification_stays_out_of_scope(self) -> None:
        # This item routes software; it must not claim hardware readiness.
        self.assertIn("hardware", self.touch["function"].lower())


if __name__ == "__main__":
    unittest.main()
