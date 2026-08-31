#!/usr/bin/env python3
"""Audit and reproducibly build the bounded Apollo LC3 service-audio adapter.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/shared/liblc3"
APOLLO_COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
ADMISSION = APOLLO_COMPONENT / "service_audio_adapter_admission.json"
ADAPTER_C = COMPONENT / "runtime_liblc3_service_audio_adapter.c"
ADAPTER_H = COMPONENT / "runtime_liblc3_service_audio_adapter.h"
PROVIDER_C = COMPONENT / "runtime_liblc3_encoder_provider.c"
PROVIDER_H = COMPONENT / "runtime_liblc3_encoder_provider.h"
TARGET_COMPAT = COMPONENT / "target_compat"
UPSTREAM = G2 / "third_party/liblc3"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
ENCODER_SOURCES = tuple(
    UPSTREAM_SRC / f"{name}.c"
    for name in (
        "attdet", "bits", "bwdet", "energy", "lc3", "ltpf", "mdct",
        "sns", "spec", "tables", "tns",
    )
)
SPECIALIZATION = APOLLO_COMPONENT / "specialization_experiment.json"
PLACEMENT = APOLLO_COMPONENT / "placement_routing_proposal.json"
FUNCTIONS = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-11.c"
LLVM_ROOT = Path("/opt/homebrew/opt/llvm@22/bin")
LLVM_NM = LLVM_ROOT / "llvm-nm"
LLVM_SIZE = LLVM_ROOT / "llvm-size"
LLVM_READOBJ = LLVM_ROOT / "llvm-readobj"
LLD = Path("/opt/homebrew/bin/ld.lld")
TARGET_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffast-math",
    "-fshort-enums", "-ffreestanding", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
    "-Werror",
)
PROFILES = {
    "apple-clang": Path("/usr/bin/clang"),
    "linux-clang": LLVM_ROOT / "clang",
}
ADAPTER_ROOTS = (
    "open_cfw_liblc3_service_audio_state_init",
    "open_cfw_liblc3_service_audio_open",
    "open_cfw_liblc3_service_audio_encode",
    "open_cfw_liblc3_service_audio_close",
)
PROVIDER_IMPORTS = {
    "open_cfw_liblc3_encoder_provider_plan",
    "open_cfw_liblc3_encoder_provider_setup",
    "open_cfw_liblc3_encoder_provider_encode",
    "open_cfw_liblc3_encoder_provider_close",
}
RUNTIME_IMPORTS = {
    "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf", "fmaxf",
    "fminf", "memcpy", "memmove", "memset", "roundf", "sqrtf",
    "truncf",
}
UINT32_LIMIT = 1 << 32


class AdmissionError(RuntimeError):
    """Raised when the adapter evidence or deterministic build drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_stock_slot_layout(addresses: list[int], *, slot_bytes: int,
                               state_bytes: int, storage_offset: int,
                               storage_bytes: int) -> dict[str, Any]:
    require(len(addresses) == 4 and all(isinstance(value, int)
                                        for value in addresses),
            "stock-slot context set must contain four integer addresses")
    require(slot_bytes == state_bytes == 2628 and storage_offset == 28 and
            storage_bytes == 2600 and storage_offset + storage_bytes ==
            state_bytes, "stock-slot state geometry drift")
    intervals: list[dict[str, int]] = []
    prior_end = -1
    for index, start in enumerate(addresses):
        end = start + state_bytes
        storage_start = start + storage_offset
        encoder_start = (storage_start + 7) & ~7
        encoder_prefix = encoder_start - storage_start
        encoder_capacity = storage_bytes - encoder_prefix
        require(0 <= start < end <= UINT32_LIMIT,
                "stock-slot state interval overflows uint32")
        require(start % 4 == 0 and encoder_prefix in (0, 4) and
                encoder_start % 8 == 0 and encoder_capacity >= 2596,
                "stock-slot state/storage alignment phase drift")
        require(start >= prior_end, "stock-slot states overlap")
        if index:
            require(start == prior_end,
                    "authenticated stock slots are no longer contiguous")
        intervals.append({
            "index": index,
            "state_start": start,
            "state_end_exclusive": end,
            "state_bytes": state_bytes,
            "storage_start": storage_start,
            "storage_end_exclusive": end,
            "storage_bytes": storage_bytes,
            "encoder_start": encoder_start,
            "encoder_prefix_bytes": encoder_prefix,
            "encoder_capacity_bytes": encoder_capacity,
        })
        prior_end = end
    return {
        "contexts": intervals,
        "first_start": intervals[0]["state_start"],
        "end_exclusive": intervals[-1]["state_end_exclusive"],
        "total_state_bytes": state_bytes * len(intervals),
        "extra_writable_bytes_required": 0,
        "nonoverlapping": True,
        "encoder_storage_eight_byte_aligned": True,
        "minimum_encoder_capacity_bytes": min(
            row["encoder_capacity_bytes"] for row in intervals),
        "placement_kind": "authenticated-existing-stock-slots",
    }


