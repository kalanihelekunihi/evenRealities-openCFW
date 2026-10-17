#!/usr/bin/env python3
"""Pin Main LV level-name RAM access without inventing its initializer."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lvlog.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-level-names-contract"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE = 0x438000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payload = STOCK.read_bytes()[32:]
    source = SOURCE.read_text()
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            "extern const char *audio_uart_lv_level_names[6];" not in source or \
            "if(level<2u||level>=6u) return;" not in source:
        raise RuntimeError("Main LV level-name baseline changed")
    at = lambda address, size: payload[address - BASE:address - BASE + size]
    # LDR literal at 0x44d2f0 targets 0x44d324; signed level indexes words.
    if at(0x44d2f0, 2) != bytes.fromhex("0c48") or \
            at(0x44d2f4, 2) != bytes.fromhex("49b2") or \
            int.from_bytes(at(0x44d324, 4), "little") != 0x20002bec:
        raise RuntimeError("Main native LV level-name read changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS_BOUNDED_MAIN_LV_LEVEL_NAMES_RAM_CONTRACT",
        "stock_package": str(STOCK.relative_to(ROOT)), "stock_package_sha256": sha(STOCK),
        "stock_payload_sha256": PAYLOAD_SHA, "payload_load_base": hex(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "native_literal_address": "0x44d324", "native_table_base": "0x20002bec",
        "native_indexed_access": "0x44d2f0..0x44d2f9",
        "source_accepted_levels": [2, 3, 4, 5], "minimum_pointer_slots": 6,
        "minimum_ram_span_bytes": 24,
        "initializer_authenticated": False, "table_extent_authenticated": False,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The native read and current C guard bound a minimum access span, not a full allocation.",
                   "Neither pointer values nor startup copy ownership were established.",
                   "The source still imports the RAM table; this receipt does not close that import."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], result["minimum_ram_span_bytes"], sha(path))


if __name__ == "__main__":
    main()
