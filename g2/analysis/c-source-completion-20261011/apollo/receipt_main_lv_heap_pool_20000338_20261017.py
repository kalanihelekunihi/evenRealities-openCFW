#!/usr/bin/env python3
"""Bind the authenticated fixed SRAM LVGL heap-pool cell address."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
HERE = BASE / "main-lv-heap-pool-20000338"
PRIOR = BASE / "main-display-draw-mask-rect-48a98e/candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_heap_pool_20000338.c"
HEAP_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_font_alloc.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT, CURRENT, OUT = HERE / "heap-pool.o", HERE / "candidate.o", HERE / "receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    # The three stock wrappers for allocation, reallocation and free all
    # load the same literal at 0x48436c, which names the preinitialized cell.
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for address in (0x484322, 0x484330, 0x48433c):
        offset = address - 0x438000
        instruction = next(decoder.disasm(payload[offset:offset + 4], address))
        match = re.fullmatch(r"r0, \[pc, #0x([0-9a-f]+)\]", instruction.op_str)
        assert instruction.mnemonic == "ldr" and match is not None
        assert ((address + 4) & ~3) + int(match.group(1), 16) == 0x48436c
    assert struct.unpack_from("<I", payload, 0x48436c - 0x438000)[0] == 0x20000338
    assert "0x20000338u" in HEAP_SOURCE.read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 107 and len(current) == 106
    assert removed == ["audio_uart_lv_heap_pool"] and not added
    entries = subprocess.check_output(["arm-none-eabi-nm", str(CURRENT)], text=True)
    assert "20000338 A audio_uart_lv_heap_pool" in entries
    record = {
        "status": "PASS_MAIN_LV_HEAP_POOL_20000338_RAM_CONTRACT_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "heap_initializer_source": ref(HEAP_SOURCE),
        "stock_payload_sha256": PAYLOAD_SHA,
        "stock_literal_address": "0x48436c", "stock_ram_cell": "0x20000338",
        "unresolved_before": 107, "unresolved_after": 106,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_heap_pool"],
        "remaining_gate": "The LVGL heap pool fixed SRAM cell is source-bound at stock address 0x20000338. Heap initialization and physical RAM placement still require whole-image link and hardware evidence; other Main imports remain.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
