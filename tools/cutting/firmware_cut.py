#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Cut official payloads into regions, reassemble them, and account for debt.

Each payload has a region manifest (tools/cutting/manifests/*.json): an
ordered, gap-free list of byte ranges that covers the whole payload. Every
region has a state:

  retained       cut from the official image and carried as bytes; names the
                 blockers (MISSING-TOOLCHAIN.md IDs) that keep it that way
  source         produced by a rebuild; bytes are read from --source-dir
                 <payload>/<label>.bin and must match the official bytes
  vendor-binary  a vendor binary carried by design (not reconstruction debt)

Commands:
  verify   check coverage and blocker IDs, reassemble every payload and
           compare against the locked SHA-256 (fails closed)
  report   retained bytes per payload and per blocker
  cut      write every region's bytes to --out <payload>/<label>.bin
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFESTS = Path(__file__).resolve().parent / "manifests"
REGISTER = REPO / "MISSING-TOOLCHAIN.md"
STATES = {"retained", "source", "vendor-binary"}


class CutError(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blocker_ids() -> set[str]:
    ids = set(re.findall(r"^\| `([A-Z0-9-]+)` \|", REGISTER.read_text(encoding="utf8"), re.M))
    if not ids:
        raise CutError(f"no blocker IDs found in {REGISTER.name}")
    return ids


def load_manifests(names: list[str] | None = None) -> list[dict]:
    paths = sorted(MANIFESTS.glob("*.json"))
    if names:
        paths = [p for p in paths if p.stem in names]
        if len(paths) != len(set(names)):
            raise CutError("unknown manifest name")
    return [json.loads(p.read_text(encoding="utf8")) | {"_path": p} for p in paths]


def check_manifest(manifest: dict, valid_blockers: set[str]) -> None:
    name = manifest["payload"]
    regions = manifest["regions"]
    offset = 0
    labels = set()
    for region in regions:
        start, end = int(region["start"], 16), int(region["end"], 16)
        if start != offset or end <= start:
            raise CutError(f"{name}: region {region['label']} breaks coverage at 0x{offset:X}")
        if region["label"] in labels:
            raise CutError(f"{name}: duplicate label {region['label']}")
        labels.add(region["label"])
        if region["state"] not in STATES:
            raise CutError(f"{name}: {region['label']} has unknown state {region['state']}")
        if region["state"] == "retained":
            blockers = region.get("blockers") or []
            if not blockers:
                raise CutError(f"{name}: retained region {region['label']} names no blocker")
            unknown = [b for b in blockers if b not in valid_blockers]
            if unknown:
                raise CutError(f"{name}: {region['label']} names unknown blockers {unknown}")
        offset = end
    if offset != manifest["size"]:
        raise CutError(f"{name}: regions end at 0x{offset:X}, payload is 0x{manifest['size']:X}")


def official_bytes(manifest: dict) -> bytes:
    path = REPO / manifest["official"]
    data = path.read_bytes()
    if len(data) != manifest["size"] or sha256(data) != manifest["sha256"]:
        raise CutError(f"{manifest['payload']}: {manifest['official']} is not the locked payload")
    return data


def assemble(manifest: dict, source_dir: Path | None) -> bytes:
    stock = official_bytes(manifest)
    out = bytearray()
    for region in manifest["regions"]:
        start, end = int(region["start"], 16), int(region["end"], 16)
        if region["state"] == "source":
            if source_dir is None:
                raise CutError(f"{manifest['payload']}: {region['label']} is source; pass --source-dir")
            built = (source_dir / manifest["payload"] / f"{region['label']}.bin").read_bytes()
            if built != stock[start:end]:
                raise CutError(f"{manifest['payload']}: rebuilt {region['label']} differs from stock")
            out += built
        else:
            out += stock[start:end]
    return bytes(out)


def cmd_verify(args) -> int:
    valid = blocker_ids()
    for manifest in load_manifests(args.payload):
        check_manifest(manifest, valid)
        image = assemble(manifest, args.source_dir)
        if sha256(image) != manifest["sha256"]:
            raise CutError(f"{manifest['payload']}: reassembly hash mismatch")
        print(f"{manifest['payload']}: {len(manifest['regions'])} regions reassemble byte-identically")
    return 0


def cmd_report(args) -> int:
    valid = blocker_ids()
    totals: dict[str, int] = defaultdict(int)
    for manifest in load_manifests(args.payload):
        check_manifest(manifest, valid)
        by_state: dict[str, int] = defaultdict(int)
        for region in manifest["regions"]:
            size = int(region["end"], 16) - int(region["start"], 16)
            by_state[region["state"]] += size
            if region["state"] == "retained":
                for blocker in region["blockers"]:
                    totals[blocker] += size
        parts = ", ".join(f"{k} {v:,}" for k, v in sorted(by_state.items()))
        print(f"{manifest['payload']:<24} {manifest['size']:>10,} B  {parts}")
    print("\nretained bytes by blocker (a region may name several blockers):")
    for blocker, size in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f"  {blocker:<20} {size:>12,}")
    return 0


def cmd_cut(args) -> int:
    valid = blocker_ids()
    for manifest in load_manifests(args.payload):
        check_manifest(manifest, valid)
        stock = official_bytes(manifest)
        target = args.out / manifest["payload"]
        target.mkdir(parents=True, exist_ok=True)
        for region in manifest["regions"]:
            start, end = int(region["start"], 16), int(region["end"], 16)
            (target / f"{region['label']}.bin").write_bytes(stock[start:end])
        print(f"{manifest['payload']}: wrote {len(manifest['regions'])} segments to {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("verify", cmd_verify), ("report", cmd_report), ("cut", cmd_cut)):
        p = sub.add_parser(name)
        p.add_argument("--payload", action="append", help="manifest name (repeatable); default all")
        p.set_defaults(func=func)
        if name == "verify":
            p.add_argument("--source-dir", type=Path)
        if name == "cut":
            p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (CutError, OSError, KeyError, ValueError) as error:
        print(f"firmware_cut: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
