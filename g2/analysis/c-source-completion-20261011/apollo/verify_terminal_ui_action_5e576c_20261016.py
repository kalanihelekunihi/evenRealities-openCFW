#!/usr/bin/env python3
"""Compare Terminal BLE display-request action with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_5e576c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e576c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_fsm_prepare_5eae94", 0x5eae94, 0),
         ("audio_ux_get_system_ble_status", 0x47d8ce, 0),
         ("audio_terminal_runtime_event_from_ble", 0x5e50ea, 1),
         ("audio_terminal_request_display", 0x5e43d2, 2),
         ("audio_terminal_display_fallback_5ecafa", 0x5ecafa, 0))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "action-5e576c-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c,uint32_t d)"
                              "{(void)a;(void)b;(void)c;(void)d;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "action-5e576c-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e576c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, old, payload, event, session):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(0x2a0))
        u.mem_write(state + 0x288, struct.pack("<I", session))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address, _) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            name, _, arity = CALLS[i]
            args = [cpu.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1)]
            trace.append((name, *args[:arity]))
            cpu.reg_write(A.UC_ARM_REG_R0, 1 if i == 1 else event if i == 2 else 0x87654321 if i == 4 else 0x12345678)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols["audio_terminal_ui_action_5e576c"] if compiled else 0x5e576c
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(state, 0x2a0))
    cases = 0
    for old in (0, 1, 0x1234, 0xff):
        for payload in (0, 1, 2, 3, 0x102, 0x12345678):
            for event in (0, 2, 3, 4, 7, 22, 255):
                for session in (0, 0xabcdef02):
                    args = old, payload, event, session
                    stock = run(False, *args)
                    selected = run(True, *args)
                    if stock != selected:
                        raise RuntimeError(f"action 5e576c mismatch {args}: {stock[:2]} != {selected[:2]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_5E576C_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "BLE event routing, session/fallback arguments, return and unchanged UI RAM",
              "limits": ["Child effects and final placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
