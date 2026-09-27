import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/g2-2.2.6.10-case-source-experimental.json"
BUILDER = ROOT / "components/case/source_image/build_image.py"
OPEN_CFW = ROOT / "tools/open_cfw.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER_MODULE = _load(BUILDER, "case_source_manifest_routing_builder")
OPEN_CFW_MODULE = _load(OPEN_CFW, "case_source_manifest_routing_open_cfw")


class CaseSourceManifestRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_data = json.loads(MANIFEST.read_text())
        cls.merged = OPEN_CFW_MODULE.load_manifest(MANIFEST)
        cls.case = next(
            component for component in cls.merged["components"]
            if component["name"] == "case")

    def test_manifest_overrides_case_to_source_build(self) -> None:
        self.assertEqual(
            self.manifest_data["component_overrides"]["case"]
            ["provider"]["kind"], "source_build")
        self.assertEqual(self.case["provider"]["kind"], "source_build")
        for component in self.merged["components"]:
            if component["name"] != "case":
                self.assertEqual(component["provider"]["kind"],
                                 "official_blob")

    def test_case_application_region_is_source_compiled(self) -> None:
        regions = {region["name"]: region for region in self.case["regions"]}
        self.assertEqual(
            regions["case_application"]["address_status"], "source_compiled")
        self.assertEqual(regions["even_wrapper"]["address_status"],
                         "container_only")

    def test_provider_pins_match_the_freshly_built_source_image(self) -> None:
        project_root = OPEN_CFW_MODULE.project_root_for_manifest(MANIFEST)
        output = project_root / "build" / "case-source-image"
        report = BUILDER_MODULE.build(output)
        provider = self.case["provider"]
        self.assertEqual(provider["size"], report["even"]["size"])
        self.assertEqual(provider["sha256"], report["even"]["sha256"])
        self.assertEqual(
            (project_root / provider["path"]).resolve(),
            (output / report["even"]["path"]).resolve(),
        )

    def test_manifest_verifies_and_assembles_deterministically(self) -> None:
        BUILDER_MODULE.build(ROOT / "build" / "case-source-image")
        manifest, _, payloads = OPEN_CFW_MODULE.verify_manifest(
            MANIFEST, toolchain_profile="apple-clang", strict_release=True)
        image_one, _ = OPEN_CFW_MODULE.assemble_evenota(manifest, payloads)
        image_two, _ = OPEN_CFW_MODULE.assemble_evenota(manifest, payloads)
        self.assertEqual(image_one, image_two)
        self.assertEqual(len(image_one), manifest["package"]["expected_size"])
        self.assertEqual(OPEN_CFW_MODULE.sha256_bytes(image_one),
                         manifest["package"]["expected_sha256"])

    def test_hardware_qualification_stays_out_of_scope(self) -> None:
        self.assertIn("physical", self.case["function"].lower())


if __name__ == "__main__":
    unittest.main()
