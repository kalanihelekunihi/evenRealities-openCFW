#!/usr/bin/env python3
"""Audit the bounded Apollo liblc3 encoder source-provider admission.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
UPSTREAM = G2 / "third_party/liblc3"
SNAPSHOT = UPSTREAM / "SNAPSHOT.sha256"
PROVENANCE = UPSTREAM / "PROVENANCE.json"
LICENSE = UPSTREAM / "LICENSE"
COMPONENT = G2 / "components/shared/liblc3"
ADMISSION = COMPONENT / "encoder_source_admission.json"
PROVIDER_C = COMPONENT / "runtime_liblc3_encoder_provider.c"
PROVIDER_H = COMPONENT / "runtime_liblc3_encoder_provider.h"
ATTRIBUTION = G2 / "tools/manifests/g2-liblc3-encoder-internals-map.tsv"

EXPECTED_COMMIT = "96a3af0beb5487aca3b98a4b992a539a1f6d80d1"
EXPECTED_RUNTIME_RELOCATIONS = {
    "__aeabi_memclr", "__aeabi_memclr4",
    "fabsf", "floorf", "fmaxf", "fminf", "memcpy", "memmove",
    "memset", "roundf", "sqrtf", "truncf",
}
EXPECTED_SOURCES = {
    "src/attdet.c", "src/bits.c", "src/bwdet.c", "src/energy.c",
    "src/lc3.c", "src/ltpf.c", "src/mdct.c", "src/sns.c",
    "src/spec.c", "src/tables.c", "src/tns.c",
}
EXPECTED_TARGET_FLAGS = {
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffast-math",
    "-fshort-enums", "-ffreestanding", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
    "-Werror",
}


class AdmissionError(RuntimeError):
    """Raised when source-provider evidence or its fail-closed contract drifts."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for line in SNAPSHOT.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        if len(digest) != 64 or relative in hashes:
            raise AdmissionError("invalid or duplicate snapshot hash row")
        hashes[relative] = digest
    return hashes


