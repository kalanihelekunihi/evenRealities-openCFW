#!/usr/bin/env python3
"""Emit exact C route data while keeping every native handler unresolved."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
EVIDENCE = G2 / "analysis/c-source-completion-20261011/apollo/main-conversate-ui-action-matrix-20261016.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_action_matrix_686920.c"
BASE = 0x686920


def main():
    record = json.loads(EVIDENCE.read_text())
    payload = STOCK.read_bytes()[32:]
    raw = payload[BASE-0x438000:BASE-0x438000 + 7*0xa8]
    if (record["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_MATRIX" or
            record["raw_matrix_sha256"] != hashlib.sha256(raw).hexdigest() or
            len(record["rows"]) != 7):
        raise RuntimeError("stock route evidence changed")
    handlers = sorted({int(route["handler_pointer"], 16) for row in record["rows"]
                       for route in row["routes"] if route["handler_pointer"]})
    lines = ["/* Exact stock route matrix at 0x686920; native handler bodies remain unresolved. */",
             "#include <stdint.h>", "",
             "typedef uint32_t (*audio_conversate_ui_action_handler)(uint32_t, uint32_t);",
             "typedef struct {",
             "    uint8_t next_state;",
             "    uint8_t reserved[3];",
             "    audio_conversate_ui_action_handler handler;",
             "} audio_conversate_ui_route;", ""]
    for address in handlers:
        lines.append(f"extern uint32_t audio_conversate_ui_route_{address & ~1:06x}(uint32_t, uint32_t);")
    lines += ["", "__attribute__((used, section(\".g2_conversate_ui_action_matrix_686920\")))",
              "const audio_conversate_ui_route audio_conversate_ui_action_matrix_686920[7][21] = {"]
    for state, row in enumerate(record["rows"]):
        if row["state"] != state or len(row["routes"]) != 21:
            raise RuntimeError("route row shape changed")
        lines.append(f"    {{ /* state {state} */")
        for event, route in enumerate(row["routes"]):
            if route["event"] != event:
                raise RuntimeError("route event order changed")
            next_state = route["next_state"]
            handler = route["handler_pointer"]
            actual_next, actual_ptr = struct.unpack_from("<II", raw, state*0xa8 + event*8)
            if actual_next != next_state or actual_ptr != (int(handler, 16) if handler else 0):
                raise RuntimeError(f"stock route mismatch at {state=} {event=}")
            pointer = f"audio_conversate_ui_route_{actual_ptr & ~1:06x}" if actual_ptr else "0"
            lines.append(f"        {{{next_state}u, {{0u, 0u, 0u}}, {pointer}}}, /* event {event} */")
        lines.append("    },")
    lines += ["};", "", "_Static_assert(sizeof(audio_conversate_ui_action_matrix_686920) == 1176u,",
              "               \"seven native 21-event route rows\");", ""]
    OUT.write_text("\n".join(lines))
    print("PASS_GENERATED_MAIN_CONVERSATE_UI_ACTION_MATRIX_C", len(handlers),
          hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
