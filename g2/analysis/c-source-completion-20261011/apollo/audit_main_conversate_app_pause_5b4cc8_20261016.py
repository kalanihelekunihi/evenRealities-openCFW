#!/usr/bin/env python3
"""Pin bounded Conversate app-pause action C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-app-pause-5b4cc8"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-event-name-5b48f8/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 132 or len(after) != 131 or before - after != {"audio_conversate_action_5b4cc8"} or after - before:
        raise RuntimeError("Conversate app-pause import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_APP_PAUSE_5B4CC8_C"
            or oracle["cases"] != 14 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate app-pause oracle changed")
    previous = json.loads((BASE / "main-conversate-event-name-5b48f8/receipt.json").read_text())
    expected = {name: (int(row["address"], 16), row["size"])
                for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_APP_PAUSE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 14,
        "native_body": "0x5b4cc8..0x5b4d0f", "native_body_bytes": 72,
        "unresolved_before": 132, "unresolved_after": 131,
        "removed_imports": ["audio_conversate_action_5b4cc8"], "new_imports": [],
        "fixed_ram_sections": {name: {"address": hex(address), "size": size,
                                      "type": "SHT_NOBITS"} for name, (address, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Nine Conversate action bodies and event-name RAM table remain, with other Main coverage.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
