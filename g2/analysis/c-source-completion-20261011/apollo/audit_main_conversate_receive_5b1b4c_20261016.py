#!/usr/bin/env python3
"""Pin bounded Conversate receive C integration and fixed RAM cells."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-receive-5b1b4c"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-data-handler-5b08a2/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 122 or len(after) != 121 or before - after != {"audio_conversate_receive_5b1b4c"} or after - before:
        raise RuntimeError("Conversate receive import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    ram = G2 / "components/audio/uart_thread_source_candidate/conversate_receive_ram_20261016.c"
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_receive_ram_20261016.ld"
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_RECEIVE_5B1B4C_C"
            or oracle["cases"] != 303 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate receive oracle changed")
    previous = json.loads((BASE / "main-conversate-data-handler-5b08a2/receipt.json").read_text())
    expected = {name: (int(row["address"], 16), row["size"])
                for name, row in previous["fixed_ram_sections"].items()}
    expected.update({".g2_conversate_last_magic_20074ff8": (0x20074ff8, 1),
                     ".g2_conversate_last_frame_tick_2007485c": (0x2007485c, 4)})
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_RECEIVE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "ram_source": ref(ram), "linker_script": ref(linker),
        "oracle_receipt": ref(oracle_path), "oracle_cases": 303,
        "native_body": "0x5b1b4c..0x5b1d29", "native_body_bytes": 478,
        "unresolved_before": 122, "unresolved_after": 121,
        "removed_imports": ["audio_conversate_receive_5b1b4c"], "new_imports": [],
        "fixed_ram_sections": {name: {"address": hex(address), "size": size,
                                      "type": "SHT_NOBITS"} for name, (address, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Nanopb and logging lowers, deeper Conversate dispatcher, context and reply-status RAM remain, alongside Main payload coverage.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()
