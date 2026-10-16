#!/usr/bin/env python3
"""Bound the stock Apollo fault lookup using its actual uint8 index semantics."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = ROOT / "g2/build/c-firmware/20261016/fault-lookup-509b48"
BASE = 0x438000
TABLE = 0x6c8e60
BODY = 0x509b48
EXPECTED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def main():
    blob = PAYLOAD.read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED:
        raise RuntimeError("authenticated payload changed")
    body = blob[BODY - BASE:BODY - BASE + 0xb2]
    # 509b68 increments r0, 509b70 truncates to uint8, 509b72 indexes 8-byte rows,
    # 509b78 repeats until equal. Pin instruction bytes so this audit cannot silently
    # claim the same index behavior after a binary change.
    index_slice = blob[0x509b68 - BASE:0x509b7a - BASE]
    if index_slice.hex() != "401c2449a2880300dbb231f833309a42f6d1":
        raise RuntimeError(f"lookup instruction slice changed: {index_slice.hex()}")
    rows = []
    first = {}
    for index in range(256):
        at = TABLE - BASE + 8 * index
        code, reserved, pointer = struct.unpack_from("<HHI", blob, at)
        rows.append({"index": index, "address": TABLE + 8 * index,
                     "code": code, "reserved": reserved, "message_pointer": pointer,
                     "pointer_in_payload": BASE <= pointer < BASE + len(blob)})
        first.setdefault(code, index)
    known = {r["code"] for r in rows[:43]}
    extended = [{"code": code, "first_index": index,
                 "message_pointer": rows[index]["message_pointer"],
                 "pointer_in_payload": rows[index]["pointer_in_payload"]}
                for code, index in sorted(first.items()) if code not in known]
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS_STOCK_FAULT_LOOKUP_256_ROW_BOUNDARY_AUDIT",
        "payload_sha256": digest,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "instruction_slice": index_slice.hex(),
        "table_address": TABLE,
        "index_width_bits": 8,
        "distinct_matchable_codes": len(first),
        "defined_43_row_codes": len(known),
        "additional_matchable_codes": len(extended),
        "nonmatching_codes_cycle_forever": 65536 - len(first),
        "extended_codes": extended,
        "rows": rows,
        "source_complete": False,
        "hardware_proof": False,
        "limits": ["The stock lookup has no failure exit and repeats after 256 rows.",
                   "Rows after the 43 fault entries overlap unrelated payload data; their pointers are not verified as strings.",
                   "Final ROM/RAM placement and whole-image build remain open."],
    }
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(first), len(extended),
          result["nonmatching_codes_cycle_forever"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
