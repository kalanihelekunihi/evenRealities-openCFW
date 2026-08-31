#!/usr/bin/env python3
"""Authenticate the unplaced Apollo service_audio LC3 stock-ABI route.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
CONFIG = COMPONENT / "service_audio_route_experiment.json"
BUILDER = COMPONENT / "build_service_audio_route_experiment.py"
sys.path.insert(0, str(G2 / "tools"))

from apollo_overlay import decode_thumb_bl  # noqa: E402
import recover_apollo_embedded_source_paths as literal_tools  # noqa: E402


class RouteAuditError(RuntimeError):
    """Raised when the stock ABI or unplaced route contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RouteAuditError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RouteAuditError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise RouteAuditError(f"path escapes G2 root: {relative}") from error
    return path


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_route_audit_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RouteAuditError("cannot load route builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def image_slice(image: bytes, evidence: dict[str, Any],
                start: int, end: int) -> bytes:
    begin = start - int(evidence["run_base"]) + int(evidence["preamble_bytes"])
    finish = end - int(evidence["run_base"]) + int(evidence["preamble_bytes"])
    require(0 <= begin <= finish <= len(image),
            f"stock interval 0x{start:08X}..0x{end:08X} escapes image")
    return image[begin:finish]


def validate_static_config(config: dict[str, Any]) -> None:
    require(config.get("schema_version") == 1 and
            config.get("mode") == "software-route-qualified-unplaced",
            "route schema or mode drift")
    require(config.get("routing") == {
        "production_placement": False,
        "service_audio_routed": False,
        "firmware_image_emitted": False,
        "hardware_operations": False,
    }, "route experiment gained production or hardware authority")
    for label, reference in config["sources"].items():
        path = resolve(reference["path"])
        require(path.is_file() and sha256(path) == reference["sha256"],
                f"{label} source pin drift")
    admission = config["encoder_admission"]
    require(sha256(resolve(admission["path"])) == admission["sha256"],
            "encoder admission pin drift")
    require(config["object_size_budgets"] == {
        "adapter.o": 10000, "shim.o": 6000},
        "route object budgets drift")
    require(set(config["profiles"]) == {"apple-clang", "linux-clang"},
            "route profile set drift")


