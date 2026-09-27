#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Describe the still-opaque charging-case residual code/data rows.

This is deliberately a shape audit, not source admission. It starts from the
byte-accounting manifest's `residual_unresolved_code_or_data` rows and records
which rows are word-table-like, cleanly Thumb-decodable, odd/mixed fragments, or
tiny separators. The result gives the next source-recovery pass a closed work
queue without moving any byte out of retained/opaque status.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "tools/manifests"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
BYTE_ACCOUNTING = MANIFEST_DIR / "g2-case-byte-accounting.tsv"
SUMMARY = MANIFEST_DIR / "g2-case-byte-accounting-summary.json"
ROWS_OUT = MANIFEST_DIR / "g2-case-residual-shape.tsv"
TARGETS_OUT = MANIFEST_DIR / "g2-case-residual-control-flow-targets.tsv"
RECOVERY_OUT = MANIFEST_DIR / "g2-case-residual-recovery-queue.tsv"
RECOVERY_ROWS_OUT = MANIFEST_DIR / "g2-case-residual-recovery-rows.tsv"
NON_TARGET_ROWS_OUT = MANIFEST_DIR / "g2-case-residual-non-target-rows.tsv"
ENTRY_CANDIDATES_OUT = MANIFEST_DIR / "g2-case-residual-entry-candidates.tsv"
SUMMARY_OUT = MANIFEST_DIR / "g2-case-residual-shape-summary.json"

APP_BASE = 0x08000000
WRAPPER = 32
APP_BYTES = 55752
EXPECTED_BYTE_ACCOUNTING_DIGEST = (
    "1bba69f30997ff95cfef326a8109d11fbaf8bf38691a81d0a22e6296d385cfc9"
)


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t"))


def _thumb_decode(body: bytes, address: int) -> dict[str, object]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    md.detail = True
    decoded_bytes = 0
    instructions = 0
    first = ""
    last = ""
    branch_count = 0
    call_count = 0
    targets: set[int] = set()
    for insn in md.disasm(body, address):
        if insn.address != address + decoded_bytes:
            break
        text = f"{insn.mnemonic} {insn.op_str}".strip()
        first = first or text
        last = text
        mnemonic = insn.mnemonic.lower()
        if mnemonic.startswith("b"):
            branch_count += 1
        if mnemonic in {"bl", "blx"}:
            call_count += 1
        if (mnemonic.startswith("b") or mnemonic in {"bl", "blx"}) and insn.operands:
            operand = insn.operands[0]
            if operand.type == ARM_OP_IMM:
                target = int(operand.imm)
                if APP_BASE <= (target & ~1) < APP_BASE + APP_BYTES:
                    targets.add(target & ~1)
        decoded_bytes += insn.size
        instructions += 1
    return {
        "decoded_bytes": decoded_bytes,
        "instructions": instructions,
        "first": first,
        "last": last,
        "branch_count": branch_count,
        "call_count": call_count,
        "in_app_targets": sorted(targets),
    }


def _word_table_score(body: bytes) -> tuple[int, int, int]:
    if len(body) < 8 or len(body) % 4:
        return 0, 0, 0
    words = [
        int.from_bytes(body[index:index + 4], "little")
        for index in range(0, len(body), 4)
    ]
    flash_words = sum(1 for word in words if APP_BASE <= (word & ~1) <
                      APP_BASE + APP_BYTES)
    sram_words = sum(1 for word in words if 0x20000000 <= word < 0x20024000)
    small_words = sum(1 for word in words if word <= 0xFFFF)
    return flash_words, sram_words, small_words


