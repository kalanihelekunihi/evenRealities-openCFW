#!/usr/bin/env python3
"""Recover and pin function boundaries in two EM9305 controller clusters.

The two largest high-confidence modern-controller residual segments —
``[0x00329888,0x0032A4BE)`` (3,126 bytes, slave connection) and
``[0x00321C30,0x0032233C)`` (1,804 bytes, master periodic-scan/PAwR) — are
bracketed in the authenticated `lib_emb_controller_iso.a` link order by exact
stock anchors.  The intervening archive symbols in sorted-section order are
candidate function identities.  This analyzer re-verifies, fail-closed:

- the two residual-segment byte identities against the official blob;
- the authenticated whole-application GNU ARCv2 EM objdump;
- the repository-owned Lorelei return
  (``research/corpus/em9305/cluster-recovery/return/cluster-objects.json``)
  containing GNU ARC disassemblies of the seven candidate archive objects,
  authenticated against the pinned ISO archive SHA-256
  ``87af23b9…6cfa`` / Git blob ``b9433012…``;
- per-function opcode-sequence alignments (``difflib.SequenceMatcher`` on
  mnemonic streams, the acceptance method established by
  ``compare_em9305_size_delta_sdk_functions.py``) at the pinned boundaries;
- exact gap tiling (functions plus interior ``nop_s`` padding cover every
  segment byte with no remainder); and
- the pinned evidence constants for the divergent bodies.

Identification tiers used in the map:

- ``opcode_sequence_exact_size_exact`` — mnemonic stream and size both match
  the archive body.  Byte-level relocation masking is *not* re-run by this
  lane, so this is not a claim of byte-exact coverage.
- ``vendor_modified_opcode_aligned`` — sequence ratio >= 0.85 at the pinned
  link-order position; same upstream function, vendor/configuration-modified
  body.
- ``vendor_modified_divergent`` — sequence ratio < 0.85 at the pinned
  link-order position; role is pinned by the bracket anchors and by shared
  context constants, but the implementation is substantially extended or
  rewritten (the `lctrCenSendPendingRspRptHandler` precedent).

All ten functions remain ``proprietary_modern_controller_source_unavailable``
stock retentions: the SDK oracle has no redistribution-safe license, and
function-level identity does not change that.
"""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence

import analyze_em9305_sdk_discovery as discovery


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = discovery.DEFAULT_IMAGE
DEFAULT_OBJDUMP = (
    ROOT / "research/corpus/em9305/size-delta/opencfw-em9305-application-objdump.txt"
)
DEFAULT_OBJECTS = (
    ROOT / "research/corpus/em9305/cluster-recovery/return/cluster-objects.json"
)
DEFAULT_TSV = ROOT / "tools/manifests/em9305-controller-cluster-map.tsv"

PACKAGE_MAP_BASE = 0x0030_1FDC
IMAGE_SHA256 = discovery.IMAGE_SHA256
OBJECTS_SHA256 = "0d3d7aebedbbba034bedd430d932047719df12bedd35133c82cd245967bf71c3"
ARCHIVE_SHA256 = "87af23b9b6a582137a02759c4af2344f7160a8b88197dd540ef8268aa55f6cfa"
ARCHIVE_GIT_BLOB = "b9433012b264da2210f602395b144a6d21795f01"

STATUS_OPCODE_EXACT = "opcode_sequence_exact_size_exact"
STATUS_MODIFIED = "vendor_modified_opcode_aligned"
STATUS_DIVERGENT = "vendor_modified_divergent"
MODIFIED_RATIO_FLOOR = 0.85

