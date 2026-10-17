#!/usr/bin/env python3
"""Authenticate the two-node stock SyncInfo nanopb graph and bind its C owner."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/sync_info_pb_descriptor_77c1cc.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = G2 / "build/c-firmware/20261016/main-sync-info-response-471ee8/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-sync-info-descriptor-77c1cc"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_sync_info_response_471ee8.ld"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SPANS = {
    "audio_sync_info_root_fields_783c94": (0x783c94, 20),
    "audio_sync_info_child_fields_78c4c4": (0x78c4c4, 12),
    "audio_sync_info_root_submsgs_78e9c4": (0x78e9c4, 8),
    "audio_sync_info_child_submsgs_78f404": (0x78f404, 4),
    "audio_sync_info_child_descriptor_77c1b4": (0x77c1b4, 24),
    "audio_sync_info_pb_descriptor_77c1cc": (0x77c1cc, 24),
}
EDGES = {
    ("audio_sync_info_root_submsgs_78e9c4", 0): "audio_sync_info_child_descriptor_77c1b4",
    ("audio_sync_info_child_descriptor_77c1b4", 0): "audio_sync_info_child_fields_78c4c4",
    ("audio_sync_info_child_descriptor_77c1b4", 4): "audio_sync_info_child_submsgs_78f404",
    ("audio_sync_info_pb_descriptor_77c1cc", 0): "audio_sync_info_root_fields_783c94",
    ("audio_sync_info_pb_descriptor_77c1cc", 4): "audio_sync_info_root_submsgs_78e9c4",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()})


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def main():
    image = STOCK.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Main payload changed")
    def stock(address, length):
        return image[address - 0x438000:address - 0x438000 + length]
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "descriptor.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {sym.name: sym for sym in elf.get_section_by_name(".symtab").iter_symbols()}
        ro = elf.get_section_by_name(".rodata").data()
        reloc = elf.get_section_by_name(".rel.rodata")
        if reloc is None:
            raise RuntimeError("descriptor has no relocation graph")
        actual_offsets = {item["r_offset"] for item in reloc.iter_relocations()}
        expected_offsets = {symbols[owner]["st_value"] + offset for owner, offset in EDGES}
        if actual_offsets != expected_offsets or len(actual_offsets) != 5:
            raise RuntimeError("C descriptor pointer graph changed")
        for name, (address, length) in SPANS.items():
            symbol = symbols[name]
            actual = bytearray(ro[symbol["st_value"]:symbol["st_value"] + length])
            expected = bytearray(stock(address, length))
            if symbol["st_size"] != length:
                raise RuntimeError(f"descriptor span size changed: {name}")
            for (owner, offset), target in EDGES.items():
                if owner == name:
                    actual[offset:offset+4] = bytes(4)
                    expected[offset:offset+4] = bytes(4)
                    if int.from_bytes(stock(address + offset, 4), "little") != SPANS[target][0]:
                        raise RuntimeError(f"stock descriptor pointer changed: {owner}+{offset}")
            if actual != expected:
                raise RuntimeError(f"descriptor non-pointer bytes differ: {name}")
        for item in reloc.iter_relocations():
            owner, offset = next((owner, offset) for (owner, offset) in EDGES
                                 if symbols[owner]["st_value"] + offset == item["r_offset"])
            target = EDGES[(owner, offset)]
            symbol = elf.get_section_by_name(".symtab").get_symbol(item["r_info_sym"])
            if symbol.name != target:
                raise RuntimeError(f"descriptor relocation target differs: {owner}+{offset}")
    before = set(imports(BASE))
    candidate = OUT / "candidate.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER.relative_to(ROOT)),
                    "-o", str(candidate), str(BASE), str(obj)], cwd=ROOT, check=True)
    after = set(imports(candidate))
    if len(before) != 121 or len(after) != 120 or before - after != {"audio_sync_info_pb_descriptor_77c1cc"} or after - before:
        raise RuntimeError("descriptor import delta changed")
    record = {
        "status": "PASS_AUTHENTICATED_MAIN_SYNC_INFO_PB_DESCRIPTOR_C",
        "stock_payload_sha256": PAYLOAD_SHA,
        "source": ref(SOURCE), "object": ref(obj), "prior_candidate": ref(BASE),
        "candidate_object": ref(candidate), "linker_script": ref(LINKER),
        "spans": {name: {"stock_address": hex(addr), "bytes": length} for name, (addr, length) in SPANS.items()},
        "authenticated_pointer_edges": len(EDGES),
        "unresolved_before": 121, "unresolved_after": 120,
        "removed_imports": ["audio_sync_info_pb_descriptor_77c1cc"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Validate arbitrary SyncInfo protobuf behavior and reconstruct remaining Main imports and payload.",
    }
    output = OUT / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
