#!/usr/bin/env python3
"""Register the reviewed G2 bootloader binary32 math runtime.

This tool updates source-ownership metadata only. It never signs, flashes,
resets, or communicates with hardware.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
CORES = ROOT / "components/bootloader/core_overlay/runtime_float_math_427c90.c"
VENEERS = ROOT / "components/bootloader/core_overlay/runtime_float_math_veneers_427c90.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-float-math-427c90-427e84-source-closure.md"
BOOT_BASE = 0x00410000
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"

FLAGS = [
    "-mcpu=cortex-m55",
    "-mthumb",
    "-Oz",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-fno-ident",
    "-mllvm",
    "-enable-machine-outliner=never",
]

# name, start, authenticated full end, authenticated full SHA, source file,
# compiled size, linked SHA, unrelocated SHA, stock-prefix SHA, call target.
FUNCTIONS = (
    (
        "open_cfw_bootloader_floorf_427c90", 0x00427C90, 0x00427CA0,
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        VENEERS, 16,
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        "253f98c811889e9313a8b570e2e5438176a3ed198a78b1ca6af3e4045cbb8435",
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        ("open_cfw_bootloader_floor_bits_427ca0", 0x00427CA0),
    ),
    (
        "open_cfw_bootloader_floor_bits_427ca0", 0x00427CA0, 0x00427CCC,
        "ba53107c41d7b78d37fea9f4c52330599640f8dab9d4be1bc94e05c8c932d234",
        CORES, 44,
        "ba53107c41d7b78d37fea9f4c52330599640f8dab9d4be1bc94e05c8c932d234",
        "ba53107c41d7b78d37fea9f4c52330599640f8dab9d4be1bc94e05c8c932d234",
        "ba53107c41d7b78d37fea9f4c52330599640f8dab9d4be1bc94e05c8c932d234",
        None,
    ),
    (
        "open_cfw_bootloader_fmodf_427ccc", 0x00427CCC, 0x00427CDC,
        "85ee2ba6a57b18253f0503ab43d1a87345f4afd32574d6c2c51f037847868d38",
        VENEERS, 16,
        "85ee2ba6a57b18253f0503ab43d1a87345f4afd32574d6c2c51f037847868d38",
        "aacb453ff303bb5ebc2e87134a6e9f5d6968807c1a6e04e7691820f9d651d5e8",
        "85ee2ba6a57b18253f0503ab43d1a87345f4afd32574d6c2c51f037847868d38",
        ("open_cfw_bootloader_fmod_bits_427cdc", 0x00427CDC),
    ),
    (
        "open_cfw_bootloader_fmod_bits_427cdc", 0x00427CDC, 0x00427D98,
        "b445746dc37bc912a67822849244ee446bea20d3aada324ef2d7c221481a1a11",
        CORES, 168,
        "ab918e42fe1b08ab253ce9e3b7965066dfb6ddefe9d4a9cf415c3d73bde7bf71",
        "ab918e42fe1b08ab253ce9e3b7965066dfb6ddefe9d4a9cf415c3d73bde7bf71",
        "e93c44c167c52f0c1b61580c3d88cf83c35f1bd8de607376d492dd36d541b355",
        None,
    ),
    (
        "open_cfw_bootloader_roundf_427d98", 0x00427D98, 0x00427DA8,
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        VENEERS, 16,
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        "253f98c811889e9313a8b570e2e5438176a3ed198a78b1ca6af3e4045cbb8435",
        "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
        ("open_cfw_bootloader_round_bits_427da8", 0x00427DA8),
    ),
    (
        "open_cfw_bootloader_round_bits_427da8", 0x00427DA8, 0x00427DD0,
        "aebed9f755ac37e7966dcec1604a58018ee6d52614adba36936aef6cae8dd358",
        CORES, 40,
        "aebed9f755ac37e7966dcec1604a58018ee6d52614adba36936aef6cae8dd358",
        "aebed9f755ac37e7966dcec1604a58018ee6d52614adba36936aef6cae8dd358",
        "aebed9f755ac37e7966dcec1604a58018ee6d52614adba36936aef6cae8dd358",
        None,
    ),
    (
        "open_cfw_bootloader_ceilf_427dd0", 0x00427DD0, 0x00427DE0,
        "835331b3678ebbb1f451d5be4f41c76b348cbcabf12bcd1031cf7d774a6c5445",
        VENEERS, 16,
        "835331b3678ebbb1f451d5be4f41c76b348cbcabf12bcd1031cf7d774a6c5445",
        "2f642fdf84f7388f01e5fa0d4081a053d52853e31645c066f8e335054b034db9",
        "835331b3678ebbb1f451d5be4f41c76b348cbcabf12bcd1031cf7d774a6c5445",
        ("open_cfw_bootloader_ceil_bits_427de0", 0x00427DE0),
    ),
    (
        "open_cfw_bootloader_ceil_bits_427de0", 0x00427DE0, 0x00427E0C,
        "22bcfb42507aa000586ec161020ba803b3727262100d77b9bd55c58edb16d57e",
        CORES, 44,
        "22bcfb42507aa000586ec161020ba803b3727262100d77b9bd55c58edb16d57e",
        "22bcfb42507aa000586ec161020ba803b3727262100d77b9bd55c58edb16d57e",
        "22bcfb42507aa000586ec161020ba803b3727262100d77b9bd55c58edb16d57e",
        None,
    ),
    (
        "open_cfw_bootloader_float_range_classify_427e0c", 0x00427E0C,
        0x00427E84,
        "1330559f27095db52bb9417d2d0512f1ff54c22aea029a6ec5985a9a82184e7b",
        CORES, 72,
        "c7cb3ff6b7a9260c115329d9f98d96aad1f25f5f35e7505475497a6be8c49f6b",
        "c7cb3ff6b7a9260c115329d9f98d96aad1f25f5f35e7505475497a6be8c49f6b",
        "ccaa9972de3f3bb3d51104223f9c7c437a382d3115b0e1371027603e820df057",
        None,
    ),
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    by_start = {item[1]: item for item in FUNCTIONS}
    intervals = [(item[1], item[2]) for item in FUNCTIONS]
    output: list[dict[str, str]] = []
    emitted: set[int] = set()
    for row in rows:
        row_start = int(row["start"], 16)
        if any(start < row_start < end for start, end in intervals):
            continue
        spec = by_start.get(row_start)
        if spec is None:
            output.append(row)
            continue
        name, start, full_end, _full_sha, _source, size, *_rest = spec
        if start in emitted:
            continue
        emitted.add(start)
        source_end = start + size
        short_name = name.removeprefix("open_cfw_bootloader_")
        body = boot[start - BOOT_BASE:source_end - BOOT_BASE]
        output.append({
            "kind": "source_function",
            "name": short_name,
            "start": f"0x{start:08x}",
            "end": f"0x{source_end:08x}",
            "size": str(size),
            "sha256": digest(body),
            "disposition": "source_owned_production",
            "provider": "openCFW freestanding binary32 math runtime",
            "license_status": "MIT",
            "evidence": "reviewed production C is compiled at the authenticated entry with strict dual-toolchain and bit-oracle pins",
        })
        if source_end < full_end:
            tail = boot[source_end - BOOT_BASE:full_end - BOOT_BASE]
            output.append({
                "kind": "unreachable_tail",
                "name": f"{short_name}_tail_{source_end:06x}_{full_end:06x}",
                "start": f"0x{source_end:08x}",
                "end": f"0x{full_end:08x}",
                "size": str(len(tail)),
                "sha256": digest(tail),
                "disposition": "retained_unreachable_tail",
                "provider": "authenticated stock suffix superseded by the in-place C return paths",
                "license_status": "official binary redistribution unresolved",
                "evidence": "no public, direct interior, or stored-pointer ingress; retained as authenticated nonexecuted complement",
            })
    if emitted != set(by_start):
        raise SystemExit("float-math census intervals were not found")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    CENSUS.write_text(stream.getvalue(), encoding="utf-8")


def source_record(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    is_veneer = path == VENEERS
    record = {
        "path": path.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "MIT",
        "origin": (
            "openCFW clean-room fixed-address hard-float ABI veneers"
            if is_veneer else
            "openCFW clean-room rounding/classification cores and bounded musl fmodf adaptation"
        ),
        "evidence": EVIDENCE,
    }
    if not is_veneer:
        record["upstream"] = "musl libc src/math/fmodf.c at tag v1.2.5"
        record["upstream_commit"] = "0784374d561435f7c787a555aeab8ede699ed298"
    return record


def main() -> int:
    boot = BOOT.read_bytes()
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {item[0] for item in FUNCTIONS}
    entries: list[dict[str, Any]] = []
    for spec in FUNCTIONS:
        (name, start, full_end, full_sha, source, size, linked_sha,
         unrelocated_sha, stock_prefix_sha, target) = spec
        full = boot[start - BOOT_BASE:full_end - BOOT_BASE]
        if digest(full) != full_sha:
            raise SystemExit(f"{name}: authenticated stock function changed")
        if digest(full[:size]) != stock_prefix_sha:
            raise SystemExit(f"{name}: authenticated replacement span changed")
        relocations = [] if target is None else [{
            "offset": 6,
            "type": "R_ARM_THM_CALL",
            "symbol": target[0],
            "symbol_type": "STT_NOTYPE",
            "target_address": target[1],
        }]
        pins = {
            "size": size,
            "sha256": linked_sha,
            "unrelocated_sha256": unrelocated_sha,
        }
        entry = {
            "function": name,
            "runtime_address": start,
            "source": source_record(source),
            "toolchain": {
                "target": "arm-none-eabi",
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "flags": FLAGS,
            },
            "strict_relocation_contract": True,
            "expected": pins,
            "stock": {"size": size, "sha256": stock_prefix_sha},
            "relocations": relocations,
            "allow_discarded_alloc_sections": True,
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": pins,
                    "stock": {"size": size, "sha256": stock_prefix_sha},
                    "relocations": relocations,
                }
            },
        }
        entries.append(entry)
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted(
        [*retained, *entries], key=lambda item: int(item["runtime_address"])
    )
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"][
        "component_sha256"
    ] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay)
    update_census(boot)
    print(f"registered {len(entries)} binary32 math in-place C leaves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
