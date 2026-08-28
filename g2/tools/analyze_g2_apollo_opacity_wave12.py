#!/usr/bin/env python3
"""Audit Apollo opacity wave 12's AmbiqSuite MSPI device closure.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp"
FUNCTIONS = DECOMP / "functions.jsonl"
CORPUS = DECOMP / "bundles/apollo-decomp-05.c"
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
UPSTREAM = G2 / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
PROVENANCE = G2 / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
LICENSE = G2 / "third_party/ambiqsuite-apollo510/LICENSE"
ADMISSION = G2 / "research/admission/apollo_opacity_wave12"
BOUNDARY = ADMISSION / "source_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
PROVIDER_C = ADMISSION / "runtime_mspi_device_configure_provider.c"
PROVIDER_H = ADMISSION / "runtime_mspi_device_configure_provider.h"
ROOT = 0x004BFED6
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPUS: (582_144, "606364a89d1be4be2a6eb0c114069ffa93139ca36cf7b8e9739fae2458c282f1"),
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    UPSTREAM: (168_473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    PROVENANCE: (18_060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    LICENSE: (1_525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-12 evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise WaveError(f"pin drift: {path}")
    return data


def tsv_rows(path: Path) -> list[dict[str, str]]:
    lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
    if not lines:
        raise WaveError(f"empty TSV: {path}")
    return list(csv.DictReader(lines, delimiter="\t"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise WaveError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corpus_function(corpus: str, entry: int) -> str:
    match = re.search(rf"/\* FUN 0x{entry:08x} .*?(?=/\* FUN 0x|\Z)", corpus, re.S)
    if match is None:
        raise WaveError(f"0x{entry:08X}: corpus body missing")
    return match.group(0)


def residual_before() -> tuple[dict[int, dict[str, str]], set[int], dict[str, Any]]:
    wave11 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave11.py", "opacity_wave12_wave11")
    report11 = wave11.run_audit()
    if report11["after"] != {"functions": 1309, "bytes": 142400} or report11["largest_remaining"] != {"entry": "0x004BFED6", "envelope_bytes": 1902}:
        raise WaveError("wave-11 residual/root drift")
    parent_none, residual, _ = wave11.residual_before()
    residual -= {int(row["entry"], 16) for row in wave11.tsv_rows(wave11.BOUNDARY)}
    return parent_none, residual, report11


def run_audit() -> dict[str, Any]:
    parent_none, residual, report11 = residual_before()
    before = {"functions": len(residual), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual)}
    if before != report11["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (1902, ROOT):
        raise WaveError("authoritative residual drift")

    local = {path: pinned(path) for path in PINS}
    payload = local[IMAGE][OTA_HEADER_BYTES:]
    functions = {int(row["entry"], 16): row for row in (json.loads(line) for line in local[FUNCTIONS].decode().splitlines())}
    body = corpus_function(local[CORPUS].decode(errors="ignore"), ROOT)
    rows = tsv_rows(BOUNDARY)
    if len(rows) != 1 or int(rows[0]["entry"], 16) != ROOT or ROOT not in residual:
        raise WaveError("selected root drift")
    row = rows[0]
    fn = functions[ROOT]
    parent = parent_none[ROOT]
    end = int(row["end_exclusive"], 16)
    envelope = int(row["envelope_bytes"])
    ranges = tuple((int(a, 16), int(b, 16) + 1) for a, b in fn["ranges"])
    installed = payload[ROOT - LOAD_ADDRESS:end - LOAD_ADDRESS]
    observed = (end, envelope, int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["symbol"], row["provider_identity"], row["license_status"], row["disposition"])
    expected = (int(parent["body_end_exclusive"], 16), int(parent["official_opaque_bytes"]), int(fn["body_bytes"]), fn["body_sha256"], 0, "mspi_device_configure", "AmbiqSuite-SDK-5.1.0-5efc0228528a8adce5eae0d226fac85d2551eb3b", "BSD-3-Clause", "source-attributed-research-only")
    if observed != expected or ranges != ((ROOT, end),) or len(installed) != envelope or sha256(installed) != row["body_sha256"]:
        raise WaveError("root body/range/source boundary drift")
    if fn["callees"] or re.findall(r"\bFUN_[0-9a-f]{8}\(", body)[1:]:
        raise WaveError("unexpected residual/static call closure")

    upstream = local[UPSTREAM].decode(errors="ignore")
    provenance = json.loads(local[PROVENANCE])
    license_text = local[LICENSE].decode(errors="ignore")
    if provenance["license"] != "BSD-3-Clause" or provenance["upstream"]["selected_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b" or "Redistribution and use in source and binary forms" not in license_text:
        raise WaveError("upstream provenance/license drift")
    upstream_function = upstream[upstream.index("mspi_device_configure(am_hal_mspi_state_t"):upstream.index("mspi_piomixed_configure(am_hal_mspi_state_t")]
    enum_names = re.findall(r"case (AM_HAL_MSPI_FLASH_[A-Z0-9_]+):", upstream_function)
    if len(enum_names) != 26 or len(set(enum_names)) != 26:
        raise WaveError("upstream 26-mode switch drift")
    for token in ("MSPIn(ui32Module)->DEV0CFG_b.DEVCFG0", "MSPIn(ui32Module)->DEV0CFG_b.SEPIO0", "MSPIn(ui32Module)->DEV0XIP_b.XIPMIXED0", "MSPIn(ui32Module)->PADOUTEN", "0x80000013", "0x8000001F"):
        if token not in upstream_function:
            raise WaveError(f"upstream source anchor missing: {token}")
    for token in ("0xffffffe0", "0xfdffffff", "0xfffff0ff", "0x3ff"):
        if token not in body.lower():
            raise WaveError(f"installed source anchor missing: {token}")

    frontier = tsv_rows(FRONTIER)
    if frontier != [{"scope": "complete-selected-closure", "selected_functions": "1", "static_call_targets": "0", "static_call_edges": "0", "wave12_additional_function_bytes": "0"}]:
        raise WaveError("zero frontier reconciliation drift")
    interior = tsv_rows(INTERIORS)
    if interior != [{"scope": "complete-selected-closure", "functions": "1", "range_count_per_function": "1", "interior_islands": "0", "interior_physical_bytes": "0", "wave12_additional_function_bytes": "0"}]:
        raise WaveError("interior reconciliation drift")

    dat = {int(value, 16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)}
    shared = tsv_rows(SHARED)
    if {int(item["address"], 16) for item in shared} != dat or dat != {0x004C0754, 0x004C0994, 0x004C0998, 0x004C0F20}:
        raise WaveError("direct data graph drift")
    expected_values = {0x004C0754: 0x40060000, 0x004C0994: 0x80000013, 0x004C0998: 0x8000001F, 0x004C0F20: 0x0007FFFF}
    for item in shared:
        address = int(item["address"], 16)
        physical = payload[address - LOAD_ADDRESS:address - LOAD_ADDRESS + 4]
        value = struct.unpack("<I", physical)[0]
        observed_data = (int(item["size"]), item["bytes_hex"], item["sha256"], item["value"], item["consumers"], int(item["wave12_additional_function_bytes"]))
        expected_data = (4, physical.hex(), sha256(physical), f"0x{value:08X}", "0x004BFED6", 0)
        if observed_data != expected_data or value != expected_values[address]:
            raise WaveError(f"0x{address:08X}: shared data drift")

    provider_c = PROVIDER_C.read_text()
    provider_h = PROVIDER_H.read_text()
    if "SPDX-License-Identifier: BSD-3-Clause" not in provider_c or "SPDX-License-Identifier: BSD-3-Clause" not in provider_h or "OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT = 26" not in provider_h:
        raise WaveError("software-only provider/license drift")
    if any(token in provider_c for token in ("0x40060000", "volatile", "MSPIn(")):
        raise WaveError("provider model unexpectedly performs or exposes MMIO")

    remaining = residual - {ROOT}
    after = {"functions": len(remaining), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in remaining)}
    largest_bytes, largest_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in remaining)
    if after != {"functions": 1308, "bytes": 140498} or (largest_entry, largest_bytes) != (0x00438FB8, 1710):
        raise WaveError("after residual drift")
    canonical = {key: row[key] for key in ("entry", "symbol", "source_path", "provider_identity", "license_status", "disposition", "body_sha256")}
    return {
        "status": "opacity-wave12-apollo510-mspi-device-source-closure",
        "wave11_residual": report11["after"],
        "before": before,
        "selected_root_range": {"start": "0x004BFED6", "end_exclusive": "0x004C0644"},
        "actionable_graph": {"positive_functions": 1, "positive_bytes": 1902, "closure_depth_max": 0, "terminal_functions": 0, "static_call_edges": 0},
        "source_attributed": {"functions": 1, "bytes": 1902, "provider": row["provider_identity"], "license": "BSD-3-Clause"},
        "range_partition": {"functions": 1, "contiguous_functions": 1, "interior_islands": 0, "interior_physical_bytes": 0},
        "shared_data": {"direct_cells": 4, "physical_bytes": 16, "additional_function_bytes": 0},
        "provider_model": {"device_modes": 26, "pure_register_plan": True, "mmio_operations": 0},
        "after": after,
        "largest_remaining": {"entry": f"0x{largest_entry:08X}", "envelope_bytes": largest_bytes},
        "record": dict(row, source_identity_authenticated=True),
        "mapping_sha256": sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()),
        "production_routed": False,
        "production_blocker": "missing exact private-state ABI/SDK revision plus reviewed dual-profile IAR Cortex-M55 codegen, relocation, link-order, and placement proof",
        "read_only": True,
        "hardware_operations": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