def attribution_rows() -> list[dict[str, str]]:
    lines = [line for line in ATTRIBUTION.read_text().splitlines()
             if line and not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def run_audit() -> dict[str, Any]:
    admission = json.loads(ADMISSION.read_text())
    provenance = json.loads(PROVENANCE.read_text())
    hashes = snapshot_hashes()

    require(admission["schema_version"] == 1, "admission schema drift")
    require(admission["upstream_commit"] == EXPECTED_COMMIT,
            "admission commit drift")
    require(provenance["upstream"]["selected_commit"] == EXPECTED_COMMIT,
            "authenticated snapshot commit drift")
    require(provenance["license"] == admission["license"] == "Apache-2.0",
            "license classification drift")
    require(not provenance["selection"]["exact_public_source_candidate"] and
            not provenance["selection"]["exact_private_checkout_proven"] and
            not admission["exact_generating_checkout_proven"],
            "compatibility baseline was over-promoted to exact source")
    require("Apache License" in LICENSE.read_text(), "license text drift")

    sources = set(admission["upstream_encoder_sources"])
    require(sources == EXPECTED_SOURCES, "encoder source-unit set drift")
    for relative in sorted(sources):
        path = UPSTREAM / relative
        require(relative in hashes, f"{relative}: absent from snapshot manifest")
        require(path.is_file() and sha256(path) == hashes[relative],
                f"{relative}: authenticated source hash drift")

    require(sha256(PROVIDER_C) == admission["provider_source_sha256"],
            "bounded provider source hash drift")
    require(sha256(PROVIDER_H) == admission["provider_header_sha256"],
            "bounded provider header hash drift")
    provider_c = PROVIDER_C.read_text()
    provider_h = PROVIDER_H.read_text()
    require("SPDX-License-Identifier: Apache-2.0" in provider_c and
            "SPDX-License-Identifier: Apache-2.0" in provider_h,
            "bounded provider SPDX drift")
    for entry in admission["provider_entries"]:
        require(entry in provider_c and entry in provider_h,
                f"bounded provider entry missing: {entry}")
    for contract in (
        "sizeof(struct lc3_encoder) == 0x4B0U",
        "_Alignof(struct lc3_encoder) == 8U",
        "sizeof(enum lc3_dt) == 1U",
        "sizeof(enum lc3_srate) == 1U",
        "open_cfw_liblc3_ranges_overlap",
        "open_cfw_liblc3_encoder_provider_seal",
    ):
        require(contract in provider_c, f"provider contract drift: {contract}")

    rows = attribution_rows()
    attributed = [row for row in rows
                  if row["status"] in {"module", "cluster"}]
    unresolved = [row for row in rows
                  if row["status"] == "investigation-required"]
    confidence = {
        name: sum(row["confidence"] == name for row in attributed)
        for name in ("high", "medium", "low")
    }
    attribution = admission["g2_0x59_source_attribution"]
    observed_attribution = {
        "functions": len(attributed),
        "official_opaque_bytes": sum(
            int(row["official_opaque_bytes"]) for row in attributed),
        "high_confidence": confidence["high"],
        "medium_confidence": confidence["medium"],
        "low_confidence": confidence["low"],
        "investigation_required_non_liblc3_functions": len(unresolved),
        "investigation_required_non_liblc3_bytes": sum(
            int(row["official_opaque_bytes"]) for row in unresolved),
    }
    require(attribution == observed_attribution,
            "0x59xxxx attribution reconciliation drift")
    require({row["module"] for row in attributed if row["module"]} ==
            {"lc3", "attdet", "mdct", "energy", "bwdet", "bits", "sns",
             "tns", "spec"}, "attributed encoder module set drift")
    require(all(row["scope"] in {"frontier", "liblc3-bucket"}
                for row in attributed), "attributed function escaped scope")

    require(set(admission["target_profile"]) == EXPECTED_TARGET_FLAGS and
            len(admission["target_profile"]) == len(EXPECTED_TARGET_FLAGS),
            "target compile profile drift")
    require(set(admission["allowed_external_runtime_relocations"]) ==
            EXPECTED_RUNTIME_RELOCATIONS,
            "allowed external-runtime seam drift")
    require(admission["link_contract"] == {
        "roots": admission["provider_entries"],
        "requires_gc_sections": True,
        "decoder_sections_from_lc3_object_must_be_discarded": True,
        "plc_source_in_encoder_route": False,
        "canonical_cantunwind_rows_may_be_discarded": True,
        "all_external_runtime_relocations_must_resolve": True,
        "qualification_relocatable_object_budget": 190000,
    }, "production link contract drift")
    require(set(admission["discarded_section_only_external_relocations"]) == {
        "__aeabi_uldivmod", "lc3_plc_reset", "lc3_plc_suspend",
        "lc3_plc_synthesize",
    }, "discarded-section relocation classification drift")
    require(admission["production_capable_source"] and
            not admission["overlay_routed"],
            "source availability/routing state drift")
    require(admission["build_component"] == {
        "path": "g2/components/apollo_main/liblc3_encoder",
        "build_only": True,
        "placement_assigned": False,
        "service_audio_routed": False,
        "firmware_image_emitted": False,
    }, "build-only component state drift")
    require(len(admission["software_integration_blockers"]) == 4 and
            len(admission["physical_evidence_blockers"]) == 1,
            "blocker ledger drift")

    return {
        "status": "liblc3-encoder-source-admission",
        "upstream": {
            "ref": admission["upstream_ref"],
            "commit": EXPECTED_COMMIT,
            "license": admission["license"],
            "exact_generating_checkout_proven": False,
            "authenticated_encoder_sources": len(sources),
        },
        "g2_0x59_source_attribution": observed_attribution,
        "bounded_provider": {
            "entries": admission["provider_entries"],
            "source_sha256": admission["provider_source_sha256"],
            "header_sha256": admission["provider_header_sha256"],
            "config_size": admission["bounded_provider_abi"]["config_size"],
            "plan_size": admission["bounded_provider_abi"]["plan_size"],
            "provider_size_arm32":
                admission["bounded_provider_abi"]["provider_size_arm32"],
        },
        "target": {
            "profile": admission["target_profile"],
            "allowed_external_runtime_relocations":
                sorted(EXPECTED_RUNTIME_RELOCATIONS),
            "object_size_budgets": admission["object_size_budgets"],
        },
        "production_capable_source": True,
        "overlay_routed": False,
        "build_component": admission["build_component"],
        "software_integration_blockers":
            admission["software_integration_blockers"],
        "physical_evidence_blockers":
            admission["physical_evidence_blockers"],
        "hardware_operations": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), sort_keys=True,
                     indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
