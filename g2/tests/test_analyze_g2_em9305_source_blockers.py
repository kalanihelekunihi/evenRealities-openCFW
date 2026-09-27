import json
import unittest

from tools import analyze_g2_em9305_source_blockers as analyzer


class G2Em9305SourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_em9305_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["size"], 212984)
        self.assertEqual(self.report["release_blocking_bytes"], 210584)
        self.assertTrue(self.report["production_routed"])
        self.assertFalse(self.report["source_complete"])
        self.assertEqual(self.report["residual_scope_bytes"], 33658)
        self.assertEqual(self.report["residual_unclassified_bytes"], 0)
        self.assertEqual(
            self.report["residual_readiness_bytes"],
            {
                "concrete_source_available": 1240,
                "typed_unsupported_external_boundary": 8348,
                "unavailable_proprietary_controller_code": 24070,
            },
        )

    def test_final_readiness_receipts_are_authenticated(self) -> None:
        receipts = self.report["final_source_readiness_receipts"]
        self.assertEqual(receipts["manifest_count"], 2)
        self.assertEqual(
            receipts["ledger"]["sha256"],
            "cfda63c68a73d27235af204f01ee6c848db9495d0294d55faf70096b7ab08bf9",
        )
        self.assertEqual(
            receipts["summary"]["sha256"],
            "fcffc7ba76ec96e371db5a5f4635e02d3259118e3529bdbcca7ee1533bac3774",
        )

    def test_em9305_source_build_route_is_authenticated(self) -> None:
        route = self.report["source_build_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-core-source.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(
            route["provider_path"],
            "components/em9305/source_overlay/build/firmware_ble_em9305.bin",
        )
        self.assertEqual(route["provider_size"], 212984)
        self.assertEqual(
            route["provider_sha256"],
            "56694060c0d2761c2004581d0cec97cdb8642c1ff44675194d05d605bf8dd9c7",
        )
        self.assertEqual(route["package_toolchain_profile"], "apple-clang")
        self.assertTrue(route["production_routed"])
        self.assertEqual(route["hardware_operations"], [])
        self.assertEqual(route["undefined_symbols"], [])
        self.assertEqual(
            route["accounting"]["typed_retained_or_external_bytes"],
            210584,
        )
        self.assertEqual(route["accounting"]["production_source_bytes"], 1190)

    def test_residual_frontier_is_pinned(self) -> None:
        frontier = self.report["residual_frontier"]
        self.assertEqual(frontier["residual_ledger_spans"], 175)
        self.assertEqual(frontier["residual_ledger_bytes"], 33658)
        self.assertEqual(
            frontier["readiness"],
            {
                "concrete_source_available": {"bytes": 1240, "spans": 23},
                "typed_unsupported_external_boundary": {
                    "bytes": 8348,
                    "spans": 25,
                },
                "unavailable_proprietary_controller_code": {
                    "bytes": 24070,
                    "spans": 127,
                },
            },
        )
        self.assertEqual(
            frontier["decision_origins"]["slave_connection_fail_closed_boundary"],
            {"bytes": 3126, "spans": 1},
        )
        self.assertEqual(
            frontier["decision_origins"]["pawr_fail_closed_boundary"],
            {"bytes": 1804, "spans": 1},
        )
        self.assertEqual(
            frontier["decision_origins"]["master_connection_fail_closed_boundary"],
            {"bytes": 1564, "spans": 1},
        )
        self.assertEqual(
            frontier["decisions"]["packetcraft_modern_controller"],
            {"bytes": 21048, "spans": 104},
        )
        self.assertEqual(
            [
                (row["start"], row["size"], row["decision"])
                for row in frontier["largest_unresolved_spans"][:3]
            ],
            [
                (3315848, 3126, "six_entry_slave_connection_provider_boundary"),
                (3284016, 1804, "four_entry_pawr_provider_boundary"),
                (3268560, 1564, "three_entry_master_connection_boundary"),
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
