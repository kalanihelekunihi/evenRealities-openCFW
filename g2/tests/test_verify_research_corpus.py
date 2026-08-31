"""Gate the unpacked research corpus and the verifier that authenticates it."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_research_corpus.py"
RESEARCH = ROOT / "research"
CORPUS = RESEARCH / "corpus"
READINESS = RESEARCH / "readiness"
MANIFEST = RESEARCH / "MANIFEST.sha256"

# The twenty-four per-topic readiness artifacts the Cordio analyzers consume.
EXPECTED_TOPICS = {
    "attc-disc", "atts-ccc", "atts-csf",
    "dm-adv", "dm-adv-leg", "dm-conn", "dm-conn-master", "dm-conn-sm",
    "dm-dev", "dm-dev-priv", "dm-main", "dm-phy", "dm-priv",
    "dm-sec", "dm-sec-lesc", "dm-sec-master", "dm-sec-slave",
    "smp-db", "smp-main",
    "wsf-assert-trace", "wsf-buf", "wsf-efs-inclusion-census",
    "wsf-os-queue-stockabi", "wstr",
}

EXPECTED_CORPUS_SUBJECTS = {
    "apollo-main", "case", "em9305", "iar", "qpc", "source-lanes", "wsf",
}


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_research_corpus", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def isolated_research(module):
    """Patch the verifier onto a disposable, structurally valid research tree."""
    with tempfile.TemporaryDirectory() as directory:
        research = Path(directory) / "research"
        corpus = research / "corpus"
        readiness = research / "readiness"
        (corpus / "qpc").mkdir(parents=True)
        (readiness / "topic").mkdir(parents=True)
        manifest = research / "MANIFEST.sha256"
        manifest.write_text("original\n", encoding="utf-8")
        with mock.patch.multiple(
            module,
            RESEARCH=research,
            CORPUS=corpus,
            READINESS=readiness,
            MANIFEST=manifest,
            KNOWN_EXCLUSIONS={},
            REVIEWED_MUTATIONS={},
        ):
            yield research


class ResearchCorpusLayoutTests(unittest.TestCase):
    """The corpus is stored unpacked, unified, and free of the host name."""

    def test_no_compressed_archives_remain(self) -> None:
        archives = sorted(
            p.relative_to(RESEARCH).as_posix()
            for p in RESEARCH.rglob("*")
            if p.is_file() and p.name.endswith((".tar.gz", ".tgz", ".tar", ".zip"))
        )
        self.assertEqual(archives, [], "research evidence must be stored unpacked")

    def test_host_name_is_not_part_of_the_layout(self) -> None:
        """`lorelei` was a machine, not a subject. It may survive only in prose."""
        offenders = sorted(
            p.relative_to(ROOT).as_posix()
            for p in RESEARCH.rglob("*")
            if "lorelei" in p.name.lower()
        )
        self.assertEqual(offenders, [])

        manifests = sorted(
            p.name for p in (ROOT / "tools" / "manifests").glob("lorelei-*")
        )
        self.assertEqual(manifests, [])

    def test_readiness_topics_are_complete(self) -> None:
        topics = {p.name for p in READINESS.iterdir() if p.is_dir()}
        self.assertEqual(topics, EXPECTED_TOPICS)

    def test_every_readiness_topic_carries_its_delivered_manifest(self) -> None:
        for topic in sorted(EXPECTED_TOPICS):
            with self.subTest(topic=topic):
                self.assertTrue((READINESS / topic / "SHA256SUMS").is_file())

    def test_corpus_is_filed_by_subject(self) -> None:
        subjects = {p.name for p in CORPUS.iterdir() if p.is_dir()}
        self.assertEqual(subjects, EXPECTED_CORPUS_SUBJECTS)

    def test_provenance_and_lane_manifest_are_present(self) -> None:
        self.assertTrue((CORPUS / "PROVENANCE.md").is_file())
        self.assertTrue((CORPUS / "SHA256SUMS.lane-bundle").is_file())


class ResearchCorpusIntegrityTests(unittest.TestCase):
    """The verifier authenticates the corpus and fails closed on any drift."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_verifier()

    def test_embedded_manifests_verify_in_place(self) -> None:
        # The immutable delivery set plus the reviewed Apollo PT and Case
        # harvest envelopes all authenticate in place.
        manifests, checked = self.module.verify_embedded()
        self.assertEqual(manifests, 47)
        self.assertEqual(checked, 1918)

    def test_index_covers_the_corpus_exactly(self) -> None:
        self.assertEqual(self.module.verify_index(), 1977)

    def test_reviewed_mutation_allowlist_is_exact(self) -> None:
        expected = {
            "corpus/iar/math-errno/iar_runtime_math_errno.S",
            "corpus/wsf/current11/inputs/runtime_cordio_wsf_timer_candidate.c",
            "corpus/wsf/current11/inputs/runtime_cordio_wsf_timer_candidate.h",
            "corpus/wsf/current11-v2/runtime_cordio_wsf_timer_candidate.c",
            "corpus/wsf/current11-v2/runtime_cordio_wsf_timer_candidate.h",
        }
        self.assertEqual(set(self.module.REVIEWED_MUTATIONS), expected)
        self.assertEqual(len(self.module.REVIEWED_MUTATIONS), 5)
        for name, mutation in self.module.REVIEWED_MUTATIONS.items():
            with self.subTest(name=name):
                self.assertRegex(mutation["delivered_sha256"], r"^[0-9a-f]{64}$")
                self.assertRegex(mutation["current_sha256"], r"^[0-9a-f]{64}$")
                self.assertNotEqual(
                    mutation["delivered_sha256"], mutation["current_sha256"]
                )
                self.assertIn("SPDX-only", mutation["reason"])

    def test_every_exclusion_is_justified(self) -> None:
        """Nothing may drop out of a delivered manifest without a stated reason."""
        exclusions = self.module.KNOWN_EXCLUSIONS
        self.assertEqual(len(exclusions), 4)
        for name, reason in exclusions.items():
            with self.subTest(name=name):
                self.assertTrue(reason, "exclusion needs a reason")
                self.assertTrue(
                    name.endswith(".pyc") or reason.startswith("duplicate of"),
                    "only regenerable caches and proven duplicates may be excluded",
                )
        for name, reason in exclusions.items():
            if reason.startswith("duplicate of"):
                target = RESEARCH / reason[len("duplicate of "):].rstrip("/")
                self.assertTrue(target.is_dir(), f"{name} points at a missing twin")

    def test_index_matches_a_freshly_computed_one(self) -> None:
        """MANIFEST.sha256 is exactly what --write-manifest would produce."""
        expected = []
        for path in self.module.corpus_files():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            expected.append(f"{digest}  {path.relative_to(RESEARCH).as_posix()}")
        self.assertEqual(
            MANIFEST.read_text(encoding="utf-8"), "\n".join(expected) + "\n"
        )


