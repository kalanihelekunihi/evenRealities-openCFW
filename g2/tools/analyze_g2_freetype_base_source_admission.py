#!/usr/bin/env python3
"""Seal the G2 FreeType 2.9.1 base-module source admission.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
SNAPSHOT = G2 / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
BASE_ANALYZER = (
    G2 / "research/candidates/freetype/analyze_base_cluster_candidate.py"
)
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_base_function_map.py"
MAP_MANIFEST = G2 / "tools/manifests/g2-freetype-base-function-map.json"
CONFIG_AUDIT = G2 / "tools/freetype_g2_config_audit.py"
COMPONENT = G2 / "components/shared/freetype_base"
ADMISSION = COMPONENT / "source_admission.json"
MANIFEST = G2 / "tools/manifests/g2-freetype-base-source-admission.json"
OVERLAY = G2 / "components/apollo_main/core_overlay/overlay.json"
BUILDER = G2 / "components/apollo_main/core_overlay/build_component.py"

EXPECTED_UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
EXPECTED_BASE_ANALYZER_SHA256 = (
    "2ef89ebbc425bb2293b0eaa75e93f5ce6923d222fbd40dfa4637382df84d2003"
)
EXPECTED_MAP_ANALYZER_SHA256 = (
    "9b0b51bd6527cfa1b984d4633c2eca4de4df7c4c367bf6da765d5021eb98a083"
)
EXPECTED_FUNCTION_MAP_SHA256 = (
    "c08117e7b02c8340e293f532f0d21473113aea17c7d6191b39422c1f01c990e3"
)
EXPECTED_CONFIG_AUDIT_SHA256 = (
    "49bfb2fe29472fe101c709a740d3cec847fcec66f94f1d26ef1367f5659f6278"
)
EXPECTED_PROVENANCE_SHA256 = (
    "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"
)
EXPECTED_INVENTORY_SHA256 = (
    "2bd46b9cb6cf8a6c6d21966aabca23e03c046be908db901a0395b0b2e390b473"
)

BUILD_TRANSLATION_UNITS = (
    "src/base/ftbase.c",
    "src/base/ftinit.c",
    "src/base/ftbitmap.c",
)
EXPECTED_COMPONENT_FILES = (
    "README.md",
    "runtime_freetype_base.c",
    "runtime_freetype_base.h",
    "runtime_freetype_base_face.c",
    "runtime_freetype_base_face.h",
    "source_admission.json",
)
RUNTIME_APIS = (
    "open_cfw_freetype_base_init",
    "open_cfw_freetype_base_done",
    "open_cfw_freetype_base_library",
    "open_cfw_freetype_base_last_error",
    "open_cfw_freetype_base_open_memory",
    "open_cfw_freetype_base_reference_face",
    "open_cfw_freetype_base_release_face",
    "open_cfw_freetype_base_load_and_render",
)
class AdmissionError(RuntimeError):
    """Raised when authenticated evidence or the maintained surface drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load analyzer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source_inventory() -> list[dict[str, Any]]:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["upstream"]["peeled_commit"] == EXPECTED_UPSTREAM_COMMIT,
            "FreeType provenance commit drift")
    by_path = {record["local_path"]: record for record in provenance["files"]}

    ftbase = (SNAPSHOT / "src/base/ftbase.c").read_text(encoding="utf-8")
    included = {
        f"src/base/{name}"
        for name in re.findall(r'^#include "([^"]+\.c)"$', ftbase, re.M)
    }
    selected = sorted(included | set(BUILD_TRANSLATION_UNITS))
    require(len(included) == 18 and len(selected) == 21,
            "selected base implementation inventory changed")

    result: list[dict[str, Any]] = []
    for local_path in selected:
        require(local_path in by_path, f"unproven base source: {local_path}")
        upstream = by_path[local_path]
        path = SNAPSHOT / local_path
        require(path.is_file(), f"base source missing: {local_path}")
        require(upstream["git_mode"] == "100644",
                f"base source mode changed: {local_path}")
        require((path.stat().st_size, sha256(path)) ==
                (upstream["size"], upstream["sha256"]),
                f"base source identity changed: {local_path}")
        result.append({
            "local_path": local_path,
            "upstream_path": upstream["upstream_path"],
            "git_mode": upstream["git_mode"],
            "git_blob_sha1": upstream["git_blob_sha1"],
            "size": upstream["size"],
            "sha256": upstream["sha256"],
            "role": (
                "build-translation-unit"
                if local_path in BUILD_TRANSLATION_UNITS
                else "ftbase-amalgamation-input"
            ),
        })
    digest = canonical_sha256(result)
    require(digest == EXPECTED_INVENTORY_SHA256,
            f"base source inventory digest changed: {digest}")
    return result


