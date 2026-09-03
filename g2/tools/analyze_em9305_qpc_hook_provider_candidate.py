#!/usr/bin/env python3
"""Authenticate named provider boundaries for two EM9305 QP/C hooks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import analyze_em9305_first_party_hooks_candidate as first_party


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
OBJDUMP = ROOT / "research/corpus/em9305/size-delta/opencfw-em9305-application-objdump.txt"
ARCHIVE_REPORT = ROOT / "research/corpus/em9305/sdk-comparison/batch16/reports/emb_controller.json"
PML_REPORT = ROOT / "research/corpus/em9305/sdk-comparison/round2/reports/pml_di03.json"
CORDIO_PROVENANCE = ROOT / "third_party/cordio/PROVENANCE.json"
CANDIDATE = ROOT / "components/shared/em9305/runtime_qpc_hook_provider_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
WSF_CANDIDATE = ROOT / "components/shared/em9305/runtime_wsf_idle_tasks.c"
WSF_HEADER = WSF_CANDIDATE.with_suffix(".h")
MANIFEST = ROOT / "tools/manifests/em9305-qpc-hook-provider-closure.tsv"

FILE_PINS = {
    IMAGE: (211_948, "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"),
    OBJDUMP: (3_463_728, "13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f"),
    ARCHIVE_REPORT: (1_810_118, "dfe669a3370e3e8417c45e1619f62c4225a9598c90156ea7649b4d9aad84a525"),
    PML_REPORT: (55_705, "99f23bae581422185362e6f11ed0afa0fd923a0d6c4f4f9e1582b43400650d4f"),
    CORDIO_PROVENANCE: (20_246, "1fffca2937f4ec8f0937f947e0d6e0c14110ea36c561826be21b67d0c7bab07a"),
    CANDIDATE: (2_557, "853865ae3bd704cc3a9153abbb43b5cbac5ddad84ff2fc4ae8505ac1272f9ac3"),
    HEADER: (1_537, "6b2be8187a7a6a80f00affa53b8f8cf4c52045eb6abaeed9965b72ed49bd1690"),
    WSF_CANDIDATE: (2_098, "5a7458762180de765802774468dae715ce637bcd6e352c20b01698083b800071"),
    WSF_HEADER: (1_214, "75183c81061def9f3de7b8286dd2697219d4b31b3e3cc83e9c9cc46ccf4062c4"),
    MANIFEST: (2_283, "92ad6acc7171c1cd60f00d6cc7f19bfbb821eac50b177afa4b6eeb4013f6083a"),
}
APP_BASE = 0x00302400
APP_FILE_OFFSET = 0x424
HOOKS = {
    0x00311150: (0x00311154, 4,
                 "7766b559c480d3129860a74a673038b9db4a622de9bb71c7957ee5e1837047de",
                 "QF_onResumeInternalHook"),
    0x00311620: (0x00311634, 20,
                 "fbb0316db14f6fc107f338a4cbf5852049003c2def1230d9f5e117e7a0a2abe4",
                 "QK_onIdleInternalHook"),
}
PROVIDERS = {
    "PalUartResume": {
        "address": 0x00310798, "size": 66,
        "sha256": "23bcfb3077b378b2decc8d547be03076e80f063f7d1ee73a7e9d963a54935261",
        "object": "pal_uart.c.obj", "compared": 34, "masked": 32,
        "normalized": "cacdadc02cc9e9cbb1aad1adeeef5f0feacc919623af33ef8035a233729add8c",
    },
    "wsfOsRunIdleTasks": {
        "address": 0x00333D7C, "size": 58,
        "sha256": "fd62056a4f17372fc978f7b17fefe03de7588d015413e78a3e298dd232b6cd38",
        "object": "wsf_os.c.obj", "compared": 54, "masked": 4,
        "normalized": "443757dcaf3311b35cca73daca2609311c98ddd0df3aaa921ae24709434fa88d",
    },
}
WSF_BODY_HEX = (
    "e8c2cb45800060600d8ded7015e82c8d0fe9b1404a2600100410002405e840782"
    "c8dc0be057ee571f10f449002f0cd7044264f10edade140c8c6"
)
WSF_OBJDUMP_MARKERS = (
    "333d7e:\t45cb 0080 6060      \tmov_s\tr13,0x806060",
    "333d84:\t8d0d                \tldb_s\tr0,[r13,0xd]",
    "333d8a:\t8d2c                \tldb_s\tr1,[r13,0xc]",
    "333d94:\t1004 2400           \tld.ab\tr0,[r16,4]",
    "333d9a:\t7840                \tjl_s\t[r0]",
    "333d9e:\tbec0                \tbmsk_s\tr14,r14,0",
    "333da0:\t7e05                \tor_s\tr14,r14,r0",
    "333dac:\t2644 104f           \tand\tr15,r14,0x1",
    "333db0:\taded                \tstb_s\tr15,[r13,0xd]",
)
VOLTMON = {
    "address": 0x00313AE4, "size": 104,
    "sha256": "5607dec62c9b662938b071e0d5f2deb0ac728650d4939d3b60b070b7af39a88e",
    "object": "pml_volt_monitor.c.obj", "compared": 80, "masked": 24,
    "normalized": "dac7a5da86e1e0d723626d2daf4ec412ea81e77840fe91c2c128ef11ac705b5d",
}
IDLE_EDGES = {
    0x003100EC: (4, "bd00c000", "f64115f823d5675ed59321d1edd7c76faddd893e7ed7914dec00cb156a6a8a04"),
    0x003119A8: (6, "3d0120010c70", "bf00a17eac1f4d73075ec9d4041282acc36f4837f37d441e8bcaf6f3bd272387"),
    0x00310728: (6, "c102efff10d8", "e9d2f8dea13fd219fc4d874e188bad89a6a1185db4704f7067ed7a5a7797564c"),
    0x003101E8: (4, "e07ee078", "edfeb981f4b027bc93163843f0d3cb3bd46cf8ea6ad690caf387525ed1c8379f"),
}


class CandidateError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, expected: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    actual = len(data), digest(data)
    if actual != expected:
        raise CandidateError(f"{path}: identity drift: {actual} != {expected}")
    return data


def installed_slice(image: bytes, start: int, size: int) -> bytes:
    offset = APP_FILE_OFFSET + start - APP_BASE
    return image[offset:offset + size]


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path, pin) for path, pin in FILE_PINS.items()}
    image = inputs[IMAGE]
    source = inputs[CANDIDATE].decode("utf-8")
    header = inputs[HEADER].decode("utf-8")
    wsf_source = inputs[WSF_CANDIDATE].decode("utf-8")
    wsf_header = inputs[WSF_HEADER].decode("utf-8")
    combined = source + "\n" + header
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise CandidateError("clean-room boundary must retain both MIT declarations")
    for symbol in ("open_cfw_em9305_qf_resume_named_boundary",
                   "open_cfw_em9305_qk_idle_named_boundary"):
        if len(re.findall(rf"\b{symbol}\s*\(", combined)) != 2:
            raise CandidateError(f"candidate symbol drift: {symbol}")
    for marker in ("OPEN_CFW_EM9305_HOOK_MODEL_NAMED_ARCHIVE_PROVIDER",
                   "OPEN_CFW_EM9305_HOOK_MODEL_TYPED_UNRESOLVED_PROVIDER",
                   "OPEN_CFW_EM9305_HOOK_MODEL_EXACT_NOOP_TARGET",
                   "PalUartResume", "wsfOsRunIdleTasks",
                   "VoltMon_DoMeasurement"):
        if marker not in combined:
            raise CandidateError(f"candidate boundary marker drift: {marker}")
    wsf_combined = wsf_source + "\n" + wsf_header
    if wsf_combined.count("SPDX-License-Identifier: MIT") != 2:
        raise CandidateError("WSF idle candidate must retain both MIT declarations")
    for marker in (
        "OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY = 3",
        "open_cfw_em9305_wsf_idle_state_init",
        "open_cfw_em9305_wsf_idle_register",
        "open_cfw_em9305_wsf_idle_request",
        "open_cfw_em9305_wsf_os_run_idle_tasks",
        "active |= callback() & 1U",
        "state->pending = (uint8_t)(active & 1U)",
    ):
        if marker not in wsf_combined:
            raise CandidateError(f"WSF idle candidate marker drift: {marker}")
    objdump = inputs[OBJDUMP].decode("ascii")
    for marker in WSF_OBJDUMP_MARKERS:
        if marker not in objdump:
            raise CandidateError(f"WSF idle stock semantic marker drift: {marker}")

    first = first_party.run_audit()
    if first["status"] != "candidate-qualified-fail-closed":
        raise CandidateError("parent first-party hook evidence is not qualified")
    decisions: dict[str, Any] = {}
    for start, (end, size, stock_sha, name) in HOOKS.items():
        body = installed_slice(image, start, size)
        if end - start != size or digest(body) != stock_sha:
            raise CandidateError(f"hook identity drift at 0x{start:08x}")
        parent = first["stock_first_party"]["spans"][f"0x{start:08X}"]
        if (
            parent["end_exclusive"], parent["bytes"], parent["sha256"]
        ) != (end, size, stock_sha):
            raise CandidateError(f"parent hook evidence drift at 0x{start:08x}")
        decisions[f"0x{start:08X}"] = {
            "end_exclusive": end, "bytes": size, "sha256": stock_sha,
            "readiness": "typed_unsupported_external_boundary",
            "decision": "named_provider_boundary",
            "name": name,
        }

    report = json.loads(inputs[ARCHIVE_REPORT])
    identity = report["identity"]
    if (identity["archive_git_blob"], identity["archive_sha256"],
        identity["compiler"], identity["optimization"]) != (
        "6a1a8e3df756a97e0afbcf7d10482eecc7856336",
        "3b256ac3352955dc4bd9b49554e011e1587be7fdb58538f0ac7b9d4fe42ac971",
        "Synopsys MetaWare ARC Compiler T-2022.09 build 004 / LLVM 14.0.6 (EM-Micro)",
        "-Os"):
        raise CandidateError("authenticated controller archive identity drift")
    functions = {item["name"]: item for item in report["functions"]}
    provider_results = {}
    for name, expected in PROVIDERS.items():
        item = functions.get(name)
        if item is None:
            raise CandidateError(f"archive provider missing: {name}")
        observed = (item["size"], item["object"], item["compared_byte_count"],
                    item["masked_byte_count"], item["normalized_sha256"],
                    item["matches"])
        wanted = (expected["size"], expected["object"], expected["compared"],
                  expected["masked"], expected["normalized"],
                  [expected["address"]])
        if observed != wanted:
            raise CandidateError(f"archive provider mapping drift: {name}")
        body = installed_slice(image, expected["address"], expected["size"])
        if digest(body) != expected["sha256"]:
            raise CandidateError(f"stock provider body drift: {name}")
        if name == "wsfOsRunIdleTasks" and body.hex() != WSF_BODY_HEX:
            raise CandidateError("stock WSF idle body bytes drift")
        provider_results[name] = {
            "address": expected["address"], "bytes": expected["size"],
            "sha256": expected["sha256"], "archive_object": expected["object"],
            "normalized_sha256": expected["normalized"],
            "redistribution_authority": (
                "clean-room-mit" if name == "wsfOsRunIdleTasks" else "unresolved"
            ),
            "clean_room_source_available": name == "wsfOsRunIdleTasks",
            "hardware_dependent": name != "wsfOsRunIdleTasks",
        }

    pml_report = json.loads(inputs[PML_REPORT])
    pml_identity = pml_report["identity"]
    if (
        pml_identity["archive_git_blob"], pml_identity["archive_sha256"],
        pml_identity["archive_kind"], pml_identity["compiler"],
        pml_identity["optimization"],
    ) != (
        "8637c90e3851846347e6b14135a6779999c570cc",
        "227d3b5395f36802781c0cff3e7a21f641da74579342d7ccfc76a74b18e51570",
        "pml_di03",
        "Synopsys MetaWare ARC Compiler T-2022.09 build 004 / LLVM 14.0.6 (EM-Micro)",
        "-Os",
    ):
        raise CandidateError("authenticated PML archive identity drift")
    volt_items = [
        item for item in pml_report["functions"]
        if item["name"] == "VoltMon_DoMeasurement"
    ]
    if len(volt_items) != 1:
        raise CandidateError("PML voltage-monitor provider count drift")
    volt = volt_items[0]
    observed = (
        volt["size"], volt["object"], volt["compared_byte_count"],
        volt["masked_byte_count"], volt["normalized_sha256"], volt["matches"],
    )
    wanted = (
        VOLTMON["size"], VOLTMON["object"], VOLTMON["compared"],
        VOLTMON["masked"], VOLTMON["normalized"], [VOLTMON["address"]],
    )
    if observed != wanted:
        raise CandidateError("PML voltage-monitor provider mapping drift")
    volt_body = installed_slice(image, VOLTMON["address"], VOLTMON["size"])
    if digest(volt_body) != VOLTMON["sha256"]:
        raise CandidateError("stock provider body drift: VoltMon_DoMeasurement")
    provider_results["VoltMon_DoMeasurement"] = {
        "address": VOLTMON["address"], "bytes": VOLTMON["size"],
        "sha256": VOLTMON["sha256"], "archive_object": VOLTMON["object"],
        "normalized_sha256": VOLTMON["normalized"],
        "redistribution_authority": "unresolved",
        "clean_room_source_available": False,
        "hardware_dependent": True,
    }
    edge_results = {}
    for address, (size, expected_hex, expected_sha) in IDLE_EDGES.items():
        body = installed_slice(image, address, size)
        if body.hex() != expected_hex or digest(body) != expected_sha:
            raise CandidateError(f"idle provider edge drift at 0x{address:08x}")
        edge_results[f"0x{address:08X}"] = {
            "bytes": size, "sha256": expected_sha,
        }

    provenance = json.loads(inputs[CORDIO_PROVENANCE])
    if (provenance["license"], provenance["upstream"]["selected_commit"],
        provenance["selection"]["exact_g2_checkout_proven"]) != (
        "Apache-2.0", "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6", False):
        raise CandidateError("public Packetcraft comparator provenance drift")
    rows = list(csv.DictReader(inputs[MANIFEST].decode("ascii").splitlines(),
                               delimiter="\t"))
    if len(rows) != 8:
        raise CandidateError("provider boundary manifest row-count drift")
    row_by_name = {row["name"]: row for row in rows}
    if (
        row_by_name["VoltMon_DoMeasurement"]["disposition"]
        != "exact_sdk_archive_identity_via_two_veneers"
        or row_by_name["wsfOsRunIdleTasks"]["disposition"]
        != "clean_room_source_candidate"
        or row_by_name["idle_final_noop"]["disposition"] != "exact_noop_target"
    ):
        raise CandidateError("idle provider manifest decision drift")
    if rows[-1]["name"] != "blocked by unavailable physical evidence":
        raise CandidateError("hardware qualification policy drift")
    return {
        "status": "candidate-qualified-software-provider-two-hardware",
        "read_only": True,
        "hardware_operations": False,
        "license": "MIT",
        "decisions": decisions,
        "providers": provider_results,
        "idle_provider_edges": edge_results,
        "unresolved_providers": [],
        "software_provider_gaps": [],
        "hardware_dependent_providers": [
            "PalUartResume", "VoltMon_DoMeasurement",
        ],
        "wsf_idle_semantics": {
            "stock_entry": 0x00333D7C,
            "stock_bytes": 58,
            "callback_capacity": 3,
            "callback_count_offset": 12,
            "pending_offset": 13,
            "result": "ordered_nonnull_callback_bit0_or",
            "clean_room_source": str(WSF_CANDIDATE.relative_to(ROOT)),
            "clean_room_header": str(WSF_HEADER.relative_to(ROOT)),
            "production_routed": False,
        },
        "semantic_noop": {
            "entry": 0x00310728, "argument": 16,
            "target": 0x003101E8, "bytes": 4,
            "behavior": "return_without_state_change",
        },
        "public_comparator": {
            "commit": provenance["upstream"]["selected_commit"],
            "license": "Apache-2.0", "exact_g2_source": False,
        },
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "production_routed": False,
        },
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 QP/C hook providers: candidate-qualified-software-provider-two-hardware")
        print("software provider: wsfOsRunIdleTasks")
        print("hardware providers: PalUartResume, VoltMon_DoMeasurement")
        print("hardware validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
