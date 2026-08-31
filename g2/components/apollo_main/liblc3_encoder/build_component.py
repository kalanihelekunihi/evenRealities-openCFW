#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the admitted, unplaced Apollo-main liblc3 encoder closure.

This component stops at a deterministic relocatable object.  It deliberately
does not assign firmware addresses, resolve target-runtime imports, patch stock
call sites, or emit an OTA image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
G2_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(G2_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402
    BuildError,
    SHF_ALLOC,
    SHF_EXECINSTR,
    SHF_WRITE,
    SHT_PROGBITS,
    SHT_REL,
    STB_GLOBAL,
    STT_FUNC,
    atomic_write,
    authenticated_cantunwind_companion_indexes,
    compiler_builtin_include_dir,
    compiler_version,
    hermetic_compiler_arguments,
    hermetic_compiler_environment,
    parse_elf32,
    parse_elf32_symbols,
    sha256,
)


RELOCATION_NAMES = {
    2: "R_ARM_ABS32",
    10: "R_ARM_THM_CALL",
    30: "R_ARM_THM_JUMP24",
    47: "R_ARM_THM_MOVW_ABS_NC",
    48: "R_ARM_THM_MOVT_ABS",
}
ARTIFACT_SECTIONS = {
    ".text": (SHT_PROGBITS, SHF_ALLOC | SHF_EXECINSTR, 16),
    ".rodata": (SHT_PROGBITS, SHF_ALLOC | 0x10, 16),
    ".data": (SHT_PROGBITS, SHF_ALLOC | SHF_WRITE, 8),
}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path} must contain a JSON object")
    return value


def _relative_g2(path: str) -> str:
    prefix = "g2/"
    return path[len(prefix):] if path.startswith(prefix) else path


def _resolve(relative: str) -> Path:
    path = (G2_ROOT / relative).resolve()
    try:
        path.relative_to(G2_ROOT.resolve())
    except ValueError as error:
        raise BuildError(f"path escapes G2 root: {relative}") from error
    return path


def _run(command: list[str], *, cwd: Path = G2_ROOT) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=hermetic_compiler_environment(),
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise BuildError(detail or f"command failed: {command[0]}")
    return completed.stdout


def _linker_version(lld: str) -> str:
    output = _run([lld, "--version"])
    lines = output.splitlines()
    if not lines:
        raise BuildError("linker returned no version")
    return lines[0].strip()


def _check_hash(path: Path, expected: str, label: str) -> None:
    if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
        raise BuildError(f"{label} SHA-256 pin is invalid")
    if not path.is_file() or _digest(path) != expected:
        raise BuildError(f"{label} differs from its SHA-256 pin")


def _snapshot_hashes() -> dict[str, str]:
    manifest = G2_ROOT / "third_party/liblc3/SNAPSHOT.sha256"
    records: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if relative in records or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise BuildError("liblc3 snapshot manifest is malformed")
        records[relative] = digest
    return records


