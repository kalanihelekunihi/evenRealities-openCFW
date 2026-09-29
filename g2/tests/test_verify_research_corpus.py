# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools/verify_research_corpus.py"
spec = importlib.util.spec_from_file_location("verify_research_corpus", TOOL)
vrc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vrc)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ResearchCorpusTest(unittest.TestCase):
    def make_tree(self, root: Path) -> None:
        run = root / "corpus/run"
        run.mkdir(parents=True)
        (run / "a.txt").write_bytes(b"alpha")
        (run / "SHA256SUMS").write_text(f"{digest(b'alpha')}  a.txt\n")
        (root / "corpus/SHA256SUMS.lane-bundle").write_text(
            f"{digest(b'alpha')}  run/a.txt\n{digest(b'gone')}  pruned/b.txt\n"
        )

    def test_repository_corpus_verifies(self) -> None:
        self.assertEqual(vrc.main([]), 0)

    def test_write_then_verify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            self.assertEqual(vrc.main(["--write-manifest"], root=root), 0)
            self.assertEqual(vrc.main([], root=root), 0)

    def test_tampered_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            vrc.main(["--write-manifest"], root=root)
            (root / "corpus/run/a.txt").write_bytes(b"changed")
            self.assertEqual(vrc.main([], root=root), 1)

    def test_unlisted_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            vrc.main(["--write-manifest"], root=root)
            (root / "corpus/extra.txt").write_bytes(b"x")
            self.assertEqual(vrc.main([], root=root), 1)

    def test_missing_delivery_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            (root / "corpus/run/a.txt").unlink()
            self.assertEqual(vrc.main(["--write-manifest"], root=root), 1)


if __name__ == "__main__":
    unittest.main()
