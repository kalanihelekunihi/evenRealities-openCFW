#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exhaustively type the charging-case 17,070-byte ownership frontier."""

from __future__ import annotations

import argparse, csv, hashlib, json, struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "tools/manifests"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
CORPUS = ROOT / "research/corpus/case/ghidra/final-frontier/functions.jsonl"
FUNCTION_MAP = MANIFEST_DIR / "g2-box-function-map.tsv"
FUNCTION_SUMMARY = MANIFEST_DIR / "g2-box-function-map-summary.json"
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
APP_BASE = 0x08000000
WRAPPER = 32
APP_BYTES = 55752
CORPUS_SHA256 = "03474766c2bef410d520dbd71fe6a0b8565ef1b117168e1639cc8ab4700773ed"
EXPECTED_ADMISSION_BREAKDOWN = {
    "g2-case-register-primitives-admission.tsv": (13, 120),
    "g2-case-register-transforms-admission.tsv": (5, 96),
    "g2-case-semantic-leaves-admission.tsv": (189, 14208),
    "g2-case-pure-helpers-admission.tsv": (7, 248),
    "g2-case-register-policies-admission.tsv": (8, 214),
}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _set_digest(addresses, blob):
    ordered = sorted(addresses)
    return sha256(b"".join(struct.pack("<I", a) for a in ordered)), sha256(bytes(blob[a] for a in ordered))


def _read_tsv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t"))


def _gap_classification(data):
    if data and set(data) == {0}:
        return ("typed_zero_alignment_or_data", "all bytes are zero; exact padding-versus-zero-data role is not needed for executable ownership")
    if len(data) % 2 == 0 and all(data[i:i + 2] in (b"\x00\xbf", b"\xc0\x46")
                                     for i in range(0, len(data), 2)):
        return ("typed_thumb_nop_padding", "every halfword is an architectural or legacy Thumb NOP")
    if len(data) % 2 == 0 and all(data[i:i + 2] == b"\x70\x47"
                                     for i in range(0, len(data), 2)):
        return ("typed_return_tail_padding", "every halfword is BX LR at an inter-function boundary")
    return ("typed_unsupported_interfunction_code_or_data_boundary",
            "the authenticated Ghidra map proves this span is outside every discovered body, but no relocation/xref or independent entry proves literal-data versus unreachable/undiscovered code")


