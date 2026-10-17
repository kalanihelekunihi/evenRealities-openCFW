#!/usr/bin/env python3
"""Pin stock-matched transcribe ring update into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-transcribe-update-5b41be"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-prep-note-utf8-prefix-5b3ef8/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_transcribe_update_5b41be"}
    if len(before) != 124 or len(after) != 123 or before-after != removed or after-before:
        raise RuntimeError("transcribe import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_TRANSCRIBE_UPDATE_5B41BE_C" or
            oracle["cases"] != 26 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("transcribe oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-utf8-prefix-5b3ef8/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_transcribe_output_200e2ae4", 0x200e2ae4, 0x1008),
                (".g2_conversate_transcribe_length_2007439c", 0x2007439c, 4),
                (".g2_conversate_transcribe_flag_20074fa2", 0x20074fa2, 1),
                (".g2_conversate_machine_context_200e3aec", 0x200e3aec, 8)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    linker = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_conversate_transcribe_ram_20261016.ld"
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_TRANSCRIBE_UPDATE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 26,
        "linker_script": ref(linker),
        "native_body": "0x5b41be..0x5b430d", "native_body_bytes": 336,
        "unresolved_before": 124, "unresolved_after": 123,
        "removed_imports": sorted(removed), "new_imports": [],
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "transcribe_ram": {"ring_address": "0x200d76b8", "slot_bytes": 0x402,
                           "slot_count": 4, "output_address": "0x200e2ae4",
                           "output_bytes": 0x1008, "length_address": "0x2007439c",
                           "flag_address": "0x20074fa2"},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Startup and wider Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
