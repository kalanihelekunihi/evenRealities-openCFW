#!/usr/bin/env python3
"""Pin direct stock-matched UTF-8 prefix body into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-utf8-prefix-5b3ef8"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-prep-note-measure-line-5b3f94/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_prep_note_utf8_prefix_5b3ef8"}
    if len(before) != 125 or len(after) != 124 or before-after != removed or after-before:
        raise RuntimeError("prep-note UTF-8 prefix import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_UTF8_PREFIX_5B3EF8_C" or
            oracle["cases"] != 117 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note UTF-8 prefix oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-measure-line-5b3f94/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_ram_200746dc", 0x200746dc, 4)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_UTF8_PREFIX_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 117,
        "native_body": "0x5b3ef8..0x5b3f93", "native_body_bytes": 156,
        "unresolved_before": 125, "unresolved_after": 124,
        "removed_imports": sorted(removed), "new_imports": [],
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Startup and wider Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
