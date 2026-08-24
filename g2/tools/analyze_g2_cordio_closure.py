#!/usr/bin/env python3
"""Reconcile retained Cordio paths with the repository's focused audits.

This is a coverage-of-evidence audit.  It does not promote source or infer that
the mixed G2 tree came from one pristine Packetcraft checkout.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_ANALYZER = ROOT / "tools/analyze_g2_cordio_source_map.py"
PROFILE_BOUNDARY_ANALYZER = ROOT / "tools/analyze_g2_ble_transport_profiles.py"
OTA_RING_ANALYZER = ROOT / "tools/analyze_g2_ble_ota_ring_profiles.py"
APP_FRAMEWORK_ANALYZER = ROOT / "tools/analyze_g2_cordio_app_framework.py"
EXPECTED_MODULE_AUDITS = 69
EXPECTED_FUNCTION_MAPS = 69
EXPECTED_PROVENANCE_MANIFESTS = 71

# Retained reusable stack/port paths and the focused analyzer that disposes of
# each one.  Two source files intentionally share one focused tranche.
FOCUSED_PATH_AUDITS = {
    "att_main.c": "att_main",
    "attc_disc.c": "attc_disc",
    "attc_main.c": "attc_main",
    "attc_proc.c": "attc_proc",
    "atts_ccc.c": "atts_ccc",
    "atts_csf.c": "atts_csf",
    "atts_ind.c": "atts_ind",
    "atts_main.c": "atts_main",
    "atts_proc.c": "atts_proc",
    "atts_sign.c": "atts_sign",
    "dm_adv_leg.c": "dm_adv_leg",
    "dm_conn_sm.c": "dm_conn_sm",
    "l2c_main.c": "l2c_main",
    "l2c_master.c": "l2c_master",
    "l2c_slave.c": "l2c_slave",
    "smp_main.c": "smp_main",
    "smp_sc_main.c": "smp_sc_main",
    "smpr_act.c": "smpr_act",
    "dm_conn.c": "dm_conn",
    "dm_dev.c": "dm_dev",
    "smp_act.c": "smp_act",
    "smp_db.c": "smp_db",
    "wsf_assert.c": "wsf_assert_trace",
    "wsf_trace.c": "wsf_assert_trace",
    "wsf_timer.c": "wsf_timer",
    "hci_evt.c": "hci_evt",
    "wsf_buf.c": "wsf_buf_msg",
}

PRODUCT_APPLICATION_PATHS = {
    "app_db.c", "app_master_leg.c", "app_slave_leg.c", "app_ui.c",
    "app_master.c", "app_server.c", "app_slave.c", "app_disc.c", "app_main.c",
}

ORIGIN_PINS = {
    "packetcraft_public_interval": {
        "repository": "https://github.com/packetcraft-inc/cordio.git",
        "releases": {
            "r20.05": "eeb34839755da1c19cc85b8795cc863483c16ef0",
            "r20.05a": "5e21ee596a80a3dc75ae5ef0938712a6042b2ac3",
            "r20.05b": "eb4282c7abe78dad8fb3984791b9c193fe904052",
            "r20.05c": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
        },
        "qualification": "bounded public compatibility interval; not one exact G2 checkout",
    },
    "packetcraft_r19_ancestry": {
        "repository": "https://github.com/packetcraft-inc/cordio.git",
        "release": "r19.02",
        "commit": "86372d84ef0386d8834ed036e613c8f2ded1ff16",
        "qualification": "module-specific ancestry/exact unchanged bodies only",
    },
    "ambiq_later_oracle": {
        "repository": "https://github.com/AmbiqAI/neuralSPOT.git",
        "release": "AmbiqSuite R4.4.1 import",
        "commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
        "qualification": "later source-family oracle; not the historical G2 producing commit",
    },
    "ambiq_freertos_port_oracle": {
        "artifact": "AmbiqSuite-R2.5.1.zip",
        "sha256": "87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133",
        "qualification": "exact proprietary implementation family for selected WSF ports; no public generating commit",
    },
}


class ClosureError(RuntimeError):
    pass


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("g2_cordio_source_map_for_closure", path)
    if spec is None or spec.loader is None:
        raise ClosureError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _basename(relative: str) -> str:
    return relative.replace("\\", "/").rsplit("/", 1)[-1]


def analyze_report(source_map: dict[str, Any], app_framework: dict[str, Any] | None = None) -> dict[str, Any]:
    profile_boundary = _load(PROFILE_BOUNDARY_ANALYZER).analyze()
    ota_ring = _load(OTA_RING_ANALYZER).analyze()
    app_module = _load(APP_FRAMEWORK_ANALYZER)
    snapshot = app_module._verify_snapshot()
    if app_framework is None:
        app_framework = {
            "lineage": {
                "selected_release": snapshot["selected_release"],
                "selected_commit": snapshot["selected_commit"],
                "historical_g2_generating_commit": None,
                "source_identification_closed": True,
                "exact_source_text_identity": False,
            },
            "stock_path_anchors": {
                "retained_paths": 9,
                "anchored_functions": 50,
                "anchored_body_bytes": 29110,
            },
            "legacy_master_slave_objects": {
                "aggregate": {"linked_functions": 14, "physical_bytes": 1406, "stored_callbacks": 2}
            },
            "production": {"production_routed": False},
        }
    if app_framework["lineage"] != {
        **app_framework["lineage"],
        "selected_release": "2.5.1",
        "selected_commit": "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
        "historical_g2_generating_commit": None,
        "source_identification_closed": True,
        "exact_source_text_identity": False,
    }:
        raise ClosureError("Cordio application-framework lineage changed")
    if app_framework["stock_path_anchors"]["retained_paths"] != 9:
        raise ClosureError("Cordio application-framework path census changed")
    if app_framework["stock_path_anchors"]["anchored_functions"] != 50 or app_framework["stock_path_anchors"]["anchored_body_bytes"] != 29110:
        raise ClosureError("Cordio application-framework anchor census changed")
    if app_framework["legacy_master_slave_objects"]["aggregate"]["linked_functions"] != 14:
        raise ClosureError("Cordio legacy application-object census changed")
    if app_framework["production"]["production_routed"]:
        raise ClosureError("Cordio application source oracle unexpectedly entered production")
    if profile_boundary["aggregate"] != {
        "modules": 4,
        "linked_functions": 25,
        "body_bytes": 2698,
        "physical_bytes": 3000,
        "production_routed": True,
    }:
        raise ClosureError("G2 BLE profile-boundary closure changed")
    if profile_boundary["upstream_sweep"]["third_party_source_dependency_identified"]:
        raise ClosureError("G2 BLE profile boundary acquired an unsupported dependency claim")
    if ota_ring["aggregate"]["ambiq_skeleton_derived_stock_functions"] != 4:
        raise ClosureError("G2 AMOTA-derived profile closure changed")
    paths = source_map["paths"]
    if len(paths) != 36:
        raise ClosureError(f"retained Cordio path census changed: {len(paths)}")

    reusable = [row for row in paths if row["ownership_boundary"] != "ambiq_or_product_application_layer"]
    application = [row for row in paths if row["ownership_boundary"] == "ambiq_or_product_application_layer"]
    reusable_names = {_basename(row["relative"]) for row in reusable}
    application_names = {_basename(row["relative"]) for row in application}
    if reusable_names != set(FOCUSED_PATH_AUDITS):
        raise ClosureError(
            f"retained reusable path set changed: missing={sorted(set(FOCUSED_PATH_AUDITS)-reusable_names)!r} "
            f"extra={sorted(reusable_names-set(FOCUSED_PATH_AUDITS))!r}"
        )
    if application_names != PRODUCT_APPLICATION_PATHS:
        raise ClosureError("Cordio application/product path set changed")

    audit_rows = []
    for row in reusable:
        name = _basename(row["relative"])
        stem = FOCUSED_PATH_AUDITS[name]
        analyzer = ROOT / f"tools/analyze_g2_cordio_{stem}.py"
        test = ROOT / f"tests/test_analyze_g2_cordio_{stem}.py"
        if not analyzer.is_file() or not test.is_file():
            raise ClosureError(f"focused audit/test missing for {name}: {stem}")
        audit_rows.append({
            "retained_path": row["relative"],
            "ownership_boundary": row["ownership_boundary"],
            "focused_analyzer": str(analyzer.relative_to(ROOT)),
            "focused_test": str(test.relative_to(ROOT)),
        })

    analyzer_names = {
        path.stem.removeprefix("analyze_g2_cordio_")
        for path in (ROOT / "tools").glob("analyze_g2_cordio_*.py")
        if path.stem not in {
            "analyze_g2_cordio_closure", "analyze_g2_cordio_source_map",
            "analyze_g2_cordio_version", "analyze_g2_cordio_ll_sea_census",
        }
    }
    tests = {
        path.stem.removeprefix("test_analyze_g2_cordio_")
        for path in (ROOT / "tests").glob("test_analyze_g2_cordio_*.py")
        if path.stem not in {
            "test_analyze_g2_cordio_closure", "test_analyze_g2_cordio_source_map",
            "test_analyze_g2_cordio_version", "test_analyze_g2_cordio_ll_sea_census",
        }
    }
    if len(analyzer_names) != EXPECTED_MODULE_AUDITS or tests != analyzer_names:
        raise ClosureError(
            f"focused analyzer/test inventory changed: analyzers={len(analyzer_names)} "
            f"tests={len(tests)} symmetric_difference={sorted(analyzer_names ^ tests)!r}"
        )

    manifests = ROOT / "tools/manifests"
    function_maps = list(manifests.glob("*cordio*function-map.tsv"))
    provenance = list(manifests.glob("*cordio*provenance.tsv"))
    if len(function_maps) != EXPECTED_FUNCTION_MAPS or len(provenance) != EXPECTED_PROVENANCE_MANIFESTS:
        raise ClosureError(
            f"Cordio manifest census changed: function_maps={len(function_maps)} provenance={len(provenance)}"
        )

    return {
        "schema_version": 1,
        "retained_path_census": {
            "total": len(paths),
            "reusable_stack_or_port": len(reusable),
            "focused_audit_present": len(audit_rows),
            "public_packetcraft_candidates": sum(row["ownership_boundary"] == "public_packetcraft_candidate" for row in reusable),
            "ambiq_ports": sum(row["ownership_boundary"] == "ambiq_port" for row in reusable),
            "application_or_product_boundary": len(application),
            "unclassified_reusable_paths": 0,
        },
        "module_evidence_census": {
            "focused_module_analyzers": len(analyzer_names),
            "matching_analyzer_tests": len(tests),
            "function_maps": len(function_maps),
            "provenance_manifests": len(provenance),
        },
        "origin_pins": ORIGIN_PINS,
        "historical_generating_commit": None,
        "historical_commit_qualification": "The G2 host is a mixed r20/R4-era Ambiq tree with module-local patches; one pristine checkout cannot explain it.",
        "third_party_residual": {
            "unclassified_retained_reusable_paths": 0,
            "unclassified_focused_module_audits": 0,
            "remaining": [
                "exact private mixed-tree checkout and original Ambiq port commits",
                "production admission/placement of clean-room or selected public sources",
                "target concurrency, controller, and hardware validation",
            ],
        },
        "application_boundary": {
            "paths": sorted(row["relative"] for row in application),
            "qualification": "AmbiqSuite application-framework ancestry is identified at commit de5c6ba3; exact G2 downstream source text remains product-local and unobservable",
        },
        "ambiq_application_framework_source_admission": {
            "focused_analyzer": "tools/analyze_g2_cordio_app_framework.py",
            "selected_release": "AmbiqSuite 2.5.1",
            "selected_commit": "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
            "packetcraft_ancestor_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "retained_paths": 9,
            "anchored_functions": 50,
            "anchored_body_bytes": 29110,
            "legacy_master_slave_linked_functions": 14,
            "source_identification_closed": True,
            "exact_source_text_identity": False,
            "historical_g2_generating_commit": None,
            "qualification": "selected public source is a semantic rebuild oracle; G2 adds MRAM, privacy, pairing, connection, diagnostics, and UI policy",
        },
        "copied_profile_source_admission": {
            "retained_path": r"platform\ble\profiles\gatt\profile_gatt.c",
            "focused_analyzer": "tools/analyze_g2_cordio_gatt_profile.py",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "source_blob": "bba9a3041ce14284a0bf527934eabd01c01694d8",
            "linked_functions": 6,
            "source_owned_functions": 6,
            "qualification": "copied Packetcraft gatt_main.c under a product path; GattDiscover carries an inserted logging expansion",
        },
        "ambiq_profile_source_admission": {
            "retained_path": r"platform\ble\profiles\ancc\profile_ancc.c",
            "focused_analyzer": "tools/analyze_g2_ambiqsuite_ancc_profile.py",
            "selected_release": "AmbiqSuite 2.5.1",
            "selected_commit": "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
            "source_blob": "4023359bf02612b07ed95f51561e7b8e7936810c",
            "linked_functions": 21,
            "source_derived_stock_functions": 12,
            "g2_local_stock_functions": 9,
            "qualification": "AmbiqSuite ANCC application profile copied under a product path; G2 adds message, synchronization, whitelist, callback, and logging policy",
        },
        "g2_profile_boundary_closure": {
            "retained_paths": sorted(
                item["retained_path"] for item in profile_boundary["modules"].values()
            ),
            "focused_analyzer": "tools/analyze_g2_ble_transport_profiles.py",
            "modules": 4,
            "linked_functions": 25,
            "body_bytes": 2698,
            "physical_bytes": 3000,
            "production_routed": True,
            "third_party_source_dependency_identified": False,
            "qualification": "EUS/ESS/EFS/NUS are G2-local Cordio provider adapters; neither AmbiqSuite profile source nor Nordic ble_nus source matches",
        },
        "amota_profile_lineage": {
            "retained_path": r"platform\ble\profiles\ota\profile_ota.c",
            "focused_analyzer": "tools/analyze_g2_ble_ota_ring_profiles.py",
            "selected_release": "AmbiqSuite 2.5.1",
            "selected_commit": "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
            "linked_functions": 7,
            "ambiq_skeleton_derived_stock_functions": 4,
            "g2_local_stock_functions": 3,
            "qualification": "G2 rewrite of the stable AMOTA application event/CCC/handler skeleton; product actions are not source-identical upstream code",
        },
        "ring_profile_boundary": {
            "retained_path": r"platform\ble\profiles\ring\profile_ring.c",
            "focused_analyzer": "tools/analyze_g2_ble_ota_ring_profiles.py",
            "linked_functions": 7,
            "g2_local_stock_functions": 7,
            "third_party_source_dependency_identified": False,
            "qualification": "G2-local 128-bit Ring service discovery, epoch-qualified CCC scheduling, RX dispatch, and send adapter",
        },
        "focused_retained_path_audits": sorted(audit_rows, key=lambda row: row["retained_path"]),
    }


def analyze(corpus: Path) -> dict[str, Any]:
    source_map = _load(SOURCE_MAP_ANALYZER).analyze(corpus)
    app_framework = _load(APP_FRAMEWORK_ANALYZER).analyze(corpus)
    return analyze_report(source_map, app_framework)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        census = report["retained_path_census"]
        modules = report["module_evidence_census"]
        print(
            "G2 Cordio aggregate closure: PASS "
            f"({census['focused_audit_present']}/{census['reusable_stack_or_port']} retained reusable paths; "
            f"{modules['focused_module_analyzers']} focused module audits)"
        )
        print("exact historical mixed-tree commit: unobservable")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
