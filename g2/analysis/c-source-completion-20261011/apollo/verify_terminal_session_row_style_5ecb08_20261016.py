#!/usr/bin/env python3
"""Compare Terminal session row styling with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_row_style_5ecb08.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-style-5ecb08"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_page_44104c", 0x44104c),
         ("audio_uart_page_4412ec", 0x4412ec),
         ("audio_uart_page_44130c", 0x44130c),
         ("audio_terminal_session_row_show_5897ee", 0x5897ee),
         ("audio_terminal_session_row_hide_589892", 0x589892))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "session-row-style-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_page_44104c(uint32_t a){return a;}\n"
                    "__attribute__((noinline,used)) void audio_uart_page_4412ec(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_uart_page_44130c(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_session_row_show_5897ee(uint32_t a){(void)a;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_session_row_hide_589892(uint32_t a){(void)a;}\n")
    elf = OUT / "session-row-style-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_session_row_style_5ecb08",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, object_value, selected, seed):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x20009000, bytes(((i + seed) & 255 for i in range(64))))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            regs = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            if i == 0:
                trace.append(("color", regs[0]))
                ret = 0x00abcdef
            elif i == 1:
                trace.append(("set_color", *regs))
                ret = 0
            elif i == 2:
                trace.append(("set_opa", *regs))
                ret = 0
            elif i == 3:
                trace.append(("show", regs[0]))
                ret = 0
            else:
                trace.append(("hide", regs[0]))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object_value)
        u.reg_write(A.UC_ARM_REG_R1, selected)
        u.emu_start((symbols["audio_terminal_session_row_style_5ecb08"] if compiled else 0x5ecb08) | 1,
                    0x600000, count=10000)
        return trace, bytes(u.mem_read(0x20009000, 64))
    cases = 0
    for object_value in (0, 0x20009000):
        for selected in (0, 1, 2, 0xff, 0x100, 0x101, 0xffffffff):
            for seed in (0, 0x55, 0xa5):
                args = object_value, selected, seed
                stock = run(False, *args)
                candidate = run(True, *args)
                if stock != candidate:
                    raise RuntimeError(f"session-row-style mismatch {args}: {stock[0]} != {candidate[0]}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SESSION_ROW_STYLE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Null guard, white color, selected opacity and show/hide calls",
              "limits": ["Show/hide animation lower effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()
