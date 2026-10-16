#!/usr/bin/env python3
"""Pin the EvenAI nanopb descriptor graph without inferring field extents."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000

def bytes_at(address, count):
    offset = address - BASE
    assert 0 <= offset <= len(IMAGE) - count
    return IMAGE[offset:offset + count]

def word(address):
    return int.from_bytes(bytes_at(address, 4), "little")

root = 0x777144
descriptors = []
field_tables = []
submsg_tables = []
for index in range(12):
    address = root + index * 24
    raw = bytes_at(address, 24)
    ptrs = [word(address + 4 * i) for i in range(4)]
    field_count = int.from_bytes(raw[16:18], "little")
    required = int.from_bytes(raw[18:20], "little")
    largest = int.from_bytes(raw[20:22], "little")
    assert raw[22:24] == b"\x00\x00"
    assert ptrs[2:] == [0, 0]
    assert 0 < field_count <= 13 and required == 0
    assert BASE <= ptrs[0] < BASE + len(IMAGE)
    assert BASE <= ptrs[1] < BASE + len(IMAGE)
    cursor = ptrs[0]
    words = []
    submessages = 0
    for _ in range(field_count):
        first = word(cursor)
        width = (1, 2, 4, 8)[first & 3]
        words.extend(word(cursor + 4 * j) for j in range(width))
        cursor += 4 * width
        if ((first >> 8) & 0xf) in (8, 9):
            submessages += 1
    subwords = [word(ptrs[1] + 4 * j) for j in range(submessages + 1)]
    assert subwords[-1] == 0
    field_tables.append(words)
    submsg_tables.append(subwords)
    descriptors.append({"address": f"0x{address:08x}",
                        "raw_sha256": hashlib.sha256(raw).hexdigest(),
                        "field_info": f"0x{ptrs[0]:08x}",
                        "submsg_info": f"0x{ptrs[1]:08x}",
                        "default_value": 0,
                        "field_callback": 0,
                        "field_count": field_count,
                        "required_field_count": required,
                        "largest_tag": largest,
                        "field_info_word_count": len(words),
                        "field_info_sha256": hashlib.sha256(bytes_at(ptrs[0], 4 * len(words))).hexdigest(),
                        "submsg_count": submessages})
assert descriptors[0]["field_count"] == 13
children = [word(0x733eb4 + 4 * i) for i in range(12)]
assert children == [root + 24 * i for i in range(1, 12)] + [0]
assert submsg_tables[0] == children
assert all(row == [0] for row in submsg_tables[1:])

source = G2 / "components/audio/uart_thread_source_candidate/even_ai_descriptor_777144.c"
lines = ["/* Authenticated Apollo main nanopb EvenAI descriptor graph at 0x777144.",
         " * Regenerate with extract_main_even_ai_descriptor_777144_20261016.py.",
         " */", '#include "pb.h"', ""]
for index, words in enumerate(field_tables):
    lines.append(f"static const uint32_t even_ai_fields_{index}[{len(words)}] = {{")
    lines.extend("    " + ", ".join(f"0x{x:08x}u" for x in words[pos:pos+4]) + ","
                 for pos in range(0, len(words), 4))
    lines.append("};")
lines.extend(["", "static const pb_msgdesc_t *const even_ai_no_submessages[1] = {0};"])
for index in range(1, 12):
    lines.append(f"static const pb_msgdesc_t even_ai_descriptor_{index} = {{")
    row = descriptors[index]
    lines.append(f"    even_ai_fields_{index}, even_ai_no_submessages, 0, 0,")
    lines.append(f"    {row['field_count']}u, {row['required_field_count']}u, {row['largest_tag']}u")
    lines.append("};")
lines.append("static const pb_msgdesc_t *const even_ai_root_submessages[12] = {")
lines.extend(f"    &even_ai_descriptor_{i}," for i in range(1, 12))
lines.extend(["    0", "};", "const pb_msgdesc_t audio_even_ai_decode_fields = {",
              "    even_ai_fields_0, even_ai_root_submessages, 0, 0,",
              "    13u, 0u, 13u", "};", ""])
source.write_text("\n".join(lines))

output = G2 / "build/c-firmware/20261016/main-even-ai-descriptor-777144/descriptor-map.json"
output.parent.mkdir(parents=True, exist_ok=True)
record = {"status": "PASS_AUTHENTICATED_MAIN_EVEN_AI_DESCRIPTOR_GRAPH_777144",
          "stock_payload_sha256": IMAGE_SHA,
          "root": f"0x{root:08x}",
          "generated_source": str(source.relative_to(ROOT)),
          "generated_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
          "descriptors": descriptors,
          "root_children": [f"0x{x:08x}" for x in children[:-1]],
          "limits": "24-byte descriptor records and root child-pointer graph only; field-info table extents and decoded message layout remain unproven"}
output.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
print(record["status"], len(descriptors), hashlib.sha256(output.read_bytes()).hexdigest())
