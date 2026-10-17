#!/usr/bin/env python3
"""Pin stock-matched Conversate start-request selection into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-enter-loading-5b57ac"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-transcribe-update-5b41be/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_enter_loading_5b57ac"}
    added = {"audio_conversate_start_request_5b1f2e"}
    if len(before) != 123 or len(after) != 123 or before-after != removed or after-before != added:
        raise RuntimeError("Conversate start-request import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_ENTER_LOADING_5B57AC_C" or
            oracle["cases"] != 35 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate start-request oracle changed")
    previous = json.loads((BASE / "main-conversate-transcribe-update-5b41be/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_ENTER_LOADING_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 35,
        "native_body": "0x5b57ac..0x5b5885", "native_body_bytes": 218,
        "unresolved_before": 123, "unresolved_after": 123,
        "removed_imports": sorted(removed), "new_imports": sorted(added),
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "request_lower": "0x5b1f2e",
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Request construction lower, startup and wider Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
