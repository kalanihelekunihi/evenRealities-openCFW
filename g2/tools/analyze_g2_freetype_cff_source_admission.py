#!/usr/bin/env python3
"""Verify the G2 FreeType 2.9.1 CFF community-source admission.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
PROVENANCE = G2 / "third_party/freetype/PROVENANCE.json"
LICENSE = G2 / "third_party/freetype/LICENSE"
WAVE_BOUNDARIES = {
    11: G2 / "research/admission/apollo_opacity_wave11/source_boundaries.tsv",
    14: G2 / "research/admission/apollo_opacity_wave14/source_boundaries.tsv",
}
COMPONENT = G2 / "components/shared/freetype_cff"
ADMISSION = COMPONENT / "source_admission.json"
RUNTIME_SOURCE = COMPONENT / "runtime_freetype_cff.c"
RUNTIME_HEADER = COMPONENT / "runtime_freetype_cff.h"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-source-admission.json"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_function_map.py"
MAP_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-function-map.json"

EXPECTED_INPUTS = {
    PROVENANCE: (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"),
    LICENSE: (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1"),
    WAVE_BOUNDARIES[11]: (12_422, "d921788723eef345a04eb40b67724abba0e70aee5a268fa4dbaf87a57e2405b4"),
    WAVE_BOUNDARIES[14]: (1_695, "8cc4ae11e418c4ce8b7c19a962aa2ae404e3291034de740a0604a669899c13a6"),
}
EXPECTED_EVIDENCE_MAPPING_SHA256 = (
    "76b90a748d6fb8b160b32bf4a94bbefe52b63583de8a0eb2fd564ac671776240"
)
EXPECTED_CFF_INVENTORY_SHA256 = (
    "507807d06cb6381f671d0083c501bedf14abb23f3f16730e953842fdfd2889c1"
)
EXPECTED_UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
EXPECTED_MAP_ANALYZER_SHA256 = (
    "68f20cf54a36305d6c460d082c907d3d94efeff545238ff8b6f1189267322b70"
)
EXPECTED_FUNCTION_MAP_SHA256 = (
    "16761c056d968c5c4847c918d5a4d04a1a5a7fb883f125e833054f3762b7266e"
)

EVIDENCE_KEYS = (
    "entry",
    "end_exclusive",
    "envelope_bytes",
    "body_sha256",
    "symbol",
    "source_path",
    "provider_identity",
    "license_status",
    "disposition",
)
INVENTORY_KEYS = (
    "local_path",
    "upstream_path",
    "git_mode",
    "size",
    "sha256",
    "git_blob_sha1",
)
RUNTIME_APIS = (
    "open_cfw_freetype_cff_set_hinting_engine",
    "open_cfw_freetype_cff_get_hinting_engine",
    "open_cfw_freetype_cff_set_no_stem_darkening",
    "open_cfw_freetype_cff_get_no_stem_darkening",
    "open_cfw_freetype_cff_set_darkening_parameters",
    "open_cfw_freetype_cff_get_darkening_parameters",
)


class AdmissionError(RuntimeError):
    """Raised when authenticated source-admission evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if not line.startswith("#")]
    require(bool(lines), f"empty evidence table: {path}")
    return list(csv.DictReader(lines, delimiter="\t"))


