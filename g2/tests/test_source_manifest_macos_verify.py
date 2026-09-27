import unittest
from pathlib import Path

from tools import open_cfw


ROOT = Path(__file__).resolve().parents[1]


class SourceManifestMacOSVerifyTests(unittest.TestCase):
    def test_source_and_experimental_manifests_verify_on_apple_clang(self) -> None:
        manifests = [
            "g2-2.2.6.10-case-source-experimental.json",
            "g2-2.2.6.10-codec-source-experimental.json",
            "g2-2.2.6.10-core-source.json",
            "g2-2.2.6.10-minimal-name-hook.json",
            "g2-2.2.6.10-name-memcpy-hook.json",
            "g2-2.2.6.10-ring-source.json",
            "g2-2.2.6.10-source-only.json",
            "g2-2.2.6.10-touch-source-experimental.json",
        ]
        for name in manifests:
            with self.subTest(manifest=name):
                manifest_path = ROOT / "manifests" / name
                manifest, _, payloads = open_cfw.verify_manifest(
                    manifest_path,
                    toolchain_profile="apple-clang",
                    strict_release=True,
                )
                image, _ = open_cfw.assemble_evenota(manifest, payloads)
                self.assertEqual(len(image), manifest["package"]["expected_size"])
                self.assertEqual(
                    open_cfw.sha256_bytes(image),
                    manifest["package"]["expected_sha256"],
                )


if __name__ == "__main__":
    unittest.main()
