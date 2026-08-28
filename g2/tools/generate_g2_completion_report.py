#!/usr/bin/env python3
"""Generate the deterministic public G2 completion assessment.

The report is a presentation of ``analyze_g2_completion_readiness.py`` rather
than an independent progress calculation.  It performs no device operation and
does not turn a classified or attributable byte into source ownership or a
binary redistribution grant.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
from pathlib import Path
from typing import Any

import analyze_g2_completion_readiness as readiness
import audit_g2_release_licensing as licensing


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs/reports/openCFW-completion-2026-08-28"
ASSESSMENT_NAME = "assessment-data.json"
ARTIFACT_NAME = "artifact.json"
REPORT_NAME = "report.html"
HARDWARE_STATUS = "deferred by project direction"

COMPONENT_LABELS = {
    "apollo_main": "Apollo main application",
    "apollo_bootloader": "Apollo bootloader",
    "codec": "GX8002 codec/DSP",
    "ble_em9305": "EM9305 BLE controller",
    "touch": "PSoC touch controller",
    "case": "STM32 charging case",
}
BUCKET_LABELS = {
    "production_source": "Production source",
    "generated_or_reconstructible": "Generated / reconstructible",
    "candidate_source_not_routed": "Candidate source, not routed",
    "typed_retained_or_external": "Typed retained / external",
    "unclassified": "Unclassified",
}
DIRECT_INPUTS = (
    readiness.BASE_MANIFEST,
    readiness.CORE_MANIFEST,
    readiness.MAIN_REPORT,
    readiness.BOOT_REPORT,
    readiness.APOLLO_ORIGIN,
    readiness.TOUCH_SUMMARY,
    readiness.TOUCH_CURRENT,
    readiness.TOUCH_FINAL,
    readiness.CASE_SUMMARY,
    readiness.CASE_REGISTER_ADMISSION,
    readiness.CASE_REGISTER_TRANSFORMS,
    readiness.CASE_FINAL,
    readiness.RAW_ENCODING_SUMMARY,
    readiness.PROJECT_LICENSE_CENSUS,
    readiness.PROJECT_LICENSE_SUMMARY,
    readiness.PROJECT_LICENSE_SCOPE_PATHS,
    readiness.PROJECT_LICENSE_ADDITIONAL_PATHS,
    ROOT / "tools/manifests/gx8002-source-readiness.tsv",
    ROOT / "tools/manifests/em9305-residual-provenance-map.tsv",
    ROOT / "components/apollo_main/core_overlay/overlay.json",
    ROOT / "components/bootloader/core_overlay/overlay.json",
    ROOT / "tools/analyze_g2_completion_readiness.py",
    ROOT / "tools/analyze_g2_production_raw_encoding_quality.py",
    ROOT / "tools/analyze_g2_project_license_normalization.py",
    ROOT / "tools/audit_g2_release_licensing.py",
    *sorted((ROOT / "tools/manifests").glob(
        "g2-touch-*-admission-summary.json")),
)


class ReportError(RuntimeError):
    """Raised when the public report cannot conserve its source audit."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReportError(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _input_record(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"report input is missing: {path}")
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size": len(raw),
        "sha256": _sha256_bytes(raw),
    }


