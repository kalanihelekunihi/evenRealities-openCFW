#!/usr/bin/env python3
"""Bound the stock UI event-name table without inventing its entry order."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "analysis/c-source-completion-20261011/apollo/main-conversate-ui-event-name-table-20261016.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    base = 0x438000
    if int.from_bytes(payload[0x5b1b00-base:0x5b1b04-base], "little") != 0x20000560:
        raise RuntimeError("UI event-name RAM table address changed")
    if int.from_bytes(payload[0x5b1afc-base:0x5b1b00-base], "little") != 0x785820:
        raise RuntimeError("UI event-name fallback pointer changed")
    candidates = []
    for match in re.finditer(rb"[ -~]{5,}\x00", payload):
        string = match.group()[:-1].decode("ascii")
        if string.startswith("CONVERSATE_UI_EVENT_") and string != "CONVERSATE_UI_EVENT_NUM":
            candidates.append({"address": f"0x{base + match.start():x}", "string": string})
    if len(candidates) != 21 or len({r["string"] for r in candidates}) != 21:
        raise RuntimeError("stock UI event-name candidate set changed")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_NAME_CANDIDATE_SET",
              "stock_payload_sha256": PAYLOAD_SHA,
              "native_lookup": "0x5b16fc..0x5b1715",
              "table_ram_address": "0x20000560", "table_entries": 21,
              "fallback_pointer": "0x785820", "fallback_string": "UNKNOWN_EVENT",
              "candidate_strings": candidates,
              "candidate_set_complete": True,
              "entry_order_authenticated": False,
              "initializer_authenticated": False,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "The 21 stock strings match lookup capacity, but no indexed RAM initializer or pointer order is authenticated. A candidate set does not resolve the table import."}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(candidates), hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
