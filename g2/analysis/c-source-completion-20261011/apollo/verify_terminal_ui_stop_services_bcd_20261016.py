#!/usr/bin/env python3
"""Compare three terminal cleanup children to pinned stock call/state effects."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_services_bcd_5ec268.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-services-bcd"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CHILDREN = [("b", 0x5ec268, "audio_terminal_ui_stop_service_b_5ec268", 0x1f4, 8),
            ("c", 0x5ebbc6, "audio_terminal_ui_stop_service_c_5ebbc6", 0x214, 4),
            ("d", 0x5ec770, "audio_terminal_ui_stop_service_d_5ec770", 0x230, 4)]
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void *audio_uart_lv_obj_parent_44dca2(void*p){return p;}
void audio_uart_page_delete_event_filter_44d7b8(void*p){(void)p;}
uint32_t audio_td_counter_b_get(void){return 0;}
void audio_terminal_ui_event_5e5484(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_display_audio_reset_441488(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    for literal in (0x5ec2e4, 0x5ebc34, 0x5ec7dc):
        if int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") != 0x2006e0d0:
            raise RuntimeError("terminal state pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "service-bcd-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "service-bcd-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_stop_service_b_5ec268",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    stock_cuts = {0x44dca2: "parent", 0x44d7b8: "delete", 0x5973dc: "counter",
                  0x5e5484: "event", 0x441488: "reset"}
    compiled_cuts = {symbols[k] & ~1: v for k, v in (
        ("audio_uart_lv_obj_parent_44dca2", "parent"),
        ("audio_uart_page_delete_event_filter_44d7b8", "delete"),
        ("audio_td_counter_b_get", "counter"),
        ("audio_terminal_ui_event_5e5484", "event"),
        ("audio_uart_display_audio_reset_441488", "reset"))}

    def run(compiled, child, first, active, parent):
        name, address, symbol, offset, count = child
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for segment_address, data in segments:
            u.mem_write(segment_address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0xa5,))*0x2a0)
        u.mem_write(state, struct.pack("<I", 0x20041000 if first else 0))
        u.mem_write(state+offset, struct.pack("<I", 0x20042000 if active else 0))
        cuts = compiled_cuts if compiled else stock_cuts
        trace = []
        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((kind, r0, r1, r2) if kind in ("event", "reset") else
                         (kind, r0) if kind in ("parent", "delete") else (kind,))
            if kind == "parent":
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20043000 if parent else 0)
            elif kind == "counter":
                cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.emu_start((symbols[symbol] if compiled else address)|1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)).hex(), trace

    cases = 0
    for child in CHILDREN:
        for first in (False, True):
            for active in (False, True):
                for parent in (False, True):
                    stock = run(False, child, first, active, parent)
                    selected = run(True, child, first, active, parent)
                    if stock != selected:
                        raise RuntimeError(f"{child[0]} {first=} {active=} {parent=} mismatch: "
                                           f"{stock[1]} vs {selected[1]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_SERVICES_BCD_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "three cleanup child branches, state bytes and lower-call traces",
              "limits": ["Lower-call effects, shared RAM ownership/placement, startup, concurrency and hardware behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
