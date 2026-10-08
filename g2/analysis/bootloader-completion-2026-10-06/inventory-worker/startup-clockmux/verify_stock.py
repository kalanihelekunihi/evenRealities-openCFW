#!/usr/bin/env python3
"""Hash-bound original-instruction checks for the clock-mux reset child.

This is static original-code evidence. Direct BL targets are explicit child
cuts; the script does not execute or simulate those children.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FUNCTIONS = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl"
OUT = Path(__file__).resolve().parent
EXPECTED_SHA256 = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
LOAD = 0x410000
START = 0x41ACB2
END = 0x41B04C  # exclusive, confirmed from Ghidra inclusive end 0x41b04b


def word(image: bytes, address: int) -> int:
    offset = address - LOAD
    return int.from_bytes(image[offset:offset + 4], "little")


def main() -> None:
    image = IMAGE.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    assert digest == EXPECTED_SHA256, digest
    fn = next(json.loads(line) for line in FUNCTIONS.read_text().splitlines()
              if json.loads(line)["entry"] == "0041acb2")
    assert fn["body_end_inclusive"] == "0041b04b", fn
    assert fn["body_bytes"] == END - START == 922

    cmd = ["arm-none-eabi-objdump", "-D", "-b", "binary", "-marm",
           "-M", "force-thumb", f"--adjust-vma=0x{LOAD:x}",
           f"--start-address=0x{START:x}", f"--stop-address=0x{END:x}", str(IMAGE)]
    disassembly = subprocess.run(cmd, check=True, text=True,
                                 stdout=subprocess.PIPE).stdout
    (OUT / "stock-disassembly.txt").write_text(disassembly)
    decoded = {}
    for line in disassembly.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+(.*)$", line)
        if match:
            decoded[int(match.group(1), 16)] = match.group(2)

    def instruction(address: int, pattern: str) -> None:
        line = decoded.get(address, "")
        assert re.search(pattern, line), (hex(address), pattern, line)

    body = image[START - LOAD:END - LOAD]
    assert len(body) == 922
    expected_words = {
        0x41B074: 0x400204D8,  # MCUCTRL.PLLCTL0
        0x41B0B0: 0x47FF0000,  # stock lookup table base
        0x41B0C8: 0x40008858,  # STIMER.HALSTATES
        0x41B0CC: 0x4000885C,  # reserved adjacent word, unnamed by HAL header
        0x41B0D0: 0x400200C0,  # reserved in public MCUCTRL map
        0x41B0D4: 0x400204E8,  # MCUCTRL.PLLMUXCTL
        0x41B0D8: 0x40004044,  # CLKGEN.MISC
        0x41B0DC: 0x40004030,  # CLKGEN.CLOCKENSTAT
        0x41B0E0: 0x40201000,  # PDM0 base
        0x41B0E4: 0x40208100,  # I2S0 + 0x100
        0x41B0E8: 0x40209100,  # I2S1 + 0x100
        0x41B0EC: 0x400B2000,  # no named base in copied Apollo510 header
        0x41B0F0: 0x40210000,  # AUDADC base
    }
    for address, expected in expected_words.items():
        assert word(image, address) == expected, (hex(address), hex(word(image, address)))

    calls = [(int(site, 16), int(target, 16)) for site, target in
             re.findall(r"^\s*([0-9a-f]+):.*\bbl\s+0x([0-9a-f]+)",
                        disassembly, flags=re.MULTILINE)]
    expected_targets = {
        0x41D1C0, 0x41D246, 0x41D3E4, 0x41D90E, 0x41D92C,
        0x41CA5C, 0x41BF84, 0x41C17A, 0x41E348, 0x41CAA2,
    }
    assert {target for _, target in calls} == expected_targets, calls
    assert [(site, target) for site, target in calls if site in
            {0x41AD6A, 0x41AD92, 0x41AD98, 0x41ADD8, 0x41ADE0,
             0x41AE22, 0x41AE2A, 0x41AE38, 0x41AEDC, 0x41AF80,
             0x41AFBC, 0x41AFFA}] == [
        (0x41AD6A, 0x41D1C0), (0x41AD92, 0x41D246),
        (0x41AD98, 0x41D1C0), (0x41ADD8, 0x41D3E4),
        (0x41ADE0, 0x41D1C0), (0x41AE22, 0x41D90E),
        (0x41AE2A, 0x41D92C), (0x41AE38, 0x41CA5C),
        (0x41AEDC, 0x41E348), (0x41AF80, 0x41CAA2),
        (0x41AFBC, 0x41D92C), (0x41AFFA, 0x41D3E4),
    ]

    # Exact register and stack setup at the status-poll child call.
    for address, pattern in [
        (0x41AD82, r"movs\s+r0, #1"),
        (0x41AD84, r"str\s+r0, \[sp, #0\]"),
        (0x41AD86, r"movs\.w\s+r3, #16777216"),
        (0x41AD8A, r"movs\.w\s+r2, #16777216"),
        (0x41AD8E, r"ldr\s+r1, \[pc, #844\]"),
        (0x41AD90, r"movs\s+r0, #200"),
    ]:
        instruction(address, pattern)
    # Pin get/update sequence; R5 is adjusted in place, not zero-filled.
    for address, pattern in [
        (0x41AE1A, r"bfi\s+r5, r0, #0, #4"),
        (0x41AE1E, r"add\s+r1, sp, #4"),
        (0x41AE20, r"movs\s+r0, #15"),
        (0x41AE26, r"movs\s+r1, r5"),
        (0x41AE28, r"movs\s+r0, #15"),
    ]:
        instruction(address, pattern)
    # Cache invalidate and mode transitions have concrete r0/r1/selector values.
    for address, pattern in [
        (0x41AD68, r"movs\s+r0, #1"),
        (0x41AD96, r"movs\s+r0, #5"),
        (0x41ADDC, r"movw\s+r0, #1500"),
        (0x41AE94, r"movs\s+r0, #5"),
        (0x41AED8, r"movs\s+r1, #1"),
        (0x41AEDA, r"movs\s+r0, #0"),
        (0x41AEE0, r"movs\s+r0, #1"),
        (0x41AEFA, r"movs\s+r0, #20"),
        (0x41AF28, r"movs\s+r0, #30"),
        (0x41AF2E, r"movs\s+r0, #31"),
        (0x41AF34, r"movs\s+r0, #32"),
        (0x41AF3A, r"movs\s+r0, #33"),
        (0x41AF40, r"movs\s+r0, #26"),
        (0x41AF46, r"movs\s+r0, #27"),
        (0x41AFB8, r"ldr\s+r1, \[sp, #4\]"),
        (0x41AFBA, r"movs\s+r0, #15"),
        (0x41AFF6, r"mov\s+r1, sp"),
        (0x41AFF8, r"movs\s+r0, #4"),
        (0x41AE6C, r"movs\s+r0, #30"),
        (0x41AE72, r"movs\s+r0, #31"),
        (0x41AE78, r"movs\s+r0, #32"),
        (0x41AE7E, r"movs\s+r0, #33"),
        (0x41AE84, r"movs\s+r0, #26"),
        (0x41AE8A, r"movs\s+r0, #27"),
    ]:
        instruction(address, pattern)

    # Caller carry: R5 is loaded from a word literal, used to update local
    # state, then preserved across the stock helper chain until this body.
    assert word(image, 0x41CB5C) == 0x20027064
    assert image[0x41C606 - LOAD:0x41C60A - LOAD] == bytes.fromhex("dff85455")
    assert image[0x41C60A - LOAD:0x41C60C - LOAD] == bytes.fromhex("2b60")
    assert "41ae1a:" in disassembly and "bfi\tr5, r0, #0, #4" in disassembly
    assert "41ae22:" in disassembly and "41ae2a:" in disassembly
    assert "41b036:" in disassembly and "41b048:" in disassembly

    result = {
        "status": "PASS",
        "mode": "static original-instruction checks; direct children cut at BL",
        "stock_sha256": digest,
        "load_address": hex(LOAD),
        "function_range": [hex(START), hex(END)],
        "function_bytes": len(body),
        "callee_addresses": [hex(t) for t in sorted(expected_targets)],
        "caller_r5_carry": {"load_site": "0x41c606", "literal": "0x41cb5c",
                             "incoming_value": "0x20027064",
                             "gpio_bfi_site": "0x41ae1a"},
        "limits": ["This receipt is static boundary/disassembly validation; native-comparison.json is the separate dynamic stock-versus-C cut test.",
                   "Child behavior is outside both parent-level checks; no child-cut result is called a whole-function source-closure comparison."],
    }
    (OUT / "stock-check.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: locked hash, exact 922-byte bound, MMIO literal map, BL cuts, and R5 carry")


if __name__ == "__main__":
    main()