class ResearchCorpusVerifierSecurityTests(unittest.TestCase):
    """Hostile path and filesystem shapes fail closed in disposable trees."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_verifier()

    @staticmethod
    def _write_embedded(research: Path, name: str = "evidence.bin") -> Path:
        member = research / "corpus" / "qpc" / name
        member.parent.mkdir(parents=True, exist_ok=True)
        member.write_bytes(b"authenticated evidence\n")
        digest = hashlib.sha256(member.read_bytes()).hexdigest()
        (research / "corpus" / "qpc" / "SHA256SUMS").write_text(
            f"{digest}  {name}\n", encoding="utf-8"
        )
        return member

    def test_delivered_dot_slash_member_spelling_is_normalized_once(self) -> None:
        with isolated_research(self.module) as research:
            member = self._write_embedded(research)
            digest = hashlib.sha256(member.read_bytes()).hexdigest()
            (member.parent / "SHA256SUMS").write_text(
                f"{digest}  ./evidence.bin\n", encoding="utf-8"
            )
            self.assertEqual(self.module.verify_embedded(), (1, 1))

    def test_manifest_traversal_and_aliases_are_rejected(self) -> None:
        with isolated_research(self.module) as research:
            member = self._write_embedded(research)
            digest = hashlib.sha256(member.read_bytes()).hexdigest()
            manifest = member.parent / "SHA256SUMS"
            for hostile in ("../../outside", "/outside", "sub\\outside", "a//b"):
                with self.subTest(hostile=hostile):
                    manifest.write_text(
                        f"{digest}  {hostile}\n", encoding="utf-8"
                    )
                    with self.assertRaisesRegex(self.module.CorpusError, "unsafe"):
                        self.module.verify_embedded()
            manifest.write_text(
                f"{digest}  evidence.bin\n{digest}  ./evidence.bin\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(self.module.CorpusError, "duplicate"):
                self.module.verify_embedded()

    def test_symlink_and_hardlink_members_are_rejected(self) -> None:
        with isolated_research(self.module) as research:
            outside = Path(research.parent) / "outside.bin"
            outside.write_bytes(b"outside\n")
            link = research / "corpus" / "qpc" / "link.bin"
            link.symlink_to(outside)
            with self.assertRaisesRegex(self.module.CorpusError, "symlink"):
                self.module.corpus_files()
            link.unlink()

            original = research / "corpus" / "qpc" / "original.bin"
            alias = research / "corpus" / "qpc" / "alias.bin"
            original.write_bytes(b"same inode\n")
            os.link(original, alias)
            with self.assertRaisesRegex(self.module.CorpusError, "hard-linked"):
                self.module.corpus_files()

    def test_research_root_identity_swap_is_rejected(self) -> None:
        with isolated_research(self.module) as research:
            moved = research.with_name("held-research")
            replacement = research.with_name("replacement-research")
            replacement.mkdir()
            with self.module._ResearchSnapshot() as snapshot:
                research.rename(moved)
                research.symlink_to(replacement, target_is_directory=True)
                with self.assertRaisesRegex(
                    self.module.CorpusError, "root identity changed"
                ):
                    snapshot.assert_root_identity()

    def test_file_change_during_descriptor_read_is_rejected(self) -> None:
        with isolated_research(self.module) as research:
            member = self._write_embedded(research)
            real_read = os.read
            changed = False

            def racing_read(descriptor: int, size: int) -> bytes:
                nonlocal changed
                chunk = real_read(descriptor, size)
                if not changed:
                    with member.open("ab") as handle:
                        handle.write(b"drift")
                    changed = True
                return chunk

            with self.module._ResearchSnapshot() as snapshot:
                with mock.patch.object(
                    self.module.os, "read", side_effect=racing_read
                ):
                    with self.assertRaisesRegex(
                        self.module.CorpusError, "changed while being read"
                    ):
                        snapshot.read("corpus/qpc/evidence.bin")

    def test_atomic_writer_is_deterministic(self) -> None:
        with isolated_research(self.module) as research:
            self._write_embedded(research)
            readiness = research / "readiness" / "topic" / "result.json"
            readiness.write_text("{}\n", encoding="utf-8")
            self.assertEqual(self.module.write_index(), 3)
            first = (research / "MANIFEST.sha256").read_bytes()
            self.assertEqual(self.module.write_index(), 3)
            self.assertEqual((research / "MANIFEST.sha256").read_bytes(), first)
            self.assertFalse(list(research.glob(".MANIFEST.sha256.tmp.*")))

    def test_failed_atomic_replace_preserves_manifest_and_cleans_temp(self) -> None:
        with isolated_research(self.module) as research:
            self._write_embedded(research)
            manifest = research / "MANIFEST.sha256"
            original = manifest.read_bytes()
            with mock.patch.object(
                self.module.os, "replace", side_effect=OSError("injected failure")
            ):
                with self.assertRaisesRegex(
                    self.module.CorpusError, "atomic research manifest"
                ):
                    self.module.write_index()
            self.assertEqual(manifest.read_bytes(), original)
            self.assertFalse(list(research.glob(".MANIFEST.sha256.tmp.*")))

    def test_atomic_writer_parent_swap_cannot_redirect_replacement(self) -> None:
        with isolated_research(self.module) as research:
            self._write_embedded(research)
            held = research.with_name("held-research")
            redirected = research.with_name("redirected-research")
            redirected.mkdir()
            redirected_manifest = redirected / "MANIFEST.sha256"
            redirected_manifest.write_bytes(b"redirected tree\n")
            real_replace = os.replace

            def swap_parent_then_replace(
                source: str,
                destination: str,
                *,
                src_dir_fd: int,
                dst_dir_fd: int,
            ) -> None:
                research.rename(held)
                research.symlink_to(redirected, target_is_directory=True)
                real_replace(
                    source,
                    destination,
                    src_dir_fd=src_dir_fd,
                    dst_dir_fd=dst_dir_fd,
                )

            with mock.patch.object(
                self.module.os, "replace", side_effect=swap_parent_then_replace
            ):
                with self.assertRaisesRegex(
                    self.module.CorpusError, "root identity changed"
                ):
                    self.module.write_index()
            self.assertEqual(redirected_manifest.read_bytes(), b"redirected tree\n")
            self.assertNotEqual(
                (held / "MANIFEST.sha256").read_bytes(), b"original\n"
            )


if __name__ == "__main__":
    unittest.main()
