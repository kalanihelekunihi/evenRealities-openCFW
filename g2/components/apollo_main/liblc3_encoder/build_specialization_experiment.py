#!/usr/bin/env python3
"""Build evidence-bounded, unplaced liblc3 encoder specializations.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
G2_ROOT = COMPONENT_ROOT.parents[2]
BASELINE_BUILDER = COMPONENT_ROOT / "build_component.py"
SPECIALIZED_XIP = COMPONENT_ROOT / "specialized_xip.py"
DEFAULT_CONFIG = COMPONENT_ROOT / "specialization_experiment.json"


def _load_baseline_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_baseline_builder", BASELINE_BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load baseline liblc3 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = _load_baseline_builder()
BuildError = B.BuildError


def _load_specialized_xip():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_specialized_xip", SPECIALIZED_XIP
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load specialized liblc3 XIP policy")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


X = _load_specialized_xip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    relocations = receipt["relocations"]
    return {
        "linked_object": receipt["linked_object"],
        "artifacts": receipt["artifacts"],
        "roots": receipt["roots"],
        "retained_imports": receipt["retained_imports"],
        "global_function_count": receipt["global_function_count"],
        "relocations": {
            key: relocations[key] for key in (
                "total", "by_type", "by_section", "external_by_symbol",
                "records_sha256")
        },
    }


def pinned_table_policy(policy: dict[str, Any]) -> dict[str, Any]:
    relocations = policy["relocations"]
    return {
        key: policy[key] for key in (
            "classification", "conversion", "pre_policy_object",
            "post_policy_object", "pre_policy_allocated_writable_sections",
            "post_policy_allocated_writable_sections", "runtime_copy_bytes",
            "runtime_writable_bytes", "table_symbols")
    } | {
        "relocations": {
            key: relocations[key] for key in (
                "total", "by_type", "by_section", "external_by_symbol",
                "records_sha256", "table_initializers",
                "table_code_references")
            if key not in {"table_initializers"}
        } | {
            "table_initializers": {
                key: relocations["table_initializers"][key]
                for key in ("count", "type", "target_section",
                            "records_sha256")
            }
        },
    }


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


def align_up(value: int, alignment: int) -> int:
    if alignment <= 0 or alignment & (alignment - 1):
        raise BuildError("invalid specialization section alignment")
    return (value + alignment - 1) & -alignment


def undefined_symbols(linked: Path) -> set[str]:
    payload, sections = B.parse_elf32(linked)
    symbols = B.parse_elf32_symbols(payload, sections)
    return {
        str(symbol["name"])
        for symbol in symbols
        if int(symbol["section_index"]) == 0 and str(symbol["name"])
    }


def layout(sections: dict[str, dict[str, Any]], start: int,
           limit: int) -> dict[str, Any]:
    cursor = start
    records: dict[str, dict[str, int]] = {}
    tail = "table_rodata" if "table_rodata" in sections else "data"
    for name, alignment in (("text", 16), ("rodata", 16), (tail, 8)):
        cursor = align_up(cursor, alignment)
        section_start = cursor
        cursor += int(sections[name]["size"])
        records[name] = {
            "runtime_start": section_start,
            "runtime_end_exclusive": cursor,
            "size": int(sections[name]["size"]),
            "alignment": alignment,
        }
    return {
        "sections": records,
        "aligned_span": cursor - start,
        "end_exclusive": cursor,
        "headroom": limit - start,
        "shortfall": max(0, cursor - limit),
        "fits_authenticated_headroom": cursor <= limit,
        "placement_assigned": False,
    }


def build_variant(*, name: str, variant: dict[str, Any],
                  baseline: dict[str, Any], admission: dict[str, Any],
                  placement: dict[str, int], table_policy: dict[str, Any],
                  clang: str, lld: str, objcopy: str, output_dir: Path,
                  record: bool) -> dict[str, Any]:
    defines = variant.get("compile_defines")
    if not isinstance(defines, list) or not defines or any(
            not isinstance(item, str) or
            re.fullmatch(r"-DLC3_PLUS(?:_HR)?=[01]", item) is None
            for item in defines):
        raise BuildError(f"{name}: malformed specialization defines")
    if name == "non_hr_only" and (
            defines != ["-DLC3_PLUS_HR=0"] or
            not variant.get("evidence_admitted")):
        raise BuildError("admitted non-HR specialization contract drift")
    if name == "standard_duration_only_counterfactual" and (
            defines != ["-DLC3_PLUS_HR=0", "-DLC3_PLUS=0"] or
            variant.get("evidence_admitted") or not variant.get("rejection")):
        raise BuildError("rejected duration specialization contract drift")

    profile_name = baseline["profile"]
    component = read_json(resolve(baseline["path"]))
    active = component["profiles"][profile_name]
    compiler_identity = B.compiler_version(clang)
    linker_identity = B._linker_version(lld)
    if not compiler_identity.startswith(active["reviewed_compiler_version_prefix"]):
        raise BuildError("specialization compiler differs from reviewed profile")
    if not linker_identity.startswith(active["reviewed_linker_version_prefix"]):
        raise BuildError("specialization linker differs from reviewed profile")

    builtin_include = B.compiler_builtin_include_dir(clang)
    hermetic = B.hermetic_compiler_arguments(builtin_include)
    compile_flags = [*admission["target_profile"], *defines]
    compile_prefix = [clang, *hermetic, *compile_flags]
    for include_dir in component["include_dirs"]:
        compile_prefix.extend(("-I", include_dir))

    object_records: list[dict[str, Any]] = []
    cantunwind_rows = 0
    sources = B._source_records(admission)
    variant_dir = output_dir / name
    variant_dir.mkdir(parents=True, exist_ok=True)
    policy_record: dict[str, Any] | None = None
    finalization_record: dict[str, Any] | None = None
    pre_policy_bytes: bytes | None = None
    with tempfile.TemporaryDirectory(
            prefix=f"open-cfw-liblc3-{name}-") as temporary:
        temporary_path = Path(temporary)
        objects: list[Path] = []
        for source in sources:
            output = temporary_path / f"{source['name']}.o"
            B._run([*compile_prefix, "-c", source["path"], "-o", str(output)])
            budget = admission["object_size_budgets"].get(output.name)
            if not isinstance(budget, int) or output.stat().st_size > budget:
                raise BuildError(f"{name}:{output.name} exceeds admitted budget")
            rows = B._validate_cantunwind(output)
            cantunwind_rows += rows
            object_records.append({
                "name": output.name,
                "source": source["path"],
                "size": output.stat().st_size,
                "sha256": digest(output),
                "canonical_cantunwind_rows": rows,
            })
            objects.append(output)

        pre_policy = temporary_path / "liblc3_encoder.pre-policy.o"
        linked = temporary_path / "liblc3_encoder.relocatable.o"
        roots = component["roots"]
        policy_admitted = name == "non_hr_only"
        link_output = pre_policy if policy_admitted else linked
        linker_script = (resolve(table_policy["linker_script"]["path"])
                         if policy_admitted
                         else resolve(component["linker_script"]["path"]))
        B._run([
            lld, "-m", "armelf", "-r", "--gc-sections", "--build-id=none",
            f"--entry={roots[2]}",
            *(f"--undefined={root}" for root in roots),
            "-T", str(linker_script),
            "-o", str(link_output), *(str(path) for path in objects),
        ])
        if link_output.stat().st_size > admission["link_contract"][
                "qualification_relocatable_object_budget"]:
            raise BuildError(f"{name}: linked object exceeds admitted budget")
        admission_imports = set(admission[
            "allowed_external_runtime_relocations"])
        imports = undefined_symbols(link_output)
        if not imports or not imports.issubset(admission_imports):
            raise BuildError(
                f"{name}: specialization gained an unadmitted import")
        if policy_admitted:
            artifacts, applied = X.apply_readonly_policy(
                pre_policy, linked, builder=B, roots=roots,
                allowed_imports=imports, objcopy=objcopy,
            )
            link_report = applied.pop("link")
            policy_record = applied
            pre_policy_bytes = pre_policy.read_bytes()
        else:
            artifacts, link_report = B._validate_linked_object(
                linked, roots, imports)
        if undefined_symbols(linked) != imports:
            raise BuildError(f"{name}: specialization gained an unadmitted import")
        linked_bytes = linked.read_bytes()

        if policy_admitted:
            sizes = {
                "text": len(artifacts[".text"]),
                "rodata": len(artifacts[".rodata"]),
                "table_rodata": len(artifacts[X.TABLE_SECTION]),
            }
            proof = table_policy["qualification_finalizer"]
            proof_layout = X.qualification_layout(
                sizes, int(proof["synthetic_text_start"]))
            finalization_record = X.finalize_xip(
                linked, variant_dir / "qualification-final",
                builder=B, roots=roots, allowed_imports=imports,
                lld=lld, layout=proof_layout,
                runtime_bindings={key: int(value) for key, value in
                                  proof["synthetic_runtime_bindings"].items()},
            )

    linked_record = B._artifact_record(linked_bytes)
    artifact_records = {
        ("table_rodata" if section == X.TABLE_SECTION else section[1:]):
            B._artifact_record(payload)
        for section, payload in artifacts.items()
    }
    receipt = B._expected_receipt(
        linked_record, artifact_records, link_report
    )
    expected = variant.get("expected")
    if not record and pinned_receipt(receipt) != expected:
        raise BuildError(f"{name}: compiler/link receipt differs from pin")
    if name == "non_hr_only":
        assert policy_record is not None
        if not record and pinned_table_policy(policy_record) != variant.get(
                "expected_table_policy"):
            raise BuildError(f"{name}: immutable-table policy receipt differs from pin")
        if not record and finalization_record != variant.get(
                "expected_qualification_finalization"):
            raise BuildError(
                f"{name}: qualification finalization receipt differs from pin")

    baseline_receipt = component["profiles"][profile_name]["expected"]
    placed = layout(
        artifact_records,
        placement["current_core_end_exclusive"],
        placement["protected_update_record_start"],
    )
    tail = "table_rodata" if "table_rodata" in artifact_records else "data"
    deltas = {
        "text": baseline_receipt["artifacts"]["text"]["size"] -
            artifact_records["text"]["size"],
        "rodata": baseline_receipt["artifacts"]["rodata"]["size"] -
            artifact_records["rodata"]["size"],
        "data": baseline_receipt["artifacts"]["data"]["size"] -
            artifact_records[tail]["size"],
    }
    deltas["raw_total"] = sum(deltas.values())
    deltas["aligned_span"] = baseline["aligned_span"] - placed["aligned_span"]

    B.atomic_write(variant_dir / "liblc3_encoder.text.bin", artifacts[".text"])
    B.atomic_write(variant_dir / "liblc3_encoder.rodata.bin", artifacts[".rodata"])
    if name == "non_hr_only":
        assert pre_policy_bytes is not None
        B.atomic_write(
            variant_dir / "liblc3_encoder.table_rodata.relocatable.bin",
            artifacts[X.TABLE_SECTION],
        )
        B.atomic_write(
            variant_dir / "liblc3_encoder.pre-policy.o", pre_policy_bytes)
    else:
        B.atomic_write(
            variant_dir / "liblc3_encoder.data.bin", artifacts[".data"])
    B.atomic_write(
        variant_dir / "liblc3_encoder.relocatable.o", linked_bytes
    )
    return {
        "name": name,
        "compile_defines": defines,
        "evidence_admitted": bool(variant["evidence_admitted"]),
        **({"rejection": variant["rejection"]}
           if not variant["evidence_admitted"] else {}),
        "toolchain": {
            "compiler": clang,
            "compiler_version": compiler_identity,
            "linker": lld,
            "linker_version": linker_identity,
            "builtin_include_dir": str(builtin_include),
            "flags": [*hermetic, *compile_flags],
        },
        "objects": object_records,
        "canonical_cantunwind_rows_discarded": cantunwind_rows,
        "receipt": receipt,
        **({"immutable_table_policy": policy_record,
            "qualification_finalization": finalization_record}
           if name == "non_hr_only" else {}),
        "baseline_deltas": deltas,
        "candidate_layout": placed,
        "routing": {
            "placement_assigned": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
        },
    }


def build(*, config_path: Path, output_dir: Path, clang: str, lld: str,
          objcopy: str, record: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    if config.get("schema_version") != 1 or config.get("mode") != \
            "build-only-unplaced-specialization-experiment":
        raise BuildError("unsupported specialization experiment schema")
    routing = config.get("routing")
    if routing != {
        "placement_assigned": False,
        "service_audio_routed": False,
        "firmware_image_emitted": False,
        "hardware_operations": False,
    }:
        raise BuildError("specialization experiment gained routing or hardware state")
    baseline = config["baseline_component"]
    baseline_path = resolve(baseline["path"])
    if digest(baseline_path) != baseline["sha256"]:
        raise BuildError("baseline component hash drift")
    component = read_json(baseline_path)
    admission_path = resolve(component["admission"]["path"])
    if digest(admission_path) != component["admission"]["sha256"]:
        raise BuildError("encoder admission hash drift")
    admission = read_json(admission_path)
    table_policy = config.get("immutable_table_policy")
    if not isinstance(table_policy, dict) or table_policy.get("enabled_variant") != \
            "non_hr_only":
        raise BuildError("immutable-table policy variant drift")
    linker_ref = table_policy.get("linker_script")
    module_ref = table_policy.get("production_module")
    builder_ref = table_policy.get("builder")
    if not all(isinstance(reference, dict) for reference in
               (builder_ref, linker_ref, module_ref)):
        raise BuildError("immutable-table policy source references are malformed")
    for label, reference in (("specialized builder", builder_ref),
                             ("table linker", linker_ref),
                             ("XIP production module", module_ref)):
        path = resolve(reference["path"])
        if digest(path) != reference["sha256"]:
            raise BuildError(f"{label} hash drift")
    objcopy_identity = B._run([objcopy, "--version"]).splitlines()[0]
    if not objcopy_identity.startswith(
            table_policy["reviewed_objcopy_version_prefix"]):
        raise BuildError("objcopy differs from reviewed immutable-table profile")
    proof = table_policy.get("qualification_finalizer")
    if not isinstance(proof, dict) or proof.get("synthetic") is not True or \
            proof.get("production_placement") is not False or \
            proof.get("runtime_bindings_authenticated_for_stock") is not False:
        raise BuildError("qualification finalizer gained production authority")
    variants = config.get("variants")
    if set(variants or {}) != {
            "non_hr_only", "standard_duration_only_counterfactual"}:
        raise BuildError("specialization variant set drift")

    records = {
        name: build_variant(
            name=name, variant=variant, baseline=baseline,
            admission=admission, placement=config["authenticated_placement"],
            table_policy=table_policy, clang=clang, lld=lld,
            objcopy=objcopy,
            output_dir=output_dir, record=record,
        )
        for name, variant in variants.items()
    }
    report = {
        "schema_version": 1,
        "name": config["name"],
        "target": config["target"],
        "mode": config["mode"],
        "config": {"path": config_path.name, "sha256": digest(config_path)},
        "baseline": {
            "path": baseline["path"],
            "sha256": baseline["sha256"],
            "aligned_span": baseline["aligned_span"],
        },
        "service_audio_configuration": config["service_audio_configuration"],
        "dimensions": config["dimensions"],
        "immutable_table_policy": {
            "enabled_variant": "non_hr_only",
            "builder": builder_ref,
            "linker_script": linker_ref,
            "production_module": module_ref,
            "objcopy": objcopy,
            "objcopy_version": objcopy_identity,
            "production_placement": False,
        },
        "variants": records,
        "outcome": {
            "admitted_variant": "non_hr_only",
            "admitted_variant_fits_authenticated_headroom":
                records["non_hr_only"]["candidate_layout"][
                    "fits_authenticated_headroom"],
            "production_routed": False,
            "hardware_operations": False,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    B.atomic_write(
        output_dir / "build-report.json",
        (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8"),
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path,
                        default=COMPONENT_ROOT / "build-specialization")
    parser.add_argument("--clang", default="/usr/bin/clang")
    parser.add_argument("--lld", default="/opt/homebrew/bin/ld.lld")
    parser.add_argument(
        "--objcopy",
        default="/opt/homebrew/opt/llvm@22/bin/llvm-objcopy")
    parser.add_argument("--record", action="store_true",
                        help="print unpinned receipts; never edits the config")
    args = parser.parse_args()
    report = build(
        config_path=args.config.resolve(), output_dir=args.output_dir.resolve(),
        clang=args.clang, lld=args.lld, objcopy=args.objcopy,
        record=args.record,
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
