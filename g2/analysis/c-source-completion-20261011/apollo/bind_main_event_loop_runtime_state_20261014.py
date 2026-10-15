#!/usr/bin/env python3
"""Bind event-loop runtime objects with source-size and native-literal gates."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/event_loop_runtime_state.c"
INIT = G2 / "components/audio/uart_thread_source_candidate/display_event_loop_init_task.c"
DELAY = G2 / "components/audio/uart_thread_source_candidate/display_event_loop_delayed.c"
TIMER = G2 / "components/audio/uart_thread_source_candidate/display_event_loop_timer_callback.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-hci-scheduler-ring-state/apollo-main-hci-scheduler-ring-state.o"
OUT = G2 / "build/c-firmware/20261014/main-event-loop-runtime-state"
CONTRACTS = {
    "audio_event_loop_delayed_slots": (0x2006dad4, 0x476c6c, 192 * 4),
    "audio_event_loop_elapsed": (0x20074600, 0x476c5c, 4),
    "audio_event_loop_mutex": (0x200745f4, 0x476c1c, 4),
    "audio_event_loop_mutex_cb": (0x20072b78, 0x785fe8, 80),
    "audio_event_loop_queue": (0x200745ec, 0x476bf0, 4),
    "audio_event_loop_queue_cb": (0x20072b28, 0x777704, 80),
    "audio_event_loop_queue_storage": (0x20071d40, 0x77770c, 120),
    "audio_event_loop_thread_cb": (0x20071f80, 0x754a24, 112),
    "audio_event_loop_thread_handle": (0x200745f0, 0x476c2c, 4),
    "audio_event_loop_thread_stack": (0x20372bc0, 0x754a2c, 3072),
    "audio_event_loop_timer": (0x200745f8, 0x476c0c, 4),
    "audio_event_loop_timer_cb": (0x20073624, 0x785ff8, 44),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source, init, delay, timer = (p.read_text() for p in (SOURCE, INIT, DELAY, TIMER))
    for name, (ram, literal, size) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native event-loop RAM literal changed: {name}")
        if name not in source or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"event-loop C source name/section changed: {name}")
        if not any(f"extern " in text and name in text for text in (init, delay, timer)):
            raise RuntimeError(f"event-loop selected source no longer uses {name}")
    if "audio_event_loop_delayed_slots[192]" not in delay or \
       "audio_event_loop_thread_stack[3072]" not in init or \
       "audio_event_loop_queue_storage[120]" not in init or \
       "audio_event_loop_timer_cb[44]" not in init:
        raise RuntimeError("event-loop source extent contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "event_loop_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("event-loop C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"event-loop C storage sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main event-loop imports changed")
    linked = OUT / "apollo-main-event-loop-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_EVENT_LOOP_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "source_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (INIT, DELAY, TIMER)},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Selected initializer sizes and native literals are covered; CMSIS implementation and lifetime remain external.",
                          "Named sections express intended native addresses but final placement is unverified.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
