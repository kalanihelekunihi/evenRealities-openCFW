#!/usr/bin/env python3
"""Verify Cordio DM action-table C relocations against stock pointer rows."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_connection_action_tables_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-dm-connection-action-tables"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROWS = {
    "audio_ble_dm_master_table_a": (0x78d424, [0x536a87, 0x55bc5d]),
    "audio_ble_dm_master_table_b": (0x78d41c, [0x55bc71, 0x55bc7d]),
    "audio_ble_dm_slave_table_a": (0x785be0, [0x536ac9, 0x536add, 0x536af1, 0x536b05]),
    "audio_ble_dm_slave_table_b": (0x78d42c, [0x56e527, 0x56e565]),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj = OUT / "tables.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        symbols = {s.name: s for s in symtab.iter_symbols()}
        rel = elf.get_section_by_name(".rel.rodata")
        assert rel is not None and rel.num_relocations() == 10
        relocations = {r["r_offset"]: symtab.get_symbol(r["r_info_sym"]).name
                       for r in rel.iter_relocations()}
        assert all(r["r_info_type"] == 2 for r in rel.iter_relocations())
        rows = []
        for name, (address, pointers) in ROWS.items():
            symbol = symbols[name]
            assert symbol["st_size"] == 4 * len(pointers)
            stock = list(struct.unpack_from("<" + "I" * len(pointers),
                                            payload, address - 0x438000))
            assert stock == pointers, (name, stock)
            expected = [f"audio_ble_dm_action_{ptr & ~1:x}" for ptr in pointers]
            actual = [relocations[symbol["st_value"] + 4 * i]
                      for i in range(len(pointers))]
            assert actual == expected, (name, actual)
            rows.append({"table": name, "stock_address": hex(address),
                         "stock_pointers": [hex(value) for value in stock],
                         "relocation_targets": actual})
    record = {"status": "PASS_MAIN_BLE_DM_CONNECTION_ACTION_TABLES_C",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE), "object_sha256": sha(obj),
              "stock_payload_sha256": PAYLOAD_SHA, "rows": rows,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Ten DM action bodies and final ROM placement remain open."}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(rows), sha(receipt))


if __name__ == "__main__":
    main()
