#!/usr/bin/env python3
"""Fail-closed verification for the R1 bootloader reconstruction package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "bootloader-reconstruction"
GENERATED = PACKAGE / "generated"
IMAGE = ROOT / "research" / "decompilation" / "rebuild" / "rebuilt-bootloader.bin"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    image = IMAGE.read_bytes()
    require(len(image) == 0x6000, f"unexpected image size: {len(image)}")
    require(
        hashlib.sha256(image).hexdigest()
        == "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b",
        "live image hash mismatch",
    )
    require(image[0x5F64:] == b"\xff" * 0x9C, "logical tail is not erased padding")

    functions = rows(GENERATED / "functions.csv")
    names = rows(GENERATED / "function-names.csv")
    summary = json.loads((GENERATED / "summary.json").read_text(encoding="utf-8"))
    require(len(functions) == 304, f"expected 304 functions, found {len(functions)}")
    require(len(names) == 304, f"expected 304 name records, found {len(names)}")
    require(summary["function_count"] == 304, "summary function count mismatch")
    require(summary["decompile_failures"] == 0, "decompiler failure present")
    require(summary["logical_bytes"] == 24420, "logical byte count mismatch")
    require(summary["decoded_instruction_bytes"] == 19684, "instruction coverage changed")
    require(summary["defined_data_bytes"] == 2619, "defined-data coverage changed")
    require(summary["unclassified_logical_bytes"] == 2117, "unclassified coverage changed")

    function_entries = [row["entry"] for row in functions]
    name_entries = [row["entry"] for row in names]
    require(len(set(function_entries)) == len(function_entries), "duplicate function entry")
    require(function_entries == name_entries, "function/name ledgers are not address-aligned")
    require(
        all("FUN_" not in row["name"] for row in functions),
        "address-only Ghidra name remains",
    )
    require(
        len({row["name"] for row in functions}) == len(functions),
        "applied function names are not unique",
    )
    kinds = Counter(row["name_kind"] for row in names)
    confidence = Counter(row["confidence"] for row in names)
    require(kinds == {"recovered": 304}, f"name kinds changed: {kinds}")
    require(
        confidence == {"high": 268, "medium": 36},
        f"name confidence changed: {confidence}",
    )

    decompilation = (GENERATED / "r1_bootloader_ghidra.c").read_text(encoding="utf-8")
    require(decompilation.count(" * entry: ") == 304, "decompilation block count mismatch")
    require("DECOMPILE_FAILED" not in decompilation, "decompilation failure marker found")

    correlations = rows(GENERATED / "source-correlations-raw.csv")
    require(len(correlations) == 3576, f"unexpected BSim row count: {len(correlations)}")
    by_source: dict[str, list[int]] = defaultdict(list)
    for row in correlations:
        by_source[row["r1_entry"]].append(int(row["rank"]))
    require(len(by_source) == 298, f"unexpected BSim source count: {len(by_source)}")
    require(set(by_source).issubset(set(function_entries)), "BSim source outside function ledger")
    require(
        all(sorted(ranks) == list(range(1, 13)) for ranks in by_source.values()),
        "a BSim source does not have exactly ranks 1 through 12",
    )
    require(
        sha256(GENERATED / "source-correlations-raw.csv")
        == "9a9c9f4f391762a73c51c816675e45ba9d8f2904afb6e5803d7461b73302dcfc",
        "source-correlation evidence changed",
    )

    key_source = (PACKAGE / "sdk-overlay" / "r1_dfu_public_key.c").read_text(encoding="utf-8")
    initializer = key_source.split("const uint8_t pk[64] = {", 1)[1].split("};", 1)[0]
    key = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2})", initializer))
    require(len(key) == 64, f"public key length changed: {len(key)}")
    require(
        hashlib.sha256(key).hexdigest()
        == "e3cf089455dd88548fdc8336feb30212ce384deef9c54843313b9226e38c6b13",
        "public key hash mismatch",
    )

    firmware_project = PACKAGE / "firmware-project"
    project_key_source = (firmware_project / "src/r1_dfu_public_key.c").read_text(encoding="utf-8")
    project_initializer = project_key_source.split("const uint8_t pk[64] = {", 1)[1].split("};", 1)[0]
    project_key = bytes(
        int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2})", project_initializer)
    )
    require(project_key == key, "firmware-project public key differs from recovered key")
    subprocess.run(
        [
            "python3",
            str(firmware_project / "tools/vendor_sdk_subset.py"),
            "--verify-only",
        ],
        check=True,
    )
    vendor_files = (firmware_project / "vendor/vendor-files.txt").read_text(encoding="utf-8").splitlines()
    require(len(vendor_files) == 316, f"unexpected firmware-project vendor file count: {len(vendor_files)}")
    upstream_inputs = json.loads(
        (firmware_project / "verification/upstream-inputs.json").read_text(encoding="utf-8")
    )
    require(
        upstream_inputs["nrf5_sdk"]["sha256"]
        == "5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061",
        "firmware-project SDK provenance changed",
    )
    require(
        upstream_inputs["toolchain"]["sha256"]
        == "bbb9b87e442b426eca3148fa74705c66b49a63f148902a0ea46f676ec24f9ac6",
        "firmware-project toolchain provenance changed",
    )
    require(
        upstream_inputs["nrf5_sdk"]["vendor_files_mismatched"] == 0,
        "firmware-project upstream comparison has mismatches",
    )
    reproducibility = json.loads(
        (firmware_project / "verification/reproducibility.json").read_text(encoding="utf-8")
    )
    expected_builds = {
        "captured": {
            "r1_bootloader.out": "47226c7e6986e01212306c424bc6d9df143b6d07da234fc4db015b6d109bda54",
            "r1_bootloader.hex": "b0889621b1f467a762fcedd336987525ca391b693aa62047de16825281eeb904",
            "r1_bootloader.bin": "583bb6b52a055f4955c4e1336c1d8b0397f742ac44b368678a50861755ac238e",
        },
        "hardened": {
            "r1_bootloader.out": "081c61e4d8ecbfdd8d84cb40e2ab145da0788dcc5fb335510c6c7f3728cd2c91",
            "r1_bootloader.hex": "62aac1d5fe29ec66418b154a4228049fa24362f18136824f933480260c13b964",
            "r1_bootloader.bin": "c391cb17f90d85e433a6e103ecd312b636ea4c78b8bd2a74f15dab43ec137ac5",
        },
    }
    for profile, expected_artifacts in expected_builds.items():
        record = reproducibility.get(profile, {})
        require(record.get("rebuilds_match") is True, f"{profile} reproducibility not established")
        require(
            record.get("relocated_rebuild_matches") is True,
            f"{profile} relocated reproducibility not established",
        )
        require(record.get("artifacts") == expected_artifacts, f"{profile} artifact evidence changed")
        metrics = record.get("metrics", {})
        require(metrics.get("source_objects") == 74, f"{profile} source-object count changed")
        require(
            metrics.get("flash_function_addresses") == 321,
            f"{profile} flash-function count changed",
        )
        require(metrics.get("signed_updates_required") is True, f"{profile} signature policy changed")

    model = PACKAGE / "functional-model"
    try:
        subprocess.run(["make", "clean", "test"], cwd=model, check=True)
    finally:
        subprocess.run(["make", "clean"], cwd=model, check=True)

    print(
        "verified R1 bootloader reconstruction: "
        "304 functions, 304 recovered names, zero synthetic names, "
        "3,576 BSim rows, 316 vendored source/library files, "
        "reproducible target builds and functional-model tests passed"
    )


if __name__ == "__main__":
    main()
