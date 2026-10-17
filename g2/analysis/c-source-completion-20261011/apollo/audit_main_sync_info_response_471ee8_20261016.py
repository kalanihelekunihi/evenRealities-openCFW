#!/usr/bin/env python3
"""Pin bounded SyncInfo response C integration and retained RAM layout."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-sync-info-response-471ee8"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()})


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def main():
    prior = BASE / "main-sync-info-common-472102/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = set(imports(prior)), set(imports(candidate))
    if len(before) != 122 or len(after) != 121 or before - after != {"audio_sync_info_command_471ee8"} or after - before:
        raise RuntimeError("unexpected SyncInfo response import frontier")
    expected = {
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
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    ram = ROOT / "g2/components/audio/uart_thread_source_candidate/sync_info_response_ram_20261016.c"
    script = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_sync_info_response_471ee8.ld"
    if oracle["status"] != "PASS_BOUNDED_MAIN_SYNC_INFO_RESPONSE_471EE8_C" or oracle["cases"] != 80 or oracle["source_sha256"] != sha(source) or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("SyncInfo response oracle changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_SYNC_INFO_RESPONSE_INTEGRATION",
        "candidate_object": ref(candidate), "prior_candidate": ref(prior),
        "source": ref(source), "ram_source": ref(ram), "linker_script": ref(script),
        "oracle_receipt": ref(oracle_path), "oracle_cases": 80,
        "native_body": "0x471ee8..0x471fa3", "native_body_bytes": 188,
        "unresolved_before": 122, "unresolved_after": 121,
        "removed_imports": ["audio_sync_info_command_471ee8"], "new_imports": [],
        "fixed_ram_sections": {name: {"address": hex(addr), "size": size, "type": "SHT_NOBITS"} for name, (addr, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Reconstruct protobuf descriptor and other remaining imports; validate complete payload and hardware separately.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
