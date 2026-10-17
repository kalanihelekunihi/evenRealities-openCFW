#!/usr/bin/env python3
"""Pin source-linked Conversate expand scheduler and update callbacks."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-expand-animation-5b7704"
PRIOR = BASE / "main-lv-async-post-484014/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_expand_animation_5b7704.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_expand_animation_5b7704_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_expand_animation_5b7704"}
    if (len(before), len(after)) != (138, 137) or before-after != removed or after-before:
        raise RuntimeError("Conversate expand animation frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_EXPAND_ANIMATION_5B7704_C" or
            oracle["cases"] != 336 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate expand animation oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_expand_animation_5b7704",
                   "audio_conversate_expand_width_5b7684",
                   "audio_conversate_expand_height_5b76a4",
                   "audio_conversate_expand_x_5b76c4",
                   "audio_conversate_expand_y_5b76e4"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate expand body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_EXPAND_ANIMATION_5B7704_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": oracle["native_bodies"], "oracle_cases": 336,
              "unresolved_before": 138, "unresolved_after": 137,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Remaining Main imports and source-owned image configuration are open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
