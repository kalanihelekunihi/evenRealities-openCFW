#!/usr/bin/env python3
"""Generate the authenticated reachable Conversate nanopb descriptor graph."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_response_descriptor_775b24.c"
OUT = G2 / "build/c-firmware/20261016/main-conversate-descriptor-775b24/descriptor-map.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE = 0x438000
ROOT_DESCRIPTOR = 0x775b24


def main():
    image = STOCK.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")

    def raw(address, count):
        offset = address - BASE
        if not (0 <= offset <= len(image) - count):
            raise RuntimeError(f"descriptor pointer outside payload: {address:#x}")
        return image[offset:offset+count]

    def word(address):
        return int.from_bytes(raw(address, 4), "little")

    rows = {}
    pending = [ROOT_DESCRIPTOR]
    while pending:
        address = pending.pop(0)
        if address in rows:
            continue
        if len(rows) >= 32:
            raise RuntimeError("unexpected Conversate descriptor graph breadth")
        descriptor = raw(address, 24)
        fields_ptr, sub_ptr, default_ptr, callback_ptr = [word(address + 4*i) for i in range(4)]
        field_count = int.from_bytes(descriptor[16:18], "little")
        required = int.from_bytes(descriptor[18:20], "little")
        largest = int.from_bytes(descriptor[20:22], "little")
        if default_ptr or callback_ptr or descriptor[22:24] != bytes(2) or field_count > 13 or required != 0:
            raise RuntimeError(f"unexpected descriptor metadata: {address:#x}")
        cursor, fields, subcount = fields_ptr, [], 0
        for _ in range(field_count):
            first = word(cursor)
            width = (1, 2, 4, 8)[first & 3]
            fields.extend(word(cursor + 4*j) for j in range(width))
            cursor += 4*width
            if ((first >> 8) & 0xf) in (8, 9):
                subcount += 1
        if field_count == 0:
            if word(fields_ptr) != 0:
                raise RuntimeError(f"nonempty zero-field table: {address:#x}")
            fields = [0]
        children = [word(sub_ptr + 4*i) for i in range(subcount+1)]
        if children[-1] != 0 or len(set(children[:-1])) != len(children)-1:
            raise RuntimeError(f"unterminated or duplicate submessage list: {address:#x}")
        for child in children[:-1]:
            raw(child, 24)
            pending.append(child)
        rows[address] = {
            "descriptor_address": address,
            "descriptor_sha256": hashlib.sha256(descriptor).hexdigest(),
            "fields_address": fields_ptr, "fields": fields,
            "fields_sha256": hashlib.sha256(raw(fields_ptr, 4*len(fields))).hexdigest(),
            "submessages_address": sub_ptr, "submessages": children,
            "submessages_sha256": hashlib.sha256(raw(sub_ptr, 4*len(children))).hexdigest(),
            "field_count": field_count, "required_count": required,
            "largest_tag": largest,
        }
    if len(rows) != 15 or len(rows[ROOT_DESCRIPTOR]["submessages"]) != 12:
        raise RuntimeError("Conversate reachable descriptor graph changed")
    addresses = [ROOT_DESCRIPTOR] + sorted(set(rows) - {ROOT_DESCRIPTOR})
    names = {address: ("audio_conversate_response_descriptor_775b24" if address == ROOT_DESCRIPTOR
                       else f"audio_conversate_descriptor_{address:06x}") for address in addresses}
    lines = ["/* Generated from authenticated Main 0x775b24 nanopb descriptor graph.",
             " * Regenerate with extract_main_conversate_descriptor_775b24_20261016.py.",
             " */", "#include <stddef.h>", "#include <stdint.h>",
             "struct pb_msgdesc_candidate {",
             "    const uint32_t *field_info;",
             "    const struct pb_msgdesc_candidate *const *submsg_info;",
             "    const uint8_t *default_value;",
             "    void *field_callback;",
             "    uint16_t field_count, required_field_count, largest_tag;",
             "};",
             "_Static_assert(sizeof(struct pb_msgdesc_candidate) == 24u,",
             "               \"ARM nanopb descriptor ABI\");",
             "_Static_assert(offsetof(struct pb_msgdesc_candidate, field_count) == 16u,",
             "               \"ARM nanopb field count offset\");", ""]
    for address in addresses:
        lines.append(f"extern const struct pb_msgdesc_candidate {names[address]};")
    lines.append("")
    for address in addresses:
        row = rows[address]
        field_name = f"audio_conversate_fields_{address:06x}"
        sub_name = f"audio_conversate_submessages_{address:06x}"
        fields = row["fields"]
        lines.append(f"const uint32_t {field_name}[{len(fields)}] = {{")
        lines.extend("    " + ", ".join(f"0x{x:08x}u" for x in fields[pos:pos+4]) + ","
                     for pos in range(0, len(fields), 4))
        lines.append("};")
        children = row["submessages"]
        lines.append(f"const struct pb_msgdesc_candidate *const {sub_name}[{len(children)}] = {{")
        lines.extend(f"    &{names[child]}," for child in children[:-1])
        lines.append("    0")
        lines.append("};")
        lines.append(f"const struct pb_msgdesc_candidate {names[address]} = {{")
        lines.append(f"    {field_name}, {sub_name}, 0, 0,")
        lines.append(f"    {row['field_count']}u, {row['required_count']}u, {row['largest_tag']}u")
        lines.extend(["};", ""])
    SOURCE.write_text("\n".join(lines))
    record = {
        "status": "PASS_AUTHENTICATED_MAIN_CONVERSATE_DESCRIPTOR_GRAPH_775B24",
        "stock_payload_sha256": PAYLOAD_SHA,
        "root": hex(ROOT_DESCRIPTOR), "node_count": len(rows),
        "pointer_edge_count": sum(2 + len(row["submessages"])-1 for row in rows.values()),
        "generated_source": str(SOURCE.relative_to(ROOT)),
        "generated_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "descriptors": [{"address": hex(address), "name": names[address],
                         **{key: value for key, value in rows[address].items()
                            if key != "descriptor_address"}} for address in addresses],
        "limits": "Reachable descriptor graph and parsed nanopb field tables only; arbitrary message behavior remains unverified.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(rows), record["pointer_edge_count"],
          hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
