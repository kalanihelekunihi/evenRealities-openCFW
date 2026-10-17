#!/usr/bin/env python3
"""Bind four exact PDM configuration objects from Apollo initialized RAM."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/codec_pdm_init_source_candidate/pdm_config_words_20000900.c"
LINKER = SOURCE.with_suffix(".ld")
INIT = G2 / "components/audio/codec_pdm_init_source_candidate/init.c"
CONFIGURE = G2 / "components/audio/codec_pdm_configure_source_candidate/configure.c"
START = G2 / "components/audio/codec_pdm_start_source_candidate/start.c"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR_DECODE = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
ORACLES = (("verify_audio_codec_pdm_configure.py", "PASS_AUDIO_CODEC_PDM_CONFIGURE 24"),
           ("verify_audio_codec_pdm_start.py", "PASS_AUDIO_CODEC_PDM_START 144"),
           ("verify_audio_codec_pdm_init.py", "PASS_AUDIO_CODEC_PDM_INIT 42"))
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-codec-clock-pin-words-20000114/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-pdm-config-words-20000900"
ROWS = (("alternate_config", 0x20000900, 28),
        ("alternate_descriptor", 0x2000091c, 12),
        ("production_config", 0x20000928, 28),
        ("production_descriptor", 0x20000944, 12))


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
        if len(row) == 4 and row[3].startswith("g2_pdm_") and \
                row[3] in {"g2_pdm_" + suffix for suffix, _, _ in ROWS}:
            if row[3] in found:
                raise RuntimeError("PDM product object duplicated")
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
    expected = {"g2_pdm_" + suffix: (address, size) for suffix, address, size in ROWS}
    if not all(name in INIT.read_text() for name in expected):
        raise RuntimeError("PDM init caller changed")
    if "c[27]" not in CONFIGURE.read_text() or "d[2]" not in START.read_text():
        raise RuntimeError("PDM config or descriptor accessed extent changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_CODEC_CLOCK_PIN_WORDS_C" or \
            base["unresolved_after"] != 147:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    before = imports(original)
    if sha(original) != base["linked_sha256"] or not set(expected) <= before:
        raise RuntimeError("Apollo Main PDM product imports changed")
    OUT.mkdir(parents=True, exist_ok=True)
    oracle_rows = []
    for name, output in ORACLES:
        script = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([str(PYTHON), str(script)], capture_output=True,
                                text=True, check=True)
        if result.stdout.strip() != output:
            raise RuntimeError("stock/C PDM oracle changed: " + name)
        oracle_rows.append({"script": str(script.relative_to(ROOT)),
                            "script_sha256": sha(script), "stdout": output})
    oracle_receipt = {"status": "PASS_PDM_CONFIG_OBJECTS", "cases": 210,
                      "oracles": oracle_rows,
                      "init": str(INIT.relative_to(ROOT)), "init_sha256": sha(INIT),
                      "configure": str(CONFIGURE.relative_to(ROOT)),
                      "configure_sha256": sha(CONFIGURE),
                      "start": str(START.relative_to(ROOT)), "start_sha256": sha(START),
                      "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
                      "prior_decode": str(PRIOR_DECODE.relative_to(ROOT)),
                      "prior_decode_sha256": sha(PRIOR_DECODE),
                      "decoded_sha256": hashlib.sha256(decoded).hexdigest()}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "pdm-config-words.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj) != {name: (0, size, "D") for name, (_, size) in expected.items()}:
        raise RuntimeError("C-owned PDM product extents changed")
    with tempfile.TemporaryDirectory() as directory:
        for suffix, address, size in ROWS:
            binary = Path(directory) / (suffix + ".bin")
            subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                            "--only-section=.data.opencfw.pdm." + suffix,
                            str(obj), str(binary)], check=True)
            offset = address - 0x20000000
            if binary.read_bytes() != decoded[offset:offset + size]:
                raise RuntimeError("compiled PDM product bytes differ from stock")
    placed = OUT / "pdm-config-words-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if symbols(placed) != {name: (address, size, "D")
                           for name, (address, size) in expected.items()}:
        raise RuntimeError("isolated PDM product placement changed")
    linked = OUT / "apollo-main-pdm-config-words-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != set(expected) or after - before or len(after) != 143:
        raise RuntimeError("unexpected Main PDM import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PDM_CONFIG_WORDS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
               "objects": {name: {"address": hex(address), "bytes": size,
                                    "stock_sha256": hashlib.sha256(decoded[
                                        address - 0x20000000:address - 0x20000000 + size]).hexdigest()}
                           for name, (address, size) in expected.items()},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(expected), "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Four PDM object bytes and isolated addresses match the official initialized low-RAM record; final startup copy and complete RAM map remain open.",
                          "The 210 controlled configure/start/init cases do not establish physical PDM or DMA behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
