#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Close Touch semantic and physical-byte classification after batch 26."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, io, json, re, struct, sys, tempfile
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
SOURCE_IMAGE_SUMMARY = MANIFEST_DIR / "g2-touch-source-image-summary.json"
SOURCE_IMAGE_ANALYZER = TOOLS / "analyze_g2_touch_source_image.py"
SOURCE_IMAGE_BUILDER = ROOT / "components/touch/source_image/build_image.py"
CANDIDATE_PROVENANCE = MANIFEST_DIR / "g2-touch-final-source-candidate-provenance.tsv"

EXPECTED_CANDIDATE_BYTES = 14_510
EXPECTED_CANDIDATE_ADDRESS_SHA256 = "ab7fbcdd8d7aa5d6a8f974f14a75eca3041689315410350d2337a309ff81277b"
EXPECTED_CANDIDATE_CONTENT_SHA256 = "36de6cf8b2b435167383990f4afe100f970959aa5607a36e233dc9a7812cac13"
ROUTE_LICENSES = {"MIT", "MIT OR GPL-3.0-only", "Apache-2.0"}
CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"
ADMISSION_STATUS_SCHEMA = {
    "g2-touch-application-core-admission.tsv": ("status", {"clean_room_application_core_source"}),
    "g2-touch-application-packet-pipeline-admission.tsv": ("status", {"clean_room_argument_relative_packet_pipeline_source"}),
    "g2-touch-application-state-pipeline-admission.tsv": ("status", {"clean_room_argument_relative_application_state_source"}),
    "g2-touch-application-upstream-admission.tsv": ("status", {"exact_upstream_source_admitted"}),
    "g2-touch-cat2-source-admission2.tsv": (None, set()),
    "g2-touch-cat2-source-admission3.tsv": (None, set()),
    "g2-touch-cat2-source-admission4.tsv": (None, set()),
    "g2-touch-cat2-source-admission5.tsv": (None, set()),
    "g2-touch-clock-application-wrappers-admission.tsv": ("status", {"clean_room_injected_wrapper_source"}),
    "g2-touch-closed-record-pipeline-admission.tsv": ("status", {"clean_room_closed_record_pipeline_source"}),
    "g2-touch-configuration-bootstrap-admission.tsv": ("status", {"clean_room_configuration_bootstrap_source"}),
    "g2-touch-configuration-start-pipeline-admission.tsv": ("status", {"clean_room_configuration_source_with_typed_providers"}),
    "g2-touch-deferred-work-admission.tsv": ("status", {"clean_room_deferred_work_source"}),
    "g2-touch-emeeprom-clean-room-admission.tsv": ("status", {"mit_clean_room_functional_replacement"}),
    "g2-touch-flash-row-admission.tsv": ("status", {"clean_room_flash_row_adapter_source"}),
    "g2-touch-leaf-primitives-admission.tsv": ("status", {"clean_room_instruction_exact_source"}),
    "g2-touch-platform-completion-admission.tsv": ("status", {"selected_mit_platform_source"}),
    "g2-touch-platform-wrappers-admission.tsv": ("status", {"clean_room_platform_wrapper_source"}),
    "g2-touch-product-orchestration-admission.tsv": ("status", {"clean_room_product_orchestration_source"}),
    "g2-touch-record-primitives-admission.tsv": ("status", {"clean_room_argument_relative_record_source"}),
    "g2-touch-selection-update-pipeline-admission.tsv": ("status", {"clean_room_argument_relative_selection_update_source"}),
    "g2-touch-source-admission.tsv": ("admission", {"runtime_mit", "cat2_apache"}),
    "g2-touch-startup-closed-admission.tsv": ("status", {"clean_room_startup_source_with_typed_providers"}),
    "g2-touch-storage-adapters-admission.tsv": ("status", {"clean_room_storage_adapter_with_typed_eula_provider"}),
    "g2-touch-terminal-wrappers-admission.tsv": ("status", {"clean_room_terminal_wrapper_source"}),
}
UPSTREAM_SOURCE_FILE_HASHES = {
    "https://github.com/Infineon/mtb-pdl-cat2/blob/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S": "c566a2156931e4179b8adfd591eee9fe3bc88e90d325ec37f43fdb599dcae281",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/include/cy_gpio.h": "b97bb3ca2eeb92940a63a4bc065310cad2dad46f275646c514475f2ce05d08f0",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/include/cy_scb_common.h": "3d23105304c9c7bb4a6fa43cc9947d1bb3d50275f9b7b1e383ca56d89feb2deb",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/include/cy_sysclk.h": "b23362eb4001ce5ccf648b2d7a9fe1c7af17568d102acfa309df679d363df574",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/source/cy_msclp.c": "2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/source/cy_scb_common.c": "e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/source/cy_scb_i2c.c": "9f3e77675ea3f02798107fe28def78b826b35d6d136785644d90ff10877f248b",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/source/cy_sysclk.c": "fa7d3221a4a52f4cae68d291237c57541448539db05ddf0ba653fd0a04c08594",
    "https://github.com/Infineon/mtb-pdl-cat2/drivers/source/cy_syspm.c": "be43e5aa704c99acca45850db68094977a274dcb1d4335fafca753269c5a93b8",
}
CANDIDATE_ROUTE_ORDER = (
    "project_mit_nonproduction_source_image_tu_semantic_route",
    "project_mit_or_gpl_nonproduction_source_image_tu_semantic_route",
    "project_mit_emeeprom_clean_room_nonproduction_source_image_tu_semantic_route",
    "apache_critical_adapter_nonproduction_source_image_tu_semantic_route",
    "apache_cat2_upstream_body_identified_not_linked",
    "overlap_or_source_output_identity_unresolved",
)
ANALYZER_INPUTS = (
    Path(__file__).resolve(), PRIOR, PREFIX, RELOCATED, SEMANTICS,
    BASE_READINESS, IDENTITY, SOURCE_IMAGE_ANALYZER, SOURCE_IMAGE_BUILDER,
)

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


