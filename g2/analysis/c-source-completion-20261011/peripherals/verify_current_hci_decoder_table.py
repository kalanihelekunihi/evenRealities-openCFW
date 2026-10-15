#!/usr/bin/env python3
"""Compare current source-linked HCI decoder pointer classes to stock ROM."""
import hashlib
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path

G2 = Path(__file__).resolve().parents[3]
REPO = G2.parent
BUILD = G2 / "build/c-firmware/20261014/main-root-dependencies"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-decoders-round434/source_linked_decoders.c"
OBJECT = BUILD / "source_linked_decoders.o"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    build = json.loads((BUILD / "receipt.json").read_text())
    assert build["hci_decoder_source"]["sha256"] == sha(SOURCE)
    object_rows = [row for row in build["objects"] if row["path"] == str(OBJECT.relative_to(REPO))]
    assert len(object_rows) == 1 and object_rows[0]["sha256"] == sha(OBJECT)
    assert sha(STOCK) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    listing = subprocess.check_output(["arm-none-eabi-nm", "-S", str(OBJECT)], text=True)
    matches = [line for line in listing.splitlines()
               if line.split()[-1:] == ["audio_ble_hci_event_decoders_6c910c"]]
    assert len(matches) == 1
    start, size = (int(part, 16) for part in matches[0].split()[:2])
    assert size == 86 * 4
    relocations = subprocess.check_output(["arm-none-eabi-readelf", "-Wr", str(OBJECT)], text=True)
    section = relocations.split("Relocation section '.rel.rodata'", 1)[1].split(
        "Relocation section", 1)[0]
    pointers = {int(offset, 16): int(value, 16) for offset, value in re.findall(
        r"(?m)^([0-9a-f]{8})\s+[0-9a-f]{8}\s+R_ARM_ABS32\s+([0-9a-f]{8})",
        section)}
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        data_path = Path(temporary) / "rodata.bin"
        subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "-j", ".rodata",
                        str(OBJECT), str(data_path)], check=True)
        data = data_path.read_bytes()
    assert start + size <= len(data)
    source_words = [pointers.get(start + 4 * i, 0) +
                    struct.unpack_from("<I", data, start + 4 * i)[0]
                    for i in range(86)]
    stock = STOCK.read_bytes()[32:]
    native_words = struct.unpack_from("<86I", stock, 0x6c910c - 0x438000)
    zero_mismatches = [i for i in range(86)
                       if (source_words[i] == 0) != (native_words[i] == 0)]
    shared_mismatches = [(i, j) for i in range(86) for j in range(i + 1, 86)
                         if (source_words[i] == source_words[j]) !=
                         (native_words[i] == native_words[j])]
    table_relocations = sum(start <= offset < start + size for offset in pointers)
    assert not zero_mismatches and not shared_mismatches
    assert table_relocations == 74 and source_words[-1] == native_words[-1] == 0
    assert len(set(source_words) - {0}) == len(set(native_words) - {0}) == 69
    receipt = {
        "status": "PASS_CURRENT_HCI_DECODER_POINTER_CLASSES",
        "current_source_sha256": sha(SOURCE),
        "current_object_sha256": sha(OBJECT),
        "stock_image_sha256": sha(STOCK),
        "table_address": "0x6c910c",
        "table_slots": 86,
        "source_pointer_relocations": table_relocations,
        "zero_slots": sum(word == 0 for word in source_words),
        "distinct_nonzero_targets": 69,
        "zero_mismatches": zero_mismatches,
        "shared_pointer_mismatches": shared_mismatches,
        "final_sentinel_zero": True,
        "parser_body_equivalence": False,
        "final_placement_proven": False,
    }
    output = BUILD / "hci-decoder-current-receipt.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
