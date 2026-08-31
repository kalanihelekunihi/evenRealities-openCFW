#!/usr/bin/env python3
"""Verify the software-only G2 FreeType 2.9.1 autofit source admission.

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
AUTOFIT = G2 / "third_party/freetype/src/autofit"
TRANSLATION_UNIT = AUTOFIT / "autofit.c"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_autofit_function_map.py"
COMPONENT = G2 / "components/shared/freetype_autofit"
ADMISSION = COMPONENT / "source_admission.json"
README = COMPONENT / "README.md"
MANIFEST = G2 / "tools/manifests/g2-freetype-autofit-source-admission.json"

PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
LICENSE_PIN = (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1")
TRANSLATION_UNIT_PIN = (1_638, "f557319a03af15795632488ffc84575e98c2f3c6a4ff44c6bcda125cdc7890d1")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
FUNCTION_MAP_SHA256 = "30eec5b242a28dbd664acc91022479edc70836b264b0bcfb97f72999fca18dd4"
INVENTORY_SHA256 = "12275283b95378cb5d8695e420b4a39776915ea84d0fd6591deb11653bd0c205"
INVENTORY_KEYS = ("local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1")
INCLUDE_ORDER = (
    "afangles.c", "afblue.c", "afcjk.c", "afdummy.c", "afglobal.c",
    "afhints.c", "afindic.c", "aflatin.c", "aflatin2.c", "afloader.c",
    "afmodule.c", "afpic.c", "afranges.c", "afshaper.c", "afwarp.c",
)


class AdmissionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"input pin drift: {path}")
    return data


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None, f"analyzer unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze() -> dict[str, Any]:
    provenance = json.loads(_pinned(PROVENANCE, PROVENANCE_PIN))
    _pinned(LICENSE, LICENSE_PIN)
    translation_data = _pinned(TRANSLATION_UNIT, TRANSLATION_UNIT_PIN)
    upstream = provenance["upstream"]
    _require(upstream["declared_library_version"] == "2.9.1", "version drift")
    _require(upstream["selected_tag"] == "VER-2-9-1", "tag drift")
    _require(upstream["peeled_commit"] == UPSTREAM_COMMIT, "commit drift")

    inventory = [
        {key: row[key] for key in INVENTORY_KEYS}
        for row in provenance["files"]
        if row["local_path"].startswith("src/autofit/")
        and Path(row["local_path"]).suffix in {".c", ".h"}
    ]
    inventory.sort(key=lambda row: row["local_path"])
    _require(_canonical(inventory) == INVENTORY_SHA256, "autofit inventory drift")
    _require((len(inventory), sum(row["size"] for row in inventory)) == (37, 650_482),
             "autofit inventory accounting drift")
    for row in inventory:
        data = (PROVENANCE.parent / row["local_path"]).read_bytes()
        _require((len(data), _sha(data)) == (row["size"], row["sha256"]),
                 f"autofit source drift: {row['local_path']}")

    translation = translation_data.decode("utf-8")
    positions = [translation.find(f'#include "{name}"') for name in INCLUDE_ORDER]
    _require(-1 not in positions and positions == sorted(positions), "include order drift")
    _require("#define FT_MAKE_OPTION_SINGLE_OBJECT" in translation,
             "autofit single-object mode drift")

    function_map = _load(MAP_ANALYZER, "open_cfw_autofit_map_dependency").run_audit()
    _require(function_map["mapping_sha256"] == FUNCTION_MAP_SHA256, "function map drift")
    _require(function_map["confidence"]["high"] == {"functions": 29, "bytes": 3_270},
             "high-confidence accounting drift")
    _require(function_map["confidence"]["medium"] == {"functions": 58, "bytes": 20_342},
             "medium-confidence accounting drift")
    _require(function_map["confidence"]["mapped_total"] == {"functions": 87, "bytes": 23_612},
             "callable accounting drift")
    _require(function_map["scope"]["residual_physical"] == {
        "intervals": 5, "bytes": 92,
        "category_bytes": {"literal-constant-pool": 92},
        "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
    }, "physical accounting drift")

    _require(ADMISSION.is_file() and README.is_file(), "autofit component files missing")
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    _require(admission["upstream"]["commit"] == UPSTREAM_COMMIT, "component commit drift")
    _require(admission["mapped_evidence"]["mapping_sha256"] == FUNCTION_MAP_SHA256,
             "component map pin drift")
    _require(admission["source_inventory"] == {
        "autofit_files": 37, "autofit_source_bytes": 650_482,
        "inventory_sha256": INVENTORY_SHA256,
    }, "component inventory drift")
    _require(admission["build"]["production_overlay"] is False, "routing status drift")
    _require(admission["build"]["authenticated_target_placement"] is False,
             "placement status drift")
    _require(admission["hardware_validation"]["performed"] is False, "hardware status drift")

    return {
        "schema_version": 1,
        "status": "g2-freetype-autofit-community-source-admission",
        "upstream": {"version": "2.9.1", "tag": "VER-2-9-1",
                     "commit": UPSTREAM_COMMIT, "license": "FTL"},
        "mapped_callable_closure": {
            "functions": 87, "bytes": 23_612,
            "high": {"functions": 29, "bytes": 3_270},
            "medium": {"functions": 58, "bytes": 20_342},
            "unresolved_callable_bytes": 0,
            "mapping_sha256": FUNCTION_MAP_SHA256,
            "compiler_byte_identity_claimed": False,
        },
        "autofit_source_inventory": {
            "files": 37, "bytes": 650_482, "inventory_sha256": INVENTORY_SHA256,
        },
        "translation_unit": {
            "path": "third_party/freetype/src/autofit/autofit.c",
            "bytes": TRANSLATION_UNIT_PIN[0], "sha256": TRANSLATION_UNIT_PIN[1],
            "single_object_includes": list(INCLUDE_ORDER),
            "target": "arm-none-eabi/cortex-m55/thumb/hard-float",
            "warnings_as_errors": True,
            "compatibility_warning_exception": "-Wno-cast-function-type-mismatch",
        },
        "production": {
            "community_source": True, "stock_image_overlay_routed": False,
            "authenticated_target_placement": False,
            "software_gate": "tests.test_freetype_autofit_source_admission",
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
            "stock physical complement is entirely pinned literal pools": True,
            "hardware_operations": False,
        },
        "inputs": {
            "third_party/freetype/PROVENANCE.json": {"bytes": PROVENANCE_PIN[0], "sha256": PROVENANCE_PIN[1]},
            "third_party/freetype/LICENSE": {"bytes": LICENSE_PIN[0], "sha256": LICENSE_PIN[1]},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    text = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True)
    if args.write_manifest:
        MANIFEST.write_text(text + "\n", encoding="utf-8")
    if args.check_manifest:
        _require(MANIFEST.is_file() and json.loads(MANIFEST.read_text()) == report,
                 "autofit source-admission manifest drift")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
