#!/usr/bin/env python3
"""Recover EM9305 SDK functions from exact-neighbor link-order constraints."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Sequence

import analyze_em9305_sdk_discovery as discovery


EXPECTED_RANGE_COUNT = 36
EXPECTED_FUNCTION_COUNT = 46
EXPECTED_IDENTIFIED_BYTES = 2_116
EXPECTED_STATUS_COUNTS = {
    "sdk_archive_exact_link_order_resolved": 16,
    "sdk_archive_link_order_low_compared": 11,
    "sdk_archive_link_order_relocation_only": 10,
    "sdk_archive_symbol_identified_vendor_modified_same_size": 9,
}
EXPECTED_STATUS_BYTES = {
    "sdk_archive_exact_link_order_resolved": 784,
    "sdk_archive_link_order_low_compared": 88,
    "sdk_archive_link_order_relocation_only": 40,
    "sdk_archive_symbol_identified_vendor_modified_same_size": 1_204,
}
EXPECTED_MODIFIED = {
    0x0030_6F44: "LctrGetPeerMinUsedChan",
    0x0031_8168: "lctrCenSendPendingRspRptHandler",
    0x0031_8F2C: "lctrConnTxCompletedHandler",
    0x0032_0274: "lctrMstExtInitiateEndOp",
    0x0032_4FB4: "lctrReceivePeriodicSyncInd",
    0x0032_5324: "lctrRxConnEnq",
    0x0032_5A68: "lctrSendChanMapUpdateInd",
    0x0032_698C: "lctrSendRejectInd",
    0x0032_72D8: "lctrSetCisTest",
}
EXPECTED_EXACT_FUNCTIONS = 16
EXPECTED_EXACT_BYTES = 784
EXPECTED_COMBINED_EXACT_FUNCTIONS = 1_451
EXPECTED_COMBINED_EXACT_BYTES = 155_750
EXPECTED_COMBINED_EXACT_INTERVALS = 858
EXPECTED_PROVENANCE_IDENTIFIED_BYTES = 157_082
EXPECTED_PROVENANCE_IDENTIFIED_INTERVALS = 831
EXPECTED_NOP_AWARE_RANGE_COUNT = 120
EXPECTED_NOP_AWARE_FUNCTION_COUNT = 156
EXPECTED_NOP_AWARE_IDENTIFIED_BYTES = 9_818
EXPECTED_NOP_AWARE_ARCHIVE_BYTES = 9_698
EXPECTED_NOP_AWARE_STATUS_COUNTS = {
    "sdk_archive_exact_nop_aware_link_order_resolved": 34,
    "sdk_archive_nop_aware_link_order_low_compared": 48,
    "sdk_archive_nop_aware_link_order_relocation_only": 32,
    "sdk_archive_symbol_identified_vendor_modified_same_size_nop_aware": 29,
    "sdk_archive_symbol_identified_vendor_modified_size_delta": 13,
}
EXPECTED_NOP_AWARE_STATUS_BYTES = {
    "sdk_archive_exact_nop_aware_link_order_resolved": 774,
    "sdk_archive_nop_aware_link_order_low_compared": 480,
    "sdk_archive_nop_aware_link_order_relocation_only": 128,
    "sdk_archive_symbol_identified_vendor_modified_same_size_nop_aware": 4_496,
    "sdk_archive_symbol_identified_vendor_modified_size_delta": 3_940,
}
EXPECTED_ALL_LINK_ORDER_RANGES = 156
EXPECTED_ALL_LINK_ORDER_FUNCTIONS = 202
EXPECTED_ALL_LINK_ORDER_BYTES = 11_934
EXPECTED_VECTOR_HANDLER_FUNCTIONS = 4
EXPECTED_VECTOR_HANDLER_BYTES = 760
EXPECTED_VECTOR_HANDLER_STATUS_COUNTS = {
    "sdk_archive_exact_vector_resolved": 3,
    "sdk_archive_vector_identified_vendor_modified_size_delta": 1,
}
EXPECTED_VECTOR_HANDLER_STATUS_BYTES = {
    "sdk_archive_exact_vector_resolved": 574,
    "sdk_archive_vector_identified_vendor_modified_size_delta": 186,
}
EXPECTED_EM_HW_REPORT_SHA256 = "8c501926a8950b2086106144a03283eea7641143f4c4aeb57bc56496dcd3fd77"
EXPECTED_RADIO_REPORT_SHA256 = "e3bb729a1ee7c47b46cf84347e0b0cc3c94ece6d0c3d90cec390e757fb69f55f"
EXPECTED_EM_SYSTEM_REPORT_SHA256 = "b0f868849611b734c2a573f0c8373a4d4121572cdf6c625a73299bb996777708"
EXPECTED_INTERRUPT_HEADER_GIT_BLOB = "8514b28756c0aeac44134404d1222c190ff4bcee"
EXPECTED_INTERRUPT_HEADER_SHA256 = "87505b42608c7f81e47c528add31c8dccecba12ba03ab2cbb99727a8e25f2d8f"
EXPECTED_SHORT_PREFIX_FUNCTIONS = 6
EXPECTED_SHORT_PREFIX_BYTES = 24
EXPECTED_SHORT_PREFIX_NAMES = (
    "EMSystemStack_ReceiveStart",
    "EMSystemStack_ReceiveStop",
    "EMSystemStack_StartAdvertising",
    "EMSystemStack_StartScan_15_4",
    "EMSystemStack_TransmitStart",
    "EMSystemStack_TransmitStop",
)
EXPECTED_ALL_IDENTIFIED_PLACEMENTS = 212
EXPECTED_ALL_IDENTIFIED_PLACEMENT_BYTES = 12_718
EXPECTED_ALL_EXACT_FUNCTIONS = 1_494
EXPECTED_ALL_EXACT_BYTES = 157_122
EXPECTED_ALL_EXACT_INTERVALS = 875
EXPECTED_ALL_PROVENANCE_BYTES = 167_684
EXPECTED_ALL_PROVENANCE_INTERVALS = 879


class LinkOrderError(RuntimeError):
    """Raised when an authenticated link-order invariant changes."""


def merge_intervals(intervals: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def discover_placements(
    report: dict[str, Any],
    authoritative_functions: Sequence[dict[str, Any]],
    *,
    maximum_intervening_functions: int = 3,
) -> list[dict[str, Any]]:
    """Place archive symbols that exactly tile gaps between exact linked neighbors."""
    known = {item["address"]: item for item in authoritative_functions}
    known_intervals = sorted((item["address"], item["end"]) for item in known.values())
    definitions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for function in report["functions"]:
        definitions[function["name"]].append(function)
    functions = sorted(
        (items[0] for items in definitions.values() if len(items) == 1),
        key=lambda item: item["name"],
    )
    anchors = [
        index
        for index, function in enumerate(functions)
        if len(function["matches"]) == 1 and function["matches"][0] in known
    ]
    placements: list[dict[str, Any]] = []
    range_index = 0
    for left_index, right_index in zip(anchors, anchors[1:]):
        left = functions[left_index]
        right = functions[right_index]
        intervening = functions[left_index + 1:right_index]
        if not intervening or len(intervening) > maximum_intervening_functions:
            continue
        start = left["matches"][0] + left["size"]
        end = right["matches"][0]
        if start >= end or sum(item["size"] for item in intervening) != end - start:
            continue
        if any(range_start < end and start < range_end for range_start, range_end in known_intervals):
            continue
        range_index += 1
        address = start
        for function in intervening:
            if address in function["matches"]:
                status = "sdk_archive_exact_link_order_resolved"
            elif function["compared_byte_count"] == 0:
                status = "sdk_archive_link_order_relocation_only"
            elif function["compared_byte_count"] >= 8:
                status = "sdk_archive_symbol_identified_vendor_modified_same_size"
            else:
                status = "sdk_archive_link_order_low_compared"
            placements.append({
                "range_index": range_index,
                "address": address,
                "end": address + function["size"],
                "size": function["size"],
                "name": function["name"],
                "object": function["object"],
                "status": status,
                "compared_byte_count": function["compared_byte_count"],
                "masked_byte_count": function["masked_byte_count"],
                "normalized_sha256": function["normalized_sha256"],
                "archive_match_addresses": function["matches"],
                "left_anchor": left["name"],
                "right_anchor": right["name"],
                "range_start": start,
                "range_end": end,
            })
            address += function["size"]
        if address != end:
            raise LinkOrderError("internal link-order tiling error")
    placement_intervals = [(item["address"], item["end"]) for item in placements]
    if sum(end - start for start, end in merge_intervals(placement_intervals)) != sum(
        item["size"] for item in placements
    ):
        raise LinkOrderError("link-order placements overlap")
    return placements


def discover_nop_aware_placements(
    report: dict[str, Any],
    authoritative_functions: Sequence[dict[str, Any]],
    strict_placements: Sequence[dict[str, Any]],
    application: bytes,
    *,
    maximum_intervening_functions: int = 8,
    maximum_singleton_size_delta: int = 32,
) -> list[dict[str, Any]]:
    """Place symbols after removing boundary NOPs and allow bounded singleton deltas."""
    definitions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for function in report["functions"]:
        definitions[function["name"]].append(function)
    functions = sorted(
        (items[0] for items in definitions.values() if len(items) == 1),
        key=lambda item: item["name"],
    )
    known_names: dict[str, set[int]] = defaultdict(set)
    for item in authoritative_functions:
        for name in item["names"]:
            known_names[name].add(item["address"])
    for item in strict_placements:
        known_names[item["name"]].add(item["address"])
    anchors = [
        (index, next(iter(known_names[function["name"]])), function)
        for index, function in enumerate(functions)
        if len(known_names[function["name"]]) == 1
    ]
    known_intervals = [
        (item["address"], item["end"])
        for item in authoritative_functions
    ] + [
        (item["address"], item["end"])
        for item in strict_placements
    ]
    placements: list[dict[str, Any]] = []
    range_index = 0
    for (left_index, left_address, left), (right_index, right_address, right) in zip(
        anchors, anchors[1:]
    ):
        intervening = functions[left_index + 1:right_index]
        if not intervening or len(intervening) > maximum_intervening_functions:
            continue
        raw_start = left_address + left["size"]
        raw_end = right_address
        if raw_start >= raw_end:
            continue
        start = raw_start
        end = raw_end
        while (
            start + 2 <= end
            and application[
                start - discovery.APP_BASE:start - discovery.APP_BASE + 2
            ] == b"\xE0\x78"
        ):
            start += 2
        while (
            end - 2 >= start
            and application[
                end - discovery.APP_BASE - 2:end - discovery.APP_BASE
            ] == b"\xE0\x78"
        ):
            end -= 2
        if start >= end or any(
            range_start < end and start < range_end
            for range_start, range_end in known_intervals
        ):
            continue
        archive_bytes = sum(item["size"] for item in intervening)
        stock_bytes = end - start
        delta = stock_bytes - archive_bytes
        exact_tile = delta == 0
        singleton_delta = (
            len(intervening) == 1
            and abs(delta) <= maximum_singleton_size_delta
            and intervening[0]["size"] * 2 >= stock_bytes
        )
        if not exact_tile and not singleton_delta:
            continue
        range_index += 1
        address = start
        for function in intervening:
            stock_size = function["size"] if exact_tile else stock_bytes
            if exact_tile and address in function["matches"]:
                status = "sdk_archive_exact_nop_aware_link_order_resolved"
            elif not exact_tile:
                status = "sdk_archive_symbol_identified_vendor_modified_size_delta"
            elif function["compared_byte_count"] == 0:
                status = "sdk_archive_nop_aware_link_order_relocation_only"
            elif function["compared_byte_count"] < 8:
                status = "sdk_archive_nop_aware_link_order_low_compared"
            else:
                status = "sdk_archive_symbol_identified_vendor_modified_same_size_nop_aware"
            placements.append({
                "range_index": range_index,
                "address": address,
                "end": address + stock_size,
                "size": stock_size,
                "archive_size": function["size"],
                "size_delta": stock_size - function["size"],
                "name": function["name"],
                "object": function["object"],
                "status": status,
                "compared_byte_count": function["compared_byte_count"],
                "masked_byte_count": function["masked_byte_count"],
                "normalized_sha256": function["normalized_sha256"],
                "archive_match_addresses": function["matches"],
                "left_anchor": left["name"],
                "right_anchor": right["name"],
                "raw_range_start": raw_start,
                "raw_range_end": raw_end,
                "range_start": start,
                "range_end": end,
            })
            address += stock_size
        if address != end:
            raise LinkOrderError("internal NOP-aware link-order tiling error")
    placement_intervals = [(item["address"], item["end"]) for item in placements]
    if sum(end - start for start, end in merge_intervals(placement_intervals)) != sum(
        item["size"] for item in placements
    ):
        raise LinkOrderError("NOP-aware link-order placements overlap")
    return placements


def discover_vector_handler_placements(
    em_hw_report: dict[str, Any],
    radio_report: dict[str, Any],
    application: bytes,
) -> list[dict[str, Any]]:
    """Resolve duplicate IRQ bodies with the authenticated EM9305 vector ABI."""
    expected_identities = {
        "em_hw_api": (
            "729ca978bb728f0289db4b3ee743e333670e4dc1",
            "74888e6952ff261b080e50c6267eed3e77d3a931dbe2dbb12f910068ca229865",
        ),
        "radio": (
            "00ce66bc3ff9968c8b233fd740332fde85d061b4",
            "de6ae31e5bf6436533296efa116c17a4fa37c3cce7652118b0b3e9e2474759cc",
        ),
    }
    reports = {"em_hw_api": em_hw_report, "radio": radio_report}
    for kind, (blob, archive_sha) in expected_identities.items():
        identity = reports[kind].get("identity", {})
        if (
            identity.get("archive_kind") != kind
            or identity.get("archive_git_blob") != blob
            or identity.get("archive_sha256") != archive_sha
            or not identity.get("compiler_anchors_matched")
        ):
            raise LinkOrderError(f"unexpected {kind} vector-handler archive identity")

    functions: dict[str, dict[str, Any]] = {}
    for report in reports.values():
        for function in report["functions"]:
            if function["name"] in {
                "IRQHandler_ArcTimer0",
                "IRQHandler_ArcTimer1",
                "IRQHandler_RadioTx",
                "IRQHandler_RadioRx",
            }:
                if function["name"] in functions:
                    raise LinkOrderError("duplicate vector-handler archive definition")
                functions[function["name"]] = function
    if len(functions) != 4:
        raise LinkOrderError("vector-handler archive definitions changed")

    vector_words = [
        struct.unpack_from("<I", application, offset)[0]
        for offset in range(0, 264, 4)
    ]
    # The authenticated SDK v4.2 interrupts.h assigns IRQ 0/1 to ARC timers
    # and IRQ 20/21 to radio TX/RX. ARC IRQ vectors begin at table word 16.
    expected = [
        (16, "IRQHandler_ArcTimer0", 0x0030_5B1C, 194),
        (17, "IRQHandler_ArcTimer1", 0x0030_5BE0, 194),
        (36, "IRQHandler_RadioTx", 0x0030_6440, 186),
        (37, "IRQHandler_RadioRx", 0x0030_6384, 186),
    ]
    timer_matches = {0x0030_5B1C, 0x0030_5BE0}
    radio_rx_matches = {0x0030_6384, 0x0030_6440}
    if (
        set(functions["IRQHandler_ArcTimer0"]["matches"]) != timer_matches
        or set(functions["IRQHandler_ArcTimer1"]["matches"]) != timer_matches
        or functions["IRQHandler_ArcTimer0"]["size"] != 194
        or functions["IRQHandler_ArcTimer1"]["size"] != 194
        or functions["IRQHandler_ArcTimer0"]["normalized_sha256"]
        != functions["IRQHandler_ArcTimer1"]["normalized_sha256"]
        or set(functions["IRQHandler_RadioRx"]["matches"]) != radio_rx_matches
        or functions["IRQHandler_RadioRx"]["size"] != 186
        or functions["IRQHandler_RadioTx"]["size"] != 380
        or functions["IRQHandler_RadioTx"]["matches"]
    ):
        raise LinkOrderError("vector-handler duplicate-body evidence changed")

    placements: list[dict[str, Any]] = []
    for vector_index, name, address, stock_size in expected:
        function = functions[name]
        if vector_words[vector_index] != address:
            raise LinkOrderError(f"stock vector target changed for {name}")
        body_end = address + stock_size
        nop_offset = body_end - discovery.APP_BASE
        if application[nop_offset:nop_offset + 2] != b"\xE0\x78":
            raise LinkOrderError(f"vector-handler boundary NOP changed for {name}")
        exact = address in function["matches"]
        if name == "IRQHandler_RadioTx":
            if exact or address not in functions["IRQHandler_RadioRx"]["matches"]:
                raise LinkOrderError("radio-TX modified-body alias evidence changed")
            status = "sdk_archive_vector_identified_vendor_modified_size_delta"
        else:
            if not exact:
                raise LinkOrderError(f"exact vector-handler body changed for {name}")
            status = "sdk_archive_exact_vector_resolved"
        placements.append({
            "vector_index": vector_index,
            "irq_number": vector_index - 16,
            "address": address,
            "end": body_end,
            "size": stock_size,
            "archive_size": function["size"],
            "size_delta": stock_size - function["size"],
            "name": name,
            "object": function["object"],
            "status": status,
            "compared_byte_count": function["compared_byte_count"],
            "masked_byte_count": function["masked_byte_count"],
            "normalized_sha256": function["normalized_sha256"],
            "archive_match_addresses": function["matches"],
            "implementation_alias": (
                "IRQHandler_RadioRx" if name == "IRQHandler_RadioTx" else None
            ),
            "interrupt_header_git_blob": EXPECTED_INTERRUPT_HEADER_GIT_BLOB,
            "interrupt_header_sha256": EXPECTED_INTERRUPT_HEADER_SHA256,
        })
    return placements


def discover_short_prefix_order_placements(
    em_system_report: dict[str, Any],
    authoritative_functions: Sequence[dict[str, Any]],
    application: bytes,
) -> list[dict[str, Any]]:
    """Resolve a complete repeated short-body run at an exact anchor boundary."""
    identity = em_system_report.get("identity", {})
    if (
        identity.get("archive_kind") != "em_system"
        or identity.get("archive_git_blob") != "47acd3c20c78d983b605267b18d4f8d6eb1e50d1"
        or identity.get("archive_sha256") != "390b2d610c01b79a01b461dc5c88c7aa249e7bbd46d528455bce3dbce93f7b96"
        or not identity.get("compiler_anchors_matched")
    ):
        raise LinkOrderError("unexpected EM-system short-prefix archive identity")
    definitions = {item["name"]: item for item in em_system_report["functions"]}
    if any(name not in definitions for name in EXPECTED_SHORT_PREFIX_NAMES):
        raise LinkOrderError("EM-system short-prefix definitions changed")
    selected = [definitions[name] for name in EXPECTED_SHORT_PREFIX_NAMES]
    expected_hash = "df76b0aba1f705436023e9ee970e8c37d8da26059a7798d11b602b9a118d51d8"
    if any(
        item["size"] != 4
        or item["compared_byte_count"] != 4
        or item["masked_byte_count"] != 0
        or item["normalized_sha256"] != expected_hash
        or item["matches"]
        for item in selected
    ):
        raise LinkOrderError("EM-system short-prefix body evidence changed")

    by_name = {
        name: item
        for item in authoritative_functions
        for name in item["names"]
        if name in {"EMSS_LeRand", "EMSystem_TransmitCM"}
    }
    if set(by_name) != {"EMSS_LeRand", "EMSystem_TransmitCM"}:
        raise LinkOrderError("EM-system short-prefix anchors changed")
    start = by_name["EMSS_LeRand"]["end"]
    right_address = by_name["EMSystem_TransmitCM"]["address"]
    run = application[
        start - discovery.APP_BASE:
        start - discovery.APP_BASE + EXPECTED_SHORT_PREFIX_BYTES
    ]
    if (
        start != 0x0030_592C
        or right_address != 0x0030_5AB4
        or len(run) != EXPECTED_SHORT_PREFIX_BYTES
        or any(
            hashlib.sha256(run[offset:offset + 4]).hexdigest() != expected_hash
            for offset in range(0, len(run), 4)
        )
        or hashlib.sha256(
            application[
                start - discovery.APP_BASE + EXPECTED_SHORT_PREFIX_BYTES:
                start - discovery.APP_BASE + EXPECTED_SHORT_PREFIX_BYTES + 4
            ]
        ).hexdigest() == expected_hash
    ):
        raise LinkOrderError("stock EM-system short-prefix run changed")

    return [
        {
            "prefix_index": index,
            "address": start + index * 4,
            "end": start + (index + 1) * 4,
            "size": 4,
            "archive_size": 4,
            "size_delta": 0,
            "name": function["name"],
            "object": function["object"],
            "status": "sdk_archive_exact_short_prefix_order_resolved",
            "compared_byte_count": 4,
            "masked_byte_count": 0,
            "normalized_sha256": expected_hash,
            "archive_match_addresses": [],
            "left_anchor": "EMSS_LeRand",
            "right_anchor": "EMSystem_TransmitCM",
        }
        for index, function in enumerate(selected)
    ]


def analyze(
    baseline_output: Path,
    enforced_output: Path,
    round2_output: Path,
    round1_min8_output: Path,
    round2_min8_output: Path,
    application_objdump: Path,
    *,
    image: Path = discovery.DEFAULT_IMAGE,
) -> dict[str, Any]:
    exact = discovery.analyze_low_floor(
        baseline_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
        include_functions=True,
    )
    controller_report_path = (
        round2_min8_output.resolve() / "reports" / "emb_controller_iso.json"
    )
    controller_report = json.loads(controller_report_path.read_text())
    if controller_report["identity"]["archive_kind"] != "emb_controller_iso":
        raise LinkOrderError("unexpected controller archive identity")
    placements = discover_placements(controller_report, exact["functions"])
    status_counts = Counter(item["status"] for item in placements)
    status_bytes = Counter()
    for item in placements:
        status_bytes[item["status"]] += item["size"]
    modified = {
        item["address"]: item["name"]
        for item in placements
        if item["status"] == "sdk_archive_symbol_identified_vendor_modified_same_size"
    }
    if (
        len({item["range_index"] for item in placements}) != EXPECTED_RANGE_COUNT
        or len(placements) != EXPECTED_FUNCTION_COUNT
        or sum(item["size"] for item in placements) != EXPECTED_IDENTIFIED_BYTES
        or dict(status_counts) != EXPECTED_STATUS_COUNTS
        or dict(status_bytes) != EXPECTED_STATUS_BYTES
        or modified != EXPECTED_MODIFIED
    ):
        raise LinkOrderError("authenticated link-order placement census changed")

    image_bytes = image.resolve().read_bytes()
    application = image_bytes[
        discovery.APP_FILE_OFFSET:discovery.APP_FILE_OFFSET + discovery.APP_SIZE
    ]
    nop_aware = discover_nop_aware_placements(
        controller_report,
        exact["functions"],
        placements,
        application,
    )
    nop_aware_counts = Counter(item["status"] for item in nop_aware)
    nop_aware_bytes = Counter()
    for item in nop_aware:
        nop_aware_bytes[item["status"]] += item["size"]
    if (
        len({item["range_index"] for item in nop_aware})
        != EXPECTED_NOP_AWARE_RANGE_COUNT
        or len(nop_aware) != EXPECTED_NOP_AWARE_FUNCTION_COUNT
        or sum(item["size"] for item in nop_aware)
        != EXPECTED_NOP_AWARE_IDENTIFIED_BYTES
        or sum(item["archive_size"] for item in nop_aware)
        != EXPECTED_NOP_AWARE_ARCHIVE_BYTES
        or dict(nop_aware_counts) != EXPECTED_NOP_AWARE_STATUS_COUNTS
        or dict(nop_aware_bytes) != EXPECTED_NOP_AWARE_STATUS_BYTES
    ):
        raise LinkOrderError("authenticated NOP-aware placement census changed")

    em_hw_report_path = baseline_output.resolve() / "reports" / "em_hw_api.json"
    radio_report_path = baseline_output.resolve() / "reports" / "radio.json"
    em_system_report_path = baseline_output.resolve() / "reports" / "em_system.json"
    if (
        discovery.sha256_file(em_hw_report_path) != EXPECTED_EM_HW_REPORT_SHA256
        or discovery.sha256_file(radio_report_path) != EXPECTED_RADIO_REPORT_SHA256
        or discovery.sha256_file(em_system_report_path) != EXPECTED_EM_SYSTEM_REPORT_SHA256
    ):
        raise LinkOrderError("vector-handler archive report identity mismatch")
    vector_handlers = discover_vector_handler_placements(
        json.loads(em_hw_report_path.read_text()),
        json.loads(radio_report_path.read_text()),
        application,
    )
    vector_counts = Counter(item["status"] for item in vector_handlers)
    vector_bytes = Counter()
    for item in vector_handlers:
        vector_bytes[item["status"]] += item["size"]
    if (
        len(vector_handlers) != EXPECTED_VECTOR_HANDLER_FUNCTIONS
        or sum(item["size"] for item in vector_handlers) != EXPECTED_VECTOR_HANDLER_BYTES
        or dict(vector_counts) != EXPECTED_VECTOR_HANDLER_STATUS_COUNTS
        or dict(vector_bytes) != EXPECTED_VECTOR_HANDLER_STATUS_BYTES
    ):
        raise LinkOrderError("authenticated vector-handler placement census changed")

    short_prefix = discover_short_prefix_order_placements(
        json.loads(em_system_report_path.read_text()), exact["functions"], application
    )
    if (
        len(short_prefix) != EXPECTED_SHORT_PREFIX_FUNCTIONS
        or sum(item["size"] for item in short_prefix) != EXPECTED_SHORT_PREFIX_BYTES
        or tuple(item["name"] for item in short_prefix) != EXPECTED_SHORT_PREFIX_NAMES
    ):
        raise LinkOrderError("authenticated short-prefix placement census changed")

    all_placements = placements + nop_aware + vector_handlers + short_prefix

    exact_placements = [
        item
        for item in all_placements
        if item["status"] in {
            "sdk_archive_exact_link_order_resolved",
            "sdk_archive_exact_nop_aware_link_order_resolved",
            "sdk_archive_exact_vector_resolved",
            "sdk_archive_exact_short_prefix_order_resolved",
        }
    ]
    exact_intervals = [
        (item["address"], item["end"])
        for item in exact["functions"]
    ] + [(item["address"], item["end"]) for item in exact_placements]
    merged_exact = merge_intervals(exact_intervals)
    exact_bytes = sum(end - start for start, end in merged_exact)
    provenance_intervals = exact_intervals + [
        (item["address"], item["end"])
        for item in all_placements
        if item not in exact_placements
    ]
    merged_provenance = merge_intervals(provenance_intervals)
    provenance_bytes = sum(end - start for start, end in merged_provenance)
    if (
        len(all_placements) != EXPECTED_ALL_IDENTIFIED_PLACEMENTS
        or sum(item["size"] for item in all_placements)
        != EXPECTED_ALL_IDENTIFIED_PLACEMENT_BYTES
        or len(exact_placements) != EXPECTED_EXACT_FUNCTIONS + 34 + 3 + 6
        or sum(item["size"] for item in exact_placements)
        != EXPECTED_EXACT_BYTES + 774 + 574 + 24
        or exact["combined_exact_function_count"] + len(exact_placements)
        != EXPECTED_ALL_EXACT_FUNCTIONS
        or exact_bytes != EXPECTED_ALL_EXACT_BYTES
        or len(merged_exact) != EXPECTED_ALL_EXACT_INTERVALS
        or provenance_bytes != EXPECTED_ALL_PROVENANCE_BYTES
        or len(merged_provenance) != EXPECTED_ALL_PROVENANCE_INTERVALS
    ):
        raise LinkOrderError(
            "combined exact/provenance coverage changed: "
            f"placements={len(all_placements)}/"
            f"{sum(item['size'] for item in all_placements)}, "
            f"exact_placements={len(exact_placements)}/"
            f"{sum(item['size'] for item in exact_placements)}, "
            f"exact={exact['combined_exact_function_count'] + len(exact_placements)}/"
            f"{exact_bytes}/{len(merged_exact)}, "
            f"provenance={provenance_bytes}/{len(merged_provenance)}"
        )

    return {
        "strict_link_order_range_count": EXPECTED_RANGE_COUNT,
        "nop_aware_link_order_range_count": EXPECTED_NOP_AWARE_RANGE_COUNT,
        "link_order_range_count": EXPECTED_ALL_LINK_ORDER_RANGES,
        "link_order_function_count": EXPECTED_ALL_LINK_ORDER_FUNCTIONS,
        "link_order_identified_bytes": EXPECTED_ALL_LINK_ORDER_BYTES,
        "vector_handler_function_count": len(vector_handlers),
        "vector_handler_identified_bytes": sum(item["size"] for item in vector_handlers),
        "short_prefix_function_count": len(short_prefix),
        "short_prefix_identified_bytes": sum(item["size"] for item in short_prefix),
        "identified_placement_count": len(all_placements),
        "identified_placement_bytes": sum(item["size"] for item in all_placements),
        "status_function_counts": dict(
            status_counts + nop_aware_counts + vector_counts
            + Counter(item["status"] for item in short_prefix)
        ),
        "status_bytes": dict(
            status_bytes + nop_aware_bytes + vector_bytes
            + Counter({"sdk_archive_exact_short_prefix_order_resolved": 24})
        ),
        "combined_exact_function_count": EXPECTED_ALL_EXACT_FUNCTIONS,
        "combined_exact_function_bytes": exact_bytes,
        "combined_exact_interval_count": len(merged_exact),
        "combined_exact_application_percent": exact_bytes / discovery.APP_SIZE * 100.0,
        "exact_function_complement_bytes": discovery.APP_SIZE - exact_bytes,
        "provenance_identified_application_bytes": provenance_bytes,
        "provenance_identified_interval_count": len(merged_provenance),
        "provenance_identified_application_percent": provenance_bytes / discovery.APP_SIZE * 100.0,
        "application_bytes_not_function_provenance_identified": discovery.APP_SIZE - provenance_bytes,
        "application_percent_not_function_provenance_identified": (
            discovery.APP_SIZE - provenance_bytes
        ) / discovery.APP_SIZE * 100.0,
        "strict_placements": placements,
        "nop_aware_placements": nop_aware,
        "vector_handler_placements": vector_handlers,
        "short_prefix_placements": short_prefix,
        "placements": all_placements,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-output", type=Path, required=True)
    parser.add_argument("--enforced-output", type=Path, required=True)
    parser.add_argument("--round2-output", type=Path, required=True)
    parser.add_argument("--round1-min8-output", type=Path, required=True)
    parser.add_argument("--round2-min8-output", type=Path, required=True)
    parser.add_argument("--application-objdump", type=Path, required=True)
    parser.add_argument("--image", type=Path, default=discovery.DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(
        args.batch_output,
        args.enforced_output,
        args.round2_output,
        args.round1_min8_output,
        args.round2_min8_output,
        args.application_objdump,
        image=args.image,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 SDK link-order recovery audit: PASS")
        print(json.dumps({key: value for key, value in report.items() if key != "placements"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
