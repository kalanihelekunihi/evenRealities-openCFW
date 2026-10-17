#!/usr/bin/env python3
"""Replay 683 Main post-tail and current C stages with corrected settings/font RAM."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261016"
CORE = BUILD / "main-combined-ram-settings-font-core-replay/receipt.json"
OUT = BUILD / "main-combined-ram-settings-font-feature-replay"
GROUPS = ("post-tail", "current")
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("Main feature replay input changed: " + name)
    return path


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def main():
    core = json.loads(CORE.read_text())
    if core["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_CORE_REPLAY_C" or \
            core["stages_replayed"] != 105:
        raise RuntimeError("corrected core replay changed")
    current = checked(core["linked_object"], core["linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    groups, sequence = [], 0
    for group in GROUPS:
        prior_path = BUILD / f"main-combined-ram-{group}-replay/receipt.json"
        prior = json.loads(prior_path.read_text())
        rows = []
        for row in prior["stages"]:
            sequence += 1
            old = checked(row["linked"], row["linked_sha256"])
            evidence_key = "historical_receipt" if group == "post-tail" else "receipt"
            checked(row[evidence_key], row[evidence_key + "_sha256"])
            input_rows = row["inputs"] if group == "post-tail" else row["objects"]
            inputs = [checked(name, digest) for name, digest in input_rows.items()]
            aliases = row["aliases"]
            target = OUT / f"{sequence:03d}-{group}-{row['stage']}.o"
            if not inputs and not aliases:
                shutil.copyfile(current, target)
            else:
                subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                                *(str(path) for path in inputs),
                                *(f"--defsym={name}={provider}"
                                  for name, provider in aliases.items()),
                                "-o", str(target)], check=True)
            old_u, new_u = names(old, "-u"), names(target, "-u")
            old_d, new_d = names(old, "-g", "--defined-only"), \
                           names(target, "-g", "--defined-only")
            if old_u - new_u != REMOVED & old_u or new_u - old_u or \
                    new_d - old_d != PROVIDERS or old_d - new_d:
                raise RuntimeError("font repair drift at " + group + "/" + row["stage"] +
                                   f": {old_u-new_u} {new_u-old_u} {new_d-old_d} {old_d-new_d}")
            rows.append({"stage": row["stage"], "prior_object": row["linked"],
                         "prior_sha256": sha(old), "receipt": row[evidence_key],
                         "receipt_sha256": row[evidence_key + "_sha256"],
                         "inputs": input_rows, "aliases": aliases,
                         "linked": str(target.relative_to(ROOT)),
                         "linked_sha256": sha(target),
                         "imports_remaining": len(new_u)})
            current = target
        groups.append({"group": group, "prior_receipt": str(prior_path.relative_to(ROOT)),
                       "prior_receipt_sha256": sha(prior_path), "stages": rows,
                       "linked_object": str(current.relative_to(ROOT)),
                       "linked_sha256": sha(current)})
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_FEATURE_REPLAY_C",
               "core_receipt": str(CORE.relative_to(ROOT)),
               "core_receipt_sha256": sha(CORE), "groups": groups,
               "stages_replayed": sequence,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_sha256": sha(current),
               "unresolved_after": groups[-1]["stages"][-1]["imports_remaining"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Post-tail and current source stages carry the corrected C archive; final 13 object/data bindings and whole-image gates remain.",
                          "Import and provider parity alone does not prove physical behavior or final image placement."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sequence, receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
