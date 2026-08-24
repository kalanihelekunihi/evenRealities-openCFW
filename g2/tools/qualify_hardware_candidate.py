#!/usr/bin/env python3
"""Fail-closed, offline qualification for G2 hardware-test candidates.

This tool never opens BLE or serial devices.  It compares the Apollo main
payload in a candidate package with the reviewed stock package and emits the
smallest facts needed to decide whether the image belongs on the next rung of
the hardware qualification ladder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any


RUN_BASE = 0x00438000
PREAMBLE_BYTES = 32
VECTOR_BYTES = 0x100
CRITICAL_RUNTIME_RE = re.compile(
    r"(?:freertos_|cmsis_|rtos_|iar_mem|iar_errno|iar_domain|iar_range|"
    r"watchdog|kernel_(?:initialize|start)|start_scheduler)",
    re.IGNORECASE,
)


class QualificationError(ValueError):
    """The input cannot be proven eligible for the requested stage."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise QualificationError(f"{path} must contain a JSON object")
    return value


def _apollo_payload(package: bytes, report: dict[str, Any]) -> bytes:
    apollo = report.get("apollo_main")
    if not isinstance(apollo, dict):
        raise QualificationError("release report has no apollo_main object")
    offset = apollo.get("payload_offset")
    size = apollo.get("payload_size")
    if not isinstance(offset, int) or not isinstance(size, int):
        raise QualificationError("Apollo payload offset/size are not integers")
    if offset < 0 or size <= 0 or offset + size > len(package):
        raise QualificationError("Apollo payload range is outside the package")
    return package[offset : offset + size]


def _difference_runs(left: bytes, right: bytes) -> list[dict[str, int]]:
    limit = min(len(left), len(right))
    runs: list[dict[str, int]] = []
    index = 0
    while index < limit:
        if left[index] == right[index]:
            index += 1
            continue
        start = index
        while index < limit and left[index] != right[index]:
            index += 1
        runs.append({"start": start, "end": index, "size": index - start})
    if len(left) != len(right):
        runs.append(
            {
                "start": limit,
                "end": max(len(left), len(right)),
                "size": abs(len(left) - len(right)),
            }
        )
    return runs


def _stock_control_allowed_offsets(report: dict[str, Any]) -> set[int]:
    apollo = report["apollo_main"]
    fields = apollo.get("runtime_version_fields")
    if not isinstance(fields, dict) or set(fields) != {
        "settings",
        "product_test_0x24",
    }:
        raise QualificationError("release report lacks the two runtime fields")
    # Bytes 4..7 are the nested Apollo CRC32.  release_cfw changes the two
    # NUL-terminated strings from 2.2.6.10 to 2.2.6.0, which may alter the last
    # two byte positions in each fixed field.
    allowed = set(range(4, 8))
    for name in sorted(fields):
        offset = fields[name].get("payload_offset")
        if not isinstance(offset, int):
            raise QualificationError(f"runtime field {name} has no offset")
        allowed.update(range(offset, offset + 16))
    return allowed


def _overlay_metrics(
    config: dict[str, Any] | None,
    candidate_report: dict[str, Any],
) -> dict[str, Any]:
    if config is None:
        return {
            "patch_site_count": 0,
            "critical_runtime_patch_count": 0,
            "critical_runtime_patches": [],
            "metadata_bound_to_candidate": True,
        }
    sites = config.get("patch_sites")
    if not isinstance(sites, list) or any(not isinstance(x, dict) for x in sites):
        raise QualificationError("overlay patch_sites must be a list of objects")
    critical = []
    for site in sites:
        text = " ".join(
            str(site.get(key, "")) for key in ("name", "target_function")
        )
        if CRITICAL_RUNTIME_RE.search(text):
            critical.append(
                {
                    "name": site.get("name"),
                    "runtime_address": site.get("runtime_address"),
                    "target_function": site.get("target_function"),
                }
            )
    expected_component_sha256 = config.get("expected", {}).get("component_sha256")
    candidate_source_sha256 = candidate_report.get("apollo_main", {}).get(
        "source_sha256"
    )
    metadata_bound_to_candidate = bool(
        isinstance(expected_component_sha256, str)
        and isinstance(candidate_source_sha256, str)
        and expected_component_sha256 == candidate_source_sha256
    )
    return {
        "patch_site_count": len(sites),
        "critical_runtime_patch_count": len(critical),
        "critical_runtime_patches": critical,
        "expected_component_sha256": expected_component_sha256,
        "candidate_source_sha256": candidate_source_sha256,
        "metadata_bound_to_candidate": metadata_bound_to_candidate,
    }


