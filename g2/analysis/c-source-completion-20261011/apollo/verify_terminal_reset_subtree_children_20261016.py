#!/usr/bin/env python3
"""Compare Terminal subtree style and initial Y helpers with pinned stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_subtree_children_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-subtree-children"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_page_44122a", 0x44122a),
         ("audio_uart_page_441238", 0x441238),
         ("audio_uart_page_44120e", 0x44120e),
         ("audio_uart_page_44121c", 0x44121c))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "subtree-children-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint32_t audio_uart_ring_primary_head_cell;\n" +
                    "\n".join(f"__attribute__((noinline,used)) void {name}"
                              "(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}"
                              for name, _ in CALLS) + "\n")
    elf = OUT / "subtree-children-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_lv_style_four_5ea224",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, which, a, b, c):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cell = symbols["audio_uart_ring_primary_head_cell"] if compiled else 0x200746dc
        u.mem_write(cell, struct.pack("<I", 0x20003000))
        u.mem_write(0x2000300c, struct.pack("<I", a))
        cuts = {(symbols[name] if compiled else address) & ~1: name
                for name, address in CALLS}
        trace = []
        def hook(cpu, pc, size, _):
            name = cuts.get(pc)
            if name is None:
                return
            trace.append((name, *(cpu.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, a if which == "height" else 0x20005000)
        u.reg_write(A.UC_ARM_REG_R1, b)
        u.reg_write(A.UC_ARM_REG_R2, c)
        name = "audio_terminal_initial_image_y_5ea2d4" if which == "height" else "audio_terminal_lv_style_four_5ea224"
        stock = 0x5ea2d4 if which == "height" else 0x5ea224
        u.emu_start((symbols[name] if compiled else stock) | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0) if which == "height" else trace
    cases = 0
    for height in (0, 1, 15, 16, 17, 18, 19, 31, 32, 127, 32767):
        if run(False, "height", height, 0, 0) != run(True, "height", height, 0, 0):
            raise RuntimeError(f"image Y mismatch {height=}")
        cases += 1
    for value in (0, 1, 0x1234, 0xffffffff):
        for selector in (0, 1, 0xfffffffc):
            if run(False, "style", 0, value, selector) != run(True, "style", 0, value, selector):
                raise RuntimeError(f"style mismatch {value=} {selector=}")
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TERMINAL_RESET_SUBTREE_CHILDREN_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
               "scope": "Initial image Y and four style-call order/arguments",
               "limits": ["Font pointer initialization, lower style effects and final RAM placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