# Pinned per-function recovery.  Offsets are installed addresses; metrics are
# (archive_instructions, stock_instructions, matched, longest_matching_run).
CLUSTERS = (
    {
        "name": "slave_connection",
        "start": 0x0032_9888,
        "end": 0x0032_A4BE,
        "segment_sha256": "45c3d2477869a9ace185078ca6b5f59621eeca07ae274414e64637e5b04f12aa",
        "left_anchor": "lctrSlvConnDisp",
        "right_anchor": "lctrSlvConnUpdateOp",
        "functions": (
            # start, name, object, archive_size, metrics, status, evidence extras
            (0x0032_9888, "lctrSlvConnEndOp", "lctr_isr_conn_slave.c.obj", 1_866,
             (588, 591, 569, 160), STATUS_MODIFIED, ()),
            (0x0032_9FD8, "lctrSlvConnExecute", "lctr_main_conn_slave.c.obj", 38,
             (13, 13, 13, 13), STATUS_OPCODE_EXACT, ()),
            (0x0032_A000, "lctrSlvConnExecuteSm", "lctr_sm_conn_slave.c.obj", 554,
             (187, 184, 165, 45), STATUS_MODIFIED, ()),
            (0x0032_A218, "lctrSlvConnResetHandler", "lctr_main_conn_slave.c.obj", 22,
             (7, 7, 7, 7), STATUS_OPCODE_EXACT, ()),
            (0x0032_A230, "lctrSlvConnRxCompletion", "lctr_isr_conn_slave.c.obj", 554,
             (185, 197, 180, 82), STATUS_MODIFIED, ()),
            (0x0032_A47C, "lctrSlvConnTxCompletion", "lctr_isr_conn_slave.c.obj", 38,
             (14, 24, 11, 6), STATUS_DIVERGENT,
             ("shared_context_offsets_341_630", "extra_event_case_0xa",
              "counter_global_0x0080568C")),
        ),
        "interior_nops": (0x0032_9FD6, 0x0032_9FFE, 0x0032_A216, 0x0032_A22E),
    },
    {
        "name": "master_periodic_scan_pawr",
        "start": 0x0032_1C30,
        "end": 0x0032_233C,
        "segment_sha256": "f1c6059c121b60e25cfcb722c6ee546af9d19acf06ab9b55d55bcde07eaae48d",
        "left_anchor": "lctrMstPerScanRxPerAdvPktHandler",
        "right_anchor": "lctrMstPerScanWithRspEndOp",
        "functions": (
            (0x0032_1C30, "lctrMstPerScanRxPerAdvPktPostHandler",
             "lctr_isr_adv_master_ae.c.obj", 500,
             (170, 164, 137, 24), STATUS_DIVERGENT,
             ("link_order_position_pinned",)),
            (0x0032_1E14, "lctrMstPerScanTransferOpCommit",
             "lctr_main_adv_master_ae.c.obj", 868,
             (283, 283, 267, 36), STATUS_MODIFIED, ()),
            (0x0032_2178, "lctrMstPerScanWithRspAbortOp",
             "lctr_isr_adv_central_pawr.c.obj", 10,
             (3, 3, 3, 3), STATUS_OPCODE_EXACT,
             ("relocation_only_branch_to_right_anchor",)),
            (0x0032_2184, "lctrMstPerScanWithRspCommitOp",
             "lctr_main_adv_central_pawr.c.obj", 432,
             (141, 145, 132, 49), STATUS_MODIFIED, ()),
        ),
        "interior_nops": (0x0032_2182,),
    },
)

EXPECTED_FUNCTION_COUNT = 10
EXPECTED_STATUS_COUNTS = {
    STATUS_OPCODE_EXACT: 3,
    STATUS_MODIFIED: 5,
    STATUS_DIVERGENT: 2,
}
EXPECTED_IDENTIFIED_BYTES = 4_920   # 3,116 + 1,804 minus interior NOP bytes (10)
EXPECTED_STATUS_BYTES = {
    STATUS_OPCODE_EXACT: 70,
    STATUS_MODIFIED: 4_300,
    STATUS_DIVERGENT: 550,
}
EXPECTED_INTERIOR_NOP_BYTES = 10

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(\S+)(.*)$")