def qualify(
    *,
    stock_package: bytes,
    candidate_package: bytes,
    stock_report: dict[str, Any],
    candidate_report: dict[str, Any],
    overlay_config: dict[str, Any] | None,
    stage: str,
    max_patch_sites: int,
    max_critical_runtime_patches: int,
) -> dict[str, Any]:
    stock = _apollo_payload(stock_package, stock_report)
    candidate = _apollo_payload(candidate_package, candidate_report)
    metrics = _overlay_metrics(overlay_config, candidate_report)
    vectors_equal = (
        len(stock) >= PREAMBLE_BYTES + VECTOR_BYTES
        and len(candidate) >= PREAMBLE_BYTES + VECTOR_BYTES
        and stock[PREAMBLE_BYTES : PREAMBLE_BYTES + VECTOR_BYTES]
        == candidate[PREAMBLE_BYTES : PREAMBLE_BYTES + VECTOR_BYTES]
    )
    initial_sp = reset_handler = None
    if len(candidate) >= PREAMBLE_BYTES + 8:
        initial_sp, reset_handler = struct.unpack_from("<II", candidate, PREAMBLE_BYTES)
    runs = _difference_runs(stock, candidate)
    changed_common_offsets = {
        index
        for index, (left, right) in enumerate(zip(stock, candidate))
        if left != right
    }

    reasons: list[str] = []
    if not vectors_equal:
        reasons.append("Cortex-M vector table differs from reviewed stock")
    if overlay_config is not None and not metrics["metadata_bound_to_candidate"]:
        reasons.append("overlay metadata is not hash-bound to this candidate payload")
    if stage == "stock-control":
        allowed = _stock_control_allowed_offsets(candidate_report)
        unexpected = sorted(changed_common_offsets - allowed)
        if len(stock) != len(candidate):
            reasons.append("stock-code control changed Apollo payload size")
        if unexpected:
            reasons.append(
                f"stock-code control changed {len(unexpected)} non-version/code bytes"
            )
        if overlay_config is not None or metrics["patch_site_count"]:
            reasons.append("stock-code control must not declare source patch sites")
    elif stage == "minimal-hook":
        if metrics["patch_site_count"] == 0:
            reasons.append("minimal-hook candidate has no source patch site")
        if metrics["patch_site_count"] > max_patch_sites:
            reasons.append(
                f"patch-site count {metrics['patch_site_count']} exceeds "
                f"qualification limit {max_patch_sites}"
            )
        if metrics["critical_runtime_patch_count"] > max_critical_runtime_patches:
            reasons.append(
                f"critical runtime patch count "
                f"{metrics['critical_runtime_patch_count']} exceeds qualification "
                f"limit {max_critical_runtime_patches}"
            )
    elif stage == "full-source":
        # Full-source is intentionally report-only until all earlier stages
        # have hardware evidence.  An operator must not mistake a structurally
        # valid build for an eligible first recovery flash.
        reasons.append("full-source requires recorded earlier-stage hardware passes")
    else:
        raise QualificationError(f"unknown stage {stage!r}")

    return {
        "schema_version": 1,
        "stage": stage,
        "eligible_for_next_hardware_test": not reasons,
        "blocking_reasons": reasons,
        "stock_apollo": {"size": len(stock), "sha256": _sha256(stock)},
        "candidate_apollo": {
            "size": len(candidate),
            "sha256": _sha256(candidate),
            "initial_sp": f"0x{initial_sp:08X}" if initial_sp is not None else None,
            "reset_handler": (
                f"0x{reset_handler:08X}" if reset_handler is not None else None
            ),
        },
        "vectors_equal": vectors_equal,
        "difference_run_count": len(runs),
        "changed_common_byte_count": len(changed_common_offsets),
        "difference_runs_sample": runs[:64],
        "difference_runs_omitted": max(0, len(runs) - 64),
        "overlay": {
            **metrics,
            "critical_runtime_patches": metrics["critical_runtime_patches"][:64],
            "critical_runtime_patches_omitted": max(
                0, len(metrics["critical_runtime_patches"]) - 64
            ),
        },
        "limits": {
            "max_patch_sites": max_patch_sites,
            "max_critical_runtime_patches": max_critical_runtime_patches,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-package", type=Path, required=True)
    parser.add_argument("--candidate-package", type=Path, required=True)
    parser.add_argument("--stock-report", type=Path, required=True)
    parser.add_argument("--candidate-report", type=Path, required=True)
    parser.add_argument("--overlay-config", type=Path)
    parser.add_argument(
        "--stage",
        choices=("stock-control", "minimal-hook", "full-source"),
        required=True,
    )
    parser.add_argument("--max-patch-sites", type=int, default=8)
    parser.add_argument("--max-critical-runtime-patches", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = qualify(
        stock_package=args.stock_package.read_bytes(),
        candidate_package=args.candidate_package.read_bytes(),
        stock_report=_load_json(args.stock_report),
        candidate_report=_load_json(args.candidate_report),
        overlay_config=(
            _load_json(args.overlay_config) if args.overlay_config is not None else None
        ),
        stage=args.stage,
        max_patch_sites=args.max_patch_sites,
        max_critical_runtime_patches=args.max_critical_runtime_patches,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["eligible_for_next_hardware_test"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
