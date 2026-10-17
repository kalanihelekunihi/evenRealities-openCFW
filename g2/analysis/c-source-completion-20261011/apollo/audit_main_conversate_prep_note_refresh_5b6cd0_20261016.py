#!/usr/bin/env python3
"""Pin the stock-compared note-content and prep-note refresh C bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-refresh-5b6cd0"
READY = BASE / "main-conversate-note-content-ready-5b74ba"
PRIOR = BASE / "main-conversate-prep-scroll-route-5b6f8e/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCES = [G2 / "components/audio/uart_thread_source_candidate/conversate_note_content_ready_5b74ba.c",
           G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_refresh_5b6cd0.c"]
VERIFIERS = [G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_note_content_ready_5b74ba_20261016.py",
             G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_prep_note_refresh_5b6cd0_20261016.py"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b74ba"}
    added = {"audio_conversate_prep_note_pool_bind_5b6ac0",
             "audio_conversate_prep_note_pool_show_5b6b58"}
    if (len(before), len(after)) != (136, 137) or before - after != removed or after - before != added:
        raise RuntimeError("Conversate prep note refresh frontier changed")
    receipts = [json.loads((READY / "oracle-receipt.json").read_text()),
                json.loads((HERE / "oracle-receipt.json").read_text())]
    expected = [("PASS_DIRECT_MAIN_CONVERSATE_NOTE_CONTENT_READY_5B74BA_C", 60),
                ("PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_REFRESH_5B6CD0_C", 480)]
    for index, ((status, cases), receipt) in enumerate(zip(expected, receipts)):
        if (receipt["status"] != status or receipt["cases"] != cases or
                receipt["source_sha256"] != sha(SOURCES[index]) or
                receipt["oracle_elf_sha256"] != sha(ROOT / receipt["oracle_elf"]) or
                receipt["source_complete"] or receipt["flashable"] or receipt["hardware_proof"]):
            raise RuntimeError("Conversate prep note oracle changed: " + status)
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_ui_route_5b74ba",
                   "audio_conversate_prep_note_refresh_5b6cd0",
                   "audio_conversate_prep_note_style_5b69d4"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate prep note body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_REFRESH_5B6CD0_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "sources": [ref(path) for path in SOURCES],
              "verifiers": [ref(path) for path in VERIFIERS],
              "oracle_receipts": [ref(READY / "oracle-receipt.json"), ref(HERE / "oracle-receipt.json")],
              "native_bodies": [receipts[0]["native_body"]] + receipts[1]["native_bodies"],
              "oracle_cases": 540, "unresolved_before": 136, "unresolved_after": 137,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Prep-note pool bind/show, remaining Main imports and image configuration are open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
