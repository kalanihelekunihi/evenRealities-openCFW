#!/usr/bin/env python3
"""Compare paired Terminal scroll/status actions with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_scroll_actions_5e6dd0_5e6e30.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-scroll-actions-5e6dd0-5e6e30"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
HELPERS = (("position", 0x5e4e06), ("scroll", 0x5e4e0a), ("status", 0x5e4e10))
CALLS = (("audio_terminal_notify_status_5ec190", 0x5ec190, 0),
         ("audio_terminal_display_status_44ea04", 0x44ea04, 3))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "scroll-actions-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c)"
                              "{(void)a;(void)b;(void)c;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "scroll-actions-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e6dd0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, action, old, payload, object_present, status):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        initial = bytes(((i * 13 + status) & 255 for i in range(0x2a0)))
        u.mem_write(state, initial)
        u.mem_write(state + 0x1f4, struct.pack("<I", 0x20009000 if object_present else 0))
        u.mem_write(state + 0x278, bytes([status]))
        cuts = {(symbols[name] if compiled else address) & ~1: (name, arity)
                for name, address, arity in CALLS}
        helpers = {address: name for name, address in HELPERS}
        trace = []
        def hook(cpu, pc, size, _):
            if not compiled and pc in helpers:
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                if pc == 0x5e4e06:
                    result = r0 & 0xffff
                elif pc == 0x5e4e0a:
                    result = (r0 >> 31) & 1
                else:
                    old_status = cpu.reg_read(A.UC_ARM_REG_R1) & 255
                    result = 2 if r0 & (1 << 28) else 1 if r0 & (1 << 29) else 0 if r0 & (1 << 30) else old_status
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                return
            item = cuts.get(pc)
            if item is None:
                return
            name, arity = item
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((name, *args[:arity]))
            cpu.reg_write(A.UC_ARM_REG_R0, 0x12345678)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols[f"audio_terminal_ui_action_{action:x}"] if compiled else action
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(state, 0x2a0))
    payloads = [0, 1, 0xffff, 0x10000000, 0x20000000, 0x40000000,
                0x80000000, 0x70001234, 0xf000abcd, 0xffffffff]
    cases = 0
    for action in (0x5e6dd0, 0x5e6e30):
        for old in (0, 0x12345678):
            for payload in payloads:
                for object_present in (0, 1):
                    for status in (0, 1, 2, 0xff):
                        args = action, old, payload, object_present, status
                        stock = run(False, *args)
                        selected = run(True, *args)
                        if stock != selected:
                            raise RuntimeError(f"scroll action mismatch {args}: {stock[:2]} != {selected[:2]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_SCROLL_ACTIONS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Both stock bodies, null guard, packed status, notifications, scroll arguments and full UI state",
              "limits": ["Notify lower effects, scroll animation effects and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()
