#!/usr/bin/env python3
"""Bind native-checked WSF message bodies to foundation imports."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-timing-state-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_core_handler.c"
VERIFIER = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/verify_ble_hci_helpers.py"
OUTPUT = OUT / "apollo-main-pool-state-wsf-message-bound.o"
RECEIPT = OUT / "pool-state-wsf-message-current-receipt.json"
ALIASES = {
    "opencfw_wsf_msg_deq": "audio_ble_wsf_message_dequeue",
    "opencfw_wsf_msg_free": "audio_ble_wsf_message_free",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 433
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    defined = names(prior, "--defined-only")
    assert set(ALIASES) <= before and set(ALIASES.values()) <= defined
    comparison = subprocess.run(["/tmp/opencfw-oracle-venv/bin/python", str(VERIFIER)],
                                check=True, capture_output=True, text=True)
    assert "PASS deq" in comparison.stdout and "PASS free" in comparison.stdout
    command = ["arm-none-eabi-ld", "-r"]
    command.extend(f"--defsym={new}={existing}" for new, existing in ALIASES.items())
    subprocess.run(command + [str(prior), "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == set(ALIASES) and after - before == set()
    assert len(before) == 433 and len(after) == 431
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_WSF_MESSAGE_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "bounded_native_verifier": str(VERIFIER.relative_to(ROOT)),
        "bounded_native_verifier_sha256": sha(VERIFIER),
        "bounded_native_output": comparison.stdout.splitlines(),
        "aliases": ALIASES, "imports_resolved": sorted(ALIASES), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The bounded native comparison covers wrapper return/call behavior; full queue concurrency, allocator effects, final placement and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
