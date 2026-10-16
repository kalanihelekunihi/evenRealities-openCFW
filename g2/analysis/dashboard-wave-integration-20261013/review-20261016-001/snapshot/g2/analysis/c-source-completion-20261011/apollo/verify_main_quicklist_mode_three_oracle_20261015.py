#!/usr/bin/env python3
"""Native/C QuickList modify comparison with composed source-owned ID lookup."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate"
SRC = SOURCE / "quicklist_mode_three_4f5c4c.c"
FIND = SOURCE / "quicklist_find_record_4f5636.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-three"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    for literal, value in ((0x4f62f0, 0x20101a1c), (0x4f62f4, 0x20075041),
                           (0x4f62f8, 0x20074e28), (0x4f6760, 0x2012a72c)):
        assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") == value
    shim = '''#include <stdint.h>
void audio_quicklist_copy_record_4f55e0(const void*a,void*b){}
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
                        "-Wl,-e,audio_quicklist_mode_three_4f5c4c", str(SRC), str(FIND), str(sh),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, guard, old_count, active, id_mode):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x200000)
            input_base, rows = 0x20101a1c, 0x2012a72c
            u.mem_write(input_base, b"\x00"*(20*232+4))
            u.mem_write(input_base+0x1220, bytes([guard]))
            u.mem_write(rows, b"\x9b"*11848)
            u.mem_write(rows, old_count.to_bytes(2, "little"))
            for index in range(old_count):
                u.mem_write(rows+296*index+0x114, (0x100+index).to_bytes(4, "little"))
            for index in active:
                item = input_base + 232*index
                match = old_count != 0 and (id_mode == 2 or (id_mode == 1 and index % 2 == 0))
                item_id = (0x100 + index % old_count) if match else (0x500+index)
                u.mem_write(item, item_id.to_bytes(4, "little"))
                u.mem_write(item+228, b"\x01")
            u.mem_write(0x20075041, b"\xee")
            u.mem_write(0x20074e28, (0xdeadbeef).to_bytes(4, "little"))
            copy_addr = (syms["audio_quicklist_copy_record_4f55e0"] & ~1) if compiled else 0x4f55e0
            flags_addr = (syms["audio_log_flags"] & ~1) if compiled else 0x43d0ce
            trace = []

            def hook(uc, address, size, unused):
                if address == copy_addr:
                    src, dst = uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1)
                    trace.append((src, dst))
                    item_id = bytes(uc.mem_read(src, 4))
                    uc.mem_write(dst, b"\x77"*296)
                    uc.mem_write(dst+0x114, item_id)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif address == flags_addr:
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, 3)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_mode_three_4f5c4c"] if compiled else 0x4f5c4c
            u.emu_start(entry | 1, 0x600000, count=10000000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace,
                    bytes(u.mem_read(rows, 11848)), bytes(u.mem_read(0x20075041, 1)),
                    bytes(u.mem_read(0x20074e28, 4)))

        count = 0
        active_sets = ((), (0,), (1,), (0, 1, 3, 19), tuple(range(20)))
        for guard, old_count, active, id_mode in itertools.product(
                (0, 1), (0, 1, 5, 39, 40), active_sets, (0, 1, 2)):
            old = run(False, guard, old_count, active, id_mode)
            new = run(True, guard, old_count, active, id_mode)
            if old != new:
                raise AssertionError((guard, old_count, active, id_mode,
                                      old[:2], new[:2], [a == b for a, b in zip(old[2:], new[2:])]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_THREE_ORACLE",
               "sources": {str(SRC.relative_to(ROOT)): hashlib.sha256(SRC.read_bytes()).hexdigest(),
                           str(FIND.relative_to(ROOT)): hashlib.sha256(FIND.read_bytes()).hexdigest()},
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5c4c..0x4f5e11", "cases": count,
               "limits": ["Record conversion and logging are controlled at native lower interfaces.",
                          "ID lookup executes in both native and compiled C composition.",
                          "Final RAM placement and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
