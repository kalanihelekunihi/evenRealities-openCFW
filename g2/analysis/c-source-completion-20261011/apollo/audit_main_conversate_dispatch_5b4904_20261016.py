#!/usr/bin/env python3
"""Pin bounded Conversate dispatcher C integration and exposed action frontier."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-dispatch-5b4904"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-receive-5b1b4c/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    actions = ["audio_conversate_action_" + addr for addr in
               ("5b4a90", "5b4cc8", "5b4d10", "5b4e98", "5b4dba",
                "5b5150", "5b52e0", "5b4f72", "5b5428", "5b55b4")]
    added = set(actions) | {"audio_conversate_event_name_5b48f8",
                            "audio_conversate_machine_context_200e3aec"}
    if (len(before) != 121 or len(after) != 132 or before - after != {"audio_conversate_dispatch_5b4904"} or after - before != added):
        raise RuntimeError("Conversate dispatcher import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_DISPATCH_5B4904_C"
            or oracle["cases"] != 160 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate dispatcher oracle changed")
    previous = json.loads((BASE / "main-conversate-receive-5b1b4c/receipt.json").read_text())
    expected = {name: (int(row["address"], 16), row["size"])
                for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_DISPATCH_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 160,
        "native_body": "0x5b4904..0x5b4a8f", "native_body_bytes": 396,
        "stock_action_table": oracle["stock_action_table"],
        "unresolved_before": 121, "unresolved_after": 132,
        "removed_imports": ["audio_conversate_dispatch_5b4904"],
        "new_imports": sorted(added),
        "fixed_ram_sections": {name: {"address": hex(address), "size": size,
                                      "type": "SHT_NOBITS"} for name, (address, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Ten action bodies, event-name lookup and machine context RAM are exposed. Full Main coverage remains open.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
