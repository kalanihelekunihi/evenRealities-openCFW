#!/usr/bin/env python3
"""Pin stock-matched prep-note packet update into the Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-packet-update-5b44d8"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-prep-note-list-update-5b4378/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_prep_note_packet_update_5b44d8"}
    added = {"audio_conversate_prep_note_text_commit_5b4164"}
    if len(before) != 125 or len(after) != 125 or before-after != removed or after-before != added:
        raise RuntimeError("prep-note packet import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_PACKET_UPDATE_5B44D8_C" or
            oracle["cases"] != 55 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note packet oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-list-update-5b4378/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_machine_context_200e3aec", 0x200e3aec, 8),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_PACKET_UPDATE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 55,
        "native_body": "0x5b44d8..0x5b4739", "native_body_bytes": 610,
        "unresolved_before": 125, "unresolved_after": 125,
        "removed_imports": sorted(removed), "new_imports": sorted(added),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "text_commit_lower": "0x5b4164",
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Text commit lower, startup and wider Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