class ClusterRecoveryError(RuntimeError):
    """Raised when cluster recovery evidence or invariants change."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_stock_stream(application_objdump: Path) -> dict[int, tuple[str, str]]:
    application_objdump = application_objdump.resolve()
    if (
        hashlib.sha256(application_objdump.read_bytes()).hexdigest()
        != discovery.EXPECTED_APPLICATION_OBJDUMP_SHA256
    ):
        raise ClusterRecoveryError("authenticated EM9305 application objdump changed")
    stream: dict[int, tuple[str, str]] = {}
    for line in application_objdump.read_text().splitlines():
        match = LINE_RE.match(line)
        if match:
            stream[int(match.group(1), 16)] = (match.group(3), match.group(4).strip())
    if not stream:
        raise ClusterRecoveryError("authenticated objdump decoded no instructions")
    return stream


def load_objects(objects_path: Path) -> dict[str, Any]:
    objects_path = objects_path.resolve()
    raw = objects_path.read_bytes()
    if sha256(raw) != OBJECTS_SHA256:
        raise ClusterRecoveryError("cluster object-disassembly return identity changed")
    report = json.loads(raw)
    identity = report["identity"]
    if (
        identity["archive_sha256"] != ARCHIVE_SHA256
        or identity["archive_git_blob"] != ARCHIVE_GIT_BLOB
        or identity["application_objdump_sha256"]
        != discovery.EXPECTED_APPLICATION_OBJDUMP_SHA256
    ):
        raise ClusterRecoveryError("cluster object-return archive identity changed")
    return report


def archive_stream(report: dict[str, Any], name: str, object_name: str) -> list[str]:
    functions = report["objects"][object_name]["functions"]
    matches = [f for f in functions if f["name"] == name]
    if len(matches) != 1 or not matches[0]["instructions"]:
        raise ClusterRecoveryError(f"archive function disassembly changed: {name}")
    return [insn["mnemonic"] for insn in matches[0]["instructions"]]


def analyze(
    *,
    image: Path = DEFAULT_IMAGE,
    application_objdump: Path = DEFAULT_OBJDUMP,
    objects_path: Path = DEFAULT_OBJECTS,
) -> dict[str, Any]:
    image_bytes = image.resolve().read_bytes()
    if sha256(image_bytes) != IMAGE_SHA256:
        raise ClusterRecoveryError("official EM9305 firmware identity changed")
    stock = load_stock_stream(application_objdump)
    objects_report = load_objects(objects_path)

    all_functions: list[dict[str, Any]] = []
    for cluster in CLUSTERS:
        start, end = cluster["start"], cluster["end"]
        segment = image_bytes[start - PACKAGE_MAP_BASE:end - PACKAGE_MAP_BASE]
        if sha256(segment) != cluster["segment_sha256"]:
            raise ClusterRecoveryError(
                f"cluster segment identity changed at 0x{start:08X}"
            )
        # Interior padding must be exactly ARC nop_s (E0 78).
        for nop_address in cluster["interior_nops"]:
            if image_bytes[nop_address - PACKAGE_MAP_BASE:nop_address - PACKAGE_MAP_BASE + 2] != b"\xe0\x78":
                raise ClusterRecoveryError(
                    f"cluster interior padding changed at 0x{nop_address:08X}"
                )
        # Exact tiling: functions plus interior NOPs cover the segment.
        covered = sum(
            cluster["functions"][index + 1][0] - address
            for index, (address, *_rest) in enumerate(cluster["functions"][:-1])
        ) + (end - cluster["functions"][-1][0])
        if covered != end - start or covered != sum(
            (cluster["functions"][i + 1][0] if i + 1 < len(cluster["functions"]) else end)
            - address
            for i, (address, *_r) in enumerate(cluster["functions"])
        ):
            raise ClusterRecoveryError(f"cluster tiling broken at 0x{start:08X}")
        nop_bytes = 2 * len(cluster["interior_nops"])
        function_bytes = covered - nop_bytes
        if function_bytes + nop_bytes != end - start:
            raise ClusterRecoveryError(f"cluster coverage broken at 0x{start:08X}")

        for (address, name, object_name, archive_size, metrics, status, extras) in cluster["functions"]:
            index = [f[0] for f in cluster["functions"]].index(address)
            span_end = (
                cluster["functions"][index + 1][0]
                if index + 1 < len(cluster["functions"])
                else end
            )
            # Trailing interior NOPs belong to the gap, not the body.
            body_end = span_end
            while body_end - 2 in cluster["interior_nops"]:
                body_end -= 2
            archive = archive_stream(objects_report, name, object_name)
            stock_mnemonics = [
                stock[a][0] for a in sorted(stock) if address <= a < body_end
            ]
            matcher = SequenceMatcher(None, archive, stock_mnemonics, autojunk=False)
            blocks = [b for b in matcher.get_matching_blocks() if b.size]
            observed = (
                len(archive),
                len(stock_mnemonics),
                sum(b.size for b in blocks),
                max((b.size for b in blocks), default=0),
            )
            if observed != metrics:
                raise ClusterRecoveryError(
                    f"cluster opcode alignment changed for {name}: {observed} != {metrics}"
                )
            ratio = matcher.ratio()
            if status == STATUS_OPCODE_EXACT and observed[2] != observed[0]:
                raise ClusterRecoveryError(f"opcode-exact status drifted for {name}")
            if status == STATUS_MODIFIED and ratio < MODIFIED_RATIO_FLOOR:
                raise ClusterRecoveryError(f"modified ratio floor violated for {name}")
            if status == STATUS_DIVERGENT and ratio >= MODIFIED_RATIO_FLOOR:
                raise ClusterRecoveryError(f"divergent status drifted for {name}")
            all_functions.append({
                "cluster": cluster["name"],
                "address": address,
                "end": body_end,
                "size": body_end - address,
                "sha256": sha256(
                    image_bytes[address - PACKAGE_MAP_BASE:body_end - PACKAGE_MAP_BASE]
                ),
                "name": name,
                "object": object_name,
                "archive_size": archive_size,
                "archive_instruction_count": observed[0],
                "stock_instruction_count": observed[1],
                "matching_instruction_count": observed[2],
                "longest_matching_instruction_run": observed[3],
                "sequence_ratio": round(ratio, 6),
                "status": status,
                "evidence": [
                    f"link_order_bracket:{cluster['left_anchor']}->{cluster['right_anchor']}",
                    f"opcode_alignment:{observed[2]}/{observed[0]}",
                    *extras,
                ],
            })

    # Pinned evidence for the two divergent bodies.
    tx = next(f for f in all_functions if f["name"] == "lctrSlvConnTxCompletion")
    stock_operands = " ".join(
        stock[a][1] for a in sorted(stock) if tx["address"] <= a < tx["end"]
    )
    if (
        "341" not in stock_operands
        or "630" not in stock_operands
        or "0x80568c" not in stock_operands
        or "0xa" not in stock_operands
    ):
        raise ClusterRecoveryError("TxCompletion divergent-body constant evidence changed")
    abort_op = next(f for f in all_functions if f["name"] == "lctrMstPerScanWithRspAbortOp")
    abort_operands = " ".join(
        stock[a][1] for a in sorted(stock) if abort_op["address"] <= a < abort_op["end"]
    )
    if "0x32233c" not in abort_operands:
        raise ClusterRecoveryError("AbortOp relocation-target evidence changed")

    status_counts = Counter(f["status"] for f in all_functions)
    status_bytes = Counter()
    for f in all_functions:
        status_bytes[f["status"]] += f["size"]
    if (
        len(all_functions) != EXPECTED_FUNCTION_COUNT
        or dict(status_counts) != EXPECTED_STATUS_COUNTS
        or dict(status_bytes) != EXPECTED_STATUS_BYTES
        or sum(f["size"] for f in all_functions) != EXPECTED_IDENTIFIED_BYTES
    ):
        raise ClusterRecoveryError(
            f"cluster recovery census changed: {dict(status_counts)} / {dict(status_bytes)}"
        )

    return {
        "clusters": [
            {
                "name": cluster["name"],
                "start": cluster["start"],
                "end": cluster["end"],
                "size": cluster["end"] - cluster["start"],
                "segment_sha256": cluster["segment_sha256"],
                "left_anchor": cluster["left_anchor"],
                "right_anchor": cluster["right_anchor"],
                "interior_nop_addresses": list(cluster["interior_nops"]),
            }
            for cluster in CLUSTERS
        ],
        "functions": all_functions,
        "function_count": len(all_functions),
        "status_counts": dict(status_counts),
        "status_bytes": dict(status_bytes),
        "identified_function_bytes": sum(f["size"] for f in all_functions),
        "interior_nop_bytes": EXPECTED_INTERIOR_NOP_BYTES,
        "ownership_category": "proprietary_modern_controller_source_unavailable",
        "retention_recommendation": (
            "all ten functions remain hash-pinned stock retentions behind the "
            "declared EM9305 controller boundary; opcode-sequence identity with "
            "the license-gated SDK oracle does not grant source availability"
        ),
    }


def format_tsv(report: dict[str, Any]) -> str:
    lines = [
        "cluster\tstart\tend\tsize\tsha256\tname\tobject\tarchive_size\t"
        "status\tarchive_insns\tstock_insns\tmatched\tlongest_run\tsequence_ratio\tevidence"
    ]
    for f in report["functions"]:
        lines.append("\t".join((
            f["cluster"],
            f"0x{f['address']:08X}",
            f"0x{f['end']:08X}",
            str(f["size"]),
            f["sha256"],
            f["name"],
            f["object"],
            str(f["archive_size"]),
            f["status"],
            str(f["archive_instruction_count"]),
            str(f["stock_instruction_count"]),
            str(f["matching_instruction_count"]),
            str(f["longest_matching_instruction_run"]),
            f"{f['sequence_ratio']:.6f}",
            ";".join(f["evidence"]),
        )))
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--application-objdump", type=Path, default=DEFAULT_OBJDUMP)
    parser.add_argument("--objects", type=Path, default=DEFAULT_OBJECTS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--tsv", type=Path, help="write the cluster function map TSV")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(
        image=args.image,
        application_objdump=args.application_objdump,
        objects_path=args.objects,
    )
    if args.tsv:
        args.tsv.write_text(format_tsv(report))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 controller cluster recovery: PASS")
        print(json.dumps(
            {k: v for k, v in report.items() if k not in {"functions", "clusters"}},
            indent=2,
            sort_keys=True,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
