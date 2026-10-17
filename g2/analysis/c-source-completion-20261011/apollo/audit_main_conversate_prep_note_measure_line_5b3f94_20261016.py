#!/usr/bin/env python3
"""Pin stock-matched prep-note line measurement into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-measure-line-5b3f94"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-prep-note-layout-parse-5b4000/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_prep_note_measure_line_5b3f94"}
    added = {"audio_conversate_prep_note_utf8_prefix_5b3ef8"}
    if len(before) != 125 or len(after) != 125 or before-after != removed or after-before != added:
        raise RuntimeError("prep-note measure import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_MEASURE_LINE_5B3F94_C" or
            oracle["cases"] != 84 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note measure oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-layout-parse-5b4000/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_machine_context_200e3aec", 0x200e3aec, 8),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94),
                (".g2_ram_200746dc", 0x200746dc, 4)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_MEASURE_LINE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 84,
        "ring_cells_linker_script": ref(ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_ring_list_cells_ram_20261016.ld"),
        "native_body": "0x5b3f94..0x5b3fff", "native_body_bytes": 108,
        "unresolved_before": 125, "unresolved_after": 125,
        "removed_imports": sorted(removed), "new_imports": sorted(added),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "utf8_prefix_lower": "0x5b3ef8",
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "UTF-8 prefix lower, startup and wider Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
