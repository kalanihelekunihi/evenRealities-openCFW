#!/usr/bin/env python3
"""Bind the two stock-compared EvenAI ready accessors to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_ready_accessors_4e550a_552ce8.c"
LINKER = COMP / "even_ai_ready_accessors.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-ready-bound/apollo-main-even-ai-ready-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ready-accessors"
ORACLE = OUT / "oracle-receipt.json"
PROVIDERS = {"audio_even_ai_stream_interval_get_4e550a",
             "audio_text_stream_pending_text_552ce8"}
EMPTY = "audio_text_stream_empty_552cf4"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_READY_ACCESSORS_C_ORACLE" or \
            oracle["cases"] != 7 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["linker_sha256"] != sha(LINKER):
        raise RuntimeError("EvenAI ready accessor oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_ready_accessors_4e550a_552ce8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != PROVIDERS | {EMPTY}:
        raise RuntimeError("EvenAI ready accessor C symbols changed")
    before = names(BASE, "-u")
    if len(before) != 183 or not PROVIDERS <= before or EMPTY in before:
        raise RuntimeError("Apollo accessor base frontier changed")
    linked = OUT / "apollo-main-even-ai-ready-accessors-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != PROVIDERS or after - before or len(after) != 181:
        raise RuntimeError("Apollo accessor linked frontier changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_ACCESSORS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(PROVIDERS), "imports_added": [],
        "empty_string_stock_address": "0x552cf4",
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Seven stock comparisons include the exact null-handle empty-string pointer.",
                   "Final global placement, startup, and text-stream object lifetimes remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
