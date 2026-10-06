import unittest
import json
from pathlib import Path
from g2.tools.trace_inventory import add_trace, summarize


class TraceInventoryTests(unittest.TestCase):
    def test_final_breakdown_includes_later_batches_and_disjoint_ranges(self):
        ledger = {}
        add_trace(ledger, "touch", {"0x1000": "0102"})
        add_trace(ledger, "apollo", {"0x1000": "aabb"})
        self.assertEqual(add_trace(ledger, "apollo", {"0x1001": "bbcc", "0x2000": "dd"}), 2)
        result = summarize(ledger)
        self.assertEqual(result["unique_original_trace_bytes"], {"touch": 2, "apollo": 4})
        self.assertEqual(result["unique_original_trace_total"], 6)
        self.assertEqual(sum(result["unique_original_trace_bytes"].values()), result["unique_original_trace_total"])

    def test_conflicting_same_payload_overlap_rejected(self):
        ledger = {}
        add_trace(ledger, "apollo", [{"pc": 4096, "bytes": "010203"}])
        with self.assertRaises(ValueError):
            add_trace(ledger, "apollo", {"0x1001": "ff"})

    def test_empty_inventory(self):
        self.assertEqual(summarize({}), {"unique_original_trace_bytes": {}, "unique_original_trace_total": 0})

    def test_saved_cumulative_inventory_has_final_payload_totals(self):
        root = Path(__file__).resolve().parents[2]
        paths = [root / 'g2/analysis' / name / 'cumulative-inventory.json' for name in
                 ('power-domain-descriptor-2026-10-06', 'cache-maintenance-2026-10-06',
                  'audio-cache-handoff-2026-10-06', 'audio-dma-rearm-2026-10-06')]
        paths = [path for path in paths if path.exists()]
        if not paths:
            self.skipTest('Saved bounded comparison inventory is not present')
        for path in paths:
            with self.subTest(inventory=str(path)):
                result = json.loads(path.read_text())
                expected = {}
                for evidence in result['evidence_inputs']:
                    payload = evidence['payload']
                    expected[payload] = expected.get(payload, 0) + evidence['new_unique_trace_bytes']
                self.assertEqual(result['unique_original_trace_bytes'], expected)
                self.assertEqual(result['unique_original_trace_total'], sum(expected.values()))