def _source_records(admission: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = _snapshot_hashes()
    records: list[dict[str, Any]] = []
    for upstream_relative in admission["upstream_encoder_sources"]:
        relative = f"third_party/liblc3/{upstream_relative}"
        expected = snapshot.get(upstream_relative)
        if expected is None:
            raise BuildError(f"source absent from snapshot manifest: {upstream_relative}")
        path = _resolve(relative)
        _check_hash(path, expected, relative)
        records.append({
            "name": Path(upstream_relative).stem,
            "path": relative,
            "sha256": expected,
            "license": "Apache-2.0",
        })

    provider_relative = _relative_g2(admission["provider_source"])
    provider = _resolve(provider_relative)
    _check_hash(provider, admission["provider_source_sha256"], provider_relative)
    records.append({
        "name": "provider",
        "path": provider_relative,
        "sha256": admission["provider_source_sha256"],
        "license": "Apache-2.0",
    })
    names = [record["name"] for record in records]
    if len(names) != len(set(names)):
        raise BuildError("encoder source object names are not unique")
    return records


def _validate_cantunwind(object_path: Path) -> int:
    data, sections = parse_elf32(object_path)
    symbols = parse_elf32_symbols(data, sections)
    text_sections = [
        section for section in sections
        if int(section["type"]) == SHT_PROGBITS
        and int(section["flags"]) == (SHF_ALLOC | SHF_EXECINSTR)
        and int(section["size"])
    ]
    admitted: set[int] = set()
    for section in text_sections:
        companions = authenticated_cantunwind_companion_indexes(
            data, sections, symbols, section
        )
        if len(companions) != 1:
            raise BuildError(
                f"{object_path.name}:{section['name']} lacks canonical CANTUNWIND"
            )
        admitted.update(companions)
    observed = {
        int(section["index"])
        for section in sections
        if str(section["name"]).startswith(".ARM.exidx")
        and int(section["size"])
    }
    if observed != admitted:
        raise BuildError(f"{object_path.name} has unreviewed unwind sections")
    return len(admitted)


def _section(sections: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [section for section in sections if section["name"] == name]
    if len(matches) != 1:
        raise BuildError(f"expected one {name} section, observed {len(matches)}")
    return matches[0]


def _relocation_report(
    data: bytes,
    sections: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    allowed_imports: set[str],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for section in sections:
        if int(section["type"]) != SHT_REL or not int(section["size"]):
            continue
        if int(section["entry_size"]) != 8 or int(section["size"]) % 8:
            raise BuildError(f"malformed relocation section {section['name']}")
        target_index = int(section["info"])
        if target_index >= len(sections):
            raise BuildError(f"relocation target is invalid: {section['name']}")
        target = str(sections[target_index]["name"])
        if target not in ARTIFACT_SECTIONS:
            raise BuildError(f"relocation targets unadmitted section {target}")
        for cursor in range(0, int(section["size"]), 8):
            offset, information = struct.unpack_from(
                "<II", data, int(section["offset"]) + cursor
            )
            kind = information & 0xFF
            symbol_index = information >> 8
            if kind not in RELOCATION_NAMES or symbol_index >= len(symbols):
                raise BuildError("linked object gained an unadmitted relocation")
            symbol = symbols[symbol_index]
            records.append({
                "section": target,
                "offset": offset,
                "type": RELOCATION_NAMES[kind],
                "symbol": str(symbol["name"]),
                "external": int(symbol["section_index"]) == 0,
            })

    external = Counter(
        record["symbol"] for record in records if record["external"]
    )
    if set(external) != allowed_imports or any(count < 1 for count in external.values()):
        raise BuildError("retained external relocation closure differs from admission")
    return {
        "total": len(records),
        "by_type": dict(sorted(Counter(record["type"] for record in records).items())),
        "by_section": dict(sorted(Counter(record["section"] for record in records).items())),
        "external_by_symbol": dict(sorted(external.items())),
        "records_sha256": sha256(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
    }


def _validate_linked_object(
    linked: Path,
    roots: list[str],
    allowed_imports: set[str],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    data, sections = parse_elf32(linked)
    symbols = parse_elf32_symbols(data, sections)
    artifacts: dict[str, bytes] = {}
    for name, (expected_type, expected_flags, expected_alignment) in ARTIFACT_SECTIONS.items():
        section = _section(sections, name)
        if (
            int(section["type"]) != expected_type
            or int(section["flags"]) != expected_flags
            or int(section["alignment"]) != expected_alignment
            or not int(section["size"])
        ):
            raise BuildError(f"linked section contract changed: {name}")
        start = int(section["offset"])
        artifacts[name] = data[start:start + int(section["size"])]

    unexpected_allocated = [
        str(section["name"])
        for section in sections
        if int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
        and str(section["name"]) not in ARTIFACT_SECTIONS
    ]
    if unexpected_allocated:
        raise BuildError(f"linked object has unexpected allocated sections: {unexpected_allocated}")

    undefined = sorted(
        str(symbol["name"])
        for symbol in symbols
        if int(symbol["section_index"]) == 0 and str(symbol["name"])
    )
    if set(undefined) != allowed_imports or len(undefined) != len(allowed_imports):
        raise BuildError(f"retained imports differ from admission: {undefined}")

    text_index = int(_section(sections, ".text")["index"])
    root_records: dict[str, dict[str, int]] = {}
    for root in roots:
        matches = [
            symbol for symbol in symbols
            if symbol["name"] == root
            and int(symbol["binding"]) == STB_GLOBAL
            and int(symbol["type"]) == STT_FUNC
            and int(symbol["section_index"]) == text_index
        ]
        if len(matches) != 1:
            raise BuildError(f"provider root ABI changed: {root}")
        root_records[root] = {
            "offset": int(matches[0]["value"]) & ~1,
            "size": int(matches[0]["size"]),
        }

    relocation_report = _relocation_report(
        data, sections, symbols, allowed_imports
    )
    global_functions = sorted(
        str(symbol["name"])
        for symbol in symbols
        if int(symbol["binding"]) == STB_GLOBAL
        and int(symbol["type"]) == STT_FUNC
        and int(symbol["section_index"]) == text_index
    )
    return artifacts, {
        "roots": root_records,
        "retained_imports": undefined,
        "global_functions": global_functions,
        "global_function_count": len(global_functions),
        "relocations": relocation_report,
    }


def _artifact_record(payload: bytes) -> dict[str, Any]:
    return {"size": len(payload), "sha256": sha256(payload)}


def _expected_receipt(
    linked_record: dict[str, Any],
    artifact_records: dict[str, dict[str, Any]],
    link_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "linked_object": linked_record,
        "artifacts": artifact_records,
        "roots": link_report["roots"],
        "retained_imports": link_report["retained_imports"],
        "global_function_count": link_report["global_function_count"],
        "relocations": link_report["relocations"],
    }


def build(
    *,
    config_path: Path,
    output_dir: Path,
    clang: str,
    lld: str,
    profile: str,
    record: bool = False,
) -> dict[str, Any]:
    config = _read_json(config_path)
    if config.get("schema_version") != 1 or config.get("mode") != \
            "build-only-unplaced-relocatable":
        raise BuildError("unsupported liblc3 encoder component schema or mode")
    if config.get("placement") is not None or config.get("stock_patch_sites") != [] or \
            config.get("service_audio_routed") or config.get("hardware_operations"):
        raise BuildError("build-only component gained placement, routing, or hardware state")
    profiles = config.get("profiles")
    if not isinstance(profiles, dict) or profile not in profiles:
        raise BuildError(f"unknown toolchain profile {profile!r}")
    active = profiles[profile]

    compiler_identity = compiler_version(clang)
    linker_identity = _linker_version(lld)
    if not compiler_identity.startswith(active["reviewed_compiler_version_prefix"]):
        raise BuildError("compiler version differs from reviewed profile")
    if not linker_identity.startswith(active["reviewed_linker_version_prefix"]):
        raise BuildError("linker version differs from reviewed profile")

    admission_relative = config["admission"]["path"]
    admission_path = _resolve(admission_relative)
    _check_hash(admission_path, config["admission"]["sha256"], "encoder admission")
    admission = _read_json(admission_path)
    if not admission.get("production_capable_source") or admission.get("overlay_routed"):
        raise BuildError("encoder admission source/routing state changed")
    roots = config["roots"]
    if roots != admission["provider_entries"] or len(set(roots)) != 4:
        raise BuildError("provider root set differs from admission")
    allowed_imports = set(admission["allowed_external_runtime_relocations"])
    if len(allowed_imports) != len(admission["allowed_external_runtime_relocations"]):
        raise BuildError("runtime import admission contains duplicates")

    linker_relative = config["linker_script"]["path"]
    linker_script = _resolve(linker_relative)
    _check_hash(linker_script, config["linker_script"]["sha256"], "linker script")
    source_records = _source_records(admission)
    target_flags = admission["target_profile"]
    include_dirs = config["include_dirs"]
    if not isinstance(target_flags, list) or not isinstance(include_dirs, list):
        raise BuildError("compile profile or include paths are malformed")

    builtin_include = compiler_builtin_include_dir(clang)
    hermetic_arguments = hermetic_compiler_arguments(builtin_include)
    compile_prefix = [clang, *hermetic_arguments, *target_flags]
    for include_dir in include_dirs:
        compile_prefix.extend(("-I", include_dir))

    object_records: list[dict[str, Any]] = []
    cantunwind_rows = 0
    with tempfile.TemporaryDirectory(prefix="open-cfw-liblc3-encoder-") as temporary:
        temporary_path = Path(temporary)
        objects: list[Path] = []
        for source in source_records:
            output = temporary_path / f"{source['name']}.o"
            _run([*compile_prefix, "-c", source["path"], "-o", str(output)])
            budget = admission["object_size_budgets"].get(output.name)
            if not isinstance(budget, int) or output.stat().st_size > budget:
                raise BuildError(f"{output.name} exceeds its admitted object budget")
            rows = _validate_cantunwind(output)
            cantunwind_rows += rows
            object_records.append({
                "name": output.name,
                "source": source["path"],
                "size": output.stat().st_size,
                "sha256": _digest(output),
                "canonical_cantunwind_rows": rows,
            })
            objects.append(output)

        linked = temporary_path / "liblc3_encoder.relocatable.o"
        link_command = [
            lld,
            "-m", "armelf",
            "-r",
            "--gc-sections",
            "--build-id=none",
            f"--entry={roots[2]}",
            *(f"--undefined={root}" for root in roots),
            "-T", linker_relative,
            "-o", str(linked),
            *(str(path) for path in objects),
        ]
        _run(link_command)
        linked_budget = admission["link_contract"][
            "qualification_relocatable_object_budget"
        ]
        if linked.stat().st_size > linked_budget:
            raise BuildError("retained relocatable object exceeds admitted budget")
        artifacts, link_report = _validate_linked_object(
            linked, roots, allowed_imports
        )
        linked_bytes = linked.read_bytes()

    linked_record = _artifact_record(linked_bytes)
    artifact_records = {
        name[1:]: _artifact_record(payload)
        for name, payload in artifacts.items()
    }
    receipt = _expected_receipt(linked_record, artifact_records, link_report)
    expected = active.get("expected")
    if not record and receipt != expected:
        raise BuildError("compiler/link output differs from the reviewed receipt")

    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(output_dir / "liblc3_encoder.text.bin", artifacts[".text"])
    atomic_write(output_dir / "liblc3_encoder.rodata.bin", artifacts[".rodata"])
    atomic_write(output_dir / "liblc3_encoder.data.bin", artifacts[".data"])
    atomic_write(output_dir / "liblc3_encoder.relocatable.o", linked_bytes)
    report = {
        "schema_version": 1,
        "name": config["name"],
        "target": config["target"],
        "mode": config["mode"],
        "profile": profile,
        "toolchain": {
            "compiler": clang,
            "compiler_version": compiler_identity,
            "linker": lld,
            "linker_version": linker_identity,
            "builtin_include_dir": str(builtin_include),
            "flags": [*hermetic_arguments, *target_flags],
        },
        "config": {"path": config_path.name, "sha256": _digest(config_path)},
        "admission": {
            "path": admission_relative,
            "sha256": config["admission"]["sha256"],
            "upstream_commit": admission["upstream_commit"],
            "license": admission["license"],
            "g2_0x59_source_attribution": admission["g2_0x59_source_attribution"],
        },
        "linker_script": {
            "path": linker_relative,
            "sha256": config["linker_script"]["sha256"],
        },
        "sources": source_records,
        "objects": object_records,
        "canonical_cantunwind_rows_discarded": cantunwind_rows,
        "linked_object": {
            "file": "liblc3_encoder.relocatable.o",
            **linked_record,
        },
        "artifacts": {
            name: {"file": f"liblc3_encoder.{name}.bin", **value}
            for name, value in artifact_records.items()
        },
        **link_report,
        "placement": {"assigned": False, "runtime_addresses": None},
        "routing": {
            "stock_patch_sites": [],
            "service_audio_routed": False,
            "firmware_image_emitted": False,
        },
        "hardware_operations": False,
    }
    atomic_write(
        output_dir / "build-report.json",
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=COMPONENT_ROOT / "component.json")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--profile", default="apple-clang")
    parser.add_argument("--clang")
    parser.add_argument("--lld")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    clang = args.clang or "/usr/bin/clang"
    lld = args.lld or shutil.which("ld.lld")
    if lld is None:
        print("error: ld.lld is required", file=sys.stderr)
        return 2
    output_dir = args.output_dir or COMPONENT_ROOT / "build" / args.profile
    try:
        report = build(
            config_path=args.config.resolve(),
            output_dir=output_dir.resolve(),
            clang=clang,
            lld=lld,
            profile=args.profile,
            record=args.record,
        )
    except (BuildError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
