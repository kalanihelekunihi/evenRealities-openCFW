#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the initial region manifests from recovered payload structure.

Every region starts as `retained`. Its blockers come from
MISSING-TOOLCHAIN.md: toolchain and vendor-object blockers for gated
payloads; OPEN-PENDING plus GATE-FREEZE (G2) for payloads whose toolchain is
open; CONTAINER for regenerable container metadata. Structure comes from:

  touch   g2/tools/manifests/g2-touch-identity-regions.tsv (+ FWPK header)
  case    g2/tools/manifests/g2-case-byte-accounting.tsv   (+ EVEN header)
  codec   g2/tools/manifests/g2-codec-fwpk-segment-map.tsv (leaf regions)
  em9305  record_package.parse_package on the official payload
  apollo  32-byte OTA preamble + image; bootloader as one image region
  r1      the application image as one region

Run it again only to reseed; hand edits (state changes to `source`) are made
in the manifests themselves.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "manifests"
G2 = REPO / "g2"
TARGET = json.loads((G2 / "workflow/target.json").read_text())
G2_OPEN = ["OPEN-PENDING", "GATE-FREEZE"]


def component(cid: str) -> dict:
    return next(c for c in TARGET["components"] if c["id"] == cid)


def rows(path: Path) -> list[dict]:
    lines = [l for l in path.read_text().splitlines() if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def region(label, start, end, blockers, note="", state="retained"):
    entry = {"label": label, "start": f"0x{start:06X}", "end": f"0x{end:06X}", "state": state}
    if state == "retained":
        entry["blockers"] = blockers
    if note:
        entry["note"] = note
    return entry


def manifest(payload, official, size, sha, device, toolchain, regions, notes):
    return {
        "schema": 1,
        "payload": payload,
        "device": device,
        "official": official,
        "size": size,
        "sha256": sha,
        "toolchain": toolchain,
        "notes": notes,
        "regions": regions,
    }


def g2_manifest(cid, payload, toolchain, regions, notes):
    c = component(cid)
    return manifest(payload, c["local_payload_path"], c["size"], c["sha256"], "g2", toolchain, regions, notes)


def touch():
    regs = [region("fwpk_header", 0, 0x20, ["CONTAINER"], "FWPK header with one type-3 record")]
    for r in rows(G2 / "tools/manifests/g2-touch-identity-regions.tsv"):
        start, end = int(r["start"], 16) + 0x20, int(r["end_exclusive"], 16) + 0x20
        blockers = ["CONTAINER"] if r["region"] == "trailing_crc" else G2_OPEN
        regs.append(region(r["region"], start, end, blockers, r["class"]))
    return g2_manifest("touch", "g2-touch", "GCC (release to identify); open", regs,
                       "PSoC 4000T image linked at flash 0x3300 (payload offset + 0x3300) after the 32-byte FWPK header")


def case():
    regs = [region("even_header", 0, 0x20, ["CONTAINER"], "EVEN wrapper: version, BE length, BE additive sum")]
    merged = []
    for r in rows(G2 / "tools/manifests/g2-case-byte-accounting.tsv"):
        start = int(r["start"], 16) - 0x08000000 + 0x20
        end = int(r["end_exclusive"], 16) - 0x08000000 + 0x20
        category = r["category"]
        if merged and merged[-1][2] == category and merged[-1][1] == start:
            merged[-1][1] = end
        else:
            merged.append([start, end, category])
    for index, (start, end, category) in enumerate(merged):
        regs.append(region(f"r{index:03d}_{category}", start, end, G2_OPEN))
    return g2_manifest("case", "g2-case", "GCC + STM32CubeG0 (release to identify); open", regs,
                       "STM32G0 image at 0x08000000 after the 32-byte EVEN wrapper; regions from the case byte accounting")


def codec():
    leaves = {"fwpk_header", "fwpk_records", "boot_header", "boot_stage1", "boot_stage2",
              "binh_a_stage1_block", "binh_a_stage2_xip_len", "binh_a_stage2", "binh_a_extra_payload",
              "binh_b_stage1_block", "binh_b_stage2_xip_len", "binh_b_stage2"}
    regs, cursor = [], 0
    size = component("codec")["size"]
    for r in rows(G2 / "tools/manifests/g2-codec-fwpk-segment-map.tsv"):
        if r["region"] not in leaves:
            continue
        start, length = int(r["package_offset"], 16), int(r["size"])
        if start > cursor:
            regs.append(region(f"gap_{cursor:06X}", cursor, start, G2_OPEN))
        container = r["region"] in {"fwpk_header", "fwpk_records", "boot_header"} or r["region"].endswith("xip_len")
        blockers = ["CONTAINER"] if container else G2_OPEN + ["TC-CSKY-EMU"]
        if r["region"] == "binh_a_extra_payload":
            blockers = G2_OPEN
        regs.append(region(r["region"], start, start + length, blockers, r["destination"]))
        cursor = start + length
    if cursor < size:
        regs.append(region(f"tail_{cursor:06X}", cursor, size, G2_OPEN))
    return g2_manifest("codec", "g2-codec", "C-SKY GCC for CK804EF (release to identify); open", regs,
                       "FWPK with UART boot stages and dual BINH images; binh_a_extra_payload is the 129,964-byte gxNPU KWS model")


def em9305():
    spec = importlib.util.spec_from_file_location("record_package", G2 / "components/em9305/source_image/record_package.py")
    rp = importlib.util.module_from_spec(spec)
    sys.modules["record_package"] = rp
    spec.loader.exec_module(rp)
    c = component("ble_em9305")
    data = (REPO / c["local_payload_path"]).read_bytes()
    parsed = rp.parse_package(data)
    gated = ["TC-METAWARE", "TC-ARCV2-DECOMP", "VO-PACKETCRAFT-LL", "GATE-FREEZE"]
    regs = [region("record_metadata", 0, parsed.metadata_size, ["CONTAINER"], "header, record descriptors, erase-sector table")]
    cursor = parsed.metadata_size
    for index, record in enumerate(parsed.records):
        end = cursor + len(record.payload)
        regs.append(region(f"record{index}_0x{record.address:06X}", cursor, end, gated, f"loads at 0x{record.address:06X}"))
        cursor = end
    return g2_manifest("ble_em9305", "g2-em9305", "Synopsys MetaWare T-2022.09 (licensed; missing)", regs,
                       "byte-identical across all 17 mirrored G2 releases")


def apollo_main():
    c = component("apollo_main")
    regs = [region("ota_preamble", 0, 0x20, ["CONTAINER"], "32-byte OTA staging preamble"),
            region("image", 0x20, c["size"], ["TC-IAR", "VO-NEMAGFX", "GATE-FREEZE"], "Cortex-M55 image linked at 0x00438000")]
    return g2_manifest("apollo_main", "g2-apollo-main", "IAR EWARM + DLIB (licensed; missing)", regs,
                       "split further by function once the pseudocode corpus is frozen")


def apollo_bootloader():
    c = component("apollo_bootloader")
    regs = [region("image", 0, c["size"], ["TC-IAR", "GATE-FREEZE"], "raw Cortex-M55 image linked at 0x00410000")]
    return g2_manifest("apollo_bootloader", "g2-apollo-bootloader", "IAR EWARM (licensed; missing)", regs, "")


def r1_application():
    path = "r1/blobs/official/r1-2.2.6.0009/application.bin"
    data = (REPO / path).read_bytes()
    regs = [region("image", 0, len(data), ["TC-ARMCC5", "VO-GOODIX", "VO-GOMORE"], "application at 0x00027000")]
    return manifest("r1-application", path, len(data), hashlib.sha256(data).hexdigest(), "r1",
                    "Arm Compiler 5.06 (licensed; missing)", regs,
                    "split by function (2,687 attributed functions) as matching begins")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for build in (touch, case, codec, em9305, apollo_main, apollo_bootloader, r1_application):
        m = build()
        (OUT / f"{m['payload']}.json").write_text(json.dumps(m, indent=1) + "\n")
        print(f"{m['payload']}: {len(m['regions'])} regions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