def display_path(path: Path) -> str:
    try:
        return path.relative_to(G2).as_posix()
    except ValueError:
        return path.as_posix()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load analyzer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def analyze(
    *,
    provenance_path: Path = PROVENANCE,
    license_path: Path = LICENSE,
    wave_boundaries: dict[int, Path] | None = None,
    component: Path = COMPONENT,
) -> dict[str, Any]:
    boundaries = WAVE_BOUNDARIES if wave_boundaries is None else wave_boundaries
    expected_paths = {
        provenance_path: EXPECTED_INPUTS[PROVENANCE],
        license_path: EXPECTED_INPUTS[LICENSE],
        boundaries[11]: EXPECTED_INPUTS[WAVE_BOUNDARIES[11]],
        boundaries[14]: EXPECTED_INPUTS[WAVE_BOUNDARIES[14]],
    }
    inputs: dict[str, dict[str, Any]] = {}
    for path, expected in expected_paths.items():
        data = path.read_bytes()
        observed = (len(data), sha256(data))
        require(observed == expected, f"input pin drift: {path}: {observed}")
        inputs[display_path(path)] = {
            "bytes": observed[0],
            "sha256": observed[1],
        }

    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    upstream = provenance["upstream"]
    require(upstream["declared_library_version"] == "2.9.1", "version drift")
    require(upstream["selected_tag"] == "VER-2-9-1", "tag drift")
    require(upstream["peeled_commit"] == EXPECTED_UPSTREAM_COMMIT, "commit drift")
    require(
        "FreeType Project LICENSE" in license_path.read_text(encoding="utf-8"),
        "FreeType license marker drift",
    )

    recovered = provenance["g2_boundary"]["recovered_configuration"]
    require(recovered["cff"] == {
        "CFF_CONFIG_OPTION_OLD_ENGINE": False,
        "default_hinting_engine": "Adobe",
    }, "recovered CFF configuration drift")
    modules = provenance["g2_boundary"]["modules"]
    cff_modules = [record for record in modules if record["module_name"] == "cff"]
    require(len(cff_modules) == 1, "CFF module-class record drift")
    cff_module = cff_modules[0]
    require(
        (cff_module["order"], cff_module["class_symbol"],
         cff_module["class_address"]) ==
        (2, "cff_driver_class", "0x006DCB74"),
        "CFF module-class identity drift",
    )

    evidence: list[dict[str, Any]] = []
    for wave in (11, 14):
        for source_row in read_tsv(boundaries[wave]):
            if source_row["license_status"] != "FTL":
                continue
            row: dict[str, Any] = {"wave": wave}
            row.update({key: source_row[key] for key in EVIDENCE_KEYS})
            evidence.append(row)
    evidence.sort(key=lambda row: (row["wave"], int(row["entry"], 16)))
    require(len({row["entry"] for row in evidence}) == len(evidence),
            "duplicate retained-function entry")
    require(canonical_sha256(evidence) == EXPECTED_EVIDENCE_MAPPING_SHA256,
            "retained-function evidence mapping drift")

    source_records = {
        record["local_path"]: record for record in provenance["files"]
    }
    for row in evidence:
        require(row["provider_identity"] == "FreeType-2.9.1-VER-2-9-1",
                f"provider drift: {row['entry']}")
        require(row["disposition"] == "source-attributed-research-only",
                f"disposition drift: {row['entry']}")
        local_path = row["source_path"].removeprefix(
            "g2/third_party/freetype/"
        )
        require(local_path in source_records,
                f"source is absent from authenticated inventory: {local_path}")
        source = provenance_path.parent / local_path
        data = source.read_bytes()
        source_record = source_records[local_path]
        require(
            (len(data), sha256(data)) ==
            (source_record["size"], source_record["sha256"]),
            f"authenticated source drift: {local_path}",
        )
        require(row["symbol"] in data.decode("utf-8", errors="ignore"),
                f"source symbol missing: {row['symbol']}")

    cff_inventory = [
        {key: record[key] for key in INVENTORY_KEYS}
        for record in provenance["files"]
        if record["local_path"].startswith("src/cff/")
        and Path(record["local_path"]).suffix in {".c", ".h"}
    ]
    cff_inventory.sort(key=lambda record: record["local_path"])
    require(canonical_sha256(cff_inventory) == EXPECTED_CFF_INVENTORY_SHA256,
            "CFF source inventory drift")
    for record in cff_inventory:
        source = provenance_path.parent / record["local_path"]
        data = source.read_bytes()
        require((len(data), sha256(data)) ==
                (record["size"], record["sha256"]),
                f"CFF source drift: {record['local_path']}")

    runtime_source = component / RUNTIME_SOURCE.name
    runtime_header = component / RUNTIME_HEADER.name
    admission_path = component / ADMISSION.name
    for path in (runtime_source, runtime_header, admission_path):
        require(path.is_file(), f"community component file missing: {path}")
    runtime_text = runtime_source.read_text(encoding="utf-8")
    header_text = runtime_header.read_text(encoding="utf-8")
    for api in RUNTIME_APIS:
        require(api in runtime_text and api in header_text,
                f"runtime API missing: {api}")
    for token in (
        "FT_CFF_HINTING_ADOBE",
        "FT_Err_Invalid_Library_Handle",
        "FT_Err_Invalid_Argument",
        "darkening-parameters",
        "no-stem-darkening",
    ):
        require(token in runtime_text, f"runtime policy token missing: {token}")

    component_admission = json.loads(admission_path.read_text(encoding="utf-8"))
    require(component_admission["license"] == "FTL", "component license drift")
    require(component_admission["upstream"]["commit"] == EXPECTED_UPSTREAM_COMMIT,
            "component upstream commit drift")
    require(
        component_admission["build"]["software_verification_target"] ==
        "freetype-cff-source-closure",
        "component software verification target drift",
    )
    require(
        component_admission["build"][
            "authenticated_stock_policy_callsite_recovered"
        ] is False,
        "component stock policy callsite status drift",
    )
    require(
        component_admission["build"]["authenticated_target_placement"]
        is False,
        "component target placement status drift",
    )

    cff_evidence = [row for row in evidence if "/src/cff/" in row["source_path"]]
    base_evidence = [row for row in evidence if "/src/base/" in row["source_path"]]
    summary = {
        "functions": len(evidence),
        "bytes": sum(int(row["envelope_bytes"]) for row in evidence),
        "cff_functions": len(cff_evidence),
        "cff_bytes": sum(int(row["envelope_bytes"]) for row in cff_evidence),
        "base_support_functions": len(base_evidence),
        "base_support_bytes": sum(
            int(row["envelope_bytes"]) for row in base_evidence
        ),
    }
    require(summary == {
        "functions": 47,
        "bytes": 12_062,
        "cff_functions": 38,
        "cff_bytes": 11_326,
        "base_support_functions": 9,
        "base_support_bytes": 736,
    }, f"retained closure accounting drift: {summary}")
    for key, value in summary.items():
        require(component_admission["retained_evidence"][key] == value,
                f"component admission accounting drift: {key}")
    source_summary = {
        "files": len(cff_inventory),
        "bytes": sum(record["size"] for record in cff_inventory),
        "inventory_sha256": EXPECTED_CFF_INVENTORY_SHA256,
    }
    require(source_summary["files"] == 17 and source_summary["bytes"] == 269_028,
            f"CFF inventory accounting drift: {source_summary}")
    require(component_admission["source_inventory"] == {
        "cff_files": source_summary["files"],
        "cff_source_bytes": source_summary["bytes"],
    }, "component source inventory drift")

    require(sha256(MAP_ANALYZER.read_bytes()) == EXPECTED_MAP_ANALYZER_SHA256,
            "CFF complete-map analyzer identity drift")
    map_report = load_module(
        MAP_ANALYZER, "g2_freetype_cff_complete_map"
    ).run_audit()
    require(map_report["mapping_sha256"] == EXPECTED_FUNCTION_MAP_SHA256,
            "CFF complete function map drift")
    require(map_report["confidence"] == {
        "high": {"functions": 101, "bytes": 16_718},
        "medium": {"functions": 0, "bytes": 0},
        "mapped_total": {"functions": 101, "bytes": 16_718},
        "unresolved_code": {
            "functions": 0, "bytes": 0, "source_identities_complete": True,
        },
    }, "CFF complete callable accounting drift")
    require(map_report["scope"]["physical_bytes"] == 16_924 and
            map_report["scope"]["residual_physical"] == {
                "intervals": 13, "bytes": 206,
                "category_bytes": {
                    "alignment-padding": 2,
                    "literal-pointer-data-pool": 204,
                },
                "unclassified_bytes": 0,
                "unresolved_callable_bytes": 0,
            }, "CFF physical residue accounting drift")
    require(MAP_MANIFEST.is_file() and
            json.loads(MAP_MANIFEST.read_text(encoding="utf-8")) == map_report,
            "checked-in CFF function-map manifest drift")
    require(component_admission["complete_map"] == {
        "functions": 101,
        "callable_bytes": 16_718,
        "physical_bytes": 16_924,
        "physical_residue_bytes": 206,
        "unresolved_callable_bytes": 0,
        "mapping_sha256": EXPECTED_FUNCTION_MAP_SHA256,
    }, "component complete-map accounting drift")
    require(component_admission["build"]["target_compile"] == {
        "translation_units": ["src/cff/cff.c"],
        "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
        "warnings_as_errors": True,
        "short_enums": True,
    }, "CFF target compile contract drift")

    return {
        "schema_version": 1,
        "status": "g2-freetype-cff-community-source-admission",
        "upstream": {
            "version": "2.9.1",
            "tag": "VER-2-9-1",
            "commit": EXPECTED_UPSTREAM_COMMIT,
            "license": "FTL",
        },
        "recovered_policy": {
            "module_index": 2,
            "module_class": "cff_driver_class",
            "module_class_run_address": "0x006DCB74",
            "old_engine": False,
            "default_and_only_admitted_hinting_engine": "Adobe",
            "darkening_parameter_validation":
                "non-negative monotonic X; Y in [0,500]",
        },
        "retained_source_evidence": {
            **summary,
            "mapping_sha256": EXPECTED_EVIDENCE_MAPPING_SHA256,
            "records": evidence,
            "complete_function_map": map_report["confidence"],
            "physical_envelope": map_report["scope"],
            "candidate_distinction": map_report["candidate_distinction"],
            "complete_mapping_sha256": EXPECTED_FUNCTION_MAP_SHA256,
        },
        "cff_source_inventory": {
            **source_summary,
            "records": cff_inventory,
        },
        "runtime": {
            "source": runtime_source.relative_to(G2).as_posix(),
            "header": runtime_header.relative_to(G2).as_posix(),
            "apis": list(RUNTIME_APIS),
            "null_inputs_fail_closed": True,
        },
        "translation_units": {
            "paths": ["src/cff/cff.c"],
            "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
            "warnings_as_errors": True,
            "short_enums": True,
        },
        "production": {
            "community_source": True,
            "stock_image_overlay_routed": False,
            "authenticated_stock_policy_callsite_recovered": False,
            "authenticated_target_placement": False,
            "software_make_target": "freetype-cff-source-closure",
            "software_gates": [
                "tests.test_runtime_freetype_cff",
                "tests.test_runtime_freetype_base_candidate",
                "tests.test_runtime_target_provider_candidate",
            ],
            "remaining_release_gates": [
                "pinned IAR-compatible code generation, relocation, and placement",
                "authenticated external CFF font payload and face-path configuration",
                "task stack and worst-case execution-time qualification",
                "authorized hardware rendering validation",
            ],
        },
        "evidence_bounds": {
            "retained closures are source identities, not compiler byte identity": True,
            "the earlier 47-body retained admission is a subset of the complete CFF map": True,
            "complete physical map does not authenticate placement or routing": True,
            "hardware_operations": False,
        },
        "inputs": {
            **inputs,
            display_path(MAP_ANALYZER): {
                "bytes": MAP_ANALYZER.stat().st_size,
                "sha256": sha256(MAP_ANALYZER.read_bytes()),
            },
            display_path(MAP_MANIFEST): {
                "bytes": MAP_MANIFEST.stat().st_size,
                "sha256": sha256(MAP_MANIFEST.read_bytes()),
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_manifest:
        MANIFEST.write_text(rendered, encoding="utf-8")
    if args.check_manifest:
        require(MANIFEST.is_file(), f"manifest missing: {MANIFEST}")
        require(json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                "checked-in CFF source-admission manifest drift")
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
