#!/usr/bin/env python3
"""Pin directly accessed Conversate UI callback RAM cells."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-callback-ram"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-data-reset-helpers/candidate.o"
    candidate = HERE / "candidate.o"
    removed = {"audio_uart_registry_context_200004d8"}
    before, after = imports(prior), imports(candidate)
    if len(before) != 119 or len(after) != 118 or before-after != removed or after-before:
        raise RuntimeError("Conversate UI callback RAM import frontier changed")
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Stock Main payload changed")
    for address, literal in ((0x200004d8, 0x5b0a94),
                             (0x20074390, 0x5b0a88),
                             (0x200743a0, 0x5b0a90)):
        if payload[literal-0x438000:literal-0x438000+4] != address.to_bytes(4, "little"):
            raise RuntimeError(f"Conversate UI callback literal changed: {address:x}")
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in (
                (".g2_conversate_registry_context_200004d8", 0x200004d8, 8),
                (".g2_conversate_ui_start_tick_20074390", 0x20074390, 4),
                (".g2_conversate_ui_app_id_200743a0", 0x200743a0, 4),
                (".g2_conversate_last_success_tick_20074394", 0x20074394, 4),
                (".g2_conversate_event_names_200004f4", 0x200004f4, 52)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_addr"] != address or
                    section["sh_size"] != size):
                raise RuntimeError(f"Conversate UI callback RAM moved: {name}")
            if name != ".g2_conversate_event_names_200004f4" and section["sh_type"] != "SHT_NOBITS":
                raise RuntimeError(f"Conversate UI callback RAM type changed: {name}")
    source = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_callback_ram_20261016.c"
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_ui_callback_ram_20261016.ld"
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_CALLBACK_RAM_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "linker_script": ref(linker),
        "stock_payload_sha256": PAYLOAD_SHA,
        "literal_addresses": ["0x5b0a88", "0x5b0a90", "0x5b0a94"],
        "registry_context_address": "0x200004d8", "registry_context_accessed_prefix": 8,
        "start_tick_address": "0x20074390", "app_id_address": "0x200743a0",
        "unresolved_before": 119, "unresolved_after": 118,
        "removed_imports": sorted(removed), "new_imports": [],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Full registry context allocation, startup and callback behavior remain open.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
