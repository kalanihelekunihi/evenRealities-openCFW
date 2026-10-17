#!/usr/bin/env python3
"""Replay receipt-linked Main library, LVGL, master, runtime and tail stages."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware"
PRIOR = BUILD / "20261014"
OUT = BUILD / "20261016/main-settings-font-later-replay"
ROOT_RECEIPT = BUILD / "20261016/main-settings-font-root-replay/receipt.json"
PHASES = ("library", "alias-lvgl", "master", "runtime", "tail")
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("later replay input changed: " + name)
    return path


def main():
    root = json.loads(ROOT_RECEIPT.read_text())
    if root["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_ROOT_REPLAY_C":
        raise RuntimeError("corrected root replay changed")
    current = checked(root["linked_object"], root["linked_object_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    phase_rows = []
    sequence = 0
    for phase in PHASES:
        prior_path = PRIOR / f"main-corrected-archive-{phase}-replay/receipt.json"
        prior = json.loads(prior_path.read_text())
        stages = []
        for row in prior["stages"]:
            sequence += 1
            old = checked(row["new_object"], row["new_sha256"])
            input_rows = row.get("inputs")
            if input_rows is None:
                input_rows = {row["input_object"]: row["input_sha256"]}
            inputs = [checked(name, digest) for name, digest in input_rows.items()]
            evidence = row.get("receipt", row.get("upstream_receipt"))
            if evidence:
                checked(evidence, row.get("receipt_sha256", row.get("upstream_receipt_sha256")))
            aliases = row.get("aliases", {})
            options = [f"--defsym={name}={provider}" for name, provider in aliases.items()]
            new = OUT / f"{sequence:03d}-{phase}-{row['stage']}.o"
            subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                            *(str(path) for path in inputs), *options,
                            "-o", str(new)], check=True)
            old_u, new_u = names(old, "-u"), names(new, "-u")
            old_d, new_d = names(old, "-g", "--defined-only"), \
                           names(new, "-g", "--defined-only")
            if old_u - new_u != REMOVED or new_u - old_u or \
                    new_d - old_d != PROVIDERS or old_d - new_d:
                raise RuntimeError("font correction changed at " + phase + "/" +
                                   row["stage"] + f": -u {old_u-new_u}, +u {new_u-old_u}, " +
                                   f"+d {new_d-old_d}, -d {old_d-new_d}")
            stages.append({"stage": row["stage"],
                           "prior_object": row["new_object"],
                           "prior_sha256": sha(old), "inputs": input_rows,
                           "aliases": aliases,
                           "new_object": str(new.relative_to(ROOT)),
                           "new_sha256": sha(new),
                           "unresolved_before": len(old_u),
                           "unresolved_after": len(new_u)})
            current = new
        phase_rows.append({"phase": phase, "prior_receipt": str(prior_path.relative_to(ROOT)),
                           "prior_receipt_sha256": sha(prior_path),
                           "stages": stages,
                           "linked_object": str(current.relative_to(ROOT)),
                           "linked_sha256": sha(current)})
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_LATER_REPLAY_C",
               "root_receipt": str(ROOT_RECEIPT.relative_to(ROOT)),
               "root_receipt_sha256": sha(ROOT_RECEIPT),
               "phases": phase_rows,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_object_sha256": sha(current),
               "stages_replayed": sequence,
               "unresolved_after": phase_rows[-1]["stages"][-1]["unresolved_after"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Receipt-linked library through tail stages carry both corrections; subsequent Main feature/data bindings still require replay.",
                          "Matching import/provider deltas do not establish final RAM placement, startup copy, or hardware effects."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sequence, receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
