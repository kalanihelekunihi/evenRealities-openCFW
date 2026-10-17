#!/usr/bin/env python3
"""Pin Conversate mutex-unlock C integration against the current Main object."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-unlock-5b0284"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-success-tick-5b03c2/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 125 or len(after) != 124 or before - after != {"audio_conversate_leave_5b0284"} or after - before:
        raise RuntimeError("Conversate unlock import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    ram = G2 / "components/audio/uart_thread_source_candidate/conversate_action_mutex_ram_20074398.c"
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_action_mutex_20074398.ld"
    if oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UNLOCK_5B0284_C" or oracle["cases"] != 30 or oracle["source_sha256"] != sha(source) or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Conversate unlock oracle changed")
    expected = {
        ".g2_conversate_action_mutex_20074398": (0x20074398, 4),
        ".g2_conversate_last_success_tick_20074394": (0x20074394, 4),
        ".g2_sync_info_response_200740c8": (0x200740c8, 12),
        ".g2_sync_info_encode_buffer_20071c48": (0x20071c48, 128),
        ".g2_sync_info_state_200740bc": (0x200740bc, 12),
        ".g2_ram_2007456c": (0x2007456c, 4),
        ".g2_print_buffer_2006b930": (0x2006b930, 1024),
        ".g2_ram_2006bd30": (0x2006bd30, 1024),
        ".g2_transaction_transport_2007397c": (0x2007397c, 30),
        ".g2_tx_packet_2007399c": (0x2007399c, 30),
        ".g2_pdm_clock_pin_words": (0x2007421c, 8),
        ".g2_ram_200742f0": (0x200742f0, 4),
    }
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_UNLOCK_INTEGRATION",
        "candidate_object": ref(candidate), "prior_candidate": ref(prior),
        "source": ref(source), "ram_source": ref(ram), "linker_script": ref(linker),
        "oracle_receipt": ref(oracle_path), "oracle_cases": 30,
        "native_body": "0x5b0284..0x5b02e3", "native_body_bytes": 96,
        "unresolved_before": 125, "unresolved_after": 124,
        "removed_imports": ["audio_conversate_leave_5b0284"],
        "fixed_ram_sections": {name: {"address": hex(addr), "size": size,
                                     "type": "SHT_NOBITS"} for name, (addr, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Conversate receive, handler, response, enter and two RAM objects remain, alongside the Main payload frontier.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
