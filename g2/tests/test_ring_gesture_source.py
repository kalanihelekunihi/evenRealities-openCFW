from __future__ import annotations

import os

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = (
    OPENCFW_ROOT / "components" / "apollo_main" / "ring_gesture"
)
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
sys.path.insert(0, str(COMPONENT_ROOT))

import build_component as ring_component  # noqa: E402
import open_cfw  # noqa: E402


SOURCE_MANIFEST_PATH = (
    OPENCFW_ROOT / "manifests" / "g2-2.2.6.10-ring-source.json"
)


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RingGestureSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.component_report = ring_component.build(
            root=OPENCFW_ROOT,
            config_path=COMPONENT_ROOT / "overlay.json",
            output_dir=COMPONENT_ROOT / "build",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.manifest, cls.project_root, cls.payloads = open_cfw.verify_manifest(
            SOURCE_MANIFEST_PATH
        )
        cls.image, cls.entries = open_cfw.assemble_evenota(
            cls.manifest,
            cls.payloads,
        )

    @_APPLE_ONLY
    def test_compiler_output_and_component_are_pinned(self) -> None:
        overlay = self.component_report["overlay"]
        component = self.component_report["component"]
        self.assertEqual(overlay["size"], 160)
        self.assertEqual(
            overlay["sha256"],
            "69eac5d0808709dce5946956d9b0568e610468b5298cbe23786f3d02868b8c78",
        )
        self.assertEqual(
            overlay["functions"],
            {
                "evenhub_longpress": {"offset": 0, "size": 54},
                "ring_release": {"offset": 56, "size": 104},
            },
        )
        self.assertEqual(component["size"], 3523556)
        self.assertEqual(
            component["sha256"],
            "fbfd509585c9487b5f65c32b0b5729c1d693a5dedbb84dc303c02d74aef6e2db",
        )

    def test_only_wrapper_redirects_and_overlay_diverge_from_base(self) -> None:
        base_path = OPENCFW_ROOT / self.component_report["base"]["path"]
        component_path = OPENCFW_ROOT / self.component_report["component"]["artifact"]
        overlay_path = OPENCFW_ROOT / self.component_report["overlay"]["artifact"]
        base = base_path.read_bytes()
        component = bytearray(component_path.read_bytes())
        overlay = overlay_path.read_bytes()

        self.assertEqual(bytes(component[len(base):]), overlay)
        component[:8] = base[:8]
        for site in self.component_report["overlay"]["patched_sites"]:
            offset = site["payload_offset"]
            expected = bytes.fromhex(site["expected_hex"])
            component[offset:offset + len(expected)] = expected
        self.assertEqual(bytes(component[:len(base)]), base)

    def test_generated_branches_land_on_exported_source_functions(self) -> None:
        for site in self.component_report["overlay"]["patched_sites"]:
            encoded = bytes.fromhex(site["replacement_hex"])
            target = ring_component.decode_thumb_bl(
                site["runtime_address"],
                encoded,
            )
            self.assertEqual(target, site["target_address"])
        self.assertEqual(
            {
                site["target_address_hex"]
                for site in self.component_report["overlay"]["patched_sites"]
            },
            {"0x00794324", "0x0079435C"},
        )

    def test_source_manifest_inherits_five_official_providers(self) -> None:
        providers = {
            component["name"]: component["provider"]["kind"]
            for component in self.manifest["components"]
        }
        self.assertEqual(providers["apollo_main"], "source_build")
        self.assertEqual(
            [kind for name, kind in providers.items() if name != "apollo_main"],
            ["official_blob"] * 5,
        )
        source_regions = {
            region["name"]: region
            for region in self.manifest["components"][-1]["regions"]
        }
        self.assertEqual(
            source_regions["ring_gesture_source_overlay"]["target_address"],
            0x00794324,
        )
        self.assertEqual(
            source_regions["ring_gesture_source_overlay"]["address_status"],
            "source_compiled",
        )

    @_APPLE_ONLY
    def test_source_evenota_is_pinned_and_build_plan_is_complete(self) -> None:
        package = self.manifest["package"]
        self.assertEqual(len(self.image), package["expected_size"])
        self.assertEqual(
            hashlib.sha256(self.image).hexdigest(),
            package["expected_sha256"],
        )
        build_parent = OPENCFW_ROOT / "build"
        build_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_parent) as temp:
            output = Path(temp)
            report = open_cfw.build(SOURCE_MANIFEST_PATH, output)
            plan = json.loads((output / "flash-plan.json").read_text())
            self.assertEqual(
                report["provider_mode"],
                "official_blob+source_build",
            )
            self.assertEqual(report["package"]["sha256"], package["expected_sha256"])
            self.assertEqual(
                {
                    region["region"]
                    for region in plan["flash_regions"]
                    if region["address_status"] == "generated_source_redirect"
                },
                {"long_press_source_redirect", "release_source_redirect"},
            )
            self.assertEqual(
                [
                    region["region"]
                    for region in plan["flash_regions"]
                    if region["address_status"] == "source_compiled"
                ],
                ["ring_gesture_source_overlay"],
            )


if __name__ == "__main__":
    unittest.main()
