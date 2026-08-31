import copy
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_imu_icm45608.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_imu_icm45608", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2Icm45608Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze(build_report_path=None)
        cls.overlay = json.loads(MODULE.OVERLAY.read_text())
        with MODULE.FUNCTION_MAP.open(newline="") as handle:
            cls.function_starts = {
                int(row["entry"], 0)
                for row in csv.DictReader(handle, delimiter="\t")
            }

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 11,
            "restored_non_anchor_functions": 42,
            "linked_functions": 53,
            "body_bytes": 11674,
            "owned_gap_pool_bytes": 762,
            "physical_bytes": 12436,
            "direct_bl_entry_sites": 72,
            "external_direct_bl_entry_sites": 35,
            "direct_body_calls": 464,
            "stored_exact_entry_pointers": 3,
            "strict_interior_bl_ingress": 0,
            "internal_b_w_epilogue_branches": 10,
            "external_b_w_ingress": 0,
            "raw_entry_or_interior_windows": 21,
        })

    def test_sample_ring_and_raw_capture_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["sample_ring_address"], "0x200640a0")
        self.assertEqual(contract["sample_ring_header_bytes"], 12)
        self.assertEqual(contract["sample_slots"], 20)
        self.assertEqual(contract["sample_stride"], 0x70)
        self.assertEqual(contract["raw_collection_limit_ms"], 120000)
        self.assertEqual(contract["accel_config_min_interval"], 100)
        self.assertEqual(contract["accel_config_max_interval"], 4999)

    def test_stock_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("imu_icm45608.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 15)
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertEqual(lineage["restricted_notice_files"], 5)
        self.assertEqual(lineage["dense_payload_files"], 10)
        self.assertEqual(
            lineage["selected_payloads_in_official_donor"], [0, 0, 0, 0, 1]
        )

        production = self.report["production"]
        self.assertFalse(production["source_inventory_available"])
        self.assertFalse(production["production_routed"])
        self.assertTrue(production["retained_donor"])
        self.assertTrue(production["stock_functionality_preserved"])
        self.assertEqual(production["source_functions"], 0)
        self.assertEqual(production["tdk_primary_functions"], 0)
        self.assertEqual(production["guarded_redirects"], 0)
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertEqual(production["retained_stock_bytes"], 12436)
        self.assertEqual(production["redirect_overlap_bytes"], 0)
        self.assertEqual(production["external_callers"], 29)
        self.assertEqual(production["external_caller_functions"], 11)
        self.assertEqual(production["external_caller_targets"], 20)
        self.assertEqual(production["restricted_compiler_or_bundle_files"], 0)
        closure = production["public_closure"]
        self.assertEqual(closure["restricted_notice_files_selected"], 0)
        self.assertEqual(closure["dense_payload_files_selected"], 0)
        self.assertEqual(closure["retired_implementation_files_selected"], 0)
        self.assertIsNone(production["remaining_software_gap"])
        self.assertEqual(
            production["hardware_validation"], "blocked by unavailable physical evidence"
        )

    def test_rejects_any_patch_overlap_with_stock_object(self) -> None:
        forged = copy.deepcopy(self.overlay)
        forged["patch_sites"].append({
            "name": "forged_imu_redirect",
            "runtime_address": MODULE.PHYSICAL[0] + 2,
            "expected_size": 4,
        })
        with self.assertRaisesRegex(MODULE.AuditError, "overlaps"):
            MODULE.audit_overlay_boundary(forged, self.function_starts)

    def test_rejects_stale_or_retargeted_stock_caller(self) -> None:
        forged = copy.deepcopy(self.overlay)
        changed = False
        for leaf in forged["relocated_leaves"]:
            for relocation in leaf.get("relocations", []):
                target = relocation.get("target_address")
                if (isinstance(target, int)
                        and MODULE.PHYSICAL[0] <= (target & ~1) < MODULE.PHYSICAL[1]):
                    relocation["target_address"] = MODULE.PHYSICAL[0]
                    changed = True
                    break
            if changed:
                break
        self.assertTrue(changed)
        with self.assertRaisesRegex(MODULE.AuditError, "caller topology"):
            MODULE.audit_overlay_boundary(forged, self.function_starts)

    def test_rejects_reintroduced_restricted_compiler_routes(self) -> None:
        source_forgery = copy.deepcopy(self.overlay)
        source_forgery["sources"].append({
            "path": MODULE.RESTRICTED_NOTICE_PATHS[0],
        })
        with self.assertRaisesRegex(MODULE.AuditError, "source route"):
            MODULE.audit_overlay_boundary(source_forgery, self.function_starts)

        include_forgery = copy.deepcopy(self.overlay)
        include_forgery["toolchain"]["include_dirs"].append(
            "third_party/invensense-icm45608/src"
        )
        with self.assertRaisesRegex(MODULE.AuditError, "include route"):
            MODULE.audit_overlay_boundary(include_forgery, self.function_starts)

    def _synthetic_build_report(
        self, directory: Path, component: bytes, overlay: bytes
    ) -> Path:
        component_path = directory / "component.bin"
        overlay_path = directory / "overlay.bin"
        component_path.write_bytes(component)
        overlay_path.write_bytes(overlay)
        grouped: dict[tuple[str, str], list[dict]] = {}
        for row in MODULE._caller_rows(self.overlay):
            grouped.setdefault((row["source"], row["function"]), []).append({
                "offset": row["offset"],
                "target_address": row["target_address"],
            })
        leaves = [{
            "source": {"path": source},
            "extraction": {"function": function, "relocations": relocations},
        } for (source, function), relocations in grouped.items()]
        report = {
            "component": {
                "artifact": str(component_path),
                "size": len(component),
                "sha256": MODULE.sha256(component),
            },
            "overlay": {
                "artifact": str(overlay_path),
                "size": len(overlay),
                "sha256": MODULE.sha256(overlay),
                "patched_sites": [],
            },
            "sources": [],
            "relocated_leaves": leaves,
        }
        report_path = directory / "build-report.json"
        report_path.write_text(json.dumps(report))
        return report_path

    def test_built_boundary_accepts_exact_donor_and_rejects_mutation(self) -> None:
        donor = MODULE.IMAGE.read_bytes()
        callers = MODULE._caller_rows(self.overlay)
        with tempfile.TemporaryDirectory(prefix="g2-imu-stock-audit-") as raw:
            directory = Path(raw)
            report_path = self._synthetic_build_report(directory, donor, b"")
            report = MODULE.audit_built_boundary(report_path, donor, callers)
            self.assertEqual(report["component_stock_object_bytes"], 12436)
            self.assertEqual(report["built_external_callers"], 29)
            self.assertEqual(report["selected_payload_sequence_hits"], [0] * 5)

            mutated = bytearray(donor)
            mutated[MODULE.PHYSICAL[0] - MODULE.BASE] ^= 1
            report_path = self._synthetic_build_report(
                directory, bytes(mutated), b""
            )
            with self.assertRaisesRegex(MODULE.AuditError, "donor ICM45608"):
                MODULE.audit_built_boundary(report_path, donor, callers)

    def test_built_boundary_rejects_retired_payload_sequence(self) -> None:
        donor = MODULE.IMAGE.read_bytes()
        callers = MODULE._caller_rows(self.overlay)
        payload = MODULE._selected_payloads()[0]
        with tempfile.TemporaryDirectory(prefix="g2-imu-payload-audit-") as raw:
            report_path = self._synthetic_build_report(
                Path(raw), donor, b"prefix" + payload + b"suffix"
            )
            with self.assertRaisesRegex(MODULE.AuditError, "payload sequence"):
                MODULE.audit_built_boundary(report_path, donor, callers)


if __name__ == "__main__":
    unittest.main()
