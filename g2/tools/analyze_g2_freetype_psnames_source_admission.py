#!/usr/bin/env python3
"""Verify the software-only G2 FreeType 2.9.1 PSNames source admission.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
PROVENANCE = G2 / "third_party/freetype/PROVENANCE.json"
LICENSE = G2 / "third_party/freetype/LICENSE"
PSNAMES = G2 / "third_party/freetype/src/psnames"
TRANSLATION_UNIT = PSNAMES / "psnames.c"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_psnames_function_map.py"
COMPONENT = G2 / "components/shared/freetype_psnames"
ADMISSION = COMPONENT / "source_admission.json"
README = COMPONENT / "README.md"
MANIFEST = G2 / "tools/manifests/g2-freetype-psnames-source-admission.json"

PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
LICENSE_PIN = (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1")
TRANSLATION_UNIT_PIN = (1_363, "27510af29ea9120772f17e97f8a01497c86ee0c3bb391021ef24b97651d01a4d")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
FUNCTION_MAP_SHA256 = "5d90ec82eb56c6ade9a6931c6b7c03cfdefe19242f3d163e8299b752794ac114"
INVENTORY_SHA256 = "61ba719e55bba95057647d697f5178794e0b579448fab3b7a2c2caa82177ac5a"

INVENTORY_KEYS = (
    "local_path", "upstream_path", "git_mode", "size", "sha256",
    "git_blob_sha1",
)
INCLUDE_ORDER = ("psmodule.c", "pspic.c")


class AdmissionError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"input pin drift: {path}")
    return data


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None,
             f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze() -> dict[str, Any]:
    provenance_data = _pinned(PROVENANCE, PROVENANCE_PIN)
    _pinned(LICENSE, LICENSE_PIN)
    translation_data = _pinned(TRANSLATION_UNIT, TRANSLATION_UNIT_PIN)
    provenance = json.loads(provenance_data)
    upstream = provenance["upstream"]
    _require(upstream["declared_library_version"] == "2.9.1", "version drift")
    _require(upstream["selected_tag"] == "VER-2-9-1", "tag drift")
    _require(upstream["peeled_commit"] == UPSTREAM_COMMIT, "commit drift")

    inventory = [
        {key: record[key] for key in INVENTORY_KEYS}
        for record in provenance["files"]
        if record["local_path"].startswith("src/psnames/")
        and Path(record["local_path"]).suffix in {".c", ".h"}
    ]
    inventory.sort(key=lambda row: row["local_path"])
    _require(_canonical_sha(inventory) == INVENTORY_SHA256,
             "PSNames inventory drift")
    _require((len(inventory), sum(row["size"] for row in inventory)) ==
             (7, 296_242), "PSNames inventory accounting drift")
    for row in inventory:
        data = (PROVENANCE.parent / row["local_path"]).read_bytes()
        _require((len(data), _sha(data)) == (row["size"], row["sha256"]),
                 f"PSNames source drift: {row['local_path']}")

    translation_text = translation_data.decode("utf-8")
    positions = [translation_text.find(f'#include "{name}"') for name in INCLUDE_ORDER]
    _require(-1 not in positions and positions == sorted(positions),
             "PSNames single-object include order drift")
    _require("#define FT_MAKE_OPTION_SINGLE_OBJECT" in translation_text,
             "PSNames single-object selection drift")

    function_map = _load(
        MAP_ANALYZER, "open_cfw_psnames_source_admission_map_dependency"
    ).run_audit()
    _require(function_map["mapping_sha256"] == FUNCTION_MAP_SHA256,
             "function map drift")
    _require(function_map["confidence"]["high"] ==
             {"functions": 8, "bytes": 844}, "high-confidence accounting drift")
    _require(function_map["confidence"]["medium"] ==
             {"functions": 3, "bytes": 288}, "medium-confidence accounting drift")
    _require(function_map["confidence"]["mapped_total"] ==
             {"functions": 11, "bytes": 1_132}, "mapped callable accounting drift")
    _require(function_map["confidence"]["unresolved_code"] == {
        "functions": 0, "bytes": 0, "source_identities_complete": True,
    }, "callable closure drift")
    _require(function_map["scope"]["residual_physical"] == {
        "intervals": 1, "bytes": 36,
        "category_bytes": {"literal-pointer-pool": 36},
        "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
    }, "physical complement drift")

    _require(ADMISSION.is_file() and README.is_file(),
             "PSNames component files missing")
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    _require(admission["license"] == "FTL", "component license drift")
    _require(admission["upstream"]["commit"] == UPSTREAM_COMMIT,
             "component commit drift")
    _require(admission["mapped_evidence"]["mapping_sha256"] == FUNCTION_MAP_SHA256,
             "component mapping pin drift")
    _require(admission["mapped_evidence"]["unresolved_callable_bytes"] == 0,
             "component callable status drift")
    _require(admission["source_inventory"] == {
        "psnames_files": 7, "psnames_source_bytes": 296_242,
        "inventory_sha256": INVENTORY_SHA256,
    }, "component inventory drift")
    _require(admission["build"]["production_overlay"] is False,
             "component production overlay status drift")
    _require(admission["build"]["authenticated_target_placement"] is False,
             "component placement status drift")
    _require(admission["hardware_validation"]["performed"] is False,
             "component hardware status drift")

    return {
        "schema_version": 1,
        "status": "g2-freetype-psnames-community-source-admission",
        "upstream": {
            "version": "2.9.1", "tag": "VER-2-9-1",
            "commit": UPSTREAM_COMMIT, "license": "FTL",
        },
        "mapped_callable_closure": {
            "functions": 11, "bytes": 1_132,
            "high": {"functions": 8, "bytes": 844},
            "medium": {"functions": 3, "bytes": 288},
            "unresolved_callable_bytes": 0,
            "mapping_sha256": FUNCTION_MAP_SHA256,
            "compiler_byte_identity_claimed": False,
        },
        "psnames_source_inventory": {
            "files": 7, "bytes": 296_242,
            "inventory_sha256": INVENTORY_SHA256,
        },
        "translation_unit": {
            "path": "third_party/freetype/src/psnames/psnames.c",
            "bytes": TRANSLATION_UNIT_PIN[0], "sha256": TRANSLATION_UNIT_PIN[1],
            "single_object_includes": list(INCLUDE_ORDER),
            "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
            "warnings_as_errors": True,
        },
        "production": {
            "community_source": True,
            "stock_image_overlay_routed": False,
            "authenticated_target_placement": False,
            "software_gate": "tests.test_freetype_psnames_source_admission",
            "existing_full_candidate_link_gate": "tests.test_runtime_target_provider_candidate",
            "remaining_release_gates": [
                "pinned IAR-compatible code generation, relocation, and placement",
                "authenticated font payload and face-path configuration",
                "task stack and worst-case execution-time qualification",
                "authorized hardware rendering validation",
            ],
        },
        "evidence_bounds": {
            "source and semantic identity are not compiler byte identity": True,
            "residual physical bytes are literal and pointer data": True,
            "hardware_operations": False,
        },
        "inputs": {
            "third_party/freetype/PROVENANCE.json": {
                "bytes": PROVENANCE_PIN[0], "sha256": PROVENANCE_PIN[1],
            },
            "third_party/freetype/LICENSE": {
                "bytes": LICENSE_PIN[0], "sha256": LICENSE_PIN[1],
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
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    if args.check_manifest:
        _require(MANIFEST.is_file(), f"manifest missing: {MANIFEST}")
        _require(json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                 "checked-in PSNames source-admission manifest drift")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
