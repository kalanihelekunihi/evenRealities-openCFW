#!/usr/bin/env python3
"""Compare Terminal FSM matrix, callback dispatch and state transitions to stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_status_5e7b74.c"
TABLE_SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_table_650430.c"
GENERATOR = G2 / "analysis/c-source-completion-20261011/apollo/generate_terminal_ui_fsm_table_650430_20261016.py"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-status-5e7b74"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
TABLE_PIN = "f14e57748e2148f596d9db59a74661cea2c4f28839059aaf42010d17fdd1fad0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    table = blob[0x650430-0x438000:0x650430-0x438000+4160]
    if hashlib.sha256(blob).hexdigest() != PIN or hashlib.sha256(table).hexdigest() != TABLE_PIN or \
            int.from_bytes(blob[0x5e7e0c-0x438000:0x5e7e10-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Terminal FSM stock inputs changed")
    subprocess.run(["python3", str(GENERATOR)], check=True, capture_output=True)
    cells = []
    targets = set()
    for state in range(13):
        row = []
        for event in range(40):
            off = (state*40+event)*8
            next_state = int.from_bytes(table[off:off+4], "little")
            pointer = int.from_bytes(table[off+4:off+8], "little")
            target = pointer & ~1
            row.append((next_state, target))
            if target:
                targets.add(target)
        cells.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "fsm-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_mode;\n"
                    "uint32_t audio_log_flags(void){return 0;}\n"
                    "void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)"
                    "{(void)a;(void)b;(void)c;return 0;}\n"
                    "const char*audio_terminal_ui_state_name_5e7b10(uint32_t x){(void)x;return 0;}\n"
                    "const char*audio_terminal_ui_event_name_5e7b2a(uint32_t x){(void)x;return 0;}\n"
                    + "".join(f"int32_t audio_terminal_ui_action_{target:06x}(uint32_t x,uint32_t y)"
                              "{(void)x;(void)y;return 0;}\n" for target in sorted(targets)))
    elf = OUT / "fsm-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_status_5e7b74",
                    str(SOURCE), str(TABLE_SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    compiled_actions = {symbols[f"audio_terminal_ui_action_{target:06x}"] & ~1: target
                        for target in targets}
    stock_actions = {target: target for target in targets}

    def run(compiled, state, event, result, payload):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        mode_addr = symbols["audio_terminal_ui_mode"] if compiled else 0x2006e345
        u.mem_write(mode_addr, bytes((state,)))
        flags = (symbols["audio_log_flags"] if compiled else 0x43d0ce)&~1
        actions = compiled_actions if compiled else stock_actions
        trace = []
        def hook(cpu, pc, size, _):
            if pc == flags:
                trace.append(("flags",))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif pc in actions:
                trace.append(("action", actions[pc], cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, event)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols["audio_terminal_ui_status_5e7b74"] if compiled else 0x5e7b74
        u.emu_start(entry|1, 0x600000, count=20000)
        return u.mem_read(mode_addr, 1)[0], trace

    cases = 0
    seen = set()
    for state in range(13):
        for event in range(40):
            stock, selected = run(False, state, event, 0, 0x13579bdf), run(True, state, event, 0, 0x13579bdf)
            if stock != selected:
                raise RuntimeError(f"FSM matrix mismatch {state=} {event=}: {stock} vs {selected}")
            cases += 1
            target = cells[state][event][1]
            if target and target not in seen:
                seen.add(target)
                for result in (-1, 1, 13, 14, 257):
                    stock = run(False, state, event, result, 0x2468ace0)
                    selected = run(True, state, event, result, 0x2468ace0)
                    if stock != selected:
                        raise RuntimeError(f"FSM result mismatch {state=} {event=} {result=}: "
                                           f"{stock} vs {selected}")
                    cases += 1
    for state, event in ((13, 0), (0xff, 0), (0, 40), (0, 0xff), (13, 40)):
        stock, selected = run(False, state, event, 0, 0x13579bdf), run(True, state, event, 0, 0x13579bdf)
        if stock != selected:
            raise RuntimeError(f"FSM invalid input mismatch {state=} {event=}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_STATUS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "table_source": str(TABLE_SOURCE.relative_to(ROOT)), "table_source_sha256": sha(TABLE_SOURCE),
              "generator": str(GENERATOR.relative_to(ROOT)), "generator_sha256": sha(GENERATOR),
              "payload_sha256": PIN, "stock_table_sha256": TABLE_PIN,
              "oracle_elf_sha256": sha(elf), "cases": cases,
              "active_cells": 159, "distinct_callback_targets": len(targets),
              "scope": "all 520 matrix cells, one of each callback result branch and invalid inputs; callback R1 compared with two payload sentinels on logging-disabled paths",
              "limits": ["Fifty callback bodies, enabled logging and name tables, final ROM/RAM placement, callback side effects and concurrency remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
