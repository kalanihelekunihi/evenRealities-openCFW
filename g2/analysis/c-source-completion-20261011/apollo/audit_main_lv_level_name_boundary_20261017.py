#!/usr/bin/env python3
"""Pin the five-name LVGL table and native level-five adjacent read."""
import hashlib
import json
import struct
from pathlib import Path

from decode_main_low_ram_20261016 import PACKAGE, PAYLOAD_SHA, decode

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main-lv-level-name-boundary-20261017.json"


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("authenticated Main payload changed")
    ram = decode()
    words = struct.unpack_from("<6I", ram, 0x2bec)
    if words != (0x78dc34, 0x78dc3c, 0x78dc44, 0x78dc4c, 0x78dc54, 0x4b26a5):
        raise RuntimeError("LVGL level-name boundary changed")
    names = []
    for address in words[:5]:
        offset = address - 0x438000
        names.append(payload[offset:payload.index(0, offset)+1].decode("ascii"))
    if names != ["Trace\x00", "Info\x00", "Warn\x00", "Error\x00", "User\x00"]:
        raise RuntimeError("LVGL level names changed")
    # 0x44d26e checks signed level >=6, 0x44d276 checks signed level <2;
    # 0x44d2f6 indexes RAM 0x20002bec by signed level*4.
    first = payload[0x44d26c-0x438000:0x44d27a-0x438000]
    lookup = payload[0x44d2f0-0x438000:0x44d2fa-0x438000]
    if first.hex() != "40b2062851da300040b202284ddb" or \
       lookup.hex() != "0c48310049b250f82130":
        raise RuntimeError("native level guard or lookup changed")
    record = {"status": "PASS_MAIN_LV_LEVEL_NAME_BOUNDARY_EVIDENCE",
              "stock_payload_sha256": PAYLOAD_SHA,
              "decoded_low_ram_sha256": hashlib.sha256(ram).hexdigest(),
              "table_base": "0x20002bec", "native_lookup": "0x44d2f0..0x44d2f9",
              "admitted_signed_levels": [2, 3, 4, 5],
              "first_five_names": [name[:-1] for name in names],
              "sixth_word_address": "0x20002c00", "sixth_word": "0x004b26a5",
              "source_owner_bound": False,
              "remaining_gate": "Level 5 reads the adjacent font-record word, not a sixth string pointer. Preserve native layout or establish a proven correction before binding the import; runtime use of level 5 is unverified.",
              "source_complete": False, "flashable": False, "hardware_proof": False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