def _semantic_category_sets(semantic_mod, relocated_mod, prefix, payload):
    """Reproduce the exhaustive code-span sets behind the pinned semantic rows."""
    base_entries = {r["entry"] for r in relocated_mod.analyze()["function_rows"]}
    entries = base_entries | {item[0] for item in semantic_mod.CONFIG_POINTERS.values()}
    entries |= semantic_mod.LINEAR_PROLOGUE_ENTRIES
    entries = relocated_mod._direct_closure(
        prefix, payload, entries, {entry: set() for entry in entries}
    )
    bodies, cfg = relocated_mod._body_bytes(prefix, payload, entries)
    refs = relocated_mod._literal_targets(bodies)
    literals = {byte for target in refs for byte in range(target, target + 4)}
    dispatch = set()
    for table, count, _role in semantic_mod.DISPATCH_TABLES:
        for value in struct.unpack_from(f"<{count}I", payload, table):
            entry = (value & ~1) - relocated_mod.LINK_BASE
            for address, insn in prefix._walk(payload, entry, entries)["instructions"].items():
                dispatch.update(range(address, address + insn.size))
    dispatch -= cfg | literals
    typed_data = {
        byte
        for start, end, _role in semantic_mod.RESIDUAL_DATA_SPANS
        for byte in range(start, end)
    }
    universe = set(range(prefix.CODE_START, prefix.CODE_END))
    remaining = universe - (cfg - literals) - dispatch - literals - typed_data
    patterns = {
        "residual_legacy_nop_padding": set(),
        "residual_arch_nop_padding": set(),
        "residual_zero_halfword_alignment_or_data": set(),
        "residual_return_tail": set(),
    }
    encodings = {
        b"\xC0\x46": "residual_legacy_nop_padding",
        b"\x00\xBF": "residual_arch_nop_padding",
        b"\x00\x00": "residual_zero_halfword_alignment_or_data",
        b"\x70\x47": "residual_return_tail",
    }
    while remaining:
        address = min(remaining)
        require(address % 2 == 0 and {address, address + 1} <= remaining,
                "typed code complement contains an unpaired byte")
        remaining.difference_update((address, address + 1))
        category = encodings.get(payload[address:address + 2])
        require(category is not None,
                f"typed code complement has an unknown halfword at {address:#x}")
        patterns[category].update((address, address + 1))
    result = {
        "cfg_instruction_candidate": cfg - literals,
        "dispatch_case_instruction_candidate": dispatch,
        "referenced_literal_data": literals,
        "residual_typed_data": typed_data,
        **patterns,
    }
    require(set().union(*result.values()) == universe,
            "semantic code sets do not cover the relocated span")
    require(sum(map(len, result.values())) == len(universe),
            "semantic code sets overlap")
    return result, base_entries


def _physical_row(category, addresses, blob, owner, license_status,
                  unresolved_sub_boundary, evidence):
    address_digest, content_digest = _set_digest(addresses, blob)
    return {
        "category": category,
        "bytes": len(addresses),
        "address_set_sha256": address_digest,
        "content_sha256": content_digest,
        "owner_or_category": owner,
        "license_status": license_status,
        "unresolved_sub_boundary": unresolved_sub_boundary,
        "evidence": evidence,
    }


def _linked_source_inventory():
    checked = json.loads(SOURCE_IMAGE_SUMMARY.read_text(encoding="utf-8"))
    source_image_mod = _load(SOURCE_IMAGE_ANALYZER,
                             "touch_final_source_image_receipt")
    summary = source_image_mod.analyze()
    require(summary == checked,
            "rebuilt Touch source-image receipt differs from checked summary")
    require(summary.get("software_link_complete") is True,
            "Touch source-image summary is not software-link complete")
    require(summary.get("production_routed") is False,
            "Touch source-image unexpectedly claims production routing")
    inventory = {
        item["path"]: item["sha256"]
        for item in summary["artifacts"]["source_inventory"]
        if Path(item["path"]).suffix in (".c", ".S")
    }
    require(bool(inventory), "Touch source-image linked TU inventory is empty")
    return summary, inventory


