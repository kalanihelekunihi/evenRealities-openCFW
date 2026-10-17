#!/usr/bin/env python3
"""Pin bounded Conversate app-open action C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-app-open-5b4a90"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-tag-data-5b4f72/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if (len(before) != 132 or len(after) != 133 or
            before - after != {"audio_conversate_action_5b4a90"} or
            after - before != {"audio_conversate_prep_note_update_5b43ee", "audio_conversate_tag_storage_init_59619e"}):
        raise RuntimeError("Conversate app-open import frontier changed")
    if "audio_quicklist_tick_now" not in subprocess.check_output(
            ["arm-none-eabi-nm", "-g", "--defined-only", str(prior)], text=True):
        raise RuntimeError("existing native time provider is missing")
    time_receipt_path = G2 / "build/c-firmware/20261014/main-quicklist-tick-alias/receipt.json"
    time_receipt = json.loads(time_receipt_path.read_text())
    if (time_receipt["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_TICK_ALIAS_C" or
            time_receipt["native_entry"] != "0x44a1c6" or
            time_receipt["context_oracle_status"] != "PASS_AUDIO_LOG_CONTEXT 35"):
        raise RuntimeError("native time provider evidence changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_APP_OPEN_5B4A90_C"
            or oracle["cases"] != 50 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate app-open oracle changed")
    previous = json.loads((BASE / "main-conversate-tag-data-5b4f72/receipt.json").read_text())
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
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_APP_OPEN_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 50,
        "native_body": "0x5b4a90..0x5b4cc7", "native_body_bytes": 568,
        "unresolved_before": 132, "unresolved_after": 133,
        "removed_imports": ["audio_conversate_action_5b4a90"],
        "new_imports": sorted({"audio_conversate_prep_note_update_5b43ee", "audio_conversate_tag_storage_init_59619e"}),
        "native_time_provider_receipt": ref(time_receipt_path),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "All ten Conversate dispatcher action bodies now have bounded C candidates; newly exposed lowers and broader Main coverage remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
