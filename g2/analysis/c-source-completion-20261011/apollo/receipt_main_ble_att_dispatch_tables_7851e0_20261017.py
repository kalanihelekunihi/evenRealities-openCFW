#!/usr/bin/env python3
"""Bind source-owned Cordio ATT no-op dispatch tables and handlers."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
HERE = BASE / "main-ble-att-dispatch-tables-7851e0"
PRIOR = BASE / "main-lv-heap-pool-20000338/candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_att_dispatch_tables_7851e0.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT, CURRENT, OUT = HERE / "att-tables.o", HERE / "candidate.o", HERE / "receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
EXPECTED = [
    "audio_ble_att_noop_4b4eec", "audio_ble_atts_callback_4b4ee6",
    "audio_ble_atts_callback_4b4ee6", "audio_ble_att_noop_4b4ee8",
    "audio_ble_att_noop_4b4eea", "audio_ble_att_noop_4b4eea",
    "audio_ble_atts_callback_4b4ee6", "audio_ble_att_noop_4b4ee8",
]
STOCK_POINTERS = (0x4b4eed, 0x4b4ee7, 0x4b4ee7, 0x4b4ee9,
                  0x4b4eeb, 0x4b4eeb, 0x4b4ee7, 0x4b4ee9)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    stock_words = struct.unpack_from("<8I", payload, 0x7851e0 - 0x438000)
    assert stock_words == STOCK_POINTERS
    for address in (0x4b4ee6, 0x4b4ee8, 0x4b4eea, 0x4b4eec):
        assert payload[address - 0x438000:address - 0x438000 + 2] == b"\x70\x47"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        reloc = elf.get_section_by_name(".rel.rodata")
        assert reloc is not None
        entries = sorted((r["r_offset"], symtab.get_symbol(r["r_info_sym"]).name)
                         for r in reloc.iter_relocations())
        assert entries == [(index * 4, name)
                           for index, name in enumerate(EXPECTED)]
        rodata = elf.get_section_by_name(".rodata")
        assert len(rodata.data()) == 32
        text = elf.get_section_by_name(".text").data()
        for name in ("audio_ble_att_noop_4b4ee8", "audio_ble_att_noop_4b4eea",
                     "audio_ble_att_noop_4b4eec"):
            sym = next(s for s in symtab.iter_symbols() if s.name == name)
            offset = sym["st_value"] & ~1
            assert text[offset:offset + 2] == b"\x70\x47"
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 106 and len(current) == 104
    assert removed == ["audio_ble_att_table_main", "audio_ble_att_table_secondary"]
    assert not added
    assert set(EXPECTED).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATT_DISPATCH_TABLES_7851E0_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "stock_payload_sha256": PAYLOAD_SHA,
        "stock_table_span": "0x7851e0..0x7851ff",
        "stock_handler_bodies": ["0x4b4ee6", "0x4b4ee8", "0x4b4eea", "0x4b4eec"],
        "stock_pointers": [f"0x{x:08x}" for x in STOCK_POINTERS],
        "unresolved_before": 106, "unresolved_after": 104,
        "removed_imports": removed, "new_imports": added,
        "new_providers": sorted(set(EXPECTED + removed)),
        "remaining_gate": "Two source-owned ATT no-op dispatch tables match eight stock pointers and four BX LR bodies. Other BLE tables, callbacks and Main imports remain; whole-image source and hardware behavior are open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
