#!/usr/bin/env python3
"""Join libc memmove to the native-checked selected C move provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-runtime-aliases-current-receipt.json"
EVIDENCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-memmove-round93/receipt.json"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-memmove-round93/move_candidate.c"
FORWARD = G2 / "components/audio/queue_cmsis_offline/cmsis.c"
BOUND = OUT / "apollo-main-pool-state-memmove-bound.o"
RECEIPT = OUT / "pool-state-memmove-current-receipt.json"
ALIAS = "memmove"
TARGET = "audio_uart_lv_grid_move_45475a"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_RUNTIME_ABI_JOINS"
    assert evidence["status"] == "PASS_INDEPENDENT_QEMU_THUMB_NATIVE_MEMMOVE"
    assert evidence["cases"] == 3888
    assert evidence["source_sha256"] == sha(SOURCE)
    assert evidence["canonical_forward_source_sha256"] == sha(FORWARD)
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(["-u"], prior)
    definitions = symbols(["--defined-only"], prior)
    assert ALIAS in before and TARGET in definitions and ALIAS not in definitions
    subprocess.run(["arm-none-eabi-ld", "-r", f"--defsym={ALIAS}={TARGET}",
                    str(prior), "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - {ALIAS}
    receipt = {"status": "PASS_POOLED_MAIN_BOUNDED_NATIVE_MEMMOVE_C_JOIN",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "native_evidence": str(EVIDENCE.relative_to(ROOT)), "native_evidence_sha256": sha(EVIDENCE),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "alias": ALIAS, "target": TARGET, "native_cases": 3888,
               "imports_resolved": [ALIAS], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["The 3,888 stock/C cases cover bounded buffer shapes on QEMU Cortex-A9 Thumb, not every CPU state or full caller domain.",
                         "Final address placement and G2 hardware operation remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
