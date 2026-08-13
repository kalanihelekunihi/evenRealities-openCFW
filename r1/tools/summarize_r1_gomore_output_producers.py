#!/usr/bin/env python3
"""Validate every R1 GoMore copied-output producer and its semantic confidence.

This static parser closes the producer side of the 27-field output ABI. It signature-checks the
vendor orchestrator, every direct or transitive producer used by the map, and the initializer that
proves five copied fields are immutable defaults in production 2.2.6.0009. It never executes the
vendor engine, reads live SRAM, or emits captured health data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_output_abi import FIELDS, IMAGE_SHA256


ORCHESTRATOR = 0x0005FF94
DEFAULT_INITIALIZER = 0x00071714

# Half-open signature ranges. Function-end padding and literal pools are excluded where known.
EXPECTED_RANGE_SHA256 = {
    (0x0005FF94, 0x000605D8): "d2573a4fc69405a9add5f88e926952e47d0d023d2cb131b8f72f29bba3066e6b",
    (0x00060680, 0x00060960): "cfc99e785d7b1636fae425a7dcddd06623517bdfe0c63f2fb8e720899b52980f",
    (0x0005F4B6, 0x0005F56C): "994a48c19b1c037a5452fb4c88585b83316b2146714ce55461333d2bffae689d",
    (0x0005EF1C, 0x0005F264): "52cf34f55c31efbf523be0a4f19b9d494a98dcb66d50c87607d1297c8ed9a32c",
    (0x000610C8, 0x00061198): "3154f525b6128ebc7a019a960816ba9970b4b39520c8bbe445ec828156fd681c",
    (0x0005F56C, 0x0005FEB8): "3797942ee75b8057fbdaa273f83e50354bc7f8bfdd53ae886f8cfe36ebafd378",
    (0x00060B80, 0x00060DC4): "0dec1f0f7e82ea9bf2b674058b4d22cc83edd70df6e3fa587befdbdd496701c4",
    (0x00060DC4, 0x000610C8): "813e98e58af680a92540c7f3f7aef5a3006fac4128d833b34bba16e9185c778a",
    (0x00061198, 0x00061274): "68b3a91eb737bce81d8d21a654a8cd66ff36eeb6ba2a408c36a3527840b91178",
    (0x00061274, 0x0006138C): "fb1ab02813fb190cbcda5392a735bc02b2d190bbd5c69b206654a06794012913",
    (0x00071714, 0x000717A2): "3112c51e53dd2e756960eb870445b953280183300cc7b70a3c5ae25fc74940af",
    (0x00069834, 0x00069C50): "cc4afba99d15e84367104fbbc83935393babb701ac7ccf2b25ef3d65edb24bec",
    (0x00067558, 0x000675C0): "0406caf7a00a6e3ab130f369bfa4f066ae621460e9b1435d1a05f372969679f6",
    (0x000692E4, 0x000694EC): "52c822b00982222b0fa1fda2128df2e170ca05cc2282320c964c5b7f253ae27a",
    (0x00058B70, 0x00058C38): "87d08976835376549e5bab7e13da07212ebcff651fa99ebfcd78662bbe52c1b4",
    (0x0005C19C, 0x0005C3F8): "81b3a16a714e85a6f565b64fee9c44a2fce7577f92c087e828b7c44a1a3ae4b8",
    (0x0009413C, 0x0009424C): "bfac2d9309c795151b73cf4ac2d203003b0040159b277684a6703a33dc6bf45e",
    (0x00094590, 0x00094694): "e0ec2adb814118836f143c52750a75bc91ffc913845942ddab6de0f7f9a82fb8",
    (0x00059D9C, 0x00059E5C): "16660063394cee6ff6305311031dea38deae059964751c1eb6d27b5336e705da",
    (0x0005FEB8, 0x0005FF90): "b410e5328af75c7a9c643b6dea01f6ff4b39d6f61ffa3b8f84eb37037e3143d7",
    (0x000715F8, 0x00071610): "d06d66726a39ec72436360c5cb6369c7debffb7d4d96d4953e984d6e75b4e5f3",
    (0x00096E0C, 0x00096E70): "5765263eb6429fea97419299f2d56b3cf6b00ab76f78def9bf9ab05c1e00c1a4",
    (0x000721B4, 0x000722E4): "0a740d3ca5ee6e62fd531f6f2692ede67a3913f1b709287dd24ac28fdb18da3c",
    (0x00069F80, 0x00069FA4): "ed379d4a20f4d255e433e9350cd268653f9895a1dd8645dd721160ca683e3c66",
}

EXPECTED_DIRECT_BRANCHES = {
    0x0005FF94: [0x0009468A],
    0x00060680: [0x0005FFD2, 0x0005FFE2],
    0x0005F4B6: [0x0006007C, 0x00060092],
    0x0005EF1C: [0x000600DC, 0x000600F2],
    0x000610C8: [0x0006013A, 0x0006014C],
    0x0005F56C: [0x00060264, 0x0006028C],
    0x00060B80: [0x000603BA, 0x000603E4],
    0x00060DC4: [0x00060480, 0x00060498],
    0x00061198: [0x0006053C, 0x00060550],
    0x00061274: [0x0006059A, 0x000605B2],
    0x00069834: [0x00060746],
    0x000692E4: [0x0006757C],
    0x00058B70: [0x0006759E],
    0x0005FEB8: [0x000602E2, 0x000602FC],
    0x000715F8: [0x00071AA4],
    0x00096E0C: [0x0005FF6E],
    0x000721B4: [0x00096E50],
    0x00069F80: [0x0005FF76],
}


def producer(
    engine_offset: int,
    io_offset: int,
    direct: int,
    group: str,
    semantic: str,
    confidence: str,
    *,
    transitive: tuple[int, ...] = (),
    initial_raw_bits: int | None = None,
) -> dict[str, Any]:
    return {
        "engine_offset": engine_offset,
        "io_offset": io_offset,
        "direct_producer": direct,
        "transitive_producers": list(transitive),
        "group": group,
        "semantic": semantic,
        "confidence": confidence,
        "initial_raw_bits": initial_raw_bits,
    }


# Copy order matches 0x59d9c. Five initialization-only values have no post-initialization writer.
# Engine +0x182 is the low byte of a compiled estimator status, but its activation word has no
# writer, so the official stock value remains its initialized zero.
PRODUCERS = [
    producer(0x224, 0x58, 0x610C8, "sps_selector", "sps_selected_speed_candidate", "stock_diagnostic_and_dataflow"),
    producer(0x22C, 0x5C, 0x610C8, "sps_selector", "sps_selected_speed_source_code", "stock_diagnostic_and_dataflow"),
    producer(0x254, 0x48, 0x5F56C, "energy_model", "energy_total_kcal", "stock_diagnostic_and_dataflow"),
    producer(0x278, 0x4C, 0x5F56C, "energy_model", "energy_s_kcal", "stock_diagnostic_and_dataflow"),
    producer(0x27C, 0x50, 0x5F56C, "energy_model", "energy_a_kcal", "stock_diagnostic_and_dataflow"),
    producer(0x184, 0xA0, 0x60680, "optical_period_estimator", "respiratory_rate_candidate_breaths_per_minute", "algorithm_formula", transitive=(0x69834,)),
    producer(0x188, 0xA4, 0x60680, "optical_period_estimator", "respiratory_rate_confidence", "algorithm_formula", transitive=(0x69834,)),
    producer(0x2F5, 0x60, 0x60DC4, "sleep_stage", "sleep_stage_code", "algorithm_dataflow"),
    producer(0x2F6, 0x61, 0x60DC4, "sleep_stage", "sleep_stage_updated", "algorithm_dataflow"),
    producer(0x2F7, 0x62, 0x60DC4, "sleep_stage", "sleep_stage_ppg_request", "stock_consumer_and_dataflow"),
    producer(0x2C4, 0x68, 0x60B80, "sleep_interval", "sleep_interval_start_unix_seconds", "algorithm_dataflow", transitive=(0x67558, 0x692E4, 0x58B70)),
    producer(0x2C8, 0x6C, 0x60B80, "sleep_interval", "sleep_interval_end_unix_seconds", "algorithm_dataflow", transitive=(0x67558, 0x692E4, 0x58B70)),
    producer(0x2DE, 0x70, 0x60B80, "sleep_transition", "sleep_lifecycle_flags", "stock_consumer_and_dataflow", transitive=(0x5C19C,)),
    producer(0x2DF, 0x71, 0x60B80, "sleep_transition", "sleep_transition_reason_code", "algorithm_dataflow", transitive=(0x5C19C,)),
    producer(0x2E0, 0x72, 0x60B80, "sleep_interval", "sleep_interval_classification_code", "algorithm_dataflow", transitive=(0x67558, 0x692E4)),
    producer(0x2E1, 0x73, 0x60B80, "sleep_interval", "sleep_interval_reconciliation_code", "algorithm_dataflow", transitive=(0x67558, 0x58B70)),
    producer(0x2C2, 0x44, DEFAULT_INITIALIZER, "initialization_only", "dormant_initialization_zero", "exact_constant_purpose_unresolved", initial_raw_bits=0),
    producer(0x21A, 0x54, 0x5F4B6, "motion_classifier", "motion_step_cadence_per_minute", "stock_diagnostic_and_dataflow", transitive=(0x9413C,)),
    producer(0x219, 0x33, 0x5F4B6, "motion_classifier", "motion_classifier_state_code", "algorithm_dataflow", transitive=(0x9413C,)),
    producer(0x181, 0x80, DEFAULT_INITIALIZER, "initialization_only", "dormant_initialization_zero", "exact_constant_purpose_unresolved", initial_raw_bits=0),
    producer(0x182, 0x81, 0x69F80, "dormant_multivariate_estimator", "dormant_estimator_status_low_byte", "algorithm_dataflow", transitive=(0x5FEB8, 0x96E0C, 0x721B4)),
    producer(0x180, 0x82, DEFAULT_INITIALIZER, "initialization_only", "dormant_initialization_zero", "exact_constant_purpose_unresolved", initial_raw_bits=0),
    producer(0x300, 0x74, DEFAULT_INITIALIZER, "initialization_only", "dormant_initialization_one", "exact_constant_purpose_unresolved", initial_raw_bits=1),
    producer(0x301, 0x75, DEFAULT_INITIALIZER, "initialization_only", "dormant_initialization_zero", "exact_constant_purpose_unresolved", initial_raw_bits=0),
    producer(0x308, 0x78, 0x61274, "activity_accumulator", "activity_steps", "stock_diagnostic_and_dataflow", transitive=(0x61198,)),
    producer(0x310, 0x7E, 0x61274, "activity_accumulator", "activity_kcal", "stock_diagnostic_and_dataflow", transitive=(0x5F56C,)),
    producer(0x30C, 0x7C, 0x61274, "activity_accumulator", "activity_all_kcal", "stock_diagnostic_and_dataflow", transitive=(0x5F56C,)),
]


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected_digest in EXPECTED_RANGE_SHA256.items():
        actual_digest = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(
                f"unexpected producer range 0x{start:08x}...0x{end:08x}: {actual_digest}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual_digest,
        })

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    abi_coordinates = [(field["engine_offset"], field["io_offset"]) for field in FIELDS]
    producer_coordinates = [(item["engine_offset"], item["io_offset"]) for item in PRODUCERS]
    if producer_coordinates != abi_coordinates:
        raise ValueError("producer table does not exactly cover the output-copy ABI in copy order")
    if len(set(producer_coordinates)) != 27:
        raise ValueError("producer table contains duplicate coordinates")

    initialization_only = [item for item in PRODUCERS if item["group"] == "initialization_only"]
    if len(initialization_only) != 5 or any(
        item["initial_raw_bits"] is None for item in initialization_only
    ):
        raise ValueError("unexpected initialization-only producer coverage")
    if len(PRODUCERS) - len(initialization_only) != 22:
        raise ValueError("unexpected runtime-produced output count")

    fields = []
    for item in PRODUCERS:
        fields.append({
            **{
                key: value for key, value in item.items()
                if key not in {"engine_offset", "io_offset", "direct_producer", "transitive_producers"}
            },
            "engine_offset": f"0x{item['engine_offset']:03x}",
            "io_offset": f"0x{item['io_offset']:02x}",
            "direct_producer": f"0x{item['direct_producer']:08x}",
            "transitive_producers": [
                f"0x{address:08x}" for address in item["transitive_producers"]
            ],
        })

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "orchestrator": f"0x{ORCHESTRATOR:08x}",
        "default_initializer": f"0x{DEFAULT_INITIALIZER:08x}",
        "field_count": len(fields),
        "compiled_post_initialization_writer_field_count": 22,
        "stock_runtime_produced_field_count": 21,
        "initialization_only_field_count": 5,
        "fields": fields,
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "semantic_boundaries": {
            "s_and_a_kcal_prefix_expansions_proven": False,
            "sps_speed_domain_formula_supported": True,
            "sps_distance_unit_proven": False,
            "sps_copied_output_is_stock_zero_source_0": True,
            "respiratory_rate_algorithm_domain_proven": True,
            "respiratory_rate_stock_public_label_found": False,
            "respiratory_rate_clinically_validated": False,
            "motion_rate_unit_steps_per_minute_proven": True,
            "motion_state_walking_running_labels_proven": False,
            "sleep_stage_wire_labels_proven": True,
            "sleep_type_wire_labels_proven": True,
            "sleep_lifecycle_consumer_masks_proven": True,
            "sleep_interval_branch_semantics_proven": True,
            "sleep_transition_reason_human_labels_proven": False,
            "sleep_stage_classifier_publicly_exposed": False,
            "initialization_only_field_purposes_proven": False,
            "dormant_estimator_enable_has_stock_writer": False,
            "dormant_estimator_copied_status_is_stock_zero": True,
        },
        "safety": {
            "static_read_only": True,
            "live_sram_reader_exposed": False,
            "vendor_engine_execution_exposed": False,
            "algorithm_outputs_remain_raw": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
