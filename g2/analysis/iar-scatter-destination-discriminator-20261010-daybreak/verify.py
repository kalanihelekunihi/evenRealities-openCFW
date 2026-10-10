#!/usr/bin/env python3
"""Verify the complete stock IAR scatter table's destination mode bits."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
IMAGE_PATH = ROOT / "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin"
BASE = 0x00438000
TABLE_START = 0x0075D3C8
TABLE_END = 0x0075D410
EXPECTED_SHA256 = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

image = IMAGE_PATH.read_bytes()
assert len(image) == 3_523_364
assert hashlib.sha256(image).hexdigest() == EXPECTED_SHA256

def u32(address):
    return struct.unpack_from("<I", image, address - BASE)[0]

def s32(value):
    return struct.unpack("<i", struct.pack("<I", value))[0]

# The runner's two PC-relative literals bind the complete table extent.
assert 0x005E42D4 + u32(0x005E42D4) == TABLE_START
assert 0x005E42D8 + u32(0x005E42D8) == TABLE_END

# The first callback consumes a zero-fill descriptor stream until a zero length.
zero_handler = TABLE_START + s32(u32(TABLE_START))
assert zero_handler == 0x005FA01F
cursor = TABLE_START + 4
zero_descriptors = []
while True:
    length = u32(cursor)
    cursor += 4
    if length == 0:
        break
    destination_word = u32(cursor)
    cursor += 4
    zero_descriptors.append({
        "length": length,
        "destination_word": f"0x{destination_word:08x}",
        "sb_relative": bool(destination_word & 1),
        "absolute_destination": f"0x{destination_word:08x}" if not destination_word & 1 else None,
    })
assert cursor == 0x0075D3E0

# Three compression rows have a 4-byte handler selector and 12-byte argument block.
compressed_rows = []
while cursor < TABLE_END:
    row = cursor
    handler = row + s32(u32(row))
    args = row + 4
    source_offset, packed_length, destination_word = (u32(args), u32(args + 4), u32(args + 8))
    source = args + source_offset
    source_bytes = packed_length >> 1
    assert handler == 0x0043A11F
    assert BASE <= source <= BASE + len(image)
    assert source + source_bytes <= BASE + len(image)
    compressed_rows.append({
        "row": f"0x{row:08x}",
        "handler_thumb": f"0x{handler:08x}",
        "source_runtime_range": [f"0x{source:08x}", f"0x{source + source_bytes:08x}"],
        "packed_length_word": f"0x{packed_length:08x}",
        "packed_source_bytes": source_bytes,
        "destination_word": f"0x{destination_word:08x}",
        "sb_relative": bool(packed_length & 1),
        "absolute_destination": f"0x{destination_word:08x}" if not packed_length & 1 else None,
    })
    cursor += 16

assert cursor == TABLE_END
assert len(zero_descriptors) == 2
assert len(compressed_rows) == 3
assert not any(x["sb_relative"] for x in zero_descriptors)
assert not any(x["sb_relative"] for x in compressed_rows)
assert [x["absolute_destination"] for x in zero_descriptors] == ["0x20004558", "0x2013be70"]
assert [x["absolute_destination"] for x in compressed_rows] == ["0x00000040", "0x20000000", "0x20080000"]
assert compressed_rows[2]["source_runtime_range"][1] == compressed_rows[1]["source_runtime_range"][0]
assert compressed_rows[1]["source_runtime_range"][1] == compressed_rows[0]["source_runtime_range"][0]
assert compressed_rows[0]["source_runtime_range"][1] == f"0x{BASE + len(image):08x}"

result = {
    "status": "PASS",
    "image": {"path": str(IMAGE_PATH.relative_to(ROOT)), "size": len(image), "sha256": EXPECTED_SHA256, "base": f"0x{BASE:08x}"},
    "table": {"start": f"0x{TABLE_START:08x}", "end_exclusive": f"0x{TABLE_END:08x}", "bytes": TABLE_END - TABLE_START},
    "zero_handler_thumb": f"0x{zero_handler:08x}",
    "zero_descriptors": zero_descriptors,
    "compressed_rows": compressed_rows,
    "summary": {
        "destination_contracts": 5,
        "sb_relative_contracts": 0,
        "absolute_contracts": 5,
        "compressed_inputs_form_contiguous_tail": ["0x0078f6f7", "0x00794324"],
    },
}
(OUT / "evidence.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS: complete authenticated scatter table has five absolute and zero SB-relative destination contracts")
