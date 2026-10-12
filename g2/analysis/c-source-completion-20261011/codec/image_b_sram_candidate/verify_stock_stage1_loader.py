#!/usr/bin/env python3
"""Pin the stock B stage-1 normal-boot payload copy instructions and extents."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGES = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"
OBJDUMP = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump"


def listing(image, start, end):
    return subprocess.check_output([
        str(OBJDUMP), "-D", "-b", "binary", "-m", "csky",
        "--adjust-vma=0x0fffffe8", f"--start-address={start:#x}",
        f"--stop-address={end:#x}", str(image),
    ], text=True)


def main():
    stage1 = IMAGES / "binh_b_stage1.bin"
    stage2 = IMAGES / "binh_b_stage2.bin"
    raw1, raw2 = stage1.read_bytes(), stage2.read_bytes()
    assert hashlib.sha256(raw1).hexdigest() == "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c"
    assert hashlib.sha256(raw2).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
    assert raw1[:4] == b"BINH"
    assert int.from_bytes(raw1[12:16], "little") == len(raw2) == 0x1408c
    assert int.from_bytes(raw1[16:20], "little") == len(raw1) == 0x3000
    entry = listing(stage1, 0x10000100, 0x10000124)
    dispatch = listing(stage1, 0x10000df0, 0x10000e1a)
    loader = listing(stage1, 0x10000d4c, 0x10000dd0)
    reader = listing(stage1, 0x10000fdc, 0x1000109a)
    for fragment in ("1000011a:", "0x10000df0", "1000011e:", "0x10003100"):
        assert fragment in entry
    for fragment in ("10000e0c:", "0x20001720", "10000e0e:", "10000e14:", "0x10000d4c"):
        assert fragment in dispatch
    for fragment in ("0x10003000", "0x2001708c", "0x100167d0", "0x200167d0",
                     "10000d84:", "0x10000fdc", "10000d90:", "10000d92:"):
        assert fragment in loader
    for fragment in ("10000fe2:", "10000fe4:", "10000fea:", "10001092:", "10001098:"):
        assert fragment in reader
    # Marker-selected branch is a separate native path. The first call reads
    # a word from package+0x323b0; the second uses that word as a base,
    # requests zero bytes at 0x20000000, and returns to stage-1 reset.
    for fragment in ("10000d9a:", "movi      \tr3, 51436", "10000da2:",
                     "10000da4:", "10000da8:", "movi      \tr3, 51437",
                     "movih      \tr1, 8192", "movi      \tr2, 0",
                     "10000dba:", "10000dc0:", "10000dc4:", "10000dc6:"):
        assert fragment in loader, fragment
    source = ROOT / "g2/components/gx8002/image_b_stage1_candidate/backup_stage1_loader.c"
    source_text = source.read_text()
    for fragment in ("package + UINT32_C(0x323b0)", "word + UINT32_C(0x323b4)",
                     "(void *)(uintptr_t)UINT32_C(0x20000000), 0u",
                     "&gx8002_image_b_stage1_reset_10000100"):
        assert fragment in source_text, fragment
    count = (0x2001708c + 0x100167d0 - 0x10003000 - 0x200167d0) & 0xffffffff
    assert count == len(raw2)
    assert len(raw2) - 300 == 0x13f60
    result = {
        "stage1_sha256": hashlib.sha256(raw1).hexdigest(),
        "stage2_sha256": hashlib.sha256(raw2).hexdigest(),
        "header_stage1_bytes": len(raw1),
        "header_stage2_bytes": len(raw2),
        "normal_branch": {
            "dispatch": "0x10000e0a..0x10000e18, mode word 0x20001720 equals 2",
            "loader": "0x10000d4c..0x10000d98",
            "flash_reader": "0x10000fdc",
            "destination": "0x10003000",
            "copy_bytes": count,
            "stage2_entry": "0x10003100",
            "initialized_tail_load": ["0x10016f60", "0x1001708c"],
            "typed_runtime_vma": ["0x20016f60", "0x2001708c"],
        },
        "marker_branch": {
            "loader": "0x10000d9a..0x10000dce",
            "first_reader_source": "package+0x323b0",
            "first_reader_bytes": 4,
            "second_reader_source": "first_read_word+0x323b4",
            "second_reader_destination": "0x20000000",
            "second_reader_bytes": 0,
            "entry_word": "0x2002d3e4",
            "entry_target": "0x10000100",
            "selected_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "qualified_as_static_native_source_control_flow": True,
            "reader_side_effects_executed": False,
        },
        "stock_normal_loader_copy_extent_proven": True,
        "iram_dram_alias_on_physical_target_proven": False,
        "custom_final_elf_or_hardware_proven": False,
        "limits": ["Both loader branch arguments and control targets are statically cross-checked. The flash reader, MMIO effects, reset transfers and package contents were not executed here.",
                   "Physical IRAM/DRAM alias behavior and final custom image placement remain unqualified."],
    }
    (HERE / "stock-stage1-loader-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"stock B stage1 normal copy: {count} bytes to 0x10003000 PASS")


if __name__ == "__main__":
    main()
