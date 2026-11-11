#!/usr/bin/env python3
"""Compare a G2 source candidate with the authenticated locked OTA payloads.

Aligned byte counts are diagnostics, not code coverage: changed section order
and lengths can shift otherwise equivalent functions. This tool reads stock
components only as a comparison oracle and never inserts them into an output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from open_cfw import EVENOTA_COMPONENT_HEADER_SIZE, EVENOTA_TOC_OFFSET, validate_evenota_image

G2 = Path(__file__).resolve().parents[1]
ROOT = G2.parent
MANIFEST = G2 / "manifests/g2-2.2.6.10.json"
TARGET = G2 / "workflow/target.json"
CODEC_COMMAND_WINDOW = (0x18D90, 0x1B15C)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def aligned_comparison(stock: bytes, candidate: bytes) -> dict:
    first = None
    same = 0
    run_start = run_length = 0
    best_start = best_length = 0
    for offset, (left, right) in enumerate(zip(stock, candidate)):
        if left == right:
            same += 1
            if run_length == 0:
                run_start = offset
            run_length += 1
            if run_length > best_length:
                best_start, best_length = run_start, run_length
        else:
            if first is None:
                first = offset
            run_length = 0
    if first is None and len(stock) != len(candidate):
        first = min(len(stock), len(candidate))
    return {
        "stock_bytes": len(stock),
        "candidate_bytes": len(candidate),
        "size_delta_bytes": len(candidate) - len(stock),
        "same_offset_equal_bytes": same,
        "first_same_offset_difference": first,
        "longest_same_offset_equal_run": {"offset": best_start, "bytes": best_length},
        "byte_identical": stock == candidate,
    }


def candidate_payloads(bundle: bytes, manifest: dict) -> dict[str, bytes]:
    validate_evenota_image(bundle, manifest)
    payloads = {}
    for index, component in enumerate(manifest["components"]):
        _, offset, size, _ = struct.unpack_from("<IIII", bundle,
            EVENOTA_TOC_OFFSET + index * 16)
        payloads[component["name"]] = bundle[
            offset + EVENOTA_COMPONENT_HEADER_SIZE:offset + size]
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--link-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    target = json.loads(TARGET.read_text())
    identity_sources = {row["path"]: row["sha256"] for row in target["identity_sources"]}
    if identity_sources.get("g2/manifests/g2-2.2.6.10.json") != sha256(manifest_bytes):
        parser.error("G2 manifest differs from the locked workflow target")
    if (target["bundle"]["size"] != manifest["package"]["expected_size"] or
            target["bundle"]["sha256"] != manifest["package"]["expected_sha256"]):
        parser.error("G2 manifest bundle identity differs from the locked target")
    candidate = args.candidate.read_bytes()
    report_bytes = args.link_report.read_bytes()
    link_report = json.loads(report_bytes)
    candidate_info = link_report.get("g2_bundle_source_candidate", {})
    if candidate_info.get("sha256") != sha256(candidate) or candidate_info.get("bytes") != len(candidate):
        parser.error("candidate differs from the source-link receipt")
    if candidate_info.get("manifest_sha256") != sha256(manifest_bytes):
        parser.error("source-link receipt uses a different G2 manifest")
    payloads = candidate_payloads(candidate, manifest)
    target_components = {row["id"]: row for row in target["components"]}
    comparisons = []
    for component in manifest["components"]:
        provider = component["provider"]
        if provider["kind"] != "official_blob":
            parser.error(f"{component['name']}: expected an authenticated official provider")
        target_component = target_components[component["name"]]
        if (target_component["size"] != provider["size"] or
                target_component["sha256"] != provider["sha256"]):
            parser.error(f"{component['name']}: provider differs from the locked workflow target")
        stock = (G2 / provider["path"]).read_bytes()
        if len(stock) != provider["size"] or sha256(stock) != provider["sha256"]:
            parser.error(f"{component['name']}: locked stock provider failed authentication")
        name = component["name"]
        comparison = {"name": name, "stock_sha256": sha256(stock),
                      "candidate_sha256": sha256(payloads[name]),
                      **aligned_comparison(stock, payloads[name])}
        if name == "codec":
            start, end = CODEC_COMMAND_WINDOW
            stock_commands = stock[start:end]
            candidate_commands = payloads[name][start:end]
            comparison["kws_command_window"] = {
                "file_window": [start, end],
                "stock_sha256": sha256(stock_commands),
                "candidate_sha256": sha256(candidate_commands),
                "byte_identical": stock_commands == candidate_commands,
            }
        comparisons.append(comparison)
    result = {
        "schema": 1,
        "method": "authenticated same-file-offset byte comparison; shifted sections are not aligned or classified",
        "source_completeness_proven": False,
        "locked_manifest_sha256": sha256(manifest_bytes),
        "source_link_report_sha256": sha256(report_bytes),
        "candidate_bundle_sha256": sha256(candidate),
        "locked_bundle_sha256": manifest["package"]["expected_sha256"],
        "bundle_byte_identical": (len(candidate) == manifest["package"]["expected_size"] and
                                  sha256(candidate) == manifest["package"]["expected_sha256"]),
        "components": comparisons,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(comparisons)} authenticated component comparisons: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
