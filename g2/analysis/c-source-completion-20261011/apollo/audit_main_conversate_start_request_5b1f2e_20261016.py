#!/usr/bin/env python3
"""Pin stock-matched prep-note selection encoder into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-start-request-5b1f2e"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-enter-loading-5b57ac/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_start_request_5b1f2e"}
    if len(before) != 123 or len(after) != 122 or before-after != removed or after-before:
        raise RuntimeError("Conversate request construction import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_START_REQUEST_5B1F2E_C" or
            oracle["cases"] != 120 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate request construction oracle changed")
    previous = json.loads((BASE / "main-conversate-enter-loading-5b57ac/receipt.json").read_text())
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_response_frame_200f4808", 0x200f4808, 4012),
                (".g2_conversate_response_encoded_2037c2a0", 0x2037c2a0, 256),
                (".g2_conversate_last_magic_20074ff8", 0x20074ff8, 1)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_START_REQUEST_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 120,
        "native_body": "0x5b1f2e..0x5b200d", "native_body_bytes": 224,
        "unresolved_before": 123, "unresolved_after": 122,
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
