#!/usr/bin/env python3
"""Build deterministic size/capacity variants of the LC3 stock-ABI route.

The experiment never assigns production addresses or emits stock patch bytes.
It retains the same 11 external runtime imports and the five-object read-only
table policy while measuring compiler/linker reductions.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
G2 = ROOT.parents[2]
MANIFEST = ROOT / "service_audio_capacity_experiment.json"
ROUTE_BUILDER = ROOT / "build_service_audio_route_experiment.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load(ROUTE_BUILDER, "open_cfw_liblc3_capacity_route")
BuildError = R.BuildError

TABLE_REFERENCE_CONTRACT = {
    "by_type": {"R_ARM_ABS32": 6},
    "by_symbol": {
        "lc3_band_lim": 2,
        "lc3_fft_twiddles_bf2": 1,
        "lc3_fft_twiddles_bf3": 1,
        "lc3_mdct_rot": 1,
        "lc3_mdct_win": 1,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BuildError(f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise BuildError(f"path escapes G2 root: {relative}") from error
    return path


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "relocatable": report["relocatable"],
        "sections": report["sections"],
        "roots": report["roots"],
        "imports": report["imports"],
        "relocations": {
            "total": report["relocations"]["total"],
            "records_sha256": report["relocations"]["records_sha256"],
            "table_code_references": report["relocations"][
                "table_code_references"],
        },
        "final_elf": report["synthetic_finalization"]["final_elf"],
        "relocation_application": report["synthetic_finalization"][
            "relocation_application"],
        "capacity": report["capacity"],
    }


def _helper_record(manifest: dict[str, Any]) -> dict[str, Any]:
    source = manifest["sources"]["aeabi_memcpy"]
    return {
        "name": "aeabi_memcpy",
        "path": source["path"],
        "sha256": source["sha256"],
        "license": "MIT",
        "object_size_budget": 4096,
    }


def _route_build(manifest: dict[str, Any], output: Path, profile: str,
                 flags: tuple[str, ...], *, gc_sections: bool = True,
                 lto: bool = False) -> dict[str, Any]:
    tools = manifest["profiles"][profile]["tools"]
    return R.build(
        config_path=resolve(manifest["route_config"]["path"]),
        output_dir=output, profile=profile,
        clang=tools["clang"], lld=tools["lld"],
        objcopy=tools["objcopy"], record=True,
        compiler_overrides=flags,
        additional_source_records=(_helper_record(manifest),),
        table_reference_contract=TABLE_REFERENCE_CONTRACT,
        object_budget_override=(1048576 if lto else None),
        bitcode_objects=lto, force_table_roots=lto,
        gc_sections=gc_sections,
    )


def build(*, manifest_path: Path = MANIFEST, output_dir: Path,
          profile: str, record: bool = False) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    if (manifest.get("schema_version"), manifest.get("mode")) != (
            1, "whole-address-capacity-qualified-unplaced"):
        raise BuildError("capacity experiment schema drift")
    if manifest.get("routing") != {
            "production_placement": False, "service_audio_routed": False,
            "firmware_image_emitted": False, "hardware_operations": False}:
        raise BuildError("capacity experiment gained production authority")
    if profile not in manifest["profiles"]:
        raise BuildError(f"unknown profile: {profile}")
    for name, source in manifest["sources"].items():
        path = resolve(source["path"])
        if not path.is_file() or sha256(path) != source["sha256"]:
            raise BuildError(f"{name} source pin drift")
    route_config = resolve(manifest["route_config"]["path"])
    if sha256(route_config) != manifest["route_config"]["sha256"]:
        raise BuildError("route config pin drift")

    output_dir.mkdir(parents=True, exist_ok=True)
    accepted: dict[str, Any] = {}
    for name, flags in (
            ("oz_gc", ("-Oz",)),
            ("oz_gc_constant_merge", ("-Oz", "-fmerge-all-constants"))):
        report = _route_build(
            manifest, output_dir / name, profile, flags)
        accepted[name] = _summary(report)

    rejected: dict[str, Any] = {}
    for name, flags, gc_sections, lto in (
            ("oz_without_gc", ("-Oz",), False, False),
            ("oz_lto", ("-Oz", "-flto"), True, True)):
        try:
            _route_build(
                manifest, output_dir / name, profile, flags,
                gc_sections=gc_sections, lto=lto)
        except Exception as error:  # the exact fail-closed reason is pinned
            rejected[name] = {
                "accepted": False,
                "reason": str(error),
            }
        else:
            raise BuildError(f"{profile}: rejected variant unexpectedly built: {name}")

    oz = accepted["oz_gc"]
    merged = accepted["oz_gc_constant_merge"]
    if ([row["size"] for row in oz["sections"].values()] !=
            [row["size"] for row in merged["sections"].values()]):
        raise BuildError("constant merging unexpectedly changed section sizes")
    if oz["imports"] != manifest["required_runtime_imports"]:
        raise BuildError("size build changed the 11-binding boundary")
    application = {
        "selected_variant": "oz_gc",
        "section_gc_enabled": True,
        "constant_merging_selected": False,
        "constant_merging_size_delta": 0,
        "lto_selected": False,
        "production_placement": False,
    }
    report = {
        "schema_version": 1,
        "profile": profile,
        "accepted": accepted,
        "rejected": rejected,
        "selection": application,
        "routing": manifest["routing"],
    }
    expected = manifest["profiles"][profile].get("expected_report_sha256")
    if not record and canonical_sha256(report) != expected:
        raise BuildError(f"{profile}: capacity experiment receipt drift")
    temporary = output_dir / ".build-report.json.tmp"
    temporary.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    os.replace(temporary, output_dir / "build-report.json")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "build-service-capacity")
    parser.add_argument("--profile", choices=("apple-clang", "linux-clang"),
                        default="apple-clang")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    report = build(
        manifest_path=args.manifest.resolve(),
        output_dir=args.output_dir.resolve(), profile=args.profile,
        record=args.record)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