def build_assessment() -> dict[str, Any]:
    """Translate the live audit into the public, lossless assessment schema."""
    live = readiness.analyze()
    license_audit = licensing.analyze()
    license_summary = license_audit["summary"]
    _require(live["licensing"]["source_files"] == license_summary["source_files"],
             "completion and licensing audits disagree on source-file count")
    _require(live["licensing"]["source_errors"] == license_summary["source_errors"],
             "completion and licensing audits disagree on source errors")
    _require(
        live["licensing"]["unresolved_binary_authority"] ==
        license_summary["redistribution_authority_unresolved"],
        "completion and licensing audits disagree on binary authority",
    )

    base = json.loads(readiness.BASE_MANIFEST.read_text(encoding="utf-8"))
    core = json.loads(readiness.CORE_MANIFEST.read_text(encoding="utf-8"))
    aggregate = deepcopy(live["aggregate"])
    components = []
    for component_id, component in live["components"].items():
        row = deepcopy(component)
        row["component_id"] = component_id
        row["component"] = COMPONENT_LABELS[component_id]
        _require(sum(row["buckets"].values()) == row["size"],
                 f"{component_id} public buckets do not conserve bytes")
        components.append(row)

    bucket_total = sum(aggregate["buckets"].values())
    _require(bucket_total == aggregate["component_payload_bytes"],
             "public aggregate buckets do not conserve component bytes")
    _require(bucket_total + aggregate["package_envelope_bytes"] ==
             aggregate["package_bytes"],
             "public package envelope does not conserve package bytes")

    touch = next(row for row in components if row["component_id"] == "touch")
    touch_detail = touch["details"]
    touch_admission = {
        "authoritative_batch": touch_detail["authoritative_batch"],
        "admission_batches": touch_detail["admission_batches"],
        "cumulative_candidate_instruction_bytes":
            touch_detail["cumulative_candidate_instruction_bytes"],
        "candidate_source_not_routed_bytes":
            touch["buckets"]["candidate_source_not_routed"],
        "remaining_unclassified_bytes": touch["buckets"]["unclassified"],
        "remaining_reachable_functions":
            touch_detail["reachable_unclassified_functions"],
        "remaining_application_contracts":
            touch_detail["unimplemented_application_contracts"],
        "production_routed": touch["production_routed"],
    }

    source_inventory = license_audit["source_inventory"]
    license_counts = Counter(row["license"] for row in source_inventory)
    classification_counts = Counter(
        row["classification"] for row in source_inventory)
    binary_authority = [
        {
            "component_id": row["component"],
            "component": COMPONENT_LABELS[row["component"]],
            "redistribution_authority": row["redistribution_authority"],
            "source_availability": row["source_availability"],
            "reason": row["reason"],
        }
        for row in license_audit["artifacts"]
    ]

    gates = deepcopy(live["gates"])
    _require(gates["hardware_validation"] == HARDWARE_STATUS,
             "hardware policy wording drifted")
    _require(gates["hardware_operations"] == [],
             "hardware operations appeared in the software-only audit")

    return {
        "schema_version": 2,
        "assessment_date": "2026-08-28",
        "target": f"{base['target']} {base['package']['version']}",
        "generated_by": "tools/generate_g2_completion_report.py",
        "authoritative_audit": "tools/analyze_g2_completion_readiness.py",
        "analysis_mode": live["analysis_mode"],
        "hardware_validation": HARDWARE_STATUS,
        "hardware_operations": [],
        "definitions": {
            "production_source": (
                "Bytes emitted from maintained source and routed by the current "
                "production component build."
            ),
            "generated_or_reconstructible": (
                "Deterministic framing, patch, alignment, or format metadata; "
                "this does not imply recovered application behavior."
            ),
            "candidate_source_not_routed": (
                "Reviewed source candidate not used by the production provider."
            ),
            "typed_retained_or_external": (
                "A known retained, upstream, proprietary, or unsupported boundary; "
                "classification is not source ownership."
            ),
            "unclassified": "Bytes without a final source or boundary decision.",
            "classification_complete": (
                "Every byte has a source, generated, candidate, or typed-boundary "
                "decision. This is independent of source completion."
            ),
            "source_complete": (
                "No component bytes still require retained or external firmware."
            ),
            "binary_redistribution_authority_resolved": (
                "A durable redistribution grant is recorded for every packaged "
                "binary. Source licensing does not establish this grant."
            ),
        },
        "package": {
            "format": base["package"]["format"],
            "expected_size": aggregate["package_bytes"],
            "expected_sha256": core["package"]["expected_sha256"],
            "component_payload_bytes": aggregate["component_payload_bytes"],
            "generated_envelope_bytes": aggregate["package_envelope_bytes"],
            "conservation": {
                "component_bucket_bytes": bucket_total,
                "component_buckets_plus_envelope_bytes":
                    bucket_total + aggregate["package_envelope_bytes"],
                "matches_expected_package_size": True,
            },
        },
        "components": components,
        "aggregate": aggregate,
        "touch_admission": touch_admission,
        "gates": gates,
        "source_ownership_quality": live["source_ownership_quality"],
        "project_license_policy": live["project_license_policy"],
        "licensing": {
            "source_files": license_summary["source_files"],
            "source_errors": license_summary["source_errors"],
            "source_metadata_clean": license_summary["source_errors"] == 0,
            "source_license_counts": dict(sorted(license_counts.items())),
            "source_classification_counts":
                dict(sorted(classification_counts.items())),
            "binary_redistribution_authority": binary_authority,
            "unresolved_binary_authority":
                license_summary["redistribution_authority_unresolved"],
            "separation_rule": license_audit["separation_rule"],
        },
        "source_inputs": [_input_record(path) for path in DIRECT_INPUTS],
    }


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _fmt_bool(value: bool) -> str:
    return "PASS" if value else "OPEN"