def _analysis_input_receipt(source_image, stock_blob):
    paths = set(ANALYZER_INPUTS)
    paths.add(SOURCE_IMAGE_SUMMARY)
    paths.add(MANIFEST_DIR / "g2-touch-software-readiness-functions.tsv")
    paths.add(stock_blob)
    paths.update(MANIFEST_DIR / name for name in ADMISSION_STATUS_SCHEMA)
    paths.update(
        ROOT / item["path"]
        for item in source_image["artifacts"]["source_inventory"]
    )
    path_sha256 = {}
    for path in paths:
        require(path.is_file() and not path.is_symlink(),
                f"analysis input is not a regular file: {path}")
        resolved = path.resolve()
        require(ROOT.resolve() in resolved.parents,
                f"analysis input escapes the G2 repository: {path}")
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
        path_sha256[relative] = sha256(resolved.read_bytes())
    path_sha256 = dict(sorted(path_sha256.items()))
    require(len(path_sha256) >= 60,
            "Touch analysis input receipt is unexpectedly incomplete")
    return {
        "path_count": len(path_sha256),
        "aggregate_sha256": sha256(json.dumps(
            path_sha256, sort_keys=True, separators=(",", ":")
        ).encode()),
        "path_sha256": path_sha256,
    }


def _local_source_route(source):
    path = Path(source)
    if len(path.parts) == 1:
        path = Path("components/shared/touch") / path
    return path.as_posix()


def _source_spdx_identifier(route):
    path = ROOT / route
    require(path.is_file() and not path.is_symlink(),
            f"candidate route is not a contained regular file: {route}")
    resolved = path.resolve()
    require(ROOT.resolve() in resolved.parents,
            f"candidate route escapes the G2 repository: {route}")
    matches = re.findall(
        r"SPDX-License-Identifier:\s*([^\r\n*]+)",
        path.read_text(encoding="utf-8"),
    )
    expressions = [match.strip() for match in matches]
    require(len(expressions) == 1,
            f"candidate source must have exactly one SPDX identifier: {route}")
    return expressions[0]


def _require_source_spdx(route, claimed_license):
    actual = _source_spdx_identifier(route)
    require(actual == claimed_license,
            f"candidate source SPDX mismatch for {route}: {actual!r} != {claimed_license!r}")
    return actual


def _require_receipt_source(route, linked_inventory):
    require(route in linked_inventory,
            f"candidate source TU is not in the rebuilt source-image inventory: {route}")
    data = (ROOT / route).read_bytes()
    require(sha256(data) == linked_inventory[route],
            f"candidate source differs from rebuilt source-image receipt: {route}")


def _candidate_claim(row, manifest, linked_inventory):
    entry_text = row.get("entry", "")
    require(entry_text.startswith("0x"),
            f"candidate claim lacks an entry: {manifest}")
    license_name = row.get("license", "").strip()
    require(license_name in ROUTE_LICENSES,
            f"candidate claim has missing or unsupported license at {entry_text}: {license_name!r}")
    source = (row.get("source") or row.get("source_or_provider") or "").strip()
    require(bool(source), f"candidate claim lacks a source route at {entry_text}")
    adapter = row.get("adapter", "").strip()
    is_upstream = source.startswith("https://")
    eula_boundary = "none"
    if is_upstream:
        require(license_name == "Apache-2.0",
                f"upstream CAT2 claim is not Apache-2.0 at {entry_text}")
        require(source.startswith("https://github.com/Infineon/mtb-pdl-cat2/"),
                f"unrecognized upstream source route at {entry_text}")
        require(row.get("provider_commit", "").strip() == CAT2_COMMIT,
                f"upstream CAT2 commit changed at {entry_text}")
        recorded_source_hash = row.get("source_file_sha256", "").strip()
        if recorded_source_hash:
            require(UPSTREAM_SOURCE_FILE_HASHES.get(source) == recorded_source_hash,
                    f"upstream source-file hash evidence changed at {entry_text}")
        if adapter:
            adapter_route = _local_source_route(adapter)
            _require_receipt_source(adapter_route, linked_inventory)
            _require_source_spdx(adapter_route, license_name)
        if adapter == "runtime_touch_critical_adapters.S":
            route_category = "apache_critical_adapter_nonproduction_source_image_tu_semantic_route"
            translation_unit_present = True
        else:
            route_category = "apache_cat2_upstream_body_identified_not_linked"
            translation_unit_present = False
        adapter_linked = bool(adapter) and (
            _local_source_route(adapter) in linked_inventory
        )
    else:
        require(license_name in ("MIT", "MIT OR GPL-3.0-only"),
                f"project claim has a non-project route license at {entry_text}")
        source = _local_source_route(source)
        _require_receipt_source(source, linked_inventory)
        _require_source_spdx(source, license_name)
        translation_unit_present = True
        adapter_linked = False
        if Path(source).name == "runtime_touch_emeeprom_clean_room.c":
            route_category = (
                "project_mit_emeeprom_clean_room_nonproduction_source_image_tu_semantic_route"
            )
            eula_boundary = "Infineon Em_EEPROM EULA comparison source excluded"
        elif license_name == "MIT OR GPL-3.0-only":
            route_category = "project_mit_or_gpl_nonproduction_source_image_tu_semantic_route"
        else:
            route_category = "project_mit_nonproduction_source_image_tu_semantic_route"
    return {
        "entry": int(entry_text, 16),
        "manifest": manifest,
        "source": source,
        "adapter": adapter,
        "license": license_name,
        "route_category": route_category,
        "translation_unit_present_in_nonproduction_source_image": translation_unit_present,
        "adapter_translation_unit_present_in_nonproduction_source_image": adapter_linked,
        "admitted_body_linked_to_stock_address": False,
        "production_elf_ownership": False,
        "stock_byte_license_authority": "NOASSERTION",
        "eula_vendor_source_included": False,
        "excluded_source_boundary": eula_boundary,
        "instruction_bytes": row.get("instruction_bytes", "").strip(),
        "instruction_sha256": row.get("instruction_sha256", "").strip(),
        "canonical_body_sha256": row.get("canonical_body_sha256", "").strip(),
        "target_signature_sha256": row.get("target_signature_sha256", "").strip(),
        "source_file_sha256": row.get("source_file_sha256", "").strip(),
    }


