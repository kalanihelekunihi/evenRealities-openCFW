#!/usr/bin/env python3
"""Authenticate and bind the four-node QuickList nanopb descriptor graph."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_pb_descriptor.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-rx-validators/apollo-main-quicklist-rx-validators.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-pb-descriptor"
IMAGE_PATH = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FIELDS = {
    "quicklist_root_fields_6e98a4": (0x6e98a4, 84),
    "quicklist_item_fields_758e2c": (0x758e2c, 36),
    "quicklist_many_fields_704f84": (0x704f84, 68),
    "quicklist_event_fields_7885e0": (0x7885e0, 16),
}
DESCRIPTORS = {
    "audio_quicklist_pb_descriptor": 0x77b02c,
    "quicklist_item_77b044": 0x77b044,
    "quicklist_many_77b05c": 0x77b05c,
    "quicklist_event_77b074": 0x77b074,
}
SUBMSGS = {
    "quicklist_root_submsgs_7885d0": (0x7885d0, 16),
    "quicklist_item_submsgs_78f3a8": (0x78f3a8, 4),
    "quicklist_many_submsgs_78e454": (0x78e454, 8),
    "quicklist_event_submsgs_78f3ac": (0x78f3ac, 4),
}
EDGES = {
    "audio_quicklist_pb_descriptor": [(0, "quicklist_root_fields_6e98a4"), (4, "quicklist_root_submsgs_7885d0")],
    "quicklist_item_77b044": [(0, "quicklist_item_fields_758e2c"), (4, "quicklist_item_submsgs_78f3a8")],
    "quicklist_many_77b05c": [(0, "quicklist_many_fields_704f84"), (4, "quicklist_many_submsgs_78e454")],
    "quicklist_event_77b074": [(0, "quicklist_event_fields_7885e0"), (4, "quicklist_event_submsgs_78f3ac")],
    "quicklist_root_submsgs_7885d0": [(0, "quicklist_item_77b044"), (4, "quicklist_many_77b05c"), (8, "quicklist_event_77b074")],
    "quicklist_many_submsgs_78e454": [(0, "quicklist_item_77b044")],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    image = IMAGE_PATH.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("official Apollo image changed")
    def stock(address, length):
        return image[address-0x438000:address-0x438000+length]
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_pb_descriptor.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in elf.get_section_by_name(".symtab").iter_symbols()}
        ro = elf.get_section_by_name(".rodata").data()
        for name, (address, length) in FIELDS.items():
            symbol = symbols[name]
            if symbol["st_size"] != length or ro[symbol["st_value"]:symbol["st_value"]+length] != stock(address, length):
                raise RuntimeError(f"QuickList field words differ: {name}")
        for name, (address, length) in SUBMSGS.items():
            symbol = symbols[name]
            if symbol["st_size"] != length or ro[symbol["st_value"]+length-4:symbol["st_value"]+length] != bytes(4):
                raise RuntimeError(f"QuickList submessage extent differs: {name}")
            if stock(address+length-4, 4) != bytes(4):
                raise RuntimeError(f"native QuickList submessage terminator differs: {name}")
        for name, address in DESCRIPTORS.items():
            symbol = symbols[name]
            if symbol["st_size"] != 24 or ro[symbol["st_value"]+8:symbol["st_value"]+24] != stock(address+8, 16):
                raise RuntimeError(f"QuickList descriptor metadata differs: {name}")
        reloc = elf.get_section_by_name(".rel.rodata")
        actual = {item["r_offset"]: int.from_bytes(ro[item["r_offset"]:item["r_offset"]+4], "little")
                  for item in reloc.iter_relocations()}
        expected = {symbols[owner]["st_value"]+offset: symbols[target]["st_value"]
                    for owner, edges in EDGES.items() for offset, target in edges}
        if actual != expected:
            raise RuntimeError(f"QuickList descriptor relocation graph differs: {actual}, {expected}")
    for owner, edges in EDGES.items():
        address = DESCRIPTORS.get(owner, SUBMSGS.get(owner, (None,))[0])
        for offset, target in edges:
            target_address = DESCRIPTORS.get(target, FIELDS.get(target, SUBMSGS.get(target, (None,)))[0])
            if int.from_bytes(stock(address+offset, 4), "little") != target_address:
                raise RuntimeError(f"native QuickList edge differs: {owner}+{offset} -> {target}")
    before = names(BASE, "-u")
    if "audio_quicklist_pb_descriptor" not in before:
        raise RuntimeError("QuickList schema import changed")
    linked = OUT / "apollo-main-quicklist-pb-descriptor.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"audio_quicklist_pb_descriptor"} or after-before:
        raise RuntimeError("QuickList schema import delta changed")
    receipt = {
        "status": "PASS_AUTHENTICATED_MAIN_QUICKLIST_PB_DESCRIPTOR_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "official_payload_sha256": hashlib.sha256(image).hexdigest(),
        "field_tables": {name: {"native_address": hex(address), "bytes": length} for name, (address, length) in FIELDS.items()},
        "descriptors": {name: hex(address) for name, address in DESCRIPTORS.items()},
        "authenticated_relocations": len(expected),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Exact field words and graph topology are authenticated, but final ROM placement is open.",
                   "Live nanopb behavior and hardware execution remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
