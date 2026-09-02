#!/usr/bin/env python3
"""Verify the production G2 MSPI transfer and interrupt-control tranche."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

import apollo_overlay


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
PRODUCTION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_control_4251c0.c"
UPSTREAM_SOURCE = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
CANDIDATE = ROOT / "research/admission/bootloader_mspi_transfer_interrupt_4262e0/runtime_bootloader_mspi_transfer_interrupt_candidate.c"
CANDIDATE_HEADER = CANDIDATE.with_suffix(".h")
CANDIDATE_FIXTURE = CANDIDATE.parent / "host_fixture.c"
REMOVED_TRANSCRIPT = ROOT / "components/bootloader/core_overlay/runtime_mspi_transfer_interrupt_4262e0.c"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

PROFILES = {
    "apple-clang": {
        "report": ROOT / "components/bootloader/core_overlay/build/build-report.json",
        "provider": ROOT / "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
        "provider_size": 163_840,
        "provider_sha256": "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b",
        "source_owned_bytes": 34_557,
    },
    "linux-clang": {
        "report": ROOT / "build/canonical-provider/linux-clang/apollo_bootloader/build-report.json",
        "provider": ROOT / "build/canonical-provider/linux-clang/apollo_bootloader/ota_s200_bootloader.bin",
        "provider_size": 163_824,
        "provider_sha256": "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875",
        "source_owned_bytes": 34_539,
    },
}

PINS = {
    OFFICIAL: (148_599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"),
    PRODUCTION_SOURCE: (171_600, "1c94d258f899221ed519c0025beeb350f3e1b3bedbc71386f554c24978561113"),
    UPSTREAM_SOURCE: (168_473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    CANDIDATE: (1_626, "c1936e16a49cadb67abeb93396f00b54f455844419523b38c6e9108d1f6cf381"),
    CANDIDATE_HEADER: (1_516, "fc89ffb842dfa3aed6b04d369a7560406bc950414d6a0e5e76bb6711409f33b7"),
    CANDIDATE_FIXTURE: (1_613, "078956d7b6d6c4f6605ed20591106f30df6ef2d9489a51db48797514aa404991"),
}

LEAVES = {
    "open_cfw_bootloader_mspi_blocking_transfer_4262e0": {
        "address": 0x004262E0,
        "size": 256,
        "sha256": "e8660331ae3b0116772257c68dc85cd3dca8616978014351c6cdca3e417dcfec",
        "unrelocated_sha256": "9dc57ef8e95c1068b8bf130457dd1d648277129557eef7799ab05a28a3727f1b",
        "stock_sha256": "9d9bee3e9dbbd2615e09789fce3df20764302c38a05a6759fbb13f259878dcf6",
        "relocations": (
            (196, "mspi_fifo_read", 0x00423E8A, "STT_FUNC"),
            (210, "mspi_fifo_write", 0x00423E40, "STT_FUNC"),
            (228, "am_hal_delay_us_status_check", 0x0041D246, "STT_NOTYPE"),
        ),
        "terminal_offset": 244,
        "terminal_hex": "bde8f883bebebe0100000640",
    },
    "open_cfw_bootloader_mspi_interrupt_enable_426450": {
        "address": 0x00426450,
        "size": 44,
        "sha256": "b19a4d2921f5307882c737a6b50a7d27f39317c3b704a702b39e2f40410155e2",
        "unrelocated_sha256": "b19a4d2921f5307882c737a6b50a7d27f39317c3b704a702b39e2f40410155e2",
        "stock_sha256": "fb0eae3321a1ec54b452e2810f243bbebdceb4417ee399d75239883a30349445",
        "relocations": (),
        "terminal_offset": 32,
        "terminal_hex": "704700bfbebebe0100020640",
    },
    "open_cfw_bootloader_mspi_interrupt_disable_426484": {
        "address": 0x00426484,
        "size": 44,
        "sha256": "930c26c26b7257d53dc5073812cca64b089f577ed8bd432c0469a210555fc166",
        "unrelocated_sha256": "930c26c26b7257d53dc5073812cca64b089f577ed8bd432c0469a210555fc166",
        "stock_sha256": "7af6cb51734e88da326fc5d8ff78d2cd302531927ff3b8022b102d35e9f384ec",
        "relocations": (),
        "terminal_offset": 34,
        "terminal_hex": "7047bebebe0100020640",
    },
    "open_cfw_bootloader_mspi_interrupt_status_get_4264ba": {
        "address": 0x004264BA,
        "size": 60,
        "sha256": "778b82cd9548a726f3430ef90b5922c734d7723a6b8a6bac50641bc72724aefc",
        "unrelocated_sha256": "778b82cd9548a726f3430ef90b5922c734d7723a6b8a6bac50641bc72724aefc",
        "stock_sha256": "84d70ad012b015f8469a6044b21d2e2c7bd7af68b4b0dafd14399ac3cec3fd62",
        "relocations": (),
        "terminal_offset": 48,
        "terminal_hex": "10bd00bfbebebe0100000640",
    },
}

RETAINED_TAILS = {
    "bootloader_mspi_control_unreachable_tail_42612c_4262e0_official": (
        0x0042612C, 0x004262E0, "c83b4119f0991198d619c51dd5bcd92807c4aafa4d181444e7d9cb484f453bfe"
    ),
    "bootloader_mspi_blocking_transfer_unreachable_tail_and_alignment_4263e0_426450_official": (
        0x004263E0, 0x00426450, "750615cb008335b6ec447c757032046216f8913c5a424c2393ccf03f7b545db1"
    ),
    "bootloader_mspi_interrupt_enable_unreachable_tail_42647c_426484_official": (
        0x0042647C, 0x00426484, "95f1b19d4d488b37fd91939552d88e79d1361f2f99f005c937e1d178aadd4256"
    ),
    "bootloader_mspi_interrupt_disable_unreachable_tail_4264b0_4264ba_official": (
        0x004264B0, 0x004264BA, "2cbb69478279294d28007dbc24297342156d44c2c3561c7ed01387394af482e8"
    ),
    "bootloader_mspi_interrupt_status_get_unreachable_tail_4264f6_426506_official": (
        0x004264F6, 0x00426506, "d23bae4506efde890d16f3ac9dbf8753b6970db0c5854c39280dbbb30c8a0eab"
    ),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def authenticated(path: Path, expected: tuple[int, str]) -> bytes:
    payload = path.read_bytes()
    require((len(payload), sha256(payload)) == expected, f"pin changed: {path.relative_to(ROOT)}")
    return payload


def external_wide_ingress(provider: bytes, start: int, end: int) -> list[tuple[int, int]]:
    hits: list[tuple[int, int]] = []
    for offset in range(0, len(provider) - 3, 2):
        address = BOOT_BASE + offset
        try:
            target = apollo_overlay.decode_thumb_branch(address, provider[offset:offset + 4])
        except apollo_overlay.BuildError:
            continue
        if start <= target < end and not start <= address < end:
            hits.append((address, target))
    return hits


def stored_tail_entries(provider: bytes, start: int, end: int) -> list[int]:
    return [target for target in range(start | 1, end, 2) if struct.pack("<I", target) in provider]


def audit() -> dict:
    official = authenticated(OFFICIAL, PINS[OFFICIAL])
    production_source = authenticated(PRODUCTION_SOURCE, PINS[PRODUCTION_SOURCE]).decode()
    upstream_source = authenticated(UPSTREAM_SOURCE, PINS[UPSTREAM_SOURCE]).decode()
    for path in (CANDIDATE, CANDIDATE_HEADER, CANDIDATE_FIXTURE):
        authenticated(path, PINS[path])
    require(not REMOVED_TRANSCRIPT.exists(), "retired raw transcript returned")
    require(not re.search(r"(?m)^\s*\.(?:byte|short|word)\b", production_source)
            and "__asm__" not in production_source,
            "production MSPI source regressed to raw executable encoding")
    for token in (*LEAVES, "mspi_fifo_read", "mspi_fifo_write"):
        require(token in production_source, f"production source token missing: {token}")
    for token in ("am_hal_mspi_blocking_transfer(", "am_hal_mspi_interrupt_enable(",
                  "am_hal_mspi_interrupt_disable(", "am_hal_mspi_interrupt_status_get("):
        require(token in upstream_source, f"upstream source token missing: {token}")

    overlay = json.loads(OVERLAY.read_text())
    configured = {item["function"]: item for item in overlay["in_place_leaves"]}
    for name, facts in LEAVES.items():
        leaf = configured[name]
        relocations = tuple((item["offset"], item["symbol"], item["target_address"], item["symbol_type"])
                            for item in leaf["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"],
                 leaf["source"]["sha256"], leaf["source"]["license"], relocations) ==
                (facts["address"], facts["size"], facts["sha256"], facts["unrelocated_sha256"],
                 facts["stock_sha256"], PINS[PRODUCTION_SOURCE][1], "BSD-3-Clause", facts["relocations"]),
                f"production leaf registration changed: {name}")
        stock = official[facts["address"] - BOOT_BASE:facts["address"] - BOOT_BASE + facts["size"]]
        require(sha256(stock) == facts["stock_sha256"], f"stock prefix changed: {name}")

    manifest = json.loads(MANIFEST.read_text())
    regions = {item["name"]: item for item in manifest["component_overrides"]["apollo_bootloader"]["regions"]}
    for name, (start, end, digest) in RETAINED_TAILS.items():
        body = official[start - BOOT_BASE:end - BOOT_BASE]
        require((len(body), sha256(body)) == (end - start, digest), f"retained tail changed: {name}")
        region = regions[name]
        require((region["target_address"], region["size"], region["address_status"]) ==
                (start, end - start, "official_blob"), f"manifest tail ownership changed: {name}")
    for name, facts in LEAVES.items():
        region_name = name.removeprefix("open_cfw_") + "_source_in_place"
        region = regions[region_name]
        require((region["target_address"], region["size"], region["address_status"]) ==
                (facts["address"], facts["size"], "source_compiled"),
                f"manifest source ownership changed: {region_name}")

    profile_results = {}
    for profile, expected in PROFILES.items():
        report = json.loads(expected["report"].read_text())
        provider = authenticated(expected["provider"], (expected["provider_size"], expected["provider_sha256"]))
        component = report["component"]
        require((component["size"], component["sha256"], component["source_owned_bytes"],
                 component["source_owned_in_place_bytes"], component["opaque_base_bytes"]) ==
                (expected["provider_size"], expected["provider_sha256"], expected["source_owned_bytes"],
                 18_828, 112_803), f"{profile} provider accounting changed")
        require(component["source_owned_bytes"] + component["opaque_base_bytes"] ==
                expected["source_owned_bytes"] + 112_803,
                f"{profile} source/official conservation changed")
        reported = {item["extraction"]["function"]: item for item in report["in_place_leaves"]}
        for name, facts in LEAVES.items():
            extraction = reported[name]["extraction"]
            body = provider[facts["address"] - BOOT_BASE:facts["address"] - BOOT_BASE + facts["size"]]
            require((extraction["runtime_address"], extraction["size"], extraction["sha256"],
                     extraction["unrelocated_sha256"], extraction["relocation_count"], sha256(body)) ==
                    (facts["address"], facts["size"], facts["sha256"], facts["unrelocated_sha256"],
                     len(facts["relocations"]), facts["sha256"]),
                    f"{profile} production leaf changed: {name}")
            require(body[facts["terminal_offset"]:].hex() == facts["terminal_hex"],
                    f"{profile} terminal return/literal boundary changed: {name}")
        for start, end, digest in RETAINED_TAILS.values():
            tail = provider[start - BOOT_BASE:end - BOOT_BASE]
            require(sha256(tail) == digest, f"{profile} retained tail bytes changed: {start:#x}")
            require(external_wide_ingress(provider, start, end) == [],
                    f"{profile} retained tail gained external B.W/BL ingress: {start:#x}")
            require(stored_tail_entries(provider, start, end) == [],
                    f"{profile} retained tail gained a stored Thumb entry: {start:#x}")
        profile_results[profile] = {
            "provider_size": component["size"],
            "provider_sha256": component["sha256"],
            "source_owned_bytes": component["source_owned_bytes"],
            "retained_official_bytes": component["opaque_base_bytes"],
        }

    return {
        "status": "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence",
        "production": {
            "routed": True,
            "source": PRODUCTION_SOURCE.relative_to(ROOT).as_posix(),
            "source_pin": {"size": PINS[PRODUCTION_SOURCE][0], "sha256": PINS[PRODUCTION_SOURCE][1]},
            "source_owned_tranche_bytes": sum(facts["size"] for facts in LEAVES.values()),
            "retained_unreachable_tail_bytes": sum(end - start for start, end, _ in RETAINED_TAILS.values()),
            "boundary_status": "source_compiled_with_authenticated_unreachable_tails",
            "next_frontier": 0x00426506,
            "next_frontier_status": "already-source-routed-interrupt-clear",
        },
        "profiles": profile_results,
        "bounded_mspi_code_closed": True,
        "candidate_semantics_closed": True,
        "adjacent_control": {"start": 0x004251C0, "end_exclusive": 0x004262E0,
                             "status": "production-source-with-authenticated-unreachable-tail"},
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("MSPI transfer/interrupt: 404 production C bytes admitted under both canonical profiles")
        print("  hardware validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as error:
        raise SystemExit(f"transfer/interrupt audit failed: {error}") from error
