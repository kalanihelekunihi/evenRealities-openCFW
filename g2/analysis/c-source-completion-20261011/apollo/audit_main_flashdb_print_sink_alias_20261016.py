#!/usr/bin/env python3
"""Check that the FlashDB sink shares the existing board callback pointer cell."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-audio-dispatch-alias/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-flashdb-print-sink-alias"
OBJ = OUT / "candidate.o"
OWNER = G2 / "components/audio/uart_thread_source_candidate/display_board_callback_444684.c"
READER = G2 / "components/main/flashdb_print_wrapper_candidates_20261010/print_wrapper.c"
LINK = G2 / "analysis/c-source-completion-20261011/apollo/main_flashdb_print_sink_alias_200742f0.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    # Retained literals in the authenticated board callback and print wrapper.
    for address in (0x4448b8, 0x47345c):
        if int.from_bytes(payload[address-0x438000:address-0x438000+4], "little") != 0x200742f0:
            raise RuntimeError(f"stock sink literal at {address:#x} changed")
    if ("audio_uart_stdio_print_char_cell_200742f0" not in OWNER.read_text()
            or "g2_flashdb_print_sink" not in READER.read_text()):
        raise RuntimeError("source ownership or reader changed")
    symbols = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(OBJ)], text=True).splitlines():
        fields = line.split()
        if fields and fields[-1] in ("audio_uart_stdio_print_char_cell_200742f0", "g2_flashdb_print_sink"):
            symbols[fields[-1]] = fields
    if (set(symbols) != {"audio_uart_stdio_print_char_cell_200742f0", "g2_flashdb_print_sink"}
            or symbols["audio_uart_stdio_print_char_cell_200742f0"][0] != symbols["g2_flashdb_print_sink"][0]
            or int(symbols["audio_uart_stdio_print_char_cell_200742f0"][1], 16) != 4
            or undefined(BASE) - undefined(OBJ) != {"g2_flashdb_print_sink"}
            or undefined(OBJ) - undefined(BASE)
            or len(undefined(BASE)) != 128 or len(undefined(OBJ)) != 127):
        raise RuntimeError("print sink alias or import reduction changed")
    oracle = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/main-flashdb-short-log-20261010/verify_flashdb_print.py")], text=True).strip()
    if "96" not in oracle or "PASS" not in oracle:
        raise RuntimeError("print wrapper oracle changed: " + oracle)
    result = {
        "status": "PASS_BOUNDED_MAIN_FLASHDB_PRINT_SINK_SHARED_RAM_ALIAS",
        "stock_payload_sha256": PAYLOAD_SHA,
        "native_sink_cell_address": "0x200742f0",
        "owner_source": str(OWNER.relative_to(ROOT)), "owner_source_sha256": sha(OWNER),
        "reader_source": str(READER.relative_to(ROOT)), "reader_source_sha256": sha(READER),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "source_cell_bytes": 4, "unresolved_before": 128, "unresolved_after": 127,
        "print_wrapper_oracle": oracle,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["Final absolute RAM placement and callback installation remain open.",
                   "The shared print buffer and formatter remain independent lower contracts.",
                   "Isolated wrapper comparison does not establish whole-image or device behavior."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], result["unresolved_after"], sha(receipt))


if __name__ == "__main__":
    main()
