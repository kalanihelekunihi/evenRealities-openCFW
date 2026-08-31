#!/usr/bin/env python3
"""Authenticate the production-routed clean-room NemaVG stroke-cap leaves."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
CORPUS = ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-08.c"
PROVENANCE = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
SOURCE = ROOT / "components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c"
HEADER = SOURCE.with_suffix(".h")
PRODUCTION_SOURCE = (
    ROOT / "components/apollo_main/core_overlay/"
    "runtime_nemavg_stroke_cap_endpoints.c"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SUMMARY = ROOT / "tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json"

PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    PROVENANCE: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
    SOURCE: (6_523, "738b8749da5f234aacaa076c087f4c99541330c30c6c475d775dc1566747edb0"),
    HEADER: (2_379, "39f9d1b645f6cbfd4cb267ba32953a0787e717ebf67936619b4d7c67142bba6c"),
    PRODUCTION_SOURCE: (
        15_166,
        "33c9292bb52e276982e9b6c4c51bc02d9381eec98f50f223c876c7f691a986a4",
    ),
}

EXPECTED = {
    0x0051B8F0: {
        "symbol": "draw_start_cap",
        "style_offsets": ["0x2e0"],
        "body_bytes": 1664,
        "physical_bytes": 1668,
        "body_sha256": "549fd3c4e21f1074d6f2b04309e72283b3f85b575f41bd31fc4718f7a63e3382",
        "ranges": [["0051b8f0", "0051bd1b"], ["0051bd20", "0051bf73"]],
        "public_dwarf_line": 1853,
    },
    0x0051BF7C: {
        "symbol": "draw_end_cap",
        "style_offsets": ["0x2e1"],
        "body_bytes": 1636,
        "physical_bytes": 1640,
        "body_sha256": "d022571f745517bf7494d69d79e5c1ba934faf8dc65c0cb6f465d4f36fb81d56",
        "ranges": [["0051bf7c", "0051c393"], ["0051c398", "0051c5e3"]],
        "public_dwarf_line": 1888,
    },
    0x0051C5EC: {
        "symbol": "draw_caps",
        "style_offsets": ["0x2e0", "0x2e1"],
        "body_bytes": 3298,
        "physical_bytes": 3306,
        "body_sha256": "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27",
        "ranges": [["0051c5ec", "0051ccc7"], ["0051cccc", "0051d08f"],
                   ["0051d094", "0051d2d5"]],
        "public_dwarf_line": 1924,
    },
}
EXPECTED_CALLEES = {
    "00516b34", "0052266e", "005226b2", "00522a24", "00522f1c",
    "00523a34", "0052405c", "00524130", "00524218",
}
DRAW_CAPS_EXTRA_CALLEES = {"0051565c"}
RETAINED_DISPATCH_CALLER = 0x0051D2E0
RETAINED_DISPATCH_CALLER_SUCCESSOR = 0x0051F798
PRODUCTION_ROUTES = {
    0x0051B8F0: "open_cfw_nemavg_draw_start_cap_endpoint",
    0x0051BF7C: "open_cfw_nemavg_draw_end_cap_endpoint",
    0x0051C5EC: "open_cfw_nemavg_draw_caps_dispatch",
}
RETAINED_PROVIDER_TARGETS = {
    "open_cfw_retained_nemavg_calculate_steps": 0x00522F1C,
    "open_cfw_retained_nemavg_cos": 0x00524130,
    "open_cfw_retained_nemavg_enable_aa": 0x0052266E,
    "open_cfw_retained_nemavg_raster_quad": 0x00516B34,
    "open_cfw_retained_nemavg_raster_triangle": 0x00522A24,
    "open_cfw_retained_nemavg_raster_triangle_fan": 0x00523A34,
    "open_cfw_retained_nemavg_restore_aa": 0x005226B2,
    "open_cfw_retained_nemavg_set_error": 0x0051565C,
    "open_cfw_retained_nemavg_sin": 0x0052405C,
    "open_cfw_retained_nemavg_sqrt": 0x00524218,
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise AuditError(f"identity drift: {path}")
    return data


def _function_body(corpus: str, entry: int, next_entry: int | None) -> str:
    marker = f"/* FUN 0x{entry:08x} "
    start = corpus.find(marker)
    if start < 0:
        raise AuditError(f"0x{entry:08X}: corpus marker missing")
    if next_entry is None:
        end = len(corpus)
    else:
        end = corpus.find(f"/* FUN 0x{next_entry:08x} ", start + len(marker))
        if end < 0:
            raise AuditError(f"0x{entry:08X}: successor marker missing")
    return corpus[start:end]


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path) for path in PINS}
    functions = {
        int(row["entry"], 16): row
        for row in (json.loads(line) for line in
                    inputs[FUNCTIONS].decode("utf-8").splitlines())
        if int(row["entry"], 16) in EXPECTED
    }
    if set(functions) != set(EXPECTED):
        raise AuditError("stock stroke-cap function set changed")
    corpus = inputs[CORPUS].decode("utf-8", errors="ignore")
    retained_dispatch = _function_body(
        corpus,
        RETAINED_DISPATCH_CALLER,
        RETAINED_DISPATCH_CALLER_SUCCESSOR,
    )
    retained_sequence = (
        "FUN_0051b8f0(), iVar5 != 0 || "
        "(iVar5 = FUN_0051bf7c(), iVar5 != 0)"
    )
    if (
        retained_dispatch.count(retained_sequence) != 1
        or "*(undefined4 *)(iVar7 + 0x114) = 0;" not in retained_dispatch
        or "*(undefined4 *)(iVar7 + 0x118) = 0;" not in retained_dispatch
        or "FUN_0051565c(iVar5);" not in retained_dispatch
    ):
        raise AuditError("retained stroke-cap dispatch/error contract drift")
    overlay = json.loads(OVERLAY.read_text())
    build_report = json.loads(BUILD_REPORT.read_text())
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    source_identity = {
        "path": source_path,
        "size": PINS[PRODUCTION_SOURCE][0],
        "sha256": PINS[PRODUCTION_SOURCE][1],
    }
    configured_leaves = {
        item.get("function"): item
        for item in overlay.get("relocated_leaves", [])
        if item.get("function") in PRODUCTION_ROUTES.values()
    }
    configured_patches = {
        item.get("runtime_address"): item
        for item in overlay.get("patch_sites", [])
        if item.get("runtime_address") in PRODUCTION_ROUTES
    }
    built_leaves = {
        item.get("extraction", {}).get("function"): item
        for item in build_report.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function")
        in PRODUCTION_ROUTES.values()
    }
    built_patches = {
        item.get("runtime_address"): item
        for item in build_report.get("overlay", {}).get("patched_sites", [])
        if item.get("runtime_address") in PRODUCTION_ROUTES
    }
    if (
        set(configured_leaves) != set(PRODUCTION_ROUTES.values())
        or set(configured_patches) != set(PRODUCTION_ROUTES)
        or set(built_leaves) != set(PRODUCTION_ROUTES.values())
        or set(built_patches) != set(PRODUCTION_ROUTES)
    ):
        raise AuditError("production NemaVG route set changed")

    for entry, function in PRODUCTION_ROUTES.items():
        expected = EXPECTED[entry]
        leaf = configured_leaves[function]
        patch = configured_patches[entry]
        built_leaf = built_leaves[function]
        built_patch = built_patches[entry]
        source = leaf.get("source", {})
        if (
            leaf.get("strict_relocation_contract") is not True
            or {key: source.get(key) for key in source_identity} != source_identity
            or patch.get("target_function") != function
            or patch.get("expected_size") != expected["physical_bytes"]
            or patch.get("expected_sha256") != expected["body_sha256"]
            or built_patch.get("target_function") != function
            or built_patch.get("expected_size") != expected["physical_bytes"]
            or built_patch.get("expected_sha256") != expected["body_sha256"]
            or built_leaf.get("source") != source
        ):
            raise AuditError(f"0x{entry:08X}: production route identity drift")
        for profile in (None, "linux-clang"):
            profile_leaf = (
                leaf if profile is None
                else leaf.get("toolchain_profiles", {}).get(profile, {})
            )
            expected_pin = profile_leaf.get("expected")
            relocations = profile_leaf.get("relocations")
            if (
                not isinstance(expected_pin, dict)
                or not isinstance(expected_pin.get("sha256"), str)
                or len(expected_pin["sha256"]) != 64
                or not isinstance(relocations, list)
                or not relocations
            ):
                raise AuditError(
                    f"0x{entry:08X}: dual-profile leaf pin missing"
                )
            for relocation in relocations:
                symbol = relocation.get("symbol")
                if symbol in RETAINED_PROVIDER_TARGETS:
                    if relocation.get("target_address") != RETAINED_PROVIDER_TARGETS[symbol]:
                        raise AuditError(
                            f"0x{entry:08X}: retained provider target drift"
                        )
                elif relocation.get("target_function") not in (
                    "open_cfw_nemavg_draw_start_cap_endpoint",
                    "open_cfw_nemavg_draw_end_cap_endpoint",
                ):
                    raise AuditError(
                        f"0x{entry:08X}: unauthenticated relocation provider"
                    )
        apple_pins = dict(leaf["expected"])
        apple_pins["relocations"] = leaf["relocations"]
        if built_leaf.get("pins") != apple_pins:
            raise AuditError(f"0x{entry:08X}: live Apple leaf pin drift")

    dual_profile_pins_ready = True
    production_routed = True
    records = []
    ordered = sorted(EXPECTED)
    for index, entry in enumerate(ordered):
        expected = EXPECTED[entry]
        row = functions[entry]
        expected_callees = EXPECTED_CALLEES | (
            DRAW_CAPS_EXTRA_CALLEES if entry == 0x0051C5EC else set())
        if (row["body_bytes"], row["body_sha256"], row["ranges"],
                set(row["callees"])) != (
                    expected["body_bytes"], expected["body_sha256"],
                    expected["ranges"], expected_callees):
            raise AuditError(f"0x{entry:08X}: stock body/call graph drift")
        successor = ordered[index + 1] if index + 1 < len(ordered) else 0x0051D2E0
        body = _function_body(corpus, entry, successor)
        if expected["body_sha256"] not in body.splitlines()[0]:
            raise AuditError(f"0x{entry:08X}: corpus digest marker drift")
        if (any(offset not in body for offset in expected["style_offsets"]) or
                "0x800000" not in body):
            raise AuditError(f"0x{entry:08X}: cap-style dispatch evidence drift")
        records.append({
            "entry": f"0x{entry:08X}",
            "end_exclusive": f"0x{int(row['body_end_inclusive'], 16) + 1:08X}",
            "body_bytes": expected["body_bytes"],
            "physical_bytes": expected["physical_bytes"],
            "body_sha256": expected["body_sha256"],
            "symbol": expected["symbol"],
            "style_context_offsets": expected["style_offsets"],
            "public_archive_dwarf_declaration_line": expected["public_dwarf_line"],
            "source_status": "production-source",
            "production_routed": production_routed,
        })

    provenance = json.loads(inputs[PROVENANCE])
    artifacts = {item["path"]: item for item in provenance["selected_artifacts"]}
    archive = artifacts.get("libraries/lib_nema_apollo5x_nemagfx.a", {})
    license_record = artifacts.get("headers/LICENSE", {})
    if (provenance["public_source_state"]["first_complete_exact_commit"] !=
            "b853fded7e545f005727e13bf2ce83018c7e242d" or
            archive.get("sha256") !=
            "109840f6e0bbeb8618a1a853966cdf68cf169620bcc4075ed7a1c86ab0d3286f" or
            license_record.get("sha256") !=
            "bb504491bd00c656c9622c9b9cfe805273c8c626ceb35480b5907983de718fbc"):
        raise AuditError("public Nema artifact/license identity drift")

    source_text = inputs[SOURCE].decode("ascii")
    header_text = inputs[HEADER].decode("ascii")
    production_text = inputs[PRODUCTION_SOURCE].decode("ascii")
    combined = source_text + header_text
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise AuditError("candidate MIT declarations drift")
    for symbol in ("open_cfw_nemavg_draw_start_cap",
                   "open_cfw_nemavg_draw_end_cap",
                   "open_cfw_nemavg_draw_caps"):
        if combined.count(symbol) < 2:
            raise AuditError(f"candidate API missing: {symbol}")
    if "__asm" in combined or ".byte" in combined:
        raise AuditError("candidate contains raw instruction directives")
    if header_text.count(
        "const struct open_cfw_nemavg_stroke_caps *caps"
    ) != 3:
        raise AuditError("caller-owned endpoint candidate ABI drift")
    for symbol in PRODUCTION_ROUTES.values():
        if production_text.count(symbol) < 1:
            raise AuditError(f"production API missing: {symbol}")
    if (
        "0x20074F04" not in production_text
        or "context + UINT32_C(0x114)" not in production_text
        or "context + UINT32_C(0x118)" not in production_text
        or "__asm" in production_text
        or ".byte" in production_text
    ):
        raise AuditError("production stroke-cap endpoint contract drift")

    routed_records = [item for item in records if item["production_routed"]]
    routed_bytes = sum(item["physical_bytes"] for item in routed_records)

    return {
        "schema_version": 1,
        "status": "nemavg-stroke-caps-production-source-routed",
        "analysis_mode": "offline; no hardware, MMIO, signing, flashing, or publishing operation",
        "provider_evidence": {
            "family": "Think Silicon NemaVG 1.1.8 co-packaged candidate",
            "public_artifact_commit": "b853fded7e545f005727e13bf2ce83018c7e242d",
            "public_archive_sha256": archive["sha256"],
            "public_dwarf_symbols": ["draw_start_cap", "draw_end_cap", "draw_caps"],
            "public_dwarf_lines": [1853, 1888, 1924],
            "license": "LicenseRef-Think-Silicon-NemaSDK-Permissive",
            "exact_stock_generating_archive_proven": False,
        },
        "stock": {
            "functions": len(records),
            "function_body_bytes": sum(item["body_bytes"] for item in records),
            "physical_bytes": sum(item["physical_bytes"] for item in records),
            "records": records,
        },
        "candidate": {
            "license": "MIT",
            "semantic_c": True,
            "raw_instruction_bytes": 0,
            "functions": 3,
            "production_source": source_identity,
            "production_routed": len(routed_records) == len(records),
            "production_routed_functions": len(routed_records),
            "production_routed_physical_bytes": routed_bytes,
            "remaining_candidate_functions": len(records) - len(routed_records),
            "remaining_candidate_physical_bytes": (
                sum(item["physical_bytes"] for item in records) - routed_bytes
            ),
            "draw_caps_no_argument_abi_authenticated": True,
            "retained_endpoint_dispatch_sequence_authenticated": True,
            "retained_endpoint_relocations_authenticated": True,
            "endpoint_stock_entries_unpatched": False,
            "endpoint_candidate_exact_stock_abi": True,
            "endpoint_candidate_abi": (
                "no arguments; global context through 0x20074F04"
            ),
            "authenticated_stock_endpoint_abi": (
                "no arguments; global context through 0x20074F04"
            ),
            "dual_profile_leaf_pins_authenticated": dual_profile_pins_ready,
            "context_pointer_cell": "0x20074F04",
            "error_state_offsets": ["0x114", "0x118"],
            "software_blocker": None,
        },
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_manifest:
        SUMMARY.write_text(rendered, encoding="utf-8")
        print(f"wrote {SUMMARY}")
    else:
        print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
