#!/usr/bin/env python3
"""Authenticate the shared Apollo510 clock-manager divider C candidate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTIONS = ROOT / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
CORPUS = ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-06.c"
FRONTIER = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
CLKMGR_HEADER = (
    ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_clkmgr.h"
)
STATUS_HEADER = (
    ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_status.h"
)
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
SOURCE = ROOT / "components/shared/ambiq/runtime_clkmgr_divider_candidate.c"
HEADER = SOURCE.with_suffix(".h")
SUMMARY = ROOT / "tools/manifests/g2-clkmgr-divider-candidate-summary.json"
MAIN_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MAIN_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
BOOT_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
BOOT_REPORT = ROOT / "components/bootloader/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
MAIN_LINUX_REPORT = (
    ROOT / "components/apollo_main/core_overlay/build-linux-clock-record/build-report.json"
)
BOOT_LINUX_REPORT = (
    ROOT / "components/bootloader/core_overlay/build-linux-clock-record/build-report.json"
)
LINUX_PACKAGE = (
    ROOT / "build/source-linux-clock-record/package/"
    "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
)

PINS = {
    BOOT: (148_599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"),
    MAIN: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPUS: (401_413, "c378175fa46f9044fa11edd79129b99ff65ecdf496fc781375708ab74479f379"),
    FRONTIER: (75_754, "76aa4c93419ee7055e6023ae28fa3382551be46fc72456ae700f0a1529780ded"),
    CLKMGR_HEADER: (15_438, "39ea260e7f1bcd06c0ced31bea86508e6861f0fa2a4ddc09571fe01a4f7573e5"),
    STATUS_HEADER: (4_903, "7ffa44277fab4731bdcb742c807c9f026aadfe8456545d8f04f5053621661ee2"),
    PROVENANCE: (18_060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    SOURCE: (1_268, "090373ed2672073930edcf35783fc1fcd785a2a812ca10088f14d8261c8b7498"),
    HEADER: (814, "d00ecb7c890ceea632769bd5c12ad8f2ac15ddf3d82a2b2f558bc031e53fb657"),
}

EXPECTED = {
    0x00426C24: {
        "end": 0x00426C4E,
        "main": 0x004D38EA,
        "sha256": "5d56a93dc2746c295ee2b3507ab4e1be4dae68f057dff4f26b519616bfd486df",
        "callers": (0x0042184C,),
        "candidate": "open_cfw_clkmgr_hfrc2_uq15_divider",
        "semantic": "HFRC2 source prescale and UQ17.15 divider synthesis",
    },
    0x00426C4E: {
        "end": 0x00426C58,
        "main": 0x004D3914,
        "sha256": "15eabeb671434c5c1f485fd4600130400e24f0e1ce62364e4b684e1b6e17bfdf",
        "callers": (0x00421718,),
        "candidate": "open_cfw_clkmgr_hfrc_integer_divider",
        "semantic": "HFRC requested/source integer divider synthesis",
    },
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise AuditError(f"identity drift: {path}")
    return data


def decode_thumb_bl(payload: bytes, address: int) -> int | None:
    offset = address - BOOT_BASE
    if offset < 0 or offset + 4 > len(payload):
        return None
    first, second = struct.unpack_from("<HH", payload, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22) |
                 ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_callers(payload: bytes, target: int) -> tuple[int, ...]:
    return tuple(address for address in range(
        BOOT_BASE, BOOT_BASE + len(payload) - 3, 2
    ) if decode_thumb_bl(payload, address) == target)


def _production_route(config_path: Path, report_path: Path, *,
                      bootloader: bool,
                      profile: str = "apple-clang") -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    leaf_key = "cave_leaves" if bootloader else "relocated_leaves"
    configured = {item.get("function"): item for item in config[leaf_key]
                  if item.get("function") in
                  {facts["candidate"] for facts in EXPECTED.values()}}
    emitted = {item["extraction"]["function"]: item
               for item in report[leaf_key]
               if item["extraction"]["function"] in configured}
    if set(configured) != {facts["candidate"] for facts in EXPECTED.values()} or \
            set(emitted) != set(configured):
        raise AuditError(f"{leaf_key} clock-manager route is incomplete")
    sites = {item["name"]: item for item in report["overlay"]["patched_sites"]
             if "clkmgr_" in item["name"]}
    if len(sites) != 2:
        raise AuditError("clock-manager entry patch count changed")
    records = []
    expected_entries = {
        facts["candidate"]: (start if bootloader else facts["main"],
                             facts["end"] - start, facts["sha256"])
        for start, facts in EXPECTED.items()
    }
    for function, (entry, stock_size, stock_sha) in expected_entries.items():
        leaf = emitted[function]
        extraction = leaf["extraction"]
        placement = leaf["placement"]
        candidate = configured[function]
        matching_sites = [site for site in sites.values()
                          if site["target_function"] == function]
        if len(matching_sites) != 1:
            raise AuditError(f"entry route missing for {function}")
        site = matching_sites[0]
        if (int(site["runtime_address"]), int(site["expected_size"]),
                site["expected_sha256"], int(site["target_address"])) != (
                entry, stock_size, stock_sha,
                int(extraction["runtime_address"])):
            raise AuditError(f"entry route drift for {function}")
        if (int(extraction["size"]), extraction["sha256"],
                int(extraction["relocation_count"])) != (
                int(candidate["expected"]["size"]),
                candidate["expected"]["sha256"], 0):
            raise AuditError(f"compiled leaf drift for {function}")
        if int(placement["size"]) != int(extraction["size"]):
            raise AuditError(f"placement size drift for {function}")
        records.append({
            "function": function,
            "stock_entry": f"0x{entry:08X}",
            "stock_bytes": stock_size,
            "source_address": extraction["runtime_address_hex"],
            "source_bytes": int(extraction["size"]),
            "source_sha256": extraction["sha256"],
            "entry_replacement_hex": site["replacement_hex"],
            "relocations": int(extraction["relocation_count"]),
        })
    component = report["component"]
    expected_component = (config["expected"] if profile == "apple-clang"
                          else config["toolchain_profiles"][profile]["expected"])
    if (int(component["size"]), component["sha256"]) != (
            int(expected_component["component_size"]),
            expected_component["component_sha256"]):
        raise AuditError("clock-manager component pin drift")
    return {
        "component_size": int(component["size"]),
        "component_sha256": component["sha256"],
        "placement_kind": "authenticated_generated_nop_caves"
        if bootloader else "canonical_appended_overlay_leaves",
        "toolchain_profile": profile,
        "records": records,
    }


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path) for path in PINS}
    boot = inputs[BOOT]
    main = inputs[MAIN]
    rows = {int(row["start"], 16): row for row in csv.DictReader(
        inputs[FRONTIER].decode().splitlines(), delimiter="\t"
    )}
    main_functions = {int(row["entry"], 16): row for row in (
        json.loads(line) for line in inputs[FUNCTIONS].decode().splitlines()
    ) if int(row["entry"], 16) in {facts["main"] for facts in EXPECTED.values()}}
    corpus = inputs[CORPUS].decode(errors="ignore")
    records = []
    for start, facts in EXPECTED.items():
        end = facts["end"]
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        main_start = facts["main"]
        main_body = main[main_start - MAIN_BASE:main_start - MAIN_BASE + len(body)]
        if len(body) != end - start or sha256(body) != facts["sha256"]:
            raise AuditError(f"stock bootloader body drift: 0x{start:08X}")
        if body != main_body:
            raise AuditError(f"cross-image identity drift: 0x{start:08X}")
        if direct_callers(boot, start) != facts["callers"]:
            raise AuditError(f"bootloader caller topology drift: 0x{start:08X}")
        row = rows.get(start, {})
        if (row.get("end"), row.get("size"), row.get("sha256"),
                row.get("disposition")) != (
                    f"0x{end:08x}", str(end - start), facts["sha256"],
                    "cross_image_exact_source_candidate"):
            raise AuditError(f"frontier record drift: 0x{start:08X}")
        function = main_functions.get(main_start)
        if function is None or (function["body_bytes"], function["body_sha256"],
                                function["callees"]) != (
                                    end - start, facts["sha256"], []):
            raise AuditError(f"main function record drift: 0x{main_start:08X}")
        marker = f"/* FUN 0x{main_start:08x} "
        position = corpus.find(marker)
        if position < 0 or facts["sha256"] not in corpus[position:position + 180]:
            raise AuditError(f"main decompilation marker drift: 0x{main_start:08X}")
        records.append({
            "bootloader_entry": f"0x{start:08X}",
            "bootloader_end_exclusive": f"0x{end:08X}",
            "apollo_main_exact_match": f"0x{main_start:08X}",
            "bytes_per_image": end - start,
            "cross_image_bytes": 2 * (end - start),
            "body_sha256": facts["sha256"],
            "bootloader_direct_callers": [f"0x{x:08X}" for x in facts["callers"]],
            "candidate_symbol": facts["candidate"],
            "semantic_contract": facts["semantic"],
        })

    provenance = json.loads(inputs[PROVENANCE])
    if provenance["upstream"]["selected_commit"] != \
            "5efc0228528a8adce5eae0d226fac85d2551eb3b":
        raise AuditError("AmbiqSuite provenance drift")
    clock_header = inputs[CLKMGR_HEADER].decode()
    status_header = inputs[STATUS_HEADER].decode()
    for token in ("am_hal_clkmgr_clock_config(",
                  "AM_HAL_CLKMGR_HFRC2_FREQ_ADJ_196P608MHZ"):
        if token not in clock_header:
            raise AuditError(f"public clock-manager contract drift: {token}")
    if "AM_HAL_STATUS_INVALID_ARG" not in status_header:
        raise AuditError("public Ambiq status contract drift")
    combined = inputs[SOURCE].decode("ascii") + inputs[HEADER].decode("ascii")
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise AuditError("candidate MIT declarations drift")
    for facts in EXPECTED.values():
        if combined.count(facts["candidate"]) < 2:
            raise AuditError(f"candidate API missing: {facts['candidate']}")
    if "__asm" in combined or ".byte" in combined:
        raise AuditError("candidate contains raw instruction directives")

    production = {
        "apollo_main": _production_route(
            MAIN_CONFIG, MAIN_REPORT, bootloader=False),
        "apollo_bootloader": _production_route(
            BOOT_CONFIG, BOOT_REPORT, bootloader=True),
    }
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    for key, component in (("apollo_main", "apollo_main"),
                           ("apollo_bootloader", "apollo_bootloader")):
        provider = manifest["component_overrides"][component]["provider"]
        route = production[key]
        if (int(provider["size"]), provider["sha256"]) != (
                route["component_size"], route["component_sha256"]):
            raise AuditError(f"{key} source-manifest provider pin drift")
    package = PACKAGE.read_bytes()
    if (len(package), sha256(package)) != (
            int(manifest["package"]["expected_size"]),
            manifest["package"]["expected_sha256"]):
        raise AuditError("clock-manager source package pin drift")
    production["package"] = {
        "size": len(package),
        "sha256": sha256(package),
        "manifest_providers_routed": 2,
    }
    linux = {
        "apollo_main": _production_route(
            MAIN_CONFIG, MAIN_LINUX_REPORT, bootloader=False,
            profile="linux-clang"),
        "apollo_bootloader": _production_route(
            BOOT_CONFIG, BOOT_LINUX_REPORT, bootloader=True,
            profile="linux-clang"),
    }
    for key, component in (("apollo_main", "apollo_main"),
                           ("apollo_bootloader", "apollo_bootloader")):
        provider = manifest["component_overrides"][component]["provider"]
        pin = provider["profiles"]["linux-clang"]
        route = linux[key]
        if (int(pin["size"]), pin["sha256"]) != (
                route["component_size"], route["component_sha256"]):
            raise AuditError(f"{key} Linux source-manifest provider pin drift")
    linux_package = LINUX_PACKAGE.read_bytes()
    linux_package_pin = manifest["package"]["profiles"]["linux-clang"]
    if (len(linux_package), sha256(linux_package)) != (
            int(linux_package_pin["expected_size"]),
            linux_package_pin["expected_sha256"]):
        raise AuditError("clock-manager Linux source package pin drift")
    linux["package"] = {
        "size": len(linux_package),
        "sha256": sha256(linux_package),
        "manifest_providers_routed": 2,
    }
    production["linux_clang"] = linux

    boot_bytes = sum(row["bytes_per_image"] for row in records)
    return {
        "schema_version": 1,
        "status": "apollo-clkmgr-divider-production-routed",
        "analysis_mode": "offline; no hardware, MMIO, signing, flashing, or publishing operation",
        "provider_evidence": {
            "family": "AmbiqSuite Apollo510 clock manager",
            "public_header_contract": "am_hal_clkmgr_clock_config",
            "public_implementation_available": False,
            "authenticated_upstream_commit": provenance["upstream"]["selected_commit"],
            "exact_cross_image_machine_body": True,
        },
        "stock": {
            "functions_per_image": len(records),
            "bootloader_bytes": boot_bytes,
            "apollo_main_bytes": boot_bytes,
            "cross_image_bytes": boot_bytes * 2,
            "records": records,
        },
        "candidate": {
            "license": "MIT",
            "semantic_c": True,
            "raw_instruction_bytes": 0,
            "functions": 2,
            "invalid_input_policy": "fail closed with AM_HAL_STATUS_INVALID_ARG-compatible status 6 and no output mutation",
            "production_routed": True,
            "cross_toolchain_routed": True,
            "software_blocker": None,
        },
        "production": production,
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_manifest:
        SUMMARY.write_text(rendered, encoding="utf-8")
        print(f"wrote {SUMMARY}")
    else:
        print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
