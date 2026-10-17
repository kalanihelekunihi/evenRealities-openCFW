#!/usr/bin/env python3
"""Authenticate the direct ROM state/event route matrix used at 0x5b1724."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "analysis/c-source-completion-20261011/apollo/main-conversate-ui-action-matrix-20261016.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE = 0x686920


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    if int.from_bytes(payload[0x5b1b20-0x438000:0x5b1b24-0x438000], "little") != BASE:
        raise RuntimeError("UI action route matrix literal changed")
    rows = []
    active = 0
    for state in range(7):
        routes = []
        for event in range(21):
            offset = BASE - 0x438000 + state*0xa8 + event*8
            next_word, handler = struct.unpack_from("<II", payload, offset)
            next_state = next_word & 0xff
            if next_word & 0xffffff00 or next_state >= 7:
                raise RuntimeError(f"route next-state field changed: {state=} {event=}")
            if handler:
                if not (0x438001 <= handler < 0x438000 + len(payload) and handler & 1):
                    raise RuntimeError(f"route handler pointer changed: {state=} {event=}")
                active += 1
            routes.append({"event": event, "next_state": next_state,
                           "handler_pointer": f"0x{handler:x}" if handler else None})
        rows.append({"state": state, "routes": routes})
    raw = payload[BASE-0x438000:BASE-0x438000 + 7*0xa8]
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_MATRIX",
              "stock_payload_sha256": PAYLOAD_SHA, "native_dispatcher": "0x5b1724..0x5b198b",
              "matrix_address": f"0x{BASE:x}", "row_count": 7,
              "events_per_row": 21, "row_stride": 0xa8, "entry_stride": 8,
              "raw_matrix_sha256": hashlib.sha256(raw).hexdigest(),
              "active_routes": active, "rows": rows,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Routes are exact stock ROM data. Handler pointers still target native code and need C bodies; the separate RAM event-name table at 0x20000560 has no authenticated index order."}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], active, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