def analyze() -> dict[str, Any]:
    require(sha256(BASE_ANALYZER) == EXPECTED_BASE_ANALYZER_SHA256,
            "base-cluster analyzer identity drift")
    require(sha256(MAP_ANALYZER) == EXPECTED_MAP_ANALYZER_SHA256,
            "base complete-map analyzer identity drift")
    require(sha256(CONFIG_AUDIT) == EXPECTED_CONFIG_AUDIT_SHA256,
            "FreeType configuration audit identity drift")
    require(sha256(PROVENANCE) == EXPECTED_PROVENANCE_SHA256,
            "FreeType provenance identity drift")

    base_analyzer = load_module(BASE_ANALYZER, "g2_freetype_base_cluster")
    base_report = base_analyzer.analyze()
    require(base_report["admitted_cluster"] == {
        "functions": 83, "bytes": 7_874
    }, "base cluster accounting drift")
    require(base_report["remaining_cluster"] == {
        "functions": 0, "bytes": 0, "rows": []
    }, "base cluster is no longer closed")
    fallback = base_report["fallback_policy"]
    require((fallback["mechanics_functions"], fallback["mechanics_bytes"]) ==
            (7, 1_862), "base fallback mechanics accounting drift")

    map_analyzer = load_module(MAP_ANALYZER, "g2_freetype_base_complete_map")
    map_report = map_analyzer.run_audit()
    require(map_report["mapping_sha256"] == EXPECTED_FUNCTION_MAP_SHA256,
            "base complete function map drift")
    require(map_report["confidence"]["mapped_total"] == {
        "functions": 182, "bytes": 20_442
    }, "base complete callable accounting drift")
    require(map_report["confidence"]["unresolved_code"] == {
        "functions": 0, "bytes": 0, "source_identities_complete": True
    }, "base callable opacity reopened")
    require(map_report["scope"]["residual_physical"] == {
        "intervals": 15,
        "bytes": 234,
        "category_bytes": {
            "alignment-padding": 4,
            "literal-pointer-data-pool": 230,
        },
        "unclassified_bytes": 0,
        "unresolved_callable_bytes": 0,
    }, "base physical residue accounting drift")
    require(MAP_MANIFEST.is_file() and
            json.loads(MAP_MANIFEST.read_text(encoding="utf-8")) == map_report,
            "checked-in base function-map manifest drift")

    config_audit = load_module(CONFIG_AUDIT, "g2_freetype_config_audit")
    config_report = config_audit.authenticate(
        config_audit.Image(config_audit.DEFAULT_IMAGE.resolve())
    )
    require(len(config_report["configuration"]["built_in_modules"]) == 10,
        "authenticated default module count changed")
    require(config_report["image"]["sha256"] ==
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
            "official Apollo image identity drift")

    inventory = source_inventory()
    component_files = sorted(
        path.name for path in COMPONENT.iterdir() if path.is_file()
    )
    require(component_files == list(EXPECTED_COMPONENT_FILES),
            "FreeType base component file census changed")
    source_text = "\n".join(
        (COMPONENT / name).read_text(encoding="utf-8")
        for name in (
            "runtime_freetype_base.c", "runtime_freetype_base.h",
            "runtime_freetype_base_face.c", "runtime_freetype_base_face.h",
        )
    )
    for api in RUNTIME_APIS:
        require(source_text.count(api) >= 2,
                f"maintained FreeType base API missing: {api}")
    for token in (
        "FT_New_Library", "FT_Add_Default_Modules", "FT_Done_Library",
        "FT_OPEN_DRIVER", "OPEN_CFW_FREETYPE_G2_MODULE_COUNT = 10",
    ):
        require(token in source_text, f"base policy token missing: {token}")

    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    require(admission["license"] == "FTL", "component license drift")
    require(admission["upstream"]["commit"] == EXPECTED_UPSTREAM_COMMIT,
            "component upstream commit drift")
    require(admission["retained_evidence"] == {
        "existing_candidate_functions": 90,
        "existing_candidate_bytes": 9_736,
        "complete_map_functions": 182,
        "complete_map_callable_bytes": 20_442,
        "complete_map_physical_bytes": 20_676,
        "physical_residue_bytes": 234,
        "unresolved_callable_bytes": 0,
        "mapping_sha256": EXPECTED_FUNCTION_MAP_SHA256,
    }, "component retained accounting drift")
    build = admission["build"]
    require(build["production_overlay"] is False,
            "component unexpectedly production-routed")
    require(build["authenticated_stock_teardown_entry_recovered"] is False,
            "stock teardown evidence changed")
    require(build["authenticated_target_placement"] is False,
            "target placement evidence changed")
    require(build["target_compile"] == {
        "translation_units": list(BUILD_TRANSLATION_UNITS),
        "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
        "warnings_as_errors": True,
        "short_enums": True,
    }, "base target-compile contract drift")
    require(admission["hardware_validation"]["performed"] is False,
            "hardware claim changed")

    forbidden = (
        "components/shared/freetype_base",
        "runtime_freetype_base.c",
        "runtime_freetype_base_face.c",
        *RUNTIME_APIS,
    )
    routed_text = OVERLAY.read_text(encoding="utf-8") + "\n" + \
        BUILDER.read_text(encoding="utf-8")
    require(not any(token in routed_text for token in forbidden),
            "FreeType base component acquired an unauthenticated route")

    return {
        "schema_version": 1,
        "status": "g2-freetype-base-community-source-admission",
        "upstream": {
            "version": "2.9.1",
            "tag": "VER-2-9-1",
            "commit": EXPECTED_UPSTREAM_COMMIT,
            "license": "FTL",
        },
        "retained_source_evidence": {
            "base_cluster": base_report,
            "mapped_callable_closure": map_report["confidence"],
            "physical_envelope": map_report["scope"],
            "candidate_distinction": map_report["candidate_distinction"],
            "boundary_corrections": map_report["boundary_corrections"],
            "mapping_sha256": EXPECTED_FUNCTION_MAP_SHA256,
            "accounting_note": (
                "the former 90-function candidate remains a historical "
                "subset of the complete 182-callable physical map"
            ),
        },
        "base_source_inventory": {
            "files": len(inventory),
            "bytes": sum(record["size"] for record in inventory),
            "inventory_sha256": EXPECTED_INVENTORY_SHA256,
            "records": inventory,
        },
        "runtime": {
            "component": "components/shared/freetype_base",
            "apis": list(RUNTIME_APIS),
            "allocator_ports_required": True,
            "exact_default_module_count": 10,
            "face_policies": ["upstream-autodetect", "truetype-only", "cff-only"],
        },
        "translation_units": {
            "paths": list(BUILD_TRANSLATION_UNITS),
            "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
            "warnings_as_errors": True,
            "short_enums": True,
        },
        "production": {
            "community_source": True,
            "authenticated_stock_initializer_sequence_recovered": True,
            "authenticated_stock_teardown_entry_recovered": False,
            "authenticated_target_placement": False,
            "stock_image_overlay_routed": False,
            "software_gate": "tests.test_runtime_freetype_base_admission",
            "remaining_release_gates": [
                "exact stock teardown ownership or reviewed maintained teardown",
                "pinned IAR-compatible code generation, relocation, and placement",
                "authenticated external font payload and face-path configuration",
                "task stack and worst-case execution-time qualification",
                "authorized hardware rendering validation",
            ],
        },
        "evidence_bounds": {
            "source_admission_is_not_compiler_byte_identity": True,
            "complete_physical_map_is_not_production_routing": True,
            "hardware_operations": False,
        },
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (
                BASE_ANALYZER, MAP_ANALYZER, MAP_MANIFEST,
                CONFIG_AUDIT, PROVENANCE
            )
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
        if args.write_manifest:
            MANIFEST.write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if args.check_manifest:
            require(MANIFEST.is_file(), f"manifest missing: {MANIFEST}")
            require(json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                    "checked-in base source-admission manifest drift")
    except (AdmissionError, KeyError, OSError, ValueError) as error:
        print(f"G2 FreeType base source admission failed: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
