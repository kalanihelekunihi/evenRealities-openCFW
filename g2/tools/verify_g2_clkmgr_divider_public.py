#!/usr/bin/env python3
"""Verify the public, corpus-free G2 clock-divider source/routing contract."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/ambiq/runtime_clkmgr_divider_candidate.c"
HEADER = SOURCE.with_suffix(".h")
MAIN_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SUMMARY = ROOT / "tools/manifests/g2-clkmgr-divider-candidate-summary.json"
SOURCE_PATH = "components/shared/ambiq/runtime_clkmgr_divider_candidate.c"

SOURCE_PIN = (
    1_268,
    "090373ed2672073930edcf35783fc1fcd785a2a812ca10088f14d8261c8b7498",
)
HEADER_PIN = (
    814,
    "d00ecb7c890ceea632769bd5c12ad8f2ac15ddf3d82a2b2f558bc031e53fb657",
)
EXPECTED = {
    "open_cfw_clkmgr_hfrc2_uq15_divider": {
        "compiled_size": 88,
        "compiled_sha256":
            "0113dce6f97c06a6bf0979cb237e245849e359377cee6ec44ab3e3b7bcf8b0e0",
        "stock_size": 42,
        "stock_sha256":
            "5d56a93dc2746c295ee2b3507ab4e1be4dae68f057dff4f26b519616bfd486df",
    },
    "open_cfw_clkmgr_hfrc_integer_divider": {
        "compiled_size": 18,
        "compiled_sha256":
            "ef3f0a171a8b56b19881704872749380f682216aa09bd656a34deabb60d4c5d3",
        "stock_size": 10,
        "stock_sha256":
            "15eabeb671434c5c1f485fd4600130400e24f0e1ce62364e4b684e1b6e17bfdf",
    },
}


class VerificationError(RuntimeError):
    """Raised when the public clock-divider contract stops matching."""


def _require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"public clock-divider JSON is invalid: {path}") from error
    _require(isinstance(value, dict), f"public clock-divider JSON shape changed: {path}")
    return value


def _indexed(rows: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(rows, list), f"{label} is not a list")
    _require(all(isinstance(row, dict) and isinstance(row.get(key), str)
                 for row in rows), f"{label} row shape changed")
    result = {row[key]: row for row in rows}
    _require(len(result) == len(rows), f"{label} contains duplicate identities")
    return result


def _verify_route(config: dict[str, Any], leaf_key: str, label: str) -> None:
    leaves = _indexed(config.get(leaf_key), "function", f"{label} leaves")
    selected = {name: leaves[name] for name in EXPECTED if name in leaves}
    _require(set(selected) == set(EXPECTED), f"{label} divider leaf census changed")
    patches = _indexed(config.get("patch_sites"), "name", f"{label} patch sites")
    selected_patches: dict[str, dict[str, Any]] = {}
    for patch in patches.values():
        target = patch.get("target_function")
        if target in EXPECTED:
            _require(target not in selected_patches,
                     f"{label} divider patch target is duplicated")
            selected_patches[target] = patch
    _require(set(selected_patches) == set(EXPECTED),
             f"{label} divider patch census changed")

    for function, expected in EXPECTED.items():
        leaf = selected[function]
        source = leaf.get("source")
        _require(isinstance(source, dict), f"{label} divider source metadata changed")
        _require(
            source.get("path") == SOURCE_PATH
            and source.get("size") == SOURCE_PIN[0]
            and source.get("sha256") == SOURCE_PIN[1]
            and source.get("license") == "MIT",
            f"{label} divider source identity changed",
        )
        compiled = leaf.get("expected")
        _require(isinstance(compiled, dict),
                 f"{label} divider compiled contract changed")
        _require(
            compiled.get("size") == expected["compiled_size"]
            and compiled.get("sha256") == expected["compiled_sha256"]
            and compiled.get("unrelocated_sha256")
                == expected["compiled_sha256"],
            f"{label} divider compiled identity changed",
        )
        _require(leaf.get("strict_relocation_contract") is True,
                 f"{label} divider relocation policy changed")
        _require(leaf.get("relocations") == [],
                 f"{label} divider unexpectedly needs relocations")
        toolchain = leaf.get("toolchain")
        _require(isinstance(toolchain, dict)
                 and toolchain.get("target") == "arm-none-eabi",
                 f"{label} divider target changed")
        profiles = leaf.get("toolchain_profiles")
        _require(isinstance(profiles, dict)
                 and isinstance(profiles.get("linux-clang"), dict),
                 f"{label} divider Linux profile disappeared")

        patch = selected_patches[function]
        _require(
            patch.get("branch") == "b_w"
            and patch.get("expected_size") == expected["stock_size"]
            and patch.get("expected_sha256") == expected["stock_sha256"],
            f"{label} divider guarded entry route changed",
        )


def verify() -> dict[str, Any]:
    source = SOURCE.read_bytes()
    header = HEADER.read_bytes()
    _require((len(source), _sha256(source)) == SOURCE_PIN,
             "public clock-divider source identity changed")
    _require((len(header), _sha256(header)) == HEADER_PIN,
             "public clock-divider header identity changed")
    combined = source.decode("utf-8") + header.decode("utf-8")
    _require(combined.count("SPDX-License-Identifier: MIT") == 2,
             "public clock-divider MIT declarations changed")
    _require("__asm" not in combined and ".byte" not in combined,
             "public clock-divider source contains raw instruction directives")
    for function in EXPECTED:
        _require(combined.count(function) >= 2,
                 f"public clock-divider API disappeared: {function}")

    _verify_route(_read_json(MAIN_OVERLAY), "relocated_leaves", "Apollo main")
    _verify_route(_read_json(BOOT_OVERLAY), "cave_leaves", "Apollo bootloader")

    summary = _read_json(SUMMARY)
    candidate = summary.get("candidate")
    stock = summary.get("stock")
    _require(
        summary.get("schema_version") == 1
        and summary.get("status") == "apollo-clkmgr-divider-production-routed"
        and summary.get("hardware_validation") == "blocked by unavailable physical evidence"
        and summary.get("hardware_operations") == []
        and isinstance(candidate, dict)
        and candidate.get("license") == "MIT"
        and candidate.get("semantic_c") is True
        and candidate.get("raw_instruction_bytes") == 0
        and candidate.get("production_routed") is True
        and isinstance(stock, dict)
        and stock.get("functions_per_image") == 2
        and stock.get("bootloader_bytes") == 52
        and stock.get("apollo_main_bytes") == 52,
        "public clock-divider summary contract changed",
    )
    records = stock.get("records")
    _require(isinstance(records, list) and len(records) == 2,
             "public clock-divider summary record census changed")
    by_function = {row.get("candidate_symbol"): row for row in records
                   if isinstance(row, dict)}
    _require(set(by_function) == set(EXPECTED),
             "public clock-divider summary function census changed")
    for function, expected in EXPECTED.items():
        row = by_function[function]
        _require(
            row.get("body_sha256") == expected["stock_sha256"]
            and row.get("bytes_per_image") == expected["stock_size"],
            f"public clock-divider summary identity changed: {function}",
        )

    return {
        "schema_version": 1,
        "status": "public-clock-divider-source-and-route-verified",
        "functions": len(EXPECTED),
        "source_sha256": SOURCE_PIN[1],
        "profiles_declared": ["apple-clang", "linux-clang"],
        "private_admission_artifacts_required_for_receipt_reproduction": True,
        "private_admission_receipt_reproduced": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    print(json.dumps(verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeDecodeError, VerificationError) as error:
        raise SystemExit(f"public clock-divider verification failed: {error}") from error
