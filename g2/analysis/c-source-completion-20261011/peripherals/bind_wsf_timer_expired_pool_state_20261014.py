#!/usr/bin/env python3
"""Bind the bounded native-checked WSF timer expiry C body."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-wsf-context-current-receipt.json"
EVIDENCE = OUT / "wsf-timer-expired-native-comparison.json"
SOURCE = ROOT / "g2/components/foundation/wsf_radio/timer_expired.c"
OBJECT = OUT / "wsf-timer-expired-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-wsf-timer-expired-bound.o"
RECEIPT = OUT / "pool-state-wsf-timer-expired-current-receipt.json"
NAME = "opencfw_wsf_timer_expired"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    assert base["unresolved_after"] == 430
    assert evidence["status"] == "PASS_BOUNDED_NATIVE_WSF_TIMER_EXPIRED_C"
    assert evidence["cases"] == 6 and evidence["stock_entry"] == "0x52a542"
    assert sha(SOURCE) == evidence["source_sha256"]
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert NAME in before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == {NAME}
    assert names(OBJECT, "-u") <= names(prior, "--defined-only")
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == {NAME} and after - before == set()
    assert len(before) == 430 and len(after) == 429
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_WSF_TIMER_EXPIRED_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "native_comparison": str(EVIDENCE.relative_to(ROOT)),
        "native_comparison_sha256": sha(EVIDENCE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "imports_resolved": [NAME], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The six native/C cases compare empty, pending and due queue heads with task-lock and queue-remove children held as explicit boundaries; concurrent timer behavior, final placement and hardware remain unproved."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
