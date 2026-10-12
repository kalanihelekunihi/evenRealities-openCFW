#!/usr/bin/env python3
"""Bound the two authentic image-B ambient reads to native/source ISA."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGES = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"
OBJDUMP = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump"
BUILD = HERE / "build-ambient-entry-round"


def dump(*args):
    return subprocess.check_output([str(OBJDUMP), *map(str, args)], text=True)


def main():
    native = dump("-D", "-b", "binary", "-m", "csky", "--adjust-vma=0x10003000",
                  "--start-address=0x100040e8", "--stop-address=0x10004184",
                  IMAGES / "binh_b_stage2.bin")
    native_rx = dump("-D", "-b", "binary", "-m", "csky", "--adjust-vma=0x10003000",
                     "--start-address=0x1000ad60", "--stop-address=0x1000adb2",
                     IMAGES / "binh_b_stage2.bin")
    wrapper = dump("-dr", BUILD / "backup_uart_dma_apply_ambient_entry.o")
    zero = dump("-dr", BUILD / "backup_native_zero_word_read_experiment.o")
    for token in ("100040e8:", "push", "r4-r11, r15, r16", "100040ec:", "52",
                  "1000410a:", "r14, 4", "10004172:", "r4, 0x20", "10004178:",
                  "10004156:", "r4, 0x2c"):
        assert token in native, token
    assert "1000414e:" in native and "10004150:" in native  # invalid port does not store slot 8
    assert "1000ad6a:" in native_rx and "r9, r2" in native_rx
    assert "1000ada6:" in native_rx and "r3, (r9, 0x0)" in native_rx
    for token in ("subi", "r14, r14, 56", "ld.w", "r3, (r14, 0x0)",
                  "addi", "R_CKCORE_PCREL_IMM16BY2"):
        assert token in wrapper, token
    for token in ("movi", "r0, 0", "ld.w", "r0, (r0, 0x0)", "jmp", "r15"):
        assert token in zero, token
    receipt = json.loads((BUILD / "receipt.json").read_text())
    assert len(receipt["units"]) == 233 and len(receipt["undefined_symbols"]) == 6
    result = {
        "native_stage2_sha256": hashlib.sha256((IMAGES / "binh_b_stage2.bin").read_bytes()).hexdigest(),
        "selected_linked_object_sha256": receipt["linked_object_sha256"],
        "zero_address_read_isa": "native r9 may be zero; selected provider loads word at address zero",
        "uart_invalid_port_ambient_isa": "native descriptor[8] at entry-SP-56 left unwritten; naked wrapper reads it before C frame",
        "result": "PASS",
        "limits": ["Only the ambient instruction/frame shape is checked, not a whole-body native effect oracle.",
                   "Actual address-zero memory and untouched stack contents remain runtime environment values."],
    }
    (HERE / "ambient-entry-isa-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print("two ambient ISA/frame contracts PASS")


if __name__ == "__main__":
    main()
