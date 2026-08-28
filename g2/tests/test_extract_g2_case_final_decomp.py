# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools import extract_g2_case_final_decomp as extractor


class CaseFinalDecompExtractionTests(unittest.TestCase):
    def test_frontier_is_exhaustively_extracted(self) -> None:
        rows, calls, harvest = extractor.extract()
        self.assertEqual(len(rows), 222)
        self.assertEqual(harvest["instruction_bytes"], 14886)
        self.assertEqual(harvest["project_source_candidates"], 222)
        self.assertEqual(harvest["software_recovery_frontier"], 0)
        self.assertGreater(len(calls), 0)
        self.assertEqual(len({row["address"] for row in rows}), 222)
        self.assertTrue(all(row["decompilation"] for row in rows))

    def test_committed_corpus_is_deterministic(self) -> None:
        rows, calls, harvest = extractor.extract()
        expected = extractor.render(rows, calls, harvest)
        for name, content in expected.items():
            self.assertEqual((extractor.OUTPUT / name).read_bytes(), content)
        sums = dict(
            line.split("  ", 1)[::-1]
            for line in (extractor.OUTPUT / "SHA256SUMS")
            .read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual(set(sums), set(expected))
        for name, digest in sums.items():
            self.assertEqual(digest, extractor.sha256(expected[name]))

    def test_jsonl_records_match_harvest(self) -> None:
        records = [json.loads(line) for line in
                   (extractor.OUTPUT / "functions.jsonl")
                   .read_text(encoding="utf-8").splitlines()]
        harvest = json.loads((extractor.OUTPUT / "HARVEST.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(len(records), harvest["functions"])
        self.assertEqual(sum(row["size"] for row in records),
                         harvest["instruction_bytes"])


if __name__ == "__main__":
    unittest.main()
