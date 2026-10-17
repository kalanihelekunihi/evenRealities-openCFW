#!/usr/bin/env python3
"""Pin bounded Conversate callback/tick integration and explicit new imports."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
COMMON = BASE / "main-conversate-common-5b0476"
TICK = BASE / "main-conversate-success-tick-5b03c2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    before_obj = BASE / "main-sync-info-notify-471fa4/candidate.o"
    common_obj = COMMON / "candidate.o"
    tick_obj = TICK / "candidate.o"
    before, middle, after = [imports(path) for path in (before_obj, common_obj, tick_obj)]
    new = {
        "audio_conversate_context_200d5bd8", "audio_conversate_data_handler_5b08a2",
        "audio_conversate_enter_5b01ca", "audio_conversate_leave_5b0284",
        "audio_conversate_receive_5b1b4c", "audio_conversate_reply_status_200d6b84",
        "audio_conversate_respond_5b200e", "audio_conversate_success_5b03c2",
    }
    if len(before) != 119 or len(middle) != 126 or len(after) != 125 or middle - before != new or before - middle != {"audio_uart_registry_callback_5b0476"} or middle - after != {"audio_conversate_success_5b03c2"} or after - middle:
        raise RuntimeError("Conversate import frontier changed")
    common_oracle_path = COMMON / "oracle-receipt.json"
    tick_oracle_path = TICK / "oracle-receipt.json"
    common_oracle = json.loads(common_oracle_path.read_text())
    tick_oracle = json.loads(tick_oracle_path.read_text())
    for receipt, status, cases in ((common_oracle, "PASS_BOUNDED_MAIN_CONVERSATE_COMMON_5B0476_C", 80),
                                   (tick_oracle, "PASS_BOUNDED_MAIN_CONVERSATE_SUCCESS_TICK_5B03C2_C", 16)):
        if receipt["status"] != status or receipt["cases"] != cases or receipt["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701" or receipt["source_sha256"] != sha(ROOT / receipt["source"]):
            raise RuntimeError("Conversate oracle source or status changed")
    expected = {
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
    with tick_obj.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_COMMON_TICK_INTEGRATION",
        "candidate_object": ref(tick_obj), "prior_candidate": ref(before_obj),
        "common_candidate": ref(common_obj),
        "common_source": ref(ROOT / common_oracle["source"]),
        "tick_source": ref(ROOT / tick_oracle["source"]),
        "tick_ram_source": ref(G2 / "components/audio/uart_thread_source_candidate/conversate_success_tick_ram_20074394.c"),
        "linker_script": ref(G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_success_tick_20074394.ld"),
        "common_oracle": ref(common_oracle_path), "common_oracle_cases": 80,
        "tick_oracle": ref(tick_oracle_path), "tick_oracle_cases": 16,
        "common_native_body": "0x5b0476..0x5b05cf", "common_native_bytes": 346,
        "tick_native_body": "0x5b03c2..0x5b03d7", "tick_native_bytes": 22,
        "unresolved_before": 119, "unresolved_common": 126, "unresolved_after": 125,
        "common_removed_import": "audio_uart_registry_callback_5b0476",
        "common_added_imports": sorted(new),
        "tick_removed_import": "audio_conversate_success_5b03c2",
        "fixed_ram_sections": {name: {"address": hex(addr), "size": size,
                                     "type": "SHT_NOBITS"} for name, (addr, size) in expected.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Reconstruct Conversate receive, handler, response, enter/leave and two RAM objects; then remaining Main imports and full payload.",
    }
    output = TICK / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
