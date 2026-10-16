#!/usr/bin/env python3
"""Transcribe the pinned Apollo Terminal FSM table as C relocations."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_table_650430.c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
TABLE_PIN = "f14e57748e2148f596d9db59a74661cea2c4f28839059aaf42010d17fdd1fad0"
TABLE = 0x650430
BASE = 0x438000


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    data = blob[TABLE-BASE:TABLE-BASE+13*40*8]
    if hashlib.sha256(data).hexdigest() != TABLE_PIN:
        raise RuntimeError("Terminal FSM table bytes changed")
    rows = []
    functions = set()
    active = 0
    for state in range(13):
        cells = []
        for event in range(40):
            offset = (state*40+event)*8
            next_state = int.from_bytes(data[offset:offset+4], "little")
            pointer = int.from_bytes(data[offset+4:offset+8], "little")
            if pointer == 0:
                if next_state != 0:
                    raise RuntimeError("null callback has nonzero transition")
                continue
            if next_state >= 13 or pointer & 1 == 0 or not 0x438000 <= pointer < 0x800000:
                raise RuntimeError("Terminal FSM cell outside observed range")
            target = pointer & ~1
            functions.add(target)
            active += 1
            cells.append(f"        [{event}] = {{{next_state}u, audio_terminal_ui_action_{target:06x}}},")
        rows.append(f"    [{state}] = {{\n" + "\n".join(cells) + "\n    },")
    lines = ["/* Stock Terminal UI FSM table 0x650430, 13 x 40 x 8 bytes.",
             f" * Source slice SHA-256 {TABLE_PIN}; callbacks retain explicit C imports. */",
             "#include <stdint.h>", "",
             "struct audio_terminal_ui_fsm_cell {",
             "    uint32_t next_state;",
             "    int32_t (*action)(uint32_t old_state, uint32_t event_payload);",
             "};",
             "_Static_assert(sizeof(struct audio_terminal_ui_fsm_cell) == 8u, \"stock FSM row ABI\");",
             ""]
    lines.extend(f"extern int32_t audio_terminal_ui_action_{target:06x}(uint32_t, uint32_t);"
                 for target in sorted(functions))
    lines.extend(["", "const struct audio_terminal_ui_fsm_cell audio_terminal_ui_fsm_table[13][40]",
                  "    __attribute__((section(\".rodata.opencfw.terminal.ui_fsm\"), used, aligned(4))) = {",
                  *rows, "};", "",
                  "_Static_assert(sizeof audio_terminal_ui_fsm_table == 4160u, \"stock FSM table extent\");", ""])
    SOURCE.write_text("\n".join(lines))
    print("TRANSCRIBED_TERMINAL_UI_FSM_C", active, len(functions), SOURCE)


if __name__ == "__main__":
    main()
