#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Close Touch semantic and physical-byte classification after batch 26."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_platform_completion_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
RELOCATED = TOOLS / "analyze_g2_touch_relocated_partition.py"
SEMANTICS = TOOLS / "analyze_g2_touch_relocated_semantics.py"
BASE_READINESS = TOOLS / "analyze_g2_touch_software_readiness.py"
IDENTITY = TOOLS / "analyze_g2_touch_identity.py"

# category, owner/boundary, license, exact missing fact or unsupported reason
APP_BOUNDARIES = {
    0x0158: ("typed_external_runtime_boundary", "selected Cortex-M0+ startup runtime", "LicenseRef-Upstream-Toolchain-Runtime", "toolchain startup contract for the SL stack-limit register is not selected"),
    0x0164: ("typed_external_runtime_boundary", "reset/CRT and Em_EEPROM initialization handoff", "LicenseRef-Upstream-Toolchain-Runtime-and-Infineon-EULA", "linker symbols, constructor hooks, non-returning exit, and the EULA initialization provider are external"),
    0x0324: ("typed_external_board_configuration", "CAT2 SCB clock/provider with board literal arguments", "Apache-2.0-provider", "board-specific SCB clock instance/configuration arguments are not supplied as an open configuration"),
    0x0338: ("typed_unsupported_mmio_configuration", "SysTick configuration and callback installation", "Apache-2.0-provider", "global callback storage and live SysTick/MMIO routing are intentionally not executed in device-free admission"),
    0x0358: ("typed_external_resident_configuration", "resident timeout/configuration record", "LicenseRef-External-Resident-ABI", "the source halfword and destination record live in unavailable resident configuration storage"),
    0x05E0: ("typed_unsupported_product_orchestration", "application bring-up and sensing dispatch", "MIT-clean-room-contract", "direct MMIO writes and the candidate-only 0x17F4 application processor prevent a production-routed device-free contract"),
    0x0648: ("typed_external_vendor_configuration", "CapSense initialization provider", "LicenseRef-Infineon-Cypress-EULA", "the call crosses into the unavailable CapSense body/configuration at 0x2998"),
    0x09A4: ("typed_external_board_configuration", "system power callback registration", "Apache-2.0-provider", "the board callback record referenced by the literal is not available as open configuration"),
    0x09B4: ("typed_unsupported_product_orchestration", "non-returning application main loop", "MIT-clean-room-contract", "direct MMIO, sleep/critical routing, CapSense calls, and product state transitions are inseparable without a product policy specification"),
    0x11A0: ("typed_unsupported_product_orchestration", "clock and GPIO startup aggregator", "MIT-clean-room-contract", "depends on the direct-MMIO clock transition and resident GPIO configuration rows"),
    0x11C4: ("typed_unsupported_product_orchestration", "startup aggregator wrapper", "MIT-clean-room-contract", "depends on the unresolved 0x11A0 board-startup aggregate"),
    0x1238: ("typed_external_resident_configuration", "six CAT2 GPIO pin initializers", "Apache-2.0-provider-and-External-Resident-ABI", "six configuration pointers resolve into the unavailable resident 0xBxxx table"),
    0x12A6: ("typed_external_system_boundary", "breakpoint fault hook", "LicenseRef-Platform-Debug-Runtime", "release fault policy for BKPT #1 is intentionally unspecified"),
    0x12AC: ("typed_unsupported_mmio_configuration", "clock-divider validation/fault path", "Apache-2.0-provider", "contains a direct SRSS register update and the external breakpoint fault policy"),
    0x12D0: ("typed_unsupported_mmio_configuration", "system clock transition sequence", "Apache-2.0-provider", "contains direct SRSS MMIO transitions and depends on unvalidated board clock calibration state"),
    0x1334: ("typed_external_board_configuration", "system power callback registration wrapper", "Apache-2.0-provider", "the linked callback record and failure object are board-specific external configuration"),
    0x1350: ("typed_unsupported_product_orchestration", "startup configuration aggregate", "MIT-clean-room-contract", "depends on unresolved board clock/GPIO and callback registration aggregates"),
    0x13F8: ("typed_unsupported_mmio_configuration", "clock frequency derivation", "Apache-2.0-provider", "reads live SRSS divider MMIO and therefore remains a typed device provider"),
    0x141C: ("typed_external_system_boundary", "interrupt-disable reset/handoff wrapper", "LicenseRef-Platform-System-Handoff", "non-returning interrupt-disabled handoff policy is external to the shipped prefix"),
    0x1434: ("typed_unsupported_mmio_configuration", "clock calibration state writer", "Apache-2.0-provider", "writes linked global clock state derived from live divider hardware"),
    0x156C: ("typed_external_vendor_callback_abi", "Em_EEPROM callback descriptor initializer", "LicenseRef-Infineon-EULA", "the callback-table ABI is consumed by the excluded Em_EEPROM provider and cannot be asserted from its body"),
    0x17BE: ("typed_unimplemented_application_contract", "touch application preflight", "MIT-clean-room-contract", "return semantics combine unavailable CapSense/status providers with application reset policy"),
    0x17F4: ("typed_unimplemented_application_contract", "top-level touch application processor", "MIT-clean-room-contract", "product retry/event policy and mixed CapSense calls are not specified independently of vendor behavior"),
    0x18A8: ("typed_unimplemented_application_contract", "per-object application processor", "MIT-clean-room-contract", "depends on explicitly unavailable pointer-table ABI 0x2638 and mixed provider results"),
    0x1904: ("typed_unimplemented_application_contract", "three-object processing aggregate", "MIT-clean-room-contract", "depends on the unresolved 0x18A8 product result policy"),
    0x1B6C: ("typed_unimplemented_application_contract", "pointer-table update ABI", "MIT-clean-room-contract", "element type, table extent, and ownership for the pointer traversal are not established"),
    0x1C54: ("typed_unimplemented_application_contract", "pointer-table wrapper ABI", "MIT-clean-room-contract", "argument/return contract of the 0x1B6C pointer-table operation is not established"),
    0x1DE4: ("typed_external_resident_configuration", "resident mapping-table loader", "LicenseRef-External-Resident-ABI", "the copied mapping table begins in unavailable resident storage at 0xB4C4"),
    0x1FBC: ("typed_external_resident_configuration", "resident configuration-table loader", "LicenseRef-External-Resident-ABI", "the copied configuration tables begin at unavailable resident address 0xB41C"),
    0x2078: ("typed_external_resident_configuration", "application register/configuration builder", "LicenseRef-External-Resident-ABI", "the body is not closed without both resident loaders at 0x1DE4 and 0x1FBC"),
    0x2638: ("typed_unimplemented_application_contract", "object pointer-table dispatch ABI", "MIT-clean-room-contract", "pointer targets, object extent, and callback result semantics remain unestablished"),
}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); require(spec and spec.loader, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); return module
def _set_digest(addresses, blob):
    ordered = sorted(addresses)
    return (sha256(b"".join(struct.pack("<I", a) for a in ordered)),
            sha256(bytes(blob[a] for a in ordered)))


