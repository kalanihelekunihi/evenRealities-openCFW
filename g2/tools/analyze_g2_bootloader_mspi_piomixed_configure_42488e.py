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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_piomixed_configure_host.c"
DUMMY = ROOT / "research/admission/bootloader_mspi_piomixed_configure_42488e/runtime_bootloader_mspi_dummy_callback_candidate.c"
SEQUENCE = ROOT / "research/admission/bootloader_mspi_piomixed_configure_42488e/runtime_bootloader_mspi_seq_loopback_candidate.c"
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
    SOURCE: (1939, "90f8f61f648b6086e14faf7a2fdfe68e1c11615bc4df1d4ea4c113c46e6b4f29"),
    HEADER: (1401, "2f97f272af211bb37a4d73e7f9d4373f209364eafccb868a4af83b669cf0c677"),
    FIXTURE: (2165, "7a99d11414f3283dbee0fd45bab940558755bb9b66d29c2e1e105911687bec67"),
    DUMMY: (450, "4ad853a02e1310bd230a362cc939490bf3c332c1cbafa458d4225de160e89b9c"),
    SEQUENCE: (1470, "0ecbbb75bfe2c2159d9208e94be59443de0f4c2ba069db83c3cc9bee31370ba2"),
    PRODUCTION_DUMMY: (253, "1802398c1e03be93a876763e77f27055d42fc2c25c88222258aeeac420951435"),
    PRODUCTION_SEQUENCE: (634, "4c9f6a9cd1d025b7f1c137d1d0b545647bf91fd19c76a256c8e66444f61bd5b3"),
    BOUNDARY: (1990, "9409cd53fa860ecb4d214c076a2ac19f6422728bb335d167120ad4f623f027ae"),
}
FLAGS = ("-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
         "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
         "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
         "-fno-jump-tables", "-mpure-code", "-Wall",
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
                expected_body = ((84,
                                  "6269fba16f490f502f6d00c87e76b4fa9521b9d9e97fbf6f7a04dd02ec9f6044")
                                 if symbol == tuple(SPANS)[0]
                                 else (end - start, expected_hash))
                require((len(body), sha(body), relocations) ==
                        (*expected_body, 0), f"{profile} {symbol} changed")
                if symbol != tuple(SPANS)[0]:
                    require(body == image[start - RUN_BASE:end - RUN_BASE],
                            f"{profile} {symbol} is not stock-exact")
                rows[symbol] = {"bytes": len(body), "sha256": sha(body)}
            profiles[profile] = {"version": version, "functions": rows}
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    leaves = {row["function"]: row for row in overlay["in_place_leaves"]}
    source_text = SOURCE.read_text(encoding="utf-8")
    require(".byte" not in source_text and "__asm__" not in source_text,
            "structured PIO-mixed source regressed to raw executable encoding")
    for symbol, (start, end, expected_hash) in SPANS.items():
        leaf = leaves[symbol]
        expected_size, routed_hash = ((84,
            "6269fba16f490f502f6d00c87e76b4fa9521b9d9e97fbf6f7a04dd02ec9f6044")
            if symbol == "open_cfw_bootloader_mspi_piomixed_configure_42488e"
            else (end - start, expected_hash))
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"], leaf["relocations"])
                == (start, expected_size, routed_hash, []),
                f"overlay registration changed: {symbol}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    expected_regions = {
        "bootloader_mspi_device_configure_424120_source_in_place":
            (0x00424120, 284, "source_compiled"),
        "bootloader_mspi_device_configure_unreachable_tail_42423c_42488e_official":
            (0x0042423C, 1618, "official_blob"),
        "bootloader_mspi_piomixed_configure_42488e_source_in_place":
            (0x0042488E, 84, "source_compiled"),
        "bootloader_mspi_piomixed_configure_unreachable_tail_4248e2_424976_official":
            (0x004248E2, 148, "official_blob"),
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
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 147350,
            "component byte conservation changed")
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "component in-place accounting changed")
    return {
        "status": "piomixed-structured-source-dual-profile / callbacks-production-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "functions": {symbol: {"start": start, "end": end, "bytes": end - start,
                                "sha256": digest}
                      for symbol, (start, end, digest) in SPANS.items()},
        "profiles": profiles,
        "production": {"routed": True,
                       "compiled_bytes": 84,
                       "compiled_sha256": "6269fba16f490f502f6d00c87e76b4fa9521b9d9e97fbf6f7a04dd02ec9f6044",
                       "routed_functions": [
                           "open_cfw_bootloader_mspi_dummy_callback_424976",
                           "open_cfw_bootloader_mspi_seq_loopback_424978",
                       ],
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "boundary_status": "source_compiled",
                       "next_frontier": literal["target_address"]},
        "next_frontier": {"start": 0x0042499C, "end": 0x004249A0,
                          "identity": "mspi0_base_literal", "bytes": 4},
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    report = audit()
    if parser.parse_args().json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader PIO-mixed: structured source routed in place; callbacks remain source-routed")
        print("  next sequential frontier: 0x42499c (MSPI0 base literal)")
        print("  physical validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader PIO-mixed audit failed: {exc}")
