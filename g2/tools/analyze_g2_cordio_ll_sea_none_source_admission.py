#!/usr/bin/env python3
"""Audit controlled source admission for the closed Apollo 0x5D none census.

SPDX-License-Identifier: MIT

This analyzer is deliberately read-only.  It admits attributable source and
provider records, not a binary overlay or an assertion of compiler byte identity.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
REPO = G2.parent
FREETYPE = G2 / "third_party/freetype"
SEGGER_DIR = G2 / "research/admission/cordio_ll_sea_none/segger_rtt_6_18a"
BATCH12 = G2 / "tools/analyze_g2_cordio_ll_sea_none_batch12_candidate.py"
FT_LICENSE = (6743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1")
FT_PROVENANCE = (102377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
SEGGER_MANIFEST = (26671, "3881eb71e5092daad261908bcffc59dbb111eac5ce27162cfd2ea0e54e3e9bb5")
SEGGER_SOURCE_SHA256 = "52f9a10baa6cea801134e7eb87848631fd03232540366c407c2a9183641c9088"
SEGGER_ARCHIVE_SHA256 = "5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061"
SEGGER_LOCAL_PINS = {
    "LICENSE.txt": (2699, "908cf7f35485bdf1df1ef7a92d4bbc6d8297c6b2d3f620b2ecc39a2a40788739"),
    "SEGGER_RTT.c": (52950, "5c4f86b4f054ac59ce4456fe069901877103cc9fd78365e2ddf715ec3b9d1789"),
    "SEGGER_RTT.h": (13286, "f1b212b3cb749a1b7934db7990457f0c2b32189615a6ea47d7e091e0c608f0dc"),
    "SEGGER_RTT_Conf.h": (19285, "c0caa356979fa4544e3d97aea9ab28a008b3bd0a8635a04e471a857aa05046c9"),
}

# basename: (snapshot-relative path, byte size, SHA-256)
MODULE_PINS = {
    "cffdecode.c": ("src/psaux/cffdecode.c", 71404, "315e935a933a775666da68062c6f61f1fd9beeb23d98da3b12ed4ba3d0b42d91"),
    "psconv.c": ("src/psaux/psconv.c", 12574, "1770ebf41ef066333aeef2f3d0a30b765d3f649c2ac1e85fac9dd98802058f5d"),
    "psft.c": ("src/psaux/psft.c", 26591, "20c152003634042eee20ffa17ab4a1280743bd6f9117725aee5534662a1a9e3f"),
    "pshalgo.c": ("src/pshinter/pshalgo.c", 59738, "cbede1f596434c2348711a1ed12c60448ed14759b52a48c31cf1898564d69842"),
    "pshglob.c": ("src/pshinter/pshglob.c", 23053, "0f22b4d604c977c377f0eb96c5b460fd74bf70c5a196aabc33ae1b94cdd99cbe"),
    "pshrec.c": ("src/pshinter/pshrec.c", 32058, "0a639419fb8051eca8836be0eb1c1c9b7d9910ed4907670dde26de166bb33378"),
    "psmodule.c": ("src/psnames/psmodule.c", 16846, "d21c06ed3dee78cd85f1008275cb888f66099b1e3650e8c8dfdcf0406e7f1368"),
    "psobjs.c": ("src/psaux/psobjs.c", 75816, "6054c46ea381596e3eec22f0c13f8aaff8a6390fa33bad619dadaae7c0cf578e"),
    "pstables.h": ("src/psnames/pstables.h", 268872, "67a4dee05b7bb71f46e53026fa3fefd23ca26604ba46741accae82bc33fa9627"),
    "sfdriver.c": ("src/sfnt/sfdriver.c", 34308, "79c368e8d3a933bb1353295046aa991d342ee272fb9b3654fb852ced396b10be"),
    "sfobjs.c": ("src/sfnt/sfobjs.c", 58595, "87999f1d3183a70e406e28d93f6b77e9a158f0e635cb3fb725af0655b7e6c402"),
    "t1cmap.c": ("src/psaux/t1cmap.c", 11693, "3543b52fe9bb45fd73d8cd5d4e7a9f60c0a71e08ce7f18602d32f314c4bf2d23"),
    "t1decode.c": ("src/psaux/t1decode.c", 63382, "e1d93cb47d218ccb536084932b65896a6ead9aadfdc1b648485e65524580fb74"),
    "ttbdf.c": ("src/sfnt/ttbdf.c", 7083, "ea44af46d27e96590681f72273273da12e146968d9c61711ca8fa73c6c99ed23"),
    "ttcmap.c": ("src/sfnt/ttcmap.c", 120864, "e321c3d6cac43fa450698f5a98456fd8e84d7da0b37ea75531ad79c3cecfe5fb"),
    "ttkern.c": ("src/sfnt/ttkern.c", 8081, "7df687ce36895754b3b3cec950409255bb1f00b26d0c2c8107743cef47112a26"),
    "ttload.c": ("src/sfnt/ttload.c", 52871, "fff297b78a470479cc41994f005a7ae5acba78ab50b1aa0fdfad7b1f7ec28ef7"),
    "ttmtx.c": ("src/sfnt/ttmtx.c", 12312, "0ccf75bfa5f2306be72650425bfae36a86f3fc92c80987cdc80d59deeabc589d"),
    "ttpost.c": ("src/sfnt/ttpost.c", 17199, "9ff630ae5a4da8558507f40ac8cce5ee132117f017568c1e23398a3cb4764bc1"),
}

BINARY_BLOCKERS = (
    "exact original compiler/version/options, ABI, FreeType macros, and LTO state are not recovered",
    "no reviewed function/literal/constant/veneer placement recipe covers all 198 bodies",
    "no complete relocation and cross-census callsite rewrite manifest exists",
    "flash, RAM, stack, and WCET budgets for the rebuilt provider graph are not reviewed",
    "exact product sdk_config values and target critical-section binding for SEGGER RTT are not recovered",
    "four adjacent non-census intervals lack complete authenticated callable records",
)


class AdmissionError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    if (len(data), _sha(data)) != pin:
        raise AdmissionError(f"pin drift: {path}")
    return data


def _load_batch12():
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch12_admission_dependency", BATCH12)
    if spec is None or spec.loader is None:
        raise AdmissionError("batch12 analyzer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    closed = _load_batch12().run_audit()
    census = closed["none_group"]
    if census["classified"] != {"functions": 198, "bytes": 33644}:
        raise AdmissionError("closed census accounting drift")
    if census["unclassified"] != {"functions": 0, "bytes": 0}:
        raise AdmissionError("closed census is no longer fully classified")

    license_data = _pinned(FREETYPE / "LICENSE", FT_LICENSE)
    provenance_data = _pinned(FREETYPE / "PROVENANCE.json", FT_PROVENANCE)
    provenance = json.loads(provenance_data)
    if provenance["upstream"]["selected_tag"] != "VER-2-9-1":
        raise AdmissionError("FreeType release pin drift")
    if provenance["upstream"]["peeled_commit"] != "86bc8a95056c97a810986434a3f268cbe67f2902":
        raise AdmissionError("FreeType commit pin drift")
    if b"FreeType Project LICENSE" not in license_data:
        raise AdmissionError("FreeType license text drift")

    module_records = []
    source_text = {}
    for module, (relative, size, digest) in sorted(MODULE_PINS.items()):
        data = _pinned(FREETYPE / relative, (size, digest))
        source_text[module] = data.decode("utf-8", errors="strict")
        module_records.append({"module": module, "path": relative, "bytes": size, "sha256": digest})
    psft = source_text["psft.c"].lower()
    if "adobe" not in psft or "patent" not in psft or "permission" not in psft:
        raise AdmissionError("Adobe psft.c notices/grant drift")

    manifest_data = _pinned(REPO / "third-party/fetched/manifest.json", SEGGER_MANIFEST)
    manifest = json.loads(manifest_data)
    segger = next((row for row in manifest["components"] if row.get("id") == "segger-rtt"), None)
    if segger is None:
        raise AdmissionError("SEGGER provider record missing")
    expected_segger = {
        "version": "6.18a",
        "container": "nordic-nrf5-sdk",
        "path": "external/segger_rtt",
        "license": "SEGGER RTT redistributable source license",
        "license_path": "external/segger_rtt/license/license.txt",
        "source_sha256": SEGGER_SOURCE_SHA256,
    }
    if any(segger.get(key) != value for key, value in expected_segger.items()):
        raise AdmissionError("SEGGER provider/version/license pin drift")
    segger_local = []
    for name, pin in sorted(SEGGER_LOCAL_PINS.items()):
        _pinned(SEGGER_DIR / name, pin)
        segger_local.append({"path": name, "bytes": pin[0], "sha256": pin[1]})
    segger_license = (SEGGER_DIR / "LICENSE.txt").read_text()
    segger_source = (SEGGER_DIR / "SEGGER_RTT.c").read_text()
    if "freely redistributed" not in segger_license or "RTT version: 6.18a" not in segger_source:
        raise AdmissionError("materialized SEGGER license/version terms drift")

    records = []
    seen_ranges = []
    provider_counts: Counter[str] = Counter()
    provider_bytes: Counter[str] = Counter()
    for address, raw in sorted(census["records"].items()):
        start = int(address, 16)
        end = raw["end_exclusive"]
        if end - start != raw["bytes"]:
            raise AdmissionError(f"{address}: body size drift")
        disposition = raw["disposition"]
        if disposition == "upstream_freetype_source":
            provider = "freetype-2.9.1-ftl"
            module = raw["upstream_module"]
            symbol = raw["upstream_function"]
            if module not in MODULE_PINS:
                raise AdmissionError(f"{address}: unpinned FreeType module {module}")
            if symbol not in source_text[module]:
                raise AdmissionError(f"{address}: {module}:{symbol} missing")
            license_id = "FTL"
        elif disposition == "upstream_segger_rtt_provider":
            provider = "segger-rtt-6.18a-external"
            module = raw["upstream_module"]
            symbol = raw["upstream_function"]
            if module != "SEGGER_RTT.c":
                raise AdmissionError(f"{address}: SEGGER module drift")
            if symbol not in segger_source:
                raise AdmissionError(f"{address}: SEGGER_RTT.c:{symbol} missing")
            license_id = "LicenseRef-SEGGER-RTT-Redistributable"
        else:
            raise AdmissionError(f"{address}: non-admissible disposition {disposition}")
        provider_counts[provider] += 1
        provider_bytes[provider] += raw["bytes"]
        seen_ranges.append((start, end))
        records.append({
            "start": address,
            "end_exclusive": f"0x{end:08X}",
            "bytes": raw["bytes"],
            "body_sha256": raw["sha256"],
            "provider": provider,
            "module": module,
            "symbol": symbol,
            "license": license_id,
        })
    if any(left[1] > right[0] for left, right in zip(seen_ranges, seen_ranges[1:])):
        raise AdmissionError("census ranges overlap")
    if (provider_counts["freetype-2.9.1-ftl"], provider_bytes["freetype-2.9.1-ftl"]) != (192, 33124):
        raise AdmissionError("FreeType provider closure drift")
    if (provider_counts["segger-rtt-6.18a-external"], provider_bytes["segger-rtt-6.18a-external"]) != (6, 520):
        raise AdmissionError("SEGGER provider closure drift")

    boundaries = closed["typed_non_census_boundaries"]
    if (boundaries["clusters"], boundaries["bytes"], boundaries["unclassified"]) != (4, 1118, {"clusters": 0, "bytes": 0}):
        raise AdmissionError("typed non-census boundary drift")
    boundary_records = []
    for row in boundaries["records"]:
        if row["claimed_exact"] or row["unclassified"] or row["disposition"] != "typed_external_not_in_none_census":
            raise AdmissionError("typed boundary fail-closed status drift")
        boundary_records.append({
            "start": f"0x{row['start']:08X}",
            "end_exclusive": f"0x{row['end_exclusive']:08X}",
            "bytes": row["bytes"],
            "body_sha256": row["sha256"],
            "candidate": row["source_order_candidate"],
            "status": "typed-external-not-callable",
            "reason": row["reason"],
        })

    mapping_sha = _sha(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "controlled-source-admission-ready",
        "read_only": True,
        "hardware_operations": False,
        "source_admission_record_ready": True,
        "redistributable_source_bundle_ready": True,
        "binary_overlay_admission_ready": False,
        "production_routed": False,
        "census": {
            "functions": len(records),
            "bytes": sum(row["bytes"] for row in records),
            "unclassified": {"functions": 0, "bytes": 0},
            "mapping_sha256": mapping_sha,
            "records": records,
        },
        "providers": {
            "freetype": {
                "functions": provider_counts["freetype-2.9.1-ftl"],
                "bytes": provider_bytes["freetype-2.9.1-ftl"],
                "version": "2.9.1",
                "tag": "VER-2-9-1",
                "commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
                "license": "FTL",
                "license_path": "third_party/freetype/LICENSE",
                "license_sha256": FT_LICENSE[1],
                "adobe_file_notice_and_patent_grant_retained": True,
                "source_materialized": True,
                "module_pins": module_records,
            },
            "segger_rtt": {
                "functions": provider_counts["segger-rtt-6.18a-external"],
                "bytes": provider_bytes["segger-rtt-6.18a-external"],
                **expected_segger,
                "manifest": "third-party/fetched/manifest.json",
                "manifest_sha256": SEGGER_MANIFEST[1],
                "container_archive_sha256": SEGGER_ARCHIVE_SHA256,
                "source_materialized": True,
                "line_endings": "repository-normalized LF; exact container source hash retained separately",
                "local_file_pins": segger_local,
                "admission_condition": "retain source and license together; supply reviewed product sdk_config/critical-section port",
            },
        },
        "provider_link_closure": {
            "classified_rows_resolved": 198,
            "classified_rows_unresolved": 0,
            "metadata_contract_cortex_m55_linkable": True,
            "segger_provider_cortex_m55_compilable": True,
            "segger_standard_runtime_symbols": ["memcpy", "strcpy", "strlen"],
            "segger_standard_runtime_symbols_locally_closed": True,
            "implementation_binary_link_closure_proven": False,
        },
        "typed_non_census_boundaries": {
            "clusters": 4,
            "bytes": 1118,
            "unclassified": {"clusters": 0, "bytes": 0},
            "records": boundary_records,
        },
        "binary_admission_blockers": list(BINARY_BLOCKERS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