def _admitted_claims(base):
    source_image, linked_inventory = _linked_source_inventory()
    claims = {}
    base_name = "g2-touch-software-readiness-functions.tsv"
    for row in base["function_rows"]:
        if row["status"] != "project_source_candidate":
            continue
        claim = _candidate_claim({
            "entry": f"0x{row['entry']:04X}",
            "license": row["license"],
            "source_or_provider": row["source_or_provider"],
            "instruction_bytes": str(row["instruction_bytes"]),
            "instruction_sha256": row["instruction_sha256"],
        }, base_name, linked_inventory)
        require(claim["entry"] not in claims,
                f"duplicate base candidate entry {claim['entry']:#x}")
        claims[claim["entry"]] = claim
    discovered = {
        path.name for path in MANIFEST_DIR.glob("g2-touch*admission*.tsv")
        if "unavailable" not in path.name
    }
    require(discovered == set(ADMISSION_STATUS_SCHEMA),
            "Touch candidate admission manifest set changed")
    evidence = []
    for name, (discriminator, allowed_values) in ADMISSION_STATUS_SCHEMA.items():
        path = MANIFEST_DIR / name
        count = 0
        with path.open(newline="") as handle:
            rows = csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            )
            required_fields = {
                "entry", "source", "license", "instruction_sha256", "evidence"
            }
            require(rows.fieldnames is not None and
                    required_fields <= set(rows.fieldnames),
                    f"candidate admission schema is incomplete: {path.name}")
            if discriminator is None:
                require("status" not in rows.fieldnames and
                        "admission" not in rows.fieldnames,
                        f"implicit CAT2 admission gained an unchecked discriminator: {path.name}")
            else:
                require(discriminator in rows.fieldnames,
                        f"candidate admission lacks {discriminator}: {path.name}")
            for row in rows:
                value = row.get("entry")
                if value and value.startswith("0x"):
                    if discriminator is not None:
                        require(row.get(discriminator) in allowed_values,
                                f"candidate admission status changed at {value}: {path.name}")
                    require(bool(row.get("evidence", "").strip()),
                            f"candidate admission evidence is empty at {value}")
                    claim = _candidate_claim(row, path.name, linked_inventory)
                    require(claim["entry"] not in claims,
                            f"duplicate candidate admission entry {claim['entry']:#x}")
                    claims[claim["entry"]] = claim
                    count += 1
        if count:
            evidence.append({"manifest": path.name, "entries": count})
    evidence.insert(0, {"manifest": base_name,
                        "entries": sum(c["manifest"] == base_name
                                       for c in claims.values())})
    return claims, evidence, source_image


def _assert_disjoint_partition(address_sets, expected):
    union = set()
    for category, addresses in address_sets.items():
        require(not union & addresses,
                f"candidate provenance subrows overlap at {category}")
        union.update(addresses)
    require(union == expected,
            "candidate provenance subrows do not cover the candidate union")


