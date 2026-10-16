#!/usr/bin/env python3
"""Bind the stock-compared EvenAI common timer/start-all provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_4e2e62.c"
LINKER = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-ready-accessors/apollo-main-even-ai-ready-accessors-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-common-timer"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_even_ai_timer_start_all_4e31a0"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_COMMON_TIMER_START_C_ORACLE" or \
            oracle["cases"] != 36 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["linker_sha256"] != sha(LINKER):
        raise RuntimeError("EvenAI timer start oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_common_timer_start_4e2e62.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-DOPENCFW_TIMER_START_ONLY",
                    "-c", str(SOURCE), "-o", str(obj)], check=True)
    expected = {PROVIDER, "audio_even_ai_common_timer_start_4e2e62",
                "audio_even_ai_common_timer_state_20074008"}
    if names(obj, "--defined-only") != expected:
        raise RuntimeError("EvenAI timer source symbols changed")
    before = names(BASE, "-u")
    if len(before) != 181 or PROVIDER not in before:
        raise RuntimeError("Apollo timer base frontier changed")
    linked = OUT / "apollo-main-even-ai-common-timer-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before or len(after) != 180:
        raise RuntimeError(f"Apollo timer linked frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_COMMON_TIMER_START_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 181, "unresolved_after": 180,
               "imports_resolved": [PROVIDER], "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Common timer stop logging is not bound yet.",
                          "Final global RAM placement, startup, and hardware validation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 181, 180, sha(path))

if __name__ == "__main__":
    main()
