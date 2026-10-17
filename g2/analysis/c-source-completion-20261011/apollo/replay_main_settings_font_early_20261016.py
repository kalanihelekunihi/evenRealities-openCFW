#!/usr/bin/env python3
"""Replay the first five Main stages with both corrected archive members."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMBINED = G2 / "build/c-firmware/20261016/main-settings-font-archive-refresh/receipt.json"
PRIOR = G2 / "build/c-firmware/20261014/main-corrected-archive-early-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-settings-font-early-replay"
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def main():
    combined, prior = json.loads(COMBINED.read_text()), json.loads(PRIOR.read_text())
    if combined["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_ARCHIVE_REFRESH_C" or \
            prior["status"] != "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_EARLY_REPLAY_C":
        raise RuntimeError("early replay input status changed")
    current = ROOT / combined["linked_object"]
    if sha(current) != combined["linked_object_sha256"]:
        raise RuntimeError("combined root object changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stages = []
    for index, row in enumerate(prior["stages"], 1):
        old = ROOT / row["new_object"]
        if sha(old) != row["new_sha256"]:
            raise RuntimeError("prior early stage changed")
        inputs = []
        for name, digest in row["inputs"].items():
            path = ROOT / name
            if sha(path) != digest:
                raise RuntimeError("early provider object changed: " + name)
            inputs.append(path)
        new = OUT / f"{index:02d}-{row['stage']}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", *row["link_options"],
                        str(current), *(str(path) for path in inputs), "-o", str(new)],
                       check=True)
        old_u, new_u = names(old, "-u"), names(new, "-u")
        old_d, new_d = names(old, "-g", "--defined-only"), \
                       names(new, "-g", "--defined-only")
        if old_u - new_u != REMOVED or new_u - old_u or \
                new_d - old_d != PROVIDERS or old_d - new_d:
            raise RuntimeError("font correction not preserved at " + row["stage"])
        stages.append({"stage": row["stage"], "prior_object": row["new_object"],
                       "prior_sha256": sha(old), "inputs": row["inputs"],
                       "link_options": row["link_options"],
                       "new_object": str(new.relative_to(ROOT)),
                       "new_sha256": sha(new),
                       "unresolved_before": len(old_u),
                       "unresolved_after": len(new_u)})
        current = new
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_EARLY_REPLAY_C",
               "combined_receipt": str(COMBINED.relative_to(ROOT)),
               "combined_receipt_sha256": sha(COMBINED),
               "prior_receipt": str(PRIOR.relative_to(ROOT)),
               "prior_receipt_sha256": sha(PRIOR),
               "stages": stages,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_object_sha256": sha(current),
               "unresolved_after": stages[-1]["unresolved_after"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Only the five early Main stages are replayed; later root, runtime and feature waves remain pending."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(stages), receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
