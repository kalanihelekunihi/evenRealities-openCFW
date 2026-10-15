#!/usr/bin/env python3
"""Controlled native/C comparison of the Apollo QuickList full-update path."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_mode_one_4f5718.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-one"
NATIVE = {"zero": 0x43c0e4, "copy": 0x4f55e0, "aux": 0x4f6328,
          "flags": 0x43d0ce}
COMPILED = {"zero": "audio_uart_buffer_zero", "copy": "audio_quicklist_copy_record_4f55e0",
            "aux": "audio_quicklist_aux_update_4f6328", "flags": "audio_log_flags"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    for literal, value in ((0x4f5c3c, 0x2012a72c), (0x4f62f0, 0x20101a1c),
                           (0x4f62f4, 0x20075041), (0x4f62f8, 0x20074e28),
                           (0x4f62fc, 0x20130654), (0x4f6300, 0x20074e14),
                           (0x4f6304, 0x20074b9c), (0x4f5c40, 0x201303cc),
                           (0x4f5c44, 0x20074e1c)):
        assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") == value
    shim = '''#include <stdint.h>
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){}
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
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_mode_one_4f5718",
                        str(SRC), str(sh), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, guard, active, aux_count, mode, flag_a, flag_b):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x200000)
            u.mem_write(0x20101a1c + 0x1220, bytes([guard]))
            for index in active:
                u.mem_write(0x20101a1c + 232*index + 228, b"\x01")
            u.mem_write(0x201308d4, aux_count.to_bytes(2, "little"))
            u.mem_write(0x2013064c, aux_count.to_bytes(2, "little"))
            u.mem_write(0x20074e1c, mode.to_bytes(4, "little"))
            u.mem_write(0x20074e14, flag_a.to_bytes(4, "little"))
            u.mem_write(0x20074b9c, flag_b.to_bytes(4, "little"))
            u.mem_write(0x2012a72c+8, b"\xab"*11840)
            u.mem_write(0x20130654, b"\xcd"*648)
            cuts = ({(syms[name] & ~1): key for key, name in COMPILED.items()}
                    if compiled else {addr: key for key, addr in NATIVE.items()})
            trace = []

            def hook(uc, address, size, unused):
                key = cuts.get(address)
                if key is None:
                    return
                r0, r1, r2 = (uc.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if key == "zero":
                    trace.append((key, r0, r1, r2))
                    uc.mem_write(r0, bytes([r2 & 255])*r1)
                elif key == "copy":
                    trace.append((key, r0, r1))
                    uc.mem_write(r1, b"\x77"*296)
                elif key == "aux":
                    trace.append((key,))
                else:
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_mode_one_4f5718"] if compiled else 0x4f5718
            u.emu_start(entry | 1, 0x600000, count=10000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace,
                    bytes(u.mem_read(0x2012a72c+8, 11840)),
                    bytes(u.mem_read(0x20130654, 648)),
                    bytes(u.mem_read(0x20075041, 1)), bytes(u.mem_read(0x20074e28, 4)))

        active_sets = ((), (0,), (0, 3, 19), tuple(range(20)))
        count = 0
        for guard, active, aux_count, mode, flag_a, flag_b in itertools.product(
                (0, 1), active_sets, (0, 1), (0, 1), (0, 1), (0, 1)):
            old = run(False, guard, active, aux_count, mode, flag_a, flag_b)
            new = run(True, guard, active, aux_count, mode, flag_a, flag_b)
            if old != new:
                raise AssertionError((guard, active, aux_count, mode, flag_a, flag_b,
                                      old[:2], new[:2], old[4:], new[4:]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_ONE_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5718..0x4f5833", "cases": count,
               "limits": ["Record copy, auxiliary update, buffer zero and logging are controlled at lower interfaces.",
                          "Final RAM placement and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
