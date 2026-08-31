#!/usr/bin/env python3
"""Audit the evidence boundary and size result of liblc3 specialization.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2))

from tools import analyze_g2_liblc3_encoder_placement as placement_audit  # noqa: E402
from tools import analyze_g2_pt_protocol_source as pt_audit  # noqa: E402


MANIFEST = (
    G2 / "components/apollo_main/liblc3_encoder/specialization_experiment.json"
)
UPSTREAM_LC3 = G2 / "third_party/liblc3/src/lc3.c"
PROVIDER = G2 / "components/shared/liblc3/runtime_liblc3_encoder_provider.c"


class SpecializationError(RuntimeError):
    """Raised when specialization evidence or rejected-state bounds drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpecializationError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SpecializationError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise SpecializationError(f"path escapes G2 root: {relative}") from error
    return path


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and alignment & (alignment - 1) == 0,
            "invalid section alignment")
    return (value + alignment - 1) & -alignment


def image_slice(image: bytes, start: int, size: int) -> bytes:
    run_base = 0x00438000
    preamble = 32
    offset = start - run_base + preamble
    require(0 <= offset <= offset + size <= len(image),
            f"runtime interval at 0x{start:08X} escapes official component")
    return image[offset:offset + size]


def _context_evidence(config: dict[str, Any], image: bytes) -> dict[str, Any]:
    service = config["service_audio_configuration"]
    pointers = service["pointer_evidence"]
    table = image_slice(image, pointers["table_address"], pointers["table_size"])
    require(sha256_bytes(table) == pointers["table_sha256"],
            "service LC3 context table hash drift")
    values = list(struct.unpack("<IIII", table))
    contexts = service["contexts"]
    require([values[index] for index in (0, 1, 3)] == contexts[:3],
            "first three service LC3 contexts drift")
    require(values[2] == 0x007639F0,
            "interleaved non-context pointer-table cell drift")
    for cell in pointers["fourth_context_literal_cells"]:
        raw = image_slice(image, cell, 4)
        require(sha256_bytes(raw) == pointers["fourth_context_literal_sha256"] and
                struct.unpack("<I", raw)[0] == contexts[3],
                "fourth service LC3 context literal drift")
    next_raw = image_slice(image, pointers["next_allocation_literal_cell"], 4)
    require(struct.unpack("<I", next_raw)[0] == pointers["next_allocation_start"],
            "service LC3 next-allocation literal drift")
    require(all(right - left == service["slot_bytes"]
                for left, right in zip(
                    contexts, contexts[1:] + [pointers["next_allocation_start"]])) and
            service["slot_bytes"] == service["header_bytes"] +
            service["encoder_storage_bytes"],
            "service LC3 slot geometry drift")

    prior = pt_audit.LC3_SETUP_EVIDENCE
    require(prior["fixed_context_starts"] == contexts and
            prior["fixed_context_slot_bytes"] == service["slot_bytes"] and
            prior["fixed_context_header_bytes"] == service["header_bytes"] and
            prior["fixed_context_storage_bytes"] ==
            service["encoder_storage_bytes"] and
            prior["configuration_initialization"] == service["initialization"] ==
            "runtime-provided; statically unproven",
            "prior authenticated service-context boundary drift")

    decomp = service["decompilation_evidence"]
    source = resolve(decomp["path"]).read_text(encoding="utf-8")
    begin = source.index(decomp["start_marker"])
    end = source.index(decomp["end_marker"], begin)
    selected = source[begin:end].encode("utf-8")
    require(len(selected) == decomp["slice_bytes"] and
            sha256_bytes(selected) == decomp["slice_sha256"],
            "service LC3 decompilation evidence drift")
    normalized = re.sub(r"\s+", " ", selected.decode("utf-8"))
    dynamic_tokens = (
        "FUN_00590e64(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 8))",
        "FUN_00590f78(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 0x14))",
        "FUN_00591374(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 8),0, param_5 + 0x1c)",
        "FUN_0059138a(*(undefined4 *)(param_5 + 0x18),*param_5,iVar5,uVar2,iVar3,param_3)",
    )
    require(all(token in normalized for token in dynamic_tokens),
            "dynamic service LC3 argument-flow evidence drift")
    require(service["field_offsets"] == {
        "pcm_format": 0,
        "frame_us": 4,
        "sample_rate_hz": 8,
        "channels_or_stride": 12,
        "channel_offset": 16,
        "bitrate_bps": 20,
        "encoder": 24,
        "storage": 28,
    }, "service LC3 header field map drift")
    require(set(service["runtime_unproven"]) == {
        "pcm_format", "frame_us", "sample_rate_hz", "channels_or_stride",
        "channel_offset", "bitrate_bps",
    }, "runtime-unproven LC3 dimension set drift")
    return {
        "contexts": [f"0x{value:08X}" for value in contexts],
        "slot_bytes": service["slot_bytes"],
        "header_bytes": service["header_bytes"],
        "encoder_storage_bytes": service["encoder_storage_bytes"],
        "known": service["known"],
        "runtime_unproven": service["runtime_unproven"],
        "initialization": service["initialization"],
        "decompilation_slice_sha256": decomp["slice_sha256"],
    }


