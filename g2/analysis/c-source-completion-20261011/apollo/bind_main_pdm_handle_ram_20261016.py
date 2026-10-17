#!/usr/bin/env python3
"""Bind four PDM handle rows and two pointer cells to C-owned RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCES = [G2 / "components/audio/codec_pdm_acquire_source_candidate/handle_rows_ram_200718c8.c",
           G2 / "components/audio/codec_pdm_init_source_candidate/handle_cells_ram_2007454c.c"]
ACQUIRE = G2 / "components/audio/codec_pdm_acquire_source_candidate/acquire.c"
INIT = G2 / "components/audio/codec_pdm_init_source_candidate/init.c"
ORACLES = [(G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_codec_pdm_lowers.py",
            "PASS_AUDIO_CODEC_PDM_LOWERS {'clock': 15, 'acquire': 48, 'dma': 32}"),
           (G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_codec_pdm_init.py",
            "PASS_AUDIO_CODEC_PDM_INIT 42")]
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-i2s-config-words-20000000/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-pdm-handle-ram"
EXPECTED = {"g2_pdm_handle_rows": (0x200718c8, 128, 0x592648),
            "g2_pdm_alternate_handle": (0x2007454c, 4, 0x57ba48),
            "g2_pdm_production_handle": (0x20074550, 4, 0x57b6d0)}


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
        if len(row) == 4 and row[3] in EXPECTED:
            if row[3] in found:
                raise RuntimeError("PDM handle symbol duplicated")
            found[row[3]] = (int(row[0], 16), int(row[1], 16), row[2])
    return found


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Apollo payload changed")
    for name, (address, _, literal) in EXPECTED.items():
        offset = literal - 0x438000
        if int.from_bytes(payload[offset:offset + 4], "little") != address:
            raise RuntimeError("stock PDM handle literal changed: " + name)
    if "instance * 32u" not in ACQUIRE.read_text() or \
            "instance >= 4u" not in ACQUIRE.read_text() or \
            not all(name in INIT.read_text() for name in
                    ("g2_pdm_alternate_handle", "g2_pdm_production_handle")):
        raise RuntimeError("PDM handle consumer extent changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_I2S_CONFIG_WORDS_C" or \
            base["unresolved_after"] != 141:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    before = imports(original)
    if sha(original) != base["linked_sha256"] or not set(EXPECTED) <= before:
        raise RuntimeError("Apollo Main PDM handle imports changed")
    OUT.mkdir(parents=True, exist_ok=True)
    oracle_rows = []
    for script, output in ORACLES:
        result = subprocess.run([str(PYTHON), str(script)], capture_output=True,
                                text=True, check=True)
        if result.stdout.strip() != output:
            raise RuntimeError("PDM oracle changed: " + script.name)
        oracle_rows.append({"path": str(script.relative_to(ROOT)),
                            "sha256": sha(script), "stdout": output})
    oracle_receipt = {"status": "PASS_PDM_HANDLE_RAM", "acquire_cases": 48,
                      "init_cases": 42, "oracles": oracle_rows,
                      "consumers": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
                                    for p in (ACQUIRE, INIT)]}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    object_paths, placed_paths = [], []
    for source in SOURCES:
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        names = {"g2_pdm_handle_rows"} if source == SOURCES[0] else \
                {"g2_pdm_alternate_handle", "g2_pdm_production_handle"}
        if symbols(obj) != {name: (0, EXPECTED[name][1], "B") for name in names}:
            raise RuntimeError("C-owned PDM handle extent changed")
        placed = OUT / (source.stem + "-placed.o")
        subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(source.with_suffix(".ld")),
                        str(obj), "-o", str(placed)], check=True)
        if symbols(placed) != {name: (EXPECTED[name][0], EXPECTED[name][1], "B")
                               for name in names}:
            raise RuntimeError("isolated PDM handle placement changed")
        object_paths.append(obj)
        placed_paths.append(placed)
    linked = OUT / "apollo-main-pdm-handles-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original),
                    *map(str, object_paths), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != set(EXPECTED) or after - before or len(after) != 138:
        raise RuntimeError("unexpected Main PDM handle import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PDM_HANDLE_RAM_C",
               "sources": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in SOURCES],
               "linkers": [{"path": str(p.with_suffix(".ld").relative_to(ROOT)),
                            "sha256": sha(p.with_suffix(".ld"))} for p in SOURCES],
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "payload_sha256": PAYLOAD_SHA,
               "cells": {name: {"address": hex(address), "bytes": size,
                                 "literal": hex(literal)}
                         for name, (address, size, literal) in EXPECTED.items()},
               "objects": {str(p.relative_to(ROOT)): sha(p) for p in object_paths},
               "placed_objects": {str(p.relative_to(ROOT)): sha(p) for p in placed_paths},
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(EXPECTED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Four 32-byte PDM rows and two pointer cells have C-owned storage and isolated stock-address placement; original initialization and lifetime remain open.",
                          "The 48 acquire and 42 init stock comparisons control hardware children; final RAM map and physical PDM behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