def _admitted_entries(base):
    entries = {r["entry"] for r in base["function_rows"]
               if r["status"] == "project_source_candidate"}
    evidence = []
    for path in sorted(MANIFEST_DIR.glob("g2-touch*admission*.tsv")):
        if "unavailable" in path.name:
            continue
        count = 0
        with path.open(newline="") as handle:
            rows = csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            )
            for row in rows:
                value = row.get("entry")
                if value and value.startswith("0x"):
                    entries.add(int(value, 16)); count += 1
        if count:
            evidence.append({"manifest": path.name, "entries": count})
    return entries, evidence


def analyze():
    prior_mod = _load(PRIOR, "touch_final_batch26")
    prefix = _load(PREFIX, "touch_final_prefix")
    relocated_mod = _load(RELOCATED, "touch_final_relocated")
    semantic_mod = _load(SEMANTICS, "touch_final_semantics")
    base_mod = _load(BASE_READINESS, "touch_final_base")
    identity = _load(IDENTITY, "touch_final_identity")
    prior = prior_mod.analyze(); residual = prior["residual_rows"]
    residual_by_entry = {r["entry"]: r for r in residual}
    expected_app_frontier = set(APP_BOUNDARIES) & set(residual_by_entry)
    require(expected_app_frontier == {e for e, r in residual_by_entry.items()
                                      if r["family"] in ("platform_startup_configuration", "touch_application_processing")},
            "application frontier is not exhaustive")
    rows = []
    for entry, old in sorted(residual_by_entry.items()):
        if entry in APP_BOUNDARIES:
            category, owner, license_name, reason = APP_BOUNDARIES[entry]
        elif old["family"] == "emeeprom_eula":
            category, owner, license_name = ("typed_external_vendor_provider", "Infineon Em_EEPROM provider", "LicenseRef-Infineon-EULA")
            reason = "authenticated provider ownership is exact, but the EULA body remains excluded from open-source admission"
        elif old["family"] == "system_handoff_mixed":
            category, owner, license_name = ("typed_external_system_boundary", "resident system/DFU handoff", "LicenseRef-External-System-Handoff")
            reason = "the resident handoff implementation and mailbox ABI are unavailable outside the shipped prefix"
        elif old["family"] == "legacy_halt":
            category, owner, license_name = ("typed_external_system_boundary", "selected non-returning halt provider", "LicenseRef-Upstream-Toolchain-Runtime")
            reason = "release halt/reset policy must be supplied by the selected platform runtime"
        else:
            raise AuditError(f"unclassified frontier row {entry:#x}")
        rows.append({"entry": entry, "instruction_bytes": old["instruction_bytes"],
                     "instruction_sha256": old["instruction_sha256"],
                     "prior_family": old["family"], "classification": category,
                     "owner_or_contract": owner, "license": license_name,
                     "concrete_source": False, "implemented": False,
                     "missing_fact_or_reason": reason})
    require(len(rows) == 0 and sum(r["instruction_bytes"] for r in rows) == 0,
            "frontier function accounting changed")

    relocated = relocated_mod.analyze(); semantic = semantic_mod.analyze(); base = base_mod.analyze()
    require(semantic["remaining_opacity"]["byte_unclassified"] == 0,
            "relocated code-span partition is not classification-complete")
    blob = prefix.BLOB.read_bytes(); payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    all_entries = {r["entry"] for r in relocated["function_rows"]}
    admitted, admission_evidence = _admitted_entries(base)
    admitted |= set(prior_mod.ADMISSIONS)
    require(admitted <= all_entries, f"admission entry escaped relocated function map: {sorted(admitted-all_entries)}")
    source_payload = set()
    for entry in sorted(admitted):
        body = prefix._walk(payload, entry, all_entries)
        for address, insn in body["instructions"].items():
            source_payload.update(range(address, address + insn.size))
    code_payload = set(range(prefix.CODE_START, prefix.CODE_END))
    require(source_payload <= code_payload, "source candidate escaped code span")
    source_blob = {prefix.RECORD_OFFSET + a for a in source_payload}
    code_blob = {prefix.RECORD_OFFSET + a for a in code_payload}
    generated = set(range(prefix.RECORD_OFFSET))
    typed_noncode = set()
    generated_names = {"zero_gap_1", "zero_gap_2", "ff_pad", "trailing_crc"}
    for name, start, end, _digest, _cls, _state, _notes in identity.REGIONS:
        if name == "code": continue
        target = generated if name in generated_names else typed_noncode
        target.update(prefix.RECORD_OFFSET + a for a in range(start, end))
    typed = (code_blob - source_blob) | typed_noncode
    universe = set(range(len(blob)))
    require(not (generated & source_blob or generated & typed or source_blob & typed),
            "physical readiness buckets overlap")
    require(generated | source_blob | typed == universe,
            "physical readiness buckets do not cover whole blob")
    buckets = {"generated_transport_fill": len(generated),
               "project_source_candidate": len(source_blob),
               "typed_external_or_unsupported": len(typed),
               "still_unclassified": 0}
    require(sum(buckets.values()) == 34464 and buckets["generated_transport_fill"] == 512,
            "whole-blob readiness buckets changed")
    physical_rows = []
    for category, addresses in (("generated_transport_fill", generated),
                                ("project_source_candidate", source_blob),
                                ("typed_external_or_unsupported", typed)):
        ad, content = _set_digest(addresses, blob)
        physical_rows.append({"category": category, "bytes": len(addresses),
                              "address_set_sha256": ad, "content_sha256": content,
                              "evidence": "disjoint physical blob-byte set derived from authenticated identity regions, relocated exhaustive code partition, and unioned source-admission entries"})
    return {"schema_version": 1, "component": "G2 Touch final classification frontier",
            "classification_complete": True, "function_rows": rows,
            "metrics": {"frontier_functions": 0, "frontier_instruction_row_bytes": 0,
                        "typed_external_or_unsupported_functions": 0,
                        "unclassified_functions": 0, "unclassified_physical_bytes": 0,
                        "whole_blob_bytes": len(blob), "whole_blob_bucket_bytes": buckets,
                        "physical_bucket_digest": sha256(json.dumps(physical_rows, sort_keys=True, separators=(",", ":")).encode())},
            "physical_rows": physical_rows, "admission_entry_count": len(admitted),
            "admission_manifests": admission_evidence,
            "physical_derivation": {"code_span": [prefix.CODE_START, prefix.CODE_END],
                "code_span_bytes": len(code_payload), "relocated_byte_partition": semantic["metrics"]["final_code_partition"],
                "instruction_rows_are_not_summed_for_physical_buckets": True,
                "source_bytes_are_a_union_of_disassembled_instruction_addresses": True},
            "hardware_validation": "deferred by project direction",
            "hardware_blocker": "deferred by project direction",
            "software_function_frontier_complete": True,
            "production_routed": False}


