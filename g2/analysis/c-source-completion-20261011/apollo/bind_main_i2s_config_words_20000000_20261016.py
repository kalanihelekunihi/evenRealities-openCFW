#!/usr/bin/env python3
"""Bind selected I2S configuration bytes from authenticated Apollo startup RAM."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/codec_i2s_init_source_candidate/i2s_config_words_20000000.c"
LINKER = SOURCE.with_suffix(".ld")
INIT = G2 / "components/audio/codec_i2s_init_source_candidate/init.c"
CONFIGURE = G2 / "components/audio/codec_i2s_configure_source_candidate/configure.c"
DMA = G2 / "components/audio/codec_i2s_dma_configure_source_candidate/dma.c"
START = G2 / "components/audio/codec_i2s_start_candidate/start.c"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR_DECODE = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
ORACLES = (("verify_audio_codec_i2s_configure.py", "PASS_AUDIO_CODEC_I2S_CONFIGURE_NONFLOAT 192"),
           ("verify_audio_codec_i2s_dma.py", "PASS_AUDIO_CODEC_I2S_DMA 60"),
           ("verify_audio_codec_i2s_start.py", "PASS_AUDIO_CODEC_I2S_START 192"))
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-pdm-config-words-20000900/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-i2s-config-words-20000000"
ROWS = (("g2_codec_i2s_config_base", 0x20000000, 40),
        ("g2_codec_i2s_dma_descriptor", 0x20000740, 24))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def symbols(path):
    found = {}
    names = {name for name, _, _ in ROWS}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(path)],
                                        text=True).splitlines():
        row = line.split()
        if len(row) == 4 and row[3] in names:
            if row[3] in found:
                raise RuntimeError("I2S data symbol duplicated")
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
    if not all(name in INIT.read_text() for name, _, _ in ROWS) or \
            "config + 0x24u" not in DMA.read_text() or \
            "d[5]" not in DMA.read_text() or \
            "pointer(c, 0x20u)" not in CONFIGURE.read_text() or \
            "options[1]" not in START.read_text():
        raise RuntimeError("selected I2S consumer extent changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_PDM_CONFIG_WORDS_C" or \
            base["unresolved_after"] != 143:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    before = imports(original)
    names = {name for name, _, _ in ROWS}
    if sha(original) != base["linked_sha256"] or not names <= before:
        raise RuntimeError("Apollo Main I2S config imports changed")
    OUT.mkdir(parents=True, exist_ok=True)
    oracle_rows = []
    for name, output in ORACLES:
        script = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([str(PYTHON), str(script)], capture_output=True,
                                text=True, check=True)
        if result.stdout.strip() != output:
            raise RuntimeError("stock/C I2S oracle changed: " + name)
        oracle_rows.append({"script": str(script.relative_to(ROOT)),
                            "script_sha256": sha(script), "stdout": output})
    oracle_receipt = {"status": "PASS_I2S_CONFIG_OBJECTS", "cases": 444,
                      "oracles": oracle_rows,
                      "consumers": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
                                    for p in (INIT, CONFIGURE, DMA, START)],
                      "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
                      "prior_decode": str(PRIOR_DECODE.relative_to(ROOT)),
                      "prior_decode_sha256": sha(PRIOR_DECODE),
                      "decoded_sha256": hashlib.sha256(decoded).hexdigest()}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "i2s-config-words.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj) != {name: (0, size, "D") for name, _, size in ROWS}:
        raise RuntimeError("C-owned I2S object extents changed")
    with tempfile.TemporaryDirectory() as directory:
        for name, address, size in ROWS:
            section = ".data.opencfw.codec." + name.removeprefix("g2_codec_")
            binary = Path(directory) / (name + ".bin")
            subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                            "--only-section=" + section, str(obj), str(binary)], check=True)
            offset = address - 0x20000000
            if binary.read_bytes() != decoded[offset:offset + size]:
                raise RuntimeError("compiled I2S product bytes differ from stock")
    placed = OUT / "i2s-config-words-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if symbols(placed) != {name: (address, size, "D") for name, address, size in ROWS}:
        raise RuntimeError("isolated I2S product placement changed")
    linked = OUT / "apollo-main-i2s-config-words-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != names or after - before or len(after) != 141:
        raise RuntimeError("unexpected Main I2S import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_I2S_CONFIG_WORDS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
               "objects": {name: {"address": hex(address), "bytes": size,
                                    "stock_sha256": hashlib.sha256(decoded[
                                        address - 0x20000000:address - 0x20000000 + size]).hexdigest()}
                           for name, address, size in ROWS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(names), "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The selected C graph accesses 40 configuration bytes and six DMA words, all byte-matched to the official initialized RAM record. Original full allocation extent remains unproven.",
                          "The 444 controlled cases exclude float paths of configure and real I2S/DMA hardware effects; final startup copy and RAM map remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
