# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import community_distribution as distribution  # noqa: E402


class CommunityMarkdownLinkClosureTests(unittest.TestCase):
    def test_assembled_public_member_set_has_closed_local_links(self) -> None:
        records = distribution._selected_records()
        payload = {
            archive_path: distribution._bundle_payload(
                path, distribution._read_regular_source_once(path)
            )
            for path, archive_path in records
        }
        distribution._verify_markdown_link_closure(payload)
        self.assertIn("README.md", payload)
        self.assertIn("Makefile", payload)
        self.assertIn("make.sh", payload)
        self.assertNotEqual(
            payload["README.md"],
            (distribution.REPOSITORY_ROOT / "README.md").read_bytes(),
        )
        self.assertEqual(
            payload["README.md"],
            (ROOT / "docs/community-archive-README.md").read_bytes(),
        )

    def test_dangling_local_target_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "dangling local Markdown link"
        ):
            distribution._verify_markdown_link_closure({
                "README.md": b"[missing](docs/missing.md)\n",
                "LICENSE": b"present\n",
            })

    def test_external_and_fragment_links_are_normalized(self) -> None:
        distribution._verify_markdown_link_closure({
            "README.md": (
                b"[section](#local) [web](https://example.com/x) "
                b"[guide](docs/guide.md#step)\n"
            ),
            "docs/guide.md": b"# Guide\n",
        })

    def test_reference_and_html_links_are_checked(self) -> None:
        payload = {
            "README.md": (
                b"[guide][g]\n[g]: docs/guide.md#top\n"
                b'<a href="docs/guide.md">guide</a>\n'
            ),
            "docs/guide.md": b"# Guide\n",
        }
        distribution._verify_markdown_link_closure(payload)
        payload["README.md"] = b"[guide][g]\n[g]: docs/missing.md\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "dangling local Markdown link"
        ):
            distribution._verify_markdown_link_closure(payload)

    def test_absolute_backslash_and_escape_targets_are_rejected(self) -> None:
        for target in ("/etc/passwd", "docs\\guide.md", "../../outside.md"):
            with self.subTest(target=target):
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError,
                    "(?:unsafe local Markdown link|escapes archive)",
                ):
                    distribution._verify_markdown_link_closure({
                        "docs/README.md": f"[bad]({target})\n".encode(),
                    })

    def test_root_entrypoints_are_single_link_regular_sources(self) -> None:
        expected = {
            "g2/community/Makefile": "Makefile",
            "g2/community/make.sh": "make.sh",
        }
        for source, destination in expected.items():
            path = distribution.REPOSITORY_ROOT / source
            metadata = os.stat(path, follow_symlinks=False)
            self.assertTrue(path.is_file())
            self.assertEqual(metadata.st_nlink, 1)
            self.assertEqual(
                distribution.RELOCATED_PUBLIC_SOURCES[source], destination
            )
        self.assertIn("make.sh", distribution.EXECUTABLE_ARCHIVE_PATHS)


if __name__ == "__main__":
    unittest.main()
