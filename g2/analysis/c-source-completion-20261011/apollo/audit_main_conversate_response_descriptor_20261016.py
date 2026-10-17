#!/usr/bin/env python3
"""Authenticate Conversate response C and its complete reachable nanopb graph."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
RESPONSE = BASE / "main-conversate-response-5b200e"
DESCRIPTOR = BASE / "main-conversate-descriptor-775b24"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    def stock(address, length):
        offset = address - 0x438000
        return image[offset:offset+length]
    prior = BASE / "main-conversate-mutex-init-5b0120/candidate.o"
    response_obj = RESPONSE / "candidate.o"
    descriptor_obj = DESCRIPTOR / "candidate.o"
    before, middle, after = [imports(path) for path in (prior, response_obj, descriptor_obj)]
    if len(before) != 123 or len(middle) != 123 or len(after) != 122 or before - middle != {"audio_conversate_respond_5b200e"} or middle - before != {"audio_conversate_response_descriptor_775b24"} or middle - after != {"audio_conversate_response_descriptor_775b24"} or after - middle:
        raise RuntimeError("Conversate response/descriptor import frontier changed")
    oracle_path = RESPONSE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_RESPONSE_5B200E_C" or oracle["cases"] != 120 or oracle["source_sha256"] != sha(source) or oracle["stock_payload_sha256"] != PAYLOAD_SHA:
        raise RuntimeError("Conversate response oracle changed")
    map_path = DESCRIPTOR / "descriptor-map.json"
    descriptor_map = json.loads(map_path.read_text())
    descriptor_source = ROOT / descriptor_map["generated_source"]
    if descriptor_map["status"] != "PASS_AUTHENTICATED_MAIN_CONVERSATE_DESCRIPTOR_GRAPH_775B24" or descriptor_map["stock_payload_sha256"] != PAYLOAD_SHA or descriptor_map["node_count"] != 15 or descriptor_map["pointer_edge_count"] != 44 or descriptor_map["generated_source_sha256"] != sha(descriptor_source):
        raise RuntimeError("Conversate descriptor graph map changed")
    raw_obj = DESCRIPTOR / "descriptor.o"
    with raw_obj.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        symbols = {sym.name: sym for sym in symtab.iter_symbols()}
        ro = elf.get_section_by_name(".rodata").data()
        reloc = elf.get_section_by_name(".rel.rodata")
        actual_edges = {item["r_offset"]: symtab.get_symbol(item["r_info_sym"]).name
                        for item in reloc.iter_relocations()}
        expected_edges = {}
        for row in descriptor_map["descriptors"]:
            address = int(row["address"], 16)
            suffix = f"{address:06x}"
            field_name = f"audio_conversate_fields_{suffix}"
            sub_name = f"audio_conversate_submessages_{suffix}"
            desc_name = row["name"]
            for name, native_address, length in (
                (field_name, row["fields_address"], len(row["fields"])*4),
                (sub_name, row["submessages_address"], len(row["submessages"])*4),
            ):
                symbol = symbols[name]
                actual = bytearray(ro[symbol["st_value"]:symbol["st_value"]+length])
                expected = bytearray(stock(native_address, length))
                if name == sub_name:
                    for offset, child in enumerate(row["submessages"][:-1]):
                        child_name = ("audio_conversate_response_descriptor_775b24"
                                      if child == 0x775b24 else f"audio_conversate_descriptor_{child:06x}")
                        expected_edges[symbol["st_value"]+offset*4] = child_name
                        actual[offset*4:offset*4+4] = bytes(4)
                        expected[offset*4:offset*4+4] = bytes(4)
                if symbol["st_size"] != length or actual != expected:
                    raise RuntimeError(f"Conversate field/submessage table differs: {name}")
            descriptor_symbol = symbols[desc_name]
            descriptor_bytes = bytearray(ro[descriptor_symbol["st_value"]:descriptor_symbol["st_value"]+24])
            native_bytes = bytearray(stock(address, 24))
            for offset, target in ((0, field_name), (4, sub_name)):
                expected_edges[descriptor_symbol["st_value"]+offset] = target
                descriptor_bytes[offset:offset+4] = bytes(4)
                native_bytes[offset:offset+4] = bytes(4)
            if descriptor_symbol["st_size"] != 24 or descriptor_bytes != native_bytes:
                raise RuntimeError(f"Conversate descriptor metadata differs: {desc_name}")
        if actual_edges != expected_edges or len(actual_edges) != 44:
            raise RuntimeError("Conversate C descriptor relocation graph differs")
    prior_receipt = json.loads((BASE / "main-conversate-mutex-init-5b0120/receipt.json").read_text())
    expected_sections = {name: (int(row["address"], 16), row["size"])
                         for name, row in prior_receipt["fixed_ram_sections"].items()}
    expected_sections.update({
        ".g2_conversate_response_frame_200f4808": (0x200f4808, 4012),
        ".g2_conversate_response_encoded_2037c2a0": (0x2037c2a0, 256),
    })
    with descriptor_obj.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in expected_sections.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
    record = {
        "status": "PASS_AUTHENTICATED_MAIN_CONVERSATE_RESPONSE_DESCRIPTOR_C",
        "prior_candidate": ref(prior), "response_candidate": ref(response_obj),
        "candidate_object": ref(descriptor_obj),
        "response_source": ref(source),
        "response_ram_source": ref(G2 / "components/audio/uart_thread_source_candidate/conversate_response_ram_20261016.c"),
        "response_oracle": ref(oracle_path), "response_oracle_cases": 120,
        "descriptor_source": ref(descriptor_source),
        "descriptor_map": ref(map_path), "descriptor_object": ref(raw_obj),
        "descriptor_nodes": 15, "authenticated_pointer_edges": 44,
        "response_native_body": "0x5b200e..0x5b212d", "response_native_bytes": 288,
        "unresolved_before": 123, "unresolved_response": 123,
        "unresolved_after": 122,
        "response_removed_import": "audio_conversate_respond_5b200e",
        "descriptor_removed_import": "audio_conversate_response_descriptor_775b24",
        "fixed_ram_sections": {name: {"address": hex(address), "size": size,
                                     "type": "SHT_NOBITS"} for name, (address, size) in expected_sections.items()},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Conversate receive, data handler, context and reply-status RAM remain, alongside Main payload coverage.",
    }
    output = DESCRIPTOR / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
