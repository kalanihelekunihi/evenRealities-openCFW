#!/usr/bin/env python3
"""Pin decoded Conversate context RAM next to reply-status RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-context-ram"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-audio-manager-aliases/candidate.o"
    candidate = HERE / "candidate.o"
    removed = {"audio_conversate_context_200d5bd8"}
    before, after = imports(prior), imports(candidate)
    if len(before) != 120 or len(after) != 119 or before-after != removed or after-before:
        raise RuntimeError("Conversate context import frontier changed")
    source = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_context_ram_200d5bd8.c"
    linker = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_conversate_context_ram_20261016.ld"
    callback_oracle = BASE / "main-conversate-common-5b0476/oracle-receipt.json"
    oracle = json.loads(callback_oracle.read_text())
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_COMMON_5B0476_C" or
            oracle["cases"] != 80 or oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate context callback oracle changed")
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_context_200d5bd8", 0x200d5bd8, 0xfac),
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"Conversate RAM section changed: {name}")
        symbols = {item.name: (item["st_value"] +
                    elf.get_section(item["st_shndx"])["sh_addr"])
                   for item in elf.get_section_by_name(".symtab").iter_symbols()
                   if isinstance(item["st_shndx"], int)}
        if symbols["audio_conversate_context_200d5bd8"] != 0x200d5bd8 or \
                symbols["audio_conversate_reply_status_200d6b84"] != 0x200d6b84:
            raise RuntimeError("Conversate RAM symbols moved")
    if 0x200d5bd8 + 0xfac != 0x200d6b84 or 0x200d6b84 + 0xaac != 0x200d7630:
        raise RuntimeError("Conversate RAM adjacency changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_CONTEXT_RAM_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "linker_script": ref(linker),
        "callback_oracle_receipt": ref(callback_oracle), "callback_oracle_cases": 80,
        "native_address": "0x200d5bd8", "size": 0xfac,
        "next_region_address": "0x200d6b84",
        "unresolved_before": 120, "unresolved_after": 119,
        "removed_imports": sorted(removed), "new_imports": [],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Startup initialization and full context lifetime remain open.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