def analyze():
    blob = BLOB.read_bytes(); require(sha256(blob) == BLOB_SHA256, "case blob identity changed")
    app = blob[WRAPPER:]; require(len(app) == APP_BYTES, "case application size changed")
    summary = json.loads(FUNCTION_SUMMARY.read_text())
    functions = _read_tsv(FUNCTION_MAP)
    unresolved = [r for r in functions if r["ownership_category"] == "unresolved"]
    require(len(unresolved) == 222 and sum(int(r["size"], 0) for r in unresolved) == 14886,
            "unresolved function baseline changed")
    admission_paths = sorted(MANIFEST_DIR.glob("g2-case-*-admission.tsv"))
    require({path.name for path in admission_paths} ==
            set(EXPECTED_ADMISSION_BREAKDOWN),
            "case source admission manifest set changed")
    admissions = {}
    admission_breakdown = {}
    for path in admission_paths:
        manifest_rows = _read_tsv(path)
        manifest_shape = (len(manifest_rows),
                          sum(int(row["size"], 0) for row in manifest_rows))
        require(manifest_shape == EXPECTED_ADMISSION_BREAKDOWN[path.name],
                f"case source admission shape changed: {path.name}")
        admission_breakdown[path.name] = {
            "functions": manifest_shape[0], "instruction_bytes": manifest_shape[1]}
        for admission in manifest_rows:
            entry = int(admission["entry"], 0)
            require(entry not in admissions,
                    f"case source admission overlaps at {entry:#x}")
            admissions[entry] = admission
    require(len(admissions) == 222, "case source admission set changed")
    require(sha256(CORPUS.read_bytes()) == CORPUS_SHA256,
            "case final-frontier corpus identity changed")
    corpus = {int((record := json.loads(line))["address"]): record
              for line in CORPUS.read_text(encoding="utf-8").splitlines()
              if line.strip()}
    function_rows = []
    candidate_addresses = set()
    for row in unresolved:
        entry = int(row["entry"], 0); size = int(row["size"], 0)
        body = app[entry - APP_BASE:entry - APP_BASE + size]
        require(len(body) == size, f"function escaped app at {entry:#x}")
        if entry in admissions:
            admitted = admissions[entry]
            require(int(admitted["size"], 0) == size and admitted["instruction_sha256"] == sha256(body),
                    f"case source admission changed at {entry:#x}")
            classification = "project_source_candidate_not_routed"
            owner = admitted["source"]
            license_name = admitted["license"]
            reason = "authenticated clean-room source and Cortex-M0+ closure exist; platform routing remains intentionally absent"
            candidate_addresses.update(range(WRAPPER + entry - APP_BASE,
                                             WRAPPER + entry - APP_BASE + size))
            evidence = corpus.get(entry)
            require(evidence is not None and int(evidence["size"]) == size and
                    evidence["instruction_sha256"] == sha256(body) and
                    evidence["prior_classification"] ==
                    "project_source_candidate_not_routed" and
                    isinstance(evidence.get("decompilation"), str) and
                    bool(evidence["decompilation"]) and
                    sha256(evidence["decompilation"].encode("utf-8")) ==
                    evidence.get("decompilation_sha256"),
                    f"case candidate decompilation evidence changed at {entry:#x}")
        else:
            classification = "typed_unsupported_unattributed_application_function"
            owner = "G2 case application or unidentified upstream/provider body"
            license_name = "LicenseRef-Unresolved-Provider-or-MIT-Clean-Room-Required"
            reason = (f"authenticated body {sha256(body)} has no positive kernel/HAL/string/descriptor/source match; "
                      "exact historical owner and callable semantic contract remain unavailable")
        function_rows.append({"entry": entry, "size": size, "name": row["name"],
            "instruction_sha256": sha256(body), "classification": classification,
            "owner_or_contract": owner, "license": license_name,
            "missing_fact_or_reason": reason})
    candidate_source_bytes = sum(
        r["size"] for r in function_rows
        if r["classification"].startswith("project_"))
    require(candidate_source_bytes == 14886,
            "case candidate-source bytes changed")

    gaps = [r for r in summary["gap_rows"] if r["ownership_category"] == "unresolved"]
    require(len(gaps) == 229 and sum(r["bytes"] for r in gaps) == 2184,
            "unresolved gap baseline changed")
    gap_rows = []
    for row in gaps:
        start, end = int(row["start"]), int(row["end"])
        data = app[start - APP_BASE:end - APP_BASE]
        category, reason = _gap_classification(data)
        gap_rows.append({"start": start, "end": end, "bytes": len(data),
                         "content_sha256": sha256(data), "classification": category,
                         "missing_fact_or_reason": reason})

    universe = set(range(len(blob))); generated = set(range(WRAPPER))
    typed = universe - generated - candidate_addresses
    require(not generated & candidate_addresses and not typed & candidate_addresses and
            generated | candidate_addresses | typed == universe,
            "case physical buckets overlap or leave a gap")
    buckets = {"generated_transport_fill": len(generated),
               "project_source_candidate": len(candidate_addresses),
               "typed_external_or_unsupported": len(typed),
               "still_unclassified": 0}
    require(buckets == {"generated_transport_fill": 32,
               "project_source_candidate": 14886,
               "typed_external_or_unsupported": 40866,
                        "still_unclassified": 0}, "case whole-blob buckets changed")
    physical_rows = []
    for category, addresses in (("generated_transport_fill", generated),
                                ("project_source_candidate", candidate_addresses),
                                ("typed_external_or_unsupported", typed)):
        ad, content = _set_digest(addresses, blob)
        physical_rows.append({"category": category, "bytes": len(addresses),
                              "address_set_sha256": ad, "content_sha256": content})
    return {"schema_version": 1, "component": "G2 charging-case final classification",
        "classification_complete": True, "function_rows": function_rows, "gap_rows": gap_rows,
        "physical_rows": physical_rows,
        "metrics": {"prior_unresolved_bytes": 17070, "frontier_function_rows": 222,
                    "frontier_function_bytes": 14886, "frontier_gap_rows": 229,
                    "frontier_gap_bytes": 2184,
                    "candidate_source_functions": len(admissions),
                    "candidate_source_bytes": candidate_source_bytes,
                    "candidate_source_breakdown": admission_breakdown,
                    "authenticated_candidate_decompilation_rows":
                        len(admissions),
                    "typed_unsupported_frontier_bytes": 17070 - candidate_source_bytes,
                    "unclassified_functions": 0, "unclassified_bytes": 0,
                    "whole_blob_bytes": len(blob), "whole_blob_bucket_bytes": buckets,
                    "gap_classification_counts": dict(sorted(Counter(r["classification"] for r in gap_rows).items())),
                    "physical_bucket_digest": sha256(json.dumps(physical_rows, sort_keys=True, separators=(",", ":")).encode())},
        "hardware_validation": "deferred by project direction",
        "hardware_blocker": "deferred by project direction",
        "hardware_operations": [],
        "production_routed": False,
        "classification_note": "Typed unsupported ownership closes opacity only; it is not source completeness, production routing, or redistribution permission."}


def write_manifests(result):
    function_path = MANIFEST_DIR / "g2-case-final-function-frontier.tsv"
    with function_path.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "size", "name", "instruction_sha256", "classification", "owner_or_contract", "license", "missing_fact_or_reason"])
        for r in result["function_rows"]: w.writerow([f"0x{r['entry']:08X}", r["size"], r["name"], r["instruction_sha256"], r["classification"], r["owner_or_contract"], r["license"], r["missing_fact_or_reason"]])
    gap_path = MANIFEST_DIR / "g2-case-final-gap-frontier.tsv"
    with gap_path.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["start", "end_exclusive", "bytes", "content_sha256", "classification", "missing_fact_or_reason"])
        for r in result["gap_rows"]: w.writerow([f"0x{r['start']:08X}", f"0x{r['end']:08X}", r["bytes"], r["content_sha256"], r["classification"], r["missing_fact_or_reason"]])
    physical_path = MANIFEST_DIR / "g2-case-final-physical-byte-buckets.tsv"
    with physical_path.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["category", "bytes", "address_set_sha256", "content_sha256"])
        for r in result["physical_rows"]: w.writerow([r["category"], r["bytes"], r["address_set_sha256"], r["content_sha256"]])
    summary_path = MANIFEST_DIR / "g2-case-final-classification-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("function_rows", "gap_rows", "physical_rows")}
    slim.update({"function_row_count": len(result["function_rows"]), "gap_row_count": len(result["gap_rows"]), "physical_row_count": len(result["physical_rows"])})
    summary_path.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [function_path, gap_path, physical_path, summary_path]


def main():
    p = argparse.ArgumentParser(); p.add_argument("--write-manifests", action="store_true"); args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Case final classification failed: {exc}") from exc
