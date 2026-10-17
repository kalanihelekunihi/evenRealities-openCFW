#!/usr/bin/env python3
"""Pin bounded Conversate prep-note packet action C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-packet-5b52e0"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-transcribe-data-5b5428/candidate.o"
    candidate = HERE / "candidate.o"
    added = {"audio_conversate_prep_note_finish_5b476a",
             "audio_conversate_prep_note_packet_update_5b44d8"}
    before, after = imports(prior), imports(candidate)
    if (len(before) != 130 or len(after) != 131 or
            before - after != {"audio_conversate_action_5b52e0"} or after - before != added):
        raise RuntimeError("Conversate prep-note packet import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_PACKET_5B52E0_C"
            or oracle["cases"] != 35 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate prep-note packet oracle changed")
    previous = json.loads((BASE / "main-conversate-transcribe-data-5b5428/receipt.json").read_text())
    fixed = {name: (int(row["address"], 16), row["size"])
             for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in fixed.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
        for name, address, size, edges in (
                (".g2_conversate_event_names_200004f4", 0x200004f4, 52, 13),
                (".g2_conversate_ui_state_names_20000540", 0x20000540, 28, 7)):
            section = elf.get_section_by_name(name)
            relocs = elf.get_section_by_name(".rel" + name)
            if section is None or section["sh_type"] != "SHT_PROGBITS" or section["sh_addr"] != address or section["sh_size"] != size or relocs is None or relocs.num_relocations() != edges:
                raise RuntimeError(f"initialized name table changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_PACKET_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 35,
        "native_body": "0x5b52e0..0x5b53f5", "native_body_bytes": 278,
        "unresolved_before": 130, "unresolved_after": 131,
        "removed_imports": ["audio_conversate_action_5b52e0"], "new_imports": sorted(added),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Three Conversate action bodies, prep-note packet update/finish lowers and broader Main coverage remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
