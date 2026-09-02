#!/usr/bin/env python3
"""Register the G2 SPOT-manager stimulus update and profile-apply entries."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x00410000
APPLE_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FLAGS = ["-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
         "-fno-builtin", "-ffunction-sections", "-fdata-sections",
         "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
         "-Wextra", "-Werror", "-fno-ident", "-mllvm",
         "-enable-machine-outliner=never"]
SPECS = (
    {
        "function": "open_cfw_bootloader_spotmgr_power_state_update_42a878",
        "source": ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_update_42a878.c",
        "source_size": 13_889,
        "source_sha": "748ea09bb3598a3ba045fda4c2c47dea74601faf85bc467966e9574534841859",
        "start": 0x0042A878, "end": 0x0042AB6E,
        "stock_sha": "83deb1cccedcf7dab0c986deaacc2f94baea6d1f74b7e7e387fbdb9f77527079",
        "raw_sha": "2939cbe9bff77ff31332559da4bf012f95b30ea65fd52954eba693168367e137",
        "origin": "Apollo510-compatible SPOT-manager stimulus update pipeline",
        "evidence": "docs/research/g2-bootloader-spotmgr-update-profile-42a878-source-closure.md",
        "relocations": (
            (0x38, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC),
            (0x16A, "open_cfw_bootloader_float_range_classify_427e0c", 0x00427E0C),
            (0x202, "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c", 0x0042A08C),
            (0x27C, "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c", 0x0042A19C),
            (0x2B2, "open_cfw_bootloader_spotmgr_power_state_determine_42a550", 0x0042A550),
            (0x2DA, "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc", 0x0042A4BC),
        ),
    },
    {
        "function": "open_cfw_bootloader_spotmgr_profile_apply_42ab7c",
        "source": ROOT / "components/bootloader/core_overlay/runtime_spotmgr_profile_apply_42ab7c.c",
        "source_size": 2_229,
        "source_sha": "1d1a2d04a25e1fb86c2bbca2c70ed8c7cf0eb1b8a1e2976461ae85e182ec966d",
        "start": 0x0042AB7C, "end": 0x0042ABB2,
        "stock_sha": "686b1225442297793c2d963c1903f0d2fa5dde214abdae1352ad5ade61c326f3",
        "raw_sha": "686b1225442297793c2d963c1903f0d2fa5dde214abdae1352ad5ade61c326f3",
        "origin": "Apollo510-compatible SPOT-manager profile register application",
        "evidence": "docs/research/g2-bootloader-spotmgr-update-profile-42a878-source-closure.md",
        "relocations": (),
    },
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def relocation_records(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
             "symbol_type": "STT_NOTYPE", "target_address": target}
            for offset, symbol, target in spec["relocations"]]


def leaf(spec: dict[str, Any]) -> dict[str, Any]:
    source = spec["source"].read_bytes()
    if len(source) != spec["source_size"] or digest(source) != spec["source_sha"]:
        raise SystemExit(f"source identity changed: {spec['function']}")
    pins = {"size": spec["end"] - spec["start"], "sha256": spec["stock_sha"],
            "unrelocated_sha256": spec["raw_sha"]}
    relocations = relocation_records(spec)
    return {
        "function": spec["function"], "runtime_address": spec["start"],
        "source": {"path": spec["source"].relative_to(ROOT).as_posix(),
                   "size": len(source), "sha256": digest(source),
                   "license": "BSD-3-Clause", "origin": spec["origin"],
                   "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
                   "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
                   "evidence": spec["evidence"]},
        "toolchain": {"target": "arm-none-eabi",
                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                      "flags": FLAGS},
        "strict_relocation_contract": True, "expected": pins,
        "stock": {"size": pins["size"], "sha256": spec["stock_sha"]},
        "relocations": relocations, "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {"linux-clang": {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins, "stock": {"size": pins["size"],
                                          "sha256": spec["stock_sha"]},
            "relocations": relocations}},
    }


def update_census() -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    replacement = (
        ("mixed_gap", "post_mspi_gap_0042a85e", 0x42A85E, 0x42A878,
         "e95dba985414d7d342626f6a294ccb4a3dceb6eb8fccbf67b7c96ed9c5dbee11",
         "typed_nonentry_mixed_or_data", "authenticated shared literal/alignment bytes"),
        ("source_function", "spotmgr_power_state_update_42a878", 0x42A878, 0x42AB6E,
         SPECS[0]["stock_sha"], "source_owned_production",
         "exact dual-toolchain stimulus update with six authenticated provider edges"),
        ("mixed_gap", "post_mspi_gap_0042ab6e", 0x42AB6E, 0x42AB7C,
         "f2838c5b52671afca201230f3ce8bc802364c7646b60fb919c671f18f86c67a5",
         "typed_nonentry_mixed_or_data", "authenticated padding and shared literals"),
        ("source_function", "spotmgr_profile_apply_42ab7c", 0x42AB7C, 0x42ABB2,
         SPECS[1]["stock_sha"], "source_owned_production",
         "exact dual-toolchain profile field application and dispatch-table ingress"),
        ("mixed_gap", "post_mspi_gap_0042abb2", 0x42ABB2, 0x42ABBC,
         "cce5757476e1a29fa450368369bb2ea4bc9663be8c5c697d6f6c69b4bb7adcf9",
         "typed_nonentry_mixed_or_data", "authenticated shared literals and alignment"),
    )
    output_rows: list[dict[str, str]] = []
    replaced = False
    for row in rows:
        if int(row["start"], 16) != 0x42A85E:
            output_rows.append(row)
            continue
        if int(row["end"], 16) != 0x42ABBC:
            raise SystemExit("mixed SPOT-manager census span changed")
        for kind, name, start, end, sha, disposition, evidence in replacement:
            source_owned = disposition == "source_owned_production"
            output_rows.append({
                **row, "kind": kind, "name": name, "start": f"0x{start:08x}",
                "end": f"0x{end:08x}", "size": str(end - start), "sha256": sha,
                "disposition": disposition,
                "provider": ("AmbiqSuite Apollo510 SPOT manager" if source_owned
                             else "linked literal/table/alignment"),
                "license_status": ("BSD-3-Clause" if source_owned
                                   else "authenticated official data"),
                "evidence": evidence,
            })
        replaced = True
    if not replaced:
        raise SystemExit("mixed SPOT-manager census span not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(output_rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes()
    for spec in SPECS:
        body = boot[spec["start"] - BASE:spec["end"] - BASE]
        if digest(body) != spec["stock_sha"]:
            raise SystemExit(f"stock identity changed: {spec['function']}")
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {spec["function"] for spec in SPECS}
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted(
        [*retained, *(leaf(spec) for spec in SPECS)],
        key=lambda item: int(item["runtime_address"]),
    )
    overlay["expected"]["component_sha256"] = APPLE_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_SHA
    write_json(OVERLAY, overlay)
    update_census()
    print("registered SPOT-manager update/profile entries at 0x0042A878/0x0042AB7C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
