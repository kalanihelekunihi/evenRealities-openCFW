"""Gate the unpacked research corpus and the verifier that authenticates it."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import tempfile
import unittest
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
    "apollo-main", "em9305", "iar", "qpc", "source-lanes", "wsf",
}


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_research_corpus", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        # 45 = the 44 delivered manifests plus the locally produced
        # apollo-main/ghidra/decomp/SHA256SUMS, which authenticates the
        # harvested decompilation the transparent-source pipeline consumes.
        manifests, checked = self.module.verify_embedded()
        self.assertEqual(manifests, 45)
        self.assertEqual(checked, 1912)

    def test_index_covers_the_corpus_exactly(self) -> None:
        # 1950 delivered files plus the 19-file decompilation harvest.
        self.assertEqual(self.module.verify_index(), 1969)

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

    def test_edited_evidence_is_rejected(self) -> None:
        target = CORPUS / "qpc" / "full8-report.json"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b" ")
            with self.assertRaises(self.module.CorpusError):
                self.module.verify_embedded()
        finally:
            target.write_bytes(original)
        self.module.verify_embedded()

    def test_added_evidence_is_rejected(self) -> None:
        intruder = CORPUS / "qpc" / "not-delivered.json"
        self.assertFalse(intruder.exists())
        try:
            intruder.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(self.module.CorpusError):
                self.module.verify_index()
        finally:
            intruder.unlink(missing_ok=True)
        self.module.verify_index()

    def test_removed_evidence_is_rejected(self) -> None:
        target = CORPUS / "qpc" / "full8-report.json"
        original = target.read_bytes()
        try:
            target.unlink()
            with self.assertRaises(self.module.CorpusError):
                self.module.verify_index()
        finally:
            target.write_bytes(original)
        self.module.verify_index()

    def test_index_matches_a_freshly_computed_one(self) -> None:
        """MANIFEST.sha256 is exactly what --write-manifest would produce."""
        expected = []
        for path in self.module.corpus_files():
            if path.name in self.module.SELF_DESCRIBING:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            expected.append(f"{digest}  {path.relative_to(RESEARCH).as_posix()}")
        self.assertEqual(
            MANIFEST.read_text(encoding="utf-8"), "\n".join(expected) + "\n"
        )


if __name__ == "__main__":
    unittest.main()
