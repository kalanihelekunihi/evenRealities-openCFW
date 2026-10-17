#!/usr/bin/env python3
"""Replay recorded Main library through tail objects from combined RAM source."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
ROOT_RECEIPT = G2 / "build/c-firmware/20261016/main-combined-ram-root-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-late-replay"
STAGES = ("library", "alias-lvgl", "master", "runtime", "tail")
ADDED = {"audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"artifact changed: {name}")
    return path


def names(path, *options):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()
        if line.strip()}


def main():
    root = json.loads(ROOT_RECEIPT.read_text())
    if root["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_ROOT_REPLAY_C":
        raise RuntimeError("combined root replay changed")
    current = checked(root["linked_object"], root["linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for group in STAGES:
        historical = BUILD / f"main-corrected-archive-{group}-replay/receipt.json"
        receipt = json.loads(historical.read_text())
        if len(receipt["stages"]) == 0:
            raise RuntimeError(f"empty replay group: {group}")
        for index, row in enumerate(receipt["stages"], 1):
            old = checked(row["new_object"], row["new_sha256"])
            inputs = dict(row.get("inputs", {}))
            if "input_object" in row:
                inputs[row["input_object"]] = row["input_sha256"]
            objects = [checked(name, digest) for name, digest in inputs.items()]
            aliases = row.get("aliases", {})
            target = OUT / f"{group}-{index:02d}-{row['stage']}.o"
            if row.get("direct_archive_dm_row"):
                if objects or aliases:
                    raise RuntimeError("unexpected direct-archive DM row inputs")
                shutil.copyfile(current, target)
            else:
                subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                                *(str(obj) for obj in objects),
                                *(f"--defsym={name}={provider}"
                                  for name, provider in aliases.items()),
                                "-o", str(target)], check=True)
            before_u, after_u = names(old, "-u"), names(target, "-u")
            before_d = names(old, "-g", "--defined-only")
            after_d = names(target, "-g", "--defined-only")
            expected_removed = before_u & ADDED
            if before_u - after_u != expected_removed or after_u - before_u or \
                    after_d - before_d != ADDED or before_d - after_d:
                raise RuntimeError(f"unexpected RAM replay delta at {group}/{row['stage']}: "
                                   f"imports {before_u-after_u}, {after_u-before_u}; "
                                   f"providers {after_d-before_d}, {before_d-after_d}")
            records.append({"group": group, "stage": row["stage"],
                            "baseline": row["new_object"],
                            "baseline_sha256": row["new_sha256"],
                            "linked": str(target.relative_to(ROOT)),
                            "linked_sha256": sha(target),
                            "inputs": inputs, "aliases": aliases,
                            "imports_resolved_vs_baseline": sorted(expected_removed),
                            "imports_remaining": len(after_u),
                            "providers_added_vs_baseline": sorted(ADDED)})
            current = target
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_LATE_REPLAY_C",
        "root_receipt": str(ROOT_RECEIPT.relative_to(ROOT)),
        "root_receipt_sha256": sha(ROOT_RECEIPT),
        "historical_receipts": {
            group: {"path": str((BUILD / f"main-corrected-archive-{group}-replay/receipt.json").relative_to(ROOT)),
                    "sha256": sha(BUILD / f"main-corrected-archive-{group}-replay/receipt.json")}
            for group in STAGES},
        "stages": records, "stage_count": len(records),
        "linked_object": str(current.relative_to(ROOT)), "linked_sha256": sha(current),
        "unresolved_after": records[-1]["imports_remaining"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Replay reaches the corrected-archive tail, not the later post-tail C bindings or current Main frontier.",
                   "Provider/import parity alone does not establish final RAM layout, stock execution or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], receipt["stage_count"], receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
