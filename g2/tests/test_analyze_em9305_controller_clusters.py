#!/usr/bin/env python3
"""Guard the EM9305 controller cluster function recovery."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_em9305_controller_clusters.py"
MANIFEST = ROOT / "tools/manifests/em9305-controller-cluster-map.tsv"
RESIDUAL_MAP = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
PACKAGE_MAP_BASE = 0x0030_1FDC


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "analyze_em9305_controller_clusters", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class Em9305ControllerClusterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_cluster_layout_constants_are_consistent(self) -> None:
        tool = self.tool
        function_total = 0
        for cluster in tool.CLUSTERS:
            starts = [f[0] for f in cluster["functions"]]
            self.assertEqual(starts[0], cluster["start"])
            self.assertEqual(starts, sorted(starts))
            for index, (address, name, obj, asize, metrics, status, _extras) in enumerate(
                cluster["functions"]
            ):
                span_end = (
                    cluster["functions"][index + 1][0]
                    if index + 1 < len(cluster["functions"])
                    else cluster["end"]
                )
                body_end = span_end
                while body_end - 2 in cluster["interior_nops"]:
                    body_end -= 2
                self.assertGreater(body_end, address)
                function_total += body_end - address
                self.assertIn(status, {
                    tool.STATUS_OPCODE_EXACT, tool.STATUS_MODIFIED, tool.STATUS_DIVERGENT,
                })
                a_ins, s_ins, matched, longest = metrics
                self.assertLessEqual(matched, min(a_ins, s_ins))
                self.assertLessEqual(longest, matched)
            for nop in cluster["interior_nops"]:
                self.assertGreater(nop, cluster["start"])
                self.assertLess(nop, cluster["end"])
        self.assertEqual(function_total, tool.EXPECTED_IDENTIFIED_BYTES)
        self.assertEqual(
            sum(tool.EXPECTED_STATUS_BYTES.values()), tool.EXPECTED_IDENTIFIED_BYTES
        )
        self.assertEqual(sum(tool.EXPECTED_STATUS_COUNTS.values()), 10)

    def test_analyze_recomputes_pinned_recovery(self) -> None:
        report = self.tool.analyze()
        self.assertEqual(report["function_count"], 10)
        self.assertEqual(report["status_counts"], self.tool.EXPECTED_STATUS_COUNTS)
        self.assertEqual(report["status_bytes"], self.tool.EXPECTED_STATUS_BYTES)
        self.assertEqual(report["identified_function_bytes"], 4_920)
        by_name = {f["name"]: f for f in report["functions"]}
        self.assertEqual(by_name["lctrSlvConnExecute"]["sequence_ratio"], 1.0)
        self.assertEqual(by_name["lctrSlvConnResetHandler"]["sequence_ratio"], 1.0)
        self.assertEqual(by_name["lctrMstPerScanWithRspAbortOp"]["sequence_ratio"], 1.0)
        self.assertLess(by_name["lctrSlvConnTxCompletion"]["sequence_ratio"], 0.85)
        self.assertLess(
            by_name["lctrMstPerScanRxPerAdvPktPostHandler"]["sequence_ratio"], 0.85
        )
        self.assertGreaterEqual(by_name["lctrSlvConnEndOp"]["sequence_ratio"], 0.85)
        for f in report["functions"]:
            self.assertEqual(
                f["ownership"] if "ownership" in f else report["ownership_category"],
                "proprietary_modern_controller_source_unavailable",
            )

    def test_manifest_rows_match_blob_and_constants(self) -> None:
        image = IMAGE.resolve().read_bytes()
        if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
            raise unittest.SkipTest("official EM9305 blob not available")
        with MANIFEST.open(newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 10)
        status_counts = {}
        status_bytes = {}
        for row in rows:
            start = int(row["start"], 16)
            end = int(row["end"], 16)
            size = int(row["size"])
            self.assertEqual(end - start, size)
            body = image[start - PACKAGE_MAP_BASE:end - PACKAGE_MAP_BASE]
            self.assertEqual(hashlib.sha256(body).hexdigest(), row["sha256"])
            self.assertIn(row["status"], {
                self.tool.STATUS_OPCODE_EXACT,
                self.tool.STATUS_MODIFIED,
                self.tool.STATUS_DIVERGENT,
            })
            matched = int(row["matched"])
            a_ins = int(row["archive_insns"])
            self.assertLessEqual(matched, a_ins)
            if row["status"] == self.tool.STATUS_OPCODE_EXACT:
                self.assertEqual(matched, a_ins)
                self.assertEqual(row["sequence_ratio"], "1.000000")
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
            status_bytes[row["status"]] = status_bytes.get(row["status"], 0) + size
        self.assertEqual(status_counts, self.tool.EXPECTED_STATUS_COUNTS)
        self.assertEqual(status_bytes, self.tool.EXPECTED_STATUS_BYTES)

    def test_clusters_remain_proprietary_retention_in_residual_map(self) -> None:
        with RESIDUAL_MAP.open(newline="") as handle:
            rows = {
                row["start"]: row
                for row in csv.DictReader(handle, delimiter="\t")
            }
        for cluster in self.tool.CLUSTERS:
            row = rows[f"0x{cluster['start']:08X}"]
            self.assertEqual(int(row["end"], 16), cluster["end"])
            self.assertEqual(row["sha256"], cluster["segment_sha256"])
            self.assertEqual(
                row["ownership_category"],
                "proprietary_modern_controller_source_unavailable",
            )
            self.assertEqual(row["family_hint"], "packetcraft_modern_controller")
            self.assertEqual(row["confidence"], "high")

    def test_object_return_identity_is_pinned(self) -> None:
        objects = self.tool.DEFAULT_OBJECTS.resolve().read_bytes()
        self.assertEqual(
            hashlib.sha256(objects).hexdigest(), self.tool.OBJECTS_SHA256
        )
        report = self.tool.load_objects(self.tool.DEFAULT_OBJECTS)
        self.assertEqual(
            report["identity"]["archive_sha256"], self.tool.ARCHIVE_SHA256
        )
        self.assertEqual(
            report["identity"]["archive_git_blob"], self.tool.ARCHIVE_GIT_BLOB
        )
        needed = {
            "lctr_isr_conn_slave.c.obj",
            "lctr_main_conn_slave.c.obj",
            "lctr_sm_conn_slave.c.obj",
            "lctr_isr_adv_master_ae.c.obj",
            "lctr_main_adv_master_ae.c.obj",
            "lctr_isr_adv_central_pawr.c.obj",
            "lctr_main_adv_central_pawr.c.obj",
        }
        self.assertEqual(set(report["objects"]), needed)


if __name__ == "__main__":
    unittest.main()
