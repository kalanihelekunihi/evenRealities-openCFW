#!/usr/bin/env python3
"""Pin the direct prep-note byte accessor in the current Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-finish-5b476a"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-ui-settings-5b133c/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if (len(before) != 128 or len(after) != 127 or
            before - after != {"audio_conversate_prep_note_finish_5b476a"} or
            after - before):
        raise RuntimeError("prep-note accessor import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_FINISH_5B476A_C" or
            oracle["cases"] != 7 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note accessor oracle changed")
    previous = json.loads((BASE / "main-conversate-ui-settings-5b133c/receipt.json").read_text())
    fixed = {name: (int(row["address"], 16), row["size"])
             for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in fixed.items():
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"fixed RAM section changed: {name}")
        for name, address, size in (
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_machine_context_200e3aec", 0x200e3aec, 8),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_FINISH_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 7,
        "native_body": "0x5b476a..0x5b476f", "native_body_bytes": 6,
        "native_read_address": "0x200d86cc", "source_region_offset": "0x109c",
        "unresolved_before": 128, "unresolved_after": 127,
        "removed_imports": ["audio_conversate_prep_note_finish_5b476a"],
        "new_imports": [], "fixed_ram_sections": previous["fixed_ram_sections"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Wider prep-note state machine and Main coverage remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