def validate_stock_evidence(stock: dict[str, Any], image: bytes
                            ) -> dict[str, Any]:
    official = stock["official_component"]
    require(len(image) == official["size"] and
            sha256_bytes(image) == official["sha256"],
            "official Apollo-main component drift")
    service = stock["service_object"]
    body = image_slice(image, official, service["start"],
                       service["end_exclusive"])
    require(len(body) == 2884 and sha256_bytes(body) == service["sha256"],
            "service_audio object boundary drift")

    entries = stock["entries"]
    require([(row["name"], row["address"], row["end_exclusive"],
              row["shim_root"]) for row in entries] == [
        ("service_audio_lc3_encoder_setup", 0x0057A926, 0x0057A940,
         "open_cfw_liblc3_service_audio_stock_setup"),
        ("SVC_Lc3EncodeMono", 0x0057A940, 0x0057AB78,
         "open_cfw_liblc3_service_audio_stock_encode"),
    ], "stock entry geometry or root mapping drift")
    entry_report = []
    for row in entries:
        payload = image_slice(
            image, official, row["address"], row["end_exclusive"])
        require(sha256_bytes(payload) == row["sha256"] and
                payload[:4].hex() == row["prologue_hex"],
                f"stock entry bytes drift: {row['name']}")
        entry_report.append({
            "name": row["name"], "address": row["address"],
            "size": len(payload), "sha256": sha256_bytes(payload),
            "prologue_hex": payload[:4].hex(),
            "shim_root": row["shim_root"],
        })

    contexts = stock["contexts"]
    require(contexts == [0x20106A7C, 0x201074C0, 0x20107F04, 0x20108948] and
            stock["context_end_exclusive"] == 0x2010938C and
            stock["slot_bytes"] == 2628 and
            stock["stock_configuration_bytes"] == 24 and
            stock["stock_encoder_pointer_offset"] == 24 and
            all(right - left == 2628 for left, right in zip(
                contexts, contexts[1:] + [stock["context_end_exclusive"]])),
            "stock context geometry drift")

    expected_cells = {
        0x0058F880: (0, [0x0058F576, 0x0058F7A0]),
        0x0058F884: (1, [0x0058F596, 0x0058F652, 0x0058F7A6]),
        0x0058F88C: (2, [0x0058F66C, 0x0058F85C]),
        0x0054F9A0: (3, [0x0054F4B2]),
        0x0057B3E4: (3, [0x0057AE96]),
    }
    observed_cells: dict[int, tuple[int, list[int]]] = {}
    for row in stock["context_literal_cells"]:
        address = int(row["address"])
        index = int(row["context_index"])
        raw = image_slice(image, official, address, address + 4)
        require(struct.unpack("<I", raw)[0] == contexts[index],
                f"context pointer drift at 0x{address:08X}")
        references = literal_tools.literal_references(image, address)
        require(references == row["references"],
                f"context literal reference closure drift at 0x{address:08X}")
        observed_cells[address] = (index, references)
    require(observed_cells == expected_cells,
            "context literal cell set drift")

    expected_ingress = {
        "service_audio_lc3_encoder_setup": [
            [0x0054F4B6, 0x0054F4B2, 3],
            [0x0058F7A2, 0x0058F7A0, 0],
            [0x0058F7A8, 0x0058F7A6, 1],
            [0x0058F85E, 0x0058F85C, 2],
        ],
        "SVC_Lc3EncodeMono": [
            [0x0057AEA4, 0x0057AE96, 3],
            [0x0058F582, 0x0058F576, 0],
            [0x0058F5A2, 0x0058F596, 1],
            [0x0058F65E, 0x0058F652, 1],
            [0x0058F678, 0x0058F66C, 2],
        ],
    }
    require(stock["ingress"] == expected_ingress,
            "stock ingress/context mapping drift")
    ingress_report: dict[str, list[dict[str, Any]]] = {}
    load_base = int(official["run_base"])
    runtime_end = load_base + len(image) - int(official["preamble_bytes"])
    for entry in entries:
        target = int(entry["address"])
        all_sites = [
            address for address in range(load_base, runtime_end - 3, 2)
            if literal_tools._thumb_bl_target(image, address) == target
        ]
        expected_rows = expected_ingress[entry["name"]]
        require(all_sites == [row[0] for row in expected_rows],
                f"whole-image ingress closure drift: {entry['name']}")
        rows = []
        for callsite, literal_ref, index in expected_rows:
            encoded = image_slice(image, official, callsite, callsite + 4)
            require(decode_thumb_bl(callsite, encoded) == target,
                    "stock ingress is not exact Thumb BL")
            matching_cells = [
                address for address, (cell_index, refs) in observed_cells.items()
                if cell_index == index and literal_ref in refs
            ]
            require(len(matching_cells) == 1,
                    "stock ingress has ambiguous context provenance")
            rows.append({
                "callsite": callsite, "instruction_hex": encoded.hex(),
                "instruction_sha256": sha256_bytes(encoded),
                "literal_reference": literal_ref,
                "literal_cell": matching_cells[0],
                "context_index": index,
                "context_address": contexts[index],
            })
        ingress_report[entry["name"]] = rows
    return {
        "service_object": {
            "start": service["start"],
            "end_exclusive": service["end_exclusive"],
            "size": len(body), "sha256": sha256_bytes(body),
        },
        "entries": entry_report,
        "ingress": ingress_report,
        "whole_image_setup_ingress_count": 4,
        "whole_image_encode_ingress_count": 5,
        "contexts": [
            {"index": index, "start": start,
             "end_exclusive": start + 2628}
            for index, start in enumerate(contexts)
        ],
        "contexts_nonoverlapping": True,
        "context_total_bytes": 10512,
    }


def _compare_build_directories(first: Path, second: Path) -> None:
    first_files = sorted(
        path.relative_to(first) for path in first.rglob("*") if path.is_file())
    second_files = sorted(
        path.relative_to(second) for path in second.rglob("*") if path.is_file())
    require(first_files == second_files,
            "deterministic route build artifact set drift")
    for relative in first_files:
        require((first / relative).read_bytes() == (second / relative).read_bytes(),
                f"deterministic route artifact bytes drift: {relative}")


