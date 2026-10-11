"""Decode the authenticated Thumb-1 case table at the legacy command entry."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_box.bin"
EXPECTED = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
data = IMAGE.read_bytes()
assert hashlib.sha256(data).hexdigest() == EXPECTED
def stock(addr, count):
    return data[32 + addr - 0x08000000:32 + addr - 0x08000000 + count]

assert stock(0x0800093c, 8).hex() == "a03a130008f026fc"  # index, BL helper
assert stock(0x08009190, 26).hex() == "30b47446641e2578641cab42" + "00d21d46635d5b00e31830bc1847"
table = stock(0x08000944, 17)
assert table[0] == 15
rows = []
for index, offset in enumerate(table[1:]):
    thumb_target = 0x08000945 + 2 * offset
    rows.append({"opcode": f"0x{0xa0 + index:02x}",
                 "offset_byte": f"0x{offset:02x}",
                 "thumb_target": f"0x{thumb_target:08x}",
                 "code_address": f"0x{thumb_target & ~1:08x}"})
out = {"firmware_sha256": EXPECTED, "helper": "0x08009190",
       "table_address": "0x08000944", "table_hex": table.hex(),
       "maximum_index": table[0], "rows": rows,
       "out_of_range_index": "clamped to index 15 by helper"}
Path(__file__).with_name("switch_table.json").write_text(json.dumps(out, indent=2) + "\n")
print("PASS: 16 authenticated Thumb-1 case targets")
