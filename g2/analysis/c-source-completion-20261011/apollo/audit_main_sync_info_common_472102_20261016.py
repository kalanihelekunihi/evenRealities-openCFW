#!/usr/bin/env python3
"""Pin bounded SyncInfo callback integration without implying payload completion."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-sync-info-common-472102"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()})


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def main():
    prior = BASE / "main-fatal-hook-alias/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = set(imports(prior)), set(imports(candidate))
    removed = before - after
    added = after - before
    if len(before) != 121 or len(after) != 122 or removed != {"audio_uart_registry_callback_472102"} or added != {
        "audio_sync_info_pb_descriptor_77c1cc", "audio_sync_info_command_471ee8"
    }:
        raise RuntimeError(f"unexpected SyncInfo import delta: {removed}, {added}")
    expected = {
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
    state = ROOT / "g2/components/audio/uart_thread_source_candidate/sync_info_state_200740bc.c"
    script = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_sync_info_common_472102.ld"
    if oracle["status"] != "PASS_BOUNDED_MAIN_SYNC_INFO_COMMON_472102_C" or oracle["cases"] != 40 or oracle["source_sha256"] != sha(source) or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("SyncInfo native oracle changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_SYNC_INFO_COMMON_INTEGRATION",
        "candidate_object": ref(candidate), "prior_candidate": ref(prior),
        "source": ref(source), "state_source": ref(state), "linker_script": ref(script),
        "oracle_receipt": ref(oracle_path), "oracle_cases": 40,
        "native_body": "0x472102..0x4721f3", "native_body_bytes": 242,
        "unresolved_before": 121, "unresolved_after": 122,
        "removed_imports": sorted(removed), "new_imports": sorted(added),
        "fixed_ram_sections": {name: {"address": hex(addr), "size": size, "type": "SHT_NOBITS"} for name, (addr, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Reconstruct protobuf descriptor, command handler and all remaining imports; validate full image payload and hardware separately.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
