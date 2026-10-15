#!/usr/bin/env python3
"""Compare Apollo LVGL timer list wrappers with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_timer_helpers_4645ec.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-timer-helpers-4645ec"
SHIM = '''#include <stdint.h>
uint8_t audio_uart_display_lv_state[512];
void *audio_uart_lv_list_first(void *p){return 0;}
void *audio_uart_lv_list_next(void *p,void *q){return 0;}
void audio_uart_lv_list_remove(void *p,void *q){}
void audio_uart_lv_heap_free(void *p){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    expected = {0x4646b4: 0x2006f5bc, 0x4646b8: 0x2006f548}
    for address, value in expected.items():
        actual = int.from_bytes(blob[address-0x438000:address-0x438000+4], "little")
        if actual != value: raise RuntimeError((hex(address), hex(actual)))
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_timer_iter_4645ec",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, entry, timer, dirty):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            state = syms["audio_uart_display_lv_state"] if compiled else 0x2006f548
            u.mem_write(state + 0x82, bytes([dirty]))
            cuts = {((syms[name] & ~1) if compiled else address): kind for kind, address, name in (
                ("first", 0x482cd8, "audio_uart_lv_list_first"),
                ("next", 0x482cf0, "audio_uart_lv_list_next"),
                ("remove", 0x482c0e, "audio_uart_lv_list_remove"),
                ("free", 0x44f758, "audio_uart_lv_heap_free"))}
            trace = []
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                if kind == "free": trace.append((kind, r0))
                elif kind == "first": trace.append((kind, r0 - state))
                else: trace.append((kind, r0 - state, r1))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20030000 if kind in ("first", "next") else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, timer)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            origin = (syms["audio_uart_lv_timer_iter_4645ec"] if entry == "iter" else
                      syms["audio_uart_lv_timer_remove_4644ee"]) if compiled else \
                     (0x4645ec if entry == "iter" else 0x4644ee)
            u.emu_start(origin | 1, 0x600000, count=10000)
            return trace, u.mem_read(state + 0x82, 1)[0], u.reg_read(A.UC_ARM_REG_R0)
        cases = [(entry, timer, dirty) for entry, timer, dirty in itertools.product(
            ("iter", "remove"), (0, 0x20010000), (0, 1, 0x80, 0xff)) if entry == "iter" or timer]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_TIMER_HELPERS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_spans": ["0x4645ec..0x464603", "0x4644ee..0x46450b"],
               "native_state_base": "0x2006f548", "cases": len(cases),
               "limits": ["List helpers and heap free controlled; live timer list mutation remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