def _shape(row: dict[str, str], app: bytes) -> dict[str, object]:
    start = int(row["start"], 16)
    end = int(row["end_exclusive"], 16)
    body = app[start - APP_BASE:end - APP_BASE]
    require(len(body) == int(row["bytes"]), "residual row length mismatch")
    decode = _thumb_decode(body, start)
    decoded_bytes = int(decode["decoded_bytes"])
    instructions = int(decode["instructions"])
    flash_words, sram_words, small_words = _word_table_score(body)
    word_count = len(body) // 4 if len(body) % 4 == 0 else 0
    word_like = word_count > 0 and (
        flash_words + sram_words >= max(2, word_count // 2) or
        small_words >= max(2, (word_count * 3) // 4)
    )
    thumb_complete = (
        start % 2 == 0 and len(body) % 2 == 0 and
        decoded_bytes == len(body) and instructions > 0
    )
    if len(body) < 8:
        classification = "tiny_separator_or_inline_operand"
    elif word_like:
        classification = "word_table_candidate"
    elif thumb_complete:
        classification = "thumb_decode_complete_candidate"
    else:
        classification = "mixed_or_odd_fragment"
    return {
        "start": start,
        "end": end,
        "bytes": len(body),
        "classification": classification,
        "content_sha256": row["content_sha256"],
        "thumb_decoded_bytes": decoded_bytes,
        "thumb_instruction_count": instructions,
        "thumb_first": decode["first"],
        "thumb_last": decode["last"],
        "thumb_branch_count": decode["branch_count"],
        "thumb_call_count": decode["call_count"],
        "thumb_in_app_targets": [
            f"0x{target:08X}" for target in decode["in_app_targets"]
        ],
        "word_count": word_count,
        "flash_pointer_words": flash_words,
        "sram_pointer_words": sram_words,
        "small_immediate_words": small_words,
    }


def _locate_target(target: str, accounting_rows: list[dict[str, str]]) -> dict[str, object]:
    address = int(target, 16)
    for row in accounting_rows:
        start = int(row["start"], 16)
        end = int(row["end_exclusive"], 16)
        if start <= address < end:
            offset = address - start
            if offset == 0:
                relation = "row_start"
            elif address + 2 == end:
                relation = "row_tail_halfword"
            else:
                relation = "row_interior"
            return {
                "target": target,
                "target_bucket": row["category"],
                "target_row_start": f"0x{start:08X}",
                "target_row_end": f"0x{end:08X}",
                "target_row_offset": offset,
                "target_row_relation": relation,
            }
    raise AuditError(f"target {target} is outside byte-accounting rows")


def _recovery_priority(row: dict[str, object]) -> int:
    refs = int(row["referencing_rows"])
    relation = str(row["target_row_relation"])
    if relation == "row_start":
        return 3000 + refs
    if relation == "row_interior":
        offset = int(row["target_row_offset"])
        if offset % 2 == 0:
            return 2000 + refs
        return 1000 + refs
    return 500 + refs


def analyze() -> dict[str, object]:
    raw_accounting = BYTE_ACCOUNTING.read_bytes()
    require(sha256(raw_accounting) == EXPECTED_BYTE_ACCOUNTING_DIGEST,
            "case byte-accounting manifest identity changed")
    accounting_summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    blob = BLOB.read_bytes()
    app = blob[WRAPPER:]
    require(len(app) == APP_BYTES, "case application size changed")
    accounting_rows = _read_tsv(BYTE_ACCOUNTING)
    rows = [
        _shape(row, app)
        for row in accounting_rows
        if row["category"] == "residual_unresolved_code_or_data"
    ]
    total_bytes = sum(row["bytes"] for row in rows)
    require(len(rows) == 0 and total_bytes == 0,
            "case residual unresolved baseline changed")
    require(
        accounting_summary["metrics"]["residual_unresolved_code_or_data_bytes"] ==
        total_bytes,
        "case residual unresolved summary baseline changed")
    class_bytes: dict[str, int] = {}
    class_rows: dict[str, int] = {}
    targets: set[str] = set()
    target_refs: dict[str, int] = {}
    branch_count = 0
    call_count = 0
    for row in rows:
        key = str(row["classification"])
        class_bytes[key] = class_bytes.get(key, 0) + int(row["bytes"])
        class_rows[key] = class_rows.get(key, 0) + 1
        targets.update(row["thumb_in_app_targets"])
        for target in row["thumb_in_app_targets"]:
            target_refs[target] = target_refs.get(target, 0) + 1
        branch_count += int(row["thumb_branch_count"])
        call_count += int(row["thumb_call_count"])
    target_rows = []
    target_bucket_counts: dict[str, int] = {}
    target_relation_counts: dict[str, int] = {}
    for target in sorted(target_refs):
        located = _locate_target(target, accounting_rows)
        located["referencing_rows"] = target_refs[target]
        located["recovery_priority"] = _recovery_priority(located)
        target_rows.append(located)
        bucket = str(located["target_bucket"])
        relation = str(located["target_row_relation"])
        target_bucket_counts[bucket] = target_bucket_counts.get(bucket, 0) + 1
        target_relation_counts[relation] = (
            target_relation_counts.get(relation, 0) + 1)
    rows_digest = sha256(json.dumps(
        rows, sort_keys=True, separators=(",", ":")
    ).encode())
    recovery_rows = [
        row for row in target_rows
        if row["target_bucket"] == "residual_unresolved_code_or_data"
    ]
    recovery_rows = sorted(
        recovery_rows,
        key=lambda row: (
            -int(row["recovery_priority"]),
            -int(row["referencing_rows"]),
            row["target"],
        ),
    )
    recovery_digest = sha256(json.dumps(
        recovery_rows, sort_keys=True, separators=(",", ":")
    ).encode())
    recovery_by_row: dict[str, dict[str, object]] = {}
    shape_by_start = {
        f"0x{int(row['start']):08X}": row
        for row in rows
    }
    for target in recovery_rows:
        start = str(target["target_row_start"])
        shape = shape_by_start[start]
        group = recovery_by_row.setdefault(start, {
            "target_row_start": start,
            "target_row_end": target["target_row_end"],
            "bytes": shape["bytes"],
            "classification": shape["classification"],
            "thumb_decoded_bytes": shape["thumb_decoded_bytes"],
            "thumb_instruction_count": shape["thumb_instruction_count"],
            "target_count": 0,
            "referencing_rows_total": 0,
            "row_start_targets": 0,
            "interior_targets": 0,
            "tail_halfword_targets": 0,
            "top_target": target["target"],
            "top_target_referencing_rows": target["referencing_rows"],
        })
        group["target_count"] = int(group["target_count"]) + 1
        group["referencing_rows_total"] = (
            int(group["referencing_rows_total"]) +
            int(target["referencing_rows"]))
        relation = str(target["target_row_relation"])
        if relation == "row_start":
            group["row_start_targets"] = int(group["row_start_targets"]) + 1
        elif relation == "row_tail_halfword":
            group["tail_halfword_targets"] = (
                int(group["tail_halfword_targets"]) + 1)
        else:
            group["interior_targets"] = int(group["interior_targets"]) + 1
    recovery_row_groups = sorted(
        recovery_by_row.values(),
        key=lambda row: (
            -int(row["referencing_rows_total"]),
            -int(row["target_count"]),
            row["target_row_start"],
        ),
    )
    for rank, row in enumerate(recovery_row_groups, 1):
        row["rank"] = rank
    recovery_rows_digest = sha256(json.dumps(
        recovery_row_groups, sort_keys=True, separators=(",", ":")
    ).encode())
    recovery_row_bytes = sum(int(row["bytes"]) for row in recovery_row_groups)
    recovery_class_rows: dict[str, int] = {}
    recovery_class_bytes: dict[str, int] = {}
    for row in recovery_row_groups:
        key = str(row["classification"])
        recovery_class_rows[key] = recovery_class_rows.get(key, 0) + 1
        recovery_class_bytes[key] = (
            recovery_class_bytes.get(key, 0) + int(row["bytes"]))
    recovery_starts = {str(row["target_row_start"]) for row in recovery_row_groups}
    non_target_rows = [
        {
            "start": f"0x{int(row['start']):08X}",
            "end": f"0x{int(row['end']):08X}",
            "bytes": row["bytes"],
            "classification": row["classification"],
            "thumb_decoded_bytes": row["thumb_decoded_bytes"],
            "thumb_instruction_count": row["thumb_instruction_count"],
            "content_sha256": row["content_sha256"],
        }
        for row in rows
        if f"0x{int(row['start']):08X}" not in recovery_starts
    ]
    non_target_rows = sorted(
        non_target_rows,
        key=lambda row: (-int(row["bytes"]), row["start"]),
    )
    non_target_class_rows: dict[str, int] = {}
    non_target_class_bytes: dict[str, int] = {}
    for row in non_target_rows:
        key = str(row["classification"])
        non_target_class_rows[key] = non_target_class_rows.get(key, 0) + 1
        non_target_class_bytes[key] = (
            non_target_class_bytes.get(key, 0) + int(row["bytes"]))
    non_target_rows_digest = sha256(json.dumps(
        non_target_rows, sort_keys=True, separators=(",", ":")
    ).encode())
    non_target_row_bytes = sum(int(row["bytes"]) for row in non_target_rows)
    require(recovery_row_bytes + non_target_row_bytes == total_bytes,
            "residual recovery/non-target partition does not conserve bytes")
    for key, total in class_rows.items():
        require(recovery_class_rows.get(key, 0) +
                non_target_class_rows.get(key, 0) == total,
                f"residual row class partition changed for {key}")
    for key, total in class_bytes.items():
        require(recovery_class_bytes.get(key, 0) +
                non_target_class_bytes.get(key, 0) == total,
                f"residual byte class partition changed for {key}")
    residual_partition = {
        "target_bearing_rows": len(recovery_row_groups),
        "target_bearing_bytes": recovery_row_bytes,
        "non_target_rows": len(non_target_rows),
        "non_target_bytes": non_target_row_bytes,
        "total_rows": len(recovery_row_groups) + len(non_target_rows),
        "total_bytes": recovery_row_bytes + non_target_row_bytes,
    }
    residual_partition_digest = sha256(json.dumps(
        residual_partition, sort_keys=True, separators=(",", ":")
    ).encode())
    entry_candidate_rows = [
        row for row in recovery_row_groups
        if int(row["row_start_targets"]) > 0
    ]
    entry_candidate_rows = sorted(
        entry_candidate_rows,
        key=lambda row: (
            -int(row["top_target_referencing_rows"]),
            -int(row["referencing_rows_total"]),
            row["target_row_start"],
        ),
    )
    for rank, row in enumerate(entry_candidate_rows, 1):
        row["entry_rank"] = rank
    entry_class_rows: dict[str, int] = {}
    entry_class_bytes: dict[str, int] = {}
    for row in entry_candidate_rows:
        key = str(row["classification"])
        entry_class_rows[key] = entry_class_rows.get(key, 0) + 1
        entry_class_bytes[key] = entry_class_bytes.get(key, 0) + int(row["bytes"])
    entry_candidate_digest = sha256(json.dumps(
        entry_candidate_rows, sort_keys=True, separators=(",", ":")
    ).encode())
    return {
        "schema_version": 1,
        "component": "G2 charging-case residual_unresolved_code_or_data shape audit",
        "byte_accounting_sha256": EXPECTED_BYTE_ACCOUNTING_DIGEST,
        "row_count": len(rows),
        "total_bytes": total_bytes,
        "class_rows": class_rows,
        "class_bytes": class_bytes,
        "thumb_branch_count": branch_count,
        "thumb_call_count": call_count,
        "thumb_in_app_target_count": len(targets),
        "thumb_in_app_target_bucket_counts": target_bucket_counts,
        "thumb_in_app_target_relation_counts": target_relation_counts,
        "thumb_in_app_targets_digest": sha256(json.dumps(
            sorted(targets), separators=(",", ":")
        ).encode()),
        "thumb_in_app_target_refs_digest": sha256(json.dumps(
            target_rows, sort_keys=True, separators=(",", ":")
        ).encode()),
        "residual_recovery_target_count": len(recovery_rows),
        "residual_recovery_queue_digest": recovery_digest,
        "residual_recovery_row_count": len(recovery_row_groups),
        "residual_recovery_row_bytes": recovery_row_bytes,
        "residual_recovery_class_rows": recovery_class_rows,
        "residual_recovery_class_bytes": recovery_class_bytes,
        "residual_recovery_rows_digest": recovery_rows_digest,
        "residual_non_target_row_count": len(non_target_rows),
        "residual_non_target_row_bytes": non_target_row_bytes,
        "residual_non_target_class_rows": non_target_class_rows,
        "residual_non_target_class_bytes": non_target_class_bytes,
        "residual_non_target_rows_digest": non_target_rows_digest,
        "residual_partition": residual_partition,
        "residual_partition_digest": residual_partition_digest,
        "residual_entry_candidate_count": len(entry_candidate_rows),
        "residual_entry_candidate_bytes":
            sum(int(row["bytes"]) for row in entry_candidate_rows),
        "residual_entry_candidate_class_rows": entry_class_rows,
        "residual_entry_candidate_class_bytes": entry_class_bytes,
        "residual_entry_candidates_digest": entry_candidate_digest,
        "rows_digest": rows_digest,
        "source_admission": False,
        "production_routed": False,
        "target_rows": target_rows,
        "recovery_rows": recovery_rows,
        "recovery_row_groups": recovery_row_groups,
        "non_target_rows": non_target_rows,
        "entry_candidate_rows": entry_candidate_rows,
        "rows": rows,
    }


def write_manifests(result: dict[str, object]) -> list[Path]:
    with ROWS_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "start", "end_exclusive", "bytes", "classification",
            "content_sha256", "thumb_decoded_bytes", "thumb_instruction_count",
            "thumb_first", "thumb_last", "thumb_branch_count",
            "thumb_call_count", "thumb_in_app_targets", "word_count",
            "flash_pointer_words", "sram_pointer_words",
            "small_immediate_words",
        ])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['start']:08X}", f"0x{row['end']:08X}",
                row["bytes"], row["classification"], row["content_sha256"],
                row["thumb_decoded_bytes"], row["thumb_instruction_count"],
                row["thumb_first"], row["thumb_last"],
                row["thumb_branch_count"], row["thumb_call_count"],
                ";".join(row["thumb_in_app_targets"]),
                row["word_count"], row["flash_pointer_words"],
                row["sram_pointer_words"], row["small_immediate_words"],
            ])
    with TARGETS_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "target", "referencing_rows", "target_bucket",
            "target_row_start", "target_row_end", "target_row_offset",
            "target_row_relation", "recovery_priority",
        ])
        for row in result["target_rows"]:
            writer.writerow([
                row["target"], row["referencing_rows"], row["target_bucket"],
                row["target_row_start"], row["target_row_end"],
                row["target_row_offset"], row["target_row_relation"],
                row["recovery_priority"],
            ])
    with RECOVERY_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "rank", "target", "referencing_rows", "target_row_start",
            "target_row_end", "target_row_offset", "target_row_relation",
            "recovery_priority",
        ])
        for rank, row in enumerate(result["recovery_rows"], 1):
            writer.writerow([
                rank, row["target"], row["referencing_rows"],
                row["target_row_start"], row["target_row_end"],
                row["target_row_offset"], row["target_row_relation"],
                row["recovery_priority"],
            ])
    with RECOVERY_ROWS_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "rank", "target_row_start", "target_row_end", "target_count",
            "bytes", "classification", "thumb_decoded_bytes",
            "thumb_instruction_count", "referencing_rows_total",
            "row_start_targets",
            "interior_targets", "tail_halfword_targets", "top_target",
            "top_target_referencing_rows",
        ])
        for row in result["recovery_row_groups"]:
            writer.writerow([
                row["rank"], row["target_row_start"], row["target_row_end"],
                row["target_count"], row["bytes"], row["classification"],
                row["thumb_decoded_bytes"], row["thumb_instruction_count"],
                row["referencing_rows_total"],
                row["row_start_targets"], row["interior_targets"],
                row["tail_halfword_targets"], row["top_target"],
                row["top_target_referencing_rows"],
            ])
    with NON_TARGET_ROWS_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "rank", "start", "end_exclusive", "bytes", "classification",
            "thumb_decoded_bytes", "thumb_instruction_count",
            "content_sha256",
        ])
        for rank, row in enumerate(result["non_target_rows"], 1):
            writer.writerow([
                rank, row["start"], row["end"], row["bytes"],
                row["classification"], row["thumb_decoded_bytes"],
                row["thumb_instruction_count"], row["content_sha256"],
            ])
    with ENTRY_CANDIDATES_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "entry_rank", "target_row_start", "target_row_end", "bytes",
            "classification", "thumb_decoded_bytes", "thumb_instruction_count",
            "target_count", "referencing_rows_total", "top_target",
            "top_target_referencing_rows",
        ])
        for row in result["entry_candidate_rows"]:
            writer.writerow([
                row["entry_rank"], row["target_row_start"],
                row["target_row_end"], row["bytes"], row["classification"],
                row["thumb_decoded_bytes"], row["thumb_instruction_count"],
                row["target_count"], row["referencing_rows_total"],
                row["top_target"], row["top_target_referencing_rows"],
            ])
    slim = {key: value for key, value in result.items() if key != "rows"}
    slim = {key: value for key, value in slim.items()
            if key not in ("target_rows", "recovery_rows",
                           "recovery_row_groups", "non_target_rows",
                           "entry_candidate_rows")}
    SUMMARY_OUT.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [ROWS_OUT, TARGETS_OUT, RECOVERY_OUT, RECOVERY_ROWS_OUT,
            NON_TARGET_ROWS_OUT, ENTRY_CANDIDATES_OUT, SUMMARY_OUT]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps({k: result[k] for k in (
        "row_count", "total_bytes", "class_rows", "class_bytes",
        "thumb_branch_count", "thumb_call_count", "thumb_in_app_target_count",
        "thumb_in_app_target_bucket_counts",
        "thumb_in_app_target_relation_counts",
        "residual_recovery_target_count",
        "residual_recovery_queue_digest",
        "residual_recovery_row_count",
        "residual_recovery_row_bytes",
        "residual_recovery_class_rows",
        "residual_recovery_class_bytes",
        "residual_recovery_rows_digest",
        "residual_non_target_row_count",
        "residual_non_target_row_bytes",
        "residual_non_target_class_rows",
        "residual_non_target_class_bytes",
        "residual_non_target_rows_digest",
        "residual_partition",
        "residual_partition_digest",
        "residual_entry_candidate_count",
        "residual_entry_candidate_bytes",
        "residual_entry_candidate_class_rows",
        "residual_entry_candidate_class_bytes",
        "residual_entry_candidates_digest",
        "thumb_in_app_targets_digest", "thumb_in_app_target_refs_digest",
        "rows_digest")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case residual shape audit failed: {exc}") from exc
