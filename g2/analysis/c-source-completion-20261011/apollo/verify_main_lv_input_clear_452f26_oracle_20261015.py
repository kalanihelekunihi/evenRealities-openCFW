#!/usr/bin/env python3
"""Compare Apollo input clear and per-device cleanup with compiled C."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_input_clear_452f26.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-input-clear-452f26"
SHIM = '''#include <stdint.h>
uint8_t audio_uart_display_lv_state[512];
void *audio_uart_lv_input_next_452edc(void *p){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t k,void *q){return 1;}
uint32_t audio_uart_lv_input_event_453002(void *p,uint32_t k,void *q){return 1;}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x4530f8-0x438000:0x4530fc-0x438000], "little") != 0x2006f548:
        raise RuntimeError("LVGL state literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_input_clear_452f26",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, count, direct, kind, match, target_mask, selected):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            state = syms["audio_uart_display_lv_state"] if compiled else 0x2006f548
            inputs = [0x20010000 + i * 0x100 for i in range(count)]
            obj, other = 0x20020000, 0x20021000
            def put(addr, value): u.mem_write(addr, value.to_bytes(4, "little"))
            def get(addr): return int.from_bytes(u.mem_read(addr, 4), "little")
            put(state + 0x50, inputs[selected] if inputs else 0)
            put(state + 0x54, obj)
            for i, item in enumerate(inputs):
                u.mem_write(item, bytes([kind]))
                u.mem_write(item + 0xb, bytes([0x80 | i]))
                for offset in (0x68, 0x6c, 0x70, 0x74, 0x78):
                    val = obj if match else other
                    if offset in (0x68, 0x70) and not (target_mask & (1 if offset == 0x68 else 2)):
                        val = 0
                    put(item + offset, val)
            cuts = {
                (syms["audio_uart_lv_input_next_452edc"] & ~1) if compiled else 0x452edc: "next",
                (syms["audio_uart_lv_obj_event_451670"] & ~1) if compiled else 0x451670: "object_event",
                (syms["audio_uart_lv_input_event_453002"] & ~1) if compiled else 0x453002: "input_event",
            }
            trace = []
            def label(value):
                return "null" if value == 0 else "object" if value == obj else "other" if value == other else \
                    f"input{inputs.index(value)}" if value in inputs else hex(value)
            def hook(cpu, address, size, user):
                kind_name = cuts.get(address)
                if kind_name is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if kind_name == "next":
                    trace.append((kind_name, label(r0)))
                    result = inputs[0] if r0 == 0 and inputs else \
                        inputs[inputs.index(r0) + 1] if r0 in inputs and inputs.index(r0) + 1 < len(inputs) else 0
                else:
                    trace.append((kind_name, label(r0), r1, label(r2)))
                    result = 1
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, inputs[selected] if direct and inputs else 0)
            u.reg_write(A.UC_ARM_REG_R1, obj if match else other)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_input_clear_452f26"] if compiled else 0x452f26) | 1,
                        0x600000, count=100000)
            offsets = (0x68, 0x6c, 0x70, 0x74, 0x78)
            state_out = (get(state + 0x50), get(state + 0x54))
            fields = [(u.mem_read(item + 0xb, 1)[0], [get(item + off) for off in offsets])
                      for item in inputs]
            return trace, state_out, fields
        cases = [(count, direct, kind, match, mask, selected)
                 for count, direct, kind, match, mask in itertools.product(
                     (0, 1, 2), (False, True), (1, 2, 3), (False, True), range(4))
                 for selected in range(max(count, 1)) if not direct or count]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_INPUT_CLEAR_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_spans": ["0x452f26..0x452f5d", "0x45305c..0x4530f5"],
               "native_state_base": "0x2006f548", "cases": len(cases),
               "limits": ["Input iterator and both event dispatches controlled; live event side effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
