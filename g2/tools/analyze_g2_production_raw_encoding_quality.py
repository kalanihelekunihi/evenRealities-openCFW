#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit raw executable encodings in production-routed overlay sources."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOLLO_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
APOLLO_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
COMPONENT_ROOT = ROOT / "components"
MANIFEST = ROOT / "tools/manifests/g2-production-raw-encoding-quality.tsv"
SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"

# A leading `(?!=)` excludes C99 designated-initializer/member-access syntax
# such as `{.word = value}` or `value.word = x`: real GNU-assembler directives
# are never followed by `=`, only by their operand list.
DIRECTIVE = re.compile(
    r"(?:^\s*|\"\s*)(?:[A-Za-z0-9_.$]+:\s*)?\."
    r"(byte|short|hword|word|inst(?:\.[A-Za-z0-9_]+)?)\s+"
    r"(?!=)([^\"\\]+)",
    re.MULTILINE,
)
WIDTH = {
    "byte": 1,
    "short": 2,
    "hword": 2,
    "word": 4,
    "inst": 4,
    "inst.n": 2,
    "inst.w": 4,
}

# path: (component, routed bytes, raw instruction bytes, semantic literal bytes,
# remediation)
EXPECTED = {
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59aa84.c":
        ("apollo_main", 2610, 518, 0,
         "replace the branch-heavy AM142 retained island transfer halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/duration_delay.c":
        ("apollo_main", 120, 0, 12, "retain the three typed literal constants; all branches are symbolic source assembly"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c800.c":
        ("apollo_main", 28, 8, 0,
         "replace the three PC-relative transfer halfwords with symbolic control flow once the surrounding AM142 span is closed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c820.c":
        ("apollo_main", 30, 8, 0,
         "replace the three branch halfwords and carried boundary halfword once the adjacent AM142 span is closed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c83e.c":
        ("apollo_main", 40, 4, 0,
         "replace the PC-relative BL halfwords with a symbolic call once the AM142 call target is source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c876.c":
        ("apollo_main", 266, 20, 0,
         "replace the cross-span helper-call halfwords with symbolic calls once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c1c4.c":
        ("apollo_main", 62, 4, 0,
         "replace the two outbound branch halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c204.c":
        ("apollo_main", 1416, 224, 0,
         "replace the branch-heavy limiter/selector, vector, and helper-call halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c7ac.c":
        ("apollo_main", 84, 16, 0,
         "replace the branch/call transfer halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b5c4.c":
        ("apollo_main", 196, 20, 0,
         "replace the helper-call halfwords with symbolic calls once the adjacent AM142 helper spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59c980.c":
        ("apollo_main", 172, 10, 0,
         "replace the helper-call and outbound branch halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59ca2c.c":
        ("apollo_main", 208, 22, 0,
         "replace the helper-call, outbound branch, and boundary halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b6d0.c":
        ("apollo_main", 66, 4, 0,
         "replace the PC-relative BL halfwords with a symbolic call once the shared initializer target is source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b4b8.c":
        ("apollo_main", 258, 28, 0,
         "replace the cross-island call and outbound branch halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b714.c":
        ("apollo_main", 86, 10, 0,
         "replace the call and outbound branch halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b76c.c":
        ("apollo_main", 156, 24, 0,
         "replace the outbound call and branch halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b80c.c":
        ("apollo_main", 70, 4, 0,
         "replace the two outbound branch halfwords with symbolic control flow once the adjacent AM142 span is source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59b852.c":
        ("apollo_main", 580, 124, 0,
         "replace the branch-heavy search-loop and helper-call halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59ba96.c":
        ("apollo_main", 78, 14, 0,
         "replace the branch transfer halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59bae4.c":
        ("apollo_main", 1666, 364, 0,
         "replace the branch-heavy search/encoder, vector, and helper-call halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59cafc.c":
        ("apollo_main", 70, 8, 0,
         "replace the two PC-relative BL halfword pairs with symbolic calls once their AM142 call targets are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59cb42.c":
        ("apollo_main", 254, 30, 0,
         "replace the cross-span BL halfwords and boundary halfword with symbolic calls/control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59cc40.c":
        ("apollo_main", 156, 20, 0,
         "replace the call, outbound branch, and boundary halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59ccdc.c":
        ("apollo_main", 170, 10, 0,
         "replace the helper-call and outbound branch halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59cd86.c":
        ("apollo_main", 152, 12, 0,
         "replace the call, outbound branch, and boundary halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59ce1e.c":
        ("apollo_main", 252, 38, 0,
         "replace the boundary, helper-call, loop-branch, and padding halfwords with symbolic control flow once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59cf1a.c":
        ("apollo_main", 572, 142, 0,
         "replace the branch-heavy helper-call and control-flow halfwords with symbolic edges once adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59d3b2.c":
        ("apollo_main", 78, 26, 0,
         "replace the branch/call and boundary halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59d380.c":
        ("apollo_main", 50, 14, 0,
         "replace the branch/call transfer halfwords with symbolic control flow once the adjacent AM142 spans are source-routed"),
    "components/apollo_main/core_overlay/runtime_liblc3_am142_0x59d8f0.c":
        ("apollo_main", 228, 104, 0,
         "replace the long outbound dispatch branches and helper-call halfwords with symbolic control flow once downstream AM142 spans are source-routed"),
    "components/bootloader/core_overlay/runtime_thread_pointer_422874.c":
        ("apollo_bootloader", 8, 0, 4, "retain the typed address literal; surrounding instructions are mnemonic assembly"),
    "components/bootloader/core_overlay/runtime_bl006_spot_trim_span_427e54.c":
        ("apollo_bootloader", 1316, 0, 12,
         "retain the three typed float-pool literals; executable bodies are mnemonic source assembly"),
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
REPLACED_TRANSCRIPTS = {
    "components/bootloader/core_overlay/runtime_mspi_control_4251c0.c":
        (24638, "b46f494c5e4b35a64fa9a13c6d256c720f413a4aa29a57f0b9ffdcb636d5a696", 4384),
}
REMOVED_TRANSCRIPTS = {
    "components/apollo_main/core_overlay/runtime_liblc3_am142_helpers.c":
        (141767, "e39ba9e6f865a35db1761c5c17c0ede5469a70eedaf6d971709c8795fb24f085", 10066),
    "components/bootloader/core_overlay/runtime_mspi_transfer_interrupt_4262e0.c":
        (3798, "1b800153d9619810fa31a3186e003fbbf4902aadf3c95b36338bca2eaa630855", 546),
    "components/apollo_main/core_overlay/runtime_liblc3_ltpf_bits_small_helpers.c":
        (77600, "c326e9322a5e87520c23f72aa375342198b245d9a2c9cc4a19e3c164e9e37652", 6150),
}
RETIRED_TRANSCRIPTS = REPLACED_TRANSCRIPTS | REMOVED_TRANSCRIPTS


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
        directive = match.group(1)
        require(directive in WIDTH,
                f"unsupported raw assembler directive: .{directive}")
        operands = [value.strip() for value in match.group(2).split(",")
                    if value.strip()]
        require(bool(operands), "empty raw assembler directive")
        result[directive] += WIDTH[directive] * len(operands)
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


def _tracked_component_sources() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "components"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    require(result.returncode == 0,
            f"could not enumerate tracked component sources: {result.stderr.strip()}")
    return {
        path for path in result.stdout.splitlines()
        if Path(path).suffix in {".c", ".h", ".S", ".s", ".asm"}
    }


def _git_tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    require(result.returncode == 0,
            f"could not enumerate tracked files: {result.stderr.strip()}")
    return set(result.stdout.splitlines())


def _overlay_source_paths(overlay: dict) -> set[str]:
    result = {row["path"] for row in overlay.get("sources", [])}
    for group in ("in_place_leaves", "cave_leaves", "relocated_leaves"):
        for row in overlay.get(group, []):
            source = row.get("source", {})
            if isinstance(source, dict) and source.get("path"):
                result.add(source["path"])
    return result


def analyze() -> dict:
    apollo_overlay = json.loads(APOLLO_OVERLAY.read_text())
    apollo_report = json.loads(APOLLO_REPORT.read_text())
    boot_overlay = json.loads(BOOT_OVERLAY.read_text())
    apollo_sources = {row["path"] for row in apollo_overlay["sources"]}
    apollo_overlay_source_paths = _overlay_source_paths(apollo_overlay)
    apollo_symbols = apollo_report["overlay"]["functions"]
    boot_routed = _boot_routed_bytes(boot_overlay)

    for relative in REMOVED_TRANSCRIPTS:
        require(not (ROOT / relative).exists(),
                f"removed executable transcript returned to public source: {relative}")
        require(relative not in boot_routed,
                f"removed executable transcript returned to production routing: {relative}")
    for relative in REPLACED_TRANSCRIPTS:
        replacement = ROOT / relative
        require(replacement.is_file() and relative in boot_routed,
                f"structured transcript replacement is not production-routed: {relative}")
        data = replacement.read_bytes()
        require((len(data), sha256(data)) ==
                (171600, "1c94d258f899221ed519c0025beeb350f3e1b3bedbc71386f554c24978561113"),
                f"structured transcript replacement changed: {relative}")
        require(sum(_directive_bytes(data.decode()).values()) == 0,
                f"structured replacement contains raw executable directives: {relative}")

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
            "inst_directive_bytes": (
                directive_bytes["inst"] + directive_bytes["inst.n"] +
                directive_bytes["inst.w"]),
            "source_sha256": sha256(path.read_bytes()),
            "source_ownership_disposition": (
                "overstated_until_remediated" if raw else
                "legitimate_typed_literal_data"),
            "remediation": remediation,
        })

    require(discovered == set(EXPECTED),
            "production raw-directive source census changed")
    public_directive_sources = set()
    public_unrouted_raw_instruction_sources = []
    tracked_paths = _git_tracked_paths()
    public_scope = (
        _tracked_component_sources() |
        routed_source_paths |
        apollo_overlay_source_paths |
        set(boot_routed)
    )
    untracked_overlay_source_inputs = sorted(
        relative for relative in (apollo_overlay_source_paths | set(boot_routed))
        if relative not in tracked_paths and (ROOT / relative).is_file()
    )
    for relative in sorted(public_scope):
        path = ROOT / relative
        if not path.is_file() or path.suffix not in {".c", ".h", ".S", ".s", ".asm"}:
            continue
        directive_bytes = _directive_bytes(path.read_text())
        if not sum(directive_bytes.values()):
            continue
        public_directive_sources.add(relative)
        require(directive_bytes["byte"] == 0,
                f"public source contains executable .byte transcription: {relative}")
        semantic_inst_sources = {
            "components/apollo_main/core_overlay/runtime_freertos_ntz_port.S",
        }
        inst_bytes = (
            directive_bytes["inst"] + directive_bytes["inst.n"] +
            directive_bytes["inst.w"]
        )
        if (
            inst_bytes
            and relative not in semantic_inst_sources
            and relative not in EXPECTED
        ):
            overlay_referenced = (
                relative in apollo_overlay_source_paths
                or relative in boot_routed
            )
            public_unrouted_raw_instruction_sources.append({
                "source": relative,
                "inst_directive_bytes": inst_bytes,
                "overlay_referenced": overlay_referenced,
                "source_sha256": sha256(path.read_bytes()),
                "disposition": (
                    "overlay_referenced_source_contains_raw_instruction_transcription"
                    if overlay_referenced else
                    "tracked_public_source_contains_unrouted_raw_instruction_transcription"
                ),
            })
        # These two source files are typed literal/alignment pools.  Their
        # `.short 0` padding is data layout, not executable transcription.
        if relative not in {
            "components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c",
            "components/bootloader/core_overlay/runtime_startup_literal_pool.c",
        } | set(EXPECTED):
            require(directive_bytes["short"] + directive_bytes["hword"] == 0,
                    f"public source contains raw instruction halfwords: {relative}")
    literal_pool_sources = {
        "components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c",
        "components/bootloader/core_overlay/runtime_startup_literal_pool.c",
        "components/shared/gx8002/runtime_gx8002_uart_stage1_vectors.S",
        "components/apollo_main/core_overlay/runtime_freertos_ntz_port.S",
        "components/apollo_main/core_overlay/runtime_liblc3_am002_helpers.c",
    }
    permitted_debt_sources = {
        row["source"] for row in public_unrouted_raw_instruction_sources
    }
    require(public_directive_sources ==
            set(EXPECTED) | literal_pool_sources | permitted_debt_sources,
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
        "public_raw_executable_transcript_files": sum(
            1 for row in rows if row["raw_instruction_transcription_bytes"]) +
        len(public_unrouted_raw_instruction_sources),
        "public_unrouted_raw_instruction_transcript_files": len(
            public_unrouted_raw_instruction_sources),
        "public_unrouted_raw_instruction_transcript_bytes": sum(
            row["inst_directive_bytes"]
            for row in public_unrouted_raw_instruction_sources),
        "public_unrouted_raw_instruction_overlay_referenced_files": sum(
            1 for row in public_unrouted_raw_instruction_sources
            if row["overlay_referenced"]),
        "public_unrouted_raw_instruction_overlay_referenced_bytes": sum(
            row["inst_directive_bytes"]
            for row in public_unrouted_raw_instruction_sources
            if row["overlay_referenced"]),
        "public_unrouted_raw_instruction_unreferenced_files": sum(
            1 for row in public_unrouted_raw_instruction_sources
            if not row["overlay_referenced"]),
        "public_unrouted_raw_instruction_unreferenced_bytes": sum(
            row["inst_directive_bytes"]
            for row in public_unrouted_raw_instruction_sources
            if not row["overlay_referenced"]),
        "removed_public_transcript_files": len(RETIRED_TRANSCRIPTS),
        "removed_public_transcript_executable_bytes": sum(
            row[2] for row in RETIRED_TRANSCRIPTS.values()),
        "untracked_overlay_source_inputs": len(untracked_overlay_source_inputs),
    }
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
                "disposition": (
                    "historical_raw_transcript_replaced_by_structured_production_c; authenticated stock boundary retained"
                    if path in REPLACED_TRANSCRIPTS else
                    "absent_from_public_source_and_production_routing; authenticated official bytes retained"
                ),
            }
            for path, record in sorted(RETIRED_TRANSCRIPTS.items())
        ],
        "public_unrouted_raw_instruction_sources": (
            public_unrouted_raw_instruction_sources),
        "untracked_overlay_source_inputs": untracked_overlay_source_inputs,
        "hardware_validation": "blocked by unavailable physical evidence",
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
