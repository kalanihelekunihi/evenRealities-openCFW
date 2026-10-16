#!/usr/bin/env python3
"""Compare Terminal query restore with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_restore_query_5e6620.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-restore-query-5e6620"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_ui_stop_service_e_5ec9c0", 0x5ec9c0, 0),
         ("audio_terminal_reset_ancillary_5e65f8", 0x5e65f8, 0),
         ("audio_terminal_ui_action_5e5442", 0x5e5442, 2),
         ("audio_terminal_ui_action_5e57c6", 0x5e57c6, 2),
         ("audio_log_flags", 0x43d0ce, 0),
         ("audio_log_extended", 0x43d574, -1),
         ("compressed_log_output", 0x43ce9e, -1))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "restore-query-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g)"
                              "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "restore-query-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_restore_query_5e6620",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, saved, old, flags, pattern):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        u.mem_write(state + 0x277, bytes((saved,)))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address, _) in enumerate(CALLS)}
        trace = []
        def cstring(cpu, address):
            raw = bytes(cpu.mem_read(address, 256))
            return raw[:raw.index(0)].decode("ascii")
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            name, _, arity = CALLS[i]
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if i == 4:
                trace.append(("flags",))
                result = flags
            elif i == 5:
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                line = int.from_bytes(cpu.mem_read(sp, 4), "little")
                msg = int.from_bytes(cpu.mem_read(sp + 4, 4), "little")
                value = int.from_bytes(cpu.mem_read(sp + 8, 4), "little")
                trace.append(("extended", args[0], cstring(cpu, args[1]),
                              cstring(cpu, args[2]), cstring(cpu, args[3]),
                              line, cstring(cpu, msg), value))
                result = 0
            elif i == 6:
                trace.append(("compressed", args[0], cstring(cpu, args[1]),
                              cstring(cpu, args[2]), args[3]))
                result = 0
            else:
                trace.append((name, *args[:arity]))
                result = 0
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        entry = symbols["audio_terminal_ui_restore_query_5e6620"] if compiled else 0x5e6620
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(state, 0x2a0)), trace
    cases = 0
    for saved in (0, 1, 2, 3, 7, 11, 12, 255):
        for old in (0, 4, 255, 256):
            for flags in (0, 1, 2, 4, 7):
                for pattern in (0, 0x5a):
                    args = (saved, old, flags, pattern)
                    stock, selected = run(False, *args), run(True, *args)
                    if stock != selected:
                        raise RuntimeError(f"query restore mismatch {args}: {stock[2]} != {selected[2]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_RESTORE_QUERY_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Saved-state branches, child-call order, return, full UI state and enabled diagnostics",
              "limits": ["Action-child effects, logger effects and final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
