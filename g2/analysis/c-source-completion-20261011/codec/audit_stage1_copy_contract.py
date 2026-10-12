#!/usr/bin/env python3
"""Check stock codec image-A stage-1 load extent and entry instructions."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IMAGES = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"
OBJDUMP = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump"


def native_listing(path, start, end):
    return subprocess.check_output([str(OBJDUMP), "-D", "-b", "binary", "-m", "csky",
                                    "--adjust-vma=0x10000000", f"--start-address={hex(start)}",
                                    f"--stop-address={hex(end)}", str(path)], text=True)


def main():
    stage1 = IMAGES / "binh_a_stage1.bin"
    stage2 = IMAGES / "binh_a_stage2_container.bin"
    raw = stage1.read_bytes()
    assert raw[:4] == b"BINH"
    assert int.from_bytes(raw[12:16], "little") == len(stage2.read_bytes()) == 0xc800
    assert int.from_bytes(raw[16:20], "little") == len(raw) == 0x3000
    listing = native_listing(stage1, 0x10000a44, 0x10000ac0)
    required = [
        "10000a4a:", "0x10023400", "10000a9e:", "10000aa0:",
        "10000aa4:", "0x20026d7c", "10000aa6:", "0x100264e4",
        "10000aae:", "0x200264e4", "10000ab4:", "10000ab8:",
        "10000abc:", "0x10023500",
    ]
    assert all(fragment in listing for fragment in required)
    sram_len = ((0x20026d7c + 0x100264e4 - 0x10023400 - 0x200264e4)
                & 0xffffffff)
    assert sram_len == 0x397c == 14716
    assert 0xc800 - sram_len == 36484
    result = {
        "stage1_sha256": hashlib.sha256(raw).hexdigest(),
        "stage2_container_sha256": hashlib.sha256(stage2.read_bytes()).hexdigest(),
        "header_stage1_bytes": 0x3000,
        "header_stage2_bytes": 0xc800,
        "nominal_first_firmware_path": {
            "flash_reader_entry": "0x10000c58",
            "stage2_header_word_read": "0x10000a9e..0x10000aa0",
            "sram_copy_call": "0x10000ab4..0x10000ab8",
            "sram_copy_destination": "0x10023400",
            "sram_copy_bytes": sram_len,
            "xip_bytes_before_sram": 36484,
            "reset_entry": "0x10023500",
            "size_formula": "0x20026d7c + 0x100264e4 - 0x10023400 - 0x200264e4",
        },
        "stock_nominal_loader_copy_extent_proven": True,
        "final_custom_image_loader_equality_proven": False,
        "limits": [
            "The other multiboot path and flash hardware side effects are not qualified by this bounded instruction audit.",
            "The start of XIP in the final custom package and physical DRAM aliasing still require full linker/loader validation.",
        ],
    }
    out = HERE / "excluded-section-eligibility/stage1-copy-contract.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print({"copy_bytes": sram_len, "xip_bytes": 36484, "reset": "0x10023500"})


if __name__ == "__main__":
    main()