def _partition_candidate_provenance(entry_addresses, claims, blob,
                                    record_offset):
    require(set(entry_addresses) == set(claims),
            "candidate entry bodies and provenance claims differ")
    byte_claims = {}
    for entry, addresses in entry_addresses.items():
        require(bool(addresses), f"candidate entry has an empty body: {entry:#x}")
        for address in addresses:
            byte_claims.setdefault(address, set()).add(entry)
    candidate_payload = set(byte_claims)
    address_sets = {category: set() for category in CANDIDATE_ROUTE_ORDER}
    row_entries = {category: set() for category in CANDIDATE_ROUTE_ORDER}
    for address, owners in byte_claims.items():
        if len(owners) != 1:
            category = "overlap_or_source_output_identity_unresolved"
        else:
            category = claims[next(iter(owners))]["route_category"]
        address_sets[category].add(record_offset + address)
        row_entries[category].update(owners)
    address_sets = {name: addresses for name, addresses in address_sets.items()
                    if addresses}
    _assert_disjoint_partition(
        address_sets, {record_offset + address for address in candidate_payload}
    )
    rows = []
    for category in CANDIDATE_ROUTE_ORDER:
        addresses = address_sets.get(category)
        if not addresses:
            continue
        entries = row_entries[category]
        route_claims = [claims[entry] for entry in sorted(entries)]
        route_licenses = sorted({claim["license"] for claim in route_claims})
        source_route_license = (
            "NOASSERTION" if category ==
            "overlap_or_source_output_identity_unresolved"
            else route_licenses[0]
        )
        if category != "overlap_or_source_output_identity_unresolved":
            require(len(route_licenses) == 1,
                    f"candidate route category mixes licenses: {category}")
        address_digest, content_digest = _set_digest(addresses, blob)
        rows.append({
            "category": category,
            "bytes": len(addresses),
            "address_set_sha256": address_digest,
            "content_sha256": content_digest,
            "entry_count": len(entries),
            "entry_set_sha256": sha256(b"".join(
                struct.pack("<I", entry) for entry in sorted(entries)
            )),
            "admission_manifests": ";".join(sorted({
                claim["manifest"] for claim in route_claims
            })),
            "source_routes": ";".join(sorted({
                claim["source"] for claim in route_claims
            })),
            "source_route_license": source_route_license,
            "claimed_route_licenses": ";".join(route_licenses),
            "translation_unit_present_in_nonproduction_source_image": all(
                claim["translation_unit_present_in_nonproduction_source_image"]
                for claim in route_claims
            ),
            "adapter_translation_unit_present_in_nonproduction_source_image": any(
                claim["adapter_translation_unit_present_in_nonproduction_source_image"]
                for claim in route_claims
            ),
            "semantic_stock_address_candidate_only": True,
            "admitted_body_linked_to_stock_address": False,
            "production_elf_ownership": False,
            "stock_byte_license_authority": "NOASSERTION",
            "eula_vendor_source_included": False,
            "excluded_source_boundaries": ";".join(sorted({
                claim["excluded_source_boundary"] for claim in route_claims
                if claim["excluded_source_boundary"] != "none"
            })) or "none",
            "evidence": (
                "disjoint stock-address subset routed by per-entry semantic "
                "admission; no stock-address-to-linked-output identity claim"
            ),
        })
    require(sum(row["bytes"] for row in rows) == len(candidate_payload),
            "candidate provenance row byte count changed")
    require(all(row["source_route_license"] for row in rows),
            "candidate provenance contains an unlicensed route row")
    require(all(not row["production_elf_ownership"] for row in rows),
            "semantic candidate was treated as production ELF ownership")
    return rows, {
        "candidate_bytes": len(candidate_payload),
        "subrow_count": len(rows),
        "subrow_overlap_bytes": 0,
        "overlapping_semantic_claim_bytes": len(address_sets.get(
            "overlap_or_source_output_identity_unresolved", set()
        )),
        "semantic_stock_address_candidates_only": True,
        "production_elf_ownership": False,
        "stock_address_to_linked_output_identity_proven": False,
        "stock_byte_redistribution_authority": "NOASSERTION",
        "eula_vendor_source_included": False,
        "row_digest": sha256(json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode()),
    }


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
    claims, admission_evidence, source_image = _admitted_claims(base)
    admitted = set(claims)
    require(set(prior_mod.ADMISSIONS) <= admitted,
            "final admission entries lack per-entry license/source provenance")
    require(admitted <= all_entries, f"admission entry escaped relocated function map: {sorted(admitted-all_entries)}")
    source_payload = set()
    entry_addresses = {}
    for entry in sorted(admitted):
        body = prefix._walk(payload, entry, all_entries)
        claim = claims[entry]
        require(re.fullmatch(r"[0-9a-f]{64}", claim["instruction_sha256"])
                is not None,
                f"candidate instruction digest is malformed at {entry:#x}")
        require(body["instruction_sha256"] == claim["instruction_sha256"],
                f"candidate instruction digest differs from stock body at {entry:#x}")
        if claim["instruction_bytes"]:
            require(body["instruction_bytes"] == int(claim["instruction_bytes"]),
                    f"candidate instruction byte count differs at {entry:#x}")
        canonical = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items())
        )
        for field in ("canonical_body_sha256", "target_signature_sha256"):
            expected_digest = claim[field]
            if expected_digest:
                require(sha256(canonical.encode()) == expected_digest,
                        f"candidate {field} differs at {entry:#x}")
        addresses = set()
        for address, insn in body["instructions"].items():
            addresses.update(range(address, address + insn.size))
        entry_addresses[entry] = addresses
        source_payload.update(addresses)
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
    typed_code = code_blob - source_blob
    typed = typed_code | typed_noncode
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
    candidate_address_digest, candidate_content_digest = _set_digest(
        source_blob, blob
    )
    require((len(source_blob), candidate_address_digest,
             candidate_content_digest) ==
            (EXPECTED_CANDIDATE_BYTES, EXPECTED_CANDIDATE_ADDRESS_SHA256,
             EXPECTED_CANDIDATE_CONTENT_SHA256),
            "Touch semantic stock-address candidate union changed")
    candidate_provenance_rows, candidate_provenance = (
        _partition_candidate_provenance(
            entry_addresses, claims, blob, prefix.RECORD_OFFSET
        )
    )
    require(candidate_provenance["candidate_bytes"] == len(source_blob),
            "candidate provenance does not conserve the physical candidate bucket")
    candidate_provenance.update({
        "address_set_sha256": candidate_address_digest,
        "content_sha256": candidate_content_digest,
        "entry_claim_count": len(claims),
        "manifest": CANDIDATE_PROVENANCE.name,
        "nonproduction_source_image_elf_sha256": source_image["artifacts"]["elf_sha256"],
        "nonproduction_source_image_production_routed": source_image["production_routed"],
    })
    analysis_inputs = _analysis_input_receipt(source_image, prefix.BLOB)
    semantic_sets, base_entries = _semantic_category_sets(
        semantic_mod, relocated_mod, prefix, payload
    )
    semantic_rows = {row["category"]: row for row in semantic["byte_rows"]}
    require(set(semantic_sets) == set(semantic_rows),
            "semantic category row set changed")
    for category, addresses in semantic_sets.items():
        address_digest, content_digest = _set_digest(addresses, payload)
        row = semantic_rows[category]
        require((len(addresses), address_digest, content_digest) ==
                (row["bytes"], row["address_set_sha256"], row["content_sha256"]),
                f"semantic address set changed: {category}")

    instruction_complement = (
        semantic_sets["cfg_instruction_candidate"] |
        semantic_sets["dispatch_case_instruction_candidate"]
    ) - source_payload
    owner_sets = {}
    for row in semantic["semantic_rows"]:
        entry = row["entry"]
        body = prefix._walk(payload, entry, base_entries)
        addresses = {
            byte
            for address, insn in body["instructions"].items()
            for byte in range(address, address + insn.size)
        }
        owner_sets.setdefault(row["batch"], set()).update(
            addresses & instruction_complement
        )
    owner_sets = {name: addresses for name, addresses in owner_sets.items()
                  if addresses}
    require(set(owner_sets) == {"capsense_cat2_mixed"},
            "typed instruction-owner categories changed")
    owned_instruction = set().union(*owner_sets.values())
    require(sum(map(len, owner_sets.values())) == len(owned_instruction),
            "typed instruction-owner categories overlap")
    unresolved_instruction = instruction_complement - owned_instruction

    typed_masks = {
        "typed_code_capsense_cat2_mixed_provider": {
            prefix.RECORD_OFFSET + address
            for address in owner_sets["capsense_cat2_mixed"]
        },
        "typed_code_owner_unresolved": {
            prefix.RECORD_OFFSET + address for address in unresolved_instruction
        },
    }
    for category in (
        "referenced_literal_data", "residual_arch_nop_padding",
        "residual_legacy_nop_padding", "residual_return_tail",
        "residual_typed_data", "residual_zero_halfword_alignment_or_data",
    ):
        typed_masks[f"typed_code_{category}"] = {
            prefix.RECORD_OFFSET + address
            for address in semantic_sets[category] - source_payload
        }
    identity_sets = {}
    for name, start, end, _digest, _cls, _state, _notes in identity.REGIONS:
        if name in ("vectors", "strings", "const_tables_a", "const_tables_b",
                    "config_block"):
            identity_sets[name] = {
                prefix.RECORD_OFFSET + address for address in range(start, end)
            }
    typed_masks["typed_noncode_vectors"] = identity_sets["vectors"]
    typed_masks["typed_noncode_strings"] = identity_sets["strings"]
    typed_masks["typed_noncode_config_and_tables"] = (
        identity_sets["const_tables_a"] | identity_sets["const_tables_b"] |
        identity_sets["config_block"]
    )
    require(set().union(*typed_masks.values()) == typed,
            "Touch typed semantic masks do not cover the typed complement")
    require(sum(map(len, typed_masks.values())) == len(typed),
            "Touch typed semantic masks overlap")
    require(len(typed_code) == 15854 and len(typed_noncode) == 3588,
            "Touch typed code/non-code complement changed")
    require((len(typed_masks["typed_noncode_vectors"]),
             len(typed_masks["typed_noncode_strings"]),
             len(typed_masks["typed_noncode_config_and_tables"])) ==
            (192, 1640, 1756), "Touch non-code semantic partition changed")

    details = {
        "typed_code_capsense_cat2_mixed_provider": (
            "Infineon CapSense/CAT2 mixed provider", "EULA-or-Apache-2.0 unresolved",
            "exact producing provider and redistribution authority remain unresolved"),
        "typed_code_owner_unresolved": (
            "expanded CFG/dispatch complement without a surviving owner row", "NOASSERTION",
            "semantic source admission does not establish stock-address ownership"),
        "typed_code_referenced_literal_data": (
            "PC-relative literal pools", "NOASSERTION",
            "value ownership and replacement mapping remain unresolved"),
        "typed_code_residual_arch_nop_padding": (
            "Thumb architectural NOP padding", "reconstructible semantics; stock authority unresolved",
            "stock-byte redistribution authority remains unresolved"),
        "typed_code_residual_legacy_nop_padding": (
            "Thumb legacy NOP padding", "reconstructible semantics; stock authority unresolved",
            "stock-byte redistribution authority remains unresolved"),
        "typed_code_residual_return_tail": (
            "bounded Thumb return tails", "NOASSERTION",
            "function ownership outside admitted source remains unresolved"),
        "typed_code_residual_typed_data": (
            "bounded in-code data/reference spans", "NOASSERTION",
            "data owner and source replacement remain unresolved"),
        "typed_code_residual_zero_halfword_alignment_or_data": (
            "zero halfwords", "NOASSERTION",
            "alignment-versus-data semantics remain intentionally unresolved"),
        "typed_noncode_vectors": (
            "ARMv6-M vector table", "external startup/provider boundary",
            "production vector ownership and routing remain unresolved"),
        "typed_noncode_strings": (
            "retained EasyLogger/product strings", "NOASSERTION",
            "string redistribution and source replacement remain unresolved"),
        "typed_noncode_config_and_tables": (
            "resident configuration and tuning tables", "external resident/provider boundary",
            "table schema, ownership, and production source mapping remain unresolved"),
    }
    physical_rows = [
        _physical_row(
            "generated_transport_fill", generated, blob,
            "deterministic FWPK/fill/checksum framing", "MIT reconstruction",
            "none", "authenticated generated transport and fill regions",
        ),
        _physical_row(
            "project_source_candidate", source_blob, blob,
            "semantic stock-address candidate union with mixed source routes",
            "MIXED semantic routes: MIT; MIT OR GPL-3.0-only; Apache-2.0; stock-byte authority NOASSERTION",
            "semantic candidate only; not production ELF ownership",
            f"disjoint route/license detail in {CANDIDATE_PROVENANCE.name}",
        ),
    ]
    for category, addresses in typed_masks.items():
        owner, license_status, unresolved = details[category]
        physical_rows.append(_physical_row(
            category, addresses, blob, owner, license_status, unresolved,
            "disjoint authenticated Touch blob-byte address set",
        ))
    return {"schema_version": 2, "component": "G2 Touch final classification frontier",
            "classification_complete": True, "function_rows": rows,
            "metrics": {"frontier_functions": 0, "frontier_instruction_row_bytes": 0,
                        "typed_external_or_unsupported_functions": 0,
                        "unclassified_functions": 0, "unclassified_physical_bytes": 0,
                        "whole_blob_bytes": len(blob), "whole_blob_bucket_bytes": buckets,
                        "typed_code_complement_bytes": len(typed_code),
                        "typed_noncode_bytes": len(typed_noncode),
                        "typed_noncode_partition": {
                            "vectors": 192, "strings": 1640,
                            "config_and_tables": 1756,
                        },
                        "physical_bucket_digest": sha256(json.dumps(physical_rows, sort_keys=True, separators=(",", ":")).encode()),
                        "candidate_union_address_set_sha256": candidate_address_digest,
                        "candidate_union_content_sha256": candidate_content_digest},
            "physical_rows": physical_rows, "admission_entry_count": len(admitted),
            "admission_manifests": admission_evidence,
            "analysis_inputs": analysis_inputs,
            "candidate_provenance": candidate_provenance,
            "candidate_provenance_rows": candidate_provenance_rows,
            "physical_derivation": {"code_span": [prefix.CODE_START, prefix.CODE_END],
                "code_span_bytes": len(code_payload), "relocated_byte_partition": semantic["metrics"]["final_code_partition"],
                "instruction_rows_are_not_summed_for_physical_buckets": True,
                "source_bytes_are_a_union_of_disassembled_instruction_addresses": True,
                "semantic_stock_address_candidates_are_not_production_elf_ownership": True},
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": "blocked by unavailable physical evidence",
            "software_function_frontier_complete": True,
            "production_routed": False}


