#!/usr/bin/env python3
"""Pin source-linked exit-prompt step-two callback and child frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-exit-prompt-fade-step-58bebc"
PRIOR = BASE / "main-conversate-exit-prompt-show-58bf12/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_exit_prompt_fade_step_58bebc.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_exit_prompt_fade_step_58bebc_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_exit_prompt_fade_step_58bebc"}
    added = {"audio_conversate_exit_prompt_fade_schedule_58c516",
             "audio_conversate_exit_prompt_fade_step3_58be1a"}
    if (len(before), len(after)) != (140, 141) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate step-two frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_EXIT_PROMPT_FADE_STEP_58BEBC_C" or
            oracle["cases"] != 40 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate step-two oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_exit_prompt_fade_step_58bebc\n" not in defined:
        raise RuntimeError("Conversate step-two body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_EXIT_PROMPT_FADE_STEP_58BEBC_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 40,
              "unresolved_before": 140, "unresolved_after": 141,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Fade scheduler 0x58c516 and step-three callback 0x58be1a remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
