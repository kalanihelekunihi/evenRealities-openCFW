#!/usr/bin/env python3
"""Build and synthetically finalize the bounded service_audio LC3 route.

This builder deliberately emits no stock-address XIP bytes and applies no
firmware patches.  It proves the complete shim/adapter/encoder relocation
closure at a deterministic synthetic layout and reports the remaining stock
capacity shortfall.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
G2_ROOT = COMPONENT_ROOT.parents[2]
CONFIG = COMPONENT_ROOT / "service_audio_route_experiment.json"
BASELINE_BUILDER = COMPONENT_ROOT / "build_component.py"
XIP_MODULE = COMPONENT_ROOT / "specialized_xip.py"
LINKER_SCRIPT = COMPONENT_ROOT / "data_policy_linker.ld"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = _load(BASELINE_BUILDER, "open_cfw_liblc3_route_baseline")
X = _load(XIP_MODULE, "open_cfw_liblc3_route_xip")
sys.path.insert(0, str(G2_ROOT / "tools"))
from apollo_overlay import decode_thumb_branch, encode_thumb_b_w  # noqa: E402

BuildError = B.BuildError
UNIQUE_ROOTS = [
    "open_cfw_liblc3_service_audio_stock_setup",
    "open_cfw_liblc3_service_audio_stock_encode",
]
# The current finalizer takes its ENTRY from index two.  Repeating the encode
# root does not retain extra code and keeps the existing reviewed module intact.
FINALIZER_ROOTS = [UNIQUE_ROOTS[0], UNIQUE_ROOTS[1], UNIQUE_ROOTS[1]]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(payload: bytes) -> dict[str, Any]:
    return {"size": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2_ROOT / relative).resolve()
    try:
        path.relative_to(G2_ROOT.resolve())
    except ValueError as error:
        raise BuildError(f"path escapes G2 root: {relative}") from error
    return path


def undefined_symbols(path: Path) -> set[str]:
    payload, sections = B.parse_elf32(path)
    symbols = B.parse_elf32_symbols(payload, sections)
    return {
        str(symbol["name"]) for symbol in symbols
        if int(symbol["section_index"]) == 0 and str(symbol["name"])
    }


def pinned_report(report: dict[str, Any]) -> dict[str, Any]:
    relocations = report["relocations"]
    finalization = report["synthetic_finalization"]
    return {
        "objects": report["objects"],
        "relocatable": report["relocatable"],
        "sections": report["sections"],
        "roots": report["roots"],
        "imports": report["imports"],
        "relocations": {
            key: relocations[key] for key in (
                "total", "by_type", "by_section", "external_by_symbol",
                "records_sha256", "table_initializers",
                "table_code_references")
            if key != "table_initializers"
        } | {
            "table_initializers": {
                key: relocations["table_initializers"][key]
                for key in ("count", "type", "target_section",
                            "records_sha256")
            }
        },
        "readonly_policy": report["readonly_policy"],
        "synthetic_finalization": {
            key: finalization[key] for key in (
                "mode", "layout", "runtime_bindings_authenticated_for_stock",
                "production_placement", "service_audio_routed",
                "firmware_image_emitted", "final_elf", "xip_artifacts",
                "relocation_application")
        },
        "entry_veneers": report["entry_veneers"],
        "capacity": report["capacity"],
    }


def expected_summary(report: dict[str, Any]) -> dict[str, Any]:
    pinned = pinned_report(report)
    encoded = json.dumps(
        pinned, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "pinned_report_sha256": hashlib.sha256(encoded).hexdigest(),
        "relocatable": report["relocatable"],
        "sections": report["sections"],
        "roots": report["roots"],
        "imports": report["imports"],
        "relocations": {
            "total": report["relocations"]["total"],
            "records_sha256": report["relocations"]["records_sha256"],
        },
        "final_elf": report["synthetic_finalization"]["final_elf"],
        "entry_veneers": report["entry_veneers"],
        "capacity": report["capacity"],
    }


def build(*, config_path: Path, output_dir: Path, profile: str,
          clang: str, lld: str, objcopy: str,
          record: bool = False,
          compiler_overrides: tuple[str, ...] = (),
          additional_source_records: tuple[dict[str, Any], ...] = (),
          table_reference_contract:
          dict[str, dict[str, int]] | None = None,
          object_budget_override: int | None = None,
          bitcode_objects: bool = False,
          force_table_roots: bool = False,
          gc_sections: bool = True,
          relocatable_output: Path | None = None,
          per_source_overrides:
          dict[str, tuple[str, ...]] | None = None) \
          -> dict[str, Any]:
    config = read_json(config_path)
    if config.get("schema_version") != 1 or config.get("mode") != \
            "software-route-qualified-unplaced":
        raise BuildError("unsupported service_audio route experiment schema")
    if config.get("routing") != {
            "production_placement": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False}:
        raise BuildError("route experiment gained production authority")
    if profile not in config.get("profiles", {}):
        raise BuildError(f"unknown route profile: {profile}")

    for label, reference in config["sources"].items():
        path = resolve(reference["path"])
        if digest(path) != reference["sha256"]:
            raise BuildError(f"{label} source pin drift")
    admission_path = resolve(config["encoder_admission"]["path"])
    if digest(admission_path) != config["encoder_admission"]["sha256"]:
        raise BuildError("encoder source admission pin drift")
    admission = read_json(admission_path)
    compiler_version = B.compiler_version(clang)
    linker_version = B._linker_version(lld)
    objcopy_version = B._run([objcopy, "--version"]).splitlines()[0]
    toolchain = config["profiles"][profile]["toolchain"]
    if not compiler_version.startswith(toolchain["compiler_version_prefix"]) or \
            not linker_version.startswith(toolchain["linker_version_prefix"]) or \
            not objcopy_version.startswith(toolchain["objcopy_version_prefix"]):
        raise BuildError(f"{profile}: reviewed toolchain identity drift")

    builtin = B.compiler_builtin_include_dir(clang)
    flags = [
        *B.hermetic_compiler_arguments(builtin),
        *admission["target_profile"], "-DLC3_PLUS_HR=0",
        *compiler_overrides,
    ]
    include_dirs = [
        "components/shared/liblc3/target_compat",
        "third_party/liblc3/include",
        "third_party/liblc3/src",
        "components/shared/liblc3",
    ]
    compile_prefix = [clang, *flags]
    for include in include_dirs:
        compile_prefix.extend(("-I", include))

    source_records = B._source_records(admission)
    for name in ("adapter", "shim"):
        reference = config["sources"][name]
        source_records.append({
            "name": name,
            "path": reference["path"],
            "sha256": reference["sha256"],
            "license": "MIT",
        })
    source_records.extend(additional_source_records)

    output_dir.mkdir(parents=True, exist_ok=True)
    objects_report: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="opencfw-lc3-route-") as temporary:
        temporary_path = Path(temporary)
        objects: list[Path] = []
        for source in source_records:
            source_path = resolve(source["path"])
            if digest(source_path) != source["sha256"]:
                raise BuildError(f"{source['name']}: source hash drift")
            output = temporary_path / f"{source['name']}.o"
            source_flags = (() if per_source_overrides is None else
                            per_source_overrides.get(source["name"], ()))
            B._run([*compile_prefix, *source_flags,
                    "-c", source["path"], "-o", str(output)])
            budget = admission["object_size_budgets"].get(
                output.name, config["object_size_budgets"].get(output.name))
            if budget is None:
                budget = source.get("object_size_budget")
            if object_budget_override is not None:
                budget = object_budget_override
            if not isinstance(budget, int) or output.stat().st_size > budget:
                raise BuildError(f"{output.name}: object budget exceeded")
            rows = [] if bitcode_objects else B._validate_cantunwind(output)
            objects_report.append({
                "name": output.name,
                "size": output.stat().st_size,
                "sha256": digest(output),
                "canonical_cantunwind_rows": rows,
            })
            objects.append(output)

        pre_policy = temporary_path / "service-route.pre-policy.o"
        relocatable = temporary_path / "service-route.relocatable.o"
        B._run([
            lld, "-m", "armelf", "-r",
            *(("--gc-sections",) if gc_sections else ()),
            "--build-id=none",
            f"--entry={UNIQUE_ROOTS[1]}",
            *(f"--undefined={root}" for root in UNIQUE_ROOTS),
            *(f"--undefined={name}" for name in
              (sorted(X.TABLE_SYMBOLS) if force_table_roots else ())),
            "-T", str(LINKER_SCRIPT), "-o", str(pre_policy),
            *(str(path) for path in objects),
        ])
        imports = undefined_symbols(pre_policy)
        allowed = set(admission["allowed_external_runtime_relocations"])
        if not imports or not imports.issubset(allowed):
            raise BuildError(
                "route link gained an unadmitted runtime import: "
                f"{sorted(imports - allowed)}")
        sections, policy = X.apply_readonly_policy(
            pre_policy, relocatable, builder=B, roots=FINALIZER_ROOTS,
            allowed_imports=imports, objcopy=objcopy,
            table_reference_contract=table_reference_contract)
        if undefined_symbols(relocatable) != imports:
            raise BuildError("route read-only conversion changed imports")
        if relocatable_output is not None:
            B.atomic_write(relocatable_output, relocatable.read_bytes())

        sizes = {
            "text": len(sections[".text"]),
            "rodata": len(sections[".rodata"]),
            "table_rodata": len(sections[X.TABLE_SECTION]),
        }
        synthetic = X.qualification_layout(
            sizes, int(config["synthetic_qualification"]["text_start"]))
        bindings = {key: int(value) for key, value in
                    config["synthetic_qualification"]["runtime_bindings"].items()}
        finalization = X.finalize_xip(
            relocatable, output_dir / "qualification-final", builder=B,
            roots=FINALIZER_ROOTS, allowed_imports=imports, lld=lld,
            layout=synthetic, runtime_bindings=bindings,
            table_reference_contract=table_reference_contract)

        root_offsets = policy["link"]["roots"]
        veneers = []
        for record in config["entry_veneers"]:
            root = record["root"]
            target = synthetic["text"]["start"] + root_offsets[root]["offset"]
            encoded = encode_thumb_b_w(int(record["stock_entry"]), target)
            if decode_thumb_branch(
                    int(record["stock_entry"]), encoded, link=False) != target:
                raise BuildError("synthetic entry veneer round trip failed")
            veneers.append({
                "stock_entry": int(record["stock_entry"]),
                "root": root,
                "synthetic_target": target,
                "kind": "Thumb-2 B.W tail branch",
                "encoded_hex": encoded.hex(),
            })

        current = int(config["capacity"]["current_core_end_exclusive"])
        limit = int(config["capacity"]["protected_update_record_start"])
        candidate = X.qualification_layout(sizes, current)
        capacity = {
            "current_core_end_exclusive": current,
            "protected_update_record_start": limit,
            "append_headroom": limit - current,
            "text_start": candidate["text"]["start"],
            "end_exclusive": candidate["table_rodata"]["end_exclusive"],
            "aligned_span_from_current_end":
                candidate["table_rodata"]["end_exclusive"] - current,
            "shortfall": max(
                0, candidate["table_rodata"]["end_exclusive"] - limit),
            "fits": candidate["table_rodata"]["end_exclusive"] <= limit,
            "placement_assigned": False,
        }
        section_report = {
            name: artifact(payload) for name, payload in (
                ("text", sections[".text"]),
                ("rodata", sections[".rodata"]),
                ("table_rodata", sections[X.TABLE_SECTION]))
        }
        report = {
            "schema_version": 1,
            "name": "liblc3_service_audio_route_build",
            "profile": profile,
            "mode": config["mode"],
            "objects": objects_report,
            "relocatable": artifact(relocatable.read_bytes()),
            "sections": section_report,
            "roots": policy["link"]["roots"],
            "imports": sorted(imports),
            "relocations": policy["relocations"],
            "readonly_policy": {
                key: policy[key] for key in (
                    "classification", "conversion", "pre_policy_object",
                    "post_policy_object", "runtime_copy_bytes",
                    "runtime_writable_bytes")
            },
            "synthetic_finalization": finalization,
            "entry_veneers": veneers,
            "capacity": capacity,
            "routing": config["routing"],
        }

    expected = config["profiles"][profile].get("expected")
    if not record and expected_summary(report) != expected:
        raise BuildError(f"{profile}: route build receipt differs from pin")
    B.atomic_write(
        output_dir / "build-report.json",
        (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--output-dir", type=Path,
                        default=COMPONENT_ROOT / "build-service-route")
    parser.add_argument("--profile", choices=("apple-clang", "linux-clang"),
                        default="apple-clang")
    parser.add_argument("--clang", default="/usr/bin/clang")
    parser.add_argument("--lld", default="/opt/homebrew/bin/ld.lld")
    parser.add_argument("--objcopy",
                        default="/opt/homebrew/opt/llvm@22/bin/llvm-objcopy")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    report = build(
        config_path=args.config.resolve(), output_dir=args.output_dir.resolve(),
        profile=args.profile, clang=args.clang, lld=args.lld,
        objcopy=args.objcopy, record=args.record)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
