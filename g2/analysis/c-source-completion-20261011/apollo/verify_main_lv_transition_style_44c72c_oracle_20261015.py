#!/usr/bin/env python3
"""Compare native and C transition-style lookup and allocation."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_style_44c72c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-style-44c72c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = """#include <stdint.h>
void *audio_uart_lv_realloc_44f76a(void *p,uint32_t n)
{uint8_t *q=(void *)0x20018000,*r=p;for(uint32_t i=0;i<n-8u;i++)q[i]=r[i];return q;}
void *audio_uart_lv_malloc(uint32_t n){(void)n;return (void *)0x20019000;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t b){uint8_t *q=p;while(n--)*q++=(uint8_t)b;}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,const char *e,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as temporary:
        elf = Path(temporary) / "lookup.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_transition_style_44c72c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {pieces[2]: int(pieces[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(pieces := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, tags, selector):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000)
            uc.mem_write(0x438000, payload)
            uc.mem_map(0x100000, 0x100000)
            for address, data in segments:
                uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x400000)
            obj, records, expanded, style = 0x20010000, 0x20011000, 0x20018000, 0x20019000
            object_bytes = bytearray(0x50)
            object_bytes[0x0c:0x10] = records.to_bytes(4, "little")
            object_bytes[0x2a:0x2c] = (len(tags) << 4).to_bytes(2, "little")
            uc.mem_write(obj, bytes(object_bytes))
            rows = bytearray(8 * len(tags))
            for index, tag in enumerate(tags):
                rows[index * 8:index * 8 + 4] = (0x20013000 + index * 0x100).to_bytes(4, "little")
                rows[index * 8 + 4:index * 8 + 8] = tag.to_bytes(4, "little")
            if rows:
                uc.mem_write(records, bytes(rows))
            if not compiled:
                def hook(cpu, address, size, unused):
                    r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                    r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                    if address == 0x44f76a:
                        if r1 > 8:
                            cpu.mem_write(expanded, bytes(cpu.mem_read(r0, r1 - 8)))
                        cpu.reg_write(A.UC_ARM_REG_R0, expanded)
                    elif address == 0x44b7a8:
                        cpu.mem_write(r0, bytes(r1))
                    elif address == 0x44f718:
                        cpu.reg_write(A.UC_ARM_REG_R0, style)
                    elif address == 0x48278c:
                        cpu.mem_write(r0, bytes(12))
                    else:
                        return
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                uc.hook_add(UC_HOOK_CODE, hook)
            uc.reg_write(A.UC_ARM_REG_R0, obj)
            uc.reg_write(A.UC_ARM_REG_R1, selector)
            uc.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = names["audio_uart_lv_transition_style_44c72c"] if compiled else 0x44c72c
            try:
                uc.emu_start(entry | 1, 0x600000, count=100000)
            except Exception as error:
                raise RuntimeError((compiled, tags, selector,
                                    hex(uc.reg_read(A.UC_ARM_REG_PC)))) from error
            changed = int.from_bytes(uc.mem_read(obj + 0x0c, 4), "little")
            count = (int.from_bytes(uc.mem_read(obj + 0x2a, 2), "little") & 0x3ff) >> 4
            return (uc.reg_read(A.UC_ARM_REG_R0),
                    bytes(uc.mem_read(obj, 0x50)),
                    bytes(uc.mem_read(changed, count * 8)),
                    bytes(uc.mem_read(style, 12)))

        cases = [
            ([0x02000001], 1),
            ([0x01000001, 0x02000001], 1),
            ([0x02000002, 0x02000001], 1),
            ([0x02000001, 0x02000002], 2),
            ([0x03000001], 1),
            ([], 1),
            ([0x01000001], 1),
            ([0x01000001, 0x00000002], 1),
        ]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[0], source[0], native[1] == source[1],
                                      native[2] == source[2], native[3] == source[3]))
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_STYLE_LOOKUP_ORACLE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "official_payload_sha256": PAYLOAD_SHA, "native_span": "0x44c72c..0x44c827",
        "cases": len(cases),
        "limits": ["Existing-record lookup plus three allocation/insertion cases are native-compared with controlled allocator returns.",
                   "Allocator failure and assertion paths remain unverified."],
    }
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()
