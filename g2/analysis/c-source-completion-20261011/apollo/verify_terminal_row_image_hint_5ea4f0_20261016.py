#!/usr/bin/env python3
"""Compare Terminal row image inheritance hint with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_row_image_hint_5ea4f0.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-row-image-hint-5ea4f0"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
__attribute__((noinline,used)) uint32_t audio_terminal_item_59737c(uint32_t a){(void)a;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "row-image-hint-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "row-image-hint-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_row_image_hint_5ea4f0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, item_on, kind, index, previous_on, previous_kind):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x20003000, bytes((0, kind, 0, 0)))
        u.mem_write(0x20004000, bytes((0, previous_kind, 0, 0)))
        cut = (symbols["audio_terminal_item_59737c"] if compiled else 0x59737c) & ~1
        trace = []
        def hook(cpu, pc, size, _):
            if pc == cut:
                trace.append(cpu.reg_read(A.UC_ARM_REG_R0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20004000 if previous_on else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, index)
        u.reg_write(A.UC_ARM_REG_R1, 0x20003000 if item_on else 0)
        entry = symbols["audio_terminal_row_image_hint_5ea4f0"] if compiled else 0x5ea4f0
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for item_on in (False, True):
        for kind in (0, 1, 2):
            for index in (0, 1, 2, 0xffff, 0x10000, 0x10001):
                for previous_on in (False, True):
                    for previous_kind in (0, 1, 2):
                        stock = run(False, item_on, kind, index, previous_on, previous_kind)
                        selected = run(True, item_on, kind, index, previous_on, previous_kind)
                        if stock != selected:
                            raise RuntimeError(f"row-image-hint mismatch {item_on=} {kind=} "
                                               f"{index=} {previous_on=} {previous_kind=}: "
                                               f"{stock} vs {selected}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ROW_IMAGE_HINT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "current/prior item guards, 16-bit index wrap and lower-call argument",
              "limits": ["Prior-item provider effects and final resource placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
