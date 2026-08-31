#!/usr/bin/env python3
"""Verify the software-only G2 FreeType 2.9.1 PSAux source admission.

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
PSAUX = G2 / "third_party/freetype/src/psaux"
TRANSLATION_UNIT = PSAUX / "psaux.c"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_psaux_function_map.py"
COMPONENT = G2 / "components/shared/freetype_psaux"
ADMISSION = COMPONENT / "source_admission.json"
README = COMPONENT / "README.md"
MANIFEST = G2 / "tools/manifests/g2-freetype-psaux-source-admission.json"

PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
LICENSE_PIN = (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1")
TRANSLATION_UNIT_PIN = (1_656, "f5c04077c995d5fe9692ab0bd310bbc8c295a03cbedd75928433a98db5a301fc")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
FUNCTION_MAP_SHA256 = "ba936457b31d9c8d94bbcabd0ad8e993103e1f423def30314c5ed81dbcf6cecb"
INVENTORY_SHA256 = "3e5cd97d8ebad001edc947962591689cb86780b8174a20e164da00d4a03ee9e1"
INVENTORY_KEYS = ("local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1")
INCLUDE_ORDER = ("afmparse.c", "psauxmod.c", "psconv.c", "psobjs.c", "t1cmap.c",
                 "t1decode.c", "cffdecode.c", "psarrst.c", "psblues.c", "pserror.c",
                 "psfont.c", "psft.c", "pshints.c", "psintrp.c", "psread.c", "psstack.c")


class AdmissionError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"input pin drift: {path}")
    return data


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("open_cfw_psaux_admission_map", path)
    if spec is None or spec.loader is None:
        raise AdmissionError(f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze() -> dict[str, Any]:
    provenance = json.loads(_pinned(PROVENANCE, PROVENANCE_PIN))
    _pinned(LICENSE, LICENSE_PIN)
    translation = _pinned(TRANSLATION_UNIT, TRANSLATION_UNIT_PIN).decode("utf-8")
    upstream = provenance["upstream"]
    _require((upstream["declared_library_version"], upstream["selected_tag"], upstream["peeled_commit"]) ==
             ("2.9.1", "VER-2-9-1", UPSTREAM_COMMIT), "upstream identity drift")

    inventory = [{key: row[key] for key in INVENTORY_KEYS} for row in provenance["files"]
                 if row["local_path"].startswith("src/psaux/")
                 and Path(row["local_path"]).suffix in {".c", ".h"}]
    inventory.sort(key=lambda row: row["local_path"])
    _require(_canonical(inventory) == INVENTORY_SHA256, "PSAux inventory drift")
    _require((len(inventory), sum(row["size"] for row in inventory)) == (37, 625_815),
             "PSAux inventory accounting drift")
    for row in inventory:
        data = (PROVENANCE.parent / row["local_path"]).read_bytes()
        _require((len(data), _sha(data)) == (row["size"], row["sha256"]),
                 f"PSAux source drift: {row['local_path']}")

    positions = [translation.find(f'#include "{name}"') for name in INCLUDE_ORDER]
    _require(-1 not in positions and positions == sorted(positions), "PSAux include order drift")
    _require("#define FT_MAKE_OPTION_SINGLE_OBJECT" in translation, "PSAux single-object drift")

    function_map = _load(MAP_ANALYZER).run_audit()
    _require(function_map["mapping_sha256"] == FUNCTION_MAP_SHA256, "function map drift")
    _require(function_map["confidence"]["high"] == {"functions": 65, "bytes": 7_020},
             "high-confidence accounting drift")
    _require(function_map["confidence"]["medium"] == {"functions": 134, "bytes": 22_730},
             "medium-confidence accounting drift")
    _require(function_map["confidence"]["mapped_total"] == {"functions": 199, "bytes": 29_750},
             "callable accounting drift")
    _require(function_map["confidence"]["unresolved_code"]["bytes"] == 0,
             "callable closure drift")
    _require(function_map["scope"]["residual_physical"]["unclassified_bytes"] == 0,
             "physical classification drift")

    _require(ADMISSION.is_file() and README.is_file(), "PSAux component files missing")
    admission = json.loads(ADMISSION.read_text())
    _require(admission["upstream"]["commit"] == UPSTREAM_COMMIT, "component commit drift")
    _require(admission["mapped_evidence"]["mapping_sha256"] == FUNCTION_MAP_SHA256,
             "component map pin drift")
    _require(admission["source_inventory"] == {
        "psaux_files": 37, "psaux_source_bytes": 625_815, "inventory_sha256": INVENTORY_SHA256,
    }, "component inventory drift")
    _require(not admission["build"]["production_overlay"] and
             not admission["build"]["authenticated_target_placement"], "component routing drift")
    _require(not admission["hardware_validation"]["performed"], "component hardware claim drift")

    return {
        "schema_version": 1,
        "status": "g2-freetype-psaux-community-source-admission",
        "upstream": {"version": "2.9.1", "tag": "VER-2-9-1", "commit": UPSTREAM_COMMIT,
                     "license": "FTL", "adobe_notice_and_patent_grant_retained": True},
        "mapped_callable_closure": {
            "functions": 199, "bytes": 29_750,
            "high": {"functions": 65, "bytes": 7_020},
            "medium": {"functions": 134, "bytes": 22_730},
            "foreign_callable": {"functions": 2, "bytes": 762},
            "residual_noncode_bytes": 144, "unresolved_callable_bytes": 0,
            "mapping_sha256": FUNCTION_MAP_SHA256, "compiler_byte_identity_claimed": False,
        },
        "psaux_source_inventory": {"files": 37, "bytes": 625_815,
                                   "inventory_sha256": INVENTORY_SHA256},
        "translation_unit": {
            "path": "third_party/freetype/src/psaux/psaux.c", "bytes": TRANSLATION_UNIT_PIN[0],
            "sha256": TRANSLATION_UNIT_PIN[1], "single_object_includes": list(INCLUDE_ORDER),
            "target": "arm-none-eabi/cortex-m55/thumb/hard-float", "warnings_as_errors": True,
        },
        "production": {
            "community_source": True, "stock_image_overlay_routed": False,
            "authenticated_target_placement": False,
            "software_gate": "tests.test_freetype_psaux_source_admission",
            "existing_full_candidate_link_gate": "tests.test_runtime_target_provider_candidate",
            "remaining_release_gates": [
                "pinned IAR-compatible code generation, relocation, and placement",
                "authenticated PostScript font payload and face-path configuration",
                "task stack and worst-case execution-time qualification",
                "authorized hardware rendering validation",
            ],
        },
        "evidence_bounds": {
            "source and semantic identity are not compiler byte identity": True,
            "interleaved Cordio callables remain foreign": True,
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
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.check_manifest:
        _require(MANIFEST.is_file(), f"manifest missing: {MANIFEST}")
        _require(json.loads(MANIFEST.read_text()) == report, "checked-in PSAux admission manifest drift")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
