#!/usr/bin/env python3
"""Measure the current experimental CASE source ELF against stock payload geometry."""
from pathlib import Path
import hashlib
import json
import subprocess
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
elf_path = HERE / "case_absolute_current_round.elf"
stock_path = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_box.bin"
stock = stock_path.read_bytes()
assert hashlib.sha256(stock).hexdigest() == "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
with elf_path.open("rb") as stream:
    elf = ELFFile(stream)
    loaded = [s for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
    assert len(loaded) == 1
    segment = loaded[0]
    result = {
        "status": "EXPERIMENTAL_LAYOUT_OVERFLOW",
        "source_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
        "stock_wrapper_sha256": hashlib.sha256(stock).hexdigest(),
        "stock_payload_bytes": len(stock) - 32,
        "stock_reset_entry": "0x08000145",
        "experimental_elf_entry": hex(elf.header["e_entry"]),
        "experimental_load_address": hex(segment["p_vaddr"]),
        "experimental_load_bytes": segment["p_filesz"],
        "overflow_bytes": segment["p_filesz"] - (len(stock) - 32),
        "source_complete": False,
        "limits": [
            "Absolute source link proves relocation resolution under the experimental script only.",
            "Startup entry differs from authenticated stock reset and final section placements are not qualified.",
            "No executable-byte equality, initialized-data, package or physical-device proof."
        ],
    }
    assert result["overflow_bytes"] > 0
    (HERE / "case-absolute-layout-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "experimental_load_bytes", "overflow_bytes", "experimental_elf_entry")}))