def _html_cell(value: Any) -> str:
    if isinstance(value, bool):
        value = "yes" if value else "no"
    return html.escape(str(value))


def build_html(assessment: dict[str, Any], assessment_sha256: str) -> bytes:
    """Render a compact, dependency-free report from the assessment data."""
    package = assessment["package"]
    aggregate = assessment["aggregate"]
    buckets = aggregate["buckets"]
    gates = assessment["gates"]
    component_rows = []
    for row in assessment["components"]:
        b = row["buckets"]
        component_rows.append(
            "<tr>"
            f"<th scope=\"row\">{_html_cell(row['component'])}</th>"
            f"<td>{_fmt_int(row['size'])}</td>"
            f"<td>{_fmt_int(b['production_source'])}</td>"
            f"<td>{_fmt_int(b['generated_or_reconstructible'])}</td>"
            f"<td>{_fmt_int(b['candidate_source_not_routed'])}</td>"
            f"<td>{_fmt_int(b['typed_retained_or_external'])}</td>"
            f"<td>{_fmt_int(b['unclassified'])}</td>"
            f"<td>{_fmt_int(row['release_blocking_bytes'])}</td>"
            f"<td>{_html_cell(row['classification_complete'])}</td>"
            f"<td>{_html_cell(row['source_complete'])}</td>"
            "</tr>"
        )
    bucket_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(BUCKET_LABELS[key])}</th>"
        f"<td>{_fmt_int(value)}</td>"
        f"<td>{value / aggregate['component_payload_bytes']:.3%}</td>"
        "</tr>"
        for key, value in buckets.items()
    )
    gate_order = (
        "byte_accounting_complete",
        "classification_complete",
        "source_complete",
        "source_metadata_clean",
        "source_ownership_quality_clean",
        "project_license_policy_clean",
        "binary_redistribution_authority_resolved",
        "release_authorized",
    )
    gate_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(key.replace('_', ' '))}</th>"
        f"<td class=\"{('pass' if gates[key] else 'open')}\">"
        f"{_fmt_bool(gates[key])}</td>"
        "</tr>"
        for key in gate_order
    )
    license_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(key)}</th>"
        f"<td>{_fmt_int(value)}</td>"
        "</tr>"
        for key, value in assessment["licensing"]["source_license_counts"].items()
    )
    authority_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(row['component'])}</th>"
        f"<td>{_html_cell(row['redistribution_authority'])}</td>"
        f"<td>{_html_cell(row['source_availability'])}</td>"
        f"<td>{_html_cell(row['reason'])}</td>"
        "</tr>"
        for row in assessment["licensing"]["binary_redistribution_authority"]
    )
    input_rows = "".join(
        "<tr>"
        f"<th scope=\"row\"><code>{_html_cell(row['path'])}</code></th>"
        f"<td>{_fmt_int(row['size'])}</td>"
        f"<td><code>{_html_cell(row['sha256'])}</code></td>"
        "</tr>"
        for row in assessment["source_inputs"]
    )
    touch = assessment["touch_admission"]
    definitions = "".join(
        f"<dt>{_html_cell(key.replace('_', ' '))}</dt>"
        f"<dd>{_html_cell(value)}</dd>"
        for key, value in assessment["definitions"].items()
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>G2 openCFW completion assessment</title>
<style>
:root{{--ink:#18202a;--muted:#5c6875;--line:#d7dde4;--paper:#fff;--wash:#f5f7f9;--pass:#176b3a;--open:#9a3e19}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--wash);color:var(--ink);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1180px;margin:auto;padding:3rem 1.25rem 5rem}} h1{{font-size:2.25rem;margin:.1rem 0}} h2{{margin-top:2.4rem}}
.lede{{font-size:1.12rem;max-width:78ch}} .meta,.note{{color:var(--muted)}} .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem;margin:2rem 0}}
.card,section{{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem}} section{{margin:1rem 0;overflow:auto}}
.card strong{{display:block;font-size:1.65rem}} table{{width:100%;border-collapse:collapse;min-width:720px}} th,td{{padding:.55rem .65rem;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}
th:first-child,td:first-child{{text-align:left}} code{{font-size:.82em;overflow-wrap:anywhere}} dt{{font-weight:700;margin-top:.8rem}} dd{{margin:.15rem 0 .65rem}}
.pass{{color:var(--pass);font-weight:700}} .open{{color:var(--open);font-weight:700}} .warning{{border-left:5px solid var(--open)}}
</style>
</head>
<body><main data-assessment-sha256="{assessment_sha256}">
<p class="meta">Deterministic software-only snapshot · {assessment['assessment_date']}</p>
<h1>G2 openCFW completion assessment</h1>
<p class="lede">{_html_cell(assessment['target'])}. This report separates byte classification, production source completion, source-license metadata, and binary redistribution authority. Those are independent claims.</p>
<p><strong>Hardware validation: {_html_cell(assessment['hardware_validation'])}.</strong> Hardware operations recorded by this assessment: 0.</p>

<div class="cards">
<div class="card"><span>Package bytes</span><strong>{_fmt_int(package['expected_size'])}</strong><small>six payloads plus envelope</small></div>
<div class="card"><span>Production source</span><strong>{_fmt_int(buckets['production_source'])}</strong><small>{buckets['production_source']/aggregate['component_payload_bytes']:.3%} of payloads</small></div>
<div class="card"><span>Generated / reconstructible</span><strong>{_fmt_int(buckets['generated_or_reconstructible'])}</strong><small>component bytes; envelope separate</small></div>
<div class="card"><span>Unclassified</span><strong>{_fmt_int(buckets['unclassified'])}</strong><small>{len(aggregate['unclassified_components'])} components remain</small></div>
<div class="card"><span>Release-blocking payload</span><strong>{_fmt_int(aggregate['release_blocking_bytes'])}</strong><small>not a redistribution-authority measure</small></div>
</div>

<section class="warning"><h2>Current gate truth</h2>
<table><thead><tr><th>Gate</th><th>Status</th></tr></thead><tbody>{gate_rows}</tbody></table>
<p>Classification can pass while source completion remains open. Both can be independent of permission to redistribute retained vendor binaries. The release gate remains fail-closed.</p></section>

<section><h2>Exact component byte conservation</h2>
<table><thead><tr><th>Component</th><th>Bytes</th><th>Production source</th><th>Generated / reconstructible</th><th>Candidate, not routed</th><th>Typed retained / external</th><th>Unclassified</th><th>Release-blocking</th><th>Classified</th><th>Source complete</th></tr></thead>
<tbody>{''.join(component_rows)}</tbody></table>
<p class="note">Each component row sums exactly to its byte size. Component payloads total {_fmt_int(aggregate['component_payload_bytes'])}; the deterministic {_fmt_int(package['generated_envelope_bytes'])}-byte package envelope reconciles them to {_fmt_int(package['expected_size'])} bytes.</p></section>

<section><h2>Aggregate payload classes</h2>
<table><thead><tr><th>Class</th><th>Bytes</th><th>Payload share</th></tr></thead><tbody>{bucket_rows}</tbody></table></section>

<section><h2>Touch candidate-admission chain</h2>
<p>Authoritative batch <strong>{touch['authoritative_batch']}</strong> closes a contiguous chain of {touch['admission_batches']} admission batches. Those batches add {_fmt_int(touch['cumulative_candidate_instruction_bytes'])} instruction bytes; the whole-image candidate bucket is {_fmt_int(touch['candidate_source_not_routed_bytes'])} bytes. It remains explicitly <strong>not production-routed</strong>.</p>
<p>{_fmt_int(touch['remaining_unclassified_bytes'])} Touch bytes, {touch['remaining_reachable_functions']} reachable functions, and {touch['remaining_application_contracts']} application contracts remain open in this snapshot.</p></section>

<section><h2>Definitions</h2><dl>{definitions}</dl></section>

<section><h2>Source-license metadata</h2>
<p>{_fmt_int(assessment['licensing']['source_files'])} unique overlay source files were audited with {assessment['licensing']['source_errors']} metadata errors.</p>
<table><thead><tr><th>SPDX license</th><th>Files</th></tr></thead><tbody>{license_rows}</tbody></table>
<p>{_html_cell(assessment['licensing']['separation_rule'])}.</p></section>

<section class="warning"><h2>Binary redistribution authority</h2>
<table><thead><tr><th>Component</th><th>Authority</th><th>Source availability</th><th>Reason</th></tr></thead><tbody>{authority_rows}</tbody></table></section>

<section><h2>Reproducible inputs</h2>
<p>Regenerate with <code>python3 g2/tools/generate_g2_completion_report.py</code>; verify without writes using <code>python3 g2/tools/generate_g2_completion_report.py --check</code>.</p>
<table><thead><tr><th>Ledger or analyzer</th><th>Bytes</th><th>SHA-256</th></tr></thead><tbody>{input_rows}</tbody></table></section>

<p class="meta">Assessment data SHA-256: <code>{assessment_sha256}</code>. No flashing, signing, publishing, MMIO, reset, DFU, or device interaction is performed by the generator.</p>
</main></body></html>
"""
    return document.encode("utf-8")


def build_outputs() -> dict[str, bytes]:
    assessment = build_assessment()
    assessment_bytes = _json_bytes(assessment)
    assessment_sha = _sha256_bytes(assessment_bytes)
    report_bytes = build_html(assessment, assessment_sha)
    artifact = {
        "schema_version": 2,
        "surface": "report",
        "title": "G2 openCFW Completion Assessment",
        "generator": "g2/tools/generate_g2_completion_report.py",
        "authoritative_audit": "g2/tools/analyze_g2_completion_readiness.py",
        "deterministic": True,
        "hardware_validation": HARDWARE_STATUS,
        "hardware_operations": [],
        "commands": {
            "generate": "python3 g2/tools/generate_g2_completion_report.py",
            "check": "python3 g2/tools/generate_g2_completion_report.py --check",
        },
        "files": {
            ASSESSMENT_NAME: {
                "size": len(assessment_bytes),
                "sha256": assessment_sha,
            },
            REPORT_NAME: {
                "size": len(report_bytes),
                "sha256": _sha256_bytes(report_bytes),
            },
        },
        "gate_snapshot": assessment["gates"],
    }
    return {
        ASSESSMENT_NAME: assessment_bytes,
        ARTIFACT_NAME: _json_bytes(artifact),
        REPORT_NAME: report_bytes,
    }


def write_outputs(output_dir: Path, *, check: bool) -> list[str]:
    outputs = build_outputs()
    stale = []
    if not check:
        output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        path = output_dir / name
        if check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(name)
        else:
            path.write_bytes(content)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed report differs from live ledgers")
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args(argv)
    stale = write_outputs(args.output_dir, check=args.check)
    if stale:
        print("G2 completion assessment is stale: " + ", ".join(stale))
        return 2
    action = "verified" if args.check else "generated"
    print(f"G2 completion assessment {action}: {args.output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        raise SystemExit(f"G2 completion report failed: {exc}") from exc
