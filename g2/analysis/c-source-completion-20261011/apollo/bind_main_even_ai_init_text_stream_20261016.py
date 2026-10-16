#!/usr/bin/env python3
"""Bind stock-compared EvenAI text-stream initialization into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_init_text_stream_4e551e.c"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-common-timer-stop/apollo-main-even-ai-common-timer-stop-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-init-text-stream"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_even_ai_init_text_stream_4e551e"
CHILD = "audio_text_stream_create_552b30"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_INIT_TEXT_STREAM_C_ORACLE" or \
            oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("EvenAI text initializer oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_init_text_stream_4e551e.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER}:
        raise RuntimeError("EvenAI text initializer symbols changed")
    before = names(BASE, "-u")
    if len(before) != 179 or PROVIDER not in before or CHILD in before:
        raise RuntimeError("Apollo text initializer base frontier changed")
    linked = OUT / "apollo-main-even-ai-init-text-stream-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before != {CHILD} or len(after) != 179:
        raise RuntimeError(f"Apollo text initializer frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_INIT_TEXT_STREAM_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 179, "unresolved_after": 179,
               "imports_resolved": [PROVIDER], "imports_added": [CHILD],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Text-stream allocator 0x552b30 is the explicit next provider.",
                          "Logger side effects, whole-image link, and hardware validation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 179, 179, sha(path))

if __name__ == "__main__":
    main()
