#!/usr/bin/env python3
"""Pin bounded Conversate data-handler C integration and frontier."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-data-handler-5b08a2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-descriptor-775b24/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 122 or len(after) != 122 or before - after != {"audio_conversate_data_handler_5b08a2"} or after - before != {"audio_conversate_dispatch_5b4904"}:
        raise RuntimeError("Conversate data-handler import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_DATA_HANDLER_5B08A2_C" or oracle["cases"] != 160 or oracle["source_sha256"] != sha(source) or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Conversate data-handler oracle changed")
    previous = json.loads((BASE / "main-conversate-descriptor-775b24/receipt.json").read_text())
    expected = {name: (int(row["address"], 16), row["size"])
                for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_DATA_HANDLER_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path),
        "oracle_cases": 160,
        "native_body": "0x5b08a2..0x5b09dd", "native_body_bytes": 316,
        "unresolved_before": 122, "unresolved_after": 122,
        "removed_imports": ["audio_conversate_data_handler_5b08a2"],
        "new_imports": ["audio_conversate_dispatch_5b4904"],
        "fixed_ram_sections": {name: {"address": hex(address), "size": size,
                                     "type": "SHT_NOBITS"} for name, (address, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Conversate receive, deeper dispatcher, context and reply-status RAM remain, alongside Main payload coverage.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
