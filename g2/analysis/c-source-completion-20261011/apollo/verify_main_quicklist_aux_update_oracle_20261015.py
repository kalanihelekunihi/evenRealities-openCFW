#!/usr/bin/env python3
"""Controlled native/C comparison of completed-UID batching and failure."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_aux_update_4f6328.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-aux-update"
NATIVE = {"zero": 0x43c0e4, "send": 0x5591b0, "flags": 0x43d0ce,
          "verbose": 0x43d574, "compact": 0x43ce9e}
SHIM = '''#include <stdint.h>
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){}
uint32_t audio_quicklist_send_completed_5591b0(uint32_t a,const void*b){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){return 0;}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_aux_update_4f6328", str(SRC), str(shim),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        compiled = {"zero": syms["audio_uart_buffer_zero"] & ~1,
                    "send": syms["audio_quicklist_send_completed_5591b0"] & ~1,
                    "flags": syms["audio_log_flags"] & ~1,
                    "verbose": syms["audio_log_extended"] & ~1,
                    "compact": syms["compressed_log_output"] & ~1}

        def run(is_compiled, count, failure):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            base = 0x201303cc
            initial = bytearray(b"\x91" * 0x288)
            for index in range(count):
                initial[16*index:16*index+4] = (0xabc000 + index).to_bytes(4, "little")
                initial[16*index+8:16*index+12] = (0x123000 + index).to_bytes(4, "little")
                initial[16*index+12:16*index+16] = (0x456000 + index).to_bytes(4, "little")
            initial[0x280:0x282] = count.to_bytes(2, "little")
            u.mem_write(base, bytes(initial))
            send_packets = []
            calls = []
            targets = compiled if is_compiled else NATIVE

            def hook(uc, address, size, unused):
                for kind, target in targets.items():
                    if address != target:
                        continue
                    r0, r1, r2 = (uc.reg_read(getattr(A, "UC_ARM_REG_R" + str(i))) for i in range(3))
                    calls.append((kind, r0 if kind in ("send", "zero") else None))
                    if kind == "zero":
                        uc.mem_write(r0, b"\x00" * r1)
                    elif kind == "flags":
                        uc.reg_write(A.UC_ARM_REG_R0, 0)
                    elif kind == "send":
                        send_packets.append(bytes(uc.mem_read(r1, 0x1230)))
                        uc.reg_write(A.UC_ARM_REG_R0, 7 if failure == len(send_packets) else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                    break

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_aux_update_4f6328"] if is_compiled else 0x4f6328
            u.emu_start(entry | 1, 0x600000, count=5000000)
            return (u.reg_read(A.UC_ARM_REG_R0), send_packets,
                    bytes(u.mem_read(base, 0x288)), [x[0] for x in calls])

        cases = 0
        for count, failure in itertools.product((0, 1, 19, 20, 21, 39, 40), (0, 1, 2)):
            native, source = run(False, count, failure), run(True, count, failure)
            if native != source:
                raise AssertionError((count, failure, native[0], source[0],
                                      len(native[1]), len(source[1]),
                                      [a == b for a, b in zip(native[1], source[1])],
                                      native[2] == source[2], native[3], source[3]))
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_AUX_UPDATE_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x4f6328..0x4f657d",
               "cases": cases,
               "limits": ["Send, zeroing, and logging are controlled lower calls.",
                          "Packet bytes, call order, completed list, and return value are compared.",
                          "RAM placement and hardware behavior remain unproved."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)


if __name__ == "__main__":
    main()
