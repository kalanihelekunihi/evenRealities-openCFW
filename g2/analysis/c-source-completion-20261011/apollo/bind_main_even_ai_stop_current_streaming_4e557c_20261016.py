#!/usr/bin/env python3
"""Bind stock-compared EvenAI stop dispatcher and bounded display RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_stop_current_streaming_4e557c.c"
RAM_SOURCE = COMP / "even_ai_stream_display_state_ram.c"
LINKER = COMP / "even_ai_stream_display_state_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-file-redirect-init/apollo-main-file-redirect-init-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-stop-streaming"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_even_ai_stop_current_streaming_4e557c"
RAM = "audio_even_ai_stream_display_state_20073a1c"
CHILDREN = {"audio_text_stream_stop_552d10", "audio_text_stream_pause_552d40"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_STOP_STREAMING_C_ORACLE" or \
            oracle["cases"] != 40 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["ram_source_sha256"] != sha(RAM_SOURCE) or \
            oracle["linker_sha256"] != sha(LINKER):
        raise RuntimeError("EvenAI stop-stream oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    body = OUT / "even_ai_stop_current_streaming_4e557c.o"
    ram = OUT / "even_ai_stream_display_state_ram.o"
    cmd = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
           "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
           "-Wextra", "-Werror", "-c"]
    subprocess.run(cmd + [str(SOURCE), "-o", str(body)], check=True)
    subprocess.run(cmd + [str(RAM_SOURCE), "-o", str(ram)], check=True)
    if names(body, "--defined-only") != {PROVIDER} or \
            names(ram, "--defined-only") != {RAM}:
        raise RuntimeError("EvenAI stop-stream source symbols changed")
    before = names(BASE, "-u")
    if len(before) != 176 or PROVIDER not in before or CHILDREN & before:
        raise RuntimeError("Apollo stop-stream base frontier changed")
    linked = OUT / "apollo-main-even-ai-stop-streaming-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(body), str(ram),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before != CHILDREN or len(after) != 177:
        raise RuntimeError(f"Apollo stop-stream frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_STOP_STREAMING_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "ram_source": str(RAM_SOURCE.relative_to(ROOT)), "ram_source_sha256": sha(RAM_SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(body.relative_to(ROOT)), "object_sha256": sha(body),
               "ram_object": str(ram.relative_to(ROOT)), "ram_object_sha256": sha(ram),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 176, "unresolved_after": 177,
               "imports_resolved": [PROVIDER], "imports_added": sorted(CHILDREN),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Two stop/pause descendants are explicit imports.",
                          "The 0x20 RAM extent covers the observed clear; full lifetime remains open.",
                          "Final global placement and hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 176, 177, sha(path))

if __name__ == "__main__":
    main()
