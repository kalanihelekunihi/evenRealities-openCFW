#!/usr/bin/env python3
"""Integrate the bounded EvenAI local decode C provider into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_local_decode_498092.c"
BASE = G2 / "build/c-firmware/20261016/main-tpl-service-row0-ram-bound/apollo-main-tpl-service-row0-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-local-decode"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_even_ai_local_decode_498092"
ADDED = {"audio_even_ai_encode_ctrl_4e3788", "audio_even_ai_encode_vad_4e3b80"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_LOCAL_DECODE_C_ORACLE" or \
            oracle["source_sha256"] != sha(SOURCE) or oracle["cases"] != 32:
        raise RuntimeError("EvenAI local decode oracle or source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_local_decode_498092.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER} or not ADDED <= names(obj, "-u"):
        raise RuntimeError("EvenAI local decode object symbols changed")
    before = names(BASE, "-u")
    if len(before) != 173 or PROVIDER not in before or ADDED & before:
        raise RuntimeError("Apollo local decode base frontier changed")
    linked = OUT / "apollo-main-even-ai-local-decode-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before != ADDED or len(after) != 174:
        raise RuntimeError("Apollo local decode linked frontier changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_LOCAL_DECODE_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [PROVIDER], "imports_added": sorted(ADDED),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Thirty-two controlled stock comparisons cover return, state, config, notification arguments, and enabled log metadata and first values.",
                   "Logger side effects, later variadic values, and final layout remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
