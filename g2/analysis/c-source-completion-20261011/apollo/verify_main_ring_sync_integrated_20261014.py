#!/usr/bin/env python3
"""Verify the corrected ring routines survived all Apollo replay stages."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BUILD = ROOT / "g2/build/c-firmware/20261014"
INPUT = BUILD / "main-input-archive-member-refresh/candidate-input-corrected.o"
ORACLE = BUILD / "ring-sync-correction/receipt.json"
REPLAY = BUILD / "main-post-tail-c-replay/receipt.json"
OUT = BUILD / "main-ring-sync-integrated"
SYMBOLS = ("audio_uart_ring_sync_active", "audio_uart_ring_sync_idle")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bodies(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        table = elf.get_section_by_name(".symtab")
        result = {}
        for symbol in table.iter_symbols():
            if symbol.name in SYMBOLS:
                section = elf.get_section(symbol["st_shndx"])
                offset = symbol["st_value"] - section["sh_addr"]
                result[symbol.name] = section.data()[offset:offset + symbol["st_size"]]
        return result


def main():
    oracle = json.loads(ORACLE.read_text())
    replay = json.loads(REPLAY.read_text())
    if oracle["status"] != "PASS_RING_SYNC_NATIVE_C_SOURCE_CORRECTION" or oracle["cases"] != 40:
        raise RuntimeError("native ring oracle evidence changed")
    if replay["status"] != "PASS_EXPERIMENTAL_MAIN_POST_TAIL_C_REPLAY" or replay["unresolved_after"] != 231:
        raise RuntimeError("Main replay changed")
    final_path = ROOT / replay["linked_object"]
    if sha(final_path) != replay["linked_object_sha256"]:
        raise RuntimeError("Main replay linked object changed")
    source = ROOT / "g2/components/audio/uart_thread_source_candidate/ring_sync.c"
    if oracle["sources"][str(source.relative_to(ROOT / "g2"))] != sha(source):
        raise RuntimeError("ring source changed after oracle")
    original, final = bodies(INPUT), bodies(final_path)
    if set(original) != set(SYMBOLS) or original != final:
        raise RuntimeError("corrected ring code changed or disappeared in Main replay")
    imports = subprocess.check_output(["arm-none-eabi-nm", "-u", str(final_path)], text=True)
    if len(imports.splitlines()) != 231:
        raise RuntimeError("Main import count changed")
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_RING_SYNC_INTEGRATED_C",
        "native_oracle": str(ORACLE.relative_to(ROOT)), "native_oracle_sha256": sha(ORACLE),
        "replay": str(REPLAY.relative_to(ROOT)), "replay_sha256": sha(REPLAY),
        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
        "input_object": str(INPUT.relative_to(ROOT)), "input_sha256": sha(INPUT),
        "final_object": str(final_path.relative_to(ROOT)), "final_sha256": sha(final_path),
        "functions": {name: hashlib.sha256(final[name]).hexdigest() for name in SYMBOLS},
        "unresolved_after": 231,
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Whole Main still has 234 imports and requires layout, startup, and device validation."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