def analyze(config_path: Path = CONFIG) -> dict[str, Any]:
    config = read_json(config_path)
    validate_static_config(config)
    stock_path = resolve(config["stock_evidence"]["official_component"]["path"])
    stock_report = validate_stock_evidence(
        config["stock_evidence"], stock_path.read_bytes())
    builder = load_builder()
    tools = {
        "apple-clang": "/usr/bin/clang",
        "linux-clang": "/opt/homebrew/opt/llvm@22/bin/clang",
    }
    lld = "/opt/homebrew/bin/ld.lld"
    objcopy = "/opt/homebrew/opt/llvm@22/bin/llvm-objcopy"
    profiles: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="opencfw-lc3-route-audit-") as temp:
        root = Path(temp)
        for profile, clang in tools.items():
            require(Path(clang).is_file() and Path(lld).is_file() and
                    Path(objcopy).is_file(),
                    f"{profile}: reviewed target tools unavailable")
            first_dir = root / profile / "first"
            second_dir = root / profile / "second"
            first = builder.build(
                config_path=config_path, output_dir=first_dir,
                profile=profile, clang=clang, lld=lld,
                objcopy=objcopy, record=False)
            second = builder.build(
                config_path=config_path, output_dir=second_dir,
                profile=profile, clang=clang, lld=lld,
                objcopy=objcopy, record=False)
            require(builder.pinned_report(first) == builder.pinned_report(second),
                    f"{profile}: deterministic route report drift")
            _compare_build_directories(first_dir, second_dir)
            summary = builder.expected_summary(first)
            require(summary == config["profiles"][profile]["expected"],
                    f"{profile}: expected summary drift")
            require(not summary["capacity"]["fits"] and
                    summary["capacity"]["shortfall"] > 0 and
                    first["synthetic_finalization"]["relocation_application"][
                        "output_relocations"] == 0 and
                    first["synthetic_finalization"]["relocation_application"][
                        "all_input_relocations_applied"],
                    f"{profile}: finalization/capacity outcome drift")
            profiles[profile] = summary | {
                "byte_reproducible_two_builds": True,
                "all_relocations_applied_at_synthetic_layout": True,
            }

    require(profiles["apple-clang"]["capacity"]["shortfall"] == 34084 and
            profiles["linux-clang"]["capacity"]["shortfall"] == 35204,
            "route-integrated residual capacity drift")
    return {
        "schema_version": 1,
        "status": "service-audio-stock-abi-route-qualified-unplaced",
        "config": {
            "path": str(config_path.relative_to(G2)),
            "sha256": sha256(config_path),
        },
        "source": config["sources"],
        "stock_abi": stock_report,
        "transition_contract": {
            "stock_configuration_bytes_copied_before_transition": 24,
            "stock_encoder_pointer_offset": 24,
            "stock_encoder_pointer_must_be_zero": True,
            "slot_derived_owner_tokens": [
                0x4C430001, 0x4C430002, 0x4C430003, 0x4C430004],
            "one_way_lazy_transition": True,
            "explicit_stock_setup_resets_codec": True,
            "failed_setup_restores_stock_header": True,
            "plan_query_reinitializes_encoder": False,
            "completed_prefix_preserved_on_provider_failure": True,
            "state_pcm_output_and_count_aliases_rejected": True,
        },
        "profiles": profiles,
        "routing": {
            "stock_entry_patch_kind": "Thumb-2 B.W tail branch",
            "stock_entry_patch_count": 2,
            "production_patch_bytes_emitted": False,
            "production_placement": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False,
            "remaining_blockers": [
                "The canonical Apple route closure exceeds authenticated append headroom by 34,084 bytes.",
                "The two veneer targets are synthetic until final text placement exists.",
                "Stock runtime bindings and final firmware relocation replay remain unassigned.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = analyze(args.config.resolve())
    print(json.dumps(report, sort_keys=True, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
