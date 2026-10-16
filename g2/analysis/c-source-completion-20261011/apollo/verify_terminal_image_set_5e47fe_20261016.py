#!/usr/bin/env python3
"""Compare Terminal image-set helper with pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_image_set_5e47fe.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-image-set-5e47fe"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_lv_style_unlink_450500", 0x450500, 2),
         ("audio_uart_display_audio_reset_441488", 0x441488, 3),
         ("audio_uart_page_498680", 0x498680, 2))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "image-set-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c)"
                              "{(void)a;(void)b;(void)c;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "image-set-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_image_set_5e47fe",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, object_value, source_value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address, _) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            name, _, arity = CALLS[i]
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((name, *args[:arity]))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object_value)
        u.reg_write(A.UC_ARM_REG_R1, source_value)
        entry = symbols["audio_terminal_image_set_5e47fe"] if compiled else 0x5e47fe
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace
    cases = 0
    for object_value in (0, 0x20001000, 0xffffffff):
        for source_value in (0, 0x20002000, 0x7733a8, 0xffffffff):
            stock, selected = run(False, object_value, source_value), run(True, object_value, source_value)
            if stock != selected:
                raise RuntimeError(f"image-set mismatch {object_value=} {source_value=}: {stock} != {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_IMAGE_SET_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Null guards and ordered style/image lower-call arguments",
              "limits": ["Lower LVGL effects and final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
