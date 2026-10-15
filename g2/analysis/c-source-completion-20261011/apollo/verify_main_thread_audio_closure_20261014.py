#!/usr/bin/env python3
"""Compose the previously verified audio/thread C graph into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261014/main-vendor-power-aliases/apollo-main-vendor-power-bound.o"
PRIOR = G2 / "build/c-firmware/20261014/main-root-dependencies/thread-audio-lowers-current-receipt.json"
OUT = G2 / "build/c-firmware/20261014/main-thread-audio-closure"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def main():
    evidence = json.loads(PRIOR.read_text())
    if evidence["status"] != "PASS_CURRENT_MAIN_THREAD_AUDIO_LOWERS_COMPILE":
        raise RuntimeError("thread/audio source receipt changed")
    if evidence["source_unit_count"] != 19 or len(evidence["source_units"]) != 19:
        raise RuntimeError("thread/audio unit inventory changed")
    paths = []
    defined = names(BASE, "-g", "--defined-only")
    for row in evidence["source_units"]:
        src, obj = ROOT / row["source"], ROOT / row["object"]
        if sha(src) != row["source_sha256"] or sha(obj) != row["object_sha256"]:
            raise RuntimeError(f"source/object drift: {src}")
        symbols = names(obj, "-g", "--defined-only")
        if symbols & defined:
            raise RuntimeError(f"duplicate global definition: {symbols & defined}")
        defined |= symbols
        paths.append(obj)
    for check in evidence["bounded_oracles_rerun"]:
        if sha(ROOT / check["path"]) != check["sha256"]:
            raise RuntimeError(f"oracle drift: {check['path']}")
    before = names(BASE, "-u")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "apollo-main-thread-audio.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *(str(path) for path in paths),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    resolved = before - after
    if len(before) != 495 or len(after) != 485 or len(resolved) != 10 or after - before:
        raise RuntimeError("unexpected Main import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_THREAD_AUDIO_C_CLOSURE",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "prior_receipt": str(PRIOR.relative_to(ROOT)), "prior_receipt_sha256": sha(PRIOR),
        "source_units": evidence["source_units"],
        "bounded_oracles_recorded": evidence["bounded_oracles_rerun"],
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(resolved), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Prior bounded oracle results were hash checked, not rerun in this closure.",
                   "Scheduling and UART hardware behavior remain unqualified.",
                   "Main image placement and hardware boot remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