def _manifest_payloads(result):
    frontier = MANIFEST_DIR / "g2-touch-final-frontier.tsv"
    h = io.StringIO(newline="")
    w = csv.writer(h, delimiter="\t", lineterminator="\n")
    w.writerow(["# SPDX-License-Identifier: MIT"])
    w.writerow(["entry", "instruction_bytes", "instruction_sha256", "prior_family", "classification", "owner_or_contract", "license", "concrete_source", "implemented", "missing_fact_or_reason"])
    for r in result["function_rows"]:
        w.writerow([f"0x{r['entry']:04X}", r["instruction_bytes"], r["instruction_sha256"], r["prior_family"], r["classification"], r["owner_or_contract"], r["license"], "false", "false", r["missing_fact_or_reason"]])
    frontier_text = h.getvalue()

    physical = MANIFEST_DIR / "g2-touch-final-physical-byte-buckets.tsv"
    h = io.StringIO(newline="")
    w = csv.writer(h, delimiter="\t", lineterminator="\n")
    w.writerow(["# SPDX-License-Identifier: MIT"])
    w.writerow(["category", "bytes", "address_set_sha256", "content_sha256",
                "owner_or_category", "license_status",
                "unresolved_sub_boundary", "evidence"])
    for r in result["physical_rows"]:
        w.writerow([r["category"], r["bytes"], r["address_set_sha256"],
                    r["content_sha256"], r["owner_or_category"],
                    r["license_status"], r["unresolved_sub_boundary"],
                    r["evidence"]])
    physical_text = h.getvalue()

    fields = [
        "category", "bytes", "address_set_sha256", "content_sha256",
        "entry_count", "entry_set_sha256", "admission_manifests",
        "source_routes", "source_route_license", "claimed_route_licenses",
        "translation_unit_present_in_nonproduction_source_image",
        "adapter_translation_unit_present_in_nonproduction_source_image",
        "semantic_stock_address_candidate_only",
        "admitted_body_linked_to_stock_address", "production_elf_ownership",
        "stock_byte_license_authority", "eula_vendor_source_included",
        "excluded_source_boundaries", "evidence",
    ]
    h = io.StringIO(newline="")
    w = csv.writer(h, delimiter="\t", lineterminator="\n")
    w.writerow(["# SPDX-License-Identifier: MIT"])
    w.writerow(fields)
    for row in result["candidate_provenance_rows"]:
        w.writerow([
            str(row[field]).lower() if isinstance(row[field], bool)
            else row[field]
            for field in fields
        ])
    provenance_text = h.getvalue()

    summary = MANIFEST_DIR / "g2-touch-final-classification-summary.json"
    slim = {k: v for k, v in result.items() if k not in (
        "function_rows", "physical_rows", "candidate_provenance_rows"
    )}
    slim["function_row_count"] = len(result["function_rows"]); slim["physical_row_count"] = len(result["physical_rows"])
    slim["candidate_provenance_row_count"] = len(
        result["candidate_provenance_rows"]
    )
    current = MANIFEST_DIR / "g2-touch-current-source-readiness-summary.json"
    b = result["metrics"]["whole_blob_bucket_bytes"]
    current_payload = {"schema_version": 2, "authoritative_batch": 26,
        "classification_complete": True, "software_function_frontier_complete": True,
        "concrete_source_or_implementation_gap": 0,
        "concrete_gap_instruction_bytes": 0, "unimplemented_application_contracts": 0,
        "typed_external_or_unavailable_functions": 0,
        "typed_external_or_unsupported_functions": 0, "unclassified_functions": 0,
        "whole_blob_bytes": 34464, "whole_blob_bucket_bytes": b,
        "physical_bucket_digest": result["metrics"]["physical_bucket_digest"],
        "candidate_union_address_set_sha256": result["metrics"]["candidate_union_address_set_sha256"],
        "candidate_union_content_sha256": result["metrics"]["candidate_union_content_sha256"],
        "candidate_provenance": result["candidate_provenance"],
        "semantic_stock_address_candidates_only": True,
        "candidate_source_is_production_elf_ownership": False,
        "stock_byte_redistribution_authority": "NOASSERTION",
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
        "production_routed": False,
        "exclusions": "software semantic function frontier is source-backed; semantic stock-address admission is not production ELF ownership; production routing, resident-data replacement accounting, hardware tuning, and stock-binary redistribution authority remain unresolved; Infineon-EULA comparison source is excluded"}
    rendered_outputs = {
        frontier.name: sha256(frontier_text.encode()),
        physical.name: sha256(physical_text.encode()),
        CANDIDATE_PROVENANCE.name: sha256(provenance_text.encode()),
        f"{summary.name}:core": sha256(json.dumps(
            slim, sort_keys=True, separators=(",", ":")
        ).encode()),
        f"{current.name}:core": sha256(json.dumps(
            current_payload, sort_keys=True, separators=(",", ":")
        ).encode()),
    }
    generation_receipt = {
        "logical_manifest_count": 5,
        "generation_receipt_sha256": sha256(json.dumps({
            "analysis_inputs": result["analysis_inputs"],
            "rendered_outputs": rendered_outputs,
        }, sort_keys=True, separators=(",", ":")).encode()),
        "analysis_inputs": result["analysis_inputs"],
        "rendered_outputs": rendered_outputs,
    }
    slim["generation_receipt"] = generation_receipt
    current_payload["generation_receipt"] = generation_receipt
    return {
        frontier: frontier_text,
        physical: physical_text,
        CANDIDATE_PROVENANCE: provenance_text,
        summary: json.dumps(slim, indent=2, sort_keys=True) + "\n",
        current: json.dumps(current_payload, indent=2, sort_keys=True) + "\n",
    }


def check_manifests(result):
    payloads = _manifest_payloads(result)
    for path, expected in payloads.items():
        require(path.is_file() and path.read_text(encoding="utf-8") == expected,
                f"checked Touch final receipt is stale: {path.name}")
    return list(payloads)


def write_manifests(result):
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    payloads = _manifest_payloads(result)
    with tempfile.TemporaryDirectory(
            prefix="g2-touch-final-receipts-", dir=MANIFEST_DIR) as raw:
        staging = Path(raw)
        staged = []
        for path, payload in payloads.items():
            candidate = staging / path.name
            candidate.write_text(payload, encoding="utf-8")
            require(candidate.read_text(encoding="utf-8") == payload,
                    f"staged Touch receipt changed: {path.name}")
            staged.append((candidate, path))
        for candidate, path in staged:
            candidate.replace(path)
    check_manifests(result)
    return list(payloads)


def main():
    p = argparse.ArgumentParser()
    actions = p.add_mutually_exclusive_group()
    actions.add_argument("--write-manifests", action="store_true")
    actions.add_argument("--check-manifests", action="store_true")
    args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    elif args.check_manifests:
        for path in check_manifests(result): print(f"checked {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch final frontier failed: {exc}") from exc
