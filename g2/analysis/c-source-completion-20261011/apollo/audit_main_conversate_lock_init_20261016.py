#!/usr/bin/env python3
"""Pin bounded Conversate lock/initializer C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
OUT = BASE / "main-conversate-mutex-init-5b0120"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-unlock-5b0284/candidate.o"
    candidate = OUT / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 124 or len(after) != 123 or before - after != {"audio_conversate_enter_5b01ca"} or after - before:
        raise RuntimeError("Conversate lock/initializer import frontier changed")
    oracles = []
    for folder, status, cases in (
        ("main-conversate-lock-5b01ca", "PASS_BOUNDED_MAIN_CONVERSATE_LOCK_5B01CA_C", 60),
        ("main-conversate-mutex-init-5b0120", "PASS_BOUNDED_MAIN_CONVERSATE_MUTEX_INIT_5B0120_C", 20),
    ):
        path = BASE / folder / "oracle-receipt.json"
        data = json.loads(path.read_text())
        if data["status"] != status or data["cases"] != cases or data["source_sha256"] != sha(ROOT / data["source"]) or data["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
            raise RuntimeError(f"Conversate oracle changed: {folder}")
        oracles.append((path, data))
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
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_LOCK_INIT_INTEGRATION",
        "candidate_object": ref(candidate), "prior_candidate": ref(prior),
        "lock_source": ref(ROOT / oracles[0][1]["source"]),
        "init_source": ref(ROOT / oracles[1][1]["source"]),
        "lock_oracle": ref(oracles[0][0]), "lock_oracle_cases": 60,
        "init_oracle": ref(oracles[1][0]), "init_oracle_cases": 20,
        "lock_native_body": "0x5b01ca..0x5b0283", "lock_native_bytes": 186,
        "init_native_body": "0x5b0120..0x5b01c9", "init_native_bytes": 170,
        "unresolved_before": 124, "unresolved_after": 123,
        "removed_imports": ["audio_conversate_enter_5b01ca"],
        "fixed_ram_sections": {name: {"address": hex(addr), "size": size,
                                     "type": "SHT_NOBITS"} for name, (addr, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Conversate receive, data handler, response and two RAM objects remain, alongside the Main payload frontier.",
    }
    output = OUT / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
