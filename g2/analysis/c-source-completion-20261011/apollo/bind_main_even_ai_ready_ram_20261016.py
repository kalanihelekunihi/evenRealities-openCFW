#!/usr/bin/env python3
"""Reserve the authenticated EvenAI async-update RAM pointers in C."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_ready_ram.c"
LINKER = COMP / "even_ai_ready_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-notify-encoders-bound/apollo-main-even-ai-notify-encoders-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ready-ram-bound"
NATIVE = G2 / "research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/004e20f2.c"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SPANS = [
    ("audio_even_ai_ready_state_2006f138", ".bss.opencfw.evenai.ready.state",
     ".opencfw.evenai.ready.state", 0x4e2c38, 0x2006f138, 0x218),
    ("audio_even_ai_text_stream_handle_20074c04", ".bss.opencfw.evenai.text.handle",
     ".opencfw.evenai.text.handle", 0x4e2d78, 0x20074c04, 4),
    ("audio_even_ai_text_pending_200f39b4", ".bss.opencfw.evenai.text.pending",
     ".opencfw.evenai.text.pending", 0x4e2d7c, 0x200f39b4, 0x400),
    ("audio_even_ai_text_merged_200f3db4", ".bss.opencfw.evenai.text.merged",
     ".opencfw.evenai.text.merged", 0x4e2d80, 0x200f3db4, 0x400),
]

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
    for _, _, _, literal, address, _ in SPANS:
        if int.from_bytes(image[literal-0x438000:literal-0x438000+4], "little") != address:
            raise RuntimeError(f"EvenAI ready RAM literal {literal:#x} changed")
    native = NATIVE.read_text()
    for marker in ("_DAT_004e2c38[8]", "pcVar2[0xd]", "_DAT_004e2d7c,0x400,0",
                   "_DAT_004e2d80,0x400,0", "*_DAT_004e2d78"):
        if marker not in native:
            raise RuntimeError(f"EvenAI ready native access changed: {marker}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_ready_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {x[0] for x in SPANS} or names(obj, "-u"):
        raise RuntimeError("EvenAI ready RAM C symbols changed")
    raw = sections(obj)
    for _, input_section, _, _, _, extent in SPANS:
        if raw[input_section][1:] != (extent, "SHT_NOBITS"):
            raise RuntimeError(f"EvenAI ready C extent changed: {input_section}")
    placed = OUT / "even-ai-ready-ram-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", SPANS[0][0],
                    str(obj), "-o", str(placed)], check=True)
    layout = sections(placed)
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    for symbol, _, output_section, _, address, extent in SPANS:
        if layout[output_section] != (address, extent, "SHT_NOBITS") or \
                located.get(symbol) != address:
            raise RuntimeError(f"EvenAI ready NOLOAD placement changed: {symbol}")
    before = names(BASE, "-u")
    if len(before) != 172 or {x[0] for x in SPANS} & before:
        raise RuntimeError("Apollo EvenAI ready RAM base frontier changed")
    linked = OUT / "apollo-main-even-ai-ready-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before != after:
        raise RuntimeError("Apollo EvenAI ready RAM unexpectedly changed imports")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    for symbol, _, _, _, address, extent in SPANS:
        if any(address < end and start < address + extent for start, end, _ in fixed):
            raise RuntimeError(f"EvenAI ready span overlaps named fixed RAM: {symbol}")
    prior = []
    for directory in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                      "main-battery-callback-manager-ram-bound"):
        data = json.loads((G2 / "build/c-firmware/20261016" / directory / "receipt.json").read_text())
        prior.extend((int(span["address"], 16), span["bytes"], directory)
                     for span in data["spans"])
    for directory in ("main-dashboard-layout-current-ram-bound", "main-efs-transfer-state-ram-bound",
                      "main-ble-flash-staging-ram-bound", "main-ble-flash-callbacks-ram-bound",
                      "main-tpl-response-buffer-ram-bound", "main-tpl-timeout-ids-ram-bound",
                      "main-tpl-service-row0-ram-bound"):
        data = json.loads((G2 / "build/c-firmware/20261016" / directory / "receipt.json").read_text())
        prior.append((int(data["address"], 16), data["bytes"], directory))
    prior.append((0x20074ff9, 1, "EvenAI notify sequence"))
    for symbol, _, _, _, address, extent in SPANS:
        if any(address < start + size and start < address + extent for start, size, _ in prior):
            raise RuntimeError(f"EvenAI ready span overlaps prior source RAM: {symbol}")
    spans = [{"symbol": symbol, "pointer_literal": hex(literal),
              "address": hex(address), "bytes": extent}
             for symbol, _, _, literal, address, extent in SPANS]
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "native_decomp": str(NATIVE.relative_to(ROOT)), "native_decomp_sha256": sha(NATIVE),
        "payload_sha256": PINNED, "spans": spans, "section_type": "NOBITS",
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [], "imports_added": [],
        "fixed_ram_sections_checked": len(fixed), "source_complete": False,
        "full_payload_linked": False, "hardware_proof": False,
        "limits": ["The 0x218-byte ready-state reservation is provisional; observed fixed accesses and text termination fit, but dynamic copy lengths can exceed it.",
                   "Both 0x400-byte text buffers match native clear extents; stream-handle startup and full allocation bounds remain open.",
                   "The EvenAI ready code provider is not yet bound; final global layout and hardware execution remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
