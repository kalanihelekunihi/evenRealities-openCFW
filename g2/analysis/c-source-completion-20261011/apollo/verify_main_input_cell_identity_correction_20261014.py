#!/usr/bin/env python3
"""Verify source correction for distinct input queues and direct ring/ROM data."""
import json
import struct
import subprocess
import sys
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SYNC = G2 / "components/audio/uart_thread_source_candidate/display_input_event_send.c"
INPUT = G2 / "components/audio/uart_thread_source_candidate/input_event.c"
DISPLAY = G2 / "components/audio/uart_thread_source_candidate/display_thread.c"
TEST = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ring_input_event_native.py"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-device-timer-runtime-state/apollo-main-device-timer-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-input-cell-identity-correction"
LITERALS = {0x4448a0: 0x200744e8, 0x4448a4: 0x200744e4,
            0x4448b0: 0x20073b60, 0x4448b4: 0x7536fc,
            0x45d068: 0x200749cc, 0x45d0c8: 0x20074b10}


def bytes_at(segments, address, count=4):
    for base, data in segments:
        if base <= address and address + count <= base + len(data):
            return data[address-base:address-base+count]
    raise RuntimeError(f"unmapped native address {address:#x}")


def compile_source(path, output):
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(path), "-o", str(output)], check=True)


def main():
    segments, _ = image(NATIVE)
    for literal, expected in LITERALS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != expected:
            raise RuntimeError(f"native input literal changed: {literal:#x}")
    if not bytes_at(segments, 0x7536fc, 33).startswith(b"input: message queue send failed\0"):
        raise RuntimeError("native input failure ROM string changed")
    sync, inp, display = SYNC.read_text(), INPUT.read_text(), DISPLAY.read_text()
    if "extern void *audio_uart_sync_schedule_queue;" not in sync or \
       "audio_uart_input_queue" in sync or \
       "extern uint32_t g2_display_ring[5];" not in inp or \
       "extern const char audio_uart_input_queue_failure_context[];" not in inp or \
       "audio_uart_input_ring_write(g2_display_ring,bytes,10u)" not in inp or \
       "extern uint32_t g2_display_ring[5];" not in display or \
       "audio_uart_display_ring_read(g2_display_ring," not in display:
        raise RuntimeError("corrected input C source contracts changed")
    OUT.mkdir(parents=True, exist_ok=True)
    objects = {}
    for key, path in (("sync", SYNC), ("input", INPUT), ("display", DISPLAY)):
        obj = OUT / f"{key}_corrected.o"
        compile_source(path, obj)
        objects[key] = obj
    sync_u, input_u, display_u = (names(objects[key], "-u") for key in ("sync", "input", "display"))
    if "audio_uart_sync_schedule_queue" not in sync_u or "audio_uart_input_queue" in sync_u or \
       "g2_display_ring" not in input_u or "audio_uart_input_ring" in input_u or \
       "audio_uart_input_queue_failure_context" not in input_u or \
       "g2_display_ring" not in display_u or "audio_uart_display_ring" in display_u:
        raise RuntimeError("corrected compiled import identities changed")
    subprocess.run([sys.executable, str(TEST)], check=True)
    unresolved = names(BASE, "-u")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_INPUT_CELL_IDENTITY_CORRECTION_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_literals": {hex(k): hex(v) for k, v in LITERALS.items()},
               "native_rom_failure_text": "input: message queue send failed",
               "sources": {str(p.relative_to(ROOT)): sha(p) for p in (SYNC, INPUT, DISPLAY)},
               "native_test": str(TEST.relative_to(ROOT)), "native_test_sha256": sha(TEST),
               "native_test_cases": 5,
               "objects": {key: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                           for key, path in objects.items()},
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "unresolved_current_root": len(unresolved),
               "source_complete": False, "full_payload_linked": False,
               "root_rebuild_required": True,
               "limits": ["The existing merged Apollo object predates these source corrections; its old imports and behavior are not relinked here.",
                          "The direct ring object and ROM string require source-owned definitions or verified resident binding.",
                          "Whole-image, final placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(unresolved), sha(path))


if __name__ == "__main__":
    main()
