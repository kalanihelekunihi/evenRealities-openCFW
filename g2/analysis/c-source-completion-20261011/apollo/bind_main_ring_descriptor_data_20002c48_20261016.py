#!/usr/bin/env python3
"""Bind the two exact four-entry display ring descriptor tables."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_descriptor_data_20002c48.c"
LINKER = SOURCE.with_suffix(".ld")
INIT = SOURCE.with_name("display_ring_init.c")
CONSTRUCTOR = SOURCE.with_name("display_ring_constructor.c")
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_uart_ring_init.py"
BASE = G2 / "build/c-firmware/20261016/main-pdm-handle-ram/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-ring-descriptor-data-20002c48"
ROWS = (("primary", 0x20002c48), ("secondary", 0x20002c78))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def symbols(path):
    found = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(path)],
                                        text=True).splitlines():
        row = line.split()
        if len(row) == 4 and row[3].startswith("audio_uart_ring_") and \
                row[3].endswith("_descriptors"):
            found[row[3]] = (int(row[0], 16), int(row[1], 16), row[2])
    return found


def main():
    spec = importlib.util.spec_from_file_location("low_ram", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decoded = module.decode()
    prior = json.loads(PRIOR.read_text())
    if prior["status"] != "PASS" or prior["compared_bytes"] != len(decoded) or \
            prior["decoded_sha256"] != sha_bytes(decoded):
        raise RuntimeError("startup decode proof changed")
    init = INIT.read_text()
    constructor = CONSTRUCTOR.read_text()
    if not all("audio_uart_ring_" + suffix + "_descriptors,4u" in init
               for suffix, _ in ROWS) or "descriptions+(uint32_t)i*12u" not in constructor:
        raise RuntimeError("four-entry descriptor consumer changed")
    base = json.loads(BASE.read_text())
    original = ROOT / base["linked_object"]
    names = {"audio_uart_ring_" + suffix + "_descriptors" for suffix, _ in ROWS}
    before = imports(original)
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_PDM_HANDLE_RAM_C" or \
            base["unresolved_after"] != 138 or sha(original) != base["linked_sha256"] or \
            not names <= before:
        raise RuntimeError("Apollo Main input changed")
    OUT.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(["/tmp/opencfw-oracle-venv/bin/python", str(ORACLE)],
                         check=True, capture_output=True, text=True)
    if run.stdout.strip() != "PASS_AUDIO_UART_RING_INIT 24":
        raise RuntimeError("ring initializer oracle changed")
    oracle_receipt = {"status": "PASS_RING_DESCRIPTOR_CONSUMER",
                      "cases": 24, "oracle": str(ORACLE.relative_to(ROOT)),
                      "oracle_sha256": sha(ORACLE), "stdout": run.stdout.strip(),
                      "init": str(INIT.relative_to(ROOT)), "init_sha256": sha(INIT),
                      "constructor": str(CONSTRUCTOR.relative_to(ROOT)),
                      "constructor_sha256": sha(CONSTRUCTOR),
                      "decoder": str(DECODER.relative_to(ROOT)),
                      "decoder_sha256": sha(DECODER),
                      "prior_decode": str(PRIOR.relative_to(ROOT)),
                      "prior_decode_sha256": sha(PRIOR),
                      "decoded_sha256": sha_bytes(decoded)}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "ring-descriptor-data.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj) != {name: (0, 48, "R") for name in names}:
        raise RuntimeError("compiled descriptor extents changed")
    with tempfile.TemporaryDirectory() as directory:
        for suffix, address in ROWS:
            binary = Path(directory) / (suffix + ".bin")
            subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                            "--only-section=.data.opencfw.ring." + suffix,
                            str(obj), str(binary)], check=True)
            offset = address - 0x20000000
            if binary.read_bytes() != decoded[offset:offset + 48]:
                raise RuntimeError("ring descriptor bytes differ from stock")
    placed = OUT / "ring-descriptor-data-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER), str(obj),
                    "-o", str(placed)], check=True)
    if symbols(placed) != {"audio_uart_ring_" + suffix + "_descriptors":
                           (address, 48, "R") for suffix, address in ROWS}:
        raise RuntimeError("isolated descriptor placement changed")
    linked = OUT / "apollo-main-ring-descriptor-data-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != names or after - before or len(after) != 136:
        raise RuntimeError("unexpected Apollo Main import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_RING_DESCRIPTOR_DATA_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "decoded_sha256": sha_bytes(decoded),
               "tables": {"audio_uart_ring_" + suffix + "_descriptors": {
                   "address": hex(address), "bytes": 48,
                   "stock_sha256": sha_bytes(decoded[address - 0x20000000:
                                                        address - 0x20000000 + 48])}
                   for suffix, address in ROWS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)),
               "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "unresolved_before": len(before),
               "unresolved_after": len(after), "imports_resolved": sorted(names),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Both 48-byte tables match the authenticated initialized low-RAM record and have isolated placements; final startup copy, pointer relocation and full RAM map remain open.",
                          "The 24 ring-init oracle cases do not validate every descriptor-consumer effect or physical display behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


if __name__ == "__main__":
    main()
