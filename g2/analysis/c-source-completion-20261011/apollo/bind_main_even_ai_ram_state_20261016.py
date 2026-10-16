#!/usr/bin/env python3
"""Reserve seven observed EvenAI RAM spans and bind their C storage symbols."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_ram_state.c"
LINKER = COMP / "even_ai_ram_state.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-frame-chain-bound/apollo-main-even-ai-frame-chain-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ram-state-bound"
SPANS = {
    "audio_even_ai_service_state_2006ed10": (0x4985a8, 0x2006ed10, 0x218, "service"),
    "audio_even_ai_heartbeat_state_20074014": (0x4e316c, 0x20074014, 10, "heartbeat"),
    "audio_even_ai_mutex_20074580": (0x4e2a40, 0x20074580, 4, "mutex"),
    "audio_even_ai_config_state_20074974": (0x4985cc, 0x20074974, 3, "config"),
    "audio_even_ai_last_frame": (0x4e3d1c, 0x20074f36, 2, "last"),
    "audio_even_ai_proto_message_200f5884": (0x4e5458, 0x200f5884, 0x20c, "proto"),
    "audio_even_ai_tx_buffer_2037c4a0": (0x4e5454, 0x2037c4a0, 0x100, "tx"),
}
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def sections(path):
    with path.open("rb") as f:
        elf = ELFFile(f)
        return {s.name: (s["sh_addr"], s["sh_size"], s["sh_type"])
                for s in elf.iter_sections()}

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    ranges = []
    for name, (literal, address, extent, section) in SPANS.items():
        actual = int.from_bytes(image[literal-0x438000:literal-0x438000+4], "little")
        if actual != address:
            raise RuntimeError(f"RAM pointer changed: {name}")
        ranges.append((address, address + extent, name))
    for left, right in zip(sorted(ranges), sorted(ranges)[1:]):
        if left[1] > right[0]:
            raise RuntimeError(f"EvenAI RAM spans overlap: {left[2]} {right[2]}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_ram_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != set(SPANS) or names(obj, "-u"):
        raise RuntimeError("EvenAI RAM source symbols changed")
    raw_sections = sections(obj)
    for name, (_, _, extent, short) in SPANS.items():
        section = raw_sections[f".bss.opencfw.evenai.{short}"]
        if section[1:] != (extent, "SHT_NOBITS"):
            raise RuntimeError(f"Unplaced extent changed: {name}")
    placed = OUT / "even-ai-ram-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER),
                    "-e", "audio_even_ai_service_state_2006ed10",
                    str(obj), "-o", str(placed)],
                   check=True)
    placed_sections = sections(placed)
    placed_symbols = {line.split()[-1]: int(line.split()[0], 16)
                      for line in subprocess.check_output(
                          ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                          text=True).splitlines()}
    for name, (_, address, extent, short) in SPANS.items():
        if placed_sections[f".opencfw.evenai.{short}"] != (address, extent, "SHT_NOBITS") or \
                placed_symbols.get(name) != address:
            raise RuntimeError(f"NOLOAD placement changed: {name}")
    before = names(BASE, "-u")
    if len(before) != 191 or not set(SPANS) <= before:
        raise RuntimeError("EvenAI frame base frontier changed")
    linked = OUT / "apollo-main-even-ai-ram-state-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != set(SPANS) or after - before or len(after) != 184:
        raise RuntimeError("EvenAI RAM binding frontier changed")
    fixed_ram = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for section in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", section.name)
            if match and section["sh_size"]:
                start = int(match.group(1), 16)
                fixed_ram.append((start, start + section["sh_size"], section.name))
    for name, (_, address, extent, _) in SPANS.items():
        for start, end, other in fixed_ram:
            if address < end and start < address + extent:
                raise RuntimeError(f"EvenAI RAM overlap: {name} with {other}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_RAM_STATE_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED,
        "spans": [{"symbol": name, "pointer_literal": hex(literal),
                   "address": hex(address), "bytes": extent, "section_type": "NOBITS"}
                  for name, (literal, address, extent, _) in SPANS.items()],
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "other_fixed_ram_sections_checked": len(fixed_ram),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Seven NOLOAD spans are bounded by observed accesses and pointer literals.",
                   "Collision check covers named .g2_ram_ sections in this relocatable object; other linker fragments remain outside it.",
                   "Startup initialization and the final whole-image linker audit remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
