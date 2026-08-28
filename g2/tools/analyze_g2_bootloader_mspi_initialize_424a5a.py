#!/usr/bin/env python3
"""Authenticate the G2 bootloader am_hal_mspi_initialize source closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl


ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = 0x00410000
ENTRY = 0x00424A5A
END = 0x00424AEA
STOCK_SHA = "7708fb5a3bfd2f3f137722f96dc65a9a566da5c70470a014a565df98e2ed87dc"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "research/admission/bootloader_mspi_initialize_424a5a/runtime_bootloader_mspi_initialize_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = SOURCE.parent / "host_fixture.c"
REMOVED_TRANSCRIPT = ROOT / "components/bootloader/core_overlay/runtime_mspi_initialize_424a5a.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-initialize-424a5a.tsv"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
PINS = {
    SOURCE: (2239, "774f9e2ef313d01dd2bdc757fd03fea298f633521f0fe1e5cd70a5906fe559a2"),
    HEADER: (715, "93990ecf52d50de736299f3700ec978f59d813b206e20fcc41b7665af546f520"),
    FIXTURE: (1554, "2e310832515505b47ff38f154fa39dcfba692174528ed6f5e80e44b965ee9f56"),
    BOUNDARY: (1929, "9c3bc347dabec7e901479a6b811ca53e6ba66661d2f345ec0389e2de06cfc63c"),
    UPSTREAM: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    PROVENANCE: (18060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
}
FLAGS = ("-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
         "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
         "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
         "-Wextra", "-Werror", "-fno-ident")
PROFILES = {
    "apple-clang": (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
    "linux-clang": (Path("/opt/homebrew/opt/llvm@22/bin/clang"),
                    "Homebrew clang version 22.1.8"),
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def extract(path: Path) -> tuple[bytes, int]:
    data, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(
        sections, ".text.open_cfw_bootloader_mspi_initialize_424a5a")
    body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    relocations = sum(int(row["size"]) // 8 for row in sections
                      if int(row["type"]) == 9 and
                      int(row["info"]) == int(section["index"]))
    return body, relocations


def audit() -> dict:
    require(not REMOVED_TRANSCRIPT.exists(),
            "raw executable transcript returned to public component source")
    for path, expected in PINS.items():
        payload = path.read_bytes()
        require((len(payload), sha(payload)) == expected,
                f"input pin changed: {path.relative_to(ROOT)}")
    image = OFFICIAL.read_bytes()
    stock = image[ENTRY - RUN_BASE:END - RUN_BASE]
    require((len(stock), sha(stock)) == (144, STOCK_SHA), "stock body changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == ENTRY)
    require(callers == (0x0042029A,), "caller topology changed")
    require(image[0x00424AEA - RUN_BASE:0x00424AEC - RUN_BASE] == b"\x00\x00",
            "post-function alignment changed")
    require(struct.unpack_from("<I", image, 0x00424AEC - RUN_BASE)[0] == 0x2001CAA0,
            "adjacent state-base literal changed")
    require(struct.unpack_from("<I", image, 0x004251AC - RUN_BASE)[0] == 0x2001CAA0,
            "PC-relative state-base literal changed")
    upstream = UPSTREAM.read_text(encoding="utf-8")
    for token in ("am_hal_mspi_initialize", "g_MSPIState[ui32Module].prefix.s.bInit",
                  "AM_HAL_MAGIC_MSPI", "AM_HAL_CLKMGR_CLK_ID_MAX",
                  "ui32XIPOffMinDelay = 8"):
        require(token in upstream, f"upstream identity token changed: {token}")

    profiles = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-initialize-audit-") as raw:
        for profile, (compiler, prefix) in PROFILES.items():
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(prefix), f"{profile} identity changed")
            outputs = {}
            for label, source in (("candidate", SOURCE),):
                output = Path(raw) / f"{profile}-{label}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(source), "-o", str(output)],
                               check=True, capture_output=True, text=True)
                body, relocations = extract(output)
                require((len(body), sha(body), relocations) == (144, STOCK_SHA, 0),
                        f"{profile} {label} body changed")
                require(body == stock, f"{profile} {label} is not stock-exact")
                outputs[label] = sha(body)
            profiles[profile] = {"version": version, "objects": outputs}

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(all(row["function"] != "open_cfw_bootloader_mspi_initialize_424a5a"
                for row in overlay["in_place_leaves"]),
            "deleted transcript remains production-routed")
    regions = json.loads(MANIFEST.read_text(encoding="utf-8"))[
        "component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    retained = by_name["bootloader_opaque_after_easylogger_transport"]
    require((retained["target_address"], retained["size"],
             retained["address_status"]) == (ENTRY, 6828, "official_blob"),
            "retained official MSPI boundary changed")
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-initialize-component-") as raw:
        subprocess.run(["python3", str(BUILDER), "--output-dir", raw], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        component = json.loads((Path(raw) / "build-report.json").read_text(
            encoding="utf-8"))["component"]
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 147296,
            "byte conservation changed")
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "in-place source accounting exceeds all source-owned bytes")
    return {
        "status": "candidate-exact-dual-profile / production-retained-official-boundary / hardware-validation-deferred-by-project-direction",
        "stock": {"start": ENTRY, "end": END, "bytes": 144, "sha256": STOCK_SHA},
        "callers": list(callers),
        "profiles": profiles,
        "state_abi": {"stride": 0x8D0, "modules": 4, "base": 0x2001CAA0,
                      "prefix": 0, "module": 4, "clock_frequency": 0x0C,
                      "tcb": 0x18, "clock_source": 0x8C9,
                      "xip_off_min_delay": 0x8CC},
        "production": {"routed": False,
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "boundary_status": "official_blob",
                       "next_frontier": END},
        "next_code_frontier": {"start": 0x00424AF0, "end": 0x00424BD4,
                               "identity": "am_hal_mspi_configure", "bytes": 228,
                               "status": "official_blob"},
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    report = audit()
    if parser.parse_args().json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader MSPI initialize: exact candidate; production retains authenticated official bytes")
        print("  next code frontier: 0x424af0 (am_hal_mspi_configure)")
        print("  physical validation: deferred by project direction")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"MSPI initialize audit failed: {exc}")