def _safe_non_hr_boundary(config: dict[str, Any]) -> None:
    service = config["service_audio_configuration"]
    require(service["known"] == {
        "hrmode": False,
        "pcm_sample_rate_hz_argument": 0,
        "pcm_sample_rate_normalizes_to_encoded_rate": True,
    }, "known service LC3 configuration subset drift")
    lc3 = UPSTREAM_LC3.read_text(encoding="utf-8")
    provider = PROVIDER.read_text(encoding="utf-8")
    for token in (
        "return lc3_hr_frame_samples(false, dt_us, sr_hz);",
        "return lc3_hr_setup_encoder(false, dt_us, sr_hz, sr_pcm_hz, mem);",
    ):
        require(token in lc3, f"upstream non-HR wrapper drift: {token}")
    require("lc3_hr_frame_bytes(false, (int)config->frame_us" in provider and
            "encoder = lc3_setup_encoder((int)config->frame_us" in provider and
            "status = lc3_encode(provider->encoder" in provider,
            "bounded provider non-HR route drift")
    dimensions = config["dimensions"]
    require("safely removed" in dimensions["high_resolution_sample_rates"] and
            all("not specialized" in dimensions[name]
                for name in ("non_hr_sample_rates", "frame_durations",
                             "bitrate", "pcm_formats")),
            "specialization evidence dimension drift")


def _immutable_table_builder_boundary(config: dict[str, Any]) -> dict[str, Any]:
    policy = config["immutable_table_policy"]
    require(policy["enabled_variant"] == "non_hr_only",
            "immutable table policy variant drift")
    for key in ("builder", "linker_script", "production_module"):
        reference = policy[key]
        require(sha256(resolve(reference["path"])) == reference["sha256"],
                f"immutable table {key} hash drift")
    qualification = policy["qualification_finalizer"]
    require(qualification["synthetic"] is True and
            qualification["production_placement"] is False and
            qualification["runtime_bindings_authenticated_for_stock"] is False,
            "synthetic finalizer gained production authority")

    admitted = config["variants"]["non_hr_only"]
    table = admitted["expected_table_policy"]
    relocations = table["relocations"]
    require(admitted["expected"]["artifacts"]["table_rodata"] == {
        "size": 404,
        "sha256":
            "c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a",
    } and table["runtime_copy_bytes"] == 0 and
            table["runtime_writable_bytes"] == 0 and
            relocations["by_section"][".lc3_table_rodata"] == 78 and
            relocations["table_initializers"]["count"] == 78 and
            relocations["table_code_references"]["count"] == 12,
            "immutable table closure receipt drift")
    final = admitted["expected_qualification_finalization"]
    require(final["production_placement"] is False and
            final["service_audio_routed"] is False and
            final["firmware_image_emitted"] is False and
            final["relocation_application"] == {
                "input_relocations": 484,
                "input_table_initializers": 78,
                "input_table_code_references": 12,
                "output_relocations": 0,
                "all_input_relocations_applied": True,
                "table_initializers_verified_word_for_word": True,
                "xip_emission_after_validation": True,
            }, "qualification finalizer relocation receipt drift")
    return {
        "output_section": ".lc3_table_rodata",
        "table_bytes": 404,
        "table_object_count": 5,
        "initializer_relocations": 78,
        "code_references": 12,
        "post_policy_allocated_writable_sections": [],
        "qualification_output_relocations": 0,
        "qualification_table_xip_sha256":
            final["xip_artifacts"]["table_rodata"]["sha256"],
        "production_placement": False,
        "runtime_bindings_authenticated_for_stock": False,
    }


def _variant_size(name: str, variant: dict[str, Any],
                  baseline: dict[str, Any], placement: dict[str, int]) -> dict[str, Any]:
    receipt = variant["expected"]
    require(isinstance(receipt, dict), f"{name}: missing deterministic receipt")
    cursor = placement["current_core_end_exclusive"]
    ranges: dict[str, dict[str, int]] = {}
    tail = "table_rodata" if "table_rodata" in receipt["artifacts"] else "data"
    for section, alignment in (("text", 16), ("rodata", 16), (tail, 8)):
        cursor = align_up(cursor, alignment)
        start = cursor
        cursor += receipt["artifacts"][section]["size"]
        ranges[section] = {
            "start": start,
            "end_exclusive": cursor,
            "size": receipt["artifacts"][section]["size"],
        }
    baseline_receipt = baseline["receipt"]
    deltas = {
        "text": (baseline_receipt["artifacts"]["text"]["size"] -
                 receipt["artifacts"]["text"]["size"]),
        "rodata": (baseline_receipt["artifacts"]["rodata"]["size"] -
                   receipt["artifacts"]["rodata"]["size"]),
        "data": (baseline_receipt["artifacts"]["data"]["size"] -
                 receipt["artifacts"][tail]["size"]),
    }
    aligned_span = cursor - placement["current_core_end_exclusive"]
    require(set(receipt["retained_imports"]).issubset(
                set(baseline_receipt["retained_imports"])) and
            receipt["global_function_count"] <=
                baseline_receipt["global_function_count"],
            f"{name}: specialization expanded retained closure")
    return {
        "evidence_admitted": bool(variant["evidence_admitted"]),
        "compile_defines": variant["compile_defines"],
        "sections": ranges,
        "raw_total": sum(row["size"] for row in ranges.values()),
        "section_deltas": deltas,
        "raw_total_delta": sum(deltas.values()),
        "aligned_span": aligned_span,
        "aligned_span_delta": baseline["aligned_span"] - aligned_span,
        "headroom": placement["headroom"],
        "shortfall": max(0, cursor - placement["protected_update_record_start"]),
        "fits_authenticated_headroom":
            cursor <= placement["protected_update_record_start"],
        "relocations": receipt["relocations"]["total"],
        "retained_imports": receipt["retained_imports"],
        **({"rejection": variant["rejection"]}
           if not variant["evidence_admitted"] else {}),
    }


