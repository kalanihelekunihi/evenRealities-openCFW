#!/usr/bin/env python3
"""Bind the previously stock-compared current-session index at its FSM name."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e576c/apollo-main-terminal-ui-action-5e576c-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-display-fallback-adapter-5ecafa"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_display_fallback_adapter_5ecafa.c"
PROVIDER = G2 / "components/audio/uart_thread_source_candidate/td_current_session_index.c"
PROVIDER_RECEIPT = G2 / "build/c-firmware/td-current-index-round932/receipt.json"
RESOLVED = {"audio_terminal_display_fallback_5ecafa"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    if provider["status"] != "PASS_NATIVE_TD_CURRENT_SESSION_INDEX" or \
            provider["cases"] != 50 or provider["source_sha256"] != sha(PROVIDER):
        raise RuntimeError("Native current-session index evidence changed")
    before = imports(BASE)
    if len(before) != 211 or not RESOLVED <= before:
        raise RuntimeError("Terminal fallback adapter frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_display_fallback_adapter_5ecafa.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-display-fallback-adapter-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 210:
        raise RuntimeError(f"Terminal fallback adapter frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_DISPLAY_FALLBACK_ADAPTER_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "provider": str(PROVIDER.relative_to(ROOT)), "provider_sha256": sha(PROVIDER),
              "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
              "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 211, "unresolved_after": 210,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Existing 50-case stock oracle covers provider; final placement and upstream effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))

if __name__ == "__main__":
    main()
