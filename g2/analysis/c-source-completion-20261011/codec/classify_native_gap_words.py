#!/usr/bin/env python3
"""Bind all aligned image-A gap-pointer words to native consumers and C owners."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE / "excluded-section-eligibility/native-gap-pointer-words.json"


def classify(region, address):
    if region == "xip_to_xip":
        if address == 0x102073ec:
            return "audio_input_irq_callback_word", "resident_xip_audio_input.c"
        if 0x1020a8f4 <= address <= 0x1020a90c:
            return "aout_lodac_interior_jump_table", "resident_xip_audio_output_lodac.c"
        if 0x1020aca4 <= address <= 0x1020acc0:
            return "gpio_trigger_interior_jump_table", "resident_xip_gpio_irq_disable.c"
    if region == "xip_to_sram" and 0x1020be1c <= address <= 0x1020be50:
        return "flash_getinfo_interior_jump_table", "resident_flash_transfer.c"
    if region == "sram_to_sram":
        if address == 0x10025ca8:
            return "clock_mode1_initialized_data_pointer", "resident_clock_boot_literals.c"
        if (address in (0x10025098, 0x10025124) or
                0x100253cc <= address < 0x10025460):
            return "platform_gate_interior_jump_table", "resident_platform_gate.c"
        if address == 0x10025224 or 0x10025460 <= address <= 0x100254a8:
            return "clock_frequency_interior_jump_table", "resident_clock_frequency.c"
        if (address == 0x1002481c or
                0x100249cc <= address <= 0x100249f0):
            return "platform_read_interior_jump_table", "resident_platform_read.c"
        if (0x100249a4 <= address <= 0x100249c8 or
                0x10025d84 <= address <= 0x10025d8c):
            return "platform_config_interior_jump_table", "resident_platform_config.c"
    raise ValueError((region, hex(address)))


def main():
    source = json.loads(SOURCE.read_text())
    groups = {}
    for region, scan in source["scans"].items():
        for hit in scan["aligned_word_hits"]:
            kind, file = classify(region, int(hit["source_address"], 16))
            path = ROOT / "g2/components/gx8002/app_callback_candidate" / file
            assert path.is_file(), path
            row = dict(hit, region=region, consumer_kind=kind,
                       selected_c_owner=str(path.relative_to(ROOT)),
                       selected_c_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            groups.setdefault(kind, []).append(row)
    count = sum(map(len, groups.values()))
    assert count == 78, count
    result = {
        "pointer_scan_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "classified_count": count,
        "unclassified_count": 0,
        "consumer_groups": groups,
        "new_distinct_executable_entry_from_aligned_word_scan": False,
        "new_initialized_data_body": "0x10025cf4..0x10025d04, 16 bytes",
        "native_indirect_root_absence_proven": False,
        "limits": [
            "Grouping uses authenticated native instruction consumers and selected C enclosing-body ownership; it is not a byte-equality proof of those bodies.",
            "The aligned-word scan omits encoded, computed, halfword and other-stage roots.",
            "Final address relocation of interior branch targets and callback descriptors remains a linker-layout gate.",
        ],
    }
    out = HERE / "excluded-section-eligibility/classified-native-gap-words.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print({name: len(rows) for name, rows in groups.items()})


if __name__ == "__main__":
    main()
