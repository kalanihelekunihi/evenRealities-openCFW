#!/usr/bin/env python3
"""Authenticate the structured G2 bootloader MSPI lifecycle source closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl


ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = 0x410000
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_lifecycle_host.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-lifecycle-425066.tsv"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fno-jump-tables",
    "-fno-vectorize", "-fno-slp-vectorize", "-mpure-code", "-Wall",
    "-Wextra", "-Werror", "-fno-ident",
)
PROFILES = {
    "apple-clang": (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
    "linux-clang": (
        Path("/opt/homebrew/Cellar/llvm@22/22.1.8/bin/clang"),
        "Homebrew clang version 22.1.8",
    ),
}
PINS = {
    SOURCE: (6019, "7d5deeda0f882a5cf824f94d0e91be41e6c5bd0f7b645c081e8b7d08041e8807"),
    HEADER: (1825, "e5764bebf8ec16efdafcf5734418d2bf36aa43e9768ce2d58729bb6ce4c07574"),
    FIXTURE: (2265, "4f01892ab92abb1cf32811500091242bef3ce53f9f6a57e34722f41f7b991805"),
    BOUNDARY: (2793, "2aa70d26ee5a179b35f6267a12700d4b868d5c18818346f201349185e59f0ae4"),
    UPSTREAM: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
}

FUNCTIONS = {
    "open_cfw_bootloader_mspi_enable_425066": {
        "start": 0x425066,
        "end": 0x4250F0,
        "stock_sha256": "3e8eafec68e5f33ec128fd64c1386692323e9b175993c267d6a2bb7ec3ac155c",
        "compiled_size": 128,
        "compiled_sha256": "c876636f4730b39f87086fb8139b51776718a9d893416679d4ec5b5f479495c4",
        "unrelocated_sha256": "48e3ad6232bc4611f275c1b2e02f56fcccb5afa95a049eb2d6f6a85446ceee48",
        "stock_prefix_sha256": "0549294ff15355c56fef6dfa0ad086c96f46a26045e92ce4168008983082f13d",
        "relocations": [
            {"offset": 46, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_bootloader_mspi_cq_init_423f28", "symbol_type": "STT_NOTYPE", "target_address": 0x423F28},
        ],
        "callers": (0x420378, 0x420E5A),
        "manifest_name": "bootloader_mspi_enable_425066_source_in_place",
    },
    "open_cfw_bootloader_mspi_disable_4250f0": {
        "start": 0x4250F0,
        "end": 0x425166,
        "stock_sha256": "d99c52bed1418f48aab03ebc6fafc8faa36b93f3a980e0bbbacaa423aa7566bc",
        "compiled_size": 112,
        "compiled_sha256": "f446afa834abdde425a837d4d7e20dd8fcbd1ec0fd8b0cc6d155a419d86aec49",
        "unrelocated_sha256": "d691afe79b669a61d3d71ea8ca375f48848c99261ac81af229f0849bb5d36a7f",
        "stock_prefix_sha256": "18922b0a184b20c27df740fad3ce431257959aa8e78671d0f8777590a58a9f9c",
        "relocations": [
            {"offset": 60, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_bootloader_mspi_cq_disable_423fac", "symbol_type": "STT_NOTYPE", "target_address": 0x423FAC},
            {"offset": 70, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_bootloader_mspi_cq_term_423f54", "symbol_type": "STT_NOTYPE", "target_address": 0x423F54},
            {"offset": 106, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_bootloader_delay_us_41d1c0", "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
        ],
        "callers": (0x420E10, 0x42518E),
        "manifest_name": "bootloader_mspi_disable_4250f0_source_in_place",
    },
    "open_cfw_bootloader_mspi_deinitialize_42516c": {
        "start": 0x42516C,
        "end": 0x4251A4,
        "stock_sha256": "17e2e38a57e5a1669a591cf61ad92ff4b5ca8a1747673512410737ac452d689b",
        "compiled_size": 56,
        "compiled_sha256": "2b647746b8f49c15a6b428c66e1e23a77b991bc324f3a94847573d5dc2f833fc",
        "unrelocated_sha256": "efb6f9ca3e303b73d14e3d46abce0f02e36f8748d272a79f94e7029d983805e6",
        "stock_prefix_sha256": "17e2e38a57e5a1669a591cf61ad92ff4b5ca8a1747673512410737ac452d689b",
        "relocations": [
            {"offset": 30, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_bootloader_mspi_disable_4250f0", "symbol_type": "STT_FUNC", "target_address": 0x4250F0},
        ],
        "callers": (0x42031C, 0x42036C, 0x4203A6),
        "manifest_name": "bootloader_mspi_deinitialize_42516c_source_in_place",
        "allowed_defined_targets": frozenset({"open_cfw_bootloader_mspi_disable_4250f0"}),
    },
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def extract(path: Path, name: str, contract: dict[str, object]):
    return apollo_overlay.extract_in_place_function_section(
        path,
        name,
        runtime_address=int(contract["start"]),
        relocation_configs=contract["relocations"],
        strict_relocation_contract=True,
        allow_discarded_alloc_sections=True,
        allowed_defined_relocation_targets=contract.get(
            "allowed_defined_targets", frozenset()
        ),
    )


def audit() -> dict[str, object]:
    for path, expected in PINS.items():
        payload = path.read_bytes()
        require(
            (len(payload), sha256(payload)) == expected,
            f"input pin changed: {path.relative_to(ROOT)}",
        )

    source_text = SOURCE.read_text(encoding="utf-8")
    require(
        ".byte" not in source_text and "__asm__" not in source_text,
        "structured lifecycle source regressed to raw instruction encoding",
    )

    image = OFFICIAL.read_bytes()
    function_results: dict[str, dict[str, object]] = {}
    for name, contract in FUNCTIONS.items():
        start = int(contract["start"])
        end = int(contract["end"])
        stock = image[start - RUN_BASE : end - RUN_BASE]
        compiled_size = int(contract["compiled_size"])
        require(
            (len(stock), sha256(stock))
            == (end - start, contract["stock_sha256"]),
            f"stock function changed: {name}",
        )
        require(
            sha256(stock[:compiled_size]) == contract["stock_prefix_sha256"],
            f"stock replacement prefix changed: {name}",
        )
        callers = tuple(
            address
            for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
            if decode_bl(image, address) == start
        )
        require(callers == contract["callers"], f"caller set changed: {name}")
        function_results[name] = {
            "start": start,
            "end": end,
            "stock_bytes": end - start,
            "compiled_bytes": compiled_size,
            "stock_sha256": contract["stock_sha256"],
            "compiled_sha256": contract["compiled_sha256"],
            "callers": list(callers),
        }

    require(
        image[0x425166 - RUN_BASE : 0x42516C - RUN_BASE].hex()
        == "0000ffff0700",
        "lifecycle alignment gap changed",
    )
    for address, target in (
        (0x42509C, 0x423F28),
        (0x425132, 0x423FAC),
        (0x42513C, 0x423F54),
        (0x42515E, 0x41D1C0),
        (0x42518E, 0x4250F0),
    ):
        require(decode_bl(image, address) == target, f"call edge {address:#x} changed")

    upstream_text = UPSTREAM.read_text(encoding="utf-8")
    for token in (
        "am_hal_mspi_enable",
        "am_hal_mspi_disable",
        "am_hal_mspi_deinitialize",
        "mspi_cq_init",
        "mspi_cq_term",
        "ui32XIPOffMinDelay",
    ):
        require(token in upstream_text, f"upstream token changed: {token}")

    profiles: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-lifecycle-audit-") as temporary:
        for profile, (compiler, version_prefix) in PROFILES.items():
            version = subprocess.run(
                [str(compiler), "--version"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()[0]
            require(version.startswith(version_prefix), f"{profile} compiler changed")
            output = Path(temporary) / f"{profile}.o"
            subprocess.run(
                [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            compiled: dict[str, object] = {}
            for name, contract in FUNCTIONS.items():
                body, report = extract(output, name, contract)
                require(
                    (
                        len(body),
                        sha256(body),
                        report["unrelocated_sha256"],
                        report["relocation_count"],
                    )
                    == (
                        contract["compiled_size"],
                        contract["compiled_sha256"],
                        contract["unrelocated_sha256"],
                        len(contract["relocations"]),
                    ),
                    f"{profile} target object changed: {name}",
                )
                compiled[name] = {
                    "bytes": len(body),
                    "sha256": sha256(body),
                    "unrelocated_sha256": report["unrelocated_sha256"],
                    "relocations": report["relocations"],
                }
            profiles[profile] = {
                "version": version,
                "exact_target_object_asserted": True,
                "functions": compiled,
            }

    config = json.loads(OVERLAY.read_text(encoding="utf-8"))
    leaves = {item["function"]: item for item in config["in_place_leaves"]}
    for name, contract in FUNCTIONS.items():
        leaf = leaves[name]
        require(
            (
                leaf["runtime_address"],
                leaf["expected"]["size"],
                leaf["expected"]["sha256"],
                leaf["expected"]["unrelocated_sha256"],
                leaf["relocations"],
            )
            == (
                contract["start"],
                contract["compiled_size"],
                contract["compiled_sha256"],
                contract["unrelocated_sha256"],
                contract["relocations"],
            ),
            f"production route changed: {name}",
        )

    regions = json.loads(MANIFEST.read_text(encoding="utf-8"))[
        "component_overrides"
    ]["apollo_bootloader"]["regions"]
    by_name = {item["name"]: item for item in regions}
    for contract in FUNCTIONS.values():
        region = by_name[str(contract["manifest_name"])]
        require(
            (
                region["target_address"],
                region["size"],
                region["address_status"],
            )
            == (contract["start"], contract["compiled_size"], "source_compiled"),
            f"manifest source boundary changed: {contract['manifest_name']}",
        )
    enable_tail = by_name[
        "bootloader_mspi_enable_unreachable_tail_4250e6_4250f0_official"
    ]
    require(
        (enable_tail["target_address"], enable_tail["size"], enable_tail["address_status"])
        == (0x4250E6, 10, "official_blob"),
        "enable unreachable-tail boundary changed",
    )
    disable_tail = by_name[
        "bootloader_mspi_disable_tail_and_lifecycle_alignment_425160_opaque"
    ]
    require(
        (disable_tail["target_address"], disable_tail["size"], disable_tail["address_status"])
        == (0x425160, 12, "official_blob"),
        "disable tail/alignment boundary changed",
    )

    with tempfile.TemporaryDirectory(prefix="open-cfw-lifecycle-component-") as temporary:
        subprocess.run(
            ["python3", str(BUILDER), "--output-dir", temporary],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        component = json.loads(
            (Path(temporary) / "build-report.json").read_text(encoding="utf-8")
        )["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"] == 146994,
        "component byte conservation changed",
    )
    require(
        (component["source_owned_bytes"], component["opaque_base_bytes"])
        == (59009, 87985),
        "lifecycle production accounting changed",
    )

    return {
        "status": "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence",
        "functions": function_results,
        "profiles": profiles,
        "production": {
            "routed": True,
            "compiled_bytes": sum(
                int(contract["compiled_size"]) for contract in FUNCTIONS.values()
            ),
            "source_owned_bytes": component["source_owned_bytes"],
            "retained_official_bytes": component["opaque_base_bytes"],
            "boundary_status": "source_compiled",
            "next_frontier": 0x4250E6,
        },
        "successor": {
            "identity": "am_hal_mspi_control",
            "status": "production-source-with-retained-prefix-and-unreachable-tail",
            "start": 0x4251C0,
            "end": 0x4262E0,
            "retained_prefix_bytes": 28,
        },
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    result = audit()
    print(
        json.dumps(result, indent=2, sort_keys=True)
        if parser.parse_args().json
        else "MSPI lifecycle: structured source routed in place across both profiles"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"lifecycle audit failed: {error}")
