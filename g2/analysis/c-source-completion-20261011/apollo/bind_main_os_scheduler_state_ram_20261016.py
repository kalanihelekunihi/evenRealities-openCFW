#!/usr/bin/env python3
"""Bind the two xTaskGetSchedulerState RAM words in the Apollo candidate."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "os_scheduler_state_ram.c"
LINKER = COMP / "os_scheduler_state_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-ram-state-bound/apollo-main-even-ai-ram-state-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-os-scheduler-state-ram-bound"
SPANS = {
    "audio_os_scheduler_running_20074a3c": (0x456064, 0x20074a3c, "running"),
    "audio_os_scheduler_suspended_20074a58": (0x456068, 0x20074a58, "suspended"),
}
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def inspect(path):
    with path.open("rb") as f:
        elf = ELFFile(f)
        return {s.name: (s["sh_addr"], s["sh_size"], s["sh_type"])
                for s in elf.iter_sections()}

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PINNED:
        raise RuntimeError("Apollo main payload changed")
    for name, (literal, address, _) in SPANS.items():
        if int.from_bytes(image[literal-0x438000:literal-0x438000+4], "little") != address:
            raise RuntimeError(f"Scheduler pointer changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "os_scheduler_state_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != set(SPANS) or names(obj, "-u"):
        raise RuntimeError("Scheduler RAM source symbols changed")
    for _, (_, _, short) in SPANS.items():
        if inspect(obj)[f".bss.opencfw.os.scheduler.{short}"][1:] != (4, "SHT_NOBITS"):
            raise RuntimeError("Scheduler cell extent changed")
    placed = OUT / "os-scheduler-state-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER),
                    "-e", "audio_os_scheduler_running_20074a3c", str(obj),
                    "-o", str(placed)], check=True)
    placed_symbols = {line.split()[-1]: int(line.split()[0], 16)
                      for line in subprocess.check_output(
                          ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                          text=True).splitlines()}
    placed_sections = inspect(placed)
    for name, (_, address, short) in SPANS.items():
        if placed_sections[f".opencfw.os.scheduler.{short}"] != (address, 4, "SHT_NOBITS") or \
                placed_symbols.get(name) != address:
            raise RuntimeError(f"Scheduler placement changed: {name}")
    before = names(BASE, "-u")
    if len(before) != 184 or not set(SPANS) <= before:
        raise RuntimeError("Apollo base import frontier changed")
    linked = OUT / "apollo-main-os-scheduler-state-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != set(SPANS) or after - before or len(after) != 182:
        raise RuntimeError("Apollo scheduler RAM frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for section in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", section.name)
            if match and section["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + section["sh_size"], section.name))
    even_ai = json.loads((G2 / "build/c-firmware/20261016/main-even-ai-ram-state-bound/receipt.json").read_text())
    if even_ai["linked_sha256"] != sha(BASE):
        raise RuntimeError("EvenAI RAM base receipt changed")
    for name, (_, address, _) in SPANS.items():
        collisions = [other for start, end, other in fixed
                      if address < end and start < address + 4]
        collisions += [span["symbol"] for span in even_ai["spans"]
                       if address < int(span["address"], 16) + span["bytes"] and
                       int(span["address"], 16) < address + 4]
        if collisions:
            raise RuntimeError(f"Scheduler RAM collision: {name} {collisions}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_OS_SCHEDULER_STATE_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED,
        "spans": [{"symbol": name, "pointer_literal": hex(literal),
                   "address": hex(address), "bytes": 4, "section_type": "NOBITS"}
                  for name, (literal, address, _) in SPANS.items()],
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "fixed_ram_sections_checked": len(fixed),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Only the observed four-byte scheduler cells are reserved.",
                   "Final linker placement, startup state, and device behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
