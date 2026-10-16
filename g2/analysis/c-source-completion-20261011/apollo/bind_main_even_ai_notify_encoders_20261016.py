#!/usr/bin/env python3
"""Bind local EvenAI notification encoders and their stock sequence cell."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_notify_encoders_4e3788.c"
RAM_SOURCE = COMP / "even_ai_notify_sequence_ram.c"
LINKER = COMP / "even_ai_notify_sequence_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-local-decode/apollo-main-even-ai-local-decode-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-notify-encoders-bound"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
NANOPB = ROOT / "third-party/upstream/nanopb"
PROVIDERS = {"audio_even_ai_encode_ctrl_4e3788", "audio_even_ai_encode_vad_4e3b80"}
SEQUENCE = "audio_even_ai_notify_sequence_20074ff9"
ADDRESS = 0x20074ff9
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
    if hashlib.sha256(image).hexdigest() != PINNED or \
            int.from_bytes(image[0x4e4124-0x438000:0x4e4128-0x438000], "little") != ADDRESS:
        raise RuntimeError("EvenAI notify sequence pointer or payload changed")
    oracles = []
    for suffix, status in (("ctrl-4e3788", "PASS_NATIVE_MAIN_EVEN_AI_NOTIFY_CTRL_4E3788"),
                           ("vad-4e3b80", "PASS_NATIVE_MAIN_EVEN_AI_NOTIFY_VAD_4E3B80")):
        path = G2 / "build/c-firmware/20261016" / f"main-even-ai-notify-{suffix}" / "oracle-receipt.json"
        data = json.loads(path.read_text())
        if data["status"] != status or data["cases"] != 68 or \
                data["source_sha256"] != sha(SOURCE) or \
                data["stock_payload_sha256"] != PINNED:
            raise RuntimeError(f"EvenAI notify oracle changed: {suffix}")
        oracles.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_notify_encoders_4e3788.o"
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
             '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
             "-I", str(CONFIG), "-I", str(NANOPB)]
    subprocess.run(["clang", *flags, "-c", str(SOURCE), "-o", str(obj)], check=True)
    ram_obj = OUT / "even_ai_notify_sequence_ram.o"
    subprocess.run(["clang", *flags, "-c", str(RAM_SOURCE), "-o", str(ram_obj)], check=True)
    if names(obj, "--defined-only") != PROVIDERS or \
            names(ram_obj, "--defined-only") != {SEQUENCE}:
        raise RuntimeError("EvenAI notify source symbols changed")
    if sections(ram_obj)[".bss.opencfw.evenai.notify.sequence"][1:] != (1, "SHT_NOBITS"):
        raise RuntimeError("EvenAI notify sequence C extent changed")
    placed = OUT / "even-ai-notify-sequence-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", SEQUENCE,
                    str(ram_obj), "-o", str(placed)], check=True)
    if sections(placed)[".opencfw.evenai.notify.sequence"] != (ADDRESS, 1, "SHT_NOBITS"):
        raise RuntimeError("EvenAI notify sequence NOLOAD placement changed")
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    if located.get(SEQUENCE) != ADDRESS:
        raise RuntimeError("EvenAI notify sequence symbol address changed")
    before = names(BASE, "-u")
    if len(before) != 174 or not PROVIDERS <= before or SEQUENCE in before:
        raise RuntimeError("Apollo EvenAI notify base frontier changed")
    linked = OUT / "apollo-main-even-ai-notify-encoders-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), str(ram_obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != PROVIDERS or after - before or len(after) != 172:
        raise RuntimeError("Apollo EvenAI notify linked frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(start <= ADDRESS < end for start, end, _ in fixed):
        raise RuntimeError("EvenAI notify sequence overlaps named fixed RAM")
    for prior in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                  "main-battery-callback-manager-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        if any(int(span["address"], 16) <= ADDRESS < int(span["address"], 16) + span["bytes"]
               for span in prior_receipt["spans"]):
            raise RuntimeError(f"EvenAI notify sequence overlaps {prior}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_NOTIFY_ENCODERS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "ram_source": str(RAM_SOURCE.relative_to(ROOT)), "ram_source_sha256": sha(RAM_SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "sequence_pointer_literal": "0x4e4124",
        "sequence_address": hex(ADDRESS), "sequence_bytes": 1,
        "oracles": oracles, "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "ram_object": str(ram_obj.relative_to(ROOT)), "ram_object_sha256": sha(ram_obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(PROVIDERS), "imports_added": [],
        "fixed_ram_sections_checked": len(fixed), "source_complete": False,
        "full_payload_linked": False, "hardware_proof": False,
        "limits": ["One hundred thirty-six controlled stock comparisons cover encoder bytes, sequence, send/fault calls, and enabled logger metadata and first formatted values.",
                   "Logger side effects, later variadic values, final global placement/startup, and hardware execution remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
