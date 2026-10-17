#!/usr/bin/env python3
"""Bind the stock initialized accessed extent of Main's locale dispatch RAM."""
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_dispatch_data_200044c0.c"
LINKER = SOURCE.with_suffix(".ld")
CONSUMER = SOURCE.with_name("display_ring_locale_dispatch.c")
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
BASE = G2 / "build/c-firmware/20261016/main-combined-ram-settings-font-final-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-locale-dispatch-data-200044c0"
NAME = "audio_uart_ring_locale_dispatch_200044c0"
ADDRESS = 0x200044c0
SIZE = 44


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def symbol(path):
    rows = [line.split() for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
            if line.endswith(" " + NAME)]
    if len(rows) != 1 or len(rows[0]) != 4:
        raise RuntimeError("locale symbol missing/duplicated")
    row = rows[0]
    return int(row[0], 16), int(row[1], 16), row[2]


def main():
    spec = importlib.util.spec_from_file_location("main_low_ram", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decoded = module.decode()
    prior = json.loads(PRIOR.read_text())
    if prior["status"] != "PASS" or prior["compared_bytes"] != len(decoded) or \
            prior["decoded_sha256"] != hashlib.sha256(decoded).hexdigest():
        raise RuntimeError("authenticated low-RAM decode proof changed")
    consumer = CONSUMER.read_text()
    if NAME not in consumer or "locale_method(0x20u)" not in consumer or \
            "locale_method(0x28u)" not in consumer:
        raise RuntimeError("locale consumer selected extent changed")
    base = json.loads(BASE.read_text())
    original = ROOT / base["linked_object"]
    before = names(original, "-u")
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_FINAL_REPLAY_C" or \
            base["unresolved_after"] != 135 or sha(original) != base["linked_sha256"] or \
            NAME not in before:
        raise RuntimeError("Apollo Main locale input changed")
    expected = decoded[ADDRESS - 0x20000000:ADDRESS - 0x20000000 + SIZE]
    callbacks = {hex(offset): hex(struct.unpack_from("<I", expected, offset)[0])
                 for offset in (0x20, 0x28)}
    if callbacks != {"0x20": "0x4d4385", "0x28": "0x4d4399"}:
        raise RuntimeError("stock locale callback slots changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "locale-dispatch-data.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbol(obj) != (0, SIZE, "D"):
        raise RuntimeError("compiled locale extent changed")
    with tempfile.TemporaryDirectory() as directory:
        binary = Path(directory) / "locale.bin"
        subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                        "--only-section=.data.opencfw.ring.locale_dispatch",
                        str(obj), str(binary)], check=True)
        if binary.read_bytes() != expected:
            raise RuntimeError("compiled locale bytes differ from stock")
    placed = OUT / "locale-dispatch-data-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER), str(obj),
                    "-o", str(placed)], check=True)
    if symbol(placed) != (ADDRESS, SIZE, "D"):
        raise RuntimeError("isolated locale placement changed")
    linked = OUT / "apollo-main-locale-dispatch-data-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before or len(after) != 134:
        raise RuntimeError("unexpected Apollo Main locale import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_DISPATCH_DATA_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "consumer": str(CONSUMER.relative_to(ROOT)),
               "consumer_sha256": sha(CONSUMER),
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "prior_decode": str(PRIOR.relative_to(ROOT)),
               "prior_decode_sha256": sha(PRIOR),
               "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
               "selected_address": hex(ADDRESS), "selected_bytes": SIZE,
               "stock_selected_sha256": hashlib.sha256(expected).hexdigest(),
               "callback_slots": callbacks,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)),
               "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [NAME], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Only the 44 bytes through the two accessed callback slots match authenticated initialized RAM; the full native table allocation and runtime mutation remain open.",
                          "Callback addresses are stock Thumb pointer values, not C callback implementations. Final relocation, startup copy and behavior are open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
