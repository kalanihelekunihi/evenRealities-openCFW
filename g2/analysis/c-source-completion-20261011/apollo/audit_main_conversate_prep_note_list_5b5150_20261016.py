#!/usr/bin/env python3
"""Pin bounded Conversate prep-note list action C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-list-5b5150"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-prep-note-packet-5b52e0/candidate.o"
    candidate = HERE / "candidate.o"
    added = {"audio_conversate_enter_loading_5b57ac",
             "audio_conversate_prep_note_list_update_5b4378"}
    before, after = imports(prior), imports(candidate)
    if (len(before) != 131 or len(after) != 132 or
            before - after != {"audio_conversate_action_5b5150"} or after - before != added):
        raise RuntimeError("Conversate prep-note list import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_LIST_5B5150_C"
            or oracle["cases"] != 45 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate prep-note list oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-packet-5b52e0/receipt.json").read_text())
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
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_LIST_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 45,
        "native_body": "0x5b5150..0x5b52c9", "native_body_bytes": 378,
        "unresolved_before": 131, "unresolved_after": 132,
        "removed_imports": ["audio_conversate_action_5b5150"], "new_imports": sorted(added),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Two Conversate action bodies, prep-note list update/enter-loading lowers and broader Main coverage remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