def write_manifests(result):
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    frontier = MANIFEST_DIR / "g2-touch-final-frontier.tsv"
    with frontier.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "instruction_bytes", "instruction_sha256", "prior_family", "classification", "owner_or_contract", "license", "concrete_source", "implemented", "missing_fact_or_reason"])
        for r in result["function_rows"]: w.writerow([f"0x{r['entry']:04X}", r["instruction_bytes"], r["instruction_sha256"], r["prior_family"], r["classification"], r["owner_or_contract"], r["license"], "false", "false", r["missing_fact_or_reason"]])
    physical = MANIFEST_DIR / "g2-touch-final-physical-byte-buckets.tsv"
    with physical.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["category", "bytes", "address_set_sha256", "content_sha256", "evidence"])
        for r in result["physical_rows"]: w.writerow([r["category"], r["bytes"], r["address_set_sha256"], r["content_sha256"], r["evidence"]])
    summary = MANIFEST_DIR / "g2-touch-final-classification-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("function_rows", "physical_rows")}
    slim["function_row_count"] = len(result["function_rows"]); slim["physical_row_count"] = len(result["physical_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    current = MANIFEST_DIR / "g2-touch-current-source-readiness-summary.json"
    b = result["metrics"]["whole_blob_bucket_bytes"]
    current.write_text(json.dumps({"schema_version": 2, "authoritative_batch": 26,
        "classification_complete": True, "software_function_frontier_complete": True,
        "concrete_source_or_implementation_gap": 0,
        "concrete_gap_instruction_bytes": 0, "unimplemented_application_contracts": 0,
        "typed_external_or_unavailable_functions": 0,
        "typed_external_or_unsupported_functions": 0, "unclassified_functions": 0,
        "whole_blob_bytes": 34464, "whole_blob_bucket_bytes": b,
        "physical_bucket_digest": result["metrics"]["physical_bucket_digest"],
        "hardware_validation": "deferred by project direction",
        "hardware_blocker": "deferred by project direction",
        "production_routed": False,
        "exclusions": "software function frontier is source-backed; production routing, resident-data replacement accounting, clean-room EEPROM migration, hardware tuning, and binary redistribution authority remain unresolved"}, indent=2, sort_keys=True) + "\n")
    return [frontier, physical, summary, current]


def main():
    p = argparse.ArgumentParser(); p.add_argument("--write-manifests", action="store_true"); args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch final frontier failed: {exc}") from exc
