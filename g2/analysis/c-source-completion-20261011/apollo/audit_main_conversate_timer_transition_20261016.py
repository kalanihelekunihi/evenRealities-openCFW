#!/usr/bin/env python3
"""Pin Conversate timer transition chain and its source-owned six-rule table."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-transition"
PRIOR = BASE / "main-conversate-ui-action-5b1724/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_transition_20261016.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_transition_20261016.py"
RULES = bytes((7,1,1,1, 1,8,1,2, 2,8,2,2, 8,2,2,1, 2,4,3,1, 4,2,3,2))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_transition_5b3d86"}
    if (len(before), len(after)) != (121, 120) or before-after != removed or after-before:
        raise RuntimeError("Conversate timer transition frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_TRANSITION_C" or
            oracle["cases"] != 1215 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer transition oracle changed")
    with CANDIDATE.open("rb") as stream:
        section = ELFFile(stream).get_section_by_name(".g2_conversate_timer_rules_775e6c")
        if section is None or section.data() != RULES:
            raise RuntimeError("Conversate timer rule data changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_timer_condition_5b3648",
                   "audio_conversate_timer_rule_match_5b3680",
                   "audio_conversate_timer_change_5b3718",
                   "audio_conversate_ui_transition_5b3d86"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError(f"Conversate timer body missing: {symbol}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_TRANSITION_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": oracle["native_bodies"],
              "stock_rule_table": oracle["stock_rule_table"],
              "rule_table_sha256": hashlib.sha256(RULES).hexdigest(),
              "oracle_cases": 1215, "unresolved_before": 121,
              "unresolved_after": 120,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "UI action route matrix and 50 native handler targets remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
