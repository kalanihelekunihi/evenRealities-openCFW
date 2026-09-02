#!/usr/bin/env python3
"""Authenticate the production G2 bootloader MSPI-control source route."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from analyze_g2_apollo510_mspi_triplet_candidate import run_audit as triplet_audit
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
BOOT_START = 0x004251C0
ADAPTER_END = 0x0042523C
SOURCE_END = 0x0042612C
STOCK_END = 0x004262E0
NEXT_SOURCE_ENTRY = 0x00426506
MAIN_BASE = 0x00438000
MAIN_START = 0x004C0F78
MAIN_END = 0x004C2098

BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PRODUCTION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_control_4251c0.c"
CANDIDATE = ROOT / "research/admission/bootloader_mspi_control_4251c0/runtime_bootloader_mspi_control_candidate.c"
CANDIDATE_HEADER = CANDIDATE.with_suffix(".h")
HOST_FIXTURE = CANDIDATE.parent / "host_fixture.c"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
UPSTREAM_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.h"
UPSTREAM_LICENSE = ROOT / "third_party/ambiqsuite-apollo510/LICENSE"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

BOOT_SHA = "d936cfa583f4d53150c86b30217e2e08ed0698793f13735e365f5a7d0cce0d48"
MAIN_SHA = "a9676ac0717977a1d4be1a730ba02d5dfefc3da780721c8b3ccd3543ca80bf7c"
SOURCE_PIN = (171600, "1c94d258f899221ed519c0025beeb350f3e1b3bedbc71386f554c24978561113")
CALLERS = (0x0041FF5A, 0x00420036, 0x00420EE8, 0x00420F48)
PINS = {
    CANDIDATE: (8229, "4914e60172be80f6e3743ffb77fd4fe500ed3b0a1af691c4ac21cf163c57a85a"),
    CANDIDATE_HEADER: (1728, "dedf0acee5de7e6dc219b5476b479d56c4d576e7d717c54a3b520bf900d5ddd5"),
    HOST_FIXTURE: (3647, "5824f00d57992364d51b0ded5c82f92cad7124aaffad5f9bb1d420811046b448"),
    UPSTREAM: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    UPSTREAM_HEADER: (36982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    UPSTREAM_LICENSE: (1525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
}

PROFILE_PINS = {
    "apple-clang": {
        "directory": ROOT / "components/bootloader/core_overlay/build",
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0",
        "component": (163840, "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"),
        "source_owned": 34557,
        "opaque": 112803,
        "body_unrelocated": "72cded3f11ee2d26547a0b080cc08de5b0328abb90b60a63ed639600ab60bac8",
        "body_relocated": "baa242511305c129975f70959f169012a1719efeacb3d255e0b37eacf840d872",
        "offsets": (900, 976, 1590, 1620, 1992, 2030, 2070, 2078, 2282, 2696, 2706, 2720, 2842, 3052, 3072, 3080, 3094, 3534, 3570, 3626, 3650, 3666, 3702, 3762, 3790),
    },
    "linux-clang": {
        "directory": ROOT / "build/canonical-provider/linux-clang/apollo_bootloader",
        "compiler": "/opt/homebrew/opt/llvm@22/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "component": (163824, "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"),
        "source_owned": 34539,
        "opaque": 112803,
        "body_unrelocated": "4fd5f1910023af3a73e8e14ae9d49ccb63c4c4a044f4c181f57f0e61583795a0",
        "body_relocated": "9b46eb4b0137ce524802b66e6253a5ff539e36278b3735f936901a3b0eb93bd5",
        "offsets": (900, 976, 1590, 1620, 1996, 2034, 2074, 2082, 2286, 2700, 2710, 2724, 2846, 3054, 3074, 3082, 3096, 3536, 3570, 3626, 3650, 3666, 3702, 3762, 3800),
    },
}

WRAPPER_PINS = (
    124,
    "fae859e32377d7075c43b37eca47e9254cc9355de355b3aa61bf28a7e207d1b7",
    "7e909a2a1903c4ef1d62135bac3f80cb1cc5fb71d605b8d5fce680305289ce56",
)
TARGETS = {
    "sched_hiprio": 0x004240AA,
    "mspi_clkgen_ctrl": 0x004249A0,
    "am_hal_cmdq_alloc_block": 0x0042790A,
    "get_pause_val": 0x00423E14,
    "am_hal_cmdq_post_loop_block": 0x00427C12,
    "mspi_cq_pause": 0x00423FB8,
    "am_hal_delay_us": 0x0041D1C0,
    "mspi_device_configure": 0x00424120,
    "am_hal_clkmgr_clock_release": 0x00422364,
    "am_hal_clkmgr_clock_request": 0x004222F0,
    "am_hal_cmdq_post_block": 0x004279F0,
    "am_hal_cmdq_release_block": 0x004279BE,
    "am_hal_cmdq_reset": 0x00427BAA,
    "mspi_get_xip_off_min_delay": 0x00424A18,
    "mspi_cq_enable": 0x00423F8E,
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(path: Path, expected: tuple[int, str]) -> None:
    data = path.read_bytes()
    require((len(data), sha256(data)) == expected, f"pin changed: {path.relative_to(ROOT)}")


def leaf(report: dict[str, object], function: str) -> dict[str, object]:
    matches = [item for item in report["in_place_leaves"] if item["placement"]["function"] == function]
    require(len(matches) == 1, f"missing or duplicate production leaf: {function}")
    return matches[0]


def rebuild_profiles() -> None:
    """Rebuild both reviewed profiles locally; this performs no hardware operation."""
    for name, expected in PROFILE_PINS.items():
        command = ["python3", str(BUILDER), "--output-dir", str(expected["directory"]), "--toolchain-profile", name]
        if name == "linux-clang":
            command += ["--clang", str(expected["compiler"])]
        subprocess.run(command, cwd=ROOT, check=True)


def audit(*, rebuild: bool = False) -> dict[str, object]:
    pinned(PRODUCTION_SOURCE, SOURCE_PIN)
    for path, expected in PINS.items():
        pinned(path, expected)

    source = PRODUCTION_SOURCE.read_text(encoding="utf-8")
    for token in (
        "open_cfw_bootloader_mspi_control_4251c0",
        "open_cfw_bootloader_mspi_control_upstream_4251c0",
        "OPEN_CFW_MSPI_PROFILE_PAD",
        "stock == 10u || stock == 11u",
        "SDR250EN0 = stock - 10u",
    ):
        require(token in source, f"production adaptation token changed: {token}")
    require("Copyright (c) 2025, Ambiq Micro" in UPSTREAM_LICENSE.read_text(), "upstream license changed")

    boot_image = BOOT_IMAGE.read_bytes()
    boot_body = boot_image[BOOT_START - BOOT_BASE:STOCK_END - BOOT_BASE]
    require((len(boot_body), sha256(boot_body)) == (4384, BOOT_SHA), "stock boot control body changed")
    stock_pins = {
        "adapter": (BOOT_START, ADAPTER_END, "e1423ab3f033fb352f3b63ae861e179bb31590de4782410d82ab2d306234550c"),
        "body": (ADAPTER_END, SOURCE_END, "5c3a7efb89fb489997d4caa58c00b93e09fc205fb0dc709f95d6e5def2e5664f"),
        "unreachable_tail": (SOURCE_END, STOCK_END, "c83b4119f0991198d619c51dd5bcd92807c4aafa4d181444e7d9cb484f453bfe"),
        "next_gap": (STOCK_END, NEXT_SOURCE_ENTRY, "7065720a4c3c48652f025fb92f8adcb18ded21ebf7d1289228b744c91411fea4"),
    }
    for name, (start, end, digest) in stock_pins.items():
        require(sha256(boot_image[start - BOOT_BASE:end - BOOT_BASE]) == digest, f"stock {name} interval changed")

    main_package = MAIN_PACKAGE.read_bytes()
    require(len(main_package) == 3_523_396, "main package envelope changed")
    main_body = main_package[32:][MAIN_START - MAIN_BASE:MAIN_END - MAIN_BASE]
    require((len(main_body), sha256(main_body)) == (4384, MAIN_SHA), "main control body changed")
    differences = tuple(i for i, pair in enumerate(zip(boot_body, main_body)) if pair[0] != pair[1])
    require((len(differences), 4384 - len(differences)) == (87, 4297), "cross-image identity changed")
    callers = tuple(address for address in range(BOOT_BASE, BOOT_BASE + len(boot_image) - 3, 2)
                    if decode_bl(boot_image, address) == BOOT_START)
    require(callers == CALLERS, "boot control callers changed")

    triplet = triplet_audit()
    control = triplet["triplet"]["0x004C0F78"]
    require((control["end_exclusive"], control["envelope_bytes"], control["upstream_function"])
            == (MAIN_END, 4384, "am_hal_mspi_control"), "independent main attribution changed")
    require(triplet["request_abi"]["stock_only_unsupported"] == [10, 11], "request ABI changed")
    require(triplet["request_abi"]["all_observed_requests_supported"], "request translation changed")

    if rebuild:
        rebuild_profiles()

    profile_results: dict[str, object] = {}
    for name, expected in PROFILE_PINS.items():
        directory = expected["directory"]
        report = json.loads((directory / "build-report.json").read_text())
        artifact = (directory / "ota_s200_bootloader.bin").read_bytes()
        require((len(artifact), sha256(artifact)) == expected["component"], f"{name} provider changed")
        component = report["component"]
        require((component["size"], component["sha256"]) == expected["component"], f"{name} report changed")
        require(component["source_owned_bytes"] == expected["source_owned"], f"{name} source accounting changed")
        require(component["opaque_base_bytes"] == expected["opaque"], f"{name} retained accounting changed")
        require(component["source_owned_in_place_bytes"] == 18828, f"{name} in-place accounting changed")
        require(report["toolchain"]["version"].startswith(expected["version"]), f"{name} compiler changed")

        wrapper = leaf(report, "open_cfw_bootloader_mspi_control_4251c0")
        wrapper_extract = wrapper["extraction"]
        require((wrapper_extract["runtime_address"], wrapper_extract["size"], wrapper_extract["unrelocated_sha256"], wrapper_extract["sha256"])
                == (BOOT_START, *WRAPPER_PINS), f"{name} adapter leaf changed")
        require([(r["offset"], r["type"], r["symbol"], r["symbol_type"], r["target_address"])
                 for r in wrapper_extract["relocations"]]
                == [(76, "R_ARM_THM_JUMP24", "open_cfw_bootloader_mspi_control_upstream_4251c0", "STT_FUNC", ADAPTER_END)],
                f"{name} adapter relocation changed")

        body = leaf(report, "open_cfw_bootloader_mspi_control_upstream_4251c0")
        body_extract = body["extraction"]
        require((body_extract["runtime_address"], body_extract["size"], body_extract["unrelocated_sha256"], body_extract["sha256"])
                == (ADAPTER_END, 3824, expected["body_unrelocated"], expected["body_relocated"]), f"{name} adapted body changed")
        relocations = body_extract["relocations"]
        require(tuple(r["offset"] for r in relocations) == expected["offsets"], f"{name} relocation offsets changed")
        require(all(r["type"] == "R_ARM_THM_CALL" and TARGETS.get(r["symbol"]) == r["target_address"] for r in relocations),
                f"{name} relocation target contract changed")
        for production_leaf in (wrapper, body):
            require((production_leaf["source"]["size"], production_leaf["source"]["sha256"]) == SOURCE_PIN,
                    f"{name} production source provenance changed")
        profile_results[name] = {
            "component_size": len(artifact),
            "component_sha256": sha256(artifact),
            "source_owned_bytes": component["source_owned_bytes"],
            "retained_official_bytes": component["opaque_base_bytes"],
            "compiler": report["toolchain"]["version"],
            "adapter_sha256": wrapper_extract["sha256"],
            "body_sha256": body_extract["sha256"],
        }

    overlay = json.loads(OVERLAY.read_text())
    leaves = {item["function"]: item for item in overlay["in_place_leaves"]}
    required = {"open_cfw_bootloader_mspi_control_4251c0", "open_cfw_bootloader_mspi_control_upstream_4251c0"}
    require(required <= leaves.keys(), "production leaves are not routed")
    require(all((leaves[key]["source"]["size"], leaves[key]["source"]["sha256"]) == SOURCE_PIN for key in required),
            "overlay production-source pin changed")

    override = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]
    provider = override["provider"]
    require((provider["size"], provider["sha256"], provider["source_owned_bytes"], provider["opaque_base_bytes"])
            == (163840, PROFILE_PINS["apple-clang"]["component"][1], 34557, 112803), "manifest provider authority changed")
    regions = {item["name"]: item for item in override["regions"]}
    expected_regions = {
        "bootloader_mspi_control_4251c0_source_in_place": (BOOT_START, 124, "source_compiled"),
        "bootloader_mspi_control_upstream_42523c_source_in_place": (ADAPTER_END, 3824, "source_compiled"),
        "bootloader_mspi_control_unreachable_tail_42612c_4262e0_official": (SOURCE_END, 436, "official_blob"),
        "bootloader_mspi_blocking_transfer_4262e0_source_in_place": (STOCK_END, 256, "source_compiled"),
        "bootloader_mspi_blocking_transfer_unreachable_tail_and_alignment_4263e0_426450_official": (0x004263E0, 112, "official_blob"),
        "bootloader_mspi_interrupt_enable_426450_source_in_place": (0x00426450, 44, "source_compiled"),
        "bootloader_mspi_interrupt_enable_unreachable_tail_42647c_426484_official": (0x0042647C, 8, "official_blob"),
        "bootloader_mspi_interrupt_disable_426484_source_in_place": (0x00426484, 44, "source_compiled"),
        "bootloader_mspi_interrupt_disable_unreachable_tail_4264b0_4264ba_official": (0x004264B0, 10, "official_blob"),
        "bootloader_mspi_interrupt_status_get_4264ba_source_in_place": (0x004264BA, 60, "source_compiled"),
        "bootloader_mspi_interrupt_status_get_unreachable_tail_4264f6_426506_official": (0x004264F6, 16, "official_blob"),
    }
    for name, expected in expected_regions.items():
        region = regions.get(name)
        require(region is not None and (region["target_address"], region["size"], region["address_status"]) == expected,
                f"manifest region changed: {name}")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-control-") as directory:
        library = Path(directory) / ("control.dylib" if sys.platform == "darwin" else "control.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(CANDIDATE), str(HOST_FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        host = ctypes.CDLL(str(library))
        host.open_cfw_test_control_run_valid.argtypes = [ctypes.c_uint32]
        host.open_cfw_test_control_run_valid.restype = ctypes.c_uint32
        for request in range(40):
            require(host.open_cfw_test_control_run_valid(request) == 0, f"semantic request {request} failed")
            require(host.open_cfw_test_control_run_valid(request | 0x123400) == 0, f"semantic alias {request} failed")
        require(host.open_cfw_test_control_run_valid(40) == 6, "semantic sentinel did not fail closed")
        require(host.open_cfw_test_control_run_valid(255) == 6, "semantic invalid request did not fail closed")

    return {
        "status": "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence",
        "function": {"start": BOOT_START, "stock_end": STOCK_END, "stock_bytes": 4384, "stock_sha256": BOOT_SHA},
        "production": {
            "routed": True,
            "adapter": {"start": BOOT_START, "end": ADAPTER_END, "bytes": 124},
            "adapted_body": {"start": ADAPTER_END, "end": SOURCE_END, "bytes": 3824},
            "source_owned_bytes": 3948,
            "retained_unreachable_tail": {"start": SOURCE_END, "end": STOCK_END, "bytes": 436},
            "next_executable_frontier": {"start": NEXT_SOURCE_ENTRY, "end": 0x00426536, "bytes": 48, "function": "am_hal_mspi_interrupt_clear", "status": "already-source-routed"},
            "profiles": profile_results,
        },
        "cross_image": {"main_start": MAIN_START, "main_end": MAIN_END, "main_sha256": MAIN_SHA,
                        "identical_bytes": 4297, "address_coupled_bytes": 87, "difference_runs": 53},
        "callers": list(callers),
        "semantic_model": {"valid_stock_requests": 40, "low_byte_aliases": 40, "invalid_requests_fail_closed": True},
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--rebuild", action="store_true", help="rebuild both reviewed local toolchain profiles before auditing")
    args = parser.parse_args()
    result = audit(rebuild=args.rebuild)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else
          "Bootloader MSPI control: production source routed for Apple/Linux; hardware validation blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"bootloader MSPI control audit failed: {error}")
