#!/usr/bin/env python3
"""Pin complete 0xac-byte owned span for the native UI deinit clear."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-deinit-tail-ram"
PRIOR = BASE / "main-conversate-ui-cleanup-5b3d62/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_deinit_tail_ram_200713fd.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_ui_deinit_tail_ram_20261016.ld"
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
    if imports(PRIOR) != imports(CANDIDATE) or len(imports(CANDIDATE)) != 126:
        raise RuntimeError("Conversate UI deinit RAM import frontier changed")
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    # 0x5b1572 loads the start address; 0x5b156e sets the exact clear size.
    if payload[0x5b15d8-0x438000:0x5b15dc-0x438000] != (0x20071368).to_bytes(4, "little"):
        raise RuntimeError("native UI deinit RAM pointer changed")
    if payload[0x5b156e-0x438000:0x5b1572-0x438000] != bytes.fromhex("ac210022"):
        raise RuntimeError("native UI deinit clear size changed")
    with CANDIDATE.open("rb") as stream:
        elf = ELFFile(stream)
        spans = ((".g2_conversate_ui_state_20071368", 0x20071368, 1),
                 (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94),
                 (".g2_conversate_ui_deinit_tail_200713fd", 0x200713fd, 0x17))
        for name, address, size in spans:
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_addr"] != address or
                    section["sh_size"] != size or section["sh_type"] != "SHT_NOBITS"):
                raise RuntimeError(f"Conversate UI deinit span changed: {name}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_DEINIT_RAM_SPAN",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "linker_script": ref(LINKER),
              "stock_payload_sha256": PAYLOAD_SHA,
              "native_clear": "0x5b156e..0x5b1579", "clear_start": "0x20071368",
              "clear_size": 172, "unresolved_before": 126, "unresolved_after": 126,
              "removed_imports": [], "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Full allocation beyond the observed deinit clear and deinit behavior remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(imports(CANDIDATE)), sha(receipt))


if __name__ == "__main__":
    main()