def run(command: list[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True,
                          text=True).stdout


def symbols(path: Path) -> tuple[set[str], set[str]]:
    output = run([str(LLVM_NM), str(path)])
    defined = set(re.findall(r"^[0-9a-fA-F]+\s+[A-Za-z]\s+(\S+)$",
                             output, re.M))
    undefined = set(re.findall(r"^\s+U\s+(\S+)$", output, re.M))
    return defined, undefined


def sections(path: Path) -> dict[str, int]:
    output = run([str(LLVM_SIZE), "-A", str(path)])
    result: dict[str, int] = {}
    for line in output.splitlines():
        match = re.match(r"^(\S+)\s+(\d+)\s+\d+$", line)
        if match:
            result[match.group(1)] = int(match.group(2))
    return result


def relocations(path: Path) -> dict[str, Any]:
    output = run([str(LLVM_READOBJ), "--relocations", "--expand-relocs",
                  str(path)])
    section = ""
    record: dict[str, Any] | None = None
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        match = re.match(r"\s+Section \(\d+\) (\S+) \{", line)
        if match:
            section = match.group(1)
            continue
        if line.strip() == "Relocation {":
            record = {"section": section}
            continue
        if record is None:
            continue
        match = re.match(r"\s+Offset: (0x[0-9A-F]+)$", line)
        if match:
            record["offset"] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+Type: (\S+) \(\d+\)$", line)
        if match:
            record["type"] = match.group(1)
            continue
        match = re.match(r"\s+Symbol: (\S+) \(\d+\)$", line)
        if match:
            record["symbol"] = match.group(1)
            continue
        if line.strip() == "}" and {"section", "offset", "type", "symbol"} <= record.keys():
            records.append(record)
            record = None
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {
        "count": len(records),
        "by_type": dict(sorted(Counter(row["type"] for row in records).items())),
        "external_by_symbol": dict(sorted(Counter(
            row["symbol"] for row in records
            if row["symbol"] in PROVIDER_IMPORTS).items())),
        "records_sha256": hashlib.sha256(payload).hexdigest(),
    }


def compile_one(compiler: Path, source: Path, output: Path) -> None:
    run([
        str(compiler), *TARGET_FLAGS,
        "-I", str(TARGET_COMPAT), "-I", str(UPSTREAM_INCLUDE),
        "-I", str(UPSTREAM_SRC), "-I", str(COMPONENT),
        "-c", str(source), "-o", str(output),
    ])


def build_once(profile: str, compiler: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True)
    objects: list[Path] = []
    for index, source in enumerate((ADAPTER_C, PROVIDER_C, *ENCODER_SOURCES)):
        output = output_dir / f"{index:02d}-{source.stem}.o"
        compile_one(compiler, source, output)
        objects.append(output)
    adapter = objects[0]
    linked = output_dir / "service-audio-retained.o"
    run([
        str(LLD), "-m", "armelf", "-r", "--gc-sections",
        f"--entry={ADAPTER_ROOTS[0]}",
        *(f"--undefined={root}" for root in ADAPTER_ROOTS),
        "-o", str(linked), *(str(path) for path in objects),
    ])
    adapter_defined, adapter_undefined = symbols(adapter)
    linked_defined, linked_undefined = symbols(linked)
    section_sizes = sections(adapter)
    text_sections = {
        name.removeprefix(".text."): size
        for name, size in section_sizes.items()
        if name.startswith(".text.")
    }
    return {
        "compiler_version": run([str(compiler), "--version"]).splitlines()[0],
        "adapter_object": {
            "size": adapter.stat().st_size,
            "sha256": sha256(adapter),
            "text_size": sum(text_sections.values()),
            "text_sections": dict(sorted(text_sections.items())),
            "rodata_size": sum(size for name, size in section_sizes.items()
                               if name.startswith(".rodata")),
            "data_size": sum(size for name, size in section_sizes.items()
                             if name.startswith(".data")),
            "defined_entries": sorted(set(ADAPTER_ROOTS) & adapter_defined),
            "undefined_provider_entries": sorted(adapter_undefined),
            "relocations": relocations(adapter),
        },
        "retained_encoder_link": {
            "size": linked.stat().st_size,
            "sha256": sha256(linked),
            "defined_adapter_entries": sorted(set(ADAPTER_ROOTS) & linked_defined),
            "undefined_runtime_imports": sorted(linked_undefined),
        },
    }


def reproducible_profile(profile: str, compiler: Path,
                         directory: Path) -> dict[str, Any]:
    first = build_once(profile, compiler, directory / "first")
    second = build_once(profile, compiler, directory / "second")
    require(first == second, f"{profile}: nondeterministic build report")
    require((directory / "first/00-runtime_liblc3_service_audio_adapter.o").read_bytes() ==
            (directory / "second/00-runtime_liblc3_service_audio_adapter.o").read_bytes(),
            f"{profile}: adapter object bytes are nondeterministic")
    require((directory / "first/service-audio-retained.o").read_bytes() ==
            (directory / "second/service-audio-retained.o").read_bytes(),
            f"{profile}: retained link bytes are nondeterministic")
    return first


def build_profiles() -> dict[str, Any]:
    for tool in (LLVM_NM, LLVM_SIZE, LLVM_READOBJ, LLD, *PROFILES.values()):
        require(tool.is_file(), f"required reviewed tool unavailable: {tool}")
    with tempfile.TemporaryDirectory(prefix="opencfw-lc3-service-admission-") as tmp:
        directory = Path(tmp)
        return {
            profile: reproducible_profile(profile, compiler,
                                          directory / profile)
            for profile, compiler in PROFILES.items()
        }


def function_record(entry: str) -> dict[str, Any]:
    for line in FUNCTIONS.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["entry"] == entry:
            return record
    raise AdmissionError(f"authenticated function record missing: {entry}")


def evidence_report() -> dict[str, Any]:
    specialization = json.loads(SPECIALIZATION.read_text(encoding="utf-8"))
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))
    stock = specialization["service_audio_configuration"]
    svc = placement["evidence"]["service_audio"]
    mapper = function_record("0057a900")
    setup = function_record("0057a926")
    encode = function_record("0057a940")
    return {
        "stock_functions": {
            "pcm_width_mapper": {
                "start": int(mapper["entry"], 16),
                "bytes": mapper["body_bytes"], "sha256": mapper["body_sha256"],
            },
            "lazy_setup": {
                "start": int(setup["entry"], 16),
                "bytes": setup["body_bytes"], "sha256": setup["body_sha256"],
            },
            "encode_mono": {
                "start": int(encode["entry"], 16),
                "bytes": encode["body_bytes"], "sha256": encode["body_sha256"],
            },
        },
        "stock_service_object": {
            "start": svc["object_start"],
            "end_exclusive": svc["object_end_exclusive"],
            "size": svc["object_size"],
            "sha256": svc["object_sha256"],
        },
        "stock_contexts": {
            "addresses": stock["contexts"],
            "count": len(stock["contexts"]),
            "slot_bytes": stock["slot_bytes"],
            "header_bytes": stock["header_bytes"],
            "encoder_storage_bytes": stock["encoder_storage_bytes"],
            "field_offsets": stock["field_offsets"],
            "pointer_table_sha256": stock["pointer_evidence"]["table_sha256"],
        },
        "decompilation_slice": stock["decompilation_evidence"],
    }