def run_audit() -> dict[str, Any]:
    config = read_json(MANIFEST)
    require(config["schema_version"] == 1 and config["mode"] ==
            "build-only-unplaced-specialization-experiment",
            "specialization manifest schema drift")
    routing = config["routing"]
    require(routing == {
        "placement_assigned": False,
        "service_audio_routed": False,
        "firmware_image_emitted": False,
        "hardware_operations": False,
    }, "specialization experiment gained routing or hardware state")

    baseline_ref = config["baseline_component"]
    baseline_path = resolve(baseline_ref["path"])
    require(sha256(baseline_path) == baseline_ref["sha256"],
            "baseline component hash drift")
    baseline_config = read_json(baseline_path)
    baseline_receipt = baseline_config["profiles"][baseline_ref["profile"]][
        "expected"]
    baseline = {
        "receipt": baseline_receipt,
        "aligned_span": baseline_ref["aligned_span"],
    }
    require(baseline_ref["aligned_span"] == 128752,
            "baseline aligned span drift")

    placement = placement_audit.run_audit()
    current = config["authenticated_placement"]
    require(current == {
        "current_core_end_exclusive": placement["placement"]["current_core_end"],
        "protected_update_record_start":
            placement["placement"]["protected_update_record"],
        "headroom": placement["placement"]["append_headroom"],
    }, "specialization placement basis drift")

    official_ref = placement_audit.read_json(
        placement_audit.PROPOSAL)["evidence"]["official_component"]
    official = resolve(official_ref["path"]).read_bytes()
    require(len(official) == official_ref["size"] and
            sha256_bytes(official) == official_ref["sha256"],
            "official component drift")
    context = _context_evidence(config, official)
    _safe_non_hr_boundary(config)
    table_builder = _immutable_table_builder_boundary(config)

    variants = config["variants"]
    require(set(variants) == {
        "non_hr_only", "standard_duration_only_counterfactual"},
        "specialization variant set drift")
    non_hr = _variant_size(
        "non_hr_only", variants["non_hr_only"], baseline, current
    )
    rejected = _variant_size(
        "standard_duration_only_counterfactual",
        variants["standard_duration_only_counterfactual"], baseline, current
    )
    require(non_hr["evidence_admitted"] and
            non_hr["section_deltas"] == {
                "text": 2368, "rodata": 24772, "data": 0} and
            non_hr["aligned_span"] == 101616 and
            non_hr["aligned_span_delta"] == 27136 and
            non_hr["shortfall"] == 30516 and
            not non_hr["fits_authenticated_headroom"],
            "admitted non-HR specialization size result drift")
    require(not rejected["evidence_admitted"] and
            "runtime frame_us fields are unproven" in rejected["rejection"] and
            rejected["aligned_span"] == 92176 and
            rejected["shortfall"] == 21076 and
            not rejected["fits_authenticated_headroom"],
            "rejected duration counterfactual drift")

    return {
        "status": "liblc3-encoder-specialization-insufficient",
        "service_audio_configuration": context,
        "authenticated_stock_calls":
            placement["routing"]["authenticated_stock_calls"],
        "baseline": {
            "text": baseline_receipt["artifacts"]["text"]["size"],
            "rodata": baseline_receipt["artifacts"]["rodata"]["size"],
            "data": baseline_receipt["artifacts"]["data"]["size"],
            "aligned_span": baseline_ref["aligned_span"],
            "headroom_shortfall":
                baseline_ref["aligned_span"] - current["headroom"],
        },
        "admitted_non_hr_only": non_hr,
        "rejected_duration_counterfactual": rejected,
        "immutable_table_builder": table_builder,
        "outcome": {
            "exact_runtime_configuration_derived": False,
            "safe_specialization_reduced_aligned_span": True,
            "safe_specialization_fits_authenticated_headroom": False,
            "remaining_shortfall": non_hr["shortfall"],
            "placement_assigned": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), sort_keys=True,
                     indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
