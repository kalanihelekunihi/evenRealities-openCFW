#!/usr/bin/env python3
"""Authenticate the G2 bootloader PIO-mixed and dummy-callback source wave."""

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
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "research/admission/bootloader_mspi_piomixed_configure_42488e/runtime_bootloader_mspi_piomixed_configure_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = SOURCE.parent / "host_fixture.c"
DUMMY = SOURCE.parent / "runtime_bootloader_mspi_dummy_callback_candidate.c"
SEQUENCE = SOURCE.parent / "runtime_bootloader_mspi_seq_loopback_candidate.c"
REMOVED_TRANSCRIPT = ROOT / "components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c"
PRODUCTION_DUMMY = ROOT / "components/bootloader/core_overlay/runtime_mspi_dummy_callback_424976.c"
PRODUCTION_SEQUENCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_seq_loopback_424978.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-piomixed-configure-42488e.tsv"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
RUN_BASE = 0x00410000
SPANS = {
    "open_cfw_bootloader_mspi_piomixed_configure_42488e":
        (0x0042488E, 0x00424976,
         "e8323e8e0ac6f59465ce1d30087eb6f4a2e3de336c45bff3e6954325a2e32fee"),
    "open_cfw_bootloader_mspi_dummy_callback_424976":
        (0x00424976, 0x00424978,
         "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "open_cfw_bootloader_mspi_seq_loopback_424978":
        (0x00424978, 0x0042499C,
         "d151d9a6fc63e8f3e8c78e4a670c7a25b34d63318e67c8e423c8a2930bb000e2"),
}
PINS = {
    SOURCE: (2580, "1282384c045eb54f7303010288a2d8d71522c78f972175d40cac2e033cf287ab"),
    HEADER: (1131, "8ae252962369187ffd47a9eeea3e7fda74a7d14c7cb9d040367b92119048b5f3"),
    FIXTURE: (1792, "5659f107c25396dcba0484c505f0103955e7002ac63829ec4f670933924687cf"),
    DUMMY: (450, "4ad853a02e1310bd230a362cc939490bf3c332c1cbafa458d4225de160e89b9c"),
    SEQUENCE: (1470, "0ecbbb75bfe2c2159d9208e94be59443de0f4c2ba069db83c3cc9bee31370ba2"),
    PRODUCTION_DUMMY: (253, "1802398c1e03be93a876763e77f27055d42fc2c25c88222258aeeac420951435"),
    PRODUCTION_SEQUENCE: (634, "4c9f6a9cd1d025b7f1c137d1d0b545647bf91fd19c76a256c8e66444f61bd5b3"),
    BOUNDARY: (1968, "81bd291a8580b37687bd82776cbdcad88030304fd72333bc94527c1c8e6ebfa4"),
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


def extract(path: Path, symbol: str) -> tuple[bytes, int]:
    data, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(sections, f".text.{symbol}")
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
    require(tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                  if decode_bl(image, address) == 0x0042488E) == (0x004258B8,),
            "PIO-mixed caller topology changed")
    require(struct.unpack_from("<I", image, 0x00426C00 - RUN_BASE)[0] == 0x00424977,
            "dummy callback pointer changed")
    successor = image[0x00424978 - RUN_BASE:0x0042499C - RUN_BASE]
    require((len(successor), sha(successor)) ==
            (36, "d151d9a6fc63e8f3e8c78e4a670c7a25b34d63318e67c8e423c8a2930bb000e2"),
            "mspi_seq_loopback successor changed")
    profiles = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-piomixed-audit-") as raw:
        for profile, (compiler, prefix) in PROFILES.items():
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(prefix), f"{profile} identity changed")
            rows = {}
            for source, symbol in ((SOURCE, tuple(SPANS)[0]),
                                   (DUMMY, tuple(SPANS)[1]),
                                   (SEQUENCE, tuple(SPANS)[2])):
                output = Path(raw) / f"{profile}-{symbol}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(source), "-o", str(output)],
                               check=True, capture_output=True, text=True)
                body, relocations = extract(output, symbol)
                start, end, expected_hash = SPANS[symbol]
                require((len(body), sha(body), relocations) ==
                        (end - start, expected_hash, 0), f"{profile} {symbol} changed")
                require(body == image[start - RUN_BASE:end - RUN_BASE],
                        f"{profile} {symbol} is not stock-exact")
                rows[symbol] = {"bytes": len(body), "sha256": sha(body)}
            profiles[profile] = {"version": version, "functions": rows}
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    leaves = {row["function"]: row for row in overlay["in_place_leaves"]}
    for symbol, (start, end, expected_hash) in SPANS.items():
        if symbol == "open_cfw_bootloader_mspi_piomixed_configure_42488e":
            require(symbol not in leaves,
                    "deleted PIO-mixed transcript remains production-routed")
            continue
        leaf = leaves[symbol]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"], leaf["relocations"])
                == (start, end - start, expected_hash, []),
                f"overlay registration changed: {symbol}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    expected_regions = {
        "bootloader_mspi_device_configure_424120_424976_official":
            (0x00424120, 2134, "official_blob"),
        "bootloader_mspi_dummy_callback_424976_source_in_place":
            (0x00424976, 2, "source_compiled"),
        "bootloader_mspi_seq_loopback_424978_source_in_place":
            (0x00424978, 36, "source_compiled"),
        "bootloader_mspi0_base_literal_42499c_opaque":
            (0x0042499C, 4, "official_blob"),
    }
    for name, expected in expected_regions.items():
        require(name in by_name, f"manifest region disappeared: {name}")
        row = by_name[name]
        require((row["target_address"], row["size"], row["address_status"])
                == expected, f"manifest region changed: {name}")
    literal = by_name["bootloader_mspi0_base_literal_42499c_opaque"]
    with tempfile.TemporaryDirectory(prefix="open-cfw-piomixed-component-") as raw:
        subprocess.run(["python3", str(BUILDER), "--output-dir", raw], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        report = json.loads((Path(raw) / "build-report.json").read_text(encoding="utf-8"))
    component = report["component"]
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 147296,
            "component byte conservation changed")
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "component in-place accounting changed")
    return {
        "status": "piomixed-candidate-exact-retained-official / callbacks-production-source / hardware-validation-deferred-by-project-direction",
        "functions": {symbol: {"start": start, "end": end, "bytes": end - start,
                                "sha256": digest}
                      for symbol, (start, end, digest) in SPANS.items()},
        "profiles": profiles,
        "production": {"routed": False,
                       "routed_functions": [
                           "open_cfw_bootloader_mspi_dummy_callback_424976",
                           "open_cfw_bootloader_mspi_seq_loopback_424978",
                       ],
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "boundary_status": "official_blob",
                       "next_frontier": literal["target_address"]},
        "next_frontier": {"start": 0x0042499C, "end": 0x004249A0,
                          "identity": "mspi0_base_literal", "bytes": 4},
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
        print("Bootloader PIO-mixed: exact candidate with retained official production bytes; callbacks remain source-routed")
        print("  next sequential frontier: 0x42499c (MSPI0 base literal)")
        print("  physical validation: deferred by project direction")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader PIO-mixed audit failed: {exc}")
