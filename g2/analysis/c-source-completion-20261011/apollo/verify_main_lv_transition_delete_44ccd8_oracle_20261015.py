#!/usr/bin/env python3
"""Compare native and C transition deletion callback control flow."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_delete_44ccd8.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-delete-44ccd8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = """#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x100];
void *audio_uart_lv_list_first(void *r){(void)r;return 0;}
void *audio_uart_lv_list_next(void *r,void *n){(void)r;(void)n;return 0;}
void audio_uart_lv_list_remove_482c0e(void *r,void *n){(void)r;(void)n;}
void audio_uart_lv_heap_free(void *n){(void)n;}
uint32_t audio_uart_lv_style_notify_4827b0(void *s,uint32_t p){(void)s;(void)p;return 0;}
void audio_uart_lv_style_remove_44ba9a(void *o,void *s,uint32_t p)
{(void)o;(void)s;(void)p;}
"""
NATIVE = {"first": 0x482cd8, "next": 0x482cf0, "remove": 0x482c0e,
          "free": 0x44f758, "notify": 0x4827b0, "style_remove": 0x44ba9a}
COMPILED = {"first": "audio_uart_lv_list_first", "next": "audio_uart_lv_list_next",
            "remove": "audio_uart_lv_list_remove_482c0e",
            "free": "audio_uart_lv_heap_free",
            "notify": "audio_uart_lv_style_notify_4827b0",
            "style_remove": "audio_uart_lv_style_remove_44ba9a"}


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
        elf = Path(temporary) / "delete.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_transition_delete_44ccd8",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {parts[2]: int(parts[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(parts := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, duplicate, matched, empty):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, payload)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            animation, node, other, obj, records, style = (
                0x20010000, 0x20011000, 0x20011100, 0x20012000, 0x20013000, 0x20014000)
            put(cpu, animation, node)
            item = bytearray(0x20)
            item[0:4] = obj.to_bytes(4, "little")
            item[4] = 0x31
            item[8:12] = (0x123456).to_bytes(4, "little")
            cpu.mem_write(node, bytes(item))
            cpu.mem_write(other, bytes(item))
            object_bytes = bytearray(0x50)
            object_bytes[0x0c:0x10] = records.to_bytes(4, "little")
            object_bytes[0x2a:0x2c] = (2 << 4).to_bytes(2, "little")
            cpu.mem_write(obj, bytes(object_bytes))
            row = bytearray(16)
            row[0:4] = (style + 0x100).to_bytes(4, "little")
            row[4:8] = (0x01000001).to_bytes(4, "little")
            row[8:12] = style.to_bytes(4, "little")
            row[12:16] = (0x02000000 | (0x123456 if matched else 0x654321)).to_bytes(4, "little")
            cpu.mem_write(records, bytes(row))
            sty = bytearray(12)
            sty[8] = 0 if empty else 1
            cpu.mem_write(style, bytes(sty))
            trace = []
            hooks = {address & ~1: name for name, address in NATIVE.items()}
            if compiled:
                hooks = {names[symbol] & ~1: name for name, symbol in COMPILED.items()}

            def hook(uc, address, size, unused):
                name = hooks.get(address)
                if name is None:
                    return
                r0, r1, r2 = (uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if name == "first":
                    trace.append((name,))
                    uc.reg_write(A.UC_ARM_REG_R0, other if duplicate else node)
                elif name == "next":
                    trace.append((name, r1))
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                elif name == "remove":
                    trace.append((name, r1))
                elif name == "free":
                    trace.append((name, r0))
                elif name == "notify":
                    trace.append((name, r0, r1))
                elif name == "style_remove":
                    trace.append((name, r0, r1, r2))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, animation)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = names["audio_uart_lv_transition_delete_44ccd8"] if compiled else 0x44ccd8
            cpu.emu_start(entry | 1, 0x600000, count=100000)
            return trace, bytes(cpu.mem_read(node, 0x20)), bytes(cpu.mem_read(obj, 0x50))

        cases = [(True, True, False), (False, False, False),
                 (False, True, False), (False, True, True)]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_DELETE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA, "native_span": "0x44ccd8..0x44cd9d",
               "cases": len(cases),
               "limits": ["Duplicate, absent overlay, retained style and empty style branches native-compared with controlled list responses.",
                          "Live linked-list mutation and deallocation remain lower-provider behavior."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()
