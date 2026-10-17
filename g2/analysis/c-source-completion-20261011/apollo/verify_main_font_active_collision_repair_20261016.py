#!/usr/bin/env python3
"""Prove selected font RAM extents and eliminate the function/data name collision."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261016/main-font-active-collision-repair"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_active_data_20002c00.c"
LOADER = SOURCE.with_name("display_ring_static_init.c")
ACTIVE = SOURCE.with_name("ring_active.c")
LINKER = SOURCE.with_suffix(".ld")
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
PRIOR = G2 / "analysis/audio-dispatch-initializer-closure-2026-10-08/results.json"
MANIFEST = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main/audio/compile-results.json"
ROWS = (("primary", 0x20002c00), ("secondary", 0x20002c24))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(*args):
    return subprocess.check_output(args, text=True)


def names(path, *args):
    return {line.split()[-1] for line in call("arm-none-eabi-nm", *args, str(path)).splitlines()}


def main():
    spec = importlib.util.spec_from_file_location("low_ram", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decoded = module.decode()
    prior = json.loads(PRIOR.read_text())
    if prior["status"] != "PASS" or prior["compared_bytes"] != len(decoded) or \
            prior["decoded_sha256"] != hashlib.sha256(decoded).hexdigest():
        raise RuntimeError("low-RAM startup evidence changed")
    loader = LOADER.read_text()
    if not all("audio_uart_font_" + suffix + "_active" in loader
               for suffix, _ in ROWS) or "audio_uart_ring_active[]" in loader or \
            "secondary[6]" not in loader or "active[6]" not in loader:
        raise RuntimeError("font state access extent or collision repair changed")
    manifest = json.loads(MANIFEST.read_text())
    old = next(row for row in manifest["rows"] if row["source"] == str(LOADER.relative_to(ROOT)))
    old_obj = Path(old["object_path"])
    old_reloc = call("arm-none-eabi-objdump", "-r", str(old_obj))
    if old["object_sha256"] != sha(old_obj) or \
            old_reloc.count("R_ARM_THM_MOVW_ABS_NC  audio_uart_ring_active") < 1:
        raise RuntimeError("original function/data collision evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
             "-Wextra", "-Werror", "-c"]
    data_obj, loader_obj, active_obj = (OUT / name for name in
                                        ("font-active-data.o", "display-ring-static-init.o",
                                         "ring-active.o"))
    for source, target in ((SOURCE, data_obj), (LOADER, loader_obj), (ACTIVE, active_obj)):
        subprocess.run([*flags, str(source), "-o", str(target)], check=True)
    with tempfile.TemporaryDirectory() as directory:
        for suffix, address in ROWS:
            target = Path(directory) / (suffix + ".bin")
            subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                            "--only-section=.data.opencfw.font." + suffix + "_active",
                            str(data_obj), str(target)], check=True)
            if target.read_bytes() != decoded[address - 0x20000000:
                                              address - 0x20000000 + 28]:
                raise RuntimeError("font active data differs from authenticated startup")
    placed = OUT / "font-active-data-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER), str(data_obj),
                    "-o", str(placed)], check=True)
    expected = {"audio_uart_font_" + suffix + "_active": (address, 28, "D")
                for suffix, address in ROWS}
    observed = {}
    for line in call("arm-none-eabi-nm", "-S", str(placed)).splitlines():
        row = line.split()
        if len(row) == 4 and row[3] in expected:
            observed[row[3]] = (int(row[0], 16), int(row[1], 16), row[2])
    if observed != expected:
        raise RuntimeError("font active isolated placement changed")
    composite = OUT / "font-loader-and-active-collision-free.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(loader_obj), str(data_obj),
                    str(active_obj), "-o", str(composite)], check=True)
    if {"audio_uart_font_primary_active", "audio_uart_font_secondary_active",
        "audio_uart_ring_active"} & names(composite, "-u"):
        raise RuntimeError("font data or ring active function unresolved")
    defined = call("arm-none-eabi-nm", "-S", str(composite))
    if " T audio_uart_ring_active" not in defined or \
            " D audio_uart_font_primary_active" not in defined or \
            " D audio_uart_font_secondary_active" not in defined:
        raise RuntimeError("font data/function types not distinct")
    repaired_reloc = call("arm-none-eabi-objdump", "-r", str(loader_obj))
    if "audio_uart_ring_active" in repaired_reloc or \
            not all("audio_uart_font_" + suffix + "_active" in repaired_reloc
                    for suffix, _ in ROWS):
        raise RuntimeError("font loader still targets ring active function")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FONT_ACTIVE_COLLISION_REPAIR_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "loader": str(LOADER.relative_to(ROOT)), "loader_sha256": sha(LOADER),
               "active_function_source": str(ACTIVE.relative_to(ROOT)),
               "active_function_source_sha256": sha(ACTIVE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "prior_decode": str(PRIOR.relative_to(ROOT)),
               "prior_decode_sha256": sha(PRIOR),
               "old_compile_manifest": str(MANIFEST.relative_to(ROOT)),
               "old_compile_manifest_sha256": sha(MANIFEST),
               "old_loader_object": str(old_obj.relative_to(ROOT)),
               "old_loader_object_sha256": sha(old_obj),
               "selected_extents": {"audio_uart_font_" + suffix + "_active": {
                   "address": hex(address), "bytes": 28,
                   "stock_sha256": hashlib.sha256(decoded[address - 0x20000000:
                                                       address - 0x20000000 + 28]).hexdigest()}
                   for suffix, address in ROWS},
               "objects": {str(path.relative_to(ROOT)): sha(path) for path in
                           (data_obj, loader_obj, active_obj, placed, composite)},
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Focused repair is collision-free; the current six-image aggregate still contains the earlier loader object and must be rebuilt from the corrected source.",
                          "Only seven accessed words per state are proven; full original allocation, startup copy, XIP record effects and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))


if __name__ == "__main__":
    main()
