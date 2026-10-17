#!/usr/bin/env python3
"""Bind Cordio ATT client, indication and server interface tables."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
HERE = BASE / "main-ble-att-interface-tables-785250"
PRIOR = BASE / "main-ble-att-dispatch-tables-7851e0/candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_att_interface_tables_785250.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/stack/att"
OBJECT, CURRENT, OUT = HERE / "att-interfaces.o", HERE / "candidate.o", HERE / "receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
TABLES = (
    (0x785250, "audio_ble_attc_table",
     (0x53119d, 0x531331, 0x5315b5, 0x53135b),
     ("audio_ble_attc_data_53119c", "audio_ble_attc_ctrl_531330",
      "audio_ble_attc_msg_5315b4", "audio_ble_attc_conn_53135a")),
    (0x7852c0, "audio_ble_atts_ind_table",
     (0x4b4eed, 0x533c4d, 0x533bcd, 0x533a41),
     ("audio_ble_att_noop_4b4eec", "audio_ble_atts_ind_ctrl_533c4c",
      "audio_ble_atts_ind_msg_533bcc", "audio_ble_atts_ind_conn_533a40")),
    (0x7852f0, "audio_ble_atts_table",
     (0x53498d, 0x534c8b, 0x534c43, 0x534abb),
     ("audio_ble_atts_data_53498c", "audio_ble_atts_ctrl_534c8a",
      "audio_ble_atts_msg_534c42", "audio_ble_atts_conn_534aba")),
)


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
    for address, _, words, _ in TABLES:
        assert struct.unpack_from("<4I", payload, address - 0x438000) == words
    dependency_sources = [UPSTREAM / name for name in
                          ("attc_main.c", "atts_ind.c", "atts_main.c")]
    for path, marker in zip(dependency_sources,
                            ("static const attFcnIf_t attcFcnIf",
                             "static const attFcnIf_t attsIndFcnIf",
                             "static const attFcnIf_t attsFcnIf")):
        assert marker in path.read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    expected = [name for _, _, _, names in TABLES for name in names]
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        reloc = elf.get_section_by_name(".rel.rodata")
        assert reloc is not None
        entries = sorted((r["r_offset"], symtab.get_symbol(r["r_info_sym"]).name)
                         for r in reloc.iter_relocations())
        assert entries == [(i * 4, name) for i, name in enumerate(expected)]
        assert len(elf.get_section_by_name(".rodata").data()) == 48
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 104 and len(current) == 112
    assert removed == sorted(name for _, name, _, _ in TABLES)
    assert added == sorted(set(expected) - {"audio_ble_att_noop_4b4eec"})
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATT_INTERFACE_TABLES_785250_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "dependency_sources": [ref(p) for p in dependency_sources],
        "stock_payload_sha256": PAYLOAD_SHA,
        "stock_tables": [{"address": f"0x{address:x}", "symbol": symbol,
                          "pointers": [f"0x{x:08x}" for x in words]}
                         for address, symbol, words, _ in TABLES],
        "unresolved_before": 104, "unresolved_after": 112,
        "removed_imports": removed, "new_imports": added,
        "new_providers": removed,
        "remaining_gate": "Three Cordio ATT interface tables match stock pointer order and pinned upstream initializers. Eleven callback bodies are now explicit imports; other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
