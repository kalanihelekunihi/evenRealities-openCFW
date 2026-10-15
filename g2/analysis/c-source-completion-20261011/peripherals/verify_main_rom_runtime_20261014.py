#!/usr/bin/env python3
"""Rebuild native-matched ROM data and runtime providers in refreshed Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-source-refresh2"
BUILD = OUT / "apollo_main"
BASE_RECEIPT = OUT / "main-smp-closure-receipt.json"
BASE = BUILD / "candidate-smp-closure.o"
FINAL = BUILD / "candidate-rom-runtime.o"
RECEIPT = OUT / "main-rom-runtime-receipt.json"
SOURCES = {
    "radio-strings": G2 / "analysis/c-source-completion-20261011/peripherals/root-rom-radio-strings-round424/radio_strings.c",
    "radio-tail": G2 / "analysis/c-source-completion-20261011/peripherals/root-rom-radio-tail-round425/radio_tail.c",
    "dm-hci-route": G2 / "analysis/c-source-completion-20261011/peripherals/root-dm-hci-route-table-round429/dm_hci_route_table.c",
    "dma-descriptors": G2 / "analysis/c-source-completion-20261011/peripherals/root-dma-descriptors-round433/dma_descriptors.c",
    "memclr4": G2 / "components/main/full_formatter_native_candidate/memclr4.c",
    "norflash-alias": G2 / "components/main/norflash_alias_candidates_20261014/aliases.c",
}
OLD_DATA = {
    "radio-strings": "radio_strings.o",
    "radio-tail": "radio_tail.o",
    "dm-hci-route": "dm_hci_route_table.o",
    "dma-descriptors": "dma_descriptors.o",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_MAIN_SMP_SOURCE_CLOSURE_RELOCATABLE"
    assert base["linked_object_sha256"] == sha(BASE)
    coherent_path = G2 / "build/c-firmware/ble-coherent-dependencies-round1046/receipt.json"
    coherent = json.loads(coherent_path.read_text())
    pinned = {row["path"]: row["sha256"] for row in coherent["objects"]}
    matches = {}
    objects = []
    for label, source in SOURCES.items():
        obj = BUILD / f"refresh-{label}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
        if label in OLD_DATA:
            if label == "dma-descriptors":
                prior = G2 / "build/c-firmware/20261014/main-root-dependencies" / OLD_DATA[label]
            else:
                rel, = [key for key in pinned if key.endswith("/" + OLD_DATA[label])]
                prior = G2 / rel
                assert pinned[rel] == sha(prior), label
            old_bytes = BUILD / f"{label}-old.rodata"
            new_bytes = BUILD / f"{label}-new.rodata"
            for item, data in ((prior, old_bytes), (obj, new_bytes)):
                subprocess.run(["arm-none-eabi-objcopy", "--dump-section",
                                ".rodata=" + str(data), str(item)], check=True)
            assert old_bytes.read_bytes() == new_bytes.read_bytes(), label
            matches[label] = {"prior_object": str(prior.relative_to(ROOT)),
                              "prior_object_sha256": sha(prior),
                              "matched_bytes": len(new_bytes.read_bytes()),
                              "rodata_sha256": sha(new_bytes)}
    stock = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
    assert sha(stock) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    payload = stock.read_bytes()[32:]
    dma = (BUILD / "dma-descriptors-new.rodata").read_bytes()
    assert len(dma) == 480
    assert dma == payload[0x6c0f40 - 0x438000:0x6c1120 - 0x438000]
    norflash_receipt = G2 / "build/c-firmware/20261014/main-root-dependencies/pool-state-norflash-alias-current-receipt.json"
    norflash = json.loads(norflash_receipt.read_text())
    assert norflash["status"] == "PASS_POOLED_MAIN_NORFLASH_ALIAS_C"
    assert norflash["source_sha256"] == sha(SOURCES["norflash-alias"])
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    resolved = sorted(before - after)
    assert len(before) == 618 and len(after) == 581
    assert len(resolved) == 37 and not after - before
    assert {"__aeabi_memclr4", "audio_ble_dma_channels_rom_6c0f40",
            "audio_ble_dm_hci_event_class_map_6e006c",
            "g2_norflash_lock_46f65e", "g2_norflash_unlock_46f674"} <= set(resolved)
    receipt = {
        "status": "PASS_MAIN_ROM_RUNTIME_SOURCE_RELOCATABLE",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "coherent_dependency_receipt": str(coherent_path.relative_to(ROOT)),
        "coherent_dependency_receipt_sha256": sha(coherent_path),
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in SOURCES.values()},
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "rom_data_matches": matches,
        "stock_package_sha256": sha(stock),
        "dma_stock_bytes_matched": 480,
        "norflash_prior_receipt": str(norflash_receipt.relative_to(ROOT)),
        "norflash_prior_receipt_sha256": sha(norflash_receipt),
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": resolved, "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["ROM data bytes match earlier checked objects; only DMA data was directly rechecked against stock in this verifier.",
                  "Other Main imports, final placement, executable behavior, and physical hardware remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
