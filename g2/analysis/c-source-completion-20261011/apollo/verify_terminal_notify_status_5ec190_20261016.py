#!/usr/bin/env python3
"""Compare Terminal status UI child with pinned Apollo stock at lower-call cuts."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_notify_status_5ec190.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-notify-status-5ec190"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_status_apply_layout_5ebc9e", 0x5ebc9e, 2),
         ("audio_uart_page_44104c", 0x44104c, 1),
         ("audio_uart_page_44140e", 0x44140e, 3),
         ("audio_uart_page_43dfa4", 0x43dfa4, 2),
         ("audio_terminal_status_publish_5e5498", 0x5e5498, 2),
         ("audio_uart_page_43ded4", 0x43ded4, 2))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "notify-status-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c)"
                              "{(void)a;(void)b;(void)c;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "notify-status-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_notify_status_5ec190",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, present, status, seed):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + seed) & 255 for i in range(0x2a0))))
        for i, offset in enumerate((0x208, 0x20c, 0x210)):
            u.mem_write(state + offset, struct.pack("<I", 0x20009000 + i * 0x100 if present & (1 << i) else 0))
        u.mem_write(state + 0x278, bytes([status]))
        cuts = {(symbols[name] if compiled else address) & ~1: (name, arity)
                for name, address, arity in CALLS}
        trace = []
        def hook(cpu, pc, size, _):
            item = cuts.get(pc)
            if item is None:
                return
            name, arity = item
            args = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            if name == "audio_terminal_status_apply_layout_5ebc9e":
                assert args[0] == state
                args[0] = 0x2006e0d0
            trace.append((name, *args[:arity]))
            ret = (args[0] ^ 0x005a3c18) if name == "audio_uart_page_44104c" else 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_notify_status_5ec190"] if compiled else 0x5ec190
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0x2a0))
    cases = 0
    for present in range(8):
        for status in (0, 1, 2, 3, 0xff):
            for seed in (0, 0x5a, 0xff):
                args = present, status, seed
                stock = run(False, *args)
                selected = run(True, *args)
                if stock != selected:
                    raise RuntimeError(f"notify-status mismatch {args}: {stock[0]} != {selected[0]}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_NOTIFY_STATUS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "All object presence patterns, status branches, call order, colors and unchanged state",
              "limits": ["Layout, LVGL style and publication lower-call effects remain open; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()
