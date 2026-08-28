#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit raw executable encodings in production-routed overlay sources."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOLLO_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
APOLLO_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
COMPONENT_ROOT = ROOT / "components"
MANIFEST = ROOT / "tools/manifests/g2-production-raw-encoding-quality.tsv"
SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"

DIRECTIVE = re.compile(r"\.(byte|short|hword|word)\s+([^\"\\]+)")
WIDTH = {"byte": 1, "short": 2, "hword": 2, "word": 4}

# path: (component, routed bytes, raw instruction bytes, semantic literal bytes,
# remediation)
EXPECTED = {
    "components/apollo_main/core_overlay/duration_delay.c":
        ("apollo_main", 120, 0, 12, "retain the three typed literal constants; all branches are symbolic source assembly"),
    "components/bootloader/core_overlay/runtime_thread_pointer_422874.c":
        ("apollo_bootloader", 8, 0, 4, "retain the typed address literal; surrounding instructions are mnemonic assembly"),
}

APOLLO_FUNCTIONS = {
    "components/apollo_main/core_overlay/duration_delay.c": (
        "open_cfw_delay_cycles", "open_cfw_delay_us", "open_cfw_delay_ms",
        "open_cfw_delay_us_passthrough",
    ),
}

# These files were executable stock bytes rendered as C ``.byte`` directives.
# They are intentionally absent from the public tree.  The digest-only records
# preserve the audit trail without redistributing the transcription.
REMOVED_TRANSCRIPTS = {
    "components/bootloader/core_overlay/runtime_mspi_configure_424af0.c":
        (1561, "ec17fa6c195b86a0b5cb7e8760b7af3be8cee47481ad837a391e4f53d090de04", 228),
    "components/bootloader/core_overlay/runtime_mspi_control_4251c0.c":
        (24638, "b46f494c5e4b35a64fa9a13c6d256c720f413a4aa29a57f0b9ffdcb636d5a696", 4384),
    "components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c":
        (13020, "93c96cb310ed58bc5f06bb048a321bf3dd4943215bd466d357decff102b53e46", 1902),
    "components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c":
        (6904, "c8754d994052a0b582a8a1ff377653492488b492138c3ac579afd3d944726725", 1154),
    "components/bootloader/core_overlay/runtime_mspi_initialize_424a5a.c":
        (1071, "4a52d4f85a7179932b25814d9109e729d19744322f09787aa4ff61bb8bb6ce41", 144),
    "components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c":
        (2266, "d9f5ce663da4ca56241e345d636021d700b8e99011c36c135783284729e873c2", 312),
    "components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c":
        (1814, "334adbc65bf4dc2e8c53442a5be2caca1808933cf8d9c62227ae326377d678c5", 232),
    "components/bootloader/core_overlay/runtime_mspi_transfer_interrupt_4262e0.c":
        (3798, "1b800153d9619810fa31a3186e003fbbf4902aadf3c95b36338bca2eaa630855", 546),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _directive_bytes(text: str) -> dict[str, int]:
    result = {name: 0 for name in WIDTH}
    for match in DIRECTIVE.finditer(text):
        operands = [value.strip() for value in match.group(2).split(",")
                    if value.strip()]
        require(bool(operands), "empty raw assembler directive")
        result[match.group(1)] += WIDTH[match.group(1)] * len(operands)
    return result


def _boot_routed_bytes(overlay: dict) -> dict[str, int]:
    result: dict[str, int] = {}
    for group in ("in_place_leaves", "cave_leaves", "relocated_leaves"):
        for row in overlay.get(group, []):
            path = row.get("source", {}).get("path")
            if not path:
                continue
            result[path] = result.get(path, 0) + int(row["expected"]["size"])
    return result


def analyze() -> dict:
    apollo_overlay = json.loads(APOLLO_OVERLAY.read_text())
    apollo_report = json.loads(APOLLO_REPORT.read_text())
    boot_overlay = json.loads(BOOT_OVERLAY.read_text())
    apollo_sources = {row["path"] for row in apollo_overlay["sources"]}
    apollo_symbols = apollo_report["overlay"]["functions"]
    boot_routed = _boot_routed_bytes(boot_overlay)

    for relative in REMOVED_TRANSCRIPTS:
        require(not (ROOT / relative).exists(),
                f"removed executable transcript returned to public source: {relative}")
        require(relative not in boot_routed,
                f"removed executable transcript returned to production routing: {relative}")

    for path, functions in APOLLO_FUNCTIONS.items():
        require(path in apollo_sources, f"Apollo raw-directive source is no longer routed: {path}")
        routed = sum(int(apollo_symbols[name]["size"]) for name in functions)
        require(routed == EXPECTED[path][1], f"Apollo routed-byte total changed: {path}")

    rows = []
    discovered = set()
    routed_source_paths = apollo_sources | set(boot_routed)
    for relative in sorted(routed_source_paths):
        path = ROOT / relative
        if not path.is_file() or path.suffix not in {".c", ".h", ".S", ".s", ".asm"}:
            continue
        directive_bytes = _directive_bytes(path.read_text())
        total = sum(directive_bytes.values())
        if total == 0:
            continue
        discovered.add(relative)
        require(relative in EXPECTED, f"unclassified production raw directive source: {relative}")
        component, routed, raw, literal, remediation = EXPECTED[relative]
        if component == "apollo_bootloader":
            require(boot_routed.get(relative) == routed,
                    f"bootloader routed-byte total changed: {relative}")
        require(total == raw + literal,
                f"directive-byte classification changed: {relative}")
        rows.append({
            "component": component,
            "source": relative,
            "routed_source_bytes": routed,
            "directive_bytes": total,
            "raw_instruction_transcription_bytes": raw,
            "semantic_literal_bytes": literal,
            "byte_directive_bytes": directive_bytes["byte"],
            "short_or_hword_directive_bytes": (
                directive_bytes["short"] + directive_bytes["hword"]),
            "word_directive_bytes": directive_bytes["word"],
            "source_sha256": sha256(path.read_bytes()),
            "source_ownership_disposition": (
                "overstated_until_remediated" if raw else
                "legitimate_typed_literal_data"),
            "remediation": remediation,
        })

    require(discovered == set(EXPECTED),
            "production raw-directive source census changed")
    public_directive_sources = set()
    for path in COMPONENT_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".c", ".h", ".S", ".s", ".asm"}:
            continue
        directive_bytes = _directive_bytes(path.read_text())
        if not sum(directive_bytes.values()):
            continue
        relative = path.relative_to(ROOT).as_posix()
        public_directive_sources.add(relative)
        require(directive_bytes["byte"] == 0,
                f"public source contains executable .byte transcription: {relative}")
        require(directive_bytes["short"] + directive_bytes["hword"] == 0,
                f"public source contains raw instruction halfwords: {relative}")
    require(public_directive_sources == set(EXPECTED),
            "public component raw-directive source census changed")
    metrics = {
        "production_routed_sources_with_directives": len(rows),
        "routed_source_bytes_in_affected_sources": sum(
            row["routed_source_bytes"] for row in rows),
        "directive_bytes": sum(row["directive_bytes"] for row in rows),
        "raw_instruction_transcription_bytes": sum(
            row["raw_instruction_transcription_bytes"] for row in rows),
        "semantic_literal_bytes": sum(
            row["semantic_literal_bytes"] for row in rows),
        "source_owned_bytes_currently_overstated": sum(
            row["raw_instruction_transcription_bytes"] for row in rows),
        "fully_raw_byte_body_bytes": sum(
            row["byte_directive_bytes"] for row in rows),
        "public_raw_executable_transcript_files": 0,
        "removed_public_transcript_files": len(REMOVED_TRANSCRIPTS),
        "removed_public_transcript_executable_bytes": sum(
            row[2] for row in REMOVED_TRANSCRIPTS.values()),
    }
    require(metrics == {
        "production_routed_sources_with_directives": 2,
        "routed_source_bytes_in_affected_sources": 128,
        "directive_bytes": 16,
        "raw_instruction_transcription_bytes": 0,
        "semantic_literal_bytes": 16,
        "source_owned_bytes_currently_overstated": 0,
        "fully_raw_byte_body_bytes": 0,
        "public_raw_executable_transcript_files": 0,
        "removed_public_transcript_files": 8,
        "removed_public_transcript_executable_bytes": 8902,
    }, "production raw-encoding totals changed")
    return {
        "schema_version": 1,
        "analysis_mode": "offline source/overlay quality audit; no build, hardware, MMIO, reset, flashing, signing, or production mutation",
        "quality_gate": "fail_closed_raw_instruction_transcription_not_source_owned",
        "classification_complete": True,
        "source_ownership_suitable": (
            metrics["source_owned_bytes_currently_overstated"] == 0
            and metrics["public_raw_executable_transcript_files"] == 0
        ),
        "public_source_scope_clean": True,
        "removed_public_transcript_boundaries": [
            {
                "path": path,
                "deleted_source_text_bytes": record[0],
                "deleted_source_sha256": record[1],
                "retained_official_executable_bytes": record[2],
                "disposition": "absent_from_public_source_and_production_routing; authenticated official bytes retained",
            }
            for path, record in sorted(REMOVED_TRANSCRIPTS.items())
        ],
        "hardware_validation": "deferred by project direction",
        "production_files_modified": [],
        "metrics": metrics,
        "rows": rows,
    }


def write_manifests(result: dict) -> list[Path]:
    with MANIFEST.open("w", newline="") as handle:
        fields = list(result["rows"][0])
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        handle.write("# SPDX-License-Identifier: MIT\n")
        writer.writeheader()
        writer.writerows(result["rows"])
    summary = {key: value for key, value in result.items() if key != "rows"}
    summary["row_count"] = len(result["rows"])
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return [MANIFEST, SUMMARY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Production raw-encoding quality audit failed: {exc}") from exc
