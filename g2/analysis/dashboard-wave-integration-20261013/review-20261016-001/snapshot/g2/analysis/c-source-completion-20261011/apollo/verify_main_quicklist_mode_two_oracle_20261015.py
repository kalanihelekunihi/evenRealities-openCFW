#!/usr/bin/env python3
"""Controlled native/C Apollo QuickList add-up comparison."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_mode_two_4f5a1c.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-two"
NATIVE = {"zero": 0x43c0e4, "select": 0x4f5662, "copy": 0x439be4,
          "record": 0x4f55e0, "aux": 0x4f6328, "flags": 0x43d0ce}
COMPILED = {"zero": "audio_uart_buffer_zero", "select": "audio_quicklist_select_records_4f5662",
            "copy": "audio_queue_copy_bytes", "record": "audio_quicklist_copy_record_4f55e0",
            "aux": "audio_quicklist_aux_update_4f6328", "flags": "audio_log_flags"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    for literal, value in ((0x4f61f0, 0x20367bd8), (0x4f5c3c, 0x2012a72c),
                           (0x4f5c40, 0x201303cc), (0x4f62fc, 0x20130654),
                           (0x4f631c, 0x2012d584), (0x4f62f4, 0x20075041),
                           (0x4f62f8, 0x20074e28)):
        assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") == value
    shim = '''#include <stdint.h>
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){}
uint32_t audio_quicklist_select_records_4f5662(void*a,uint32_t b,uint32_t*c,uint32_t d){return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){return a;}
void audio_quicklist_copy_record_4f55e0(const void*a,void*b){}
void audio_quicklist_aux_update_4f6328(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){return 0;}
'''
    with tempfile.TemporaryDirectory() as td:
        sh = Path(td) / "shim.c"
        sh.write_text(shim)
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_mode_two_4f5a1c", str(SRC), str(sh),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, selected, old_count, aux_mode, status):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x200000)
            u.mem_map(0x20300000, 0x100000)
            rows, incoming, scratch, removed, aux = (0x2012a72c, 0x20367bd8,
                                                     0x2012d584, 0x201303cc, 0x20130654)
            u.mem_write(rows, b"\x9b"*11848)
            u.mem_write(rows, old_count.to_bytes(2, "little"))
            for i in range(old_count):
                u.mem_write(rows+8+296*i+0x114, (1000+i).to_bytes(4, "little"))
            u.mem_write(incoming, b"\x8a"*4640)
            u.mem_write(scratch, b"\x7c"*11840)
            u.mem_write(removed, b"\x5d"*648)
            u.mem_write(aux, b"\x4e"*648)
            u.mem_write(removed+0x280, (40 if aux_mode == 2 else 0).to_bytes(2, "little"))
            u.mem_write(aux+0x280, (2 if aux_mode else 0).to_bytes(2, "little"))
            if aux_mode:
                u.mem_write(aux, (1000+old_count-1 if old_count else 9999).to_bytes(4, "little"))
                u.mem_write(aux+16, (1000+old_count-2 if old_count>1 else 9998).to_bytes(4, "little"))
            cuts = ({(syms[name] & ~1): key for key, name in COMPILED.items()}
                    if compiled else {addr: key for key, addr in NATIVE.items()})
            trace = []

            def hook(uc, address, size, unused):
                key = cuts.get(address)
                if key is None:
                    return
                r0, r1, r2, r3 = (uc.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if key == "zero":
                    trace.append((key, r0, r1, r2))
                    uc.mem_write(r0, bytes([r2 & 255])*r1)
                elif key == "select":
                    trace.append((key, r0, r1, r3))
                    uc.mem_write(r2, selected.to_bytes(4, "little"))
                    for i in range(selected):
                        row = incoming + 232*i
                        uc.mem_write(row, bytes([i+1])*232)
                    uc.reg_write(A.UC_ARM_REG_R0, status)
                elif key == "copy":
                    trace.append((key, r0, r1, r2))
                    if r2:
                        uc.mem_write(r0, bytes(uc.mem_read(r1, r2)))
                elif key == "record":
                    trace.append((key, r0, r1))
                    uc.mem_write(r1, b"\x77"*296)
                elif key == "aux":
                    trace.append((key,))
                else:
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, 2)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_mode_two_4f5a1c"] if compiled else 0x4f5a1c
            u.emu_start(entry | 1, 0x600000, count=100000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace,
                    bytes(u.mem_read(rows, 11848)), bytes(u.mem_read(removed, 648)),
                    bytes(u.mem_read(aux, 648)), bytes(u.mem_read(scratch, 11840)),
                    bytes(u.mem_read(0x20075041, 1)), bytes(u.mem_read(0x20074e28, 4)))

        count = 0
        for selected, old_count, aux_mode, status in itertools.product(
                (0, 1, 2, 5, 20), (0, 1, 20, 39, 40), (0, 1, 2), (0, 2)):
            old = run(False, selected, old_count, aux_mode, status)
            new = run(True, selected, old_count, aux_mode, status)
            if old != new:
                raise AssertionError((selected, old_count, aux_mode, status,
                                      old[:2], new[:2], [a == b for a, b in zip(old[2:], new[2:])]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_TWO_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5a1c..0x4f5c39", "cases": count,
               "limits": ["Selector, byte copy, record conversion, aux update and logging use controlled lower calls.",
                          "Final RAM placement and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
