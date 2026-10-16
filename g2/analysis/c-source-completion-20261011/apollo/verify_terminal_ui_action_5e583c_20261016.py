#!/usr/bin/env python3
"""Compare Terminal processing-response action with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_5e583c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e583c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_ui_stop_service_a_5eceb2", 0x5eceb2, 0),
         ("audio_terminal_reset_display_5e4c84", 0x5e4c84, 1),
         ("audio_uart_page_43dfa4", 0x43dfa4, 2),
         ("audio_terminal_processing_prepare_5ea30c", 0x5ea30c, 0),
         ("audio_terminal_set_label_style_5e482a", 0x5e482a, 4),
         ("audio_uart_page_49942e", 0x49942e, 2),
         ("audio_terminal_elapsed_refresh_5e4902", 0x5e4902, 0))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "action-5e583c-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "uint8_t audio_terminal_output_style_20003f80[0x100];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c,uint32_t d)"
                              "{(void)a;(void)b;(void)c;(void)d;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "action-5e583c-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e583c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, present, root, pattern):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        style = symbols["audio_terminal_output_style_20003f80"] if compiled else 0x20003f80
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        u.mem_write(style, bytes(((i ^ pattern) & 255 for i in range(0x100))))
        u.mem_write(state, struct.pack("<I", 0x20001000 if root else 0))
        for i, offset in enumerate((0x1cc, 0x1d0, 0x1d4, 0x1dc)):
            u.mem_write(state + offset,
                        struct.pack("<I", 0x20002000 + i * 0x100 if present & (1 << i) else 0))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address, _) in enumerate(CALLS)}
        trace = []
        def cstring(cpu, address):
            raw = bytes(cpu.mem_read(address, 128))
            return raw[:raw.index(0)]
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            name, _, arity = CALLS[i]
            args = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                     A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            if i == 4:
                if args[1] != style:
                    raise RuntimeError("output style pointer changed")
                args[1] = 0x20003f80
            elif i == 5:
                args[1] = cstring(cpu, args[1])
            trace.append((name, *args[:arity]))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x12)
        u.reg_write(A.UC_ARM_REG_R1, 0x34)
        entry = symbols["audio_terminal_ui_action_5e583c"] if compiled else 0x5e583c
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(state, 0x2a0)), trace
    cases = 0
    for present in range(16):
        for root in (0, 1):
            for pattern in (0, 0x5a, 0xff):
                args = (present, root, pattern)
                stock, selected = run(False, *args), run(True, *args)
                if stock != selected:
                    raise RuntimeError(f"action 5e583c mismatch {args}: {stock[2]} != {selected[2]}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_5E583C_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "UI field-presence guards, state, call order, style pointer and source-owned text",
              "limits": ["Output-style RAM ownership, lower effects and final placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
