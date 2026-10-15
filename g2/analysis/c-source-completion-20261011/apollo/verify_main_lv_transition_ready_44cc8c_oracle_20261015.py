#!/usr/bin/env python3
"""Compare native and C transition completion callback sequencing."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_ready_44cc8c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-ready-44cc8c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = """#include <stdint.h>
uint32_t audio_uart_page_style_selector_44b860(uint32_t x){return x&0xff0000;}
uint32_t audio_uart_lv_style_property_44bdea(void *o,uint32_t s,uint32_t p)
{(void)o;(void)s;(void)p;return 0;}
uint32_t audio_uart_page_style_resolve_44ca18(void *o,uint32_t s,uint8_t p,void *n)
{(void)o;(void)s;(void)p;(void)n;return 0;}
void *audio_uart_lv_transition_style_44c72c(void *o,uint32_t s)
{(void)o;(void)s;return 0;}
void audio_uart_page_style_value_482868(void *s,uint32_t p,uint32_t v)
{(void)s;(void)p;(void)v;}
void audio_uart_page_style_refresh_44bc8c(void *o,uint32_t s,uint32_t p)
{(void)o;(void)s;(void)p;}
"""
NATIVE = {"selector": 0x44b860, "property": 0x44bdea,
          "resolve": 0x44ca18, "transition_style": 0x44c72c,
          "style_value": 0x482868, "refresh": 0x44bc8c}
COMPILED = {"selector": "audio_uart_page_style_selector_44b860",
            "property": "audio_uart_lv_style_property_44bdea",
            "resolve": "audio_uart_page_style_resolve_44ca18",
            "transition_style": "audio_uart_lv_transition_style_44c72c",
            "style_value": "audio_uart_page_style_value_482868",
            "refresh": "audio_uart_page_style_refresh_44bc8c"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as temporary:
        elf = Path(temporary) / "ready.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_transition_ready_44cc8c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {parts[2]: int(parts[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(parts := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, selector, prop, value):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, payload)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            animation, record, object, style_entry = 0x20010000, 0x20011000, 0x20012000, 0x20013000
            put(cpu, animation, record)
            row = bytearray(0x20)
            row[0:4] = object.to_bytes(4, "little")
            row[4] = prop
            row[8:12] = selector.to_bytes(4, "little")
            row[12:16] = (0x89abcdef).to_bytes(4, "little")
            cpu.mem_write(record, bytes(row))
            put(cpu, style_entry, 0x20013100)
            trace = []
            hooks = {address & ~1: name for name, address in NATIVE.items()}
            if compiled:
                hooks = {names[symbol] & ~1: name for name, symbol in COMPILED.items()}

            def hook(uc, address, size, unused):
                name = hooks.get(address)
                if name is None:
                    return
                r0, r1, r2, r3 = (uc.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if name == "selector":
                    trace.append((name, r0))
                    uc.reg_write(A.UC_ARM_REG_R0, r0 & 0xff0000)
                elif name == "property":
                    trace.append((name, r0, r1, r2))
                    uc.reg_write(A.UC_ARM_REG_R0, value)
                elif name == "resolve":
                    trace.append((name, r0, r1, r2, r3,
                                  uc.mem_read(record + 4, 1)[0]))
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                elif name == "transition_style":
                    trace.append((name, r0, r1))
                    uc.reg_write(A.UC_ARM_REG_R0, style_entry)
                elif name == "style_value":
                    trace.append((name, r0, r1, r2))
                elif name == "refresh":
                    trace.append((name, r0, r1, r2))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, animation)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = names["audio_uart_lv_transition_ready_44cc8c"] if compiled else 0x44cc8c
            cpu.emu_start(entry | 1, 0x600000, count=100000)
            return trace, bytes(cpu.mem_read(record, 0x20))

        cases = [(0x123456, 0x10, 0x9876), (0x120000, 0x0c, 0x7fff),
                 (0x000000, 0x71, 0), (0xf0000, 0x3a, 0xffffffff)]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_READY_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA, "native_span": "0x44cc8c..0x44ccd7",
               "cases": len(cases),
               "limits": ["Four callback sequences native-compared with controlled lower providers.",
                          "Live transition list mutation and display effects remain open."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()
