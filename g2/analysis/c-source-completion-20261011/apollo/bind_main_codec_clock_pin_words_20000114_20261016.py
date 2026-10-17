#!/usr/bin/env python3
"""Bind nine exact initialized codec pin words from the Apollo startup record."""
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/codec_i2s_clock_enable_source_candidate/clock_pin_words_20000114.c"
LINKER = SOURCE.with_suffix(".ld")
CALLER = G2 / "components/audio/codec_i2s_clock_enable_source_candidate/enable.c"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR_DECODE = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_codec_clock_enable.py"
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-ble-vendor-itcm-delay-00000040/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-codec-clock-pin-words-20000114"
PIN_ORDER = (("0a", 0x20000114), ("0d", 0x20000118),
             ("0b", 0x2000011c), ("0c", 0x20000120),
             ("1a", 0x20000124), ("1d", 0x20000128),
             ("1e", 0x2000012c), ("1b", 0x20000130),
             ("1c", 0x20000134))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def symbols(path):
    found = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(path)],
                                        text=True).splitlines():
        row = line.split()
        if len(row) == 4 and row[3].startswith("g2_codec_clock_pin_"):
            if row[3] in found:
                raise RuntimeError("codec pin word duplicated")
            found[row[3]] = (int(row[0], 16), int(row[1], 16), row[2])
    return found


def main():
    spec = importlib.util.spec_from_file_location("opencfw_main_low_ram", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decoded = module.decode()
    prior = json.loads(PRIOR_DECODE.read_text())
    if prior["status"] != "PASS" or prior["compared_bytes"] != len(decoded) or \
            prior["decoded_sha256"] != hashlib.sha256(decoded).hexdigest():
        raise RuntimeError("previous stock/C startup decode proof changed")
    expected = {"g2_codec_clock_pin_" + suffix:
                (address, struct.unpack_from("<I", decoded, address - 0x20000000)[0])
                for suffix, address in PIN_ORDER}
    if [value for _, value in expected.values()] != [0x402, 0x409, 0xc09,
            0x409, 0x40a, 0x409, 0x40a, 0x40a, 0x40a]:
        raise RuntimeError("stock codec pin config values changed")
    if not all(name in CALLER.read_text() for name in expected):
        raise RuntimeError("codec clock pin caller changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_VENDOR_ITCM_DELAY_C" or \
            base["unresolved_after"] != 156:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    before = imports(original)
    if sha(original) != base["linked_sha256"] or not set(expected) <= before:
        raise RuntimeError("Apollo Main codec pin imports changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(PYTHON), str(ORACLE)], capture_output=True,
                            text=True, check=True)
    if result.stdout.strip() != "PASS_AUDIO_CODEC_CLOCK_ENABLE 20":
        raise RuntimeError("stock/C codec pin oracle changed")
    oracle_receipt = {"status": "PASS_AUDIO_CODEC_CLOCK_ENABLE", "cases": 20,
                      "script": str(ORACLE.relative_to(ROOT)), "script_sha256": sha(ORACLE),
                      "caller": str(CALLER.relative_to(ROOT)), "caller_sha256": sha(CALLER),
                      "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
                      "prior_decode": str(PRIOR_DECODE.relative_to(ROOT)),
                      "prior_decode_sha256": sha(PRIOR_DECODE),
                      "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                      "stdout": result.stdout.strip()}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "codec-clock-pin-words.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    found = symbols(obj)
    if found != {name: (0, 4, "R") for name in expected}:
        raise RuntimeError("C-owned codec pin symbol extents changed")
    with tempfile.TemporaryDirectory() as directory:
        for suffix, address in PIN_ORDER:
            section = ".data.opencfw.codec.clock_pin_" + suffix
            binary = Path(directory) / (suffix + ".bin")
            subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                            "--only-section=" + section, str(obj), str(binary)], check=True)
            if binary.read_bytes() != decoded[address - 0x20000000:address - 0x20000000 + 4]:
                raise RuntimeError("compiled codec pin word differs from stock RAM")
    placed = OUT / "codec-clock-pin-words-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if symbols(placed) != {name: (address, 4, "R") for name, (address, _) in expected.items()}:
        raise RuntimeError("isolated codec pin placement changed")
    linked = OUT / "apollo-main-codec-clock-pin-words-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != set(expected) or after - before or len(after) != 147:
        raise RuntimeError("unexpected Main codec pin import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_CODEC_CLOCK_PIN_WORDS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "stock_ram_span": ["0x20000114", "0x20000138"],
               "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
               "pin_values": {name: {"address": hex(address), "word": hex(value)}
                              for name, (address, value) in expected.items()},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(expected), "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Nine initialized word values and positions match the official decoded low-RAM record; final C startup copy and whole-image RAM layout remain open.",
                          "The 20-case clock-enable oracle controls pin-function effects, not physical pin behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