def validate_admission(admission_path: Path, report: dict[str, Any]) -> None:
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    require(admission["schema_version"] == 1, "adapter admission schema drift")
    require(admission["name"] == "liblc3_service_audio_adapter_admission",
            "adapter admission name drift")
    evidence_payload = json.dumps(
        report["evidence"], sort_keys=True, separators=(",", ":")).encode()
    observed_contract = {
        "source": report["source"],
        "evidence_sha256": hashlib.sha256(evidence_payload).hexdigest(),
        "abi": report["abi"],
        "behavior": report["behavior"],
        "stock_slot_placement": report["stock_slot_placement"],
        "target_flags": report["target"]["flags"],
        "target_roots": report["target"]["roots"],
        "provider_imports": report["target"]["provider_imports"],
        "runtime_import_allowlist":
            report["target"]["runtime_import_allowlist"],
        "profiles": report["target"]["profiles"],
        "routing": report["routing"],
        "hardware_operations": report["hardware_operations"],
    }
    require(admission["expected"] == observed_contract,
            "adapter admission report or deterministic build drift")


def run_audit(admission_path: Path = ADMISSION,
              *, discover: bool = False) -> dict[str, Any]:
    evidence = evidence_report()
    profiles = build_profiles()
    stock = evidence["stock_contexts"]
    stock_slot_placement = validate_stock_slot_layout(
        stock["addresses"], slot_bytes=stock["slot_bytes"],
        state_bytes=2628, storage_offset=28,
        storage_bytes=stock["encoder_storage_bytes"])
    report = {
        "status": "liblc3-service-audio-adapter-admission",
        "source": {
            "implementation": {"path": str(ADAPTER_C.relative_to(G2)),
                               "size": ADAPTER_C.stat().st_size,
                               "sha256": sha256(ADAPTER_C)},
            "header": {"path": str(ADAPTER_H.relative_to(G2)),
                       "size": ADAPTER_H.stat().st_size,
                       "sha256": sha256(ADAPTER_H)},
            "provider_implementation_sha256": sha256(PROVIDER_C),
            "provider_header_sha256": sha256(PROVIDER_H),
            "license": "MIT",
        },
        "evidence": evidence,
        "abi": {
            "service_config_bytes": 24,
            "service_plan_bytes": 20,
            "encoder_storage_bytes": 2600,
            "adapter_state_arm32_bytes": 2628,
            "adapter_state_alignment": 4,
            "stock_address_phases_mod8": [0, 4],
            "maximum_encoder_alignment_prefix_bytes": 4,
            "minimum_encoder_capacity_bytes": 2596,
            "control_header_bytes": 28,
            "owner_offset_arm32": 4,
            "generation_offset_arm32": 8,
            "config_word_offset_arm32": 12,
            "channels_offset_arm32": 16,
            "channel_offset_arm32": 20,
            "bitrate_offset_arm32": 24,
            "storage_offset_arm32": 28,
            "stock_slot_bytes": 2628,
            "per_context_delta_bytes": 0,
            "four_context_delta_bytes": 0,
        },
        "behavior": {
            "pcm_width_bytes": [2, 4, 3, 4],
            "minimum_encoded_frame_bytes": 20,
            "pcm_sample_rate_argument": 0,
            "interleaved_frame_multiple_required": True,
            "selected_channel_offset_and_stride_preserved": True,
            "partial_output_bytes_reported_on_provider_failure": True,
            "provider_failure_invalidates_lifetime": True,
            "owner_token_required_for_encode_and_close": True,
            "single_executor_busy_fails_closed": True,
            "encoder_storage_retained_on_close": True,
            "configuration_encoding_lossless_for_provider_admitted_values": True,
            "transient_provider_view_rederived_per_operation": True,
            "encoder_reinitialized_during_encode": False,
            "plan_query_rederives_without_encoder_reinitialization": True,
        },
        "stock_slot_placement": stock_slot_placement,
        "target": {
            "flags": list(TARGET_FLAGS),
            "roots": list(ADAPTER_ROOTS),
            "provider_imports": sorted(PROVIDER_IMPORTS),
            "runtime_import_allowlist": sorted(RUNTIME_IMPORTS),
            "profiles": profiles,
        },
        "routing": {
            "software_boundary_implemented": True,
            "direct_stock_abi_compatible": False,
            "stock_contexts_fit_adapter_state": True,
            "stock_slot_placement_proven": True,
            "placement_assigned": True,
            "placement_scope": "writable-adapter-state-only",
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "remaining_software_prerequisites": [
                "The separately admitted stock-ABI shim must be placed and its two authenticated entry tail branches applied.",
                "The stock header contents require the shim's guarded one-way transition to compact adapter control before first use.",
                "Final production text/rodata placement, runtime bindings, relocation replay, and firmware patch emission remain unassigned.",
            ],
        },
        "hardware_operations": False,
    }
    if discover:
        return report
    validate_admission(admission_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, default=ADMISSION)
    parser.add_argument("--discover", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(args.admission, discover=args.discover),
                     sort_keys=True, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
